# Leakage & Clinical-Stage Audit

*Stage-gated feature sets*

_Generated: 2026-06-14 20:04 — VECTRA-X pipeline_

Features were screened by **name pattern** AND **statistics** (mutual information + single-feature ROC-AUC vs each active label). Decisions:

| feature_set | n_features |
| --- | --- |
| PRE_LAB_TRIAGE | 81 |
| LAB_AWARE_CONFIRMATION | 97 |
| FULL_RESEARCH_ONLY | 99 |


## Confirmed leakage / lab-confirmation features

| feature | decision | best_label | max_single_feature_auc | mutual_info | rationale |
| --- | --- | --- | --- | --- | --- |
| Autres maladies présentées par le patient | research_only | other_diseases | 0.9747 | 0.5620 | Explicitly governed target-restatement / post-diagnosis field |
| Dengue (Dengua) | research_only | dengue | 0.9643 | 0.4084 | Disease-named feature ~ target (post-diagnosis) |
| Test TDR | lab_aware | malaria | 0.8681 | 0.1019 | Ordered lab / rapid diagnostic test |
| Goutte épaisse | lab_aware | malaria | 0.8163 | 0.0853 | Ordered lab / rapid diagnostic test |
| Neutrophiles / Neutrophils | lab_aware | typhoid | 0.6815 | 0.0098 | Ordered lab / rapid diagnostic test |
| Numération plaquettaire Platelet count | lab_aware | other_diseases | 0.6701 | 0.0765 | Ordered lab / rapid diagnostic test |
| Nombre de globules blancs (cellules/ML) / White blood cell count / WBC count (cells/ML) | lab_aware | typhoid | 0.6645 | 0.0077 | Ordered lab / rapid diagnostic test |
| Lymphocytes | lab_aware | typhoid | 0.6577 | 0.0071 | Ordered lab / rapid diagnostic test |
| Créatinine élevée / Elevated Creatinine | lab_aware | dengue | 0.6340 | 0.0200 | Ordered lab / rapid diagnostic test |
| Hematocrite (Hematrocrit) | lab_aware | malaria | 0.6229 | 0.0373 | Ordered lab / rapid diagnostic test |
| Hémoconcentration | lab_aware | dengue | 0.6227 | 0.0272 | Ordered lab / rapid diagnostic test |
| Thrombocytopénie(Thrombocytopenia) | lab_aware | malaria | 0.5716 | 0.0000 | Ordered lab / rapid diagnostic test |
| ALAT / ASAT élevés. / Elevated ALAT / Elevated ASAT | lab_aware | typhoid | 0.5519 | 0.0000 | Ordered lab / rapid diagnostic test |
| Transaminases (Transaminases) | lab_aware | typhoid | 0.5389 | 0.0000 | Ordered lab / rapid diagnostic test |
| CRP>50 /CRP 10-50 | lab_aware | yellow_fever | 0.5348 | 0.0007 | Ordered lab / rapid diagnostic test |
| Neutropénie (Neutropenia) | lab_aware | malaria | 0.5215 | 0.0000 | Ordered lab / rapid diagnostic test |
| Lymphocytopénie (Lymphocytopenia) | lab_aware | malaria | 0.5204 | 0.0000 | Ordered lab / rapid diagnostic test |
| Carences en leucocytes (Leucopenia) | lab_aware | malaria | 0.5172 | 0.0000 | Ordered lab / rapid diagnostic test |


## Decision logic

- **PRE_LAB_TRIAGE** — demographics, symptoms, vitals only; the honest early-triage model.
- **LAB_AWARE_CONFIRMATION** — adds ordered lab/rapid tests (TDR, thick smear, haematology).
- **FULL_RESEARCH_ONLY** — adds target-restatement features (e.g. *Dengue (Dengua)*, AUC≈0.96) to demonstrate the cost of leakage; never deployed.
