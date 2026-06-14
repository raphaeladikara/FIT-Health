# VECTRA-X Scientific Notebook Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the competition notebook into a rigorous, reproducible scientific analysis that maximizes the three notebook scoring criteria while preserving honest limitations and safe real-world interpretation.

**Architecture:** Raw data flows through stateless feature derivation, fold-local preprocessing, repeated nested multi-label validation, locked model-and-threshold selection, and one frozen-test confirmation. The executed notebook exports a single versioned release bundle that becomes the only scientific source for the web phase.

**Tech Stack:** Python, pandas, NumPy, scikit-learn, iterative-stratification, SciPy, matplotlib, seaborn, joblib, nbformat, nbclient, pytest, JSON Schema.

---

## Scope And Non-Negotiable Rules

- This plan covers the notebook, scientific Python modules, tests, generated scientific artifacts, and release bundle.
- It does not redesign the website and does not include the Technical Report.
- `PRE_LAB` is the primary deployable track. `LAB_AWARE` is a paired secondary track.
- `RESEARCH_ONLY` and diagnosis-restating features may never enter deployable evidence.
- Every learned operation, including category encoding, imputation, calibration, model selection, and threshold selection, must be trained without access to the evaluated rows.
- The frozen test set is touched once, after the policy is locked from the training pool.
- Stronger validation is allowed to lower headline metrics. Scientific validity and defensibility take priority.
- All principal claims must state partition, patient count, positive support, and uncertainty.

## Target File Map

**Modify**

- `src/preprocessing.py`: preserve raw categorical values and build fold-local transformers.
- `src/schema_audit.py`: add impossible-range, unit, duplicate, and outlier checks.
- `src/modeling.py`: expose deterministic, constrained candidate configurations.
- `src/evaluation.py`: standardize aggregate and per-label metric computation.
- `src/research_evaluation.py`: add paired intervals, ablations, risk-coverage, and support-aware summaries.
- `src/calibration.py`: make calibration fold-safe and expose calibration diagnostics.
- `src/conformal.py`: separate exact and pragmatic prediction-set policies and efficiency metrics.
- `src/fairness.py`: add support-aware subgroup intervals and insufficient-evidence states.
- `src/explainability.py`: bind explanations to the locked model bundle.
- `src/notebook_workflow.py`: orchestrate the full scientific workflow without test leakage.
- `scripts/build_final_notebook.py`: rebuild the judge-facing narrative and appendix.
- `scripts/validate_final_notebook.py`: enforce structure, claims, execution, and artifact consistency.
- `run_pipeline.py`: delegate artifact creation to the canonical release exporter.
- `requirements.txt`: pin any newly required validation or stratification dependency.

**Create**

- `src/feature_contract.py`: define feature stages, raw-to-derived lineage, and clinical validity bounds.
- `src/nested_validation.py`: implement repeated nested multi-label model and threshold selection.
- `src/decision_analysis.py`: implement risk-coverage, abstention, and net-benefit analyses.
- `src/release_bundle.py`: write and validate the versioned scientific release.
- `config/clinical_ranges.json`: explicit hard-invalid and soft-warning ranges with source notes.
- `config/notebook_experiment.json`: seeds, folds, candidate models, threshold grid, bootstrap settings, and frozen-test policy.
- `schemas/scientific-release.schema.json`: machine-readable release contract.
- `tests/test_fold_local_preprocessing.py`
- `tests/test_feature_contract.py`
- `tests/test_nested_validation.py`
- `tests/test_decision_analysis.py`
- `tests/test_release_bundle.py`

**Generated, not manually edited**

- `notebooks/VECTRA_X_Final.ipynb`
- `outputs/releases/<run_id>/scientific-release.json`
- `outputs/releases/<run_id>/models/*.joblib`
- `outputs/releases/<run_id>/figures/*`
- `outputs/releases/<run_id>/tables/*`
- `outputs/releases/<run_id>/manifest.json`

## Task 1: Freeze The Experimental Contract

**Files**

- Create: `config/notebook_experiment.json`
- Modify: `tests/test_notebook_workflow.py`
- Modify: `src/notebook_workflow.py`

- [ ] Write a failing test that requires the workflow to load one explicit experiment configuration containing:
  - dataset path and target policy;
  - frozen-test size and seed;
  - outer folds, inner folds, and repeated seeds;
  - candidate model configurations;
  - threshold grid and threshold objective;
  - calibration methods;
  - bootstrap repetitions and confidence level;
  - minimum subgroup support;
  - release schema version.

