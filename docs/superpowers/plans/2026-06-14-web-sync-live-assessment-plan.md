# VECTRA-X Web Synchronization And Live Assessment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize the existing dashboard with the locked scientific notebook release and add a safe, provenance-verified Live Clinical Decision-Support Assessment that improves judge impact without overstating clinical readiness.

**Architecture:** The web remains a mostly static presentation layer. A strict exporter converts one validated notebook release into public JSON, figures, and a deployable model bundle. A lightweight Python inference API loads that exact bundle, while the frontend renders evidence and submits schema-validated anonymous assessments without persisting health inputs.

**Tech Stack:** HTML, CSS, vanilla JavaScript ES modules, Node.js test runner, Playwright, Python standard-library HTTP server for local integration, NumPy, pandas, scikit-learn, joblib, pytest, JSON Schema, Vercel Python Functions.

---

## Dependency Gate

Do not start implementation until every exit criterion in
`docs/superpowers/plans/2026-06-14-scientific-notebook-upgrade-plan.md`
passes and `outputs/releases/latest.json` points to a validated locked run.

Before Task 1, record:

- notebook run ID;
- scientific release schema version;
- source commit;
- feature-contract hash;
- model-bundle hash;
- frozen-test split hash;
- `PRE_LAB` and `LAB_AWARE` policy IDs.

If any value is absent or inconsistent, stop the web phase and repair the
notebook release. Never compensate by manually editing public JSON.

## Scope And Product Rules

- Preserve the current visual identity, landing page, routing, responsive system, and useful chart components.
- This is a targeted information-architecture and inference extension, not a full rewrite.
- The feature name is **Live Clinical Decision-Support Assessment**, never live diagnosis.
- `PRE_LAB` is the default assessment mode. `LAB_AWARE` appears only after laboratory inputs are intentionally enabled.
- The interface may show modeled risk, uncertainty, prediction sets, and review recommendations.
- It may not claim confirmed disease, treatment recommendations, measured clinical impact, or production readiness.
- Assessment requests contain no names, identifiers, contact data, free-text notes, or persistent storage.
- Frozen-test evidence, training validation, illustrative cases, and full-cohort scenario projections must remain visibly distinct.

## Target File Map

**Modify**

- `export_web_data.py`: consume one canonical scientific release only.
- `scripts/validate_web_bundle.py`: enforce provenance, privacy, and model parity gates.
- `web/index.html`: update the executive story and navigation.
- `web/dashboard.html`: host the revised evidence information architecture.
- `web/demo.html`: retain scenario simulation but clarify its assumption-bound scope.
- `web/assets/dashboard.js`: render only release-backed evidence.
- `web/assets/data-client.js`: load and validate versioned public contracts.
- `web/assets/components.js`: add provenance, evidence-status, and safety components.
- `web/assets/router.js`: add stable routes for the new scientific sections.
- `web/assets/base.css`
- `web/assets/dashboard.css`
- `web/assets/responsive.css`
- `web/assets/demo.js`
- `web/assets/resource-simulator.js`
- `web/package.json`: make Windows-compatible syntax checks and add live integration commands.
- `web/vercel.json`: add API headers, cache rules, and request-routing constraints.
- `web/README.md`: document release synchronization and safe demo operation.
- `tests/test_export_web_data.py`
- `tests/test_public_bundle_privacy.py`
- `web/tests/smoke.spec.mjs`

**Create**

- `web/assessment.html`
- `web/assets/assessment.js`
- `web/assets/assessment.css`
- `web/assets/evidence-views.js`
- `web/assets/schema-form.js`
- `web/assets/provenance.js`
- `web/api/assess.py`
- `web/api/inference.py`
- `web/api/validation.py`
- `web/api/__init__.py`
- `web/serve_live.py`
- `web/requirements.txt`
- `web/tools/check-js.mjs`
- `web/data/schemas/evidence.schema.json`
- `web/data/schemas/input-schema.schema.json`
- `web/data/schemas/assessment-response.schema.json`
- `web/tests/assessment.test.js`
- `web/tests/data-client.test.js`
- `tests/test_web_inference.py`
- `tests/test_web_model_parity.py`

