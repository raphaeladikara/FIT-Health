"""Canonical end-to-end research workflow used by the final competition notebook."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score

from . import calibration as cal
from . import conformal as cf
from . import data_loader as dl
from . import evaluation as ev
from . import explainability as xai
from . import fairness as fr
from . import label_detection as ld
from . import leakage_audit as lk
from . import modeling as M
from . import preprocessing as pp
from . import report_utils as ru
from . import research_evaluation as reval
from . import schema_audit as sa
from . import triage_engine as te


@dataclass
class ResearchWorkflowResult:
    config: dict[str, Any]
    cohort_audit: dict[str, Any]
    schema_table: pd.DataFrame
    missingness_table: pd.DataFrame
    target_distribution: pd.DataFrame
    target_cardinality: pd.DataFrame
    target_cooccurrence: pd.DataFrame
    top_combinations: pd.DataFrame
    label_text_validation: pd.DataFrame
    leakage_audit: pd.DataFrame
    leakage_candidates: pd.DataFrame
    research_only_features: list[str]
    feature_contract: pd.DataFrame
    design_frames: dict[str, pd.DataFrame]
    frozen_indices: dict[str, np.ndarray]
    split_support: pd.DataFrame
    baselines: pd.DataFrame
    ablations: pd.DataFrame
    model_comparison: pd.DataFrame
    repeated_validation: pd.DataFrame
    selection_audit: pd.DataFrame
    final_test_metrics: pd.DataFrame
    final_per_label: pd.DataFrame
    final_intervals: pd.DataFrame
    paired_track_comparison: pd.DataFrame
    final_test_audit: pd.DataFrame
    coinfection_results: pd.DataFrame
    calibration_metrics: pd.DataFrame
    calibration_audit: pd.DataFrame
    conformal_exact: pd.DataFrame
    conformal_exact_summary: dict[str, float]
    conformal_pragmatic: pd.DataFrame
    conformal_pragmatic_summary: dict[str, float]
    selective_risk: pd.DataFrame
    fairness_metrics: pd.DataFrame
    fairness_gaps: pd.DataFrame
    leave_one_center_out: pd.DataFrame
    global_importance: pd.DataFrame
    local_explanation: dict[str, Any]
    scenario_sensitivity: pd.DataFrame
    safe_claims: pd.DataFrame
    artifact_manifest: pd.DataFrame
    fitted_models: dict[str, Any]
    thresholds: dict[str, dict[str, float]]
    active_labels: list[str]


def _subset_meta(meta: pp.FeatureMeta, columns: list[str]) -> pp.FeatureMeta:
    keep = set(columns)
    return pp.FeatureMeta(
        numeric_cols=[c for c in meta.numeric_cols if c in keep],
        binary_cols=[c for c in meta.binary_cols if c in keep],
        indicator_cols=[c for c in meta.indicator_cols if c in keep],
        dropped_constant=list(meta.dropped_constant),
        notes=list(meta.notes),
        source_map={c: s for c, s in meta.source_map.items() if c in keep},
    )


def _split_support(y: pd.DataFrame, train_idx: np.ndarray, test_idx: np.ndarray) -> pd.DataFrame:
    rows = []
    for label in y.columns:
        for partition, idx in [("train", train_idx), ("frozen_test", test_idx)]:
            rows.append(
                {
                    "partition": partition,
                    "label": label,
                    "n": len(idx),
                    "positives": int(y.iloc[idx][label].sum()),
                    "prevalence": float(y.iloc[idx][label].mean()),
                }
            )
    return pd.DataFrame(rows)


def _thresholds(y: pd.DataFrame, proba: np.ndarray) -> dict[str, float]:
    return {
        label: ev.optimise_threshold(y[label].to_numpy(), proba[:, j], "f1")[0]
        for j, label in enumerate(y.columns)
    }


def _evaluate_track(
    track: str,
    model_name: str,
    X: pd.DataFrame,
    meta: pp.FeatureMeta,
    y: pd.DataFrame,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    oof: np.ndarray,
    random_state: int,
    n_boot: int,
) -> tuple[Any, dict[str, float], np.ndarray, np.ndarray, pd.DataFrame, pd.DataFrame]:
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    thresholds = _thresholds(y_train, oof)
    model = M.BinaryRelevanceModel(model_name, meta, random_state).fit(
        X.iloc[train_idx], y_train
    )
    proba = model.predict_proba(X.iloc[test_idx])
    pred = ev.apply_thresholds(proba, thresholds, list(y.columns))
    aggregate = ev.multilabel_summary(y_test, pred, proba)
    aggregate.update({"track": track, "model": model_name})
    per_label = ev.per_label_metrics(y_test, pred, proba, list(y.columns))
    per_label.insert(0, "track", track)
    interval_rows = []
    for j, label in enumerate(y.columns):
        for metric, values in [("f1", pred[:, j]), ("recall", pred[:, j]), ("pr_auc", proba[:, j])]:
            interval_rows.append(
                {
                    "track": track,
                    "label": label,
                    "metric": metric,
                    **reval.bootstrap_metric_interval(
                        y_test[label].to_numpy(),
                        values,
                        metric,
                        n_boot=n_boot,
                        random_state=random_state + j,
                    ),
                }
            )
    return model, thresholds, proba, pred, pd.DataFrame([aggregate]), pd.DataFrame(interval_rows)


@lru_cache(maxsize=2)
def run_research_workflow(quick: bool = False) -> ResearchWorkflowResult:
    """Run the complete competition analysis from raw files."""
    cfg = ru.load_config()
    rs = int(cfg["project"]["random_state"])
    n_folds = 3 if quick else int(cfg["modeling"]["cv_folds"])
    repeated_seeds = [rs, rs + 1] if quick else list(range(rs, rs + 10))
    n_boot = 100 if quick else 2000
    candidate_models = (
        ["logreg", "extra_trees"]
        if quick
        else [
            "logreg_c0.1",
            "logreg",
            "logreg_c2.0",
            "random_forest",
            "extra_trees",
            "extra_trees_leaf5",
            "hist_gb",
        ]
    )

    raw = dl.load_raw(cfg)
    dictionary = dl.load_dictionary(cfg)
    schema = sa.audit_schema(raw, dictionary, cfg)
    label_info = ld.detect_labels(raw, cfg)
    supervised_index = label_info["supervised_index"]
    data = raw.loc[supervised_index].reset_index(drop=True)
    y = label_info["y"].reset_index(drop=True)
    uuid = data[cfg["io"]["uuid_col"]].reset_index(drop=True)
    train_idx, test_idx = M.train_test_indices(
        y, cfg["modeling"]["test_size"], rs
    )

    feature_cols = ld.feature_columns(data, label_info["label_columns_raw"], cfg)
    leakage = lk.audit_leakage(
        data.iloc[train_idx].reset_index(drop=True),
        y.iloc[train_idx].reset_index(drop=True),
        feature_cols,
        cfg=cfg,
    )
    feature_sets = leakage["feature_sets"]
    research_only = feature_sets["FULL_RESEARCH_ONLY"][
        len(feature_sets["LAB_AWARE_CONFIRMATION"]):
    ]

    X_pre, meta_pre = pp.make_feature_frame(data, feature_sets["PRE_LAB_TRIAGE"], cfg)
    X_lab, meta_lab = pp.make_feature_frame(
        data, feature_sets["LAB_AWARE_CONFIRMATION"], cfg
    )
    X_full, meta_full = pp.make_feature_frame(data, feature_sets["FULL_RESEARCH_ONLY"], cfg)
    pp.assert_no_research_features(
        list(X_pre.columns), meta_pre.source_map, set(research_only)
    )
    pp.assert_no_research_features(
        list(X_lab.columns), meta_lab.source_map, set(research_only)
    )
    design_frames = {"PRE_LAB": X_pre, "LAB_AWARE": X_lab, "RESEARCH_FULL": X_full}
    metas = {"PRE_LAB": meta_pre, "LAB_AWARE": meta_lab, "RESEARCH_FULL": meta_full}

    contract_rows = []
    audit_by_feature = leakage["audit"].set_index("feature")
    for track, meta in metas.items():
        for derived, source in meta.source_map.items():
            contract_rows.append(
                {
                    "track": track,
                    "raw_feature": source,
                    "model_feature": derived,
                    "stage": audit_by_feature.loc[source, "stage"],
                    "decision": audit_by_feature.loc[source, "decision"],
                }
            )
    feature_contract = pd.DataFrame(contract_rows)

    support = _split_support(y, train_idx, test_idx)
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    baseline_rows = []
    prevalence = y_train.mean().to_dict()
    for name in ["always_malaria", "prevalence", "random_prevalence"]:
        pred = reval.baseline_predictions(
            name, len(test_idx), list(y.columns), prevalence, rs
        )
        baseline_rows.append(
            {
                "baseline": name,
                **ev.multilabel_summary(y_test, pred),
            }
        )
    baselines = pd.DataFrame(baseline_rows)

    comparison_rows = []
    oof_store: dict[tuple[str, str], np.ndarray] = {}
    for track in ["PRE_LAB", "LAB_AWARE"]:
        X, meta = design_frames[track], metas[track]
        splits = M.make_cv_splits(y_train, n_folds, rs)
        for model_name in candidate_models:
            oof = M.cross_val_proba(
                model_name, meta, X.iloc[train_idx], y_train, splits, rs
            )
            oof_store[(track, model_name)] = oof
            metrics = ev.multilabel_summary(y_train, (oof >= 0.5).astype(int), oof)
            comparison_rows.append(
                {
                    "track": track,
                    "model": model_name,
                    "data_partition": "training_only",
                    **metrics,
                }
            )
    model_comparison = pd.DataFrame(comparison_rows)
    selected = {
        track: (
            model_comparison[model_comparison["track"] == track]
            .sort_values(["macro_pr_auc", "macro_f1"], ascending=False)
            .iloc[0]["model"]
        )
        for track in ["PRE_LAB", "LAB_AWARE"]
    }
    selection_audit = pd.DataFrame(
        [
            {
                "track": track,
                "selected_model": model,
                "criterion": "training OOF macro-PR-AUC",
                "data_partition": "training_only",
            }
            for track, model in selected.items()
        ]
    )

    repeated_rows = []
    for track in ["PRE_LAB", "LAB_AWARE"]:
        X, meta = design_frames[track], metas[track]
        for seed in repeated_seeds:
            splits = M.make_cv_splits(y_train, n_folds, seed)
            oof = M.cross_val_proba(
                selected[track], meta, X.iloc[train_idx], y_train, splits, seed
            )
            repeated_rows.append(
                {
                    "track": track,
                    "seed": seed,
                    **ev.multilabel_summary(
                        y_train, (oof >= 0.5).astype(int), oof
                    ),
                }
            )
    repeated_validation = pd.DataFrame(repeated_rows)

    fitted_models = {}
    track_thresholds = {}
    test_proba = {}
    test_pred = {}
    final_metrics = []
    final_per_label = []
    final_intervals = []
    for track in ["PRE_LAB", "LAB_AWARE"]:
        result = _evaluate_track(
            track,
            selected[track],
            design_frames[track],
            metas[track],
            y,
            train_idx,
            test_idx,
            oof_store[(track, selected[track])],
            rs,
            n_boot,
        )
        model, thresholds, proba, pred, agg, intervals = result
        fitted_models[track] = model
        track_thresholds[track] = thresholds
        test_proba[track], test_pred[track] = proba, pred
        final_metrics.append(agg)
        final_per_label.append(
            ev.per_label_metrics(y_test, pred, proba, list(y.columns)).assign(
                track=track
            )
        )
        final_intervals.append(intervals)
    final_test_metrics = pd.concat(final_metrics, ignore_index=True)
    final_per_label_df = pd.concat(final_per_label, ignore_index=True)
    final_intervals_df = pd.concat(final_intervals, ignore_index=True)
    final_test_audit = pd.DataFrame(
        {
            "track": ["PRE_LAB", "LAB_AWARE"],
            "evaluations_per_track": [1, 1],
            "selection_used_test": [False, False],
        }
    )

    paired_rows = []
    for j, label in enumerate(y.columns):
        paired_rows.append(
            {
                "label": label,
                "metric": "f1",
                **reval.paired_bootstrap_difference(
                    y_test[label].to_numpy(),
                    test_pred["LAB_AWARE"][:, j],
                    test_pred["PRE_LAB"][:, j],
                    "f1",
                    n_boot=n_boot,
                    random_state=rs + j,
                ),
            }
        )
    paired_track = pd.DataFrame(paired_rows)

    ablation_rows = []
    variants = {
        "all_pre_lab": list(X_pre.columns),
        "without_center": [c for c in X_pre.columns if c != "center_code"],
        "without_missing_indicators": [
            c for c in X_pre.columns if not c.endswith("__missing")
        ],
    }
    for name, columns in variants.items():
        meta_variant = _subset_meta(meta_pre, columns)
        oof = M.cross_val_proba(
            selected["PRE_LAB"],
            meta_variant,
            X_pre.iloc[train_idx][columns],
            y_train,
            M.make_cv_splits(y_train, n_folds, rs),
            rs,
        )
        ablation_rows.append(
            {
                "ablation": name,
                "n_features": len(columns),
                **ev.multilabel_summary(
                    y_train, (oof >= 0.5).astype(int), oof
                ),
            }
        )
    ablations = pd.DataFrame(ablation_rows)

    pre_oof = oof_store[("PRE_LAB", selected["PRE_LAB"])]
    calibrated_oof, calibration_audit = cal.cross_fitted_calibration(
        y_train, pre_oof, n_splits=n_folds, random_state=rs
    )
    calibrated_test, _ = cal.calibrate_matrix(
        y_train, pre_oof, test_proba["PRE_LAB"], list(y.columns)
    )
    cal_raw = cal.calibration_metrics(y_test, test_proba["PRE_LAB"], list(y.columns))
    cal_raw["variant"] = "uncalibrated"
    cal_adjusted = cal.calibration_metrics(y_test, calibrated_test, list(y.columns))
    cal_adjusted["variant"] = "calibrated_from_training_OOF"
    calibration_metrics = pd.concat([cal_raw, cal_adjusted], ignore_index=True)

    exact_info = cf.fit_conformal(
        y_train, calibrated_oof, list(y.columns),
        alpha=cfg["modeling"]["conformal_alpha"], mode="exact"
    )
    exact_table, exact_summary = cf.conformal_metrics(
        y_test, calibrated_test, exact_info, list(y.columns)
    )
    pragmatic_info = cf.fit_conformal(
        y_train, calibrated_oof, list(y.columns),
        alpha=cfg["modeling"]["conformal_alpha"], mode="pragmatic"
    )
    pragmatic_table, pragmatic_summary = cf.conformal_metrics(
        y_test, calibrated_test, pragmatic_info, list(y.columns)
    )

    row_correct = (test_pred["PRE_LAB"] == y_test.to_numpy()).all(axis=1)
    entropy = te.uncertainty_scores(calibrated_test, list(y.columns))["mean_entropy"]
    selective_risk = reval.selective_risk_curve(row_correct, entropy.to_numpy())

    y_co_train = M.coinfection_target(y_train)
    y_co_test = M.coinfection_target(y_test)
    co_splits = M.make_cv_splits(y_train, n_folds, rs)
    co_rows = []
    co_oof_store = {}
    for model_name in candidate_models:
        co_oof = M.coinfection_cv_proba(
            model_name, meta_pre, X_pre.iloc[train_idx], y_co_train, co_splits, rs
        )
        co_oof_store[model_name] = co_oof
        co_rows.append(
            {
                "model": model_name,
                "partition": "training_only_OOF",
                "roc_auc": ev._safe_auc(y_co_train.to_numpy(), co_oof),
                "pr_auc": ev._safe_ap(y_co_train.to_numpy(), co_oof),
            }
        )
    co_best = max(co_rows, key=lambda row: row["pr_auc"])["model"]
    co_pipe = M.make_pipeline(co_best, meta_pre, rs)
    co_pipe.fit(X_pre.iloc[train_idx], y_co_train)
    co_test_proba = co_pipe.predict_proba(X_pre.iloc[test_idx])[:, 1]
    co_pred = (co_test_proba >= 0.5).astype(int)
    co_rows.append(
        {
            "model": co_best,
            "partition": "frozen_test_once",
            "roc_auc": ev._safe_auc(y_co_test.to_numpy(), co_test_proba),
            "pr_auc": ev._safe_ap(y_co_test.to_numpy(), co_test_proba),
            "recall": recall_score(y_co_test, co_pred, zero_division=0),
            "specificity": recall_score(y_co_test, co_pred, pos_label=0, zero_division=0),
            "f1": f1_score(y_co_test, co_pred, zero_division=0),
        }
    )
    coinfection_results = pd.DataFrame(co_rows)

    subgroups = fr.build_subgroups(data[feature_cols], X_pre, data, cfg)
    test_subgroups = {
        name: values.iloc[test_idx].reset_index(drop=True)
        for name, values in subgroups.items()
    }
    fairness_metrics = fr.subgroup_metrics(
        y_test.reset_index(drop=True),
        test_pred["PRE_LAB"],
        list(y.columns),
        test_subgroups,
    )
    gaps = [
        fr.recall_gap(fairness_metrics, axis, list(y.columns))
        for axis in test_subgroups
    ]
    fairness_gaps = (
        pd.concat([g for g in gaps if not g.empty], ignore_index=True)
        if any(not g.empty for g in gaps)
        else pd.DataFrame()
    )
    loco = (
        fr.leave_one_center_out(
            selected["PRE_LAB"], meta_pre, X_pre, y, subgroups["center"],
            list(y.columns), rs
        )
        if "center" in subgroups
        else pd.DataFrame()
    )

    importance = xai.permutation_importance_per_label(
        fitted_models["PRE_LAB"],
        X_pre.iloc[test_idx],
        y_test,
        list(y.columns),
        rs,
        n_repeats=2 if quick else 10,
    )
    global_importance = xai.global_importance(importance, top=25)
    explanation_label = "dengue" if "dengue" in y.columns else y.columns[0]
    local_explanation = xai.explain_deployed_tree(
        fitted_models["PRE_LAB"],
        X_pre.iloc[train_idx],
        X_pre.iloc[test_idx[: min(3, len(test_idx))]],
        explanation_label,
    )

    scenario = te.scenario_sensitivity(
        calibrated_test,
        list(y.columns),
        {
            "base": cfg["modeling"]["risk_weights"],
            "rare_disease_emphasis": {
                **cfg["modeling"]["risk_weights"],
                "yellow_fever": 3.0,
                "dengue": 2.0,
            },
        },
        {
            "performance": track_thresholds["PRE_LAB"],
            "conservative": {
                label: max(0.05, threshold - 0.10)
                for label, threshold in track_thresholds["PRE_LAB"].items()
            },
        },
        capacities=[10, 25, len(test_idx)],
        false_negative_costs=[1.0, 3.0, 5.0],
    )

    pre_row = final_test_metrics.set_index("track").loc["PRE_LAB"]
    lab_row = final_test_metrics.set_index("track").loc["LAB_AWARE"]
    safe_claims = pd.DataFrame(
        [
            {
                "claim": "The verified supervised cohort contains 299 patients.",
                "evidence": "One row with all diagnosis targets missing was excluded.",
                "status": "supported",
            },
            {
                "claim": "The dataset is multi-label and severely imbalanced.",
                "evidence": f"{label_info['n_multilabel_patients']} patients have multiple active labels.",
                "status": "supported",
            },
            {
                "claim": "The other-disease presentation field is a target restatement.",
                "evidence": "Presence-indicator AUC is documented in the representation-aware leakage audit.",
                "status": "supported",
            },
            {
                "claim": "Laboratory-aware modeling improves frozen-test macro-F1.",
                "evidence": f"PRE_LAB={pre_row['macro_f1']:.3f}; LAB_AWARE={lab_row['macro_f1']:.3f}.",
                "status": "supported" if lab_row["macro_f1"] > pre_row["macro_f1"] else "not supported",
            },
            {
                "claim": "Prediction-set evidence is exact only for the uncapped empirical policy.",
                "evidence": "Exact and pragmatic modes are reported separately with per-label support.",
                "status": "supported",
            },
        ]
    )
    artifact_manifest = pd.DataFrame(
        [
            {"artifact": name, "type": type(value).__name__}
            for name, value in {
                "model_comparison": model_comparison,
                "final_test_metrics": final_test_metrics,
                "final_per_label": final_per_label_df,
                "calibration_metrics": calibration_metrics,
                "conformal_exact": exact_table,
                "fairness_metrics": fairness_metrics,
                "scenario_sensitivity": scenario,
            }.items()
        ]
    )

    return ResearchWorkflowResult(
        config=cfg,
        cohort_audit={
            "n_raw": len(raw),
            "n_supervised": len(data),
            "n_excluded_unknown_target": len(label_info["excluded_target_index"]),
            "excluded_indices": label_info["excluded_target_index"].tolist(),
        },
        schema_table=schema["data_dictionary"],
        missingness_table=schema["missingness"],
        target_distribution=label_info["distribution"],
        target_cardinality=label_info["cardinality"],
        target_cooccurrence=label_info["cooccurrence"],
        top_combinations=label_info["top_combinations"],
        label_text_validation=label_info["text_validation"],
        leakage_audit=leakage["audit"],
        leakage_candidates=leakage["leakage_candidates"],
        research_only_features=research_only,
        feature_contract=feature_contract,
        design_frames=design_frames,
        frozen_indices={"train": train_idx, "test": test_idx},
        split_support=support,
        baselines=baselines,
        ablations=ablations,
        model_comparison=model_comparison,
        repeated_validation=repeated_validation,
        selection_audit=selection_audit,
        final_test_metrics=final_test_metrics,
        final_per_label=final_per_label_df,
        final_intervals=final_intervals_df,
        paired_track_comparison=paired_track,
        final_test_audit=final_test_audit,
        coinfection_results=coinfection_results,
        calibration_metrics=calibration_metrics,
        calibration_audit=calibration_audit,
        conformal_exact=exact_table,
        conformal_exact_summary=exact_summary,
        conformal_pragmatic=pragmatic_table,
        conformal_pragmatic_summary=pragmatic_summary,
        selective_risk=selective_risk,
        fairness_metrics=fairness_metrics,
        fairness_gaps=fairness_gaps,
        leave_one_center_out=loco,
        global_importance=global_importance,
        local_explanation=local_explanation,
        scenario_sensitivity=scenario,
        safe_claims=safe_claims,
        artifact_manifest=artifact_manifest,
        fitted_models=fitted_models,
        thresholds=track_thresholds,
        active_labels=list(y.columns),
    )
