# VECTRA-X: Leakage-Aware Multi-Label Clinical Triage for Vector-Borne Disease Response

**FIT Competition 2026 - Track IV: AI-based Vector-Borne Disease Prediction**

## Structured Abstract

**Background.** Vector-borne and febrile diseases frequently share early clinical
signs, and more than one diagnosis may be recorded for the same patient. Models
developed without respecting this structure can produce attractive but misleading
results, particularly when post-diagnosis variables or target restatements are
included among predictors.

**Objective.** VECTRA-X investigates whether clinically staged, multi-label models
can support early triage while remaining explicit about leakage, rare-label
uncertainty, center shift, and the limits of operational interpretation.

**Methods.** The analysis is fully reproduced in
`notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`. Raw diagnosis values are
parsed as nullable binary targets. One observation whose complete diagnosis vector
is missing is excluded rather than treated as an all-negative patient, producing a
verified supervised cohort of **299** patients. Features are separated into
pre-laboratory triage, laboratory-aware confirmation, and research-only groups.
Leakage screening evaluates the representations consumed by the model, including
presence and missingness indicators. A deterministic multi-label-stratified test set
is frozen before statistical feature decisions and model selection. Candidate
estimators and a modest hyperparameter grid are compared using training-only
out-of-fold predictions. The selected model is evaluated across ten validation seeds
and then once on the frozen test. Baselines, center and missing-indicator ablations,
patient-level bootstrap intervals, cross-fitted calibration, exact and pragmatic
prediction-set policies, selective-risk analysis, deployed-model explanations,
support-aware fairness metrics, leave-one-center-out testing, and scenario
sensitivity are reported.

**Results.** The representation-aware audit identifies `Autres maladies présentées
par le patient` as a target-restatement field: its derived presence indicator has a
single-feature ROC-AUC of approximately 0.975 for `other_diseases`. It is therefore
excluded from deployable tracks. After this correction, the selected pre-laboratory
Extra Trees model obtains frozen-test macro-F1 **0.482**, macro PR-AUC **0.525**, and
macro recall **0.501**. The laboratory-aware HistGradientBoosting model obtains
macro-F1 **0.444**, macro PR-AUC **0.502**, and macro recall **0.522**. Laboratory
information therefore does not improve aggregate F1 or PR-AUC in this experiment,
although dengue recall increases from 0.357 to 0.786 at the cost of substantially
more false positives and weaker typhoid performance. Yellow fever has only three
positive test observations and zero recall in both tracks. Leave-one-center-out
macro-F1 ranges from approximately 0.265 to 0.302, demonstrating severe center
transfer limitations.

**Conclusion.** The principal contribution of VECTRA-X is not an inflated diagnostic
score. It is an auditable workflow showing that multi-label framing, representation-
aware leakage control, frozen-test discipline, and uncertainty reporting materially
change the credibility of competition results. The current evidence supports a
research decision-support prototype, not autonomous diagnosis or deployment.

## 1. Problem and Contribution

The official dataset contains demographics, symptoms, vital signs, laboratory and
rapid-test variables, and several diagnosis columns. Five diagnosis labels have
positive observations: malaria, other diseases, dengue, typhoid fever, and yellow
fever. The outcome is multi-label because patients can carry multiple active
diagnoses. Malaria dominates the cohort, while yellow fever and typhoid are rare.
Consequently, accuracy and micro-averaged metrics can hide failure on clinically
important minority labels.

VECTRA-X contributes five elements. First, it validates the target structure and
preserves unknown diagnosis values rather than silently converting them to
negatives. Second, it governs predictors by clinical availability stage. Third, it
screens the actual transformed model inputs for leakage. Fourth, it separates
training-only selection from a frozen final test and reports uncertainty intervals.
Fifth, it evaluates calibration, selective prediction, subgroup evidence, center
shift, and operational scenarios without presenting them as validated clinical
impact.

## 2. Methodology Overview

The pre-laboratory track contains demographics, history, symptoms, and available
vital signs. The laboratory-aware track adds ordered tests and laboratory
measurements. Diagnosis restatements and post-diagnosis fields are retained only for
audit demonstrations. Deterministic preprocessing parses decimal-comma measurements,
normalizes binary tokens, separates systolic and diastolic blood pressure, encodes
low-cardinality categories, and records missingness indicators. Imputation and
scaling are fitted within training folds.

Transparent baselines include an always-malaria rule, a prevalence threshold rule,
and prevalence-matched random predictions. Candidate models include regularized
Logistic Regression, Random Forest, Extra Trees, and HistGradientBoosting. Logistic
regularization and Extra Trees leaf size are selected from a modest grid using
training out-of-fold macro PR-AUC. The selected estimator is then evaluated over ten
multi-label-stratified validation seeds. Per-label thresholds are learned from
training OOF predictions only.

