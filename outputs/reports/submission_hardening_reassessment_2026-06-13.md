# VECTRA-X Submission Hardening Reassessment

Date: 13 June 2026

## Defensible Score

The hardened submission supports a conservative **89.5/100** estimate. This is
lower than the earlier 93/100 internal estimate because the final score now uses
only evidence reproduced by the clean-room notebook run and the seven-page
Technical Report.

| Rubric component | Weight | Score | Fresh evidence |
|---|---:|---:|---|
| Visualization and data understanding | 20 | 18.5 | Prevalence, support, missingness, model comparison, calibration, uncertainty, fairness, center transfer, decision curves, and resource trade-offs are regenerated in the notebook. |
| Preprocessing appropriateness | 20 | 19.0 | Holdout creation precedes learned preprocessing; schema, imputation, encoding, feature selection, thresholds, and models are training-fitted. PRE_LAB is separated from LAB_AWARE and leakage-demonstration FULL tracks. |
| Model performance and evaluation | 20 | 17.5 | Eight model families, OOF macro PR-AUC selection, held-out per-label results, calibration, bootstrap intervals, repeated validation, center transfer, decision curves, and resource burden are reported. Rare-label failure prevents a higher score. |
| Introduction and contribution | 10 | 9.5 | The humanitarian triage need, uncertainty gate, resource allocation workflow, and decision-support boundary are explicit. |
| Literature and research gap | 10 | 8.0 | The report positions the work against disease prediction, calibration, conformal prediction, explainability, and fairness, but the review remains concise rather than systematic. |
| Methodology | 10 | 9.0 | Data resolution, leakage control, evaluation logic, uncertainty, triage, and resource simulation are reproducible from the notebook. |
| Results and discussion | 10 | 8.0 | Results are candid and operationally interpreted, but external validity and rare-label conclusions remain weak. |
| **Total** | **100** | **89.5** | |

The clean-room run selected **Extra Trees** using training-only OOF macro
PR-AUC (**0.566**). On the untouched PRE_LAB holdout, calibrated macro PR-AUC
was **0.582**, macro F1 **0.535**, micro F1 **0.851**, and macro recall
**0.535**. The bootstrap 95% interval for macro F1 was **0.446-0.626**.

The result is operationally useful but not uniformly safe. Malaria recall was
**1.000** and dengue recall **0.571**, while typhoid recall was **0.143** and
yellow-fever recall **0.000** with only three positive holdout cases. These
failures are displayed rather than hidden behind aggregate metrics.

## Remaining Deductions

- No prospective, temporal, or genuinely external validation dataset exists.
- Yellow fever and typhoid support is too small for stable safety, fairness, or
  conformal claims.
- Center-transfer results demonstrate distribution shift but cannot establish
  generalization beyond the two represented centers.
- The caution-set implementation is an empirical uncertainty aid, not a
  clinical coverage guarantee under arbitrary deployment shift.
- Resource weights and triage thresholds are scenario assumptions rather than
  clinician-validated utilities or observed patient-outcome optimization.
- The literature review is credible but not a formal systematic review.
- The prototype has not undergone clinician usability, workflow, or prospective
  harm testing.

## P0 Before Submission

1. Submit the executed notebook, the exact CSV used for execution, and the
   generated Technical Report PDF together; do not include stale model or result
   artifacts as required inputs.
2. Run the notebook once in the final submission folder and confirm the
   execution manifest contains the expected CSV hash and selected model.
3. Preserve the wording “decision-support,” “triage prioritization,”
   “competition prototype,” and “requires prospective validation” in every
   public artifact.
4. Keep typhoid, yellow-fever, center-shift, and conformal limitations visible
   in the notebook conclusion, report, pitch, and dashboard.
5. Check the final PDF and notebook after upload to ensure outputs, figures,
   captions, and references were not stripped by the submission portal.

## P1 Highest-Value Improvements

- Add a compact preprocessing/component ablation table with uncertainty
  intervals, especially center features, missingness indicators, calibration,
  and threshold policy.
- Add a second seed or nested repeated validation summary for the top model
  families to quantify model-selection instability.
- Expand the related-work matrix with explicit dataset, task, validation
  setting, uncertainty method, and gap columns.
- Add a privacy-safe synthetic-case walkthrough showing why two patients with
  similar probabilities can receive different actions because of uncertainty
  and resource constraints.
- Obtain expert review of triage weights, confirmatory-test priority rules, and
  the number-needed-to-review interpretation.

## Longer-Term Research

- External and temporal validation across additional facilities and outbreak
  periods.
- Facility-specific recalibration and drift monitoring with explicit update
  triggers.
- Purposeful collection of typhoid and yellow-fever positives to reduce
  rare-label uncertainty.
- Clinician usability studies measuring comprehension, override behavior,
  workload, and unsafe automation bias.
- Outcome-based resource optimization using waiting time, test yield, severe
  deterioration, bed occupancy, and equity constraints.
- Prospective comparison of uncertainty gates, selective prediction, and
  conformal variants under center and prevalence shift.

## Final Positioning

VECTRA-X is strongest as an **uncertainty-aware humanitarian triage workflow**,
not as a replacement for clinician assessment. Its competition advantage is the integration
of honest pre-lab prediction, uncertainty communication, explainability,
resource allocation, and explicit failure reporting in one reproducible
submission package.
