# VECTRA-X: A Multi-label, Explainable, and Uncertainty-Aware Clinical Triage Intelligence System for Vector-Borne Disease Response

**FIT Competition 2026 — Track IV: AI-based Vector-Borne Disease Prediction**

> *Draft technical report. Figures referenced as `outputs/figures/*.png`, tables as
> `outputs/tables/*.csv`. All numbers are reproducible via `python run_pipeline.py`
> (RANDOM_STATE = 42).*

---

## Cover (placeholder)

- **Title:** VECTRA-X — A Multi-label, Explainable, and Uncertainty-Aware Clinical Triage Intelligence System for Vector-Borne Disease Response
- **Team / Institution:** _[placeholder]_
- **Track:** IV — AI-based Vector-Borne Disease Prediction
- **Date:** _[placeholder]_

## Table of Contents (placeholder)

1. Introduction
2. Literature Review
3. Methodology
4. Results and Discussion
5. Conclusion and Recommendations
6. References
7. Appendix

---

## Chapter I — Introduction

### 1.1 Background

Vector-borne diseases (malaria, dengue, yellow fever, typhoid and others) remain a
dominant cause of febrile illness in many endemic, resource-constrained settings.
Their early symptoms overlap heavily — fever, headache, myalgia, vomiting — and a
single patient frequently presents with **more than one** disease simultaneously.
Front-line health centers must triage such patients quickly, often **before**
laboratory confirmation is available, and decide who needs a confirmatory test, who
needs urgent escalation, and who can be monitored routinely.

The official dataset (`data.csv`, 300 patients × 109 variables, two health centers
in a francophone setting) captures exactly this reality: demographics, self-reported
symptoms, vital signs, laboratory/rapid-test results, and a multi-label diagnosis.

### 1.2 Problem statement

A naive classifier trained on this data faces three traps that make it look
impressive but clinically misleading:

1. **It is multi-label, not multi-class.** 158/300 patients carry more than one
   diagnosis; collapsing to a single class discards co-infection information.
2. **It contains diagnostic leakage.** Variables such as *Dengue (Dengua)*
   (single-feature AUC ≈ 0.96 with the dengue label) and the rapid tests
   *Test TDR* / *Goutte épaisse* are near-confirmatory. A model that uses them at
   "triage" time would report inflated performance it could never achieve before
   tests exist.
3. **It is severely imbalanced.** Malaria is present in 90% of patients while yellow
   fever appears in only 4%; accuracy and micro-averaged metrics hide failure on the
   rare-but-dangerous labels.

### 1.3 Objectives

- Reframe the task as **stage-aware multi-label triage**: a **pre-lab** model
  (honest, deployable) and a **lab-aware** confirmation model.
- Quantify and **audit leakage** explicitly, turning it into a methodological strength.
- Produce **calibrated probabilities**, **conformal prediction sets**, and a
  **triage priority** with transparent decision-support actions.
- Audit **fairness** across health center, gender and age, including a
  leave-one-center-out generalisation test.

### 1.4 Benefits

VECTRA-X supports faster, safer and more transparent triage: it flags which patients
need confirmatory testing or urgent review, it abstains (returns a multi-disease set)
when evidence is ambiguous, and it surfaces fairness gaps — directly serving the
competition's humanitarian / well-being theme.

---

## Chapter II — Literature Review

- **Vector-borne disease response & clinical decision support.** WHO/CDC case-
  management and dengue warning-sign guidance frame triage as a staged decision under
  uncertainty; clinical decision-support systems (CDSS) are positioned as aids to —
  not replacements for — clinicians.
- **Multi-label classification.** Binary relevance, classifier chains and label
  powerset are the canonical approaches; chains and label-graph priors exploit
  label dependency (here, co-diagnosis), which matters because >50% of patients are
  multi-label.
