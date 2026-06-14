# VECTRA-X Final Competition Notebook Design

**Date:** 14 June 2026  
**Primary deliverable:** `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`  
**Language:** Formal academic English  
**Execution contract:** Fully executable from the raw competition files without relying on precomputed analytical results  
**Priority:** Scientific rigor, reproducibility, clarity, and defensibility before headline performance

## 1. Purpose

The final notebook will be the canonical competition submission and the primary
scientific record for VECTRA-X. It will replace the fragmented three-notebook
submission path with one coherent, top-to-bottom research narrative that:

1. establishes the clinical and competition problem;
2. validates the raw dataset and target construction;
3. discovers and removes target-restatement leakage;
4. evaluates models under leakage-free, stage-aware protocols;
5. quantifies uncertainty in small and imbalanced samples;
6. explains the selected model rather than a separate proxy classifier;
7. documents fairness, center shift, and operational limitations;
8. ends with restrained, evidence-supported competition claims.

The notebook is designed as a research monograph rather than a collection of
independent experiments. Each major result will be presented using the sequence:
research question, hypothesis, method, evidence, interpretation, and limitation.

## 2. Scientific Principles

### 2.1 Data integrity before modeling

Rows with unknown diagnosis targets must not be silently converted into confirmed
all-negative observations. The notebook will identify incomplete target rows,
explain the exclusion rule, preserve an audit trail, and use the verified supervised
cohort for all training and evaluation.

### 2.2 Stage-aware feature governance

Features will be divided into:

- `PRE_LAB_TRIAGE`: information available before laboratory confirmation;
- `LAB_AWARE_CONFIRMATION`: pre-lab information plus ordered tests and laboratory
  measurements;
- `RESEARCH_ONLY`: diagnosis restatements, post-diagnosis fields, and suspicious
  features retained only for leakage demonstrations.

`Autres maladies presentees par le patient` must be routed to `RESEARCH_ONLY`.
Leakage screening must evaluate the actual representations consumed by models,
including missingness and presence indicators, rather than only raw ordinal codes.
Semantic screening must include bilingual aliases such as `other` and `autres`.

### 2.3 Frozen-test discipline

A deterministic multi-label-stratified test set will be created once and frozen.
All feature decisions, estimator selection, hyperparameter selection, threshold
selection, calibration choices, and ablation conclusions will use training data
only. The final test set will be evaluated after the analytical policy is locked.

### 2.4 Honest uncertainty

Point estimates will not be presented without support information. Repeated
multi-label validation and bootstrap or repeated-validation confidence intervals
will be used for primary metrics. Rare-label results will always show positive
support and will explicitly state when estimates are unstable.

### 2.5 Negative results remain visible

If the lab-aware track does not outperform the pre-lab track, the notebook will
present this as a meaningful negative result. No claim of laboratory improvement
will be made unless paired leakage-free evidence supports it.

## 3. Notebook Narrative

### Part I: Executive orientation

1. Title, team metadata, competition track, and reproducibility statement.
2. Executive abstract summarizing the problem, method, principal findings, and
   limitations after execution.
3. Contribution table contrasting VECTRA-X with a conventional single-model
   competition workflow.
4. A compact roadmap explaining the notebook's analytical sequence.

### Part II: Reproducibility and data provenance

5. Imports, deterministic random seeds, path resolution, version manifest, and
   warning policy.
6. Dependency availability checks with clear failures for mandatory packages and
   transparent fallback notes for optional engines.
7. Raw-file identity, dimensions, encoding, delimiter, data-dictionary source, and
   non-destructive loading.

### Part III: Dataset and target audit

8. Schema roles, duplicate checks, UUID integrity, constant columns, and missingness.
9. Diagnosis-column detection and bilingual alias mapping.
10. Explicit visualization of incomplete target rows and the supervised-cohort
    exclusion decision.
11. Validation of binary diagnosis columns against the free-text diagnosis field.
12. Label prevalence, cardinality, co-occurrence, and top label combinations.
13. Formal justification for multi-label rather than multi-class modeling.
14. Discussion of imbalance and why accuracy is not a primary metric.

### Part IV: Exploratory data analysis

15. Demographics and center composition.
16. Symptom, vital-sign, laboratory, and missingness structure.
17. Missingness by diagnosis and center.
18. Feature association and low-dimensional projection, interpreted cautiously.
19. A written interpretation block after every table and figure, including what the
    result does not establish.

