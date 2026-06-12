# VECTRA-X — Blueprint Execution Summary

*Dataset-aware extraction of the VECTRA-X Refined Blueprint (FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction), reconciled with what was actually verified in `data.csv`.*

This document is **Step 1** of the execution: it distils the blueprint's technical
requirements and records how each was realised (or adjusted) after inspecting the
real dataset. Every dataset figure below was **re-computed from `data.csv`**, not
copied from the blueprint.

---

## 1. Project objective

Build a **Clinical Triage Intelligence System** — not a generic disease classifier —
for vector-borne disease response. The system must:

- predict **multiple co-occurring** vector-borne diseases per patient (multi-label),
- separate what is knowable **before** vs **after** laboratory confirmation
  (leakage-aware staging),
- quantify **uncertainty** and emit **conformal prediction sets** instead of forcing
  one label,
- **explain** predictions, **audit fairness**, and translate outputs into a
  **triage priority** + **resource** view.

Final positioning: *"Prediction is not enough. In humanitarian health response the
model must know when it is uncertain, explain why, and help prioritise action."*

## 2. Dataset-aware adjustments (verified)

| Blueprint claim | Verified in `data.csv` | Consequence |
|---|---|---|
| ~300 × 109, 0 duplicates | **300 × 109, 0 duplicates, 300 unique UUIDs** | small + high-dimensional → regularise, CV, report uncertainty |
| Multi-label diagnosis | **158/300 patients have >1 diagnosis**; binary↔free-text agreement **100%** | multi-label (binary relevance / classifier chains), not multi-class |
| 5 active labels | malaria **270 (90%)**, other diseases **99 (33%)**, dengue **56 (18.7%)**, typhoid **29 (9.7%)**, yellow fever **12 (4%)** | macro-F1 + per-label recall, not accuracy |
| 3 inactive labels | chikungunya **0**, zika **0**, option 8 **0** | excluded from scoring; reported as a limitation |
| Leakage features | *Dengue (Dengua)* single-feature AUC≈**0.96**; *Test TDR* AUC≈0.85; *Goutte épaisse* AUC≈0.80 | stage-gated pre-lab / lab-aware / full-research feature sets |
| No timestamp/coordinates | confirmed: only health-center names | external data is **supplementary only** (literature/dashboard), never patient-level training |
| 2 health centers | CMA de DAFRA / CMA de DO | fairness + leave-one-center-out axis |

## 3. Major modeling tracks (implemented)

- **M1 — Pre-lab triage (headline model):** 82 features (demographics, symptoms,
  vitals). The realistic, deployable early-triage model.
- **M2 — Lab-aware confirmation:** 98 features (adds TDR, thick smear, haematology).
  Confirmation support, not early triage.
- **M3 — Full research-only:** 99 features (adds the *Dengue (Dengua)*
  target-restatement). Used **only** to quantify the cost of leakage; never deployed.
- **M3-chain — Classifier chains:** supplemental, exploits co-diagnosis dependency.
- **M4 — Co-infection detector:** binary target = (#labels > 1).
- **M5 — Rare-label sentinel:** recall-oriented, class-weighted handling for yellow
  fever / typhoid.
- **M5/M6 — Uncertainty, conformal, calibration, triage priority engine.**

Each track is benchmarked across Logistic Regression, Random Forest, Extra Trees,
HistGradientBoosting, XGBoost and LightGBM (binary relevance), with multi-label
stratified CV.

## 4. Leakage strategy (the methodological core)

Features are screened by **name pattern AND statistics** (mutual information +
single-feature ROC-AUC vs each label), then partitioned:

- **PRE_LAB_TRIAGE (82)** — no diagnostic tests, no target-restatements.
- **LAB_AWARE_CONFIRMATION (98)** — adds ordered lab/rapid tests.
- **FULL_RESEARCH_ONLY (99)** — adds *Dengue (Dengua)*.

Two scoreboards are presented (pre-lab vs lab-aware) so the model looks clinically
honest and methodologically superior. *Diagnosis label columns and the free-text
diagnosis are targets only — never features.*

## 5. Advanced features implemented

- Multi-label stratified CV (`iterstrat`) preserving prevalence + co-occurrence.
- Per-label threshold optimisation with **3 clinical policies** (performance / safety / operational).
- Probability **calibration** (Platt/isotonic) + Brier + ECE + reliability curves.
- **Split-conformal** recall-oriented multi-label prediction sets (per-label thresholds, coverage report).
- **Uncertainty** scores (entropy, top-2 margin, #labels above threshold, set size) → low/moderate/high.
- **Explainability**: permutation importance (global + per-label) + linear-surrogate local case studies + optional SHAP.
- **Fairness**: subgroup recall/FNR (center, gender, age) + **leave-one-center-out** stress test.
- **Triage engine**: transparent risk + severe + uncertainty + co-infection score → 4 tiers + decision-support actions.
- **Resource simulation** + threshold-policy trade-off.
- **Streamlit dashboard** (10 pages) loading precomputed artifacts.

## 6. Expected final deliverables

Project folder with `src/` modules, 3 notebooks, `run_pipeline.py`; data-audit,
leakage-audit, EDA, modeling, threshold, calibration, uncertainty, conformal,
explainability, fairness, triage and resource reports; trained pre-lab + lab-aware
models; ~27 tables and ~26 figures; technical-report draft; presentation outline;
jury Q&A bank; limitations/ethics; README + `requirements.txt`.

## 7. Assumptions and risks

- **Small n (300):** high variance — report per-label support, avoid overclaiming;
  rare-label metrics are estimates.
- **Missing ≠ negative:** lab/vital missingness kept as `__missing` indicators
  (workflow signal); never converted to `NON`.
- **Anonymised features:** explanations describe **model signals, not medical
  causation**.
- **Decision support, not diagnosis:** the system prioritises and explains; it does
  not replace clinicians.
- **External data:** literature/context/dashboard only — never merged into
  patient-level training (no timestamp/coordinates exist).