- [ ] Run:

```powershell
python -m pytest tests/test_notebook_workflow.py -q
```

Expected: failure because the workflow currently embeds part of the policy in code.

- [ ] Add `config/notebook_experiment.json` with conservative defaults:
  - one stratified frozen split;
  - five outer folds across three deterministic seeds where support permits;
  - three inner folds;
  - modest logistic-regression and constrained tree candidates;
  - label-specific thresholds selected from training predictions only;
  - 2,000 paired bootstrap repetitions for final tables.

- [ ] Add a typed loader and validation function in `src/notebook_workflow.py`. Fail on unknown keys, duplicate seeds, impossible fold counts, or an empty candidate set.

- [ ] Re-run the focused test and commit:

```powershell
python -m pytest tests/test_notebook_workflow.py -q
git add config/notebook_experiment.json src/notebook_workflow.py tests/test_notebook_workflow.py
git commit -m "feat: freeze notebook experiment contract"
```

## Task 2: Replace Global Category Factorization

**Files**

- Modify: `src/preprocessing.py`
- Create: `tests/test_fold_local_preprocessing.py`
- Modify: `tests/test_pipeline_cohort_alignment.py`

- [ ] Write tests proving:
  - feature derivation preserves category strings;
  - an unseen validation category is handled without failure;
  - encoder categories contain training values only;
  - imputer statistics are learned from training rows only;
  - transformed columns are deterministic across repeated fits;
  - row order and patient alignment are preserved.

- [ ] Run:

```powershell
python -m pytest tests/test_fold_local_preprocessing.py tests/test_pipeline_cohort_alignment.py -q
```

Expected: failure against the current global factorization path.

- [ ] Extend `FeatureMeta` with `categorical_cols`, raw source lineage, availability stage, and missingness-indicator metadata.

- [ ] Split preprocessing into two explicit stages:
  1. stateless raw feature derivation that may normalize names or derive clinically justified values but learns nothing from the cohort;
  2. a scikit-learn `ColumnTransformer` fitted inside each fold.

- [ ] Use:
  - numeric median imputation with optional missing indicators;
  - `OneHotEncoder(handle_unknown="ignore")` for nominal categories;
  - no global `factorize`, target encoding, or cohort-wide scaling;
  - stable feature-name extraction for explanation and release metadata.

- [ ] Ensure every candidate model receives preprocessing inside a `Pipeline`.

- [ ] Remove or deprecate every code path that accepts a globally transformed feature matrix for validation.

- [ ] Re-run tests and commit:

```powershell
python -m pytest tests/test_fold_local_preprocessing.py tests/test_pipeline_cohort_alignment.py -q
git add src/preprocessing.py tests/test_fold_local_preprocessing.py tests/test_pipeline_cohort_alignment.py
git commit -m "fix: make preprocessing fold local"
```

## Task 3: Formalize Feature Governance And Clinical Input Validity

**Files**

- Create: `src/feature_contract.py`
- Create: `config/clinical_ranges.json`
- Create: `tests/test_feature_contract.py`
- Modify: `src/leakage_audit.py`
- Modify: `tests/test_leakage_governance.py`

- [ ] Write failing tests requiring every deployable feature to have:
  - canonical raw name;
  - derived representation;
  - `PRE_LAB`, `LAB_AWARE`, or `RESEARCH_ONLY` stage;
  - transformation;
  - missingness behavior;
  - unit where applicable;
  - hard-invalid bounds;
  - soft observed-range warning policy;
  - leakage rationale.

- [ ] Add tests that fail when:
  - a derived feature loses its raw-source lineage;
  - a `RESEARCH_ONLY` source enters `PRE_LAB` or `LAB_AWARE`;
  - a diagnosis-restating source is renamed and then admitted;
  - the same raw feature has contradictory stages.

- [ ] Implement `FeatureContract`, `FeatureSpec`, and `validate_feature_contract`.

- [ ] Populate `config/clinical_ranges.json` only with defensible checks. Separate:
  - hard-invalid physiological or encoding values;
  - soft observed-distribution warnings learned later from training data;
  - values with no defensible hard bound.

