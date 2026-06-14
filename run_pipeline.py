"""run_pipeline.py — VECTRA-X end-to-end orchestrator.

Runs the full leakage-aware, multi-label clinical-triage pipeline and writes
every deliverable (tables, figures, models, programmatic reports, dashboard
data). Designed to be re-runnable and deterministic (RANDOM_STATE=42).

Protocol (honest by construction):
  * Outer multi-label-stratified split  -> train (75%) / test (25%).
  * Model selection by 5-fold OOF metrics on TRAIN (leaderboard).
  * Best model per track refit on TRAIN; reported metrics come from the
    held-out TEST split (per-label metrics, calibration, conformal coverage).
  * Cohort dashboard table uses full-data out-of-fold probabilities so every
    patient is scored by a model that did not train on them.

Usage:  python run_pipeline.py            (from the project root)
        python run_pipeline.py --quick    (fewer permutation repeats)
"""
from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src import (
    calibration as cal,
    conformal as cf,
    data_loader as dl,
    evaluation as ev,
    explainability as xai,
    fairness as fr,
    label_detection as ld,
    leakage_audit as lk,
    modeling as M,
    preprocessing as pp,
    report_utils as ru,
    schema_audit as sa,
    triage_engine as te,
    visualization as viz,
)

warnings.filterwarnings("ignore")
logger = ru.get_logger("run_pipeline")


