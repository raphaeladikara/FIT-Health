# VECTRA-X Final Rubric Reassessment

Date: 13 June 2026

## Verdict

The requested rubric improvements have been implemented and verified. The
notebook now covers every actionable item that can be solved with the available
dataset and repository. A strict scientific score of **93.0/100** is defensible.

An honest 100/100 cannot be guaranteed from code changes alone. The remaining
points require new external/prospective data, more rare-label positives, and
clinical validation. Claiming 100 despite those limits would contradict the
responsible framing now used throughout the notebook.

| Rubric component | Weight | Previous | New score |
|---|---:|---:|---:|
| Visualization and understanding of data | 20 | 16.5 | 19.0 |
| Preprocessing appropriateness | 20 | 14.0 | 19.0 |
| Model performance and evaluation | 20 | 15.0 | 17.5 |
| Introduction, problem, solution, contribution | 10 | 9.0 | 9.5 |
| Literature review | 10 | 4.5 | 9.0 |
| Methodology | 10 | 7.0 | 9.5 |
| Results and discussion | 10 | 7.0 | 9.5 |
| **Estimated total** | **100** | **73.0** | **93.0** |

## Evidence Added

- Outer holdout split now occurs before target-aware leakage screening and
  feature-schema fitting.
- Categories, constants, missing indicators, and feature types are learned from
  train only. Unknown categories have an explicit all-zero policy.
- Nominal categories use fitted one-hot encoding rather than arbitrary integer
  factorization.
- Patient-level bootstrap 95% intervals are reported for headline metrics.
- Three repeated multi-label CV runs expose model-selection variance.
- A prevalence baseline, preprocessing ablations, threshold sensitivity, and
  decision-curve net benefit are included.
- Prevalence Wilson intervals, center-by-label prevalence, and
  missingness-by-center/label diagnostics strengthen EDA.
- The literature review now contains a related-work table and 20 references.
- Calibration is described as label-dependent; conformal evidence is presented
  per label before aggregate coverage.
- Typhoid false negatives and center-transfer failures are headline limitations.
- A package lock snapshot and SHA-256 artifact provenance manifest were added.
- The public static bundle no longer contains patient records.

## Fresh Results

The verified quick recomputation profile selected Extra Trees for pre-lab
triage:

- Held-out macro F1: **0.6095**, bootstrap 95% CI **0.5021-0.7013**
- Held-out micro F1: **0.8240**, bootstrap 95% CI **0.7619-0.8797**
- Held-out macro PR-AUC: **0.6059**, bootstrap 95% CI **0.5318-0.7721**
- Held-out macro recall: **0.6968**, bootstrap 95% CI **0.5269-0.8450**

Repeated train-only CV macro F1 ranged from **0.5796 to 0.6010**. Removing
center features slightly improved OOF macro F1 from **0.6010 to 0.6106**,
supporting the shortcut-learning concern.

Rare-label limitations remain material:

- Typhoid: recall **0.2857**, F1 **0.3077**, conformal coverage **0.5714**
- Yellow fever: three held-out positives; F1 **0.3333**
- Leave-one-center-out macro F1: **0.3555** and **0.3652**
- Dengue, typhoid, and yellow-fever transfer recall: **0 at both centers**

These results are intentionally less flattering than the prior artifact because
the revised pipeline is methodologically stricter.

## Why The Remaining Seven Points Are Not Software Fixes

1. The holdout contains only seven typhoid and three yellow-fever positives.
2. There is no prospective, temporal, or external multi-center validation set.
3. Triage weights and decision thresholds have not been clinically validated.
4. Fairness and conformal estimates remain unstable for rare labels.
5. The verified run used the documented quick recomputation profile; the full
   six-family benchmark remains available but is substantially slower.

The notebook is therefore positioned as a **competition prototype requiring
prospective validation**, which is the strongest defensible competition story.
