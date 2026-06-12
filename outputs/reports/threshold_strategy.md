# Threshold Strategy

*Three clinical policies*

_Generated: 2026-06-13 02:43 — VECTRA-X pipeline_

Default 0.5 is rarely optimal under imbalance. Thresholds tuned per label on out-of-fold train predictions.


## Per-label optimisation

| label | thr_maxF1 | f1 | thr_recall_oriented | recall | thr_balanced |
| --- | --- | --- | --- | --- | --- |
| malaria | 0.0500 | 0.9531 | 0.0500 | 1.0000 | 0.0500 |
| other_diseases | 0.5000 | 0.9722 | 0.0500 | 1.0000 | 0.5000 |
| dengue | 0.3500 | 0.5000 | 0.2000 | 0.8571 | 0.3500 |
| typhoid | 0.5000 | 0.4444 | 0.4500 | 0.5455 | 0.5000 |
| yellow_fever | 0.2500 | 0.1579 | 0.0500 | 0.3889 | 0.1000 |


## Policies

| label | performance | safety | operational |
| --- | --- | --- | --- |
| malaria | 0.0500 | 0.0500 | 0.0500 |
| other_diseases | 0.5000 | 0.5000 | 0.5000 |
| dengue | 0.3500 | 0.2000 | 0.3500 |
| typhoid | 0.5000 | 0.4500 | 0.5000 |
| yellow_fever | 0.2500 | 0.0500 | 0.1000 |

- **Performance** — maximise per-label F1.
- **Safety** — lower thresholds for severe/rare labels (dengue, typhoid, yellow fever) to raise recall.
- **Operational** — balanced threshold to limit unnecessary confirmatory-test burden.


![Threshold vs F1](../figures/threshold_tradeoff.png)

*Threshold vs F1*
