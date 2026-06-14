# Fairness & Robustness Summary

*Subgroup + center shift*

_Generated: 2026-06-14 20:04 — VECTRA-X pipeline_

Audited axes: health center, gender, age group. Goal: no systematic under-detection for any subgroup.


## Recall gaps (max − min across subgroup levels)

| axis | label | max_recall | min_recall | recall_gap | worst_level |
| --- | --- | --- | --- | --- | --- |
| gender | malaria | 1.0000 | 1.0000 | 0.0000 | Homme |
| gender | other_diseases | 0.7500 | 0.6923 | 0.0577 | Homme |
| gender | dengue | 0.4286 | 0.2857 | 0.1429 | Homme |
| gender | typhoid | 0.5000 | 0.3333 | 0.1667 | Femme |
| center | malaria | 1.0000 | 1.0000 | 0.0000 | CMA de DO |
| center | other_diseases | 1.0000 | 0.6111 | 0.3889 | CMA de DAFRA |
| center | dengue | 0.4167 | 0.0000 | 0.4167 | CMA de DAFRA |
| center | typhoid | 0.6000 | 0.0000 | 0.6000 | CMA de DAFRA |
| center | yellow_fever | 0.0000 | 0.0000 | 0.0000 | CMA de DO |
| age_group | malaria | 1.0000 | 1.0000 | 0.0000 | infant_<=5 |
| age_group | other_diseases | 1.0000 | 0.0000 | 1.0000 | adolescent_13_18 |
| age_group | dengue | 0.6667 | 0.0000 | 0.6667 | infant_<=5 |
| age_group | typhoid | 1.0000 | 0.0000 | 1.0000 | infant_<=5 |
| age_group | yellow_fever | 0.0000 | 0.0000 | 0.0000 | adult_19_50 |


![Recall gaps](../figures/fairness_recall_gap.png)

*Recall gaps*


## Leave-one-center-out stress test

Macro-F1 when transferring across centers: [0.2645, 0.3062].
