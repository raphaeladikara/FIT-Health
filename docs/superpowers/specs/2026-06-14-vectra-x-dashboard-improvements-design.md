# VECTRA-X Dashboard Improvements Design

**Date:** 14 June 2026  
**Status:** Approved design direction  
**Register:** Product  
**Primary surface:** Static-first Next.js application backed by privacy-safe pipeline exports

## 1. Objective

Upgrade VECTRA-X from a polished analytical viewer into a complete competition
prototype that:

1. explains the project clearly to a first-time visitor;
2. supports a structured three-to-seven-minute judge demonstration;
3. preserves a fast operational workspace for repeated exploration;
4. communicates scientific evidence, provenance, uncertainty, and limitations
   without overstating clinical readiness; and
5. implements every dashboard capability claimed in the final presentation.

The experience will use a hybrid architecture: a concise public landing page, a
guided demo, and a separate operational application shell.

## 2. Users And Success Criteria

### Competition judge

Needs to understand the problem, methodological contribution, evidence, operational
value, and limitations without opening the notebook.

Success:

- can explain VECTRA-X accurately after one minute on the landing page;
- can complete the guided demonstration without choosing an arbitrary navigation path;
- can verify the source, run type, and uncertainty of every headline claim; and
- does not encounter a feature promised by the pitch that is absent from the prototype.

### Frontline health-workflow reviewer

Needs to inspect anonymous cases, distinguish risk from diagnosis, identify
uncertainty, and understand the recommended human action.

Success:

- can follow patient risk to human action without translating unexplained ML terms;
- can distinguish urgent, confirmatory, review, and routine states;
- can see why the system is uncertain; and
- never mistakes the interface for a diagnostic authority.

### Humanitarian response coordinator

Needs to explore resource shortages and compare transparent allocation scenarios.

Success:

- can adjust or enter capacity values;
- can distinguish allocated, waitlisted, and ineligible cases;
- can compare operational and safety-first policies; and
- can see all assumptions used by the simulator.

## 3. Experience Architecture

### Public layer

- `/`: landing page and product briefing.
- `/demo`: guided judge demonstration.
- `/methodology`: accessible methodology, limitations, glossary, and provenance.

The public layer uses a lightweight top navigation and does not show the dense
operational sidebar.

### Operational application

- `/command-center`: cohort status and prioritized human actions.
- `/patients`: patient review.
- `/intake`: batch intake and saved-model inference.
- `/resources`: resource scenarios and policy comparison.
- `/evidence`: trust center.

These routes use the existing application shell, renamed navigation, case search,
artifact-status access, and responsive mobile navigation.

### Compatibility

The existing root command center route will move to `/command-center`. Internal links,
tests, README instructions, and static export behavior must be updated together.

## 4. Landing Page

The landing page is required. It is a short product briefing, not a long marketing
site. Its job is to reduce cognitive load before a first-time visitor enters a dense
clinical analytics workspace.

### Page structure

1. **Hero**
   - Humanitarian problem in one sentence.
   - Product definition in one sentence.
   - Primary CTA: `Start guided demo`.
   - Secondary CTA: `Open command center`.
   - Persistent stage label: `Competition prototype, not clinically validated`.

2. **Operational flow**
   - Pre-lab intake.
   - Multi-label risk estimation.
   - Uncertainty and caution set.
   - Human triage action.
   - Resource consequence.

3. **Why VECTRA-X**
   - Multi-label by design.
   - Leakage-aware feature staging.
   - Calibrated uncertainty and abstention.
   - Translation into transparent operational priorities.

4. **Evidence snapshot**
   - Patient count and multi-label count.
   - PRE_LAB macro F1 with bootstrap interval.
   - Co-infection ROC-AUC.
   - Center-transfer limitation.
   - Every value includes provenance and run identity.

5. **Choose a path**
   - Guided demonstration.
   - Patient review.
   - Resource scenario.
   - Trust center.

6. **Limitations**
   - Small two-center cohort.
   - Rare-label uncertainty.
   - Weak cross-center transfer.
   - No prospective clinical validation or regulatory review.

### Visual direction

Use a restrained clinical-operations palette with one committed blue accent.
The physical scene is a judge or response coordinator reviewing a high-stakes
prototype on a laptop in a bright presentation or operations room. The interface must
feel calm, legible, and prepared, not dramatic or consumer-medical.

Reference qualities:

- Stripe documentation for concise explanation and evidence;
- Linear for hierarchy and navigation discipline;
- WHO operational reports for responsible, non-promotional clinical language.

The landing page may use larger typography and broader composition than the app, but
it must share the same tokens and semantic colors.

## 5. Guided Judge Demo

The guided demo is a five-step stateful flow with a visible progress indicator,
previous/next controls, direct step navigation, and links into the corresponding
operational workspace.