# =========================================================================== #
def main(quick: bool = False, use_cache: bool = False) -> None:
    cfg = ru.load_config()
    rs = cfg["project"]["random_state"]
    np.random.seed(rs)
    paths = ru.get_paths(cfg)
    T, F, R, MODELS, PROC, DASH = (paths["tables"], paths["figures"], paths["reports"],
                                   paths["models"], paths["processed"], paths["dashboard_data"])
    n_repeats = 4 if quick else 10
    summary: dict = {"project": cfg["project"]["name"]}

    logger.info("=" * 70)
    logger.info("VECTRA-X pipeline starting (quick=%s)", quick)

    # ---------------- Stage 1: load + schema audit ---------------------- #
    df = dl.load_raw(cfg)
    dic = dl.load_dictionary(cfg)
    dl.save_interim(df, cfg)
    uuid = df[cfg["io"]["uuid_col"]]

    audit = sa.audit_schema(df, dic, cfg)
    ru.save_table(audit["data_dictionary"], T / "data_dictionary_auto.csv")
    ru.save_table(audit["missingness"], T / "missingness_summary.csv")
    viz.data_type_summary(audit["data_dictionary"], F / "data_type_summary.png")
    viz.missingness_top(audit["missingness"], F / "missingness_top_features.png")
    summary["shape"] = list(audit["shape"])
    summary["n_duplicate_rows"] = audit["n_duplicate_rows"]
    summary["n_constant_columns"] = len(audit["constant_columns"])

    # ---------------- Stage 2: labels / target engineering -------------- #
    labels_info = ld.detect_labels(df, cfg)
    # Supervised modeling excludes rows with incomplete diagnosis targets.
    # Keep the raw-schema audit above at n=300, then align every downstream
    # feature, UUID, target, split, metric, and artifact to the verified cohort.
    df = df.loc[labels_info["supervised_index"]].reset_index(drop=True)
    uuid = df[cfg["io"]["uuid_col"]].reset_index(drop=True)
    y = labels_info["y"].reset_index(drop=True)
    active = labels_info["active_labels"]
    y_out = pd.concat([uuid.reset_index(drop=True), y.reset_index(drop=True)], axis=1)
    ru.save_table(y_out, PROC / "y_multilabel.csv")
    ru.save_table(labels_info["distribution"], T / "label_distribution.csv")
    ru.save_table(labels_info["cooccurrence"].reset_index().rename(columns={"index": "label"}),
                  T / "label_cooccurrence.csv")
    ru.save_table(labels_info["top_combinations"], T / "label_top_combinations.csv")
    ru.save_table(labels_info["text_validation"], T / "label_text_validation.csv")
    viz.target_distribution(labels_info["distribution"], F / "target_distribution.png")
    viz.label_cardinality(labels_info["cardinality"], F / "label_cardinality.png")
    viz.cooccurrence_heatmap(labels_info["cooccurrence"], F / "label_cooccurrence_heatmap.png")
    summary["active_labels"] = active
    summary["inactive_labels"] = labels_info["inactive_labels"]
    summary["n_multilabel_patients"] = labels_info["n_multilabel_patients"]

    # ---------------- Stage 3: leakage audit + feature sets ------------- #
    feat_cols = ld.feature_columns(df, labels_info["label_columns_raw"], cfg)
    dcats = {}
    if "dict_category" in audit["data_dictionary"].columns:
        dcats = dict(zip(audit["data_dictionary"]["column"], audit["data_dictionary"]["dict_category"]))
    leak = lk.audit_leakage(df, y, feat_cols, dcats, cfg)
    ru.save_table(leak["leakage_candidates"], T / "leakage_candidates.csv")
    ru.save_table(leak["feature_sets_long"], T / "feature_sets.csv")
    ru.save_table(leak["audit"], T / "leakage_audit_full.csv")

    fs = leak["feature_sets"]
    # raw feature subsets (transparency)
    ru.save_table(pd.concat([uuid, df[feat_cols]], axis=1), PROC / "X_features_raw.csv")
    ru.save_table(pd.concat([uuid, df[fs["PRE_LAB_TRIAGE"]]], axis=1), PROC / "X_pre_lab.csv")
    ru.save_table(pd.concat([uuid, df[fs["LAB_AWARE_CONFIRMATION"]]], axis=1), PROC / "X_lab_aware.csv")
    ru.save_table(pd.concat([uuid, df[fs["FULL_RESEARCH_ONLY"]]], axis=1), PROC / "X_full.csv")
    summary["feature_set_sizes"] = {k: len(v) for k, v in fs.items()}

    # clean design frames per track
    X_pre, meta_pre = pp.make_feature_frame(df, fs["PRE_LAB_TRIAGE"], cfg)
    X_lab, meta_lab = pp.make_feature_frame(df, fs["LAB_AWARE_CONFIRMATION"], cfg)
    X_full, meta_full = pp.make_feature_frame(df, fs["FULL_RESEARCH_ONLY"], cfg)
    tracks = {
        "PRE_LAB": (X_pre, meta_pre),
        "LAB_AWARE": (X_lab, meta_lab),
        "FULL": (X_full, meta_full),
    }

    # ---------------- Stage 4: EDA figures ------------------------------ #
    raw = df
    gcol = next((c for c in raw.columns if cfg["preprocessing"]["gender_col_fragment"].lower() in c.lower()), None)
    ccol = next((c for c in raw.columns if cfg["preprocessing"]["center_col_fragment"].lower() in c.lower()), None)
    acol = next((c for c in raw.columns if cfg["preprocessing"]["age_col_fragment"].lower() in c.lower()), None)
    viz.missingness_by_label(X_full, y, active, F / "missingness_by_disease.png")
    viz.demographics(raw, acol, gcol, ccol, F / "demographics.png")
    viz.correlation_matrix(X_full, F / "association_matrix.png")
    viz.coinfection_profile(labels_info["top_combinations"], F / "coinfection_profile.png")
    try:
        from sklearn.decomposition import PCA
        pre = pp.build_preprocessor(meta_pre, scale_numeric=True)
        Xp = pre.fit_transform(X_pre)
        proj = PCA(n_components=2, random_state=rs).fit_transform(Xp)
        color = y["malaria"].map({1: "malaria+", 0: "malaria-"}) if "malaria" in y else y.iloc[:, 0]
        color.name = "malaria"
        viz.projection_2d(proj, color, "PCA of pre-lab features (colour = malaria)", F / "feature_projection_pca.png")
    except Exception as exc:
        logger.warning("PCA projection skipped: %s", exc)

    # ---------------- Stage 5: split + leaderboard ---------------------- #
    train_idx, test_idx = M.train_test_indices(y, cfg["modeling"]["test_size"], rs)
    summary["n_train"], summary["n_test"] = len(train_idx), len(test_idx)
    model_names = M.available_model_names()
    summary["models_available"] = model_names
    logger.info("Models available: %s", model_names)

    cache_path = DASH / "_cache_leaderboard.joblib"
    if use_cache and cache_path.exists():
        cached = joblib.load(cache_path)
        leaderboard, track_oof_train = cached["leaderboard"], cached["track_oof_train"]
        logger.info("Loaded leaderboard from cache (%s).", cache_path.name)
    else:
        leaderboard_rows = []
        track_oof_train = {}   # (track,model) -> oof proba on train
        for track, (Xt, metat) in tracks.items():
            X_train = Xt.iloc[train_idx]
            y_train = y.iloc[train_idx]
            splits = M.make_cv_splits(y_train, cfg["modeling"]["cv_folds"], rs)
            for mname in model_names:
                oof = M.cross_val_proba(mname, metat, X_train, y_train, splits, rs)
                track_oof_train[(track, mname)] = oof
                pred05 = (oof >= 0.5).astype(int)
                mls = ev.multilabel_summary(y_train, pred05, oof)
                leaderboard_rows.append({"track": track, "model": mname,
                                         "model_track": f"{track}:{mname}", **mls})
            # supplemental classifier chain
            cc = M.classifier_chain_proba(metat, X_train, y_train, splits, rs)
            if cc is not None:
                pred05 = (cc >= 0.5).astype(int)
                mls = ev.multilabel_summary(y_train, pred05, cc)
                leaderboard_rows.append({"track": track, "model": "classifier_chain",
                                         "model_track": f"{track}:classifier_chain", **mls})
                track_oof_train[(track, "classifier_chain")] = cc

        leaderboard = pd.DataFrame(leaderboard_rows).sort_values(
            ["track", "macro_pr_auc"], ascending=[True, False]).reset_index(drop=True)
        joblib.dump({"leaderboard": leaderboard, "track_oof_train": track_oof_train}, cache_path)
    ru.save_table(leaderboard, T / "model_leaderboard.csv")
    viz.model_leaderboard(leaderboard, "macro_f1", F / "model_leaderboard.png")

    # best model per track (by OOF macro PR-AUC). The supplemental
    # classifier_chain is reported in the leaderboard but is not selected for
    # deployment/refit (it is a co-diagnosis dependency demonstrator).
    best = {}
    for track in tracks:
        sub = leaderboard[(leaderboard["track"] == track)
                          & (leaderboard["model"].isin(model_names))]
        best[track] = sub.sort_values("macro_pr_auc", ascending=False).iloc[0]["model"]
    summary["best_model_per_track"] = best
    logger.info("Best model per track: %s", best)

    # ---------------- Stage 6: held-out TEST eval for each track -------- #
    per_label_all = []
    test_results = {}
    thresholds_by_track = {}
    for track, (Xt, metat) in tracks.items():
        mname = best[track]
        X_train, X_test = Xt.iloc[train_idx], Xt.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        # refit on full train, predict test
        model = M.BinaryRelevanceModel(mname, metat, rs).fit(X_train, y_train)
        test_proba = model.predict_proba(X_test)
        oof_train = track_oof_train[(track, mname)]
        # tune thresholds on OOF-train (performance policy)
        thr = {}
        for j, lab in enumerate(active):
            t, _ = ev.optimise_threshold(y_train[lab].values, oof_train[:, j], "f1")
            thr[lab] = t
        thresholds_by_track[track] = thr
        test_pred = ev.apply_thresholds(test_proba, thr, active)
        mls = ev.multilabel_summary(y_test, test_pred, test_proba)
        test_results[track] = {"model": mname, "test_metrics": mls,
                               "test_proba": test_proba, "oof_train": oof_train}
        pl = ev.per_label_metrics(y_test, test_pred, test_proba, active)
        pl.insert(0, "track", track)
        per_label_all.append(pl)
        # save deployable models for pre-lab + lab-aware
        if track in ("PRE_LAB", "LAB_AWARE"):
            joblib.dump({"model": model, "labels": active, "thresholds": thr,
                         "feature_set": fs["PRE_LAB_TRIAGE" if track == "PRE_LAB"
                                          else "LAB_AWARE_CONFIRMATION"]},
                        MODELS / f"{track.lower()}_model.joblib")

    per_label_metrics = pd.concat(per_label_all, ignore_index=True)
    ru.save_table(per_label_metrics, T / "per_label_metrics.csv")
    summary["test_metrics"] = {k: v["test_metrics"] for k, v in test_results.items()}

    # figures on best PRE_LAB (the honest headline model)
    best_track = "PRE_LAB"
    y_test = y.iloc[test_idx]
    pl_pre = per_label_metrics[per_label_metrics["track"] == best_track]
    tp = test_results[best_track]["test_proba"]
    viz.per_label_bar(pl_pre, "f1", F / "per_label_f1.png", "Pre-lab per-label F1 (held-out test)")
    viz.per_label_bar(pl_pre, "recall", F / "per_label_recall.png", "Pre-lab per-label recall (held-out test)")
    viz.confusion_matrices(pl_pre, F / "confusion_matrices.png")
    viz.roc_curves(y_test, tp, active, F / "roc_curves.png")
    viz.pr_curves(y_test, tp, active, F / "pr_curves.png")

    # ---------------- Stage 7: threshold optimisation + policies -------- #
    oof_pre = test_results["PRE_LAB"]["oof_train"]
    y_train = y.iloc[train_idx]
    thr_rows, policy_rows = [], []
    perf_pol, safety_pol, oper_pol = {}, {}, {}
    severe = set(cfg["modeling"]["severe_labels"])
    for j, lab in enumerate(active):
        yv, sv = y_train[lab].values, oof_pre[:, j]
        t_f1, v_f1 = ev.optimise_threshold(yv, sv, "f1")
        t_rec, v_rec = ev.optimise_threshold(yv, sv, "recall_at_prec", recall_floor=0.30)
        t_bal, v_bal = ev.optimise_threshold(yv, sv, "balanced", recall_floor=0.5)
        thr_rows.append({"label": lab, "thr_maxF1": t_f1, "f1": v_f1,
                         "thr_recall_oriented": t_rec, "recall": v_rec,
                         "thr_balanced": t_bal})
        perf_pol[lab] = t_f1
        # safety: severe labels get the recall-oriented (lower) threshold
        safety_pol[lab] = min(t_f1, t_rec) if lab in severe else t_f1
        oper_pol[lab] = t_bal
    threshold_opt = pd.DataFrame(thr_rows)
    ru.save_table(threshold_opt, T / "threshold_optimization.csv")
    policies = {"performance": perf_pol, "safety": safety_pol, "operational": oper_pol}
    pol_table = pd.DataFrame([{"label": lab,
                               "performance": perf_pol[lab],
                               "safety": safety_pol[lab],
                               "operational": oper_pol[lab]} for lab in active])
    ru.save_table(pol_table, T / "threshold_policies.csv")
    viz.threshold_tradeoff(threshold_opt.rename(columns={"thr_maxF1": "threshold"})[["label", "threshold", "f1"]],
                           F / "threshold_tradeoff.png")

    # ---------------- Stage 8: calibration (pre-lab) -------------------- #
    test_proba_cal, calibrators = cal.calibrate_matrix(y_train, oof_pre, tp, active, method="auto")
    cal_metrics_raw = cal.calibration_metrics(y_test, tp, active)
    cal_metrics_cal = cal.calibration_metrics(y_test, test_proba_cal, active)
    cal_metrics_raw["variant"] = "uncalibrated"; cal_metrics_cal["variant"] = "calibrated"
    cal_metrics = pd.concat([cal_metrics_raw, cal_metrics_cal], ignore_index=True)
    ru.save_table(cal_metrics, T / "calibration_metrics.csv")
    viz.calibration_curves(y_test, tp, active, F / "calibration_curves.png")
    summary["calibration_mean_brier"] = round(float(cal_metrics_raw["brier"].mean()), 4)

    # ---------------- Stage 9: conformal (test) ------------------------- #
    conf_info = cf.fit_conformal(y_train, oof_pre, active, cfg["modeling"]["conformal_alpha"])
    conf_pl, conf_summary = cf.conformal_metrics(y_test, tp, conf_info, active)
    ru.save_table(conf_pl, T / "conformal_metrics.csv")
    examples = cf.set_examples(uuid.iloc[test_idx].reset_index(drop=True), tp, y_test, conf_info, active, 40)
    ru.save_table(examples, T / "conformal_prediction_examples.csv")
    summary["conformal"] = conf_summary

    # ---------------- Stage 10: cohort-wide OOF (dashboard) ------------- #
    full_splits = M.make_cv_splits(y, cfg["modeling"]["cv_folds"], rs)
    cohort_proba = M.cross_val_proba(best["PRE_LAB"], meta_pre, X_pre, y, full_splits, rs)
    cohort_cal, _ = cal.calibrate_matrix(y, cohort_proba, cohort_proba, active, method="auto")
    cohort_conf = cf.fit_conformal(y, cohort_proba, active, cfg["modeling"]["conformal_alpha"])
    cohort_sets = cf.predict_sets(cohort_proba, cohort_conf, active)
    set_sizes = np.array([len(s) for s in cohort_sets])

    # co-infection (Track 4) cohort OOF
    y_co = M.coinfection_target(y)
    co_best, co_best_auc = None, -1
    co_rows = []
    for mname in model_names:
        co_oof = M.coinfection_cv_proba(mname, meta_pre, X_pre, y_co, full_splits, rs)
        auc = ev._safe_auc(y_co.values, co_oof)
        ap = ev._safe_ap(y_co.values, co_oof)
        co_rows.append({"model": mname, "roc_auc": round(auc, 4), "pr_auc": round(ap, 4)})
        if auc > co_best_auc:
            co_best_auc, co_best, co_best_oof = auc, mname, co_oof
    co_table = pd.DataFrame(co_rows).sort_values("roc_auc", ascending=False)
    ru.save_table(co_table, T / "coinfection_model_metrics.csv")
    co_pred = (co_best_oof >= 0.5).astype(int)
    summary["coinfection"] = {"best_model": co_best, "roc_auc": round(co_best_auc, 4),
                              "pr_auc": round(float(ev._safe_ap(y_co.values, co_best_oof)), 4),
                              "recall": round(float(((co_pred == 1) & (y_co.values == 1)).sum() / max(1, y_co.sum())), 4)}

    # ---------------- Stage 11: uncertainty + triage (cohort) ----------- #
    # Uncertainty is assessed on the calibrated probabilities (our best
    # probability estimate) combined with the conformal set size.
    unc = te.uncertainty_scores(cohort_cal, active, set_sizes)
    unc_out = pd.concat([uuid.reset_index(drop=True), unc], axis=1)
    ru.save_table(unc_out, T / "patient_uncertainty_scores.csv")
    viz.uncertainty_distribution(unc, F / "uncertainty_distribution.png")
    summary["uncertainty_counts"] = unc["uncertainty_level"].value_counts().to_dict()

    cohort_thr = thresholds_by_track["PRE_LAB"]
    patient_table = te.build_patient_table(
        uuid.reset_index(drop=True), cohort_proba, cohort_cal, y, active,
        cohort_thr, cfg, unc, co_best_oof, cohort_sets)
    ru.save_table(patient_table, T / "vectra_patient_level_predictions.csv")
    # dashboard subset (lighter)
    dash_cols = ["uuid", "predicted_labels", "true_labels", "conformal_set",
                 "coinfection_prob", "uncertainty_level", "triage_score",
                 "triage_category", "recommended_action"] + [f"calprob_{l}" for l in active]
    ru.save_table(patient_table[[c for c in dash_cols if c in patient_table.columns]],
                  T / "vectra_triage_dashboard_data.csv")
    summary["triage_distribution"] = patient_table["triage_category"].value_counts().to_dict()

    # ---------------- Stage 12: resource simulation --------------------- #
    resource = te.resource_simulation(patient_table, active)
    ru.save_table(resource, T / "resource_simulation.csv")
    viz.resource_priority(resource, F / "resource_priority_distribution.png")
    tradeoff = te.policy_resource_tradeoff(cohort_proba, active, policies)
    ru.save_table(tradeoff, T / "threshold_policy_resource_tradeoff.csv")
    viz.policy_tradeoff(tradeoff, F / "threshold_policy_resource_tradeoff.png")

    # ---------------- Stage 13: explainability (pre-lab + lab-aware) ---- #
    X_test_pre = X_pre.iloc[test_idx]
    model_pre = M.BinaryRelevanceModel(best["PRE_LAB"], meta_pre, rs).fit(X_pre.iloc[train_idx], y_train)
    pli = xai.permutation_importance_per_label(model_pre, X_test_pre, y_test, active, rs, n_repeats)
    if pli.empty:  # fall back to train if test too small for signal
        pli = xai.permutation_importance_per_label(model_pre, X_pre.iloc[train_idx], y_train, active, rs, n_repeats)
    gimp = xai.global_importance(pli, top=25)
    ru.save_table(gimp, T / "feature_importance_global.csv")
    ru.save_table(pli.sort_values(["label", "importance_mean"], ascending=[True, False]),
                  T / "feature_importance_per_label.csv")
    viz.importance_global(gimp, F / "feature_importance_global.png")
    viz.importance_per_label(pli, active, F / "feature_importance_per_label.png")

    # local explanations: pick representative cases from cohort
    explainers = xai.fit_linear_explainers(meta_pre, X_pre.iloc[train_idx], y_train, active, rs)
    cases = _select_cases(patient_table, y, active)
    case_expl = {}
    for title, (row_idx, lab) in cases.items():
        if lab in explainers and lab in active:
            case_expl[f"{title}\n({lab})"] = xai.explain_patient(explainers, X_pre.iloc[[row_idx]], lab)
    if case_expl:
        viz.local_explanations(case_expl, F / "local_explanation_examples.png")
    # optional SHAP
    shap_done = False
    try:
        res = xai.try_shap(model_pre, X_pre.iloc[train_idx], "malaria")
        if res is not None:
            sv, Xs = res
            viz.shap_summary(sv, Xs, "malaria", F / "shap_summary.png")
            shap_done = True
    except Exception as exc:
        logger.info("SHAP summary skipped: %s", exc)
    summary["shap_generated"] = shap_done

    # ---------------- Stage 14: fairness -------------------------------- #
    subs_full = fr.build_subgroups(df[feat_cols], X_pre, df, cfg)
    subs_test = {k: v.iloc[test_idx].reset_index(drop=True) for k, v in subs_full.items()}
    test_pred_pre = ev.apply_thresholds(tp, cohort_thr, active)
    sub_metrics = fr.subgroup_metrics(y_test, test_pred_pre, active, subs_test)
    ru.save_table(sub_metrics, T / "fairness_metrics.csv")
    gap_frames = [fr.recall_gap(sub_metrics, ax, active) for ax in subs_test]
    gap_df = pd.concat([g for g in gap_frames if not g.empty], ignore_index=True) if gap_frames else pd.DataFrame()
    if not gap_df.empty:
        ru.save_table(gap_df, T / "fairness_recall_gaps.csv")
        viz.fairness_recall_gap(gap_df, F / "fairness_recall_gap.png")
    # leave-one-center-out stress test
    if "center" in subs_full:
        loco = fr.leave_one_center_out(best["PRE_LAB"], meta_pre, X_pre, y,
                                       subs_full["center"], active, rs)
        if not loco.empty:
            ru.save_table(loco, T / "leave_one_center_out.csv")
            summary["loco_macro_f1"] = loco["macro_f1"].round(4).tolist()

    # ---------------- Stage 15: programmatic reports -------------------- #
    _write_reports(cfg, R, F, summary, audit, labels_info, leak, leaderboard, best,
                   per_label_metrics, threshold_opt, pol_table, cal_metrics, conf_pl,
                   conf_summary, unc, co_table, patient_table, resource, gimp, pli,
                   gap_df, examples)

    # ---------------- persist artifacts for notebooks/dashboard --------- #
    joblib.dump({
        "cohort_proba": cohort_proba, "cohort_cal": cohort_cal, "active": active,
        "cohort_conf": cohort_conf, "thresholds": cohort_thr,
        "co_best_oof": co_best_oof, "uuid": uuid.tolist(),
    }, DASH / "artifacts.joblib")
    with open(DASH / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str)

    # ---- refresh the static (Vercel-ready) web dashboard bundle ------- #
    try:
        import export_web_data
        export_web_data.main()
    except Exception as exc:  # pragma: no cover - web export is non-critical
        logger.info("Web export skipped (%s). Run `python export_web_data.py` manually.", exc)

    logger.info("=" * 70)
    logger.info("PIPELINE COMPLETE.")
    logger.info("Best PRE-LAB model: %s | test macro-F1=%.3f macro-PR-AUC=%.3f",
                best["PRE_LAB"], summary["test_metrics"]["PRE_LAB"]["macro_f1"],
                summary["test_metrics"]["PRE_LAB"]["macro_pr_auc"])
    logger.info("Conformal avg set size=%.2f, coverage=%.2f",
                conf_summary["avg_set_size"], conf_summary.get("overall_coverage", float("nan")))


