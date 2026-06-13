# Leakage & Clinical-Stage Audit

*Stage-gated feature sets*

_Generated: 2026-06-13 12:31 — VECTRA-X pipeline_

Features were screened by **name pattern** AND **statistics** (mutual information + single-feature ROC-AUC vs each active label). Decisions:

| feature_set | n_features |
| --- | --- |
| PRE_LAB_TRIAGE | 82 |
| LAB_AWARE_CONFIRMATION | 98 |
| FULL_RESEARCH_ONLY | 99 |


## Confirmed leakage / lab-confirmation features

| feature | decision | best_label | max_single_feature_auc | mutual_info | rationale |
| --- | --- | --- | --- | --- | --- |
| Dengue (Dengua) | research_only | dengue | 0.9643 | 0.4052 | Disease-named feature ~ target (post-diagnosis) |
| Test TDR | lab_aware | malaria | 0.8537 | 0.0910 | Ordered lab / rapid diagnostic test |
| Goutte épaisse | lab_aware | malaria | 0.8037 | 0.0734 | Ordered lab / rapid diagnostic test |
| Neutrophiles / Neutrophils | lab_aware | typhoid | 0.6816 | 0.0047 | Ordered lab / rapid diagnostic test |
| Numération plaquettaire Platelet count | lab_aware | other_diseases | 0.6700 | 0.1040 | Ordered lab / rapid diagnostic test |
| Nombre de globules blancs (cellules/ML) / White blood cell count / WBC count (cells/ML) | lab_aware | typhoid | 0.6648 | 0.0127 | Ordered lab / rapid diagnostic test |
| Créatinine élevée / Elevated Creatinine | lab_aware | dengue | 0.6341 | 0.0019 | Ordered lab / rapid diagnostic test |
| Hémoconcentration | lab_aware | dengue | 0.6221 | 0.0000 | Ordered lab / rapid diagnostic test |
| Hematocrite (Hematrocrit) | lab_aware | malaria | 0.6193 | 0.0378 | Ordered lab / rapid diagnostic test |
| Thrombocytopénie(Thrombocytopenia) | lab_aware | malaria | 0.5722 | 0.0147 | Ordered lab / rapid diagnostic test |
| Lymphocytes | lab_aware | malaria | 0.5575 | 0.0030 | Ordered lab / rapid diagnostic test |
| ALAT / ASAT élevés. / Elevated ALAT / Elevated ASAT | lab_aware | typhoid | 0.5517 | 0.0000 | Ordered lab / rapid diagnostic test |
| Transaminases (Transaminases) | lab_aware | typhoid | 0.5387 | 0.0000 | Ordered lab / rapid diagnostic test |
| CRP>50 /CRP 10-50 | lab_aware | typhoid | 0.5221 | 0.0000 | Ordered lab / rapid diagnostic test |
| Lymphocytopénie (Lymphocytopenia) | lab_aware | malaria | 0.5204 | 0.0195 | Ordered lab / rapid diagnostic test |
| Neutropénie (Neutropenia) | lab_aware | malaria | 0.5204 | 0.0112 | Ordered lab / rapid diagnostic test |
| Carences en leucocytes (Leucopenia) | lab_aware | malaria | nan | 0.0135 | Ordered lab / rapid diagnostic test |


## Decision logic

- **PRE_LAB_TRIAGE** — demographics, symptoms, vitals only; the honest early-triage model.
- **LAB_AWARE_CONFIRMATION** — adds ordered lab/rapid tests (TDR, thick smear, haematology).
- **FULL_RESEARCH_ONLY** — adds target-restatement features (e.g. *Dengue (Dengua)*, AUC≈0.96) to demonstrate the cost of leakage; never deployed.
