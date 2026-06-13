# VECTRA-X Next.js Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Streamlit dashboard with a privacy-safe, static-first Next.js Outbreak Triage Command Center deployable to Vercel.

**Architecture:** The Python pipeline exports validated public JSON artifacts. A typed Next.js App Router application renders those artifacts and performs only deterministic client-side filtering and resource allocation. No model training, uploaded data, database, or Python server is part of the deployed application.

**Tech Stack:** Python 3.12, Next.js, React, TypeScript, Tailwind CSS, Recharts, Lucide React, Zod, Vitest, Testing Library, Vercel.

---

### Task 1: Public artifact exporter

**Files:**
- Create: `scripts/export_web_data.py`
- Create: `tests/test_web_export.py`

- [ ] Write failing tests for required artifact failure, UUID and ground-truth removal,
  generated case IDs, manifest warnings, and numeric JSON output.
- [ ] Run `py -3.12 -m pytest tests/test_web_export.py -q` and confirm failures are caused
  by the missing exporter.
- [ ] Implement focused loaders, record sanitization, table serialization, and the four
  public JSON files defined by the specification.
- [ ] Run the exporter tests and confirm they pass.
- [ ] Run `py -3.12 scripts/export_web_data.py` and inspect generated record counts.

### Task 2: Next.js foundation and data contracts

**Files:**
- Create: `web/package.json`
- Create: `web/next.config.ts`
- Create: `web/tsconfig.json`
- Create: `web/postcss.config.mjs`
- Create: `web/eslint.config.mjs`
- Create: `web/vitest.config.ts`
- Create: `web/vitest.setup.ts`
- Create: `web/lib/types.ts`
- Create: `web/lib/schema.ts`
- Create: `web/lib/data.ts`
- Create: `web/lib/format.ts`
- Create: `web/tests/schema.test.ts`

- [ ] Create package and test configuration.
- [ ] Write failing schema tests for accepted exported data and rejected schema versions.
- [ ] Run the focused Vitest command and confirm the expected failures.
- [ ] Implement Zod schemas, typed file loading, and formatting helpers.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Resource and patient-selection logic

**Files:**
- Create: `web/lib/resource-allocation.ts`
- Create: `web/lib/patient-selection.ts`
- Create: `web/tests/resource-allocation.test.ts`
- Create: `web/tests/patient-selection.test.ts`

- [ ] Write failing tests for demand calculation, shortage status, stable test allocation,
  representative scenarios, and label parsing.
- [ ] Run focused tests and verify RED state.
- [ ] Implement pure deterministic functions with no React dependency.
- [ ] Run focused tests and verify GREEN state.

### Task 4: Design system and application shell

**Files:**
- Create: `web/app/globals.css`
- Create: `web/app/layout.tsx`
- Create: `web/components/shell/app-shell.tsx`
- Create: `web/components/shell/side-navigation.tsx`
- Create: `web/components/shell/mobile-navigation.tsx`
- Create: `web/components/ui/status-badge.tsx`
- Create: `web/components/ui/page-header.tsx`
- Create: `web/components/ui/safety-note.tsx`
- Create: `web/components/ui/metric-strip.tsx`
- Create: `web/components/ui/artifact-state.tsx`
- Create: `web/tests/navigation.test.tsx`

- [ ] Write failing navigation and accessibility tests.
- [ ] Run focused tests and verify RED state.
- [ ] Implement semantic shell, responsive navigation, tokens, focus states, reduced
  motion, and shared UI primitives.
- [ ] Run focused tests and verify GREEN state.

### Task 5: Command Center

**Files:**
- Create: `web/app/page.tsx`
- Create: `web/components/command-center/command-center.tsx`
- Create: `web/components/command-center/triage-queue.tsx`
- Create: `web/components/command-center/action-list.tsx`
- Create: `web/components/command-center/demand-charts.tsx`
- Create: `web/tests/command-center.test.tsx`

- [ ] Write failing tests for KPI values, queue sorting, priority filtering, privacy-safe
  display, and safety context.
- [ ] Run focused tests and verify RED state.
- [ ] Implement the server route and interactive client workspace.
- [ ] Run focused tests and verify GREEN state.