- **Explainable AI (XAI).** Permutation importance and SHAP provide global and local
  attributions; in a leakage-aware design, explanations must be reported **per stage**
  so diagnostic-test features cannot dominate the early-triage explanation.
- **Calibration & uncertainty.** Reliability curves, Brier score and Expected
  Calibration Error assess whether probabilities are trustworthy; predictive entropy
  and prediction-set size quantify uncertainty for safe deferral.
- **Conformal prediction.** Split-conformal methods give finite-sample coverage
  guarantees and naturally produce *prediction sets* — ideal when the safe action is
  "consider dengue or typhoid, request a confirmatory test" rather than a forced label.
- **Fairness in healthcare AI.** Subgroup recall gaps, false-negative-rate parity and
  domain-shift (here, between two facilities) are standard equity audits aligned with
  equitable access to care.

*(References to be finalised in the References section.)*

---

## Chapter III — Methodology

### 3.1 Dataset overview

300 patients × 109 columns; 0 duplicate rows; 300 unique UUIDs. Two centers
(CMA de DAFRA, CMA de DO). Semicolon-separated, decimal-comma French/English export.

### 3.2 Data description

- **Targets (multi-label):** eight `Maladies diagnostiquées/<disease>` binary columns.
  Five are **active** — malaria (270; 90.0%), other diseases (99; 33.0%),
  dengue (56; 18.7%), typhoid (29; 9.7%), yellow fever (12; 4.0%) — and three are
  **inactive** with zero positives (chikungunya, zika, option 8), excluded from
  scoring and reported as a limitation. The binary encoding matches the free-text
  diagnosis column with **100% agreement** (validated).
- **Cardinality:** 1 patient with no label, 141 single-label, 149 two-label, 9 three-label.
- **Features:** demographics, ~60 symptom yes/no items, vitals, and laboratory/rapid
  tests. Missingness is substantial for several lab/vital fields (e.g. MUAC 91.7%,
  capillary refill 69.7%, blood pressure 57.0%).

### 3.3 Preprocessing

Deterministic, leakage-safe cleaning (`src/preprocessing.py`): decimal-comma numeric
parsing; blood-pressure → systolic/diastolic + parse-failure flag; OUI/NON and
Positif/Négatif → 1/0; gender / center encoding; high-cardinality free-text → presence
flag; per-column `__missing` indicators (so *unknown* is never confused with the
negative class *NON*); constant columns dropped **with logging**. Imputation
(median / constant-0) and optional scaling are wrapped in an sklearn `ColumnTransformer`
and fit **inside CV folds only**.

### 3.4 Leakage-aware feature sets (`src/leakage_audit.py`)

Each feature is screened by **name pattern AND statistics** (mutual information +
single-feature ROC-AUC vs each active label) and routed to a stage:

| Set | n features | Contents |
|---|---|---|
| PRE_LAB_TRIAGE | 82 | demographics, symptoms, vitals — the honest early-triage set |
| LAB_AWARE_CONFIRMATION | 98 | + ordered lab/rapid tests (TDR, thick smear, haematology) |
| FULL_RESEARCH_ONLY | 99 | + *Dengue (Dengua)* target-restatement (AUC ≈ 0.96); never deployed |

### 3.5 Models / methods

Binary relevance with six base estimators (Logistic Regression, Random Forest,
Extra Trees, HistGradientBoosting, XGBoost, LightGBM) plus a supplemental
ClassifierChain; a co-infection detector; and a recall-oriented rare-label sentinel.
Calibration (Platt/isotonic), split-conformal prediction sets, permutation-importance
explainability, fairness auditing and the triage engine sit on top.

### 3.6 Evaluation protocol

Multi-label stratified split → train (223) / test (77). Model selection by **5-fold
out-of-fold (OOF) macro-PR-AUC** on train (more stable than the small test split).
Reported metrics: macro / micro / weighted / samples F1, Hamming loss, subset
accuracy, Jaccard, per-label precision/recall/F1/ROC-AUC/PR-AUC, calibration
(Brier, ECE), conformal coverage and set size, and subgroup recall gaps. Thresholds,
calibrators and conformal quantiles are fit on OOF-train and applied to the held-out
test (no leakage).