### Part V: Leakage discovery and feature governance

20. Definition and taxonomy of target, temporal, semantic, and workflow leakage.
21. Demonstration of the known dengue restatement.
22. Dedicated case study of `Autres maladies presentees par le patient`, including
    the raw-value relationship, derived presence indicator, confusion counts,
    single-feature ROC-AUC, and model importance.
23. Comparison between raw ordinal screening and model-representation screening.
24. Bilingual semantic alias checks for all active targets.
25. Final stage-gated feature table with rationale for every suspicious feature.
26. Suspicious-feature ablation showing the change produced by each removed or
    stage-gated field.

### Part VI: Leakage-safe preprocessing

27. Decimal-comma parsing, binary encoding, blood-pressure parsing, categorical
    encoding, missing indicators, and constant-column handling.
28. Fold-local imputation and scaling.
29. A preprocessing contract table showing raw input, transformed representation,
    availability stage, and leakage status.
30. Assertions proving that research-only fields and their derived columns cannot
    enter deployable tracks.

### Part VII: Experimental protocol

31. Frozen train/test split and support table.
32. Repeated multi-label-stratified validation on the training pool using at least
    ten deterministic seeds.
33. Primary metrics: macro-F1, macro-PR-AUC, macro-recall, per-label F1 and recall.
34. Secondary metrics: micro-F1, Hamming loss, subset accuracy, Jaccard, ROC-AUC,
    calibration, and error counts.
35. Confidence-interval method and limitations under small positive support.
36. Threshold tuning performed only within training predictions.

### Part VIII: Baselines and ablations

37. Always-malaria baseline.
38. Per-label prevalence baseline.
39. Logistic-regression reference baseline.
40. Incremental feature-family ablations: demographics, symptoms, vitals, and labs.
41. Center-feature ablation.
42. Missing-indicator ablation.
43. Suspicious-feature ablation.
44. Interpretation focused on marginal value rather than raw metric ranking alone.

### Part IX: Model development

45. Binary-relevance models with regularized Logistic Regression, Random Forest,
    Extra Trees, HistGradientBoosting, and available optional boosting engines.
46. Modest nested or inner-CV hyperparameter search over clinically and statistically
    defensible ranges.
47. Label-specific performance reporting, especially for rare labels.
48. Supplemental classifier-chain analysis clearly separated from the primary model.
49. Selection by repeated training-only evidence, not by final-test performance.

### Part X: Final performance and error analysis

50. Locked selected models and thresholds.
51. One final frozen-test evaluation for pre-lab and lab-aware tracks.
52. Confidence intervals, test support, and confusion counts beside every headline
    per-label metric.
53. Paired pre-lab versus lab-aware comparison.
54. Error taxonomy and representative false-negative or false-positive cases without
    exposing patient identifiers.
55. Explicit reassessment of all prior headline claims after leakage removal.

### Part XI: Co-infection

56. Co-infection target definition and prevalence.
57. Model selection confined to training data.
58. Independent frozen-test evaluation with ROC-AUC, PR-AUC, sensitivity,
    specificity, F1, and uncertainty intervals.
59. Interpretation as an auxiliary risk signal, not an independently validated
    diagnostic endpoint.

### Part XII: Calibration and prediction sets

60. Cross-fitted calibration so each reported calibrated training probability comes
    from a calibrator that did not observe that patient.
61. Reliability curves, Brier score, and ECE with support context.
62. Exact uncapped label-wise conformal procedure with accurate naming.
63. A separately labeled pragmatic prediction-set policy if an efficiency cap is
    retained.
64. Per-label coverage, macro and micro coverage, set size, singleton rate,
    ambiguity, and false-negative risk.
65. Coverage-efficiency curves and an explicit statement that tiny rare-label
    support prevents strong empirical assurance.

### Part XIII: Selective prediction and uncertainty

66. Risk-coverage and abstention curves.
67. Validation that proposed uncertainty categories correspond to observed error or
    false-negative risk.
68. If categories are not validated, replace categorical claims with continuous
    uncertainty scores and transparent quantile bands.

### Part XIV: Explainability