### Task 6: Patient Intelligence

**Files:**
- Create: `web/app/patients/page.tsx`
- Create: `web/components/patients/patient-intelligence.tsx`
- Create: `web/components/patients/patient-selector.tsx`
- Create: `web/components/patients/probability-profile.tsx`
- Create: `web/components/patients/decision-record.tsx`
- Create: `web/components/patients/explanation-panel.tsx`
- Create: `web/tests/patient-intelligence.test.tsx`

- [ ] Write failing tests for scenario shortcuts, case changes, probability labels,
  caution sets, recommendation copy, and explanation fallback.
- [ ] Run focused tests and verify RED state.
- [ ] Implement the patient workspace and chart summaries.
- [ ] Run focused tests and verify GREEN state.

### Task 7: Resource Allocation

**Files:**
- Create: `web/app/resources/page.tsx`
- Create: `web/components/resources/resource-allocation.tsx`
- Create: `web/components/resources/capacity-controls.tsx`
- Create: `web/components/resources/capacity-ledger.tsx`
- Create: `web/components/resources/allocation-queue.tsx`
- Create: `web/components/resources/policy-burden.tsx`
- Create: `web/tests/resource-workspace.test.tsx`

- [ ] Write failing interaction tests for slider updates, shortage summaries, and queue
  allocation changes.
- [ ] Run focused tests and verify RED state.
- [ ] Implement the simulator using the tested pure allocation functions.
- [ ] Run focused tests and verify GREEN state.

### Task 8: Trust, Evidence, and Methodology

**Files:**
- Create: `web/app/evidence/page.tsx`
- Create: `web/app/methodology/page.tsx`
- Create: `web/components/evidence/evidence-workspace.tsx`
- Create: `web/components/evidence/model-comparison.tsx`
- Create: `web/components/evidence/safety-evidence.tsx`
- Create: `web/components/evidence/fairness-panel.tsx`
- Create: `web/components/evidence/explainability-panel.tsx`
- Create: `web/components/evidence/methodology-content.tsx`
- Create: `web/tests/evidence.test.tsx`

- [ ] Write failing tests for held-out metric labels, false-negative evidence, fairness
  caveats, leakage warnings, and methodology safety language.
- [ ] Run focused tests and verify RED state.
- [ ] Implement both routes with progressive evidence disclosure.
- [ ] Run focused tests and verify GREEN state.

### Task 9: Remove Streamlit and update project integration

**Files:**
- Delete: `app/`
- Delete: `.streamlit/`
- Delete: `tests/test_dashboard_utils.py`
- Delete: `docs/superpowers/specs/2026-06-13-streamlit-bat-launcher-design.md`
- Delete: `docs/superpowers/plans/2026-06-13-streamlit-bat-launcher.md`
- Modify: `requirements.txt`
- Modify: `README.md`
- Modify: `PRODUCT.md`
- Modify: `open_dashboard.bat`
- Create: `web/vercel.json`

- [ ] Remove Streamlit-only code, tests, dependency, and stale instructions.
- [ ] Rewrite README setup, export, local launch, build, and Vercel deployment sections.
- [ ] Update PRODUCT.md to identify the Next.js command center as the product surface.
- [ ] Rewrite the launcher for npm discovery, conditional install, public-data export,
  development server start, browser opening, error handling, and test mode.
- [ ] Add static Vercel configuration.

### Task 10: Full verification and visual inspection

**Files:**
- Modify only files required by discovered defects.

- [ ] Run `py -3.12 -m pytest tests/test_web_export.py tests/test_submission_artifacts.py -q`.
- [ ] Run `npm test` from `web/`.
- [ ] Run `npm run lint` from `web/`.
- [ ] Run `npm run build` from `web/`.
- [ ] Run launcher test mode and confirm `VECTRA_X_LAUNCHER_OK`.
- [ ] Start the local server and inspect `/`, `/patients`, `/resources`, `/evidence`,
  and `/methodology` at desktop and mobile widths.
- [ ] Fix discovered functional, responsive, accessibility, or visual defects.
- [ ] Re-run the full test, lint, and build gates.