**Generated, never manually edited**

- `web/data/manifest.json`
- `web/data/evidence.json`
- `web/data/input-schema.json`
- `web/data/demo-cases.json`
- `web/model/pre_lab.joblib`
- `web/model/lab_aware.joblib`
- `web/model/model-manifest.json`
- `web/figures/*`

## Task 1: Replace Mixed Historical Inputs With One Release Source

**Files**

- Modify: `export_web_data.py`
- Modify: `tests/test_export_web_data.py`
- Modify: `tests/test_public_bundle_privacy.py`

- [ ] Write failing tests that create a temporary scientific release and require the exporter to read only:
  - `outputs/releases/latest.json`;
  - the referenced `scientific-release.json`;
  - artifacts whose hashes are listed in that release.

- [ ] Add negative tests for:
  - stale legacy CSVs with conflicting values;
  - a figure from another run;
  - thresholds differing from the locked model;
  - hard-coded train or test counts;
  - source commit mismatch;
  - `FULL` or `RESEARCH_ONLY` evidence in a public deployable section.

- [ ] Run:

```powershell
python -m pytest tests/test_export_web_data.py tests/test_public_bundle_privacy.py -q
```

Expected: failure because the current exporter mixes final and historical tables.

- [ ] Refactor the exporter into:
  - `load_locked_release`;
  - `verify_release_provenance`;
  - `build_public_evidence`;
  - `build_public_input_schema`;
  - `copy_verified_models`;
  - `copy_verified_figures`;
  - `write_public_manifest`.

- [ ] Remove fallback reads from historical CSVs and stale `web/figures`.

- [ ] Derive every partition count, threshold, metric, scenario value, and claim from the release object.

