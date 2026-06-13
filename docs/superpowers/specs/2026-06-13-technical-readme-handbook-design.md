# VECTRA-X Technical README Handbook Design

## Goal

Replace the current root `README.md` with a comprehensive English technical
handbook for developers and technical reviewers. The handbook must explain what
VECTRA-X does, why its architecture and evaluation protocol were chosen, how
data moves through the system, how to reproduce every major artifact, and how
to safely extend or troubleshoot the project.

## Primary Audience

- Developers maintaining or extending the repository.
- Technical reviewers auditing scientific validity, leakage controls,
  reproducibility, privacy, and implementation quality.
- Secondary readers such as competition judges may use the executive summary,
  results, and limitations sections, but the document will prioritize technical
  precision over promotional presentation.

## Documentation Principles

1. Derive claims from current code, configuration, tests, or generated
   artifacts.
2. Distinguish train-only model-selection evidence, untouched held-out test
   evidence, and full-cohort out-of-fold dashboard predictions.
3. Present PRE_LAB as the honest early-triage track, LAB_AWARE as confirmation
   support, and FULL as a research-only leakage demonstration.
4. Treat VECTRA-X as decision support that requires prospective validation, not
   as a diagnostic authority.
5. Separate aggregate public web artifacts from local patient-level Streamlit
   workflows.
6. Keep commands Windows-friendly while including portable Python alternatives.
7. Link concepts to concrete files, outputs, and tests so reviewers can verify
   each claim.

## Proposed README Structure

### 1. Project Identity

- Project title and technical subtitle.
- Competition context.
- One-paragraph system summary.
- Clinical safety and research-status warning.

### 2. Quick Start

- Prerequisites.
- Virtual environment and dependency installation.
- Full, quick, and cached pipeline commands.
- Streamlit launcher and manual launch commands.
- Test command.

### 3. Problem Definition

- Dataset shape and source files.
- Multi-label target interpretation.
- Active and inactive labels.
- Co-infection prevalence.
- Why ordinary multiclass classification is inappropriate.

### 4. Core Design Principles

- Clinical-stage feature gating.
- Leakage prevention.
- Train-only transformations.
- Multi-label stratification.
- Honest holdout evaluation.
- Calibrated and uncertainty-aware outputs.
- Transparent operational decision rules.

### 5. System Architecture

- Mermaid architecture diagram.
- Raw inputs, pipeline orchestrator, domain modules, generated artifacts,
  notebook, local dashboard, static dashboard, and submission outputs.
- Clear separation between training-time and presentation-time components.

### 6. End-to-End Data Flow

- The complete 15-stage pipeline in execution order.
- Inputs, main computations, and outputs for each stage.
- Explanation of the three prediction contexts:
  train OOF, held-out test, and full-cohort OOF.

### 7. Repository Structure

- Accurate current directory tree.
- Responsibility of each top-level file and folder.
- Explicit distinction between source files and generated artifacts.

### 8. Data Loading and Schema Audit

- Semicolon delimiter, decimal comma, encoding fallback, UUID handling.
- Automated role/type classification.
- Missingness, duplicates, constant columns, and dictionary attachment.

### 9. Label Engineering

- Detection from prefixed diagnosis columns.
- Canonical aliases.
- Binary conversion and free-text validation.
- Zero-positive label handling.
- Multi-label cardinality and co-occurrence outputs.

### 10. Leakage and Feature Staging

- Name-based and statistical leakage screens.
- PRE_LAB_TRIAGE, LAB_AWARE_CONFIRMATION, and FULL_RESEARCH_ONLY.
- Examples of legitimate pre-lab exposures, ordered tests, and target
  restatements.
- Why leakage can inflate apparent performance.

### 11. Preprocessing

- `FittedFeatureFrame` train-only fitting.
- Numeric parsing, blood-pressure parsing, binary encoding, categorical
  handling, missing indicators, constant removal, and unseen categories.
- Preservation of identical train/test design matrices.

### 12. Modeling Strategy

- Binary relevance.
- Candidate model zoo and optional dependency fallbacks.
- Classifier-chain supplemental benchmark.
- Multi-label stratified train/test and cross-validation splits.
- Model selection by train OOF macro PR-AUC.
- Saved deployable model bundle contents.

### 13. Evaluation Protocol

- Untouched 75/25 holdout.
- Per-label and aggregate metrics.
- Threshold optimization based only on train OOF predictions.
- Bootstrap confidence intervals.
- Repeated validation, simple baseline, preprocessing ablation, and
  decision-curve analysis.
- Interpretation caveats for rare labels.

### 14. Calibration, Conformal Prediction, and Uncertainty

