# VECTRA-X Competition Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a fully executable competition notebook and a tested, utility-first Streamlit dashboard that performs saved-model inference, interactive patient review, threshold simulation, resource planning, and robust artifact fallback.

**Architecture:** Keep the existing pipeline and artifacts as the source of truth. Add a small dashboard utility layer with pure functions and tests, compose it from Streamlit, and generate the final notebook programmatically so required sections and execution behavior can be verified automatically.

**Tech Stack:** Python 3.12, pandas, NumPy, scikit-learn, joblib, Plotly, Streamlit, nbformat, nbclient, unittest.

---

### Task 1: Create a Functional Baseline and Branch

**Files:**
- Modify: `.gitignore`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create and switch to `codex/vectra-x-competition-upgrade`.**
- [ ] **Step 2: Add notebook checkpoint and test cache paths to `.gitignore`.**
- [ ] **Step 3: Run Python dependency imports and compile the current dashboard.**
- [ ] **Step 4: Record any pre-existing failures before production edits.**

### Task 2: Test Dashboard Utility Contracts

**Files:**
- Create: `tests/test_dashboard_utils.py`
- Create: `app/dashboard_config.py`
- Create: `app/dashboard_utils.py`

- [ ] **Step 1: Write failing tests for artifact loading, model availability, schema validation, threshold application, resource capacity calculations, patient report generation, and missing-file fallbacks.**
- [ ] **Step 2: Run `python -m unittest tests.test_dashboard_utils -v` and confirm failures are caused by missing utility functions.**
- [ ] **Step 3: Implement constants and pure utility functions with project-relative paths.**
- [ ] **Step 4: Run the utility tests and confirm all pass.**

### Task 3: Implement Saved-Model Batch Inference

**Files:**
- Modify: `tests/test_dashboard_utils.py`
- Modify: `app/dashboard_utils.py`

- [ ] **Step 1: Add failing tests using a temporary joblib model bundle and uploaded frame.**
- [ ] **Step 2: Verify the inference tests fail before implementation.**
- [ ] **Step 3: Implement feature-frame preparation, saved bundle loading, probability extraction, policy thresholds, and downloadable prediction assembly.**
- [ ] **Step 4: Add explicit errors for unsupported full-feature inference, missing columns, and incompatible bundles.**
- [ ] **Step 5: Run all utility tests.**

### Task 4: Rebuild the Streamlit Dashboard Around Working Utilities

**Files:**
- Modify: `app/streamlit_app.py`
- Test: `tests/test_dashboard_utils.py`

- [ ] **Step 1: Add global model-mode and threshold-policy controls.**
- [ ] **Step 2: Implement Executive Overview, Patient Prediction, Batch Upload, Population Overview, and Resource Prioritization as functional interactive pages.**
- [ ] **Step 3: Implement Model Trust, Explainability, Uncertainty, Fairness, and Methodology pages with available-artifact fallbacks.**
- [ ] **Step 4: Add downloads for patient predictions, one-page patient Markdown reports, resource scenarios, leaderboard data, and filtered triage output.**
- [ ] **Step 5: Compile and import-smoke-test all dashboard modules.**

### Task 5: Generate the Final Competition Notebook

**Files:**
- Create: `scripts/build_final_notebook.py`
- Create: `tests/test_final_notebook.py`
- Create: `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`
- Create: `outputs/final_notebook/.gitkeep`

- [ ] **Step 1: Write failing tests for required section headings, root detection, `RECOMPUTE_MODELS`, output directory creation, and notebook metadata.**
- [ ] **Step 2: Run notebook tests and confirm failure because the generator/notebook is absent.**
- [ ] **Step 3: Implement the nbformat generator with all required sections, narrative markdown, lightweight artifact-backed analysis, optional deterministic pipeline recomputation, patient case selection, Plotly views, and report exports.**
- [ ] **Step 4: Generate the notebook and run structural tests.**
- [ ] **Step 5: Execute the notebook top-to-bottom with the installed Python kernel and verify expected outputs under `outputs/final_notebook/`.**

### Task 6: Create Competition Audit and Judge Pitch

**Files:**
- Create: `outputs/reports/project_competitiveness_audit.md`
- Create: `outputs/reports/final_judge_pitch.md`

- [ ] **Step 1: Ground all claims in `summary.json`, leaderboard, per-label metrics, fairness, calibration, conformal, and resource tables.**
- [ ] **Step 2: Write strengths, risks, jury attack points, competitor comparison, improvement tiers, final framing, and FIT criterion scores.**
- [ ] **Step 3: Write 60-second, 3-minute, and 7-minute pitches plus judge Q&A.**
- [ ] **Step 4: Check both reports for unsupported claims and required sections.**

### Task 7: Update Documentation and Final Verification

**Files:**
- Modify: `README.md`
- Modify: `requirements.txt`
- Create: `outputs/dashboard_screenshots/README.md`

- [ ] **Step 1: Document the explicit Windows Python path fallback, notebook execution modes, dashboard command, upload schema behavior, and model-mode limitations.**
- [ ] **Step 2: Add missing direct dependencies such as Plotly, nbformat, nbclient, and ipykernel if required.**
- [ ] **Step 3: Run the full unittest suite, `py_compile`, notebook execution, and Streamlit headless smoke launch.**
- [ ] **Step 4: Inspect git diff and verify existing notebooks, scripts, outputs, and reports were preserved.**
- [ ] **Step 5: Commit the verified implementation with a scoped commit message.**