- [ ] Copy artifacts by verified hash. Delete generated public artifacts not referenced by the current manifest.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_export_web_data.py tests/test_public_bundle_privacy.py -q
git add export_web_data.py tests/test_export_web_data.py tests/test_public_bundle_privacy.py
git commit -m "fix: make web export release only"
```

## Task 2: Define Versioned Public Data Contracts

**Files**

- Create: `web/data/schemas/evidence.schema.json`
- Create: `web/data/schemas/input-schema.schema.json`
- Create: `web/data/schemas/assessment-response.schema.json`
- Modify: `web/data/schemas/manifest.schema.json`
- Modify: `web/data/schemas/demo-cases.schema.json`
- Create: `web/tests/data-client.test.js`
- Modify: `web/assets/data-client.js`

- [ ] Define `manifest.json` fields:
  - public schema version;
  - notebook run ID and scientific schema version;
  - source commit and generated timestamp;
  - evidence, input-schema, demo-case, figure, and model hashes;
  - policy IDs and class order;
  - safe-scope statement.

- [ ] Define `evidence.json` sections:
  - executive summary;
  - cohort and partitions;
  - data quality and leakage;
  - validation and frozen-test metrics;
  - per-label support and intervals;
  - baselines and ablations;
  - calibration and prediction sets;
  - risk-coverage and decision scenarios;
  - fairness and center transfer;
  - limitations and deployment gates.

- [ ] Define `input-schema.json` without patient-derived values. Each field must contain display label, type, stage, unit, required state, allowed values or hard bounds, soft warning bounds, missingness behavior, and clinical help text.

- [ ] Define the assessment response contract with:
  - provenance;
  - selected mode;
  - calibrated probabilities;
  - label thresholds and decisions;
  - prediction set;
  - uncertainty;
  - abstention status and reasons;
  - triage category;
  - explanation;
  - warnings;
  - safe scope.

- [ ] Write frontend tests for schema-version rejection, missing required fields, and hash mismatch.

- [ ] Implement `loadWebBundle()` to load the manifest first, reject unsupported versions, then load referenced documents.

- [ ] Run and commit:

```powershell
npm --prefix web test
git add web/data/schemas web/assets/data-client.js web/tests/data-client.test.js
git commit -m "feat: define public evidence contracts"
```

## Task 3: Reframe The Dashboard Information Architecture

**Files**

- Modify: `web/index.html`
- Modify: `web/dashboard.html`
- Modify: `web/assets/router.js`
- Create: `web/assets/evidence-views.js`
- Modify: `web/assets/dashboard.js`
- Modify: `web/assets/components.js`
- Modify: `web/assets/dashboard.css`
- Modify: `web/assets/responsive.css`
- Modify: `web/tests/router.test.js`
- Modify: `web/tests/smoke.spec.mjs`

- [ ] Add route tests for:
  - Executive Evidence;
  - Data and Leakage Governance;
  - Model Evaluation;
  - Uncertainty and Safe Deferral;
  - Fairness and Center Transfer;
  - Live Assessment;
  - Scenario Prototype;
  - Limitations and Deployment Gates.

- [ ] Preserve existing reusable cards, charts, tables, label colors, and responsive breakpoints.

- [ ] Move scientific rendering into `evidence-views.js`, leaving `dashboard.js` responsible for orchestration and route state.

- [ ] Add reusable components:
  - `EvidenceScopeBadge`;
  - `ProvenanceStrip`;
  - `SupportStatus`;
  - `IntervalMetric`;
  - `DeploymentGate`;
  - `ScientificCaveat`.

- [ ] Make partition scope visible beside every result:
  - training-only nested validation;
  - frozen test;
  - illustrative case;
  - full-cohort scenario projection.

- [ ] Remove or replace visuals whose hashes are absent from the locked release.

- [ ] Keep one principal message per route and move dense diagnostics into expandable detail panels.

- [ ] Run:

```powershell
npm --prefix web test
npm --prefix web run check
```

- [ ] Commit:

```powershell
git add web/index.html web/dashboard.html web/assets/router.js web/assets/evidence-views.js web/assets/dashboard.js web/assets/components.js web/assets/dashboard.css web/assets/responsive.css web/tests/router.test.js web/tests/smoke.spec.mjs
git commit -m "feat: align dashboard with scientific evidence"
```

## Task 4: Build The Locked Inference Service

**Files**

- Create: `web/api/__init__.py`
- Create: `web/api/inference.py`
- Create: `tests/test_web_inference.py`
- Create: `tests/test_web_model_parity.py`
- Modify: `web/requirements.txt`

- [ ] Write tests that load an exported model bundle and verify:
  - manifest hash matches the joblib file;
  - feature-contract version and class order match;
  - the requested mode has a locked policy;
  - preprocessing accepts raw schema-shaped inputs;
  - unseen categories are handled;
  - returned probabilities are finite and ordered by the canonical label list;
  - thresholds and calibrators come from the bundle, not API defaults.

- [ ] Add parity fixtures generated by the notebook release. For each fixture, compare direct locked-pipeline output with API service output using a strict documented tolerance.

- [ ] Implement `LockedInferenceService`:
  - load manifest and model bundles once;
  - verify hashes and versions during initialization;
  - accept only `PRE_LAB` and released `LAB_AWARE`;
  - construct a one-row DataFrame from canonical field names;
  - run the exact preprocessor, estimators, and calibrators;
  - apply locked thresholds;
  - compute the released prediction-set and uncertainty policy;
  - return only JSON-serializable values.

- [ ] Do not reimplement preprocessing in API code. The joblib bundle must contain the exact fitted pipeline.

- [ ] Pin minimal inference dependencies in `web/requirements.txt`. Exclude notebook-only libraries such as plotting and SHAP unless the exported model genuinely requires them.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_web_inference.py tests/test_web_model_parity.py -q
git add web/api/__init__.py web/api/inference.py web/requirements.txt tests/test_web_inference.py tests/test_web_model_parity.py
git commit -m "feat: load locked web inference bundle"
```

## Task 5: Add Input Validation, OOD Warnings, And Mandatory Abstention

**Files**

- Create: `web/api/validation.py`
- Modify: `web/api/inference.py`
- Modify: `tests/test_web_inference.py`
- Create: `web/api/assess.py`
- Modify: `web/vercel.json`

