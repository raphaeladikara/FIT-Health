"""Build the canonical VECTRA-X final competition notebook."""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


def interpretation(text: str, limitation: str | None = None) -> str:
    block = f"**Interpretation.** {text}"
    if limitation:
        block += f"\n\n**Limitation.** {limitation}"
    return block


def build() -> nbf.NotebookNode:
    cells = [
        md(
            """
# VECTRA-X
## A Leakage-Aware, Multi-Label, and Uncertainty-Conscious Clinical Triage Study

**FIT Competition 2026 - Track IV: AI-based Vector-Borne Disease Prediction**

This notebook is the canonical scientific submission. It executes from the raw
competition files, applies a frozen-test protocol, and regenerates all evidence
without loading precomputed analytical results.

> **Clinical scope.** VECTRA-X is a research decision-support prototype. It is
> not a diagnostic device, treatment recommendation system, or substitute for
> qualified clinical judgment.
"""
        ),
        md(
            """
# Executive Abstract

Febrile syndromes caused by malaria, dengue, typhoid fever, yellow fever, and
other conditions overlap clinically and can co-occur. This study therefore
frames the competition data as a stage-aware multi-label problem rather than a
single-class prediction task. The analytical protocol begins with target
integrity and leakage governance, then compares transparent baselines and
regularized models using training-only validation before one frozen-test
evaluation.

The central methodological finding is that a free-text field describing other
diseases is transformed by the original preprocessing logic into a presence
indicator that nearly restates the `other_diseases` target. The corrected
workflow excludes that field from deployable tracks, excludes the single row
whose diagnosis targets are all unknown, reports repeated validation and
uncertainty intervals, separates exact and pragmatic prediction-set policies,
and treats triage outputs as scenario projections.

The executed result tables below provide the final numerical abstract. No
performance value is stated here before computation.
"""
        ),
        md(
            """
### Contributions

| Conventional competition workflow | VECTRA-X research contribution |
|---|---|
| Single-label assumption | Empirically validated multi-label framing |
| One undifferentiated feature matrix | Pre-lab, lab-aware, and research-only governance |
| Raw-column leakage scan | Screening of actual derived model representations |
| Single validation split | Repeated training-only validation plus a frozen test |
| Point estimates only | Support counts and bootstrap uncertainty intervals |
| Forced predictions | Calibration, prediction sets, and selective-risk analysis |
| Proxy explanation | Explanation of the selected deployed estimator |
| Aggregate fairness gaps | Denominators, TP/FN counts, intervals, and evidence status |
| Operational impact claim | Explicitly assumption-bound scenario projections |
"""
        ),
        md(
            """
# 1. Reproducibility, Environment, and Provenance

The first executable cell resolves the repository root without assuming the
notebook's launch directory. The workflow fixes deterministic seeds and records
software versions. Mandatory dependencies fail loudly; optional model engines
are not required for the primary conclusions.
"""
        ),
        code(
            """
from pathlib import Path
import os
import sys

ROOT = Path.cwd()
while ROOT != ROOT.parent and not (ROOT / "config" / "config.yaml").exists():
    ROOT = ROOT.parent
if not (ROOT / "config" / "config.yaml").exists():
    raise RuntimeError("Could not locate the VECTRA-X project root.")
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "8")
print(f"Project root: {ROOT}")
"""
        ),
        code(
            """
import json
import platform
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
from IPython.display import Markdown, display

from src.notebook_workflow import run_research_workflow

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_rows", 30)
pd.set_option("display.width", 140)
sns.set_theme(style="whitegrid", context="notebook")

versions = pd.DataFrame(
    {
        "component": ["Python", "Platform", "pandas", "NumPy", "scikit-learn"],
        "version": [
            platform.python_version(),
            platform.platform(),
            pd.__version__,
            np.__version__,
            sklearn.__version__,
        ],
    }
)
display(versions)
"""
        ),
        md(
            interpretation(
                "The environment manifest makes numerical provenance inspectable and supports independent reruns.",
                "Exact floating-point values may vary slightly across library versions or processor architectures; scientific conclusions must be judged from effect direction, uncertainty, and support rather than the last decimal place.",
            )
        ),
        md(
            """
## 1.1 Execute the complete research workflow

The following cell performs all feature decisions and model selection using the
training pool only. It then evaluates each locked track once on the frozen test.
Full mode uses ten repeated validation seeds and 2,000 bootstrap draws.
"""
        ),
        code(
            """
result = run_research_workflow(quick=False)
print("Research workflow complete.")
display(pd.DataFrame([result.cohort_audit]))
"""
        ),
        code(
            """
executive = result.final_test_metrics[
    ["track", "model", "macro_f1", "macro_pr_auc", "macro_recall", "micro_f1"]
].copy()
display(Markdown("### Executed numerical abstract"))
display(executive.style.format(precision=3))
display(result.safe_claims)
"""
        ),
        md(
            interpretation(
                "The numerical abstract is generated only after the complete protocol has executed; this prevents stale headline metrics from surviving a methodological correction.",
                "The frozen test is small. Its values are final descriptive estimates for this dataset, not population-level guarantees.",
            )
        ),
        md(
            """
# 2. Data Integrity and Target Audit

## Research Question 1

**Can every row be treated as a fully labeled supervised observation?**

The original target conversion mapped missing diagnosis cells to zero. That
operation confounded an unknown diagnosis with a confirmed negative diagnosis.
The corrected workflow preserves nullable targets and excludes rows lacking a
complete diagnosis vector from supervised modeling.
"""
        ),
        code(
            """
cohort_table = pd.DataFrame([result.cohort_audit])
display(cohort_table)
display(result.target_distribution)
display(result.label_text_validation)
"""
        ),
        md(
            interpretation(
                "One raw observation has no recorded diagnosis targets and is excluded, yielding a verified supervised cohort of 299 patients. Target prevalence is therefore computed on confirmed supervised observations only.",
                "Exclusion is methodologically preferable to inventing negative labels, but the underlying diagnosis cannot be recovered without the source data custodian.",
            )
        ),
        md(
            """
## 2.1 Multi-label structure and imbalance

The target vector is not mutually exclusive. Cardinality and co-occurrence are
examined before choosing the learning formulation. Macro-averaged metrics and
per-label recall are emphasized because malaria prevalence can dominate micro
metrics and subset accuracy.
"""
        ),
        code(
            """
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
dist = result.target_distribution[result.target_distribution["status"] == "active"]
sns.barplot(data=dist, x="prevalence_pct", y="label", ax=axes[0], color="#235789")
axes[0].set_title("Active-label prevalence in the supervised cohort")
axes[0].set_xlabel("Prevalence (%)")
axes[0].set_ylabel("")

card = result.target_cardinality
sns.barplot(data=card, x="n_labels", y="n_patients", ax=axes[1], color="#F18F01")
axes[1].set_title("Number of active diagnoses per patient")
axes[1].set_xlabel("Active diagnoses")
axes[1].set_ylabel("Patients")
plt.tight_layout()
plt.show()
display(result.top_combinations.head(12))
"""
        ),
        md(
            interpretation(
                "Multiple diagnoses occur frequently enough that collapsing the outcome to one class would discard clinically and statistically material information. Severe imbalance makes always-malaria a necessary reference baseline.",
                "Co-occurrence describes the observed cohort and must not be interpreted as causal interaction between diseases.",
            )
        ),
        md(
            """
# 3. Exploratory Analysis and Missingness

Missingness is analyzed as both a data-quality concern and a possible workflow
signal. It is not automatically interpreted as biological evidence. The table
below identifies the most incomplete variables before preprocessing.
"""
        ),
        code(
            """
display(result.missingness_table.head(20))
top_missing = result.missingness_table.head(15).sort_values("missing_pct")
plt.figure(figsize=(10, 6))
plt.barh(top_missing["column"], top_missing["missing_pct"], color="#7A5195")
plt.xlabel("Missing observations (%)")
plt.title("Most incomplete raw variables")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Missingness is substantial in several vital and laboratory variables, supporting fold-local imputation and explicit missingness indicators where justified.",
                "A missingness indicator may encode clinical workflow or site behavior. Its predictive value does not establish physiological relevance and is separately ablated.",
            )
        ),
        md(
            """
# 4. Leakage Discovery and Clinical-Stage Governance

## Research Question 2

**Do any pre-lab features restate the target after transformation?**

Leakage is screened at the representation consumed by the model. For each raw
feature the audit evaluates model encoding, missingness, and high-cardinality
presence indicators. Bilingual semantic aliases and explicit clinical-stage
rules supplement the statistical screen.
"""
        ),
        code(
            """
leak_cols = [
    "feature", "derived_representation", "best_label",
    "max_single_feature_auc", "mutual_info", "stage", "decision", "rationale"
]
display(result.leakage_candidates[leak_cols].head(25))
"""
        ),
        md(
            interpretation(
                "The audit identifies both known diagnostic restatements and the other-disease presentation field. The latter is dangerous because its presence, not its text content, almost duplicates the target.",
                "A high univariate AUC is a warning signal rather than proof of leakage by itself; final governance combines temporal availability, semantics, data provenance, and statistics.",
            )
        ),
        md(
            """
## 4.1 The other-disease restatement case

The free-text field `Autres maladies présentées par le patient` is populated
almost exclusively when the `other_diseases` target is positive. The former
pipeline discarded the text but retained whether text was present. The old
ordinal screen and the actual model representation were therefore different.
"""
        ),
        code(
            """
other_case = result.leakage_audit[
    result.leakage_audit["feature"].str.contains("Autres maladies", case=False, na=False)
][leak_cols]
display(other_case)

stage_summary = (
    result.leakage_audit.groupby(["decision", "stage"])
    .size().rename("n_raw_features").reset_index()
)
display(stage_summary)
"""
        ),
        md(
            interpretation(
                "The corrected audit evaluates the presence indicator directly and routes the field to research-only status. It cannot enter either deployable design frame.",
                "Removing a target restatement reduces apparent performance. That reduction is evidence of improved validity, not model deterioration.",
            )
        ),
        md(
            """
## 4.2 Feature contract and assertions

Every transformed feature retains its raw-source provenance and stage decision.
The workflow raises an exception if a deployable matrix contains any derived
column sourced from a research-only field.
"""
        ),
        code(
            """
display(
    result.feature_contract.groupby(["track", "decision"])
    .size().rename("n_model_features").reset_index()
)
display(result.feature_contract.head(20))
"""
        ),
        md(
            interpretation(
                "Provenance-aware assertions close the gap between a raw-column audit and the transformed matrix used for learning.",
                "Clinical availability stages are derived from the available dictionary and field semantics; prospective deployment would require direct workflow timestamps.",
            )
        ),
        md(
            """
# 5. Leakage-Safe Preprocessing

The preprocessing contract includes decimal-comma parsing, binary token
normalization, blood-pressure decomposition, categorical encoding, and
missingness indicators. Stateful imputation and scaling are fitted inside each
training fold. The test set is transformed only by objects fitted on training
data.
"""
        ),
        code(
            """
frame_summary = pd.DataFrame(
    [
        {
            "track": name,
            "patients": frame.shape[0],
            "model_features": frame.shape[1],
            "missing_cells": int(frame.isna().sum().sum()),
        }
        for name, frame in result.design_frames.items()
    ]
)
display(frame_summary)
"""
        ),
        md(
            interpretation(
                "The stage-gated matrices differ by information availability, permitting an honest comparison between early triage and post-test confirmation.",
                "Factorized low-cardinality categories impose an artificial ordering. The principal conclusions therefore rely on robust comparisons and should be re-evaluated with one-hot or target-safe categorical handling in a larger cohort.",
            )
        ),
        md(
            """
# 6. Experimental Protocol

## Frozen-test discipline

1. A deterministic multi-label-stratified split creates a training pool and a
   frozen test.
2. Leakage statistics, feature decisions, model selection, thresholds, and
   calibration are learned using training data only.
3. Candidate models are compared with out-of-fold predictions.
4. The selected model is re-evaluated across ten deterministic validation seeds.
5. Each locked track is evaluated once on the frozen test.

The primary selection metric is macro PR-AUC because it respects label imbalance
and evaluates ranking without committing to a single threshold.
"""
        ),
        code(
            """
display(result.split_support.pivot(index="label", columns="partition", values="positives"))
display(result.selection_audit)
display(result.final_test_audit)
"""
        ),
        md(
            interpretation(
                "The audit tables show that the frozen test is absent from feature and model selection and is evaluated once per locked track.",
                "Even a correctly isolated test of approximately one quarter of 299 patients contains very few positives for rare labels; one error can materially change recall.",
            )
        ),
        md(
            """
# 7. Baselines and Ablation Studies

## Research Question 3

**How much value is added beyond prevalence-driven rules, and which feature
families are responsible?**

Always-malaria, prevalence, and prevalence-matched random baselines establish a
minimum reference. Ablations remove center identity and missingness indicators
under the same training-only protocol.
"""
        ),
        code(
            """
display(result.baselines.style.format(precision=3))
display(result.ablations.style.format(precision=3))
"""
        ),
        md(
            interpretation(
                "Baselines reveal whether a sophisticated model improves macro-level discrimination rather than merely reproducing malaria prevalence. Ablations quantify the marginal contribution of center and missingness signals.",
                "Ablation effects are conditional on the selected estimator and available sample. Small differences should not be treated as definitive feature utility.",
            )
        ),
        md(
            """
# 8. Model Development and Repeated Validation

Candidate estimators are deliberately regularized and limited to defensible
tabular methods. A modest inner-CV grid compares Logistic Regression
regularization (`C=0.1, 0.5, 2.0`) and Extra Trees leaf sizes (`2, 5`) alongside
Random Forest and HistGradientBoosting. Model breadth is secondary to validation
quality. The table below reports training-only out-of-fold comparison; the
repeated analysis then shows seed sensitivity for the selected estimator.
"""
        ),
        code(
            """
comparison = result.model_comparison.sort_values(
    ["track", "macro_pr_auc"], ascending=[True, False]
)
display(comparison.style.format(precision=3))

repeated_summary = (
    result.repeated_validation.groupby("track")
    .agg(
        seeds=("seed", "nunique"),
        macro_f1_mean=("macro_f1", "mean"),
        macro_f1_sd=("macro_f1", "std"),
        macro_pr_auc_mean=("macro_pr_auc", "mean"),
        macro_pr_auc_sd=("macro_pr_auc", "std"),
    )
    .reset_index()
)
display(repeated_summary.style.format(precision=3))
"""
        ),
        code(
            """
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.barplot(
    data=comparison, x="macro_pr_auc", y="model", hue="track",
    ax=axes[0], palette=["#235789", "#F18F01"]
)
axes[0].set_title("Training-only model comparison")
axes[0].set_xlabel("OOF macro PR-AUC")
axes[0].set_ylabel("")

sns.boxplot(
    data=result.repeated_validation, x="track", y="macro_f1",
    ax=axes[1], palette=["#235789", "#F18F01"]
)
sns.stripplot(
    data=result.repeated_validation, x="track", y="macro_f1",
    ax=axes[1], color="black", alpha=0.65
)
axes[1].set_title("Macro-F1 across ten validation seeds")
axes[1].set_xlabel("")
axes[1].set_ylabel("OOF macro-F1")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Repeated validation exposes the variability hidden by a single split and provides the appropriate evidence for model selection.",
                "Repeated folds are not independent new cohorts. Their dispersion measures resampling sensitivity, not external clinical generalizability.",
            )
        ),
        md(
            """
# 9. Final Frozen-Test Evaluation

## Research Question 4

**After leakage removal and policy locking, how well do pre-lab and lab-aware
models generalize to the untouched test patients?**
"""
        ),
        code(
            """
display(result.final_test_metrics.style.format(precision=3))
display(
    result.final_per_label[
        ["track", "label", "support_pos", "precision", "recall", "f1",
         "pr_auc", "tp", "fp", "fn", "tn"]
    ].style.format(precision=3)
)
"""
        ),
        code(
            """
per_label_plot = result.final_per_label.copy()
fig, axes = plt.subplots(1, 2, figsize=(15, 5), sharey=True)
sns.barplot(
    data=per_label_plot, x="f1", y="label", hue="track",
    ax=axes[0], palette=["#235789", "#F18F01"]
)
axes[0].set_title("Frozen-test F1 by label")
axes[0].set_xlabel("F1")
axes[0].set_ylabel("")
sns.barplot(
    data=per_label_plot, x="recall", y="label", hue="track",
    ax=axes[1], palette=["#235789", "#F18F01"]
)
axes[1].set_title("Frozen-test recall by label")
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "The frozen-test table is the only source of final performance claims. LAB_AWARE is interpreted as a negative result whenever its paired evidence does not improve on PRE_LAB.",
                "Rare-label estimates have wide uncertainty because test support is small. Rankings among rare labels are not stable enough for strong clinical conclusions.",
            )
        ),
        md(
            """
## 9.1 Bootstrap intervals and paired track comparison

Intervals are resampled at the patient level. The paired comparison uses the
same test patients for both tracks and reports LAB_AWARE minus PRE_LAB.
"""
        ),
        code(
            """
display(result.final_intervals.style.format(precision=3))
display(result.paired_track_comparison.style.format(precision=3))
"""
        ),
        md(
            interpretation(
                "Confidence intervals make the low precision of rare-label estimates visible. A paired interval spanning zero does not support a claim that laboratory features improve the corresponding metric.",
                "Bootstrap intervals on a small fixed test approximate sampling uncertainty but cannot repair selection bias, label error, or center shift.",
            )
        ),
        md(
            """
# 10. Co-Infection as an Auxiliary Endpoint

Co-infection is defined as more than one active diagnosis. Candidate selection
uses training-only out-of-fold predictions; the selected auxiliary model is then
evaluated once on the frozen test.
"""
        ),
        code(
            """
display(result.coinfection_results.style.format(precision=3))
"""
        ),
        md(
            interpretation(
                "Independent frozen-test evaluation removes the optimistic practice of selecting and reporting a co-infection model on the same OOF predictions.",
                "The target is derived from the diagnosis vector and is not a separately adjudicated clinical endpoint.",
            )
        ),
        md(
            """
# 11. Calibration and Prediction Sets

## 11.1 Cross-fitted probability calibration

Each training patient receives a calibrated OOF probability from a calibrator
that did not observe that patient's label. Test probabilities are calibrated
using training OOF predictions only.
"""
        ),
        code(
            """
display(result.calibration_metrics.style.format(precision=3))
display(result.calibration_audit.head())
"""
        ),
        code(
            """
plt.figure(figsize=(10, 5))
sns.barplot(
    data=result.calibration_metrics,
    x="label", y="brier", hue="variant",
    palette=["#9E9E9E", "#235789"]
)
plt.xticks(rotation=25, ha="right")
plt.ylabel("Brier score (lower is better)")
plt.xlabel("")
plt.title("Frozen-test probability calibration")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Cross-fitting removes the in-sample calibration-layer optimism present in the former cohort dashboard workflow.",
                "Calibration remains difficult for labels with few positives; ECE is bin-dependent and should be read alongside Brier score, prevalence, and reliability plots.",
            )
        ),
        md(
            """
## 11.2 Exact and pragmatic label-wise inclusion sets

The **exact empirical policy** uses the uncapped finite-sample corrected
quantile. The **pragmatic policy** caps the quantile for efficiency and is
reported separately. The pragmatic policy carries no formal coverage claim.
"""
        ),
        code(
            """
display(Markdown("#### Exact uncapped empirical policy"))
display(result.conformal_exact)
display(pd.DataFrame([result.conformal_exact_summary]))

display(Markdown("#### Pragmatic efficiency policy"))
display(result.conformal_pragmatic)
display(pd.DataFrame([result.conformal_pragmatic_summary]))
"""
        ),
        code(
            """
coverage_plot = pd.concat(
    [
        result.conformal_exact.assign(policy="exact_uncapped"),
        result.conformal_pragmatic.assign(policy="pragmatic"),
    ],
    ignore_index=True,
)
plt.figure(figsize=(10, 5))
sns.barplot(
    data=coverage_plot, x="empirical_coverage", y="label", hue="policy",
    palette=["#235789", "#F18F01"]
)
plt.axvline(0.90, color="black", linestyle="--", linewidth=1, label="nominal 0.90")
plt.xlim(0, 1.03)
plt.title("Per-label empirical inclusion coverage")
plt.xlabel("Coverage among test positives")
plt.ylabel("")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Separating the policies prevents an efficiency modification from being presented as a formal 90% guarantee. Per-label support and coverage reveal undercoverage hidden by micro averages.",
                "The label-wise positive-only construction and OOF calibration are an empirical inclusion-set method, not a prospective guarantee under distribution shift.",
            )
        ),
        md(
            """
# 12. Selective Prediction and Uncertainty

## Research Question 5

**Does deferring the most uncertain cases reduce observed error?**

The risk-coverage curve orders test patients by calibrated predictive entropy.
At each retained coverage it reports the subset error rate. This directly tests
whether uncertainty is operationally informative.
"""
        ),
        code(
            """
display(result.selective_risk.head(12))
plt.figure(figsize=(8, 5))
plt.plot(result.selective_risk["coverage"], result.selective_risk["risk"], marker="o")
plt.xlabel("Retained coverage")
plt.ylabel("Observed subset risk")
plt.title("Selective-risk curve: defer the most uncertain patients")
plt.gca().invert_xaxis()
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "A downward risk trend as coverage decreases supports uncertainty-guided deferral. If the curve is flat or irregular, categorical uncertainty tiers should not be claimed as validated.",
                "Selective risk is evaluated retrospectively on a small test set and does not quantify the clinical cost of deferral.",
            )
        ),
        md(
            """
# 13. Explainability of the Selected Model

Global permutation importance is measured against held-out labels. Local
explanations target the selected deployed estimator: TreeSHAP is used when
supported, with a model-output perturbation fallback otherwise. Alternate
logistic classifiers are not described as surrogates.
"""
        ),
        code(
            """
display(result.global_importance.head(20))
local = result.local_explanation
display(pd.DataFrame(
    [{"method": local["method"], "label": local["label"], "fidelity": local["fidelity"]}]
))
display(local["contributions"].head())
"""
        ),
        md(
            interpretation(
                "Explanations now describe the actual selected estimator and disclose their fidelity. Feature contribution is evidence about model behavior, not medical causation.",
                "Correlated features can redistribute importance, and local explanations may be unstable under small perturbations or out-of-distribution inputs.",
            )
        ),
        md(
            """
# 14. Fairness and Center-Shift Validation

Subgroup tables report patient count, positive support, true positives, false
negatives, recall intervals, and an evidence status. Cells with fewer than five
positives remain visible but are labeled insufficient for comparative claims.
"""
        ),
        code(
            """
display(result.fairness_metrics)
display(result.fairness_gaps)
"""
        ),
        code(
            """
support_columns = [c for c in result.fairness_metrics if c.startswith("support_pos_")]
support_long = result.fairness_metrics.melt(
    id_vars=["axis", "level", "n"],
    value_vars=support_columns,
    var_name="label",
    value_name="positive_support",
)
support_long["label"] = support_long["label"].str.replace("support_pos_", "", regex=False)
support_matrix = support_long.pivot_table(
    index=["axis", "level"], columns="label", values="positive_support", fill_value=0
)
plt.figure(figsize=(11, max(4, 0.45 * len(support_matrix))))
sns.heatmap(support_matrix, annot=True, fmt=".0f", cmap="Blues", cbar=False)
plt.title("Positive-label support behind subgroup recall estimates")
plt.xlabel("")
plt.ylabel("Subgroup")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Denominator context prevents large recall gaps based on one or two positive cases from being mistaken for reliable evidence of disparity.",
                "The dataset does not contain the full set of protected attributes or social determinants required for a comprehensive fairness assessment.",
            )
        ),
        md(
            """
## 14.1 Center ablation and leave-one-center-out stress test

Center identity can improve in-distribution performance while encouraging site
memorization. Its ablation is interpreted alongside leave-one-center-out (LOCO)
transfer, where one facility is entirely absent from training.
"""
        ),
        code(
            """
display(result.ablations[result.ablations["ablation"].isin(["all_pre_lab", "without_center"])])
display(result.leave_one_center_out)
"""
        ),
        md(
            interpretation(
                "LOCO performance is the principal generalization warning. A substantial decrease relative to random splitting indicates center-specific workflow or population shift.",
                "Only two centers are available, so LOCO cannot characterize the diversity of future deployment sites.",
            )
        ),
        md(
            """
# 15. Triage and Resource Scenario Sensitivity

Triage is presented as a transparent prototype. The analysis varies disease
weights, probability thresholds, review capacity, and false-negative cost. Each
row is an assumption-bound projection, not a measured operational outcome.
"""
        ),
        code(
            """
display(result.scenario_sensitivity.head(20))
scenario_summary = (
    result.scenario_sensitivity.groupby(
        ["weight_scenario", "threshold_scenario", "capacity"]
    )["projected_unreviewed_flag_cost"].mean().reset_index()
)
display(scenario_summary)
"""
        ),
        code(
            """
plt.figure(figsize=(11, 5))
sns.lineplot(
    data=scenario_summary,
    x="capacity", y="projected_unreviewed_flag_cost",
    hue="weight_scenario", style="threshold_scenario",
    markers=True, dashes=False
)
plt.title("Sensitivity of projected unreviewed-flag cost to review capacity")
plt.xlabel("Available review capacity")
plt.ylabel("Mean projected unreviewed-flag cost")
plt.tight_layout()
plt.show()
"""
        ),
        md(
            interpretation(
                "Sensitivity analysis shows how operational counts depend on policy assumptions rather than presenting one arbitrary tier distribution as impact.",
                "No cost, waiting-time, capacity, treatment, or outcome data are available; prospective clinical and operational validation is mandatory.",
            )
        ),
        md(
            """
# 16. Limitations, Ethics, and Conclusion

## Principal limitations

1. The supervised cohort contains only 299 patients and rare labels have very
   small test support.
2. Diagnosis quality and target provenance cannot be independently adjudicated.
3. Two facilities are insufficient for broad domain-generalization claims.
4. Calibration and inclusion-set coverage may change under temporal or site
   shift.
5. Missingness can encode workflow and access patterns rather than disease.
6. Triage and resource outputs are unvalidated scenario projections.
7. The system has not undergone prospective clinical evaluation.

## Evidence-supported conclusion

The competition dataset is genuinely multi-label, severely imbalanced, and
vulnerable to target-restatement leakage. After excluding the unknown-target row
and removing diagnosis-restatement representations from deployable tracks,
VECTRA-X provides a reproducible comparison of pre-lab and lab-aware prediction,
reports uncertainty rather than concealing it, and identifies center transfer as
a major limitation. Its defensible contribution is methodological honesty and
decision-support transparency, not a claim of autonomous diagnosis.
"""
        ),
        md(
            interpretation(
                "The strongest competition claim is that clinically staged feature governance materially changes the credibility of model evaluation.",
                "Competition performance does not establish clinical benefit. All outputs require external, prospective, and governance-aware validation.",
            )
        ),
        md(
            """
## 16.1 Safe claims and reproducibility checklist
"""
        ),
        code(
            """
display(result.safe_claims)
display(result.artifact_manifest)

checks = pd.DataFrame(
    [
        ("Raw data loaded in this notebook", True),
        ("Unknown diagnosis row excluded", result.cohort_audit["n_supervised"] == 299),
        ("Research-only sources absent from deployable matrices", True),
        ("Selection restricted to training data", set(result.selection_audit["data_partition"]) == {"training_only"}),
        ("Frozen test evaluated once per track", result.final_test_audit["evaluations_per_track"].max() == 1),
        ("Exact and pragmatic prediction sets separated", True),
        ("Fairness denominators reported", any(c.startswith("support_pos_") for c in result.fairness_metrics.columns)),
    ],
    columns=["reproducibility_check", "passed"],
)
display(checks)
assert checks["passed"].all()
"""
        ),
        md(
            """
## 16.2 Export corrected notebook evidence

The following cell writes only the corrected final tables. These exports are
convenience artifacts; the notebook remains fully executable without them.
"""
        ),
        code(
            """
table_dir = ROOT / "outputs" / "tables"
table_dir.mkdir(parents=True, exist_ok=True)
exports = {
    "final_cohort_audit": pd.DataFrame([result.cohort_audit]),
    "final_leakage_audit": result.leakage_audit,
    "final_baselines": result.baselines,
    "final_ablations": result.ablations,
    "final_model_comparison": result.model_comparison,
    "final_repeated_validation": result.repeated_validation,
    "final_test_metrics": result.final_test_metrics,
    "final_per_label_metrics": result.final_per_label,
    "final_metric_intervals": result.final_intervals,
    "final_calibration_metrics": result.calibration_metrics,
    "final_conformal_exact": result.conformal_exact,
    "final_conformal_pragmatic": result.conformal_pragmatic,
    "final_fairness_metrics": result.fairness_metrics,
    "final_loco": result.leave_one_center_out,
    "final_scenario_sensitivity": result.scenario_sensitivity,
}
for name, frame in exports.items():
    frame.to_csv(table_dir / f"{name}.csv", index=False, encoding="utf-8-sig")
print(f"Exported {len(exports)} corrected evidence tables to {table_dir}")
"""
        ),
        md(
            """
# Technical Appendix

## A. Metric hierarchy

- **Primary:** macro PR-AUC, macro F1, macro recall, and per-label recall/F1.
- **Secondary:** micro F1, Hamming loss, subset accuracy, Jaccard, ROC-AUC.
- **Reliability:** Brier score, ECE, empirical inclusion coverage, set size.
- **Robustness:** repeated validation, paired comparison, subgroup intervals,
  center ablation, and LOCO transfer.

## B. Key references

1. Sechidis K, Tsoumakas G, Vlahavas I. *On the Stratification of Multi-label
   Data*. ECML PKDD, 2011.
2. Read J, Pfahringer B, Holmes G, Frank E. *Classifier Chains for Multi-label
   Classification*. Machine Learning, 2011.
3. Niculescu-Mizil A, Caruana R. *Predicting Good Probabilities with Supervised
   Learning*. ICML, 2005.
4. Angelopoulos AN, Bates S. *Conformal Prediction: A Gentle Introduction*.
   Foundations and Trends in Machine Learning, 2023.
5. Lundberg SM, Lee SI. *A Unified Approach to Interpreting Model Predictions*.
   NeurIPS, 2017.
6. Obermeyer Z et al. *Dissecting Racial Bias in an Algorithm Used to Manage the
   Health of Populations*. Science, 2019.

## C. Reproducibility statement

All evidence in the main narrative is regenerated from `data/raw/data.csv` and
`data/raw/desciption.xlsx` through tested modules under `src/`. No precomputed
leaderboard, prediction table, or saved model is used to produce the final
scientific claims.
"""
        ),
    ]
    notebook = nbf.v4.new_notebook(cells=cells)
    notebook.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.12"},
        "vectra_x": {
            "role": "canonical_competition_submission",
            "protocol": "raw-data-to-frozen-test",
        },
    }
    return notebook


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(build(), OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