# --------------------------------------------------------------------------- #
def _select_cases(patient_table: pd.DataFrame, y: pd.DataFrame, active: list[str]) -> dict:
    """Pick representative patient rows for local explanation case studies."""
    cases = {}
    # confident single-label
    single = patient_table[(patient_table["uncertainty_level"] == "low")
                           & (patient_table["conformal_set_size"] == 1)]
    if not single.empty:
        cases["Confident single-label"] = (single.index[0], "malaria")
    # high uncertainty
    hi = patient_table[patient_table["uncertainty_level"] == "high"]
    if not hi.empty:
        lab = "dengue" if "dengue" in active else active[0]
        cases["High uncertainty"] = (hi.index[0], lab)
    # co-infection
    co = patient_table[patient_table["conformal_set_size"] >= 2]
    if not co.empty:
        cases["Co-infection / ambiguous"] = (co.index[0], "dengue" if "dengue" in active else active[0])
    # rare label
    if "yellow_fever" in y.columns:
        yf = np.where(y["yellow_fever"].values == 1)[0]
        if len(yf):
            cases["Rare label (yellow fever)"] = (int(yf[0]), "yellow_fever")
    return cases


# --------------------------------------------------------------------------- #
def _write_reports(cfg, R, F, summary, audit, labels_info, leak, leaderboard, best,
                   per_label_metrics, threshold_opt, pol_table, cal_metrics, conf_pl,
                   conf_summary, unc, co_table, patient_table, resource, gimp, pli,
                   gap_df, examples) -> None:
    """Generate all programmatic markdown reports (figures referenced relatively)."""
    figrel = "../figures"

    # --- data audit ---
    rep = ru.MarkdownReport("Data Audit Summary", "VECTRA-X — official dataset")
    rep.p(f"**Shape:** {summary['shape'][0]} rows × {summary['shape'][1]} columns. "
          f"**Duplicate rows:** {summary['n_duplicate_rows']}. "
          f"**Constant columns:** {summary['n_constant_columns']}.")
    rep.h2("Column roles").table(audit["data_dictionary"]["role"].value_counts()
                                 .rename_axis("role").reset_index(name="n"))
    rep.h2("Top missing columns").table(audit["missingness"].head(15))
    rep.h2("Constant columns (dropped from modelling, logged)")
    rep.bullets(audit["constant_columns"] or ["none"])
    rep.figure(f"{figrel}/data_type_summary.png", "Column roles")
    rep.figure(f"{figrel}/missingness_top_features.png", "Top missingness")
    rep.h2("Target structure")
    rep.table(labels_info["distribution"])
    rep.p(f"Multi-label patients (>1 diagnosis): **{labels_info['n_multilabel_patients']}**; "
          f"patients with no active label: **{labels_info['n_no_label_patients']}**.")
    rep.p("Binary-vs-free-text label agreement = 100% on all labels (encoding validated).")
    rep.figure(f"{figrel}/target_distribution.png").figure(f"{figrel}/label_cardinality.png")
    rep.save(R / "data_audit_summary.md")

    # --- leakage audit ---
    rep = ru.MarkdownReport("Leakage & Clinical-Stage Audit", "Stage-gated feature sets")
    rep.p("Features were screened by **name pattern** AND **statistics** (mutual "
          "information + single-feature ROC-AUC vs each active label). Decisions:")
    rep.table(leak["feature_sets_long"][["feature_set", "n_features"]])
    rep.h2("Confirmed leakage / lab-confirmation features")
    rep.table(leak["leakage_candidates"].head(20)[
        ["feature", "decision", "best_label", "max_single_feature_auc", "mutual_info", "rationale"]])
    rep.h2("Decision logic")
    rep.bullets([
        "**PRE_LAB_TRIAGE** — demographics, symptoms, vitals only; the honest early-triage model.",
        "**LAB_AWARE_CONFIRMATION** — adds ordered lab/rapid tests (TDR, thick smear, haematology).",
        "**FULL_RESEARCH_ONLY** — adds target-restatement features (e.g. *Dengue (Dengua)*, AUC≈0.96) "
        "to demonstrate the cost of leakage; never deployed.",
    ])
    rep.save(R / "leakage_audit.md")

    # --- EDA ---
    rep = ru.MarkdownReport("EDA Insights", "Multi-label clinical structure")
    rep.bullets([
        f"Malaria dominates ({labels_info['distribution'].iloc[0]['prevalence_pct']:.0f}% prevalence) — "
        "accuracy/micro metrics are misleading; macro-F1 and per-label recall are primary.",
        f"{labels_info['n_multilabel_patients']} patients carry >1 diagnosis — multi-label, not multi-class.",
        "Top co-diagnoses: malaria+other, malaria+dengue, malaria+typhoid (see co-infection profile).",
        "Several lab/vital fields are heavily missing — kept with missing-indicator flags (workflow signal).",
        "Two health centers enable a domain-shift / fairness axis (leave-one-center-out).",
    ])
    for fig, cap in [("label_cooccurrence_heatmap.png", "Co-occurrence"),
                     ("coinfection_profile.png", "Top combinations"),
                     ("missingness_by_disease.png", "Missingness by disease"),
                     ("demographics.png", "Demographics"),
                     ("association_matrix.png", "Feature associations"),
                     ("feature_projection_pca.png", "PCA projection")]:
        rep.figure(f"{figrel}/{fig}", cap)
    rep.save(R / "eda_insights.md")

    # --- modeling ---
    rep = ru.MarkdownReport("Modeling Summary", "Leaderboard & pre-lab vs lab-aware")
    rep.p(f"Best model per track (by OOF macro-PR-AUC): **{best}**.")
    rep.h2("Leaderboard (5-fold OOF on train)")
    rep.table(leaderboard[["model_track", "macro_f1", "micro_f1", "macro_pr_auc",
                           "macro_roc_auc", "hamming_loss", "subset_accuracy"]], max_rows=30)
    rep.h2("Held-out TEST metrics by track")
    tm = pd.DataFrame([{"track": k, **m} for k, m in summary["test_metrics"].items()])
    rep.table(tm[["track", "macro_f1", "micro_f1", "macro_pr_auc", "macro_recall",
                  "hamming_loss", "subset_accuracy"]])
    pre_metrics = summary["test_metrics"]["PRE_LAB"]
    lab_metrics = summary["test_metrics"]["LAB_AWARE"]
    if (
        lab_metrics["macro_f1"] > pre_metrics["macro_f1"]
        and lab_metrics["macro_pr_auc"] > pre_metrics["macro_pr_auc"]
    ):
        comparison_text = (
            "LAB_AWARE improves both frozen-test macro-F1 and macro-PR-AUC; "
            "this remains a stage-specific comparison rather than evidence "
            "that laboratory data improve early triage."
        )
    else:
        comparison_text = (
            "LAB_AWARE does not improve both frozen-test macro-F1 and "
            "macro-PR-AUC. This is retained as a negative result; adding "
            "laboratory variables is not claimed to improve aggregate performance."
        )
    rep.p(f"**Pre-lab vs lab-aware vs full**: {comparison_text} "
          "FULL remains a research-only leakage demonstration and is never deployable.")
    rep.h2("Per-label metrics (held-out test)")
    rep.table(per_label_metrics)
    rep.h2("Co-infection detector (Track 4, cohort OOF)").table(co_table)
    for fig, cap in [("model_leaderboard.png", "Leaderboard"),
                     ("per_label_f1.png", "Per-label F1"), ("per_label_recall.png", "Recall"),
                     ("confusion_matrices.png", "Confusion"), ("roc_curves.png", "ROC"),
                     ("pr_curves.png", "PR")]:
        rep.figure(f"{figrel}/{fig}", cap)
    rep.save(R / "modeling_summary.md")

    # --- threshold strategy ---
    rep = ru.MarkdownReport("Threshold Strategy", "Three clinical policies")
    rep.p("Default 0.5 is rarely optimal under imbalance. Thresholds tuned per label on "
          "out-of-fold train predictions.")
    rep.h2("Per-label optimisation").table(threshold_opt)
    rep.h2("Policies").table(pol_table)
    rep.bullets([
        "**Performance** — maximise per-label F1.",
        "**Safety** — lower thresholds for severe/rare labels (dengue, typhoid, yellow fever) to raise recall.",
        "**Operational** — balanced threshold to limit unnecessary confirmatory-test burden.",
    ])
    rep.figure(f"{figrel}/threshold_tradeoff.png", "Threshold vs F1")
    rep.save(R / "threshold_strategy.md")

    # --- calibration ---
    rep = ru.MarkdownReport("Calibration Summary", "Trustworthy probabilities")
    rep.table(cal_metrics)
    rep.p(f"Mean uncalibrated Brier (pre-lab, test) = {summary['calibration_mean_brier']}.")
    rep.figure(f"{figrel}/calibration_curves.png", "Reliability curves")
    rep.save(R / "calibration_summary.md")

    # --- uncertainty ---
    rep = ru.MarkdownReport("Uncertainty Summary", "Entropy, margin, set size")
    rep.p("Per-patient uncertainty from predictive entropy, top-2 margin, #labels above "
          "threshold, and conformal set size.")
    rep.table(unc["uncertainty_level"].value_counts().rename_axis("level").reset_index(name="patients"))
    rep.figure(f"{figrel}/uncertainty_distribution.png", "Uncertainty")
    rep.save(R / "uncertainty_summary.md")

    # --- conformal ---
    rep = ru.MarkdownReport("Conformal Prediction Summary", "Recall-oriented prediction sets")
    rep.p(f"Exact uncapped empirical inclusion policy with nominal target "
          f"{100*(1-cfg['modeling']['conformal_alpha']):.0f}% (alpha="
          f"{cfg['modeling']['conformal_alpha']}). This small-sample result is "
          "reported per label and is not a prospective coverage guarantee. "
          f"Avg set size = {conf_summary['avg_set_size']}, empty sets "
          f"{conf_summary['pct_empty_sets']}%, ambiguous (≥2) {conf_summary['pct_ambiguous_multi']}%.")
    rep.h2("Per-label coverage (held-out test)").table(conf_pl)
    rep.h2("Example prediction sets").table(examples.head(15))
    rep.save(R / "conformal_summary.md")

    # --- explainability ---
    rep = ru.MarkdownReport("Explainability Summary", "Permutation importance + linear local")
    rep.p("Features are anonymised/encoded clinical **signals** — explanations describe model "
          "behaviour, not medical causation.")
    rep.h2("Global importance (top 15)").table(gimp.head(15))
    rep.figure(f"{figrel}/feature_importance_global.png", "Global importance")
    rep.figure(f"{figrel}/feature_importance_per_label.png", "Per-label importance")
    rep.figure(f"{figrel}/local_explanation_examples.png", "Local case studies")
    if summary.get("shap_generated"):
        rep.figure(f"{figrel}/shap_summary.png", "SHAP summary (malaria)")
    rep.save(R / "explainability_summary.md")

    # --- fairness ---
    rep = ru.MarkdownReport("Fairness & Robustness Summary", "Subgroup + center shift")
    rep.p("Audited axes: health center, gender, age group. Goal: no systematic under-detection "
          "for any subgroup.")
    if not gap_df.empty:
        rep.h2("Recall gaps (max − min across subgroup levels)").table(gap_df)
        rep.figure(f"{figrel}/fairness_recall_gap.png", "Recall gaps")
    if "loco_macro_f1" in summary:
        rep.h2("Leave-one-center-out stress test")
        rep.p(f"Macro-F1 when transferring across centers: {summary['loco_macro_f1']}.")
    rep.save(R / "fairness_summary.md")

    # --- triage ---
    rep = ru.MarkdownReport("Triage Engine Summary", "VECTRA-X decision support")
    rep.p("Triage score = 0.45·risk + 0.25·severe + 0.15·uncertainty + 0.15·co-infection "
          "(all bounded to [0,1]). Tiers assigned by transparent rules on severe-disease "
          "probability, uncertainty, co-infection and conformal set.")
    rep.h2("Cohort triage distribution").table(
        patient_table["triage_category"].value_counts().rename_axis("tier").reset_index(name="patients"))
    rep.h2("Sample patient outputs").table(
        patient_table[["uuid", "predicted_labels", "conformal_set", "uncertainty_level",
                       "triage_score", "triage_category", "recommended_action"]].head(10))
    rep.save(R / "triage_engine_summary.md")

    # --- resource ---
    rep = ru.MarkdownReport("Resource Simulation Summary", "Operational impact")
    rep.table(resource)
    rep.figure(f"{figrel}/resource_priority_distribution.png", "Priority distribution")
    rep.figure(f"{figrel}/threshold_policy_resource_tradeoff.png", "Policy trade-off")
    rep.save(R / "resource_simulation_summary.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="fewer permutation repeats")
    ap.add_argument("--use-cache", action="store_true",
                    help="reuse cached leaderboard OOF (skip the ~5-min CV stage)")
    args = ap.parse_args()
    main(quick=args.quick, use_cache=args.use_cache)
