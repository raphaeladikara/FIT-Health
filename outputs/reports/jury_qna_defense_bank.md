# VECTRA-X — Jury Q&A Defense Bank

Concise, evidence-backed answers to anticipated questions. Numbers are reproducible
via `python run_pipeline.py`.

---

**Q1. Why multi-label and not multi-class?**
Because **158/300 patients have more than one diagnosis**. Multi-class would discard
co-diagnosis information and misrepresent the clinical problem. The binary encoding
also matches the free-text diagnosis with 100% agreement, so the multi-label structure
is real, not an artefact.

**Q2. Why exclude TDR / thick smear / *Dengue (Dengua)* from the pre-lab model?**
They are diagnostic-test / current-disease indicators. We confirmed this statistically:
*Dengue (Dengua)* has single-feature AUC ≈ 0.96 with the dengue label; *Test TDR* ≈ 0.85
and *Goutte épaisse* ≈ 0.80 with malaria. Using them at "triage" time inflates
performance the model could never deliver before tests exist. We use lab/rapid tests
only in the **lab-aware confirmation** model, and *Dengue (Dengua)* only in the
**research-only** model.

**Q3. Your full model scores higher — why not present that?**
Because its advantage is almost entirely a **leakage artefact**. Dengue F1 jumps from
0.57 (pre-lab) to 0.92 (full) solely because *Dengue (Dengua)* restates the dengue
outcome. The genuine lab tests add little to multi-label macro performance. Presenting
the full model as deployable would be clinically dishonest — exposing this is one of
our main contributions.

**Q4. Why is macro-F1 your primary metric, not accuracy?**
Malaria is present in 90% of patients. A model that predicts "malaria, nothing else"
scores high accuracy/micro-F1 while completely missing yellow fever and typhoid.
Macro-F1, per-label recall and PR-AUC protect the rare, high-impact labels.

**Q5. Malaria recall is 1.0 — isn't that overfitting?**
No — it reflects hyperendemic reality. The pre-lab model **cannot rule out malaria from
symptoms alone** (ROC-AUC for malaria is only ~0.70 despite recall 1.0). That is
exactly why a confirmatory test matters, and why our triage flags patients for testing
rather than over-trusting the symptom-only prediction.

**Q6. Why conformal prediction?**
In healthcare, forcing one label under ambiguity is unsafe. Conformal prediction sets
let the model say "consider dengue or typhoid — request a confirmatory test"
(empirical coverage 94.8% at a 90% target). It can also abstain. We documented the
small-sample caveat for rare labels honestly.

**Q7. Your conformal sets average ~2.9 labels — isn't that too large?**
Malaria is in nearly every set because it is present in 90% of patients, so a set of
{malaria, +1–2 others} is expected and clinically sensible. The informative signal is
the **≥2-label ambiguous sets**, which correctly route patients to confirmatory testing.

**Q8. How do you handle the rare labels (yellow fever, typhoid)?**
Class-balanced learning, recall-oriented thresholds (the "safety" policy), a dedicated
rare-label sentinel, and — crucially — we **report uncertainty instead of overclaiming**.
With only 12 yellow-fever positives we treat its metrics as estimates and lean on the
conformal/sentinel layer rather than a hard diagnosis.

**Q9. Is your evaluation leakage-free?**
Yes. Thresholds, calibrators and conformal quantiles are fit on **out-of-fold train**
predictions and applied to a held-out test split. Imputation and scaling are fit inside
CV folds. Model selection uses 5-fold OOF macro-PR-AUC (more stable than the 77-row test).

**Q10. How well does it generalise across facilities?**
We ran a **leave-one-center-out** stress test: macro-F1 drops to ≈ 0.38 when
transferring between the two centers, revealing genuine workflow/domain shift. We
report this openly and recommend per-facility recalibration — we do not hide it.

**Q11. How do you use external data without breaking the rules?**
The official dataset is the **only** training source. Because there is no patient
timestamp or coordinate, external data (WHO/CDC guidelines, OSM/WorldPop/climate) is
used **only** for literature, facility context and dashboard — never merged into
patient-level training. This is enforced, not just promised.

**Q12. Your features are anonymised — how can you explain them?**
We explain them as **model signals, not medical causes**. Global permutation importance
and a transparent logistic surrogate for local attributions show *what the model used*;
we make no causal medical claims from encoded variables.

**Q13. Can this replace a clinician?**
No. VECTRA-X is **decision support** — it prioritises, quantifies uncertainty and
explains. Every recommendation is an action like "prioritise confirmatory testing" or
"flag for urgent evaluation", never a treatment or autonomous diagnosis.

**Q14. Why these models (Extra Trees / XGBoost) and not deep learning?**
With n=300 and ~100 features, regularised tree ensembles are the right tool; we
benchmarked six families with multi-label stratified CV and selected by OOF PR-AUC.
Deep tabular models would need heavy regularisation and offer little upside at this n.

**Q15. What is the single biggest innovation?**
**Stage-aware multi-label triage**: pre-lab vs lab-aware scoreboards, co-infection
detection, calibrated uncertainty, conformal safety, explainability and a fairness
audit — wrapped in a deployable triage + resource engine.

**Q16. What would you do with more data / time?**
Collect more rare-label cases and timestamp/location metadata (to responsibly add
climate/geospatial context), prospectively validate calibration, add per-facility
recalibration, and test classifier-chain co-diagnosis priors at scale.