- [ ] Write tests for:
  - unsupported content type;
  - oversized request;
  - identifiers or unknown keys;
  - missing required fields;
  - impossible hard-range values;
  - soft observed-range warnings;
  - unseen categories;
  - too many missing fields;
  - high uncertainty;
  - nearly uninformative prediction set;
  - model-manifest mismatch;
  - generic error output with no raw health values.

- [ ] Implement structured validation from `input-schema.json`:
  - reject hard-invalid values with field-level messages;
  - accept soft out-of-distribution values but force a warning or abstention;
  - reject free text and identifiers;
  - ignore no unknown keys silently.

- [ ] Implement released abstention rules. Reasons must be machine-readable, for example:
  - `INSUFFICIENT_INPUT`;
  - `OUT_OF_DISTRIBUTION`;
  - `HIGH_UNCERTAINTY`;
  - `UNINFORMATIVE_SET`;
  - `UNSUPPORTED_MODE`;
  - `MODEL_VERSION_MISMATCH`.

- [ ] Implement `POST /api/assess` in `web/api/assess.py`:
  - accept JSON only;
  - enforce request size and timeout-friendly execution;
  - return `400` for invalid input, `409` for incompatible model versions, and generic `500` errors;
  - never log request bodies;
  - set `Cache-Control: no-store`.

- [ ] Add security headers for `/api/*` and document that platform rate limiting must be enabled before public deployment. Treat absent platform rate limiting as a deployment-gate failure, not as an in-process promise.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_web_inference.py tests/test_web_model_parity.py -q
git add web/api/validation.py web/api/inference.py web/api/assess.py web/vercel.json tests/test_web_inference.py
git commit -m "feat: validate and safely abstain on assessments"
```

## Task 6: Build The Schema-Driven Live Assessment UI

**Files**

- Create: `web/assessment.html`
- Create: `web/assets/assessment.js`
- Create: `web/assets/assessment.css`
- Create: `web/assets/schema-form.js`
- Create: `web/assets/provenance.js`
- Create: `web/tests/assessment.test.js`
- Modify: `web/assets/components.js`
- Modify: `web/assets/responsive.css`

- [ ] Write JavaScript unit tests for:
  - rendering fields from `input-schema.json`;
  - conditional display of laboratory fields;
  - required and numeric validation;
  - unit and range help;
  - request serialization with no unknown keys;
  - result rendering for normal, warning, and abstention responses;
  - clearing all entered values.

- [ ] Build a progressive form:
  1. choose `PRE_LAB` or intentionally enable `LAB_AWARE`;
  2. enter demographics and center context;
  3. enter symptoms and vital signs;
  4. optionally enter laboratory evidence;
  5. review missing and range warnings;
  6. submit assessment.

- [ ] Render results in this order:
  - prominent scope and non-diagnosis notice;
  - abstention or review state;
  - calibrated risk estimates with label-specific thresholds;
  - prediction set and uncertainty;
  - reasons for mandatory review;
  - model-behavior explanation with non-causality warning;
  - run ID, policy ID, and release timestamp.

- [ ] Use language such as “elevated modeled risk” and “requires clinical review or confirmatory testing”. Ban “positive diagnosis”, “confirmed”, “treat”, and “safe to discharge”.

- [ ] Add an immediate “Clear assessment” control that removes values and rendered results from the DOM.

- [ ] Make keyboard order, labels, error messages, focus states, and result announcements accessible.

- [ ] Run and commit:

```powershell
npm --prefix web test
npm --prefix web run check
git add web/assessment.html web/assets/assessment.js web/assets/assessment.css web/assets/schema-form.js web/assets/provenance.js web/assets/components.js web/assets/responsive.css web/tests/assessment.test.js
git commit -m "feat: add live decision support assessment"
```

## Task 7: Add Safe Demonstration Cases

**Files**

- Modify: `export_web_data.py`
- Modify: `web/data/schemas/demo-cases.schema.json`
- Modify: `web/assets/assessment.js`
- Modify: `web/assets/demo.js`
- Modify: `tests/test_export_web_data.py`
- Modify: `web/tests/assessment.test.js`

- [ ] Define three to five anonymous synthetic cases covering:
  - a straightforward low-uncertainty example;
  - a multi-label ambiguous example;
  - substantial missingness that triggers review;
  - an out-of-distribution value;
  - optional `LAB_AWARE` comparison.

- [ ] Generate cases from explicit synthetic values, never copied patient rows.

- [ ] Mark cases as `illustrative_synthetic` in both data and interface.

- [ ] Add one-click case loading and preserve the ability to edit values before submission.

- [ ] Ensure expected outputs are not hard-coded in the frontend. Cases must call the same API as manual input.

- [ ] Update the existing scenario demo to distinguish population-level assumption testing from individual assessment.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_export_web_data.py tests/test_public_bundle_privacy.py -q
npm --prefix web test
git add export_web_data.py web/data/schemas/demo-cases.schema.json web/assets/assessment.js web/assets/demo.js tests/test_export_web_data.py web/tests/assessment.test.js
git commit -m "feat: add synthetic judge demo cases"
```

