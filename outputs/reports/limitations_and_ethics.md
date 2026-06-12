# VECTRA-X — Limitations and Ethics

## 1. Intended use

VECTRA-X is a **clinical decision-support and triage-prioritisation** tool. It is
**not** an autonomous diagnostic system and must not replace clinical judgement. All
outputs are framed as decision-support actions (e.g. "prioritise confirmatory testing",
"manual clinical review", "flag for urgent evaluation"), never treatments or definitive
diagnoses.

## 2. Data limitations

- **Small sample (n = 300).** High variance; metrics — especially for rare labels —
  are estimates. We report per-label support and avoid overclaiming.
- **Severe class imbalance.** Malaria 90%, yellow fever 4%. Accuracy is misleading;
  we use macro-F1, per-label recall and PR-AUC.
- **Inactive labels.** Chikungunya, zika and option 8 have **zero positives** in this
  file and are excluded from primary scoring — a data limitation, not a modelling
  choice.
- **High, structured missingness.** Several lab/vital fields are >50% missing. We keep
  them with `__missing` indicators (a workflow-availability signal) and never convert
  missing to the negative class.
- **No timestamp or location.** Only health-center names exist. External climate /
  population / facility data therefore **cannot** be responsibly merged into
  patient-level training; it is used only for literature, context and the dashboard.
- **Two facilities only.** Leave-one-center-out macro-F1 ≈ 0.38 reveals real
  center-specific workflow shift; the model may not transfer to unseen facilities
  without recalibration.

## 3. Modelling limitations

- **Leakage realism.** The pre-lab model is intentionally weaker than the leakage-laden
  full model; this is by design. Reported pre-lab performance is the realistic
  deployable expectation.
- **Conformal coverage for rare labels is approximate.** With ~12 yellow-fever
  positives the finite-sample quantile is capped to keep prediction sets informative;
  the rigorous coverage figure applies to well-populated labels.
- **Calibration is in-sample for the cohort dashboard.** The rigorous calibration /
  conformal numbers come from the held-out test split; the 300-patient dashboard uses
  out-of-fold probabilities with in-sample conformal thresholds for display.

## 4. Ethical considerations

- **No medical causation claims.** Features are anonymised/encoded clinical signals;
  explanations describe model behaviour only.
- **Fairness.** We audit recall and false-negative gaps across gender, age group and
  health center. Any gap is a flag for human oversight, not an acceptable trade-off.
  False negatives on severe diseases are treated as the most harmful error and inform
  the recall-oriented "safety" threshold policy.
- **Transparency.** The full pipeline is reproducible (RANDOM_STATE = 42), every
  feature's stage/leakage decision is logged, and dropped columns are recorded with
  reasons.
- **Human-in-the-loop.** The triage tier and conformal set are designed to *defer* to
  clinicians under uncertainty (abstention / multi-label sets), not to automate care.
- **Privacy.** Only the provided anonymised data is used; UUIDs are retained for row
  tracking only and are not features.

## 5. Responsible-deployment recommendations

1. Deploy the **pre-lab** model for early triage; use **lab-aware** only after tests
   are ordered; **never** deploy the full (leakage) model.
2. Recalibrate per facility before any new-site rollout; monitor center-shift.
3. Keep a clinician in the loop for all Orange/Red tiers and all abstentions.
4. Collect more rare-label cases and (with consent/governance) timestamp/location
   metadata before adding any environmental enrichment.
5. Re-validate calibration and fairness prospectively on incoming data.