69. Global permutation importance on held-out data where feasible.
70. TreeSHAP or model-native explanations for the actual deployed tree estimator.
71. Local explanations for selected cases with a fidelity statement.
72. Clear separation between association, model contribution, and medical causation.

### Part XV: Fairness and domain shift

73. Subgroup size, positive support, TP, FN, recall, and confidence intervals for
    center, gender, and age groups.
74. An `insufficient evidence` state for subgroup-label cells with inadequate support.
75. Recall gaps interpreted only when denominator context permits.
76. Center-feature ablation and leave-one-center-out validation as the headline
    generalization warning.

### Part XVI: Triage and resource scenario analysis

77. Triage score and tier logic presented as a transparent research prototype.
78. Sensitivity analysis over label weights, thresholds, capacity, and
    false-negative cost.
79. Scenario projections reported as counts under assumptions, not measured clinical
    impact.
80. Clear statement that prospective clinical validation is required.

### Part XVII: Conclusions

81. Evidence-supported contributions.
82. Safe competition claims after the leakage-free rerun.
83. Limitations covering sample size, rare labels, center shift, calibration,
    uncertainty, and absence of prospective validation.
84. Reproducibility checklist and generated-artifact manifest.
85. Compact technical appendix containing expanded grids, diagnostics, and
    implementation details that would interrupt the main narrative.

## 4. Visual and Editorial System

The notebook will use a restrained research-report style:

- consistent typography and figure sizing;
- one color system with accessible contrast and stable label colors;
- numbered research questions and findings;
- compact callouts for `Finding`, `Interpretation`, `Limitation`, and
  `Reproducibility Check`;
- tables sorted by analytical importance rather than arbitrary column order;
- captions that state the data partition and evaluation protocol;
- no decorative visuals that do not contribute evidence;
- no unexplained output dumps or long raw DataFrame displays.

All charts must be generated in the notebook or through imported project functions
called by the notebook. Every chart will be followed by a formal interpretation.

## 5. Code Architecture

The notebook will remain readable by delegating reusable computations to tested
modules under `src/`. The notebook will orchestrate and explain the work, while the
modules will provide:

- supervised-cohort validation;
- representation-aware leakage screening;
- stage-aware feature construction;
- baseline and ablation evaluation;
- repeated validation and confidence intervals;
- cross-fitted calibration;
- exact and pragmatic prediction-set evaluation;
- selective-risk analysis;
- fairness interval reporting;
- scenario sensitivity analysis.

Notebook cells will be intentionally sized and independently understandable. Long
algorithm implementations will not be embedded when a focused tested module is more
appropriate.

## 6. Testing and Verification

Before notebook generation, regression tests will prove:

1. missing target rows are excluded from supervised modeling;
2. the other-disease presentation field is research-only;
3. leakage screening detects derived presence and missing indicators;
4. deployable feature matrices contain no research-only derived feature;
5. calibration predictions are cross-fitted;
6. conformal exact mode has no quantile cap;
7. fairness tables contain support and error counts;
8. center ablation removes all center-derived columns.

The completed notebook must then:

- execute from the first cell to the last without manual intervention;
- contain no error outputs or stale execution order;
- regenerate its analytical tables and figures from raw data;
- contain no unsupported headline claim;
- keep the final test isolated from model and policy selection;
- pass notebook structural checks for required sections and interpretation blocks.

## 7. Report Scope

The technical report will be reduced to a concise sketch aligned with the notebook:

1. title and abstract;
2. problem and contribution summary;
3. methodology overview;
4. principal leakage-free results;
5. limitations and conclusion;
6. short reference list.

The report will not duplicate the notebook's full experimental detail. Its purpose is
to satisfy the submission structure and direct judges to the notebook as the primary
scientific artifact.

## 8. Acceptance Criteria

The work is complete when:

- `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb` exists and runs end to end;
- it uses the verified supervised cohort and leakage-free pre-lab track;
- all major audit findings are either corrected or explicitly resolved through
  evidence and accurate naming;
- baselines, ablations, repeated validation, intervals, frozen-test results,
  cross-fitted calibration, uncertainty analysis, deployed-model explainability,
  fairness support, center shift, and scenario sensitivity are present;
- the notebook is written entirely in polished formal academic English;
- the concise report sketch is regenerated from the corrected results;
- automated tests and a clean notebook execution provide fresh completion evidence.