Calibration uses cross-fitting so a training patient's calibrated probability is
produced by a calibrator that did not observe that patient. The exact prediction-set
policy uses an uncapped finite-sample quantile; a separate pragmatic policy applies
an efficiency cap and is not described as having formal coverage. Fairness tables
show subgroup size, positive support, true positives, false negatives, recall
intervals, and an insufficient-evidence state. Explanations target the deployed
estimator using TreeSHAP when supported, with a disclosed perturbation fallback.

## 3. Corrected Results and Discussion

The original PRE_LAB result was inflated primarily by the other-disease free-text
presence signal. After its removal, `other_diseases` frozen-test F1 is 0.667 rather
than the previously reported near-perfect value. This performance reduction is a
validity correction: a model should not receive credit for predicting a diagnosis
from a field that almost states whether that diagnosis is present.

For PRE_LAB, malaria F1 is 0.932 with recall 1.000, other-disease F1 is 0.667,
dengue F1 is 0.385, typhoid F1 is 0.429, and yellow-fever F1 is 0.000. Bootstrap
intervals are wide for dengue and typhoid and degenerate at zero for yellow-fever
F1. These results prevent a defensible claim that rare diseases are reliably
detected.

LAB_AWARE increases malaria ranking quality and dengue recall, but frozen-test
macro-F1 and macro PR-AUC are lower than PRE_LAB. This is reported as a negative
result. Additional information does not necessarily improve a small-data model:
laboratory variables can be sparse, workflow-dependent, redundant, or associated
with overfitting. Paired per-label comparisons and intervals are retained in the
notebook rather than reducing the comparison to one headline number.

Calibration improves some labels but worsens others. For example, calibrated Brier
scores improve for typhoid and yellow fever but worsen for other diseases. The exact
inclusion-set policy achieves high empirical positive coverage by producing large,
inefficient sets for rare labels. The pragmatic policy improves efficiency but is
reported without a formal guarantee. Selective-risk analysis directly examines
whether deferring high-entropy patients reduces observed error.

Center transfer is the strongest robustness warning. LOCO macro-F1 below 0.31 is
substantially weaker than random in-distribution testing. Center identity itself
contributes little incremental OOF performance, suggesting that the shift involves
broader differences in population, measurement, workflow, or missingness. New-center
deployment would require external validation and likely local recalibration.

## 4. Operational Interpretation

The triage and resource layer is a scenario-analysis prototype. Disease weights,
thresholds, review capacity, and false-negative costs are varied explicitly. Output
counts describe what the policy would flag under each assumption; they do not measure
waiting time, clinical outcomes, treatment benefit, resource savings, or cost
effectiveness. No patient-level operational recommendation should be used outside a
properly governed prospective study.

## 5. Limitations

The cohort is small, diagnoses cannot be independently adjudicated, and rare-label
test support is extremely limited. Only two centers are represented. Resampling
intervals quantify instability within this dataset but do not establish transport to
new populations. Missingness may encode care pathways and access differences.
Calibration and empirical prediction-set coverage can fail under distribution shift.
The system has not undergone prospective clinical, safety, usability, or operational
validation.

## 6. Conclusion

VECTRA-X demonstrates that scientific credibility in clinical machine learning
depends on what information was available, how targets were encoded, and whether the
evaluation protocol could influence feature and model decisions. The final notebook
provides the complete evidence trail and should be treated as the primary submission
artifact. Safe claims are limited to the multi-label structure, the necessity of
stage-aware leakage governance, the observed leakage-free frozen-test results, the
failure to establish reliable rare-label performance, and the substantial
center-shift risk.

## References

1. Sechidis K, Tsoumakas G, Vlahavas I. On the Stratification of Multi-label
   Data. ECML PKDD; 2011.
2. Read J, Pfahringer B, Holmes G, Frank E. Classifier Chains for Multi-label
   Classification. *Machine Learning*. 2011.
3. Niculescu-Mizil A, Caruana R. Predicting Good Probabilities with Supervised
   Learning. ICML; 2005.
4. Angelopoulos AN, Bates S. Conformal Prediction: A Gentle Introduction.
   *Foundations and Trends in Machine Learning*. 2023.
5. Lundberg SM, Lee SI. A Unified Approach to Interpreting Model Predictions.
   NeurIPS; 2017.
6. Obermeyer Z, Powers B, Vogeli C, Mullainathan S. Dissecting Racial Bias in an
   Algorithm Used to Manage the Health of Populations. *Science*. 2019.
