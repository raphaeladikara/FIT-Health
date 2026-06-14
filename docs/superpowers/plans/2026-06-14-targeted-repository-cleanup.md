# Targeted Repository Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a minimal, coherent repository whose scientific and public claims are synchronized with the final leakage-safe notebook.

**Architecture:** Keep the final notebook and `final_*` tables as canonical evidence. Rebuild the existing static dashboard data contract from those tables, retain only supporting scenario artifacts, and remove retired runtimes and duplicate generated files without altering the dashboard design.

**Tech Stack:** Python 3.12, pandas, scikit-learn, Jupyter, static HTML/CSS/ES modules, Node test runner, Git.

---

### Task 1: Lock the Canonical Repository Contract

**Files:**
- Modify: `tests/test_export_web_data.py`
- Create: `tests/test_repository_cleanliness.py`

- [ ] Add tests requiring cohort size 299, canonical final metrics, exact/pragmatic
  conformal separation, and absence of public FULL results.
- [ ] Add tests requiring the Streamlit app and obsolete notebooks to be absent.
- [ ] Run the focused tests and confirm they fail against the legacy repository.

### Task 2: Remove Retired and Duplicate Artifacts

**Files:**
- Delete: `app/streamlit_app.py`
- Delete: `notebooks/01_data_audit_eda.ipynb`
- Delete: `notebooks/02_modeling_multilabel.ipynb`
- Delete: `notebooks/03_explainability_uncertainty_triage.ipynb`
- Modify: `requirements.txt`
- Modify: `.gitignore`

- [ ] Remove the retired runtime, superseded notebooks, Streamlit dependency, local
  caches, serialized caches/models, and generated duplicates not used by the final
  notebook or static dashboard.
- [ ] Preserve all Markdown history and official raw data.

### Task 3: Rebuild the Public Evidence Contract

**Files:**
- Modify: `export_web_data.py`
- Modify: `scripts/validate_web_bundle.py`
- Modify: `web/assets/dashboard.js`
- Modify: `web/assets/landing.js`
- Modify: `web/assets/demo.js`
- Modify: `web/data/*.json`

- [ ] Build summary, final metrics, per-label metrics, calibration, conformal,
  fairness, leakage, and LOCO evidence from canonical final tables.
- [ ] Keep curated anonymous demo cases and deterministic scenario projections.
- [ ] Remove public FULL model evidence and stale cohort-300 claims.
- [ ] Regenerate and validate the static bundle.

### Task 4: Align Documentation and Entrypoints

**Files:**
- Modify: `README.md`
- Modify: `web/README.md`
- Modify: `docs/dashboard-capabilities.md`
- Modify: `run_pipeline.py`

- [ ] Document the final notebook as the sole scientific notebook.
- [ ] Remove Streamlit launch and capability references from current documentation.
- [ ] Describe historical Markdown as retained provenance.
- [ ] Ensure pipeline/export messaging names the canonical public bundle correctly.

### Task 5: Verify and Publish

**Files:**
- Verify: entire repository

- [ ] Run Python tests, compile checks, notebook validation, web export validation,
  Node tests, JavaScript syntax checks, and Git whitespace checks.
- [ ] Inspect staged scope with `git diff --cached --stat`.
- [ ] Commit all approved cleanup changes.
- [ ] Push `main` to `origin/main`.

