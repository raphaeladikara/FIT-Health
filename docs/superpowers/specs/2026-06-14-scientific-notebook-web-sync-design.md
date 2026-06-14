# VECTRA-X Scientific Notebook and Web Synchronization Design

## Purpose

Upgrade VECTRA-X in two sequential phases:

1. maximize the FIT preliminary-round notebook score through a rigorous,
   professional, and defensible scientific workflow; and
2. synchronize the web prototype with the locked notebook evidence while adding
   a safe live clinical decision-support demonstration.

The Technical Report is intentionally excluded. It will be designed only after
the notebook evidence and web narrative are stable.

## Strategic Direction

The project will use a scientific-first strategy. Methodological validity,
clarity, reproducibility, and safe real-world interpretation take precedence
over maximizing a single held-out metric. Model selection, headline values, and
conclusions may change when stricter validation produces different evidence.

The competitive position is built around four ideas:

- representation-aware leakage governance;
- clinically staged multi-label modeling;
- uncertainty-aware human review rather than forced diagnosis; and
- explicit deployment gates under rare-label and center-shift limitations.

## Phase 1: Canonical Scientific Notebook

### Scoring alignment

The notebook directly targets the three 20-point FIT criteria:

- **Visualization and understanding:** research-question-driven EDA, consistent
  figures, written findings, operational meaning, and limitations.
- **Appropriateness of preprocessing:** fold-local transformations, target and
  feature governance, leakage assertions, missingness rationale, and explicit
  preprocessing contracts.
- **Model performance and evaluation:** transparent baselines, nested repeated
  validation, locked frozen-test confirmation, support-aware metrics,
  uncertainty intervals, calibration, and robustness analysis.

### Evidence hierarchy

The notebook follows this order:

1. data and target integrity;
2. multi-label problem formulation;
3. EDA and data-quality findings;
4. leakage and clinical-stage governance;
5. fold-local preprocessing;
6. baselines and feature-family ablations;
7. nested repeated model and threshold selection;
8. locked frozen-test confirmation;
9. calibration, prediction sets, and selective prediction;
10. explainability, fairness, and center transfer;
11. decision-utility and scenario analysis;
12. deployment gates, limitations, and safe claims.

The frozen test is used only after preprocessing choices, model families,
hyperparameters, calibration strategy, and threshold policy are locked.

### Data integrity and EDA

The notebook will:

- validate shape, schema, duplicate rows, identifier integrity, target
  completeness, units, impossible values, and suspected outliers;
- justify the exclusion of unknown diagnosis targets;
- prove the multi-label framing using cardinality and co-occurrence;
- show label prevalence and positive support before presenting model metrics;
- analyze demographics, symptoms, vital signs, missingness, and center
  composition;
- compare missingness and label prevalence by center;
- distinguish descriptive association from predictive or causal evidence; and
- place a `Finding`, `Interpretation`, `Operational Meaning`, and `Limitation`
  block after every principal visualization.

### Feature governance and preprocessing

Features remain divided into:

- `PRE_LAB`: information plausibly available before confirmatory testing;
- `LAB_AWARE`: the pre-lab set plus ordered laboratory evidence; and
- `RESEARCH_ONLY`: diagnosis restatements or post-outcome information.

Every model representation is governed by its raw source. Categorical encoders,
imputers, scalers, missingness decisions, and other learned transformations are
fit inside training folds. The project will replace global factorization with a
fold-local encoder that handles unseen categories.

The notebook will publish a feature contract containing raw feature, derived
representation, availability stage, transformation, missingness behavior, and
leakage decision. Assertions will fail execution if a research-only source
reaches a deployable track.

### Validation protocol

The primary estimate will use repeated nested multi-label-stratified
cross-validation on the training pool:

- inner folds select model configuration and label-specific thresholds;
- outer folds estimate the complete selected policy;
- all reported outer-fold predictions come from decisions that did not observe
  those rows; and
- deterministic seeds and split-support tables are recorded.

Model breadth will remain modest and rational. Candidate families should include
regularized logistic regression and carefully constrained tree ensembles.
Optional boosting engines may be included only when reproducible and materially
useful. Label-specific configurations are allowed when selected exclusively
inside training data.