## Task 8: Synchronize Scenario And Resource Narratives

**Files**

- Modify: `web/demo.html`
- Modify: `web/assets/demo.js`
- Modify: `web/assets/resource-simulator.js`
- Modify: `web/tests/resource-simulator.test.js`
- Modify: `web/assets/evidence-views.js`

- [ ] Add tests proving scenario calculations use released policy inputs and display assumption metadata.

- [ ] Remove any resource value that is neither released by the notebook nor calculated transparently from user-adjustable assumptions.

- [ ] Label outputs as:
  - projected review volume;
  - projected confirmatory-test demand;
  - scenario sensitivity;
  - not observed patient outcomes or clinical savings.

- [ ] Visibly separate full-cohort scenario counts from frozen-test performance metrics.

- [ ] Link the scenario page back to the risk-coverage and threshold evidence explaining the trade-off.

- [ ] Run and commit:

```powershell
npm --prefix web test
git add web/demo.html web/assets/demo.js web/assets/resource-simulator.js web/assets/evidence-views.js web/tests/resource-simulator.test.js
git commit -m "fix: align scenario claims with released evidence"
```

## Task 9: Add Local Full-Stack Demo Support

**Files**

- Create: `web/serve_live.py`
- Modify: `web/README.md`
- Modify: `web/package.json`
- Create: `web/tools/check-js.mjs`

- [ ] Implement `web/serve_live.py` with the Python standard library:
  - serve static files from `web`;
  - route `POST /api/assess` through the same API handler/service;
  - disable directory listing;
  - set no-store for assessment responses;
  - print only method, path, status, and duration;
  - never print request bodies.

- [ ] Replace the Windows-fragile wildcard syntax check with `web/tools/check-js.mjs`, which enumerates JavaScript files and invokes `node --check` for each.

- [ ] Add package commands:
  - `npm run check`;
  - `npm run test`;
  - `npm run test:browser`;
  - `npm run serve:live`.

- [ ] Document exact local judge-demo commands and the expected run ID shown in the interface.

- [ ] Run:

```powershell
npm --prefix web run check
npm --prefix web test
python web/serve_live.py --help
```

- [ ] Commit:

```powershell
git add web/serve_live.py web/README.md web/package.json web/tools/check-js.mjs
git commit -m "chore: add portable live demo tooling"
```

## Task 10: Enforce Bundle Provenance, Privacy, And Security Gates

**Files**

- Modify: `scripts/validate_web_bundle.py`
- Modify: `tests/test_public_bundle_privacy.py`
- Modify: `tests/test_web_model_parity.py`
- Modify: `web/vercel.json`
- Modify: `web/README.md`

- [ ] Add validation failures for:
  - mismatched run, source commit, schema, policy, model, or figure hashes;
  - public row-level targets or identifiers;
  - demo cases that match source patient rows;
  - missing support or intervals;
  - research-only features;
  - diagnosis or treatment claims;
  - API caching;
  - unsupported model dependency;
  - missing production rate-limit declaration.

- [ ] Validate Content Security Policy and security headers without enabling inline script execution.