- [ ] Update leakage auditing to evaluate raw-source lineage, not only transformed column names.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_feature_contract.py tests/test_leakage_governance.py -q
git add src/feature_contract.py src/leakage_audit.py config/clinical_ranges.json tests/test_feature_contract.py tests/test_leakage_governance.py
git commit -m "feat: enforce feature lineage and clinical stages"
```

## Task 4: Expand Data Integrity And Research-Question EDA

**Files**

- Modify: `src/schema_audit.py`
- Modify: `src/visualization.py`
- Modify: `tests/test_notebook_workflow.py`
- Modify: `scripts/build_final_notebook.py`

- [ ] Add tests for an audit result containing:
  - shape and schema;
  - exact and identifier-level duplicates;
  - target completeness and unknown-target exclusion;
  - units and impossible values;
  - suspected outliers;
  - label prevalence and support;
  - label cardinality and co-occurrence;
  - center composition;
  - missingness and prevalence by center.

- [ ] Implement structured audit tables. Do not silently mutate invalid data; classify each finding as `error`, `warning`, or `descriptive`.

- [ ] Add reusable plotting functions with stable label colors and partition subtitles for:
  - prevalence and support;
  - cardinality and co-occurrence;
  - demographics, symptoms, and vital signs;
  - global and center-stratified missingness;
  - center-stratified label prevalence;
  - suspected outliers with unit-aware captions.

- [ ] Add notebook section templates that require four short blocks after every principal figure:
  - `Finding`
  - `Interpretation`
  - `Operational Meaning`
  - `Limitation`

- [ ] Ensure captions distinguish association from prediction and causality.

- [ ] Run:

```powershell
python -m pytest tests/test_notebook_workflow.py tests/test_final_notebook_structure.py -q
```

- [ ] Commit:

```powershell
git add src/schema_audit.py src/visualization.py scripts/build_final_notebook.py tests/test_notebook_workflow.py tests/test_final_notebook_structure.py
git commit -m "feat: strengthen data integrity and EDA"
```

## Task 5: Define Constrained Candidate Models And Baselines

**Files**

- Modify: `src/modeling.py`
- Modify: `tests/test_model_variants.py`
- Modify: `src/research_evaluation.py`

- [ ] Write tests requiring deterministic candidate IDs and constrained parameter spaces.

- [ ] Include:
  - regularized one-vs-rest logistic regression;
  - constrained random forest or extra-trees configurations;
  - optional boosting only when installed and explicitly enabled;
  - no unrestricted search or dozens of near-duplicate configurations.

- [ ] Implement non-learned baselines:
  - always-malaria;
  - prevalence threshold;
  - prevalence-matched random with deterministic seeds.

- [ ] Define feature-family ablations:
  - demographics;
  - demographics plus symptoms;
  - plus vital signs;
  - plus laboratory variables;
  - center removed;
  - missingness indicators removed.

- [ ] Ensure every baseline and ablation returns the same metric schema as learned models.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_model_variants.py tests/test_research_evaluation.py -q
git add src/modeling.py src/research_evaluation.py tests/test_model_variants.py tests/test_research_evaluation.py
git commit -m "feat: add disciplined baselines and ablations"
```

## Task 6: Implement Repeated Nested Multi-Label Validation

**Files**

- Create: `src/nested_validation.py`
- Create: `tests/test_nested_validation.py`
- Modify: `src/modeling.py`
- Modify: `requirements.txt`

- [ ] Write isolation tests using spy estimators and synthetic row IDs. Prove that:
  - outer validation rows never enter inner model fitting;
  - outer labels never enter threshold selection;
  - preprocessing is refit inside each inner and outer training partition;
  - all outer predictions are out-of-sample;
  - seeds produce deterministic assignments;
  - every row appears in the expected number of outer validation folds.

- [ ] Add failure tests for labels whose support cannot sustain the requested folds. The workflow must reduce folds explicitly or mark the label/estimate insufficient; it must not silently use invalid stratification.

- [ ] Implement iterative multi-label stratification with recorded split diagnostics.

- [ ] Implement inner selection:
  1. produce inner out-of-fold probabilities for each candidate;
  2. fit any calibration only from inner-training evidence;
  3. choose label thresholds using the configured training-only objective and tie-break rules;
  4. score the complete candidate-plus-threshold policy;
  5. select one deterministic policy.

- [ ] Implement outer estimation:
  1. rerun the selected policy on the outer-training partition;
  2. predict untouched outer-validation rows;
  3. save probabilities, decisions, selected config, thresholds, support, and split IDs.

- [ ] Return tidy tables rather than deeply nested dictionaries:
  - `outer_predictions`;
  - `outer_policy_selections`;
  - `inner_candidate_scores`;
  - `split_support`;
  - `policy_stability`.

- [ ] Run:

```powershell
python -m pytest tests/test_nested_validation.py -q
```