The notebook will not imply that a broad model zoo is scientific novelty.
Selection complexity must be justified against the 299-patient cohort.

### Metrics and statistical reporting

Primary metrics:

- macro PR-AUC;
- macro F1;
- macro recall; and
- per-label recall, F1, and PR-AUC.

Secondary metrics:

- micro F1;
- Hamming loss;
- sample Jaccard;
- subset accuracy; and
- ROC-AUC with prevalence context.

All headline results must report partition, patient count, positive support, and
an uncertainty interval. Aggregate metric intervals and paired track
comparisons are required. The repeated-validation tables must evaluate the same
threshold policy used by the final model, rather than using an unrelated fixed
0.5 threshold.

### Baselines and ablations

Required baselines:

- always-malaria;
- prevalence-based;
- prevalence-matched random;
- regularized logistic regression; and
- a simple clinically interpretable reference when defensible.

Required ablations:

- demographics only;
- demographics plus symptoms;
- addition of vital signs;
- addition of laboratory variables;
- center removed;
- missingness indicators removed; and
- each suspicious or research-only source excluded from deployable evidence.

The discussion emphasizes marginal evidence and uncertainty, not only rank.

### Reliability and safe decision science

The notebook will report:

- raw and calibrated Brier score and ECE;
- reliability plots with bin counts and positive support;
- exact and pragmatic prediction-set policies as distinct methods;
- per-label coverage, micro and macro coverage, set-size distribution,
  singleton rate, ambiguity, and false-negative risk;
- risk-coverage and abstention curves;
- decision-curve or net-benefit analysis where the assumptions can be stated
  precisely; and
- sensitivity to false-negative cost, review capacity, and threshold policy.

High prediction-set coverage must never be presented without efficiency. A
nearly full five-label set is described as safe but uninformative.

### Robustness, explainability, and deployment gates

Explainability will target the actual locked model. Attribution is described as
model behavior, not medical causation.

Fairness and robustness reporting includes subgroup patient count, positive
support, TP, FN, recall interval, and an insufficient-evidence state. Center
ablation and leave-one-center-out validation remain the principal transport
warning.

The conclusion includes an explicit deployment gate table:

- evidence currently supported;
- conditions requiring clinician review;
- out-of-distribution or incomplete-input rejection;
- labels for which performance is insufficient;
- monitoring and recalibration requirements; and
- conditions that prohibit autonomous use.

### Notebook presentation

The main narrative will be concise and judge-readable. Dense grids and extended
diagnostics move to an appendix. Visuals use stable label colors, readable
captions, partition labels, and accessible contrast. Long raw DataFrame dumps
are prohibited.

The notebook is built deterministically from a reviewed builder, executed from
raw data in a clean kernel, and validated for stale cells, errors, unsupported
claims, and artifact consistency.

## Phase 2: Synchronized Web Prototype

### Role

The web application is a presentation and demonstration layer. It never becomes
an independent source of scientific truth. Every evidence claim must originate
from the locked notebook run.

The existing visual system, landing page, routing, charts, responsive behavior,
and scenario components should be preserved where they remain useful. This is a
targeted architectural extension, not a full rewrite.

### Canonical artifact contract

The notebook pipeline exports one versioned release bundle containing:

- run ID, source commit, generated timestamp, schema version, and scientific
  notebook identity;
- cohort, split, and partition metadata;
- selected models and configuration summaries;
- threshold and calibration policy;
- aggregate and per-label metrics with support and intervals;
- EDA, leakage, robustness, fairness, uncertainty, and scenario evidence;
- deployable feature contract and input schema;
- safe claims and deployment gates; and
- hashes or run identifiers for generated figures and model bundles.

The web exporter must consume only this release bundle. Historical CSV files,
figures, thresholds, resource summaries, or manifests are forbidden as public
inputs.

Export fails when:

- source commit or run ID is stale;
- cohort or partition counts disagree;
- thresholds differ from the locked notebook;
- a public figure belongs to another run;
- target-restating `FULL` evidence enters the public product;
- required support or uncertainty fields are absent; or
- patient identifiers or ground truth are exposed.