- Brier score, ECE, reliability curves, and calibrator behavior.
- Label-conditional conformal sets and target coverage.
- Entropy, probability margin, predicted-label count, and conformal-set size.
- Meaning of low, moderate, and high uncertainty.

### 15. Co-Infection, Triage, and Resource Allocation

- Binary co-infection target and benchmark.
- Transparent triage score components and four operational tiers.
- Recommended action generation.
- Resource-demand simulation and threshold-policy trade-offs.

### 16. Explainability, Fairness, and Robustness

- Permutation importance, linear local explanations, and optional SHAP.
- Non-causality warning.
- Center, gender, and age subgroup metrics.
- Recall gaps and leave-one-center-out stress testing.
- Limits of fairness claims on a small sample.

### 17. Current Reproducible Results

- Values sourced from `outputs/dashboard_data/summary.json`,
  `model_leaderboard.csv`, `per_label_metrics.csv`, and bootstrap intervals.
- Separate held-out results from train OOF leaderboard values.
- Explicitly label the currently stored execution profile as `quick_smoke`.
- Include conformal, co-infection, uncertainty, triage, and center-transfer
  results.

### 18. Running the Project

- Environment setup.
- Pipeline modes and expected behavior.
- Rebuilding web data.
- Building and executing the final notebook.
- Building the technical submission report.
- Windows interpreter fallback examples.

### 19. Dashboards

- Local Streamlit command center with its four current workspaces.
- Aggregate-only static web dashboard.
- Privacy boundary: no patient records in the public static bundle.
- Windows `.bat` behavior and custom port usage.
- Vercel deployment instructions for `web/`.

### 20. Generated Artifacts

- Tables, figures, reports, models, dashboard data, final notebook exports, and
  submission files.
- Which artifacts are reproducible, which are caches, and which are
  presentation deliverables.

### 21. Testing and Verification

- Full unittest discovery command.
- Test-file responsibilities.
- Launcher smoke-test mechanism.
- Scientific, notebook, privacy, and submission assertions.
- Suggested pre-submission verification sequence.

### 22. Developer Module Reference

- One concise entry for every module under `src/`.
- Inputs, outputs, and responsibilities.
- Application, export, notebook-builder, and report-builder components.

### 23. Common Development Workflows

- Change configuration and rerun.
- Add a model.
- Add or reclassify a feature.
- Add an evaluation table or figure.
- Extend the dashboard without exposing patient data.
- Refresh notebook and submission artifacts.

### 24. Troubleshooting

- Python or Streamlit not found.
- `ModuleNotFoundError: app`.
- Missing output artifacts.
- Stale cached leaderboard.
- Optional XGBoost, LightGBM, or SHAP unavailable.
- Browser `file://` fetch failures.
- Notebook execution timeouts.

### 25. Reproducibility, Privacy, and Safety

- Random seed and dependency lock file.
- Artifact provenance and SHA-256 manifest.
- Local versus public data boundary.
- No patient-level public JSON.
- Clinical safety language and prospective-validation requirement.

### 26. Limitations and Future Work

- Small sample size.
- Rare-label instability.
- Center shift.
- Approximate conformal performance for rare labels.
- No prospective, temporal, or geographic validation.
- Recommended research and engineering extensions.

## Source-of-Truth Hierarchy

When documentation sources disagree, the README will use this priority:

1. Current executable code and tests.
2. Current configuration.
3. Current generated JSON/CSV artifacts.
4. Current focused design documents.
5. Existing README prose.

This hierarchy prevents outdated prose from overriding the implemented system.

## Accuracy Controls

- Do not claim the Streamlit app has ten pages; it currently has four
  workspaces.
- Do not claim `open_dashboard.bat` serves the static site; it launches
  Streamlit.
- Do not expose UUIDs or describe the public web bundle as patient-level.
- Do not mix quick-smoke stored results with hypothetical full-benchmark
  results.
- Do not describe FULL-track performance as deployable.
- Do not call predictions diagnoses.

## Verification Plan

After writing the README:

1. Scan every referenced path and command against the repository.
2. Parse current JSON/CSV artifacts to verify all reported numbers.
3. Run the full unittest discovery suite.
4. Run the launcher smoke test.
5. Search the README for stale claims such as "10 pages," static-launcher
   behavior, patient-level public JSON, or unsupported diagnostic language.
6. Review the final diff to ensure only documentation and its intended
   verification test changes are included.

## Out of Scope

- Changing pipeline behavior or scientific methodology.
- Regenerating expensive model outputs solely to improve headline metrics.
- Redesigning either dashboard.
- Rewriting generated reports or notebooks.
- Publishing, deploying, committing unrelated worktree changes, or changing
  competition claims without evidence.