- [ ] Add `robots` and cache behavior appropriate for a competition prototype and sensitive-looking forms.

- [ ] Document:
  - no persistence;
  - no raw-input logging;
  - anonymous synthetic demo cases;
  - request-size constraints;
  - platform rate-limit requirement;
  - deployment gates that prohibit clinical use.

- [ ] Run and commit:

```powershell
python -m pytest tests/test_public_bundle_privacy.py tests/test_web_model_parity.py -q
python scripts/validate_web_bundle.py
git add scripts/validate_web_bundle.py tests/test_public_bundle_privacy.py tests/test_web_model_parity.py web/vercel.json web/README.md
git commit -m "test: enforce web provenance and privacy gates"
```

## Task 11: Run Browser, Accessibility, And Responsive Verification

**Files**

- Modify: `web/tests/smoke.spec.mjs`
- Modify as findings require: `web/assets/*.css`, `web/assets/*.js`, `web/*.html`

- [ ] Extend browser smoke coverage to:
  - load every principal route;
  - verify no console errors or failed asset requests;
  - confirm the run ID is visible;
  - load each synthetic case;
  - submit one normal, one abstention, and one invalid request;
  - switch between `PRE_LAB` and `LAB_AWARE`;
  - clear assessment data;
  - verify scenario and frozen-test scope labels.

- [ ] Verify desktop, tablet, and mobile widths.

- [ ] Check keyboard-only flow, visible focus, labels, error association, contrast, reduced-motion behavior, and live result announcements.

- [ ] Start the local integration server:

```powershell
python web/serve_live.py --port 4173
```

- [ ] In another terminal, run:

```powershell
npm --prefix web run test:browser
```

- [ ] Capture reviewed competition screenshots only after all provenance and parity tests pass.

- [ ] Commit fixes and smoke coverage:

```powershell
git add web/tests/smoke.spec.mjs web
git commit -m "test: verify live assessment experience"
```

## Task 12: Build And Validate The Final Web Release

**Files**

- Generated: `web/data/**`
- Generated: `web/model/**`
- Generated: `web/figures/**`
- Modify only if validation finds a defect: source files above

- [ ] Generate the public bundle from the locked notebook release:

```powershell
python export_web_data.py
```

- [ ] Run all Python and web gates:

```powershell
python -m pytest -q
python scripts/validate_final_notebook.py
python scripts/validate_web_bundle.py
npm --prefix web run check
npm --prefix web test
npm --prefix web run test:browser
```

- [ ] Compare one parity fixture manually:
  - direct notebook bundle probabilities;
  - API probabilities;
  - thresholds;
  - decisions;
  - uncertainty;
  - abstention reason.

- [ ] Review every public claim against `scientific-release.json`.

- [ ] Verify that deleting legacy CSVs or figures does not change the rebuilt website.

- [ ] Verify no submitted assessment survives refresh, clear, server logs, or browser storage.

- [ ] Commit the synchronized public artifacts:

```powershell
git status --short
git add web/data web/model web/figures
git commit -m "release: synchronize web with locked evidence"
```

## Web Milestone Exit Criteria

- [ ] The public bundle is generated only from the locked notebook release.
- [ ] Run ID, source commit, policy IDs, model hashes, figures, counts, thresholds, and metrics agree.
- [ ] Historical CSVs and stale figures cannot influence the build.
- [ ] Every scientific result shows its partition and evidence scope.
- [ ] Live assessment uses the exact locked preprocessing, calibration, thresholds, and class order.
- [ ] Model parity tests pass within the documented tolerance.
- [ ] Missing, extreme, unseen-category, and high-uncertainty inputs behave safely.
- [ ] Mandatory abstention is visible and understandable.
- [ ] No identifiers, free text, raw health logs, or persistent inputs exist.
- [ ] Scenario projections are explicitly assumption-bound.
- [ ] The interface never claims diagnosis, treatment, or validated clinical impact.
- [ ] Syntax, unit, integration, browser, accessibility, and responsive checks pass.
- [ ] Production deployment remains blocked until platform rate limiting and final release validation are confirmed.