### Information architecture

The revised web experience contains:

1. Executive Evidence;
2. Data and Leakage Governance;
3. Model Evaluation;
4. Uncertainty and Safe Deferral;
5. Fairness and Center Transfer;
6. Live Assessment;
7. Scenario Prototype; and
8. Limitations and Deployment Gates.

Each page communicates one principal scientific message and uses the terminology
locked by the notebook.

### Live Assessment

The feature is called **Live Clinical Decision-Support Assessment**, never live
diagnosis.

The assessment supports:

- `PRE_LAB` as the primary mode;
- optional `LAB_AWARE` comparison after laboratory inputs exist;
- example cases that populate the form for a rapid judge demonstration;
- schema-driven validation;
- missing-input warnings;
- observed-range and out-of-distribution warnings;
- calibrated risk estimates;
- label-specific decision thresholds;
- uncertainty and prediction-set output;
- mandatory abstention or human review when evidence is insufficient;
- model explanation with a non-causality warning; and
- model version, run ID, scope, and evidence limitations.

User-facing language must say elevated or reduced modeled risk, not confirmed
disease. The output recommends review or confirmatory testing, never treatment.

### Inference architecture

The preferred design is a static frontend plus a server-side inference API:

```text
Locked notebook run
  -> canonical evidence bundle
  -> deployable preprocessing/model/calibration bundle

Dashboard frontend
  -> evidence bundle for analytical views
  -> validated assessment request
  -> inference API
  -> risk, uncertainty, explanation, abstention, and provenance response
```

The inference API loads the exact locked preprocessing and model bundle. It does
not retrain. It validates the release manifest against the model bundle at
startup and rejects incompatible requests.

No submitted assessment data is persisted. Logs exclude raw health inputs and
identifiers. The endpoint receives rate limiting, request-size limits,
structured validation, timeouts, and generic error responses.

### Partition and scope clarity

Every web result identifies its scope:

- training-only validation;
- frozen-test evidence;
- anonymous illustrative case; or
- full-cohort scenario projection.

The interface must not combine a frozen-test metric with full-cohort triage
counts without visibly distinguishing the partitions. Resource projections are
assumption-bound and are not presented as measured clinical impact.

## Testing and Verification

### Notebook gates

- unit tests for fold-local categorical handling;
- tests proving nested selection isolation;
- tests for threshold-policy consistency;
- tests for aggregate and per-label intervals;
- leakage and feature-contract regression tests;
- clean full notebook execution;
- canonical artifact schema validation; and
- deterministic rerun comparison within documented numerical tolerance.

### Web gates

- canonical bundle contract tests;
- stale-run and mixed-artifact rejection tests;
- privacy and research-only evidence tests;
- inference request/response schema tests;
- preprocessing parity tests between notebook and API;
- missing, extreme, and unseen-category input tests;
- abstention and out-of-distribution behavior tests;
- unit and syntax tests on Windows;
- local browser smoke tests for every principal page; and
- accessibility and responsive checks for the live assessment flow.

## Delivery Sequence

### Notebook milestone

The notebook phase is complete only when the stricter workflow has been executed,
the final model and thresholds are locked, all canonical artifacts are generated
from that run, and the notebook satisfies the scoring and scientific gates.

No web scientific values are updated before this milestone.

### Web synchronization milestone

The evidence pages are synchronized first. The live assessment is enabled only
after preprocessing parity and model-bundle provenance tests pass.

## Acceptance Criteria

- The notebook is the sole scientific source of truth.
- All learned preprocessing is fold-local.
- Repeated nested validation estimates the full model-and-threshold policy.
- The frozen test is used only after decisions are locked.
- All headline evidence includes support and uncertainty.
- Rare-label and center-transfer weaknesses remain visible.
- The web bundle contains no historical or mixed-run evidence.
- The live assessment runs the locked model and can safely abstain.
- No patient input is stored or exposed.
- The dashboard never claims diagnosis, treatment, or validated clinical impact.
- Technical Report work remains outside this scope.