### Step 1: Cohort reality

- 300 patients and 109 source variables.
- 158 multi-label patients.
- Label imbalance and rare-label support.
- Explanation of why accuracy and multi-class framing are inadequate.

### Step 2: Leakage trap

- PRE_LAB, LAB_AWARE, and FULL tracks.
- Feature availability at decision time.
- Concrete leakage candidate.
- Clear verdict: higher FULL performance is research evidence, not the deployment
  choice.

### Step 3: Patient decision

- Representative urgent patient.
- Calibrated per-label probabilities.
- Actual per-label thresholds.
- Uncertainty, conformal caution set, co-infection detector, priority, and human action.

### Step 4: Ambiguous case

- Representative high-uncertainty patient.
- Broad caution set.
- Explanation of abstention and confirmatory review.
- No forced diagnostic answer.

### Step 5: Resource consequence

- Current demand and capacity.
- Adjustable rapid-test scenario.
- Allocated, waitlisted, and not-eligible counts.
- Center-transfer and clinical-validation limitation in the closing frame.

The flow state is encoded in the URL as `/demo?step=<slug>` so individual steps are
shareable and browser navigation works.

## 6. Command Center

The command center answers three questions:

1. What is the current cohort situation?
2. Which cases need human action now?
3. Which operational capacity is under pressure?

### Required changes

- Replace five equal KPI cards with one primary situation summary and a compact
  secondary metric strip.
- Add an explicit decision chain, such as urgent cases to confirmation demand to
  review burden to resource shortfall.
- Preserve searchable and filterable triage queue.
- Add visible result count, pagination, empty state, and clear filters.
- Link each case to patient review.
- Add a direct link to the relevant resource scenario.
- Add a cohort provenance panel showing run ID, generated time, data mode, model
  track, and whether the export is canonical.
- Do not show `quick_smoke` output as the official competition run.

## 7. Patient Review

The page follows a decision sequence rather than presenting independent metrics.

### Sequence

1. Select a representative scenario or anonymous case.
2. Read the patient decision summary.
3. Inspect calibrated risks and per-label thresholds.
4. Inspect uncertainty and caution set.
5. Distinguish multi-label prediction from separate co-infection probability.
6. Read recommended human action and limitations.
7. Export a privacy-safe case report.

### Corrections

- Derive triage tone from the actual category.
- Export and render the threshold used for every label.
- Determine the co-infection representative scenario from `coinfection_prob`.
- Explain why predicted labels and caution sets may differ.
- Show model track, policy, artifact run, and record source.
- Provide invalid-case recovery and recommended alternatives.

## 8. Batch Intake

Batch intake is necessary because the competition pitch describes saved-model
inference. It must be implemented without exposing the private raw cohort or silently
running unvalidated server-side behavior.

### Architecture

Use a Python inference command to produce a privacy-safe JSON result from an uploaded
CSV during local or controlled demonstrations. The static Vercel prototype offers a
bundled synthetic sample and a schema-validation preview. If a secure inference API
is not configured, the UI explicitly labels live upload inference as unavailable in
the public deployment.

### Workflow

1. Select bundled sample or upload CSV.
2. Parse file and show row count.
3. Validate required, optional, extra, and invalid fields.
4. Select `PRE_LAB` or `LAB_AWARE`, with PRE_LAB as default.
5. Display model version, feature stage, threshold policy, and limitations.
6. Run saved-model inference in the supported environment.
7. Review batch summary and row-level results.
8. Download result CSV and a concise HTML/print report.

### Safety rules

- Never retrain from the dashboard.
- Never silently impute an entirely missing required feature group.
- Never present FULL as an inference mode.
- Never include source UUID or ground-truth diagnosis in public results.
- Preserve the uploaded file only in memory or a temporary controlled location.

## 9. Resource Scenarios

The page is a transparent scenario simulator, not a validated optimization engine.

### Required changes

- Rename resource `gap` to `shortfall` and display only non-negative shortage.
- Introduce `Allocated`, `Waitlisted`, and `Not eligible`.
- Provide sliders and numeric inputs.
- Provide `Current`, `Operational balance`, `Safety-first`, and `Severe shortage`
  presets.
- Provide reset and scenario comparison.
- Show exact demand formulas and identify them as prototype assumptions.
- Compare threshold policies using case burden and resulting resource demand, not only
  total disease flags.
- Show the impact on tests, beds, monitoring, staff review, and high-uncertainty
  backlog.

## 10. Trust Center

The Trust Center organizes evidence around user questions instead of method names.

### Sections

1. How well does the model distinguish diseases?
2. Where does it miss cases?
3. Can probabilities be trusted?
4. When does the model abstain?
5. Does it generalize across centers and groups?
6. What leakage was prevented?

Each section contains:

