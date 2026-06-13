# VECTRA-X Rubric Maximization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address the scientific, reporting, reproducibility, and privacy gaps in the 13 June 2026 rubric reassessment.

**Architecture:** Add fitted train-only feature transformation and reusable evaluation utilities, refactor the pipeline to generate judge-facing evidence, and regenerate the final notebook from those artifacts. Keep the pre-lab model as the primary claim and treat all operational layers as prototype decision support.

**Tech Stack:** Python 3.12, pandas, NumPy, scikit-learn, Plotly, nbformat, unittest.

---

### Task 1: Lock Scientific Contracts With Tests

**Files:**
- Create: `tests/test_scientific_upgrade.py`
- Modify: `tests/test_final_notebook.py`

- [ ] Write failing tests for train-only category/schema learning.
- [ ] Write failing tests for bootstrap confidence intervals and provenance.
- [ ] Write failing tests preventing patient-level static export.
- [ ] Write failing tests for required notebook evidence and references.
- [ ] Run tests and verify failures are caused by missing behavior.

### Task 2: Implement Train-Only Transformation And Evaluation Utilities

**Files:**
- Modify: `src/preprocessing.py`
- Modify: `src/evaluation.py`
- Create: `src/scientific_analysis.py`

- [ ] Implement a fitted feature-frame transformer with unknown-category handling.
- [ ] Implement bootstrap intervals, Wilson intervals, repeated-CV aggregation, and decision net benefit.
- [ ] Implement missingness dependence, center prevalence, ablation, and provenance helpers.
- [ ] Run focused tests until green.

### Task 3: Refactor Pipeline And Privacy Export

**Files:**
- Modify: `run_pipeline.py`
- Modify: `app/dashboard_utils.py`
- Modify: `export_web_data.py`

- [ ] Move the outer split before leakage screening and schema fitting.
- [ ] Fit audit/schema decisions on train and apply them unchanged to test/full data.
- [ ] Save fitted transformers with model bundles.
- [ ] Generate CI, repeated-CV, baseline, ablation, decision-curve, EDA, and provenance tables.
- [ ] Export aggregate-only public web data.

### Task 4: Upgrade The Final Notebook

**Files:**
- Modify: `scripts/build_final_notebook.py`
- Regenerate: `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`

- [ ] Add uncertainty-aware EDA and the finding-to-consequence table.
- [ ] Document strict train-only methodology and exact model-selection endpoint.
- [ ] Add baselines, repeated validation, confidence intervals, ablations, and decision curves.
- [ ] Add completed related work, citations, equations, and replication details.
- [ ] Rewrite calibration, conformal, center-transfer, privacy, and ethics discussion.

### Task 5: Recompute And Reassess

**Files:**
- Modify: `outputs/reports/project_rubric_reassessment_2026-06-13.md`
- Create: `outputs/reports/project_rubric_final_score_2026-06-13.md`

- [ ] Run the pipeline from raw data.
- [ ] Generate and execute the notebook top-to-bottom.
- [ ] Run all tests and compile checks.
- [ ] Re-score each rubric component from fresh evidence and state residual limitations.