- [ ] Commit:

```powershell
git add src/nested_validation.py src/modeling.py requirements.txt tests/test_nested_validation.py
git commit -m "feat: add nested multilabel validation"
```

## Task 7: Make Metrics, Thresholds, And Intervals Internally Consistent

**Files**

- Modify: `src/evaluation.py`
- Modify: `src/research_evaluation.py`
- Modify: `tests/test_research_evaluation.py`
- Modify: `tests/test_notebook_workflow.py`

- [ ] Add regression tests proving repeated-validation F1 and recall use the saved selected thresholds, never a hidden fixed `0.5`.

- [ ] Standardize one evaluation API accepting probabilities, decisions, targets, patient IDs, split IDs, and threshold metadata.

- [ ] Compute primary metrics:
  - macro PR-AUC;
  - macro F1;
  - macro recall;
  - per-label PR-AUC, F1, and recall.

- [ ] Compute secondary metrics:
  - micro F1;
  - Hamming loss;
  - sample Jaccard;
  - subset accuracy;
  - ROC-AUC with prevalence context.

- [ ] Add patient-level paired bootstrap intervals for aggregate metrics and label-level intervals where support permits. Resample patients, not individual label cells.

- [ ] Add paired `PRE_LAB` versus `LAB_AWARE` deltas with confidence intervals from identical rows and bootstrap draws.

- [ ] Require every exported metric row to include partition, `n_patients`, positive support, point estimate, lower bound, upper bound, and method.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_research_evaluation.py tests/test_notebook_workflow.py -q
git add src/evaluation.py src/research_evaluation.py tests/test_research_evaluation.py tests/test_notebook_workflow.py
git commit -m "fix: align thresholds metrics and uncertainty"
```

## Task 8: Add Reliability, Prediction Sets, And Decision Utility

**Files**

- Modify: `src/calibration.py`
- Modify: `src/conformal.py`
- Create: `src/decision_analysis.py`
- Create: `tests/test_decision_analysis.py`
- Modify: `tests/test_calibration_conformal.py`

- [ ] Write tests for:
  - calibration fitted without evaluated rows;
  - raw versus calibrated Brier score and ECE;
  - reliability-bin counts and positive support;
  - exact and pragmatic prediction-set policies stored under distinct names;
  - per-label, micro, and macro coverage;
  - set-size distribution, singleton rate, ambiguity, and false-negative risk;
  - monotonic risk-coverage output as review coverage increases;
  - deterministic net-benefit calculations under explicit cost assumptions.

- [ ] Refactor calibration to expose fit and apply stages and to retain calibration provenance.

- [ ] Refactor prediction sets so a nearly full set is reported as high coverage with poor efficiency, never simply “safe”.

- [ ] Implement abstention analysis using a documented uncertainty score. Export:
  - retained fraction;
  - reviewed fraction;
  - error or false-negative risk among retained cases;
  - label-specific support.

- [ ] Implement decision-curve/net-benefit tables only for declared threshold probabilities and false-negative/false-positive cost assumptions. Label them scenario analysis, not measured clinical utility.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_calibration_conformal.py tests/test_decision_analysis.py -q
git add src/calibration.py src/conformal.py src/decision_analysis.py tests/test_calibration_conformal.py tests/test_decision_analysis.py
git commit -m "feat: add reliability and safe deferral analysis"
```

## Task 9: Strengthen Fairness, Center Transfer, And Locked Explanations

**Files**

- Modify: `src/fairness.py`
- Modify: `src/explainability.py`
- Modify: `tests/test_trust_analysis.py`
- Modify: `src/research_evaluation.py`

- [ ] Add tests requiring subgroup rows to contain patient count, positive support, TP, FN, recall interval, and evidence status.

- [ ] Implement `insufficient_evidence` when subgroup support is below the configured threshold. Do not render unstable point estimates as reliable comparisons.

- [ ] Retain center ablation and implement leave-one-center-out evaluation using the same fold-local pipeline and locked metric schema.

- [ ] Quantify the difference between center-included and center-removed evidence without treating center as a causal explanation.

- [ ] Bind global and local explanations to:
  - the locked model hash;
  - transformed feature names from the fitted preprocessor;
  - the selected track;
  - a non-causality warning.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_trust_analysis.py tests/test_research_evaluation.py -q
