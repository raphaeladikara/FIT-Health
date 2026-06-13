# Leakage & Clinical-Stage Audit

*Stage-gated feature sets*

_Generated: 2026-06-13 13:56 — VECTRA-X pipeline_

Features were screened by **name pattern** AND **statistics** (mutual information + single-feature ROC-AUC vs each active label). Decisions:

| feature_set | n_features |
| --- | --- |
| PRE_LAB_TRIAGE | 82 |
| LAB_AWARE_CONFIRMATION | 98 |
| FULL_RESEARCH_ONLY | 99 |


## Confirmed leakage / lab-confirmation features

| feature | decision | best_label | max_single_feature_auc | mutual_info | rationale |
| --- | --- | --- | --- | --- | --- |
| Dengue (Dengua) | research_only | dengue | 0.9762 | 0.4446 | Disease-named feature ~ target (post-diagnosis) |
| Test TDR | lab_aware | malaria | 0.8659 | 0.0983 | Ordered lab / rapid diagnostic test |
| Goutte épaisse | lab_aware | malaria | 0.7884 | 0.0663 | Ordered lab / rapid diagnostic test |
| Neutrophiles / Neutrophils | lab_aware | typhoid | 0.7490 | 0.0635 | Ordered lab / rapid diagnostic test |
| Nombre de globules blancs (cellules/ML) / White blood cell count / WBC count (cells/ML) | lab_aware | typhoid | 0.6950 | 0.0359 | Ordered lab / rapid diagnostic test |
| Hematocrite (Hematrocrit) | lab_aware | malaria | 0.6933 | 0.0253 | Ordered lab / rapid diagnostic test |
| Numération plaquettaire Platelet count | lab_aware | dengue | 0.6535 | 0.0403 | Ordered lab / rapid diagnostic test |
| Créatinine élevée / Elevated Creatinine | lab_aware | dengue | 0.6360 | 0.0174 | Ordered lab / rapid diagnostic test |
| Lymphocytes | lab_aware | malaria | 0.6278 | 0.0007 | Ordered lab / rapid diagnostic test |
| Hémoconcentration | lab_aware | typhoid | 0.6265 | 0.0188 | Ordered lab / rapid diagnostic test |
| Thrombocytopénie(Thrombocytopenia) | lab_aware | typhoid | 0.5594 | 0.0000 | Ordered lab / rapid diagnostic test |
| ALAT / ASAT élevés. / Elevated ALAT / Elevated ASAT | lab_aware | typhoid | 0.5547 | 0.0000 | Ordered lab / rapid diagnostic test |
| Transaminases (Transaminases) | lab_aware | typhoid | 0.5398 | 0.0000 | Ordered lab / rapid diagnostic test |
| CRP>50 /CRP 10-50 | lab_aware | malaria | 0.5278 | 0.0000 | Ordered lab / rapid diagnostic test |
| Lymphocytopénie (Lymphocytopenia) | lab_aware | typhoid | 0.5249 | 0.0000 | Ordered lab / rapid diagnostic test |
| Neutropénie (Neutropenia) | lab_aware | malaria | 0.5201 | 0.0000 | Ordered lab / rapid diagnostic test |
| Carences en leucocytes (Leucopenia) | lab_aware | malaria | nan | 0.0000 | Ordered lab / rapid diagnostic test |


## Decision logic

- **PRE_LAB_TRIAGE** — demographics, symptoms, vitals only; the honest early-triage model.
- **LAB_AWARE_CONFIRMATION** — adds ordered lab/rapid tests (TDR, thick smear, haematology).
- **FULL_RESEARCH_ONLY** — adds target-restatement features (e.g. *Dengue (Dengua)*, AUC≈0.96) to demonstrate the cost of leakage; never deployed.