- one interpretable headline;
- metric estimate and confidence interval where available;
- support count;
- visualization and accessible table;
- plain-language interpretation;
- operational implication;
- `What we cannot claim`; and
- artifact source and evaluation mode.

Typhoid conformal undercoverage and zero rare-label center-transfer recall must be
prominent, not buried.

Tab state is encoded in the URL as `/evidence?section=<slug>`.

## 11. Methodology, Glossary, And Provenance

Expand methodology into:

- problem framing;
- feature-stage model;
- split and validation strategy;
- threshold tuning;
- calibration;
- uncertainty and conformal caution sets;
- co-infection model;
- triage rules and resource assumptions;
- privacy;
- limitations;
- glossary; and
- artifact provenance.

Terms such as macro F1, PR-AUC, entropy, conformal set, calibration, leakage, and
center transfer receive short plain-language definitions. Contextual help links from
other pages target the relevant methodology section.

## 12. Canonical Data Contract

The Python pipeline remains the source of truth. Web exports move to schema version 2.

### Manifest additions

- `run_id`
- `git_commit`
- `data_checksum`
- `config_checksum`
- `execution_profile`
- `canonical`
- `evaluation_mode`
- `model_versions`
- `threshold_policy`
- `generated_at`
- `warnings`

### Patient additions

- per-label calibrated probability;
- per-label decision threshold;
- per-label predicted decision;
- `record_source`;
- model track and policy identifiers.

### Evidence additions

- normalized headline confidence intervals;
- per-label support and prevalence interval;
- policy demand comparison;
- narrative evidence summaries generated from deterministic values;
- source table name and evaluation mode.

Export fails when a production destination is requested from a non-canonical run
unless an explicit development override is supplied.

## 13. Shared Interaction And Content Rules

- Every async action has idle, loading, success, and error states.
- Every table has result count, pagination or explicit complete-list status, and empty
  state.
- Every filter set has a clear/reset action.
- Every icon-only control has an accessible name and a visible explanation where its
  action is not conventional.
- Charts have equivalent summaries or tables for assistive technology.
- Tab systems implement arrow-key behavior and correct panel relationships.
- Capacity controls support keyboard, range, and direct numeric input.
- Clinical status is never communicated by color alone.
- Motion communicates state and respects reduced-motion preferences.

## 14. Error States

### Global

- Unsupported schema version: block rendering and show refresh instructions.
- Missing optional artifact: render an explanatory unavailable state.
- Missing required canonical artifact: block official mode and allow clearly labeled
  development mode only.

### Patient review

- Unknown case: show `Case not found`, preserve the query, and offer representative
  scenarios.

### Batch intake

- Invalid file type or size.
- Empty file.
- Missing required fields.
- Invalid numeric/category values.
- Unsupported model track.
- Inference unavailable in public static mode.
- Partial row failures with downloadable validation report.

### Resource scenarios

- Values below zero or above configured limits.
- No eligible patients.
- Capacity covering all demand.
- Zero available capacity.

## 15. Testing Strategy

- Python tests for export schema, canonical-run guard, privacy fields, and inference
  result generation.
- TypeScript schema tests for v2 contracts.
- Unit tests for thresholds, case selection, allocation status, shortfall, presets,
  evidence interpretation, and URL state.
- Component tests for every page's default, empty, invalid, and interactive state.
- Navigation tests for public versus operational shells.
- Accessibility tests for tabs, focus, accessible chart alternatives, forms, and
  keyboard operation.
- Build and static prerender verification for all public routes.
- Browser smoke tests at desktop, tablet, and mobile widths during implementation.

## 16. Release Phases

1. Canonical data and scientific-semantic corrections.
2. Shared shell separation and landing page.
3. Guided demo.
4. Command center and patient review.
5. Resource scenarios.
6. Trust center and methodology.
7. Batch intake and reporting.
8. Accessibility, responsive, documentation, and release hardening.

Every phase must leave the application testable and deployable. Scientific-semantic
corrections precede visual expansion.

## 17. Non-Goals

- Clinical diagnosis or treatment recommendation.
- Public deployment of raw clinical records or private model artifacts.
- Real-time hospital integration.
- Geospatial outbreak forecasting without timestamps and reliable locations.
- Claiming fairness, external validity, or deployment readiness.
- Building a general-purpose drag-and-drop analytics platform.

## 18. Definition Of Done

- Landing page communicates the project accurately within one minute.
- Guided demo supports the full competition narrative.
- All pitch-promised dashboard features are implemented or the pitch is corrected.
- Dashboard, notebook, report, and pitch use the same canonical run.
- Per-label thresholds and all status semantics match pipeline logic.
- Resource assumptions are visible and allocation states are correct.
- Trust Center foregrounds rare-label and center-transfer limitations.
- All routes pass tests, lint, production build, responsive review, keyboard review,
  and WCAG 2.1 AA checks.