git add src/fairness.py src/explainability.py src/research_evaluation.py tests/test_trust_analysis.py tests/test_research_evaluation.py
git commit -m "feat: strengthen transport and trust evidence"
```

## Task 10: Lock The Final Policy And Touch The Frozen Test Once

**Files**

- Modify: `src/notebook_workflow.py`
- Modify: `tests/test_notebook_workflow.py`
- Modify: `tests/test_pipeline_cohort_alignment.py`

- [ ] Write a state-machine test that rejects:
  - frozen-test evaluation before policy lock;
  - changes to features, model config, calibration, or thresholds after lock;
  - repeated frozen-test calls in one run;
  - final metrics without a lock manifest.

- [ ] Implement workflow phases:
  1. `prepare_training_pool`;
  2. `run_nested_validation`;
  3. `select_and_lock_policy`;
  4. `fit_locked_policy`;
  5. `evaluate_frozen_test_once`;
  6. `build_release`.

- [ ] Define final policy aggregation explicitly:
  - candidate selection from outer evidence with deterministic tie breaks;
  - thresholds re-estimated from training-pool out-of-fold probabilities for the locked candidate;
  - calibration refit using training-only cross-fitted evidence;
  - final pipeline fit on the complete training pool.

- [ ] Store a lock manifest before test evaluation containing feature-contract hash, split hash, selected config, threshold vector, calibration method, seeds, and source commit.

- [ ] Ensure no frozen-test value influences headline selection or notebook wording.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_notebook_workflow.py tests/test_pipeline_cohort_alignment.py -q
git add src/notebook_workflow.py tests/test_notebook_workflow.py tests/test_pipeline_cohort_alignment.py
git commit -m "feat: enforce one-shot frozen test policy"
```

## Task 11: Create The Canonical Scientific Release Bundle

**Files**

- Create: `src/release_bundle.py`
- Create: `schemas/scientific-release.schema.json`
- Create: `tests/test_release_bundle.py`
- Modify: `run_pipeline.py`
- Modify: `tests/test_public_bundle_privacy.py`

- [ ] Write failing schema and privacy tests requiring:
  - schema version, run ID, source commit, timestamp, and notebook identity;
  - dataset fingerprint, cohort counts, split counts, and partition labels;
  - locked models, thresholds, calibration, and hashes;
  - aggregate and per-label metrics with support and intervals;
  - EDA, leakage, ablation, reliability, prediction-set, fairness, center-transfer, and scenario evidence;
  - feature contract and deployable input schema;
  - safe claims, limitations, and deployment gates;
  - figure and model hashes;
  - no patient IDs, row-level targets, or raw assessment data.

- [ ] Implement a canonical JSON writer with deterministic key ordering and content hashes.

- [ ] Export joblib bundles containing the exact fitted preprocessor, per-label estimators, calibrators, thresholds, class order, feature-contract version, and run provenance.

- [ ] Reject release creation when:
  - source commit or split hash disagrees with the lock manifest;
  - required intervals or supports are absent;
  - a deployable track contains a research-only source;
  - figure/model hashes are missing;
  - cohort counts disagree across sections.

