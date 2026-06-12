"""VECTRA-X — Streamlit decision-support dashboard.

Loads PRECOMPUTED artifacts from ``outputs/tables`` and ``outputs/figures``
(run ``python run_pipeline.py`` first). It does NOT retrain models live.

Run:  streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
REPORTS = ROOT / "outputs" / "reports"
DASH = ROOT / "outputs" / "dashboard_data"

st.set_page_config(page_title="VECTRA-X", page_icon="🦟", layout="wide")


# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def load_table(name: str) -> pd.DataFrame:
    p = TABLES / name
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_summary() -> dict:
    p = DASH / "summary.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def show_fig(name: str, caption: str = "") -> None:
    p = FIGURES / name
    if p.exists():
        st.image(str(p), caption=caption, width="stretch")
    else:
        st.info(f"Figure not found: {name} — run `python run_pipeline.py`.")


def show_report(name: str) -> None:
    p = REPORTS / name
    if p.exists():
        st.markdown(p.read_text(encoding="utf-8"))
    else:
        st.info(f"Report not found: {name}")


summary = load_summary()
if not summary:
    st.error("No precomputed artifacts found. Run `python run_pipeline.py` first.")
    st.stop()

# --------------------------------------------------------------------------- #
st.sidebar.title("🦟 VECTRA-X")
st.sidebar.caption("Clinical Triage Intelligence — FIT 2026, Track IV")
PAGES = [
    "1 · Executive Overview",
    "2 · Dataset & EDA",
    "3 · Model Performance",
    "4 · Disease Prediction Explorer",
    "5 · Patient-level Triage",
    "6 · Uncertainty & Conformal",
    "7 · Explainability",
    "8 · Fairness & Robustness",
    "9 · Resource Simulation",
    "10 · Methodology & Limitations",
]
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.caption("Decision support — **not** a diagnostic authority. "
                   "Features are anonymised signals, not medical causes.")


# =========================================================================== #
if page.startswith("1"):
    st.title("VECTRA-X — Executive Overview")
    st.markdown("*A multi-label, explainable, uncertainty-aware clinical triage "
                "intelligence system for vector-borne disease response.*")
    shape = summary.get("shape", [0, 0])
    tm = summary.get("test_metrics", {}).get("PRE_LAB", {})
    c = st.columns(4)
    c[0].metric("Patients × features", f"{shape[0]} × {shape[1]}")
    c[1].metric("Active disease labels", len(summary.get("active_labels", [])))
    c[2].metric("Multi-label patients", summary.get("n_multilabel_patients", "—"))
    c[3].metric("Best pre-lab model", summary.get("best_model_per_track", {}).get("PRE_LAB", "—"))
    c = st.columns(4)
    c[0].metric("Pre-lab macro-F1 (test)", tm.get("macro_f1", "—"))
    c[1].metric("Pre-lab macro-recall", tm.get("macro_recall", "—"))
    c[2].metric("Conformal coverage", summary.get("conformal", {}).get("overall_coverage", "—"))
    c[3].metric("Co-infection ROC-AUC", summary.get("coinfection", {}).get("roc_auc", "—"))

    st.subheader("The thesis")
    st.markdown(
        "- **Multi-label, not multi-class** — over half of patients carry >1 diagnosis.\n"
        "- **Leakage-aware staging** — separate *pre-lab triage* from *lab-aware confirmation*.\n"
        "- **Uncertainty-aware** — calibrated probabilities + conformal prediction sets.\n"
        "- **Actionable** — triage tiers + resource simulation, with fairness auditing.")
    col1, col2 = st.columns(2)
    with col1:
        show_fig("target_distribution.png", "Disease prevalence")
    with col2:
        show_fig("resource_priority_distribution.png", "Triage tiers")

elif page.startswith("2"):
    st.title("Dataset & Exploratory Data Analysis")
    st.markdown(f"**Active labels:** {', '.join(summary.get('active_labels', []))}  \n"
                f"**Inactive (0 positives):** {', '.join(summary.get('inactive_labels', []))}")
    tab = st.tabs(["Targets", "Co-occurrence", "Missingness", "Demographics", "Associations"])
    with tab[0]:
        show_fig("target_distribution.png"); show_fig("label_cardinality.png")
        st.dataframe(load_table("label_distribution.csv"), width="stretch")
    with tab[1]:
        show_fig("label_cooccurrence_heatmap.png"); show_fig("coinfection_profile.png")
        st.dataframe(load_table("label_top_combinations.csv"), width="stretch")
    with tab[2]:
        show_fig("missingness_top_features.png"); show_fig("missingness_by_disease.png")
    with tab[3]:
        show_fig("demographics.png"); show_fig("feature_projection_pca.png")
    with tab[4]:
        show_fig("association_matrix.png")

elif page.startswith("3"):
    st.title("Model Performance")
    st.subheader("Leaderboard — pre-lab vs lab-aware vs full (5-fold OOF)")
    lb = load_table("model_leaderboard.csv")
    if not lb.empty:
        st.dataframe(lb, width="stretch", height=420)
    show_fig("model_leaderboard.png")
    st.subheader("Held-out test metrics by track")
    tms = summary.get("test_metrics", {})
    st.dataframe(pd.DataFrame(tms).T, width="stretch")
    st.info("The large gain in **FULL** is a leakage artefact (*Dengue (Dengua)*). "
            "The **pre-lab** model is the realistic deployable system.")
    st.subheader("Per-label metrics (held-out test)")
    st.dataframe(load_table("per_label_metrics.csv"), width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        show_fig("per_label_f1.png"); show_fig("roc_curves.png")
    with c2:
        show_fig("per_label_recall.png"); show_fig("pr_curves.png")
    show_fig("confusion_matrices.png")

elif page.startswith("4"):
    st.title("Disease Prediction Explorer")
    pt = load_table("vectra_patient_level_predictions.csv")
    if pt.empty:
        st.stop()
    labels = summary.get("active_labels", [])
    st.subheader("Cohort predicted-probability profile")
    prob_cols = [f"prob_{l}" for l in labels if f"prob_{l}" in pt.columns]
    st.bar_chart(pt[prob_cols].mean().rename(lambda s: s.replace("prob_", "")))
    st.subheader("Filter cohort by predicted disease")
    sel = st.selectbox("Disease", labels)
    mask = pt["predicted_labels"].str.contains(sel, na=False)
    st.metric(f"Patients predicted {sel}", int(mask.sum()))
    st.dataframe(pt.loc[mask, ["uuid", "predicted_labels", "conformal_set",
                               "triage_category"]].head(50), width="stretch")

elif page.startswith("5"):
    st.title("Patient-level Triage Card")
    pt = load_table("vectra_patient_level_predictions.csv")
    if pt.empty:
        st.stop()
    labels = summary.get("active_labels", [])
    uid = st.selectbox("Select patient (UUID)", pt["uuid"].astype(str).tolist())
    row = pt[pt["uuid"].astype(str) == uid].iloc[0]
    tier = row["triage_category"]
    color = {"Routine Monitoring": "🟢", "Clinical Review": "🟡",
             "Confirmatory Test Priority": "🟠", "Urgent Response Priority": "🔴"}.get(tier, "⚪")
    c = st.columns(3)
    c[0].metric("Triage tier", f"{color} {tier}")
    c[1].metric("Triage score", row.get("triage_score", "—"))
    c[2].metric("Uncertainty", row.get("uncertainty_level", "—"))
    st.markdown(f"**Recommended action:** {row.get('recommended_action', '—')}")
    st.markdown(f"**Predicted labels:** {row.get('predicted_labels','')} &nbsp; "
                f"**Conformal set:** {row.get('conformal_set','')} &nbsp; "
                f"**True labels:** {row.get('true_labels','(hidden)')}")
    st.subheader("Calibrated disease probabilities")
    cal_cols = [f"calprob_{l}" for l in labels if f"calprob_{l}" in pt.columns]
    if cal_cols:
        st.bar_chart(row[cal_cols].rename(lambda s: s.replace("calprob_", "")))
    st.caption("Decision support only — confirm clinically. Conformal set with ≥2 "
               "labels indicates ambiguity → confirmatory testing recommended.")

elif page.startswith("6"):
    st.title("Uncertainty & Conformal Prediction")
    conf = summary.get("conformal", {})
    c = st.columns(4)
    c[0].metric("Target coverage", "90%")
    c[1].metric("Empirical coverage", conf.get("overall_coverage", "—"))
    c[2].metric("Avg set size", conf.get("avg_set_size", "—"))
    c[3].metric("Ambiguous (≥2) %", conf.get("pct_ambiguous_multi", "—"))
    show_fig("uncertainty_distribution.png")
    st.subheader("Per-label conformal coverage (held-out test)")
    st.dataframe(load_table("conformal_metrics.csv"), width="stretch")
    st.subheader("Example prediction sets")
    st.dataframe(load_table("conformal_prediction_examples.csv").head(25), width="stretch")

elif page.startswith("7"):
    st.title("Explainability")
    st.caption("Permutation importance + transparent logistic local attributions. "
               "Features are anonymised model signals, not medical causes.")
    c1, c2 = st.columns(2)
    with c1:
        show_fig("feature_importance_global.png")
    with c2:
        show_fig("feature_importance_per_label.png")
    show_fig("local_explanation_examples.png", "Local case studies")
    show_fig("shap_summary.png", "SHAP summary (malaria), if available")
    st.dataframe(load_table("feature_importance_global.csv"), width="stretch")

elif page.startswith("8"):
    st.title("Fairness & Robustness")
    show_fig("fairness_recall_gap.png")
    st.subheader("Subgroup metrics")
    st.dataframe(load_table("fairness_metrics.csv"), width="stretch")
    st.subheader("Leave-one-center-out stress test")
    loco = load_table("leave_one_center_out.csv")
    if not loco.empty:
        st.dataframe(loco, width="stretch")
        st.warning("Macro-F1 drops when transferring across centers — real workflow "
                   "shift. Recommend per-facility recalibration.")

elif page.startswith("9"):
    st.title("Resource Simulation")
    res = load_table("resource_simulation.csv")
    st.dataframe(res, width="stretch")
    show_fig("resource_priority_distribution.png")
    st.subheader("Threshold-policy trade-off")
    st.dataframe(load_table("threshold_policy_resource_tradeoff.csv"), width="stretch")
    show_fig("threshold_policy_resource_tradeoff.png")

elif page.startswith("10"):
    st.title("Methodology & Limitations")
    tab = st.tabs(["Leakage audit", "Thresholds", "Calibration", "Limitations & Ethics"])
    with tab[0]:
        show_report("leakage_audit.md")
    with tab[1]:
        show_report("threshold_strategy.md")
    with tab[2]:
        show_report("calibration_summary.md")
    with tab[3]:
        show_report("limitations_and_ethics.md")