---

## Chapter IV — Results and Discussion

### 4.1 EDA insights

Malaria dominates (90%), so accuracy/micro metrics are misleading; macro-F1 and
per-label recall are primary. Co-diagnosis is central — the top combinations are
malaria-only (119), malaria+other (74), malaria+dengue (36), malaria+typhoid (24)
(`outputs/figures/coinfection_profile.png`, `label_cooccurrence_heatmap.png`).
Lab/vital missingness is heavy and disease-dependent, supporting the
missing-indicator strategy (`missingness_by_disease.png`).

### 4.2 Model results (leaderboard + pre-lab vs lab-aware vs full)

Best model per track (by OOF macro-PR-AUC): **PRE_LAB → Extra Trees**,
**LAB_AWARE → XGBoost**, **FULL → HistGradientBoosting**.

Held-out test (best model per track):

| Track | macro-F1 | micro-F1 | macro-PR-AUC | macro-recall | subset acc |
|---|---|---|---|---|---|
| PRE_LAB (Extra Trees) | 0.647 | 0.840 | 0.608 | 0.725 | 0.623 |
| LAB_AWARE (XGBoost) | 0.555 | 0.815 | 0.568 | 0.612 | 0.533 |
| FULL (HistGB) | **0.705** | **0.893** | **0.682** | 0.707 | **0.727** |

**Key finding (the leakage thesis, sharpened).** The decisive performance jump comes
almost entirely from the **FULL** set — and that jump is driven by a single
target-restatement feature, *Dengue (Dengua)*: per-label **dengue F1 rises from 0.57
(pre-lab) to 0.92 (full)**. The genuine laboratory tests (TDR, thick smear,
haematology) in LAB_AWARE add only marginal multi-label value because they mostly
confirm the already-easy malaria label. In other words, a model that naively includes
the leakage feature looks excellent yet is clinically worthless at triage time — which
is precisely the danger VECTRA-X is designed to expose. We therefore present the
**pre-lab model as the deployable system** and the full model only as a
leakage demonstration. *(See `model_leaderboard.csv`, `per_label_metrics.csv`,
`outputs/figures/model_leaderboard.png`.)*

Per-label (pre-lab, held-out test): malaria F1 0.93 (recall 1.00 — the model cannot
rule out malaria from symptoms alone, consistent with hyperendemic transmission);
other diseases F1 0.98; dengue F1 0.57; yellow fever F1 0.44 (recall 0.67 on 3 test
positives); typhoid F1 0.31. The rare labels are hard — motivating the conformal and
sentinel layers rather than overclaiming.

**Co-infection detector:** ROC-AUC 0.86, PR-AUC 0.87, recall 0.84 (Extra Trees,
cohort OOF) — co-infection is detectable from pre-lab features alone.

### 4.3 Threshold, calibration results

Per-label thresholds are tuned away from 0.5 under three policies — **performance**
(max F1), **safety** (lower thresholds for severe/rare labels to raise recall) and
**operational** (balanced, to limit confirmatory-test burden); see
`threshold_policies.csv`. Calibration: mean pre-lab Brier ≈ 0.082; reliability curves
and per-label ECE in `calibration_metrics.csv` / `calibration_curves.png`.

### 4.4 Uncertainty / conformal results

Patient uncertainty (calibrated entropy + set size): low 118, moderate 138, high 44.
Split-conformal at target 90% coverage achieves **94.8% empirical coverage** with an
average prediction-set size of **2.90** labels. Because malaria is present in 90% of
patients it is in nearly every set; ambiguous (≥2-label) sets correctly flag patients
for confirmatory testing. **Documented limitation:** for rare labels (yellow fever
~12 positives) the finite-sample quantile is capped to keep sets informative, so their
coverage is approximate. *(See `conformal_metrics.csv`, `conformal_prediction_examples.csv`.)*

