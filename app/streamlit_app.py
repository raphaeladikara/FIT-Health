"""VECTRA-X interactive decision-support dashboard.

Run from the project root:
    streamlit run app/streamlit_app.py

The app loads precomputed artifacts and saved pipelines. It never retrains models.
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app import dashboard_config as cfg
from app import dashboard_utils as du

st.set_page_config(page_title="VECTRA-X", page_icon="VX", layout="wide")


@st.cache_data(show_spinner=False)
def table(name: str) -> pd.DataFrame:
    return du.load_csv(cfg.TABLES / name)


@st.cache_data(show_spinner=False)
def summary() -> dict:
    return du.load_json(cfg.DASHBOARD_DATA / "summary.json", {})


@st.cache_data(show_spinner=False)
def cohort_data() -> pd.DataFrame:
    patients = table("vectra_patient_level_predictions.csv")
    raw = du.load_csv(cfg.ROOT / "data" / "interim" / "cleaned_patient_table.csv")
    if not patients.empty and not raw.empty:
        uuid = "_uuid" if "_uuid" in raw.columns else "uuid" if "uuid" in raw.columns else None
        if uuid:
            raw = raw.rename(columns={uuid: "uuid"})
            return patients.merge(raw, on="uuid", how="left", suffixes=("", "_raw"))
    return patients


@st.cache_resource(show_spinner=False)
def model_modes() -> dict:
    return du.available_model_modes()


def plotly_chart(fig: go.Figure) -> None:
    fig.update_layout(
        margin=dict(l=10, r=10, t=48, b=10),
        legend_title_text="",
        hovermode="closest",
    )
    st.plotly_chart(fig, width="stretch")


def download_frame(label: str, frame: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button(
        label,
        du.dataframe_csv_bytes(frame),
        file_name=filename,
        mime="text/csv",
        key=key,
        disabled=frame.empty,
    )


def figure_image(name: str, caption: str) -> None:
    path = cfg.FIGURES / name
    if path.exists():
        st.image(str(path), caption=caption, width="stretch")
    else:
        st.info(f"Optional figure unavailable: `{name}`.")


def report_text(name: str) -> str:
    path = cfg.REPORTS / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def label_probabilities(row: pd.Series, labels: list[str]) -> pd.DataFrame:
    records = []
    for label in labels:
        calibrated = f"calprob_{label}"
        raw = f"prob_{label}"
        value = row.get(calibrated, row.get(raw, np.nan))
        if pd.notna(value):
            records.append({"disease": label, "probability": float(value)})
    return pd.DataFrame(records).sort_values("probability", ascending=True)


def find_column(frame: pd.DataFrame, fragments: list[str]) -> str | None:
    for column in frame.columns:
        lowered = str(column).lower()
        if any(fragment.lower() in lowered for fragment in fragments):
            return column
    return None


data_summary = summary()
patients = cohort_data()
if not data_summary or patients.empty:
    st.error("Required dashboard artifacts are unavailable. Run `python run_pipeline.py` first.")
    st.stop()

labels = list(data_summary.get("active_labels", []))
modes = model_modes()

st.sidebar.title("VECTRA-X")
st.sidebar.caption("Vector-borne disease triage intelligence")
mode_name = st.sidebar.selectbox(
    "Model mode",
    list(modes),
    index=0,
    help="Pre-lab is the primary deployable model. Full-feature is a leakage demonstration.",
)
policy_name = st.sidebar.selectbox(
    "Threshold policy",
    ["performance", "safety", "operational"],
    index=2,
    help="Safety lowers selected severe-disease thresholds; operational balances recall and capacity.",
)
mode = modes[mode_name]
if mode["available"]:
    st.sidebar.success(f"{mode_name} model is available.")
else:
    st.sidebar.warning(f"{mode_name} has no deployable saved model.")
st.sidebar.caption(mode["description"])

pages = [
    "Executive Overview",
    "Patient-level Prediction",
    "Batch Prediction / Upload",
    "Population Overview",
    "Resource Prioritization",
    "Model Trust",
    "Explainability",
    "Uncertainty & Conformal",
    "Fairness & Robustness",
    "Methodology & Limitations",
]
page = st.sidebar.radio("Navigate", pages)
st.sidebar.divider()
st.sidebar.info(cfg.SAFETY_NOTE)


if page == "Executive Overview":
    st.title("VECTRA-X")
    st.subheader("Explainable and uncertainty-aware triage intelligence for vector-borne disease response")
    st.write(
        "The primary system is a leakage-aware pre-lab multi-label model. It supports "
        "patient review, confirmatory-test prioritization, and resource planning."
    )
    track = mode["track"]
    metrics = data_summary.get("test_metrics", {}).get(track, {})
    high_priority = int(
        patients["triage_category"].isin(
            ["Confirmatory Test Priority", "Urgent Response Priority"]
        ).sum()
    )
    multi_label = patients["predicted_labels"].map(lambda value: len(du.parse_label_set(value)) > 1).sum()
    cards = st.columns(6)
    cards[0].metric("Patients", len(patients))
    cards[1].metric("Macro F1", metrics.get("macro_f1", "Unavailable"))
    cards[2].metric("Micro F1", metrics.get("micro_f1", "Unavailable"))
    cards[3].metric("Weighted F1", metrics.get("weighted_f1", "Unavailable"))
    cards[4].metric("High priority", high_priority)
    cards[5].metric("Predicted multi-label", int(multi_label))

    c1, c2, c3 = st.columns(3)
    disease_counts = {
        label: int(patients["predicted_labels"].str.contains(label, regex=False, na=False).sum())
        for label in labels
    }
    with c1:
        fig = px.bar(
            x=list(disease_counts.values()),
            y=list(disease_counts.keys()),
            orientation="h",
            title="Predicted disease burden",
            labels={"x": "Patients", "y": "Disease"},
            color=list(disease_counts.keys()),
            color_discrete_map=cfg.DISEASE_COLORS,
        )
        plotly_chart(fig)
    with c2:
        triage_counts = patients["triage_category"].value_counts().rename_axis("category").reset_index(name="patients")
        fig = px.pie(
            triage_counts,
            names="category",
            values="patients",
            hole=0.48,
            title="Triage distribution",
            color="category",
            color_discrete_map=cfg.TRIAGE_COLORS,
        )
        plotly_chart(fig)
    with c3:
        uncertainty_counts = patients["uncertainty_level"].value_counts().rename_axis("level").reset_index(name="patients")
        fig = px.bar(
            uncertainty_counts,
            x="level",
            y="patients",
            title="Uncertainty distribution",
            labels={"level": "Uncertainty", "patients": "Patients"},
            color="level",
            color_discrete_map={"low": "#2a9d8f", "moderate": "#f4a261", "high": "#e76f51"},
        )
        plotly_chart(fig)
    st.info(
        "Mode context: cohort patient predictions were generated by the pre-lab model. "
        "Changing model mode updates the verified track metrics and batch-inference pipeline."
    )


elif page == "Patient-level Prediction":
    st.title("Patient-level Prediction")
    case_type = st.selectbox(
        "Case shortcut",
        ["Select patient", "High confidence", "Co-infection", "High uncertainty", "Urgent priority", "False-negative risk"],
    )
    candidates = patients
    if case_type == "High confidence":
        candidates = patients[patients["uncertainty_level"] == "low"]
    elif case_type == "Co-infection":
        candidates = patients[patients["predicted_labels"].map(lambda value: len(du.parse_label_set(value)) > 1)]
    elif case_type == "High uncertainty":
        candidates = patients[patients["uncertainty_level"] == "high"]
    elif case_type == "Urgent priority":
        candidates = patients[patients["triage_category"] == "Urgent Response Priority"]
    elif case_type == "False-negative risk" and "true_labels" in patients:
        candidates = patients[
            patients.apply(
                lambda row: bool(set(du.parse_label_set(row["true_labels"])) - set(du.parse_label_set(row["predicted_labels"]))),
                axis=1,
            )
        ]
    if candidates.empty:
        st.warning("No patient matches this case shortcut; showing the full cohort.")
        candidates = patients
    patient_id = st.selectbox("Patient ID", candidates["uuid"].astype(str).tolist())
    row = candidates[candidates["uuid"].astype(str) == patient_id].iloc[0]

    metrics = st.columns(5)
    metrics[0].metric("Triage", row.get("triage_category", "Unavailable"))
    metrics[1].metric("Triage score", row.get("triage_score", "Unavailable"))
    metrics[2].metric("Uncertainty", row.get("uncertainty_level", "Unavailable"))
    metrics[3].metric("Co-infection probability", row.get("coinfection_prob", "Unavailable"))
    metrics[4].metric("Conformal set size", len(du.parse_label_set(row.get("conformal_set", ""))))
    st.write(f"**Predicted labels:** {row.get('predicted_labels', 'Unavailable')}")
    st.write(f"**Conformal prediction set:** {row.get('conformal_set', 'Unavailable')}")
    st.write(f"**Recommended action:** {row.get('recommended_action', 'Clinical review required.')}")

    c1, c2 = st.columns([3, 2])
    with c1:
        probabilities = label_probabilities(row, labels)
        if not probabilities.empty:
            fig = px.bar(
                probabilities,
                x="probability",
                y="disease",
                orientation="h",
                range_x=[0, 1],
                title="Calibrated disease probabilities",
                labels={"probability": "Probability", "disease": "Disease"},
                color="disease",
                color_discrete_map=cfg.DISEASE_COLORS,
            )
            plotly_chart(fig)
    with c2:
        st.info(
            "**What this means**\n\n"
            "The predicted labels are diseases whose probabilities cross the selected "
            "decision threshold. A larger conformal set means the system cannot safely "
            "narrow the case to one disease. High uncertainty should trigger manual review."
        )
        explanation = row.get("explanation_summary")
        if explanation:
            st.write("**Top contributing signals**")
            st.write(explanation)
        else:
            st.caption("Patient-specific explanation text is unavailable; see the Explainability page.")
    report = du.patient_markdown_report(row)
    st.download_button(
        "Download one-page patient report",
        report.encode("utf-8"),
        file_name=f"vectra_x_patient_{patient_id}.md",
        mime="text/markdown",
    )


elif page == "Batch Prediction / Upload":
    st.title("Batch Prediction / Upload")
    st.write(
        "Upload a CSV using the original dataset schema. The selected saved pipeline "
        "generates probabilities without retraining."
    )
    if not mode["available"]:
        st.warning("This model mode cannot run uploaded inference. Select Pre-lab or Lab-aware.")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is not None and mode["available"]:
        try:
            content = uploaded.getvalue()
            try:
                upload_frame = pd.read_csv(io.BytesIO(content), sep=";", decimal=",")
                if upload_frame.shape[1] == 1:
                    upload_frame = pd.read_csv(io.BytesIO(content))
            except (UnicodeDecodeError, pd.errors.ParserError):
                upload_frame = pd.read_csv(io.BytesIO(content), encoding="latin1", sep=";", decimal=",")
            with st.spinner("Running saved-model inference..."):
                result, validation = du.predict_uploaded_frame(upload_frame, mode_name, policy_name)
            st.success(f"Generated predictions for {len(result)} rows.")
            if validation.extra:
                st.caption(f"{len(validation.extra)} extra columns were ignored by the selected model.")
            st.dataframe(result, width="stretch", height=420)
            download_frame("Download prediction CSV", result, "vectra_x_batch_predictions.csv", "batch_download")
        except Exception as exc:
            st.error(str(exc))
            st.info(
                "Fallback demonstration: the precomputed cohort table remains available below. "
                "Use the original dataset column names to enable saved-model inference."
            )
    with st.expander("Precomputed prediction table fallback"):
        st.dataframe(patients.head(100), width="stretch")
        download_frame(
            "Download precomputed patient predictions",
            patients,
            "vectra_x_precomputed_predictions.csv",
            "precomputed_download",
        )


elif page == "Population Overview":
    st.title("Population Overview")
    filtered = patients.copy()
    filter_columns = {
        "Gender": find_column(filtered, ["genre", "gender"]),
        "Center": find_column(filtered, ["centre de santé", "health center", "center"]),
        "Age": find_column(filtered, ["âge", "age"]),
        "Region": find_column(filtered, ["region", "location", "province", "district"]),
    }
    control_cols = st.columns(4)
    for index, (label, column) in enumerate(filter_columns.items()):
        if column and label != "Age":
            choices = sorted(filtered[column].dropna().astype(str).unique().tolist())
            selected = control_cols[index].multiselect(label, choices)
            if selected:
                filtered = filtered[filtered[column].astype(str).isin(selected)]
    triage_filter = st.multiselect("Triage category", cfg.TRIAGE_ORDER)
    if triage_filter:
        filtered = filtered[filtered["triage_category"].isin(triage_filter)]
    uncertainty_filter = st.multiselect("Uncertainty", ["low", "moderate", "high"])
    if uncertainty_filter:
        filtered = filtered[filtered["uncertainty_level"].isin(uncertainty_filter)]
    disease_filter = st.selectbox("Predicted disease", ["All"] + labels)
    if disease_filter != "All":
        filtered = filtered[filtered["predicted_labels"].str.contains(disease_filter, regex=False, na=False)]

    cards = st.columns(4)
    cards[0].metric("Filtered patients", len(filtered))
    cards[1].metric(
        "High-priority proportion",
        f"{100 * filtered['triage_category'].isin(['Confirmatory Test Priority', 'Urgent Response Priority']).mean():.1f}%"
        if len(filtered)
        else "0.0%",
    )
    cards[2].metric(
        "Predicted co-infection",
        int(filtered["predicted_labels"].map(lambda value: len(du.parse_label_set(value)) > 1).sum()),
    )
    cards[3].metric("High uncertainty", int((filtered["uncertainty_level"] == "high").sum()))
    disease_rows = [
        {"disease": label, "patients": int(filtered["predicted_labels"].str.contains(label, regex=False, na=False).sum())}
        for label in labels
    ]
    c1, c2 = st.columns(2)
    with c1:
        plotly_chart(
            px.bar(
                pd.DataFrame(disease_rows),
                x="disease",
                y="patients",
                title="Predicted prevalence in filtered cohort",
                color="disease",
                color_discrete_map=cfg.DISEASE_COLORS,
            )
        )
    with c2:
        subgroup_col = filter_columns["Center"] or filter_columns["Gender"]
        if subgroup_col:
            breakdown = filtered.groupby([subgroup_col, "triage_category"]).size().reset_index(name="patients")
            plotly_chart(
                px.bar(
                    breakdown,
                    x=subgroup_col,
                    y="patients",
                    color="triage_category",
                    barmode="stack",
                    title="Triage by available subgroup",
                    color_discrete_map=cfg.TRIAGE_COLORS,
                )
            )
        else:
            st.info("No subgroup column was available for this view.")
    date_col = find_column(filtered, ["date", "timestamp"])
    location_col = filter_columns["Region"]
    if not date_col or not location_col:
        st.info(
            "No timestamp/location fields were available, so temporal/geospatial outbreak "
            "monitoring is provided as a future deployment extension."
        )
    download_frame("Download filtered triage output", filtered, "vectra_x_filtered_triage.csv", "population_download")


elif page == "Resource Prioritization":
    st.title("Resource Prioritization")
    st.write("Adjust capacity assumptions and compare them with the current triage demand.")
    c1, c2, c3, c4 = st.columns(4)
    rapid_tests = c1.number_input("Rapid tests available", min_value=0, value=100, step=5)
    beds = c2.number_input("Beds available", min_value=0, value=50, step=5)
    monitoring = c3.number_input("Monitoring capacity", min_value=0, value=150, step=5)
    staff = c4.number_input("Staff review capacity", min_value=0, value=200, step=5)
    capacity = du.calculate_resource_capacity(patients, rapid_tests, beds, monitoring, staff)
    urgent = int((patients["triage_category"] == "Urgent Response Priority").sum())
    confirm = int(
        patients["triage_category"].isin(["Confirmatory Test Priority", "Urgent Response Priority"]).sum()
    )
    cards = st.columns(4)
    cards[0].metric("Urgent patients", urgent)
    cards[1].metric("Confirmatory-test demand", confirm)
    cards[2].metric("Dominant prediction", du.dominant_predicted_disease(patients))
    cards[3].metric("Insufficient resources", int((capacity["gap"] < 0).sum()))
    long_capacity = capacity.melt(
        id_vars="resource", value_vars=["demand", "capacity"], var_name="measure", value_name="count"
    )
    plotly_chart(
        px.bar(
            long_capacity,
            x="resource",
            y="count",
            color="measure",
            barmode="group",
            title="Resource demand versus capacity",
        )
    )
    st.dataframe(capacity, width="stretch")
    if (capacity["gap"] < 0).any():
        shortages = ", ".join(capacity.loc[capacity["gap"] < 0, "resource"])
        st.error(f"Current capacity is insufficient for: {shortages}. Prioritize urgent and high-uncertainty cases.")
    else:
        st.success("Current capacity is sufficient under these assumptions.")
    st.info(
        f"Prioritize confirmatory testing for patients flagged under the **{policy_name}** policy. "
        "High-uncertainty cases should be reviewed manually."
    )
    tradeoff = table("threshold_policy_resource_tradeoff.csv")
    if not tradeoff.empty:
        st.subheader("Threshold policy comparison")
        st.dataframe(tradeoff, width="stretch")
        plotly_chart(
            px.bar(
                tradeoff,
                x="policy",
                y="total_flags",
                title="Operational burden by threshold policy",
                labels={"total_flags": "Total disease flags", "policy": "Policy"},
            )
        )
    download_frame("Download resource scenario", capacity, "vectra_x_resource_scenario.csv", "resource_download")


elif page == "Model Trust":
    st.title("Model Trust")
    track = mode["track"]
    metrics = data_summary.get("test_metrics", {}).get(track, {})
    cards = st.columns(5)
    for column, key in zip(
        cards,
        ["macro_f1", "micro_f1", "weighted_f1", "macro_recall", "macro_pr_auc"],
    ):
        column.metric(key.replace("_", " ").title(), metrics.get(key, "Unavailable"))
    st.caption(
        "Macro metrics give each disease equal weight. Recall is emphasized because missed "
        "rare or severe disease labels can be operationally costly."
    )
    leaderboard = table("model_leaderboard.csv")
    if not leaderboard.empty:
        st.subheader("Model leaderboard")
        st.dataframe(leaderboard, width="stretch", height=360)
        plot = leaderboard[leaderboard["track"] == track].copy()
        if not plot.empty:
            plotly_chart(
                px.bar(
                    plot.sort_values("macro_f1"),
                    x="macro_f1",
                    y="model",
                    orientation="h",
                    title=f"{track} model comparison",
                )
            )
        download_frame("Download leaderboard", leaderboard, "vectra_x_model_leaderboard.csv", "leaderboard_download")
    per_label = table("per_label_metrics.csv")
    per_label = per_label[per_label["track"] == track] if not per_label.empty else per_label
    if not per_label.empty:
        st.subheader("Per-label precision, recall, and F1")
        st.dataframe(per_label, width="stretch")
        metric_long = per_label.melt(
            id_vars="label", value_vars=["precision", "recall", "f1"], var_name="metric", value_name="score"
        )
        plotly_chart(
            px.bar(metric_long, x="label", y="score", color="metric", barmode="group", range_y=[0, 1])
        )
    tabs = st.tabs(["Confusion matrices", "Calibration", "ROC / PR", "Threshold policies"])
    with tabs[0]:
        figure_image("confusion_matrices.png", "Per-label confusion matrices for the primary pre-lab model.")
    with tabs[1]:
        figure_image("calibration_curves.png", "Reliability curves indicate whether probability claims are trustworthy.")
        st.dataframe(table("calibration_metrics.csv"), width="stretch")
    with tabs[2]:
        c1, c2 = st.columns(2)
        with c1:
            figure_image("roc_curves.png", "ROC curves")
        with c2:
            figure_image("pr_curves.png", "Precision-recall curves")
    with tabs[3]:
        st.dataframe(table("threshold_policies.csv"), width="stretch")
    if track == "FULL":
        st.warning("Full-feature performance is a leakage demonstration and must not be presented as deployable.")


elif page == "Explainability":
    st.title("Explainability")
    st.warning(
        "Because features may be anonymized or encrypted, explanations are model-based "
        "statistical signals, not direct medical causality."
    )
    global_importance = table("feature_importance_global.csv")
    per_label_importance = table("feature_importance_per_label.csv")
    if not global_importance.empty:
        top = global_importance.head(20).sort_values("importance_mean")
        plotly_chart(
            px.bar(
                top,
                x="importance_mean",
                y="feature",
                orientation="h",
                title="Global permutation importance",
                labels={"importance_mean": "Mean importance", "feature": "Feature"},
            )
        )
        st.dataframe(global_importance, width="stretch")
    if not per_label_importance.empty and "label" in per_label_importance:
        selected_label = st.selectbox("Disease explanation", labels)
        local = per_label_importance[per_label_importance["label"] == selected_label].head(15)
        if not local.empty:
            plotly_chart(
                px.bar(
                    local.sort_values("importance_mean"),
                    x="importance_mean",
                    y="feature",
                    orientation="h",
                    title=f"Top features for {selected_label}",
                )
            )
    patient_id = st.selectbox("Local patient case", patients["uuid"].astype(str).tolist(), key="xai_patient")
    row = patients[patients["uuid"].astype(str) == patient_id].iloc[0]
    if row.get("explanation_summary"):
        st.write(row["explanation_summary"])
    else:
        figure_image("local_explanation_examples.png", "Representative local explanation cases")
    if (cfg.FIGURES / "shap_summary.png").exists():
        with st.expander("Optional SHAP summary"):
            figure_image("shap_summary.png", "SHAP summary for the available label/model.")


elif page == "Uncertainty & Conformal":
    st.title("Uncertainty & Conformal Prediction")
    conformal = data_summary.get("conformal", {})
    cards = st.columns(4)
    cards[0].metric("Target coverage", "90%")
    cards[1].metric("Empirical coverage", conformal.get("overall_coverage", "Unavailable"))
    cards[2].metric("Average set size", conformal.get("avg_set_size", "Unavailable"))
    cards[3].metric("Ambiguous sets", f"{conformal.get('pct_ambiguous_multi', 'Unavailable')}%")
    st.info(
        "Conformal prediction returns a set of plausible diseases instead of forcing a "
        "single answer. Larger sets signal that confirmatory testing or manual review is safer."
    )
    counts = patients.groupby(["uncertainty_level", "triage_category"]).size().reset_index(name="patients")
    plotly_chart(
        px.bar(
            counts,
            x="uncertainty_level",
            y="patients",
            color="triage_category",
            barmode="stack",
            title="How uncertainty affects triage",
            color_discrete_map=cfg.TRIAGE_COLORS,
        )
    )
    example_tabs = st.tabs(["Low uncertainty", "High uncertainty", "Multi-disease set"])
    examples = [
        patients[patients["uncertainty_level"] == "low"],
        patients[patients["uncertainty_level"] == "high"],
        patients[patients["conformal_set"].map(lambda value: len(du.parse_label_set(value)) > 1)],
    ]
    for tab, frame in zip(example_tabs, examples):
        with tab:
            columns = ["uuid", "predicted_labels", "conformal_set", "uncertainty_level", "triage_category"]
            st.dataframe(frame[[c for c in columns if c in frame]].head(10), width="stretch")
    st.subheader("Per-label coverage")
    st.dataframe(table("conformal_metrics.csv"), width="stretch")


elif page == "Fairness & Robustness":
    st.title("Fairness & Robustness")
    fairness = table("fairness_metrics.csv")
    gaps = table("fairness_recall_gaps.csv")
    if not fairness.empty:
        axes = sorted(fairness["axis"].dropna().unique().tolist()) if "axis" in fairness else []
        selected_axis = st.selectbox("Subgroup axis", axes) if axes else None
        view = fairness[fairness["axis"] == selected_axis] if selected_axis else fairness
        st.dataframe(view, width="stretch")
    if not gaps.empty:
        plotly_chart(
            px.bar(
                gaps,
                x="label",
                y="recall_gap",
                color="axis",
                barmode="group",
                title="Recall disparity by subgroup",
                labels={"recall_gap": "Maximum recall gap", "label": "Disease"},
            )
        )
    else:
        figure_image("fairness_recall_gap.png", "Fairness recall gaps")
    loco = table("leave_one_center_out.csv")
    if not loco.empty:
        st.subheader("Leave-one-center-out stress test")
        st.dataframe(loco, width="stretch")
        st.warning(
            "Performance decreases across health centers. Prospective deployment requires "
            "facility-specific validation and likely recalibration."
        )
    st.caption(
        "Subgroup analysis is constrained by the small dataset. Missingness groups and "
        "center transfer are robustness indicators, not proof of clinical fairness."
    )


elif page == "Methodology & Limitations":
    st.title("Methodology & Limitations")
    tabs = st.tabs(["Methodology", "Feature stages", "Leakage", "Ethics", "Reproducibility"])
    with tabs[0]:
        st.markdown(
            """
            VECTRA-X uses multi-label binary relevance with multi-label stratified
            evaluation. The primary model is selected by out-of-fold macro PR-AUC,
            followed by per-label threshold tuning, probability calibration, conformal
            prediction, uncertainty estimation, co-infection modeling, and transparent
            triage rules.
            """
        )
    with tabs[1]:
        st.dataframe(table("feature_sets.csv"), width="stretch")
        st.markdown(
            "- **Pre-lab:** demographics, symptoms, and available vital signs.\n"
            "- **Lab-aware:** adds ordered test information for confirmation support.\n"
            "- **Full-feature:** includes research-only leakage candidates and is not deployable."
        )
    with tabs[2]:
        text = report_text("leakage_audit.md")
        st.markdown(text if text else "Leakage audit report unavailable.")
    with tabs[3]:
        text = report_text("limitations_and_ethics.md")
        st.markdown(text if text else cfg.SAFETY_NOTE)
    with tabs[4]:
        st.code(
            "python run_pipeline.py --quick\n"
            "jupyter nbconvert --execute --to notebook "
            "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb\n"
            "streamlit run app/streamlit_app.py",
            language="powershell",
        )
        st.write(f"Random seed: `{data_summary.get('random_state', 42)}`")
        st.write(f"Project root: `{Path(cfg.ROOT).name}`")