- [ ] Refactor `run_pipeline.py` to call the scientific workflow and release writer instead of maintaining an independent CSV truth path.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_release_bundle.py tests/test_public_bundle_privacy.py tests/test_export_web_data.py -q
git add src/release_bundle.py schemas/scientific-release.schema.json run_pipeline.py tests/test_release_bundle.py tests/test_public_bundle_privacy.py
git commit -m "feat: export canonical scientific release"
```

## Task 12: Rebuild The Judge-Facing Notebook

**Files**

- Modify: `scripts/build_final_notebook.py`
- Modify: `tests/test_final_notebook_structure.py`
- Modify: `tests/test_final_notebook_execution.py`

- [ ] Update structure tests to require this narrative order:
  1. executive research question and safe scope;
  2. data and target integrity;
  3. multi-label formulation;
  4. EDA and center heterogeneity;
  5. leakage and staged feature governance;
  6. fold-local preprocessing;
  7. baselines and ablations;
  8. repeated nested validation;
  9. locked frozen-test confirmation;
  10. calibration and prediction sets;
  11. selective prediction and decision utility;
  12. explanations, fairness, and center transfer;
  13. deployment gates, limitations, and conclusion;
  14. technical appendix.

- [ ] Keep the main path concise:
  - one principal chart or compact table per question;
  - no long raw DataFrame dumps;
  - no duplicated metric leaderboards;
  - detailed fold grids and diagnostics in the appendix.

- [ ] Add a scoring-map cell near the beginning showing where each FIT 20-point notebook criterion is satisfied.

- [ ] Require all result callouts to read values from workflow output or the release object. Ban manually typed headline metrics.

- [ ] Add explicit wording that the system supports differential-risk review and confirmatory testing; it does not diagnose or recommend treatment.

- [ ] Generate the notebook:

```powershell
python scripts/build_final_notebook.py
```

- [ ] Run focused tests:

```powershell
python -m pytest tests/test_final_notebook_structure.py tests/test_final_notebook_execution.py -q
```

- [ ] Commit:

```powershell
git add scripts/build_final_notebook.py tests/test_final_notebook_structure.py tests/test_final_notebook_execution.py notebooks/VECTRA_X_Final.ipynb
git commit -m "feat: rebuild scientific competition notebook"
```

## Task 13: Upgrade Notebook And Release Validation

**Files**

- Modify: `scripts/validate_final_notebook.py`
- Modify: `tests/test_final_notebook_structure.py`
- Modify: `tests/test_release_bundle.py`
- Modify: `tests/test_repository_cleanliness.py`

- [ ] Add validator tests for:
  - missing required sections;
  - stale execution counts;
  - error outputs;
  - hard-coded metric claims;
  - metric claims without partition/support/interval;
  - forbidden diagnosis or treatment wording;
  - figure hashes not present in the release;
  - notebook run ID differing from the release run ID;
  - stale source commit;
  - deployable evidence containing `FULL` or `RESEARCH_ONLY`.

- [ ] Implement a machine-readable validation report with `errors`, `warnings`, and `passed_checks`.

- [ ] Make validation exit non-zero on scientific or provenance errors.

- [ ] Update cleanliness rules to allow only intentional release manifests or documented generated artifacts. Do not commit caches, temporary notebooks, or unreferenced model files.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_final_notebook_structure.py tests/test_release_bundle.py tests/test_repository_cleanliness.py -q
git add scripts/validate_final_notebook.py tests/test_final_notebook_structure.py tests/test_release_bundle.py tests/test_repository_cleanliness.py
git commit -m "test: enforce notebook scientific release gates"
```

## Task 14: Execute, Review, And Lock The Notebook Milestone

**Files**

- Generated: `notebooks/VECTRA_X_Final.ipynb`
- Generated: `outputs/releases/<run_id>/**`
- Modify only if evidence requires correction: scientific source files above

- [ ] Run the complete test suite before the expensive notebook execution:

```powershell
python -m pytest -q
```

Expected: all tests pass.

- [ ] Execute the notebook from a clean kernel using the project execution command used by `tests/test_final_notebook_execution.py`.

- [ ] Run:

```powershell
python scripts/validate_final_notebook.py
python scripts/validate_web_bundle.py
```

At this milestone, `validate_web_bundle.py` may validate only that the scientific release exists and is not yet published to the web.

- [ ] Rerun the pipeline with the same config and compare:
  - split hashes;
  - selected policy;
  - thresholds;
  - model and figure hashes where determinism is expected;
  - metric differences within the documented floating-point tolerance.

- [ ] Perform a manual scientific review:
  - every claim is supported by the displayed evidence;
  - no rare-label weakness is hidden;
  - `PRE_LAB` and `LAB_AWARE` are never conflated;
  - exact and pragmatic prediction sets are not conflated;
  - high coverage is paired with efficiency;
  - center-transfer limitations remain prominent;
  - no causal language is used for associations or explanations.

- [ ] Record the final notebook run ID and release path in `outputs/releases/latest.json`.

- [ ] Commit only reviewed source changes and intentionally versioned competition artifacts:

```powershell
git status --short
git add notebooks/VECTRA_X_Final.ipynb outputs/releases/latest.json
git commit -m "release: lock scientific notebook evidence"
```

## Notebook Milestone Exit Criteria

- [ ] Fold-local preprocessing tests pass, including unseen categories.
- [ ] Nested-selection isolation tests pass.
- [ ] Repeated-validation metrics use the selected threshold policy.
- [ ] Frozen-test evaluation occurs exactly once after lock.
- [ ] Every headline metric includes support and uncertainty.
- [ ] Baselines and feature-family ablations are visible.
- [ ] Reliability, prediction-set efficiency, and abstention are reported together.
- [ ] Fairness and center-transfer evidence exposes insufficient support.
- [ ] The notebook executes cleanly from raw data.
- [ ] The canonical release validates against its schema and privacy gates.
- [ ] The notebook run ID, source commit, model bundle, figures, and release hashes agree.
- [ ] Only after all checks pass may the web synchronization plan begin.