### 4.5 Explainability

Global permutation importance and per-label top features
(`feature_importance_global.png`, `feature_importance_per_label.png`); local
case studies via a transparent logistic surrogate for a confident single-label case,
a high-uncertainty case, a co-infection case and a rare yellow-fever case
(`local_explanation_examples.png`); optional SHAP summary for malaria
(`shap_summary.png`). **Features are anonymised/encoded clinical signals —
explanations describe model behaviour, not medical causation.**

### 4.6 Fairness

Subgroup recall/FNR by health center, gender and age group (`fairness_metrics.csv`,
`fairness_recall_gap.png`). The **leave-one-center-out** stress test is the headline
robustness check: transferring across the two facilities yields macro-F1 ≈ 0.38 —
a substantial drop from in-distribution performance, revealing real center-specific
workflow shift. This is reported transparently as a generalisation limitation rather
than hidden.

### 4.7 Triage engine

The triage score combines risk (label-weighted calibrated probability), a severe
non-malaria signal, uncertainty and co-infection probability into four tiers with
decision-support actions. Cohort distribution: Routine Monitoring 66, Clinical Review
87, Confirmatory Test Priority 88, Urgent Response Priority 59
(`vectra_patient_level_predictions.csv`, `resource_priority_distribution.png`).
Resource simulation and threshold-policy trade-offs quantify operational burden
(`resource_simulation.csv`, `threshold_policy_resource_tradeoff.png`).

---

## Chapter V — Conclusion and Recommendations

VECTRA-X reframes a deceptively simple classification dataset into a **stage-aware,
multi-label, uncertainty-aware triage system**. Its contributions are: (1) a
dataset-aware multi-label reframing; (2) an explicit leakage audit separating pre-lab
triage from lab-aware confirmation, which demonstrates that the headline accuracy of
naive models is largely a leakage artefact; (3) calibrated probabilities and conformal
prediction sets for safe deferral; (4) per-stage explainability; (5) a fairness and
center-robustness audit; and (6) a deployable triage + resource layer with a dashboard.

**Recommendation for deployment:** present the **pre-lab Extra Trees** model as the
operational triage model, use the **lab-aware** model only once tests are ordered, and
**never** deploy the full model. Recommended next steps: collect more rare-label cases
and timestamp/location metadata (to responsibly add climate/geospatial context),
prospectively validate calibration, and pursue per-facility recalibration to close the
center-shift gap.

---

## References (placeholder)

- WHO — Guidelines for the treatment of malaria; Dengue guidelines for diagnosis,
  treatment, prevention and control.
- CDC — Dengue clinical guidance and warning signs.
- Tsoumakas & Katakis — Multi-label classification: an overview.
- Read et al. — Classifier chains for multi-label classification.
- Sechidis et al. — Stratification of multi-label data.
- Guo et al. — On calibration of modern neural networks (ECE / reliability).
- Angelopoulos & Bates — A gentle introduction to conformal prediction.
- Lundberg & Lee — SHAP: A unified approach to interpreting model predictions.
- Chen & Guestrin — XGBoost; Ke et al. — LightGBM.
- Obermeyer et al. — Dissecting racial bias in healthcare algorithms (fairness).

## Appendix (placeholder)

- A. Full feature-stage table (`outputs/tables/leakage_audit_full.csv`).
- B. Auto data dictionary (`outputs/tables/data_dictionary_auto.csv`).
- C. Full leaderboard (`outputs/tables/model_leaderboard.csv`).
- D. Per-label metrics, threshold policies, calibration, conformal, fairness tables.
- E. Reproducibility: environment (`requirements.txt`), `run_pipeline.py`, RANDOM_STATE=42.
