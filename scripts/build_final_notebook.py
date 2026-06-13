from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def takeaway(text: str):
    return md(
        f"""
        > **Key Takeaway**
        >
        > {text}
        """
    )


def build_notebook():
    cells = [
        md(
            """
            # 0. Title Page / Executive Summary

            ## VECTRA-X: Explainable and Uncertainty-Aware Triage Intelligence for Vector-Borne Disease Response

            **FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction**

            VECTRA-X is a leakage-aware, multi-label clinical decision-support system
            designed for humanitarian health response. It separates early **pre-lab
            triage** from **lab-aware confirmation**, detects possible co-infection,
            calibrates confidence, returns conformal prediction sets when evidence is
            ambiguous, explains model behavior, and converts predictions into
            transparent triage and resource-planning outputs.

            The primary competition model is the **pre-lab Extra Trees model**, with
            held-out macro F1 of approximately **0.65**, micro F1 of **0.84**, and
            macro recall of **0.73**. A lab-aware model is retained for confirmation
            support, while the full-feature model is shown only to demonstrate how
            target leakage can inflate apparent performance.

            The accompanying Streamlit prototype supports patient selection, saved-model
            CSV inference, threshold-policy changes, population filtering, resource
            simulation, model-trust inspection, uncertainty review, and downloadable
            outputs.

            > **Clinical Safety Statement:** VECTRA-X supports decisions. It does not
            > replace medical professionals, clinical examination, or confirmatory tests.
            """
        ),
        code(
            """
            from pathlib import Path
            import json
            import os
            import sys
            import warnings

            import joblib
            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            from IPython.display import Markdown, display

            warnings.filterwarnings("ignore")

            def find_project_root(start: Path) -> Path:
                start = start.resolve()
                for candidate in [start, *start.parents]:
                    if (candidate / "config" / "config.yaml").exists() and (candidate / "run_pipeline.py").exists():
                        return candidate
                raise FileNotFoundError("Could not locate the VECTRA-X project root.")

            ROOT = find_project_root(Path.cwd())
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))

            TABLES = ROOT / "outputs" / "tables"
            FIGURES = ROOT / "outputs" / "figures"
            REPORTS = ROOT / "outputs" / "reports"
            MODELS = ROOT / "outputs" / "models"
            DASHBOARD_DATA = ROOT / "outputs" / "dashboard_data"
            FINAL_OUTPUT = ROOT / "outputs" / "final_notebook"
            FINAL_OUTPUT.mkdir(parents=True, exist_ok=True)

            RANDOM_STATE = 42
            np.random.seed(RANDOM_STATE)

            # Set True for a deterministic full pipeline rebuild before rendering.
            # The default fast path uses verified saved artifacts and remains executable.
            RECOMPUTE_MODELS = os.environ.get("VECTRA_X_RECOMPUTE", "0") == "1"
            if RECOMPUTE_MODELS:
                from run_pipeline import main as run_full_pipeline
                run_full_pipeline(quick=False, use_cache=False)

            def read_table(name: str) -> pd.DataFrame:
                path = TABLES / name
                return pd.read_csv(path) if path.exists() else pd.DataFrame()

            def read_summary() -> dict:
                path = DASHBOARD_DATA / "summary.json"
                return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

            def show_figure(name: str, caption: str):
                path = FIGURES / name
                if path.exists():
                    display(Markdown(f"![{caption}]({path.as_posix()})"))
                else:
                    display(Markdown(f"*Optional figure unavailable: `{name}`.*"))

            summary = read_summary()
            assert summary, "Dashboard summary is missing. Run `python run_pipeline.py`."
            print(f"Project root: {ROOT}")
            print(f"Execution mode: {'full recomputation' if RECOMPUTE_MODELS else 'verified artifact-backed'}")
            print(f"Random state: {RANDOM_STATE}")
            """
        ),
        takeaway(
            "The notebook is fully executable in artifact-backed mode and supports a "
            "deterministic full rebuild through `VECTRA_X_RECOMPUTE=1`."
        ),
        md(
            """
            # 1. Humanitarian Background

            Vector-borne diseases create an acute triage challenge in endemic and
            resource-constrained settings. Early symptoms overlap, laboratory tests may
            be delayed, and multiple diseases may occur in the same patient. Frontline
            teams therefore need more than a single predicted label: they need an
            indication of urgency, uncertainty, possible co-infection, and the likely
            resource consequence of each decision.

            Explainability matters because health workers and response coordinators must
            understand why a case was flagged. Uncertainty matters because a model should
            defer or return multiple plausible diseases instead of expressing false
            confidence. These principles make VECTRA-X a humanitarian decision-support
            system rather than a generic classification exercise.
            """
        ),
        md(
            """
            # 2. Project Objective

            **Main research question:** Can a leakage-aware, multi-label machine-learning
            system provide clinically honest early triage support for vector-borne disease
            while communicating uncertainty and operational priority?

            Secondary objectives:

            - Predict multiple simultaneous disease labels.
            - Detect possible co-infection.
            - Audit diagnostic and target leakage.
            - Separate pre-lab triage from lab-aware confirmation.
            - Calibrate confidence and construct conformal prediction sets.
            - Prioritize patients through transparent triage rules.
            - Provide explainability, fairness, robustness, and model-trust evidence.
            """
        ),
        md(
            """
            # 3. Data Loading and Dataset Overview

            The official dataset is a semicolon-separated bilingual clinical export with
            decimal-comma formatting. Disease outcomes are represented by multiple binary
            label columns. A patient may therefore have more than one positive diagnosis,
            making this a **multi-label** problem rather than a multi-class problem.
            """
        ),
        code(
            """
            from src import data_loader, label_detection, report_utils

            project_config = report_utils.load_config()
            raw = data_loader.load_raw(project_config)
            label_info = label_detection.detect_labels(raw, project_config)
            y = label_info["y"]
            active_labels = label_info["active_labels"]

            overview = pd.DataFrame({
                "item": ["Patients", "Columns", "Active labels", "Multi-label patients"],
                "value": [len(raw), raw.shape[1], len(active_labels), label_info["n_multilabel_patients"]],
            })
            display(overview)
            display(raw.head(3))
            display(pd.DataFrame({"column": raw.columns, "dtype": raw.dtypes.astype(str)}).head(20))
            print("Active label columns:", active_labels)
            """
        ),
        takeaway(
            "158 of 300 patients carry more than one active diagnosis. Collapsing these "
            "records into a single class would discard clinically important co-infection information."
        ),
        md(
            """
            # 4. Data Quality and Schema Audit

            Data quality checks cover missingness, duplicate rows, constant and
            near-constant columns, feature types, and the available data dictionary.
            Missing values are treated as unknown observations, not negative clinical findings.
            """
        ),
        code(
            """
            missingness = read_table("missingness_summary.csv")
            dictionary = read_table("data_dictionary_auto.csv")
            quality = pd.DataFrame({
                "measure": ["Rows", "Columns", "Duplicate rows", "Constant columns"],
                "value": [
                    raw.shape[0],
                    raw.shape[1],
                    int(raw.duplicated().sum()),
                    summary.get("n_constant_columns", "Unavailable"),
                ],
            })
            display(quality)
            display(missingness.head(15))
            display(dictionary.head(15))

            if not missingness.empty:
                top = missingness.head(15).copy()
                missing_col = next(c for c in top.columns if "missing" in c.lower() and c != "column")
                fig = px.bar(
                    top.sort_values(missing_col),
                    x=missing_col,
                    y="column",
                    orientation="h",
                    title="Features with the highest missingness",
                    labels={missing_col: "Missing values", "column": "Feature"},
                )
                fig.show()
            """
        ),
        takeaway(
            "Substantial missingness in selected vital and laboratory fields supports "
            "explicit missing indicators and reinforces the value of a pre-lab feature track."
        ),
        md(
            """
            # 5. Diagnostic Leakage Audit

            Leakage occurs when a model receives information that would not be available
            at the intended prediction time, including diagnostic results or direct
            restatements of the target. In medical AI, leakage can produce impressive but
            operationally invalid performance.

            VECTRA-X defines:

            - **A. Pre-lab triage:** demographics, symptoms, and available vital signs.
            - **B. Lab-aware confirmation:** adds ordered laboratory or rapid-test information.
            - **C. Full-feature research-only:** includes target-restatement candidates to
              demonstrate the magnitude of leakage.

            The pre-lab model is the primary deployable model.
            """
        ),
        code(
            """
            leakage = read_table("leakage_candidates.csv")
            feature_sets = read_table("feature_sets.csv")
            display(feature_sets)
            display(leakage.head(20))
            leakage.to_csv(FINAL_OUTPUT / "leakage_candidates.csv", index=False)
            """
        ),
        takeaway(
            "The feature named `Dengue (Dengua)` behaves like a target restatement. "
            "VECTRA-X excludes it from deployable models and uses it only as a leakage demonstration."
        ),
        md(
            """
            # 6. Exploratory Data Analysis

            The exploratory analysis focuses on disease imbalance, label cardinality,
            co-occurrence, missingness, demographics, feature associations, and the
            structure of co-infection. Every view is interpreted in relation to model
            design and operational risk.
            """
        ),
        code(
            """
            label_distribution = read_table("label_distribution.csv")
            cooccurrence = read_table("label_cooccurrence.csv")
            combinations = read_table("label_top_combinations.csv")

            fig = px.bar(
                label_distribution,
                x="label",
                y="positives",
                color="label",
                title="Disease label distribution",
                labels={"label": "Disease", "positives": "Positive patients"},
            )
            fig.show()

            cardinality = y.sum(axis=1).value_counts().sort_index().rename_axis("labels_per_patient").reset_index(name="patients")
            px.bar(
                cardinality,
                x="labels_per_patient",
                y="patients",
                title="Multi-label cardinality",
                labels={"labels_per_patient": "Active disease labels per patient", "patients": "Patients"},
            ).show()

            matrix = y.corr()
            px.imshow(
                matrix,
                text_auto=".2f",
                color_continuous_scale="RdBu",
                zmin=-1,
                zmax=1,
                title="Disease label association matrix",
                labels={"x": "Disease", "y": "Disease", "color": "Association"},
            ).show()

            display(combinations.head(10))
            show_figure("demographics.png", "Available demographic and center distributions")
            show_figure("feature_projection_pca.png", "PCA projection of pre-lab features")
            """
        ),
        takeaway(
            "Malaria dominates the dataset, while co-diagnosis is common. Macro metrics, "
            "per-label recall, and explicit co-infection modeling are therefore more informative than accuracy."
        ),
        md(
            """
            # 7. Modeling Strategy

            VECTRA-X uses binary relevance as the primary multi-label strategy, with a
            classifier-chain benchmark to explore label dependence. Macro F1 and macro
            PR-AUC prevent the dominant malaria label from masking poor rare-label
            performance. Per-label thresholds are optimized because a universal 0.5
            threshold is not appropriate under severe imbalance.

            Calibration and conformal prediction are added because triage decisions depend
            on confidence quality, not only ranking performance. Pre-lab and lab-aware
            models remain separate because their information availability and deployment
            roles are fundamentally different.
            """
        ),
        md(
            """
            # 8. Preprocessing Pipeline

            The deterministic cleaning layer parses decimal-comma numerics, blood pressure,
            binary yes/no fields, center and gender fields, low-cardinality categorical
            features, and missing indicators. Stateful imputation and scaling are fitted
            inside cross-validation folds to prevent information leakage.

            Multi-label stratified splitting preserves label prevalence and co-occurrence.
            Random state 42 is used throughout for reproducibility.
            """
        ),
        code(
            """
            from src import preprocessing
            pre_lab_raw = pd.read_csv(ROOT / "data" / "processed" / "X_pre_lab.csv")
            print(f"Saved pre-lab design source: {pre_lab_raw.shape}")
            print("Reproducibility seed:", RANDOM_STATE)
            """
        ),
        md(
            """
            # 9. Baseline Models

            Logistic regression provides the interpretable linear baseline. Random Forest
            and Extra Trees test whether nonlinear symptom interactions improve performance.
            A baseline is valuable because it reveals whether added model complexity produces
            meaningful gains rather than cosmetic leaderboard differences.
            """
        ),
        code(
            """
            leaderboard = read_table("model_leaderboard.csv")
            baselines = leaderboard[leaderboard["model"].isin(["logreg", "random_forest"])].copy()
            display(baselines[["track", "model", "macro_f1", "micro_f1", "macro_pr_auc"]])
            """
        ),
        takeaway(
            "The baseline establishes a credible lower bound and shows that model selection "
            "must consider rare-label and probability-ranking metrics, not accuracy alone."
        ),
        md(
            """
            # 10. Advanced Model Benchmark

            The benchmark compares Logistic Regression, Random Forest, Extra Trees,
            HistGradientBoosting, XGBoost, LightGBM, and a supplemental classifier chain
            when available. Selection is based on out-of-fold macro PR-AUC on the training
            partition, followed by evaluation on a held-out test set.
            """
        ),
        code(
            """
            display(leaderboard)
            px.bar(
                leaderboard,
                x="model",
                y="macro_f1",
                color="track",
                barmode="group",
                title="Advanced model leaderboard by feature track",
                labels={"model": "Model", "macro_f1": "Out-of-fold macro F1", "track": "Feature track"},
            ).show()
            leaderboard.to_csv(FINAL_OUTPUT / "model_leaderboard.csv", index=False)
            """
        ),
        takeaway(
            "Extra Trees is selected for pre-lab triage. Higher full-feature performance "
            "is not accepted as deployment evidence because the track contains target-restatement leakage."
        ),
        md(
            """
            # 11. Pre-Lab Triage Model

            This is the primary competition model because it uses information intended to
            be available before laboratory confirmation. Evaluation includes micro, macro,
            weighted, and samples F1; Hamming loss; subset accuracy; per-label precision,
            recall, and F1; confusion matrices; and false-negative analysis.
            """
        ),
        code(
            """
            pre_metrics = summary["test_metrics"]["PRE_LAB"]
            display(pd.DataFrame([pre_metrics]).T.rename(columns={0: "PRE_LAB"}))
            per_label = read_table("per_label_metrics.csv")
            pre_label = per_label[per_label["track"] == "PRE_LAB"].copy()
            display(pre_label)
            px.bar(
                pre_label,
                x="label",
                y="recall",
                color="label",
                range_y=[0, 1],
                title="Pre-lab recall by disease label",
                labels={"label": "Disease", "recall": "Recall"},
            ).show()
            false_negative = pre_label[["label", "support_pos", "fn", "false_negative_rate"]].sort_values(
                "false_negative_rate", ascending=False
            )
            display(false_negative)
            show_figure("confusion_matrices.png", "Pre-lab confusion matrices by label")
            """
        ),
        takeaway(
            "Pre-lab micro F1 is strong, but typhoid and other rare-label false negatives "
            "remain a safety concern. VECTRA-X therefore combines threshold policy, uncertainty, and manual review."
        ),
        md(
            """
            # 12. Lab-Aware Confirmation Model

            The lab-aware model is a confirmation-support model for settings where ordered
            test results are already available. It must not be described as the early
            triage model. Performance changes are interpreted together with the cost and
            timing of obtaining laboratory information.
            """
        ),
        code(
            """
            comparison = pd.DataFrame(summary["test_metrics"]).T[
                ["macro_f1", "micro_f1", "weighted_f1", "macro_recall", "macro_pr_auc"]
            ]
            display(comparison.loc[["PRE_LAB", "LAB_AWARE"]])
            comparison.loc[["PRE_LAB", "LAB_AWARE"]].plot(kind="bar", figsize=(10, 4), title="Pre-lab versus lab-aware held-out metrics")
            """
        ),
        takeaway(
            "Laboratory availability changes the model's role. VECTRA-X preserves this "
            "distinction instead of mixing confirmation evidence into an early-triage claim."
        ),
        md(
            """
            # 13. Full-Feature Leakage Demonstration

            The full-feature track deliberately shows what happens when a target-restatement
            variable enters the feature matrix. Unrealistically strong performance is
            treated as evidence of leakage awareness, not as the headline model result.
            """
        ),
        code(
            """
            display(comparison.loc[["PRE_LAB", "FULL"]])
            dengue = per_label[(per_label["label"] == "dengue") & per_label["track"].isin(["PRE_LAB", "FULL"])]
            display(dengue[["track", "precision", "recall", "f1", "roc_auc", "pr_auc"]])
            """
        ),
        takeaway(
            "Dengue F1 increases sharply in the full track because a leakage candidate "
            "nearly restates the outcome. The result strengthens the methodological defense for the pre-lab model."
        ),
        md(
            """
            # 14. Threshold Optimization

            A default threshold of 0.5 does not reflect disease imbalance or asymmetric
            clinical cost. VECTRA-X defines three policies:

            - **Performance:** maximize per-label F1.
            - **Safety:** lower selected severe or rare-label thresholds to improve recall.
            - **Operational:** balance recall with confirmatory-test and review capacity.
            """
        ),
        code(
            """
            policies = read_table("threshold_policies.csv")
            display(policies)
            policy_long = policies.melt(id_vars="label", var_name="policy", value_name="threshold")
            px.line(
                policy_long,
                x="label",
                y="threshold",
                color="policy",
                markers=True,
                title="Per-label threshold policies",
                labels={"label": "Disease", "threshold": "Decision threshold", "policy": "Policy"},
            ).show()
            """
        ),
        takeaway(
            "The operational policy is recommended for the main demonstration because it "
            "connects model behavior to realistic response capacity; the safety policy is available for sensitivity analysis."
        ),
        md(
            """
            # 15. Calibration

            Calibration asks whether a predicted probability corresponds to observed
            frequency. This matters for triage because a confidence score should support
            prioritization and communication, not merely rank patients.
            """
        ),
        code(
            """
            calibration = read_table("calibration_metrics.csv")
            display(calibration)
            show_figure("calibration_curves.png", "Calibration curves for the primary pre-lab model")
            """
        ),
        takeaway(
            "The mean pre-lab Brier score is reported from the verified summary artifact. "
            "Calibration evidence is shown alongside discrimination metrics."
        ),
        md(
            """
            # 16. Uncertainty Estimation

            Patient uncertainty combines predictive entropy, confidence, top-two margin,
            and conformal set size. Low uncertainty suggests a comparatively stable model
            output; high uncertainty indicates that manual review or confirmatory testing
            should receive greater priority.
            """
        ),
        code(
            """
            uncertainty = read_table("patient_uncertainty_scores.csv")
            display(uncertainty["uncertainty_level"].value_counts().rename_axis("level").reset_index(name="patients"))
            px.histogram(
                uncertainty,
                x="mean_entropy",
                color="uncertainty_level",
                nbins=25,
                title="Patient uncertainty score distribution",
                labels={"mean_entropy": "Mean predictive entropy", "count": "Patients"},
            ).show()
            """
        ),
        md(
            """
            # 17. Conformal Prediction

            Conformal prediction produces a set of plausible diseases rather than forcing
            one answer. Coverage describes how often the true label is included; average
            set size describes how specific the system can be. In ambiguous cases, a
            multi-disease set is safer than an overconfident single diagnosis.
            """
        ),
        code(
            """
            conformal_metrics = read_table("conformal_metrics.csv")
            conformal_examples = read_table("conformal_prediction_examples.csv")
            display(pd.DataFrame([summary["conformal"]]))
            display(conformal_metrics)
            display(conformal_examples.head(12))
            """
        ),
        takeaway(
            "Empirical coverage and average set size are reported from the verified "
            "conformal artifact. The broad sets "
            "appropriately communicate ambiguity, but rare-label coverage remains limited by sample size."
        ),
        md(
            """
            # 18. Explainability

            Global and per-label permutation importance describe which signals affect model
            performance. Local explanations illustrate representative patient cases. SHAP
            is included when available, with permutation importance retained as the
            dependency-light fallback.

            > **Warning:** Because features may be anonymized or encrypted, explanations
            > are model-based statistical signals, not direct medical causality.
            """
        ),
        code(
            """
            importance_global = read_table("feature_importance_global.csv")
            importance_label = read_table("feature_importance_per_label.csv")
            display(importance_global.head(20))
            if not importance_global.empty:
                px.bar(
                    importance_global.head(20).sort_values("importance_mean"),
                    x="importance_mean",
                    y="feature",
                    orientation="h",
                    title="Global permutation importance",
                    labels={"importance_mean": "Mean importance", "feature": "Feature"},
                ).show()
            display(importance_label.groupby("label").head(5))
            show_figure("local_explanation_examples.png", "Representative local patient explanations")
            show_figure("shap_summary.png", "Optional SHAP summary")
            """
        ),
        md(
            """
            # 19. Fairness and Robustness Audit

            Performance is evaluated across available center, gender, and age-group
            subgroups. Recall gaps and false-negative behavior are emphasized. A
            leave-one-center-out test measures whether the system transfers across
            facilities with different workflows or patient distributions.
            """
        ),
        code(
            """
            fairness = read_table("fairness_metrics.csv")
            fairness_gaps = read_table("fairness_recall_gaps.csv")
            loco = read_table("leave_one_center_out.csv")
            display(fairness)
            display(fairness_gaps)
            display(loco)
            if not fairness_gaps.empty:
                px.bar(
                    fairness_gaps,
                    x="label",
                    y="recall_gap",
                    color="axis",
                    barmode="group",
                    title="Subgroup recall gaps",
                    labels={"label": "Disease", "recall_gap": "Maximum recall gap", "axis": "Audit axis"},
                ).show()
            """
        ),
        takeaway(
            "Leave-one-center-out macro F1 falls to approximately 0.38. This is a major "
            "generalization limitation and a strong argument for prospective, facility-specific validation."
        ),
        md(
            """
            # 20. Co-Infection Detection

            A separate binary model estimates whether a patient carries more than one
            active diagnosis. This supports confirmatory-test prioritization and resource
            planning beyond the individual disease classifiers.
            """
        ),
        code(
            """
            coinfection = read_table("coinfection_model_metrics.csv")
            display(coinfection)
            px.bar(
                coinfection,
                x="model",
                y=["roc_auc", "pr_auc"],
                barmode="group",
                title="Co-infection model benchmark",
                labels={"value": "Score", "model": "Model", "variable": "Metric"},
            ).show()
            """
        ),
        takeaway(
            "The best co-infection detector reports strong ROC-AUC and recall, indicating that pre-lab signals "
            "contain useful information about multi-disease burden."
        ),
        md(
            """
            # 21. VECTRA-X Triage Engine

            The triage score combines label-weighted calibrated risk, severe-disease
            probability, uncertainty, and co-infection probability. Transparent rules map
            patients to:

            - Routine Monitoring
            - Clinical Review
            - Confirmatory Test Priority
            - Urgent Response Priority

            The result is an operational recommendation, not a treatment instruction.
            """
        ),
        code(
            """
            patients = read_table("vectra_patient_level_predictions.csv")

            def label_count(value):
                text = str(value).strip("{}")
                return 0 if not text or text == "none" else len([x for x in text.split(",") if x.strip()])

            case_frames = {
                "high_confidence_single_disease": patients[
                    (patients["uncertainty_level"] == "low") &
                    (patients["predicted_labels"].map(label_count) == 1)
                ],
                "coinfection_case": patients[patients["predicted_labels"].map(label_count) > 1],
                "high_uncertainty_case": patients[patients["uncertainty_level"] == "high"],
                "urgent_priority_case": patients[patients["triage_category"] == "Urgent Response Priority"],
                "false_negative_risk_case": patients[
                    patients.apply(
                        lambda row: bool(
                            set(str(row.get("true_labels", "")).strip("{}").split(", ")) -
                            set(str(row.get("predicted_labels", "")).strip("{}").split(", "))
                        ),
                        axis=1,
                    )
                ],
            }
            case_cards = pd.concat(
                [frame.head(1).assign(case_type=name) for name, frame in case_frames.items() if not frame.empty],
                ignore_index=True,
            )
            columns = [
                "case_type", "uuid", "predicted_labels", "true_labels", "conformal_set",
                "coinfection_prob", "uncertainty_level", "triage_score",
                "triage_category", "recommended_action",
            ]
            display(case_cards[[c for c in columns if c in case_cards]])
            case_cards.to_csv(FINAL_OUTPUT / "patient_case_cards.csv", index=False)
            """
        ),
        takeaway(
            "The triage layer converts probabilistic outputs into transparent response "
            "categories while preserving uncertainty and the need for clinical review."
        ),
        md(
            """
            # 22. Resource Prioritization Simulation

            Resource simulation estimates urgent patients, confirmatory-test demand,
            monitoring need, dominant predicted diseases, and operational burden under
            different threshold policies. Assumptions are intentionally transparent and
            are adjustable in the Streamlit dashboard.
            """
        ),
        code(
            """
            resource = read_table("resource_simulation.csv")
            policy_resource = read_table("threshold_policy_resource_tradeoff.csv")
            display(resource)
            display(policy_resource)
            px.bar(
                policy_resource,
                x="policy",
                y="total_flags",
                title="Threshold policy and operational burden",
                labels={"policy": "Threshold policy", "total_flags": "Total disease flags"},
            ).show()
            resource.to_csv(FINAL_OUTPUT / "resource_simulation.csv", index=False)
            """
        ),
        takeaway(
            "Threshold selection changes workload. Presenting this trade-off makes "
            "VECTRA-X a response-planning system rather than an isolated predictive model."
        ),
        md(
            """
            # 23. Dashboard Prototype Overview

            The Streamlit dashboard is a functional prototype rather than a static report.
            Judges can:

            - Switch between pre-lab, lab-aware, and research-only model contexts.
            - Change threshold policy.
            - Select representative or individual patients.
            - Upload original-schema CSV files for saved-model inference.
            - Filter the population and download triage outputs.
            - Adjust rapid-test, bed, monitoring, and staff capacity.
            - Inspect model performance, calibration, uncertainty, explainability, and fairness.

            Run from the project root:

            ```powershell
            streamlit run app/streamlit_app.py
            ```
            """
        ),
        md(
            """
            # 24. Final Discussion

            VECTRA-X differs from generic disease classification in five ways:

            1. It preserves multi-label and co-infection structure.
            2. It explicitly separates pre-lab triage from lab-aware confirmation.
            3. It treats leakage detection as a methodological contribution.
            4. It communicates calibrated confidence, uncertainty, and conformal sets.
            5. It connects predictions to triage and resource decisions.

            ## Why VECTRA-X Can Win

            Many competitor solutions are likely to present a single XGBoost classifier,
            accuracy, a small set of EDA charts, and a static dashboard. VECTRA-X offers a
            stronger scientific defense and a more complete humanitarian workflow. It
            shows not only which model performs best, but which information is available
            at each clinical stage, when the model is uncertain, where it may fail across
            facilities, and how its outputs change response capacity.
            """
        ),
        md(
            """
            # 25. Limitations and Ethics

            - VECTRA-X is not a replacement for medical diagnosis or professional judgment.
            - The dataset contains only 300 patients and very few positives for rare labels.
            - Performance estimates for yellow fever and typhoid have wide uncertainty.
            - Center transfer performance indicates substantial domain shift.
            - Some features are anonymized, bilingual, or operationally ambiguous.
            - Full-feature performance is affected by target-restatement leakage.
            - Conformal coverage for rare labels is approximate under limited calibration data.
            - Prospective clinical validation, governance, consent, and monitoring are required.
            """
        ),
        md(
            """
            # 26. Conclusion and Recommendations

            **Final model recommendation:** present the pre-lab Extra Trees model as the
            primary operational model. Use the lab-aware model only after tests are
            available. Retain the full-feature model exclusively as a leakage demonstration.

            **Final system recommendation:** present VECTRA-X as a staged decision-support
            workflow combining multi-label prediction, uncertainty-aware review,
            co-infection detection, triage prioritization, and resource simulation.

            Future work should collect more rare-label cases, add prospective multi-center
            validation, monitor calibration over time, integrate real-time and
            geospatial/climate data when timestamps and locations become available, and
            co-design deployment with health workers.
            """
        ),
        md(
            """
            # 27. Appendix

            ## Configuration

            - Random state: 42
            - Multi-label stratified train/test split
            - Five-fold out-of-fold model selection
            - Project-relative paths
            - Saved model bundles under `outputs/models/`

            ## Reproducibility Notes

            Fast verified execution:

            ```powershell
            jupyter nbconvert --execute --to notebook --inplace notebooks/VECTRA_X_Final_Competition_Notebook.ipynb
            ```

            Full deterministic recomputation:

            ```powershell
            $env:VECTRA_X_RECOMPUTE="1"
            jupyter nbconvert --execute --to notebook --inplace notebooks/VECTRA_X_Final_Competition_Notebook.ipynb
            ```

            ## Generated Outputs

            Notebook-specific exports are written to `outputs/final_notebook/`.

            ## References Placeholder

            Final submission references should include WHO and CDC vector-borne disease
            guidance; multi-label classification; iterative stratification; probability
            calibration; conformal prediction; SHAP; XGBoost; LightGBM; and healthcare
            algorithm fairness literature.
            """
        ),
        code(
            """
            final_summary = {
                "project": "VECTRA-X",
                "execution_mode": "full_recomputation" if RECOMPUTE_MODELS else "artifact_backed",
                "random_state": RANDOM_STATE,
                "primary_model": summary["best_model_per_track"]["PRE_LAB"],
                "pre_lab_metrics": summary["test_metrics"]["PRE_LAB"],
                "conformal": summary["conformal"],
                "coinfection": summary["coinfection"],
            }
            (FINAL_OUTPUT / "execution_summary.json").write_text(
                json.dumps(final_summary, indent=2), encoding="utf-8"
            )
            pd.DataFrame(summary["test_metrics"]).T.to_csv(
                FINAL_OUTPUT / "held_out_track_metrics.csv"
            )
            print("Notebook execution completed.")
            print("Outputs:", sorted(path.name for path in FINAL_OUTPUT.iterdir()))
            """
        ),
    ]

    notebook = nbf.v4.new_notebook(cells=cells)
    notebook.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.language_info = {"name": "python", "version": "3.12"}
    return notebook


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
