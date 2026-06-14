# Final Competition Audit Resolution Map

The canonical evidence artifact is
`notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`. The concise report is
`outputs/reports/final_technical_report_sketch.md`.

| Audit finding | Resolution | Evidence |
|---|---|---|
| Other-disease target-restatement leak | Fixed | Representation-aware screening detects the presence indicator at ROC-AUC approximately 0.975 and routes the raw source and derivatives to research-only. |
| Missing diagnosis row converted to negatives | Fixed | Nullable target parsing and supervised-cohort audit exclude one row; final n=299. |
| No unified final notebook | Fixed | One 84-cell, fully executed formal-English notebook with 52 markdown cells, 32 code cells, and 9 embedded figures. |
| Draft report and placeholders | Scoped as requested | A concise 1,369-word report sketch replaces the detailed report deliverable. |
| Single split and unstable rare-label estimates | Fixed in notebook | Ten repeated validation seeds and 2,000-draw patient bootstrap intervals are reported. |
| Missing baselines and ablations | Fixed | Always-malaria, prevalence, random-prevalence, center, and missing-indicator analyses are included. |
| Optimistic co-infection selection | Fixed in notebook | Selection is training-only; the selected auxiliary model is evaluated once on the frozen test. |
| LAB_AWARE claim contradicted results | Fixed | LAB_AWARE underperformance is retained as a negative result in notebook, report sketch, README, and generated summary logic. |
| Shallow hyperparameter selection | Improved | Training-only grid covers Logistic Regression C and Extra Trees leaf size alongside regularized tabular models. |
| In-sample calibration layer | Fixed in notebook | Training probabilities use cross-fitted calibrators with row-level index audit. |
| Capped conformal quantile described as guaranteed | Fixed | Exact uncapped and pragmatic capped policies are separated; pragmatic output carries no formal guarantee. |
| Heuristic uncertainty categories | Fixed in notebook | Risk-coverage analysis tests whether deferral reduces observed error. |
| Proxy local explanations mislabeled as surrogate | Fixed in notebook | Local explanations target the selected deployed estimator and disclose method/fidelity. |
| Fairness lacked denominators and intervals | Fixed | Subgroup n, positive support, TP, FN, Wilson intervals, and insufficient-evidence status are reported. |
| Center memorization concern | Fixed | Center ablation and bidirectional leave-one-center-out validation are included. |
| Triage/resource outputs overstated impact | Fixed | Outputs are explicitly labeled scenario projections with sensitivity over weights, thresholds, capacity, and false-negative cost. |
| Legacy pipeline cohort misalignment | Fixed | `run_pipeline.py --quick` completes successfully on the verified n=299 cohort. |

## Remaining Scientific Limitations

- Yellow fever has only three frozen-test positives and zero recall in both tracks.
- Typhoid and dengue intervals remain wide.
- Leave-one-center-out macro-F1 is approximately 0.265-0.302.
- No prospective clinical, safety, usability, or operational validation exists.
- Competition ranking cannot be guaranteed; the submission is optimized for
  scientific credibility and defensibility.
