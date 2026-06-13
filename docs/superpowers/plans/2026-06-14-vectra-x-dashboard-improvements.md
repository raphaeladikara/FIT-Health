# VECTRA-X Dashboard Improvements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clear hybrid VECTRA-X experience consisting of a concise landing page, a guided judge demo, and scientifically accurate operational workspaces backed by one canonical artifact contract.

**Architecture:** The Python pipeline remains the analytical source of truth and exports schema-v2 privacy-safe artifacts. Next.js separates public briefing routes from the operational app shell, then composes each page from typed domain helpers and focused UI components. Scientific semantics and provenance are corrected before page redesign, and every phase remains independently testable.

**Tech Stack:** Python 3.12, pandas, scikit-learn/joblib, Next.js 16 App Router, React 19, TypeScript, Zod, Recharts, Vitest, Testing Library, ESLint, Tailwind CSS 4 plus project CSS tokens.

---

## Delivery Map

| Phase | Deliverable | Primary routes |
|---|---|---|
| 1 | Canonical schema-v2 exports and semantic corrections | Data foundation |
| 2 | Public and operational shell separation | All routes |
| 3 | Landing page | `/` |
| 4 | Guided judge demo | `/demo` |
| 5 | Operational cohort workflow | `/command-center` |
| 6 | Patient decision workflow | `/patients` |
| 7 | Resource policy simulator | `/resources` |
| 8 | Evidence interpretation | `/evidence` |
| 9 | Methodology and glossary | `/methodology` |
| 10 | Batch intake and report export | `/intake` |
| 11 | Accessibility, responsive behavior, documentation, release | All routes |

## Target File Structure

```text
scripts/
|-- export_web_data.py
`-- run_web_inference.py
tests/
|-- test_web_export.py
`-- test_web_inference.py
web/
|-- app/
|   |-- (public)/
|   |   |-- layout.tsx
|   |   |-- page.tsx
|   |   |-- demo/page.tsx
|   |   `-- methodology/page.tsx
|   |-- (workspace)/
|   |   |-- layout.tsx
|   |   |-- command-center/page.tsx
|   |   |-- patients/page.tsx
|   |   |-- resources/page.tsx
|   |   |-- evidence/page.tsx
|   |   `-- intake/page.tsx
|   |-- globals.css
|   `-- layout.tsx
|-- components/
|   |-- landing/
|   |-- demo/
|   |-- command-center/
|   |-- patients/
|   |-- resources/
|   |-- evidence/
|   |-- intake/
|   |-- methodology/
|   |-- shell/
|   `-- ui/
|-- lib/
|   |-- data.ts
|   |-- schema.ts
|   |-- types.ts
|   |-- thresholds.ts
|   |-- provenance.ts
|   |-- resource-allocation.ts
|   |-- resource-presets.ts
|   |-- evidence-insights.ts
|   `-- intake-schema.ts
`-- tests/
```

## Phase 1: Canonical Data And Scientific Semantics

### Task 1: Introduce Schema V2 And Canonical Run Provenance

**Files:**
- Modify: `scripts/export_web_data.py`
- Modify: `web/lib/schema.ts`
- Modify: `web/lib/types.ts`
- Modify: `web/lib/data.ts`
- Modify: `tests/test_web_export.py`
- Modify: `web/tests/schema.test.ts`
- Create: `web/lib/provenance.ts`
- Create: `web/tests/provenance.test.ts`

- [ ] **Step 1: Write failing Python export tests**

Add tests asserting that the manifest contains a stable run identity and that official
exports reject non-canonical profiles:

```python
def test_export_manifest_contains_canonical_provenance(tmp_path, prepared_outputs):
    manifest = export_dashboard_data(
        prepared_outputs,
        tmp_path,
        require_canonical=True,
    )
    assert manifest["schema_version"] == 2
    assert manifest["canonical"] is True
    assert manifest["run_id"]
    assert manifest["data_checksum"]
    assert manifest["config_checksum"]
    assert manifest["evaluation_mode"] == "held_out"


def test_official_export_rejects_quick_smoke(tmp_path, prepared_outputs):
    summary_path = prepared_outputs / "dashboard_data" / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["execution_profile"] = "quick_smoke"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    with pytest.raises(ValueError, match="canonical"):
        export_dashboard_data(prepared_outputs, tmp_path, require_canonical=True)
```

- [ ] **Step 2: Run the focused Python tests**

Run:

```powershell
pytest tests/test_web_export.py -q
```

Expected: FAIL because `require_canonical` and schema version 2 do not exist.

- [ ] **Step 3: Implement deterministic provenance helpers**

In `scripts/export_web_data.py`, add:

```python
import hashlib
import subprocess

SCHEMA_VERSION = 2


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
```

Extend `export_dashboard_data` with `require_canonical: bool = False`, derive
`canonical = execution_profile == "full"`, and reject official export when required.
Build `run_id` from generated timestamp, git commit prefix, data checksum prefix, and
config checksum prefix.

- [ ] **Step 4: Update the TypeScript schema and types**

Define:

```ts
export type Manifest = {
  schema_version: 2;
  run_id: string;
  git_commit: string;
  data_checksum: string;
  config_checksum: string;
  generated_at: string;
  execution_profile: string;
  canonical: boolean;
  evaluation_mode: "held_out" | "oof" | "simulated";
  threshold_policy: string;
  model_versions: Record<string, string>;
  patient_count: number;
  active_labels: string[];
  available_evidence: string[];
  warnings: string[];
};
```

Make `manifestSchema` strict and match the exact fields. Add
`assertOfficialArtifact(manifest)` in `web/lib/provenance.ts`:

```ts
export function officialArtifactWarning(manifest: Manifest): string | null {
  if (!manifest.canonical) {
    return `Development artifact: ${manifest.execution_profile}`;
  }
  if (manifest.evaluation_mode !== "held_out") {
    return `Headline metrics are ${manifest.evaluation_mode}, not held-out`;
  }
  return null;
}
```

- [ ] **Step 5: Add TypeScript schema and provenance tests**

Assert schema-v1 rejection, schema-v2 acceptance, canonical warning behavior, and
exact evaluation-mode parsing.

- [ ] **Step 6: Run focused verification**

Run:

```powershell
pytest tests/test_web_export.py -q
cd web
npm.cmd test -- schema.test.ts provenance.test.ts
```

Expected: all focused tests PASS.

- [ ] **Step 7: Commit**

```powershell
git add scripts/export_web_data.py tests/test_web_export.py web/lib/schema.ts web/lib/types.ts web/lib/data.ts web/lib/provenance.ts web/tests/schema.test.ts web/tests/provenance.test.ts
git commit -m "feat: add canonical web artifact provenance"
```

### Task 2: Export Per-Label Thresholds And Correct Patient Semantics

**Files:**
- Modify: `scripts/export_web_data.py`
- Modify: `web/lib/schema.ts`
- Modify: `web/lib/types.ts`
- Create: `web/lib/thresholds.ts`
- Create: `web/tests/thresholds.test.ts`
- Modify: `web/lib/patient-selection.ts`
- Modify: `web/tests/patient-selection.test.ts`

- [ ] **Step 1: Write failing threshold and scenario tests**

```ts
it("uses the exported threshold for each label", () => {
  expect(
    decisionForProbability({ probability: 0.2, threshold: 0.18 }),
  ).toBe(true);
});

it("selects the strongest separate co-infection risk", () => {
  expect(selectRepresentativePatient(patients, "co-infection")?.case_id).toBe(
    "Case 003",
  );
});
```

The fixture must include a multi-label case with low co-infection probability and a
different case with the highest `coinfection_prob`.

- [ ] **Step 2: Run tests and confirm failure**

Run:

```powershell
cd web
npm.cmd test -- thresholds.test.ts patient-selection.test.ts
```

Expected: FAIL because `decisionForProbability` is missing and co-infection selection
still uses predicted-label count.

- [ ] **Step 3: Normalize patient decisions in the Python export**

Export each patient with:

```json
{
  "label_decisions": {
    "dengue": {
      "probability": 0.23,
      "threshold": 0.18,
      "predicted": true
    }
  },
  "model_track": "PRE_LAB",
  "threshold_policy": "operational",
  "record_source": "full_cohort_oof"
}
```

Read thresholds from `outputs/tables/threshold_policies.csv` or the canonical table
selected by the summary. Fail export when an active label lacks a threshold.

- [ ] **Step 4: Implement typed helpers**

In `web/lib/thresholds.ts`:

```ts
export type LabelDecision = {
  probability: number;
  threshold: number;
  predicted: boolean;
};

export function decisionForProbability({
  probability,
  threshold,
}: Pick<LabelDecision, "probability" | "threshold">): boolean {
  return probability >= threshold;
}
```

Change co-infection selection to:

```ts
if (scenario === "co-infection") {
  return [...patients].sort(
    (a, b) => b.coinfection_prob - a.coinfection_prob,
  )[0];
}
```

- [ ] **Step 5: Run focused tests**

Run:

```powershell
pytest tests/test_web_export.py -q
cd web
npm.cmd test -- thresholds.test.ts patient-selection.test.ts schema.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add scripts/export_web_data.py tests/test_web_export.py web/lib/schema.ts web/lib/types.ts web/lib/thresholds.ts web/lib/patient-selection.ts web/tests/thresholds.test.ts web/tests/patient-selection.test.ts
git commit -m "fix: align patient decisions with label thresholds"
```

### Task 3: Correct Resource Allocation Domain Semantics

**Files:**
- Modify: `web/lib/types.ts`
- Modify: `web/lib/resource-allocation.ts`
- Create: `web/lib/resource-presets.ts`
- Modify: `web/tests/resource-allocation.test.ts`
- Create: `web/tests/resource-presets.test.ts`

- [ ] **Step 1: Write failing allocation tests**

```ts
it("distinguishes allocated, waitlisted, and ineligible cases", () => {
  const result = allocateRapidTests(patients, 1);
  expect(result.find((p) => p.case_id === "Case 001")?.test_allocation).toBe("Allocated");
  expect(result.find((p) => p.case_id === "Case 002")?.test_allocation).toBe("Waitlisted");
  expect(result.find((p) => p.case_id === "Case 003")?.test_allocation).toBe("Not eligible");
});

it("reports a non-negative shortfall", () => {
  const row = calculateCapacity(patients, inputs)[0];
  expect(row.shortfall).toBe(Math.max(row.demand - row.capacity, 0));
});
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```powershell
cd web
npm.cmd test -- resource-allocation.test.ts
```

Expected: FAIL because the current model returns `Waiting` and exposes signed `gap`.

- [ ] **Step 3: Implement corrected domain types**

```ts
export type CapacityRow = {
  resource: ResourceName;
  demand: number;
  capacity: number;
  shortfall: number;
  surplus: number;
  status: "Sufficient" | "Insufficient";
  assumption: string;
};

export type TestAllocation = "Allocated" | "Waitlisted" | "Not eligible";
```

Return:

```ts
shortfall: Math.max(demand - capacity, 0),
surplus: Math.max(capacity - demand, 0),
```

For allocation:

```ts
const test_allocation = !eligible
  ? "Not eligible"
  : receivesTest
    ? "Allocated"
    : "Waitlisted";
```

- [ ] **Step 4: Add named presets**

In `resource-presets.ts`, export:

```ts
export const RESOURCE_PRESETS = {
  current: { rapidTests: 50, beds: 12, monitoringSlots: 80, staffReviews: 80 },
  operational: { rapidTests: 100, beds: 35, monitoringSlots: 120, staffReviews: 150 },
  safety: { rapidTests: 160, beds: 50, monitoringSlots: 180, staffReviews: 220 },
  severeShortage: { rapidTests: 20, beds: 5, monitoringSlots: 30, staffReviews: 40 },
} satisfies Record<string, CapacityInput>;
```

Keep values configurable later, but make this first implementation deterministic.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd web
npm.cmd test -- resource-allocation.test.ts resource-presets.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add web/lib/types.ts web/lib/resource-allocation.ts web/lib/resource-presets.ts web/tests/resource-allocation.test.ts web/tests/resource-presets.test.ts
git commit -m "fix: clarify resource shortfall and eligibility"
```

## Phase 2: Route And Shell Architecture

### Task 4: Separate Public And Operational Layouts

**Files:**
- Modify: `web/app/layout.tsx`
- Create: `web/app/(public)/layout.tsx`
- Create: `web/app/(workspace)/layout.tsx`
- Move: `web/app/page.tsx` to `web/app/(workspace)/command-center/page.tsx`
- Move: `web/app/patients/page.tsx` to `web/app/(workspace)/patients/page.tsx`
- Move: `web/app/resources/page.tsx` to `web/app/(workspace)/resources/page.tsx`
- Move: `web/app/evidence/page.tsx` to `web/app/(workspace)/evidence/page.tsx`
- Move: `web/app/methodology/page.tsx` to `web/app/(public)/methodology/page.tsx`
- Create: `web/components/shell/public-header.tsx`
- Modify: `web/components/shell/app-shell.tsx`
- Modify: `web/components/shell/side-navigation.tsx`
- Modify: `web/tests/navigation.test.tsx`
- Create: `web/tests/layout-routing.test.tsx`

- [ ] **Step 1: Write failing navigation tests**

Assert that:

- the public header contains `Overview`, `Guided demo`, `Methodology`, and
  `Open command center`;
- the operational sidebar contains `Command Center`, `Patient Review`, `Batch Intake`,
  `Resource Scenarios`, and `Trust Center`;
- `/command-center` is the active operational route; and
- the landing page does not render the operational sidebar.

- [ ] **Step 2: Run tests and verify failure**

Run:

```powershell
cd web
npm.cmd test -- navigation.test.tsx layout-routing.test.tsx
```

- [ ] **Step 3: Implement route groups**

Keep the root layout limited to fonts, metadata, and global styles:

```tsx
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jakarta.variable}`}>{children}</body>
    </html>
  );
}
```

The workspace layout wraps children in `AppShell`. The public layout renders
`PublicHeader`, `<main id="main-content">`, and a compact footer containing the
non-diagnostic warning.

- [ ] **Step 4: Update operational labels and links**

Use:

```ts
[
  ["/command-center", "Command Center"],
  ["/patients", "Patient Review"],
  ["/intake", "Batch Intake"],
  ["/resources", "Resource Scenarios"],
  ["/evidence", "Trust Center"],
]
```

Update all old `/` links to `/command-center`.

- [ ] **Step 5: Run tests and build route discovery**

Run:

```powershell
cd web
npm.cmd test -- navigation.test.tsx layout-routing.test.tsx
npm.cmd run lint
```

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add web/app web/components/shell web/tests/navigation.test.tsx web/tests/layout-routing.test.tsx
git commit -m "refactor: separate public and workspace routes"
```

## Phase 3: Landing Page

### Task 5: Build The Landing Page Data Model

**Files:**
- Create: `web/lib/landing-content.ts`
- Create: `web/tests/landing-content.test.ts`
- Modify: `web/lib/data.ts`

- [ ] **Step 1: Write a failing content test**

```ts
it("builds the landing evidence snapshot from canonical artifacts", () => {
  const snapshot = buildLandingSnapshot(data);
  expect(snapshot.patientCount).toBe(300);
  expect(snapshot.multiLabelCount).toBe(158);
  expect(snapshot.macroF1.interval).toEqual([0.5021, 0.7013]);
  expect(snapshot.canonical).toBe(true);
});
```

- [ ] **Step 2: Implement deterministic landing selectors**

Create selectors that retrieve confidence intervals by metric name and throw a useful
error if the canonical headline interval is absent. Do not hard-code metric values in
components.

- [ ] **Step 3: Run test**

Run:

```powershell
cd web
npm.cmd test -- landing-content.test.ts
```

- [ ] **Step 4: Commit**

```powershell
git add web/lib/landing-content.ts web/lib/data.ts web/tests/landing-content.test.ts
git commit -m "feat: add typed landing page evidence model"
```

### Task 6: Implement The Landing Page

**Files:**
- Create: `web/app/(public)/page.tsx`
- Create: `web/components/landing/landing-hero.tsx`
- Create: `web/components/landing/operational-flow.tsx`
- Create: `web/components/landing/differentiators.tsx`
- Create: `web/components/landing/evidence-snapshot.tsx`
- Create: `web/components/landing/path-selector.tsx`
- Create: `web/components/landing/limitations-band.tsx`
- Modify: `web/app/globals.css`
- Create: `web/tests/landing-page.test.tsx`

- [ ] **Step 1: Write failing page tests**

Assert the page exposes:

- one `h1`;
- `Start guided demo` linked to `/demo`;
- `Open command center` linked to `/command-center`;
- five operational-flow steps;
- canonical run status;
- four limitations; and
- no operational sidebar.

- [ ] **Step 2: Run test and verify failure**

```powershell
cd web
npm.cmd test -- landing-page.test.tsx
```

- [ ] **Step 3: Implement semantic page composition**

Use a server page:

```tsx
export default async function LandingPage() {
  const data = await loadDashboardData();
  const snapshot = buildLandingSnapshot(data);
  return (
    <>
      <LandingHero manifest={data.manifest} />
      <OperationalFlow />
      <Differentiators />
      <EvidenceSnapshot snapshot={snapshot} />
      <PathSelector />
      <LimitationsBand />
    </>
  );
}
```

Avoid six identical cards. Use one horizontal flow, a two-column differentiator
section, a compact evidence band, and a final route chooser.

- [ ] **Step 4: Add responsive and reduced-motion styles**

Create `.landing-*` rules using existing tokens. Use fixed product typography,
maximum copy width of 70ch, and stack the operational flow at mobile widths. Do not
introduce new gradients, glass panels, or decorative medical imagery.

- [ ] **Step 5: Run focused and global checks**

```powershell
cd web
npm.cmd test -- landing-page.test.tsx
npm.cmd run lint
```

- [ ] **Step 6: Commit**

```powershell
git add web/app/(public)/page.tsx web/components/landing web/app/globals.css web/tests/landing-page.test.tsx
git commit -m "feat: add VECTRA-X product briefing"
```

## Phase 4: Guided Judge Demo

### Task 7: Implement Shareable Demo State

**Files:**
- Create: `web/lib/demo-steps.ts`
- Create: `web/tests/demo-steps.test.ts`
- Create: `web/components/demo/demo-navigation.tsx`

- [ ] **Step 1: Write failing demo-state tests**

```ts
it("falls back to cohort when the step is invalid", () => {
  expect(resolveDemoStep("unknown").slug).toBe("cohort");
});

it("returns adjacent steps", () => {
  expect(adjacentDemoSteps("patient").next?.slug).toBe("uncertainty");
});
```

- [ ] **Step 2: Implement the step registry**

```ts
export const DEMO_STEPS = [
  { slug: "cohort", label: "Cohort reality", workspaceHref: "/command-center" },
  { slug: "leakage", label: "Leakage trap", workspaceHref: "/evidence?section=leakage" },
  { slug: "patient", label: "Patient decision", workspaceHref: "/patients" },
  { slug: "uncertainty", label: "Ambiguous case", workspaceHref: "/patients?scenario=high-uncertainty" },
  { slug: "resources", label: "Resource consequence", workspaceHref: "/resources" },
] as const;
```

- [ ] **Step 3: Run test and commit**

```powershell
cd web
npm.cmd test -- demo-steps.test.ts
git add web/lib/demo-steps.ts web/tests/demo-steps.test.ts web/components/demo/demo-navigation.tsx
git commit -m "feat: add guided demo navigation model"
```

### Task 8: Build All Five Demo Steps

**Files:**
- Create: `web/app/(public)/demo/page.tsx`
- Create: `web/components/demo/guided-demo.tsx`
- Create: `web/components/demo/cohort-step.tsx`
- Create: `web/components/demo/leakage-step.tsx`
- Create: `web/components/demo/patient-step.tsx`
- Create: `web/components/demo/uncertainty-step.tsx`
- Create: `web/components/demo/resources-step.tsx`
- Modify: `web/app/globals.css`
- Create: `web/tests/guided-demo.test.tsx`

- [ ] **Step 1: Write failing tests for every step**

Test the following authoritative signals:

- cohort: multi-label count and imbalance explanation;
- leakage: FULL labeled `Research only`;
- patient: selected urgent case uses exported label thresholds;
- uncertainty: high-uncertainty case and caution-set explanation;
- resources: allocated, waitlisted, and not-eligible counts;
- navigation: URL links use `?step=<slug>`.

- [ ] **Step 2: Build the server page and client navigator**

The server resolves `searchParams.step`, loads data once, and passes the selected
step to `GuidedDemo`. The demo navigator uses links, not hidden local-only state, so
browser history and sharing work.

- [ ] **Step 3: Implement each step as a focused component**

Each step must expose:

- one thesis heading;
- one primary visual or comparison;
- one plain-language interpretation;
- one limitation or safety statement; and
- one deep link into the operational workspace.

Do not reuse the full operational pages inside the demo.

- [ ] **Step 4: Run tests**

```powershell
cd web
npm.cmd test -- guided-demo.test.tsx demo-steps.test.ts
npm.cmd run lint
```

- [ ] **Step 5: Commit**

```powershell
git add web/app/(public)/demo web/components/demo web/app/globals.css web/tests/guided-demo.test.tsx
git commit -m "feat: add five-step judge demonstration"
```

## Phase 5: Command Center

### Task 9: Refactor The Command Center Into A Decision Overview

**Files:**
- Modify: `web/app/(workspace)/command-center/page.tsx`
- Modify: `web/components/command-center/command-center.tsx`
- Create: `web/components/command-center/situation-summary.tsx`
- Create: `web/components/command-center/decision-chain.tsx`
- Create: `web/components/command-center/triage-queue.tsx`
- Create: `web/components/ui/pagination.tsx`
- Create: `web/components/ui/empty-state.tsx`
- Create: `web/components/ui/provenance-panel.tsx`
- Create: `web/lib/pagination.ts`
- Create: `web/tests/command-center.test.tsx`
- Create: `web/tests/pagination.test.ts`

- [ ] **Step 1: Write failing queue and pagination tests**

Test:

- result count changes with filters;
- empty filters render `No matching cases`;
- `Clear filters` restores results;
- page size is 25;
- page navigation does not lose filters;
- provenance warning appears for non-canonical artifacts.

- [ ] **Step 2: Extract pure pagination**

```ts
export function paginate<T>(items: T[], page: number, pageSize: number) {
  const totalPages = Math.max(1, Math.ceil(items.length / pageSize));
  const currentPage = Math.min(Math.max(page, 1), totalPages);
  return {
    items: items.slice((currentPage - 1) * pageSize, currentPage * pageSize),
    currentPage,
    totalPages,
  };
}
```

- [ ] **Step 3: Build the new composition**

Order:

1. `SituationSummary`
2. `DecisionChain`
3. `TriageQueue`
4. secondary charts and provenance

The primary summary sentence must be generated from data:

```tsx
<strong>{urgent}</strong> cases require urgent response.{" "}
<strong>{confirmatory + urgent}</strong> compete for confirmatory tests, and{" "}
<strong>{uncertain}</strong> add human-review demand.
```

- [ ] **Step 4: Add resource deep link**

Use:

```tsx
<Link href="/resources?preset=current">Review current capacity</Link>
```

- [ ] **Step 5: Run tests and commit**

```powershell
cd web
npm.cmd test -- command-center.test.tsx pagination.test.ts
npm.cmd run lint
git add web/app/(workspace)/command-center web/components/command-center web/components/ui web/lib/pagination.ts web/tests/command-center.test.tsx web/tests/pagination.test.ts
git commit -m "feat: turn command center into a decision overview"
```

## Phase 6: Patient Review

### Task 10: Rebuild Patient Review Around The Decision Sequence

**Files:**
- Modify: `web/app/(workspace)/patients/page.tsx`
- Modify: `web/components/patients/patient-intelligence.tsx`
- Create: `web/components/patients/patient-selector.tsx`
- Create: `web/components/patients/decision-summary.tsx`
- Create: `web/components/patients/label-decision-list.tsx`
- Create: `web/components/patients/uncertainty-panel.tsx`
- Create: `web/components/patients/action-record.tsx`
- Create: `web/components/patients/case-report.tsx`
- Modify: `web/components/ui/status-badge.tsx`
- Create: `web/tests/patient-review.test.tsx`

- [ ] **Step 1: Write failing patient-review tests**

Test:

- routine case uses routine tone;
- every label renders its exported threshold;
- threshold crossing matches `predicted`;
- co-infection scenario chooses highest detector probability;
- unknown case shows recovery state;
- report excludes private identifiers and diagnosis claims.

- [ ] **Step 2: Implement semantic tone selection**

Replace fixed urgent tone with:

```tsx
tone: triageTone(selected.triage_category)
```

Add `Waitlisted` and `Not eligible` mappings to `StatusBadge`.

- [ ] **Step 3: Render label decisions from structured data**

Use:

```tsx
{Object.entries(selected.label_decisions).map(([label, decision]) => (
  <LabelDecisionRow
    key={label}
    label={label}
    probability={decision.probability}
    threshold={decision.threshold}
    predicted={decision.predicted}
  />
))}
```

The marker position is `threshold * 100`, never a hard-coded 50%.

- [ ] **Step 4: Add unknown-case recovery**

When `initialCaseId` is absent from the data, show:

```tsx
<EmptyState
  title="Case not found"
  description={`No anonymous case matches ${initialCaseId}.`}
  actionHref="/patients?scenario=highest-priority"
  actionLabel="Open highest-priority case"
/>
```

- [ ] **Step 5: Add privacy-safe printable report**

Render a print-only section with run ID, model track, probabilities, thresholds,
uncertainty, caution set, action, and non-diagnostic warning. Add a client button that
calls `window.print()` and label it `Print case report`.

- [ ] **Step 6: Run tests and commit**

```powershell
cd web
npm.cmd test -- patient-review.test.tsx patient-selection.test.ts thresholds.test.ts
npm.cmd run lint
git add web/app/(workspace)/patients web/components/patients web/components/ui/status-badge.tsx web/tests/patient-review.test.tsx
git commit -m "feat: rebuild patient review around human action"
```

## Phase 7: Resource Scenarios

### Task 11: Add Presets, Numeric Inputs, Comparison, And Assumptions

**Files:**
- Modify: `web/app/(workspace)/resources/page.tsx`
- Modify: `web/components/resources/resource-workspace.tsx`
- Create: `web/components/resources/capacity-control.tsx`
- Create: `web/components/resources/scenario-presets.tsx`
- Create: `web/components/resources/scenario-comparison.tsx`
- Create: `web/components/resources/allocation-queue.tsx`
- Create: `web/components/resources/assumptions-panel.tsx`
- Modify: `web/app/globals.css`
- Modify: `web/tests/resource-workspace.test.tsx`

- [ ] **Step 1: Write failing resource-workspace tests**

Test:

- selecting `Safety-first` loads the safety preset;
- numeric input and slider remain synchronized;
- reset restores current preset;
- shortfall is never negative;
- non-eligible patients are labeled correctly;
- comparison displays changes in allocated and waitlisted counts;
- assumptions are visible without hover.

- [ ] **Step 2: Build accessible capacity controls**

Each resource control contains:

```tsx
<input type="number" min={0} max={max} value={value} ... />
<input type="range" min={0} max={max} value={value} ... />
```

Both inputs share one label and update the same state. Clamp values with a pure helper.

- [ ] **Step 3: Add scenario state**

Read `preset` from the query string on initial load. Preserve a baseline and current
scenario, then calculate:

```ts
type ScenarioImpact = {
  allocatedTests: number;
  waitlistedTests: number;
  urgentBedShortfall: number;
  monitoringShortfall: number;
  reviewShortfall: number;
};
```

- [ ] **Step 4: Replace the old policy list**

Turn `threshold_policy_tradeoff` into a comparison table with policy, average flags,
confirmatory demand, review demand, and a plain-language trade-off. Extend the Python
export if these resource-demand columns are not present.

- [ ] **Step 5: Run tests and commit**

```powershell
cd web
npm.cmd test -- resource-workspace.test.tsx resource-allocation.test.ts resource-presets.test.ts
npm.cmd run lint
git add web/app/(workspace)/resources web/components/resources web/app/globals.css web/tests/resource-workspace.test.tsx scripts/export_web_data.py tests/test_web_export.py
git commit -m "feat: add transparent resource scenario comparison"
```

## Phase 8: Trust Center

### Task 12: Build Typed Evidence Interpretation

**Files:**
- Create: `web/lib/evidence-insights.ts`
- Create: `web/tests/evidence-insights.test.ts`
- Modify: `web/lib/types.ts`

- [ ] **Step 1: Write failing interpretation tests**

```ts
it("flags typhoid conformal undercoverage", () => {
  const insight = conformalInsight(typhoidRow, 0.9);
  expect(insight.severity).toBe("warning");
  expect(insight.summary).toMatch(/57.1%/);
});

it("flags zero rare-label transfer recall", () => {
  expect(centerTransferInsight(rows).limitations).toContain(
    "Rare-label recall is zero in both held-out centers",
  );
});
```

- [ ] **Step 2: Implement deterministic insight builders**

Return structured objects:

```ts
export type EvidenceInsight = {
  title: string;
  summary: string;
  implication: string;
  cannotClaim: string;
  severity: "neutral" | "warning" | "critical";
  source: string;
};
```

No generated or free-form AI text is used in production evidence interpretation.

- [ ] **Step 3: Run tests and commit**

```powershell
cd web
npm.cmd test -- evidence-insights.test.ts
git add web/lib/evidence-insights.ts web/lib/types.ts web/tests/evidence-insights.test.ts
git commit -m "feat: add deterministic evidence interpretation"
```

### Task 13: Rebuild Trust Center Around Six Questions

**Files:**
- Modify: `web/app/(workspace)/evidence/page.tsx`
- Modify: `web/components/evidence/evidence-workspace.tsx`
- Create: `web/components/evidence/evidence-navigation.tsx`
- Create: `web/components/evidence/evidence-section.tsx`
- Create: `web/components/evidence/metric-with-interval.tsx`
- Create: `web/components/evidence/support-aware-table.tsx`
- Create: `web/components/evidence/claim-boundary.tsx`
- Create: `web/tests/trust-center.test.tsx`

- [ ] **Step 1: Write failing Trust Center tests**

Assert:

- URL section selects the correct content;
- invalid section falls back to performance;
- confidence intervals appear beside headline metrics;
- support counts appear beside rare-label metrics;
- typhoid undercoverage is prominent;
- center-transfer zero recall is visible;
- FULL is labeled research-only;
- every section includes `What we cannot claim`.

- [ ] **Step 2: Implement URL-driven sections**

Use slugs:

```ts
type EvidenceSection =
  | "performance"
  | "missed-cases"
  | "calibration"
  | "abstention"
  | "generalization"
  | "leakage";
```

Use links with `?section=<slug>` and implement `role="tablist"` only if full keyboard
tab semantics are provided. Otherwise use a conventional local navigation list.

- [ ] **Step 3: Compose each section**

Each section renders:

```tsx
<EvidenceSection
  headline={...}
  insight={...}
  visualization={...}
  table={...}
  claimBoundary={...}
  provenance={...}
/>
```

- [ ] **Step 4: Add accessible alternatives**

Every Recharts visualization must have an adjacent summary and a visually collapsible
data table that remains available to assistive technology.

- [ ] **Step 5: Run tests and commit**

```powershell
cd web
npm.cmd test -- trust-center.test.tsx evidence-insights.test.ts
npm.cmd run lint
git add web/app/(workspace)/evidence web/components/evidence web/tests/trust-center.test.tsx
git commit -m "feat: turn evidence into a question-led trust center"
```

## Phase 9: Methodology And Contextual Help

### Task 14: Expand Methodology, Glossary, And Deep Links

**Files:**
- Modify: `web/app/(public)/methodology/page.tsx`
- Create: `web/components/methodology/methodology-navigation.tsx`
- Create: `web/components/methodology/glossary.tsx`
- Create: `web/components/ui/term-help.tsx`
- Create: `web/lib/glossary.ts`
- Create: `web/tests/methodology.test.tsx`
- Create: `web/tests/glossary.test.ts`

- [ ] **Step 1: Write failing glossary tests**

Assert definitions exist for:

- macro F1;
- PR-AUC;
- calibration;
- entropy;
- conformal caution set;
- leakage;
- center transfer; and
- out-of-fold prediction.

- [ ] **Step 2: Create the glossary registry**

```ts
export const GLOSSARY = {
  "macro-f1": {
    term: "Macro F1",
    definition: "The average F1 score across diseases, giving each disease equal weight.",
  },
  leakage: {
    term: "Diagnostic leakage",
    definition: "Information unavailable at the intended decision time that reveals or restates the outcome.",
  },
} as const;
```

- [ ] **Step 3: Expand methodology sections**

Add sections for feature stages, validation, thresholds, calibration, conformal
caution sets, co-infection, triage formula, resource assumptions, privacy, artifact
provenance, and limitations. Link each section with stable IDs.

- [ ] **Step 4: Add contextual term links**

`TermHelp` renders an accessible link to `/methodology#glossary-<slug>`. Use it beside
technical terms on patient, resource, and evidence pages; do not hide essential
definitions exclusively in tooltips.

- [ ] **Step 5: Run tests and commit**

```powershell
cd web
npm.cmd test -- methodology.test.tsx glossary.test.ts
npm.cmd run lint
git add web/app/(public)/methodology web/components/methodology web/components/ui/term-help.tsx web/lib/glossary.ts web/tests/methodology.test.tsx web/tests/glossary.test.ts
git commit -m "feat: add methodology guidance and glossary"
```

## Phase 10: Batch Intake And Reporting

### Task 15: Define Intake Schema And Validation Report

**Files:**
- Create: `web/lib/intake-schema.ts`
- Create: `web/lib/intake-validation.ts`
- Create: `web/tests/intake-validation.test.ts`
- Create: `web/public/samples/vectra-x-pre-lab-sample.csv`
- Modify: `scripts/export_web_data.py`

- [ ] **Step 1: Write failing validation tests**

Test:

- valid sample passes;
- missing required columns blocks inference;
- extra columns produce warnings but remain allowed;
- invalid numeric values report row and column;
- FULL is rejected as an inference track;
- empty CSV is rejected.

- [ ] **Step 2: Export a machine-readable intake schema**

Create `web/public/data/intake-schema.json`:

```json
{
  "schema_version": 1,
  "tracks": {
    "PRE_LAB": {
      "required_columns": ["..."],
      "optional_columns": ["..."]
    },
    "LAB_AWARE": {
      "required_columns": ["..."],
      "optional_columns": ["..."]
    }
  },
  "max_rows": 500,
  "max_bytes": 5242880
}
```

Derive columns from the fitted pipeline metadata rather than maintaining a second
manual list.

- [ ] **Step 3: Implement browser-side preflight validation**

Return:

```ts
export type IntakeValidation = {
  valid: boolean;
  rowCount: number;
  missingColumns: string[];
  extraColumns: string[];
  cellErrors: Array<{ row: number; column: string; message: string }>;
};
```

- [ ] **Step 4: Run tests and commit**

```powershell
cd web
npm.cmd test -- intake-validation.test.ts
cd ..
pytest tests/test_web_export.py -q
git add web/lib/intake-schema.ts web/lib/intake-validation.ts web/tests/intake-validation.test.ts web/public/samples scripts/export_web_data.py tests/test_web_export.py
git commit -m "feat: add batch intake schema validation"
```

### Task 16: Add Saved-Model Inference Command

**Files:**
- Create: `scripts/run_web_inference.py`
- Create: `tests/test_web_inference.py`
- Modify: `vectra_x_outputs/models/README.json` or canonical model manifest generator
- Modify: `README.md`

- [ ] **Step 1: Write failing command tests**

Test:

- PRE_LAB sample produces privacy-safe JSON;
- LAB_AWARE requires its additional fields;
- FULL track is rejected;
- output includes model version, run ID, thresholds, and warnings;
- source UUID and ground truth never appear;
- partial invalid rows produce a validation report without inference.

- [ ] **Step 2: Implement a pure inference function**

```python
def run_saved_inference(
    frame: pd.DataFrame,
    *,
    track: str,
    model_dir: Path,
    threshold_policy: str,
) -> dict[str, Any]:
    if track not in {"PRE_LAB", "LAB_AWARE"}:
        raise ValueError("Only PRE_LAB and LAB_AWARE inference are supported")
    ...
```

Load persisted preprocessing and model bundles with joblib. Never fit or retrain.

- [ ] **Step 3: Implement the CLI**

```powershell
python scripts/run_web_inference.py `
  --input web/public/samples/vectra-x-pre-lab-sample.csv `
  --track PRE_LAB `
  --output C:\tmp\vectra-x-inference.json
```

Expected: exit code 0 and a privacy-safe JSON result.

- [ ] **Step 4: Run tests and commit**

```powershell
pytest tests/test_web_inference.py -q
git add scripts/run_web_inference.py tests/test_web_inference.py README.md vectra_x_outputs/models/README.json
git commit -m "feat: add saved-model batch inference command"
```

### Task 17: Build Batch Intake UI With Static-Mode Honesty

**Files:**
- Create: `web/app/(workspace)/intake/page.tsx`
- Create: `web/components/intake/intake-workspace.tsx`
- Create: `web/components/intake/file-dropzone.tsx`
- Create: `web/components/intake/schema-preflight.tsx`
- Create: `web/components/intake/model-track-selector.tsx`
- Create: `web/components/intake/batch-results.tsx`
- Create: `web/components/intake/export-actions.tsx`
- Create: `web/tests/intake-workspace.test.tsx`
- Modify: `web/app/globals.css`

- [ ] **Step 1: Write failing intake-workspace tests**

Test:

- bundled sample can be loaded;
- invalid CSV blocks the run action;
- missing columns are listed;
- PRE_LAB is selected by default;
- FULL never appears;
- public static mode clearly says live inference is unavailable;
- imported result JSON renders batch summary;
- CSV and print report export controls become available after success.

- [ ] **Step 2: Implement deployment capability configuration**

Use:

```ts
export type InferenceCapability =
  | { mode: "static-demo"; liveInference: false }
  | { mode: "connected"; liveInference: true; endpoint: string };
```

Read a server-side environment setting in the page. Never expose a secret in the
client bundle.

- [ ] **Step 3: Implement the workflow state machine**

```ts
type IntakeState =
  | { status: "idle" }
  | { status: "validating"; fileName: string }
  | { status: "invalid"; report: IntakeValidation }
  | { status: "ready"; report: IntakeValidation }
  | { status: "running"; report: IntakeValidation }
  | { status: "success"; result: BatchInferenceResult }
  | { status: "error"; message: string };
```

- [ ] **Step 4: Implement exports**

Generate CSV with `Blob` and `URL.createObjectURL`; generate a print-friendly report
within the page. Include run ID, model track, policy, row count, validation warnings,
and non-diagnostic statement.

- [ ] **Step 5: Run tests and commit**

```powershell
cd web
npm.cmd test -- intake-workspace.test.tsx intake-validation.test.ts
npm.cmd run lint
git add web/app/(workspace)/intake web/components/intake web/app/globals.css web/tests/intake-workspace.test.tsx
git commit -m "feat: add transparent batch intake workspace"
```

## Phase 11: Cross-Cutting Quality And Release

### Task 18: Add Global Status, Empty, Error, And Artifact States

**Files:**
- Create: `web/components/ui/artifact-status.tsx`
- Create: `web/components/ui/error-state.tsx`
- Create: `web/components/ui/loading-skeleton.tsx`
- Modify: `web/components/shell/top-bar.tsx`
- Modify: `web/components/shell/app-shell.tsx`
- Create: `web/tests/artifact-status.test.tsx`
- Modify: `web/app/globals.css`

- [ ] **Step 1: Write failing artifact-state tests**

Test canonical, development, optional-warning, and blocking-required-artifact states.
The top-bar control must open visible content rather than relying on a `title`
attribute.

- [ ] **Step 2: Replace the inert bell**

Use a native `<details>` disclosure or accessible popover containing:

- run ID;
- generation time;
- execution profile;
- canonical status;
- evaluation mode;
- model versions; and
- warnings.

- [ ] **Step 3: Add shared states**

All pages use the same `EmptyState`, `ErrorState`, and skeleton patterns. No page
silently renders an empty table or missing artifact.

- [ ] **Step 4: Run tests and commit**

```powershell
cd web
npm.cmd test -- artifact-status.test.tsx
npm.cmd run lint
git add web/components/ui web/components/shell web/app/globals.css web/tests/artifact-status.test.tsx
git commit -m "feat: expose artifact and recovery states"
```

### Task 19: Complete Keyboard And Accessible Data Behavior

**Files:**
- Modify: `web/components/charts/*.tsx`
- Modify: `web/components/evidence/evidence-navigation.tsx`
- Modify: `web/components/shell/mobile-navigation.tsx`
- Modify: `web/components/ui/pagination.tsx`
- Create: `web/components/ui/accessible-chart.tsx`
- Create: `web/tests/accessibility-behavior.test.tsx`

- [ ] **Step 1: Write failing keyboard tests**

Test:

- demo step links are keyboard reachable;
- evidence navigation supports standard link behavior;
- mobile menu closes with Escape and restores focus;
- pagination announces current page;
- charts expose an accessible summary and table;
- all range controls have numeric alternatives.

- [ ] **Step 2: Implement accessible chart wrapper**

```tsx
export function AccessibleChart({
  label,
  summary,
  chart,
  table,
}: {
  label: string;
  summary: string;
  chart: ReactNode;
  table: ReactNode;
}) {
  return (
    <figure aria-labelledby={`${slug(label)}-caption`}>
      <div aria-hidden="true">{chart}</div>
      <figcaption id={`${slug(label)}-caption`}>{summary}</figcaption>
      <div className="sr-only">{table}</div>
    </figure>
  );
}
```

- [ ] **Step 3: Implement mobile focus behavior**

Store the menu button ref, close on Escape, and return focus to the button. Locking
body scroll is optional only if the panel covers the viewport; do not trap focus for
a simple inline navigation panel.

- [ ] **Step 4: Run tests and commit**

```powershell
cd web
npm.cmd test -- accessibility-behavior.test.tsx
npm.cmd run lint
git add web/components/charts web/components/evidence/evidence-navigation.tsx web/components/shell/mobile-navigation.tsx web/components/ui web/tests/accessibility-behavior.test.tsx
git commit -m "fix: complete keyboard and accessible data behavior"
```

### Task 20: Responsive And Visual Polish Pass

**Files:**
- Modify: `web/app/globals.css`
- Modify: page components only where markup changes are required
- Create: `docs/dashboard-responsive-checklist.md`

- [ ] **Step 1: Define required viewport checks**

Document and verify:

- 1440×900 presentation laptop;
- 1024×768 tablet;
- 768×1024 portrait tablet;
- 390×844 mobile; and
- 320×568 narrow mobile.

- [ ] **Step 2: Fix structural responsive behavior**

Required outcomes:

- landing flow stacks without horizontal scrolling;
- demo controls remain visible and ordered;
- data tables have a mobile summary mode or controlled horizontal scroll;
- sidebar collapses at tablet width;
- patient probability labels do not truncate critical names;
- capacity controls remain at least 44px high;
- no heading or badge overflows at 200% zoom.

- [ ] **Step 3: Verify color and semantic consistency**

Check:

- body and muted text meet WCAG AA;
- semantic colors retain text/icon labels;
- routine patient never appears urgent;
- FULL research track cannot visually resemble the primary deployment track;
- warnings use readable text, not color alone.

- [ ] **Step 4: Verify motion**

Remove decorative page-load staggering from dense operational pages. Retain only
state transitions under 250ms and preserve the existing reduced-motion override.

- [ ] **Step 5: Run lint and tests**

```powershell
cd web
npm.cmd test
npm.cmd run lint
```

- [ ] **Step 6: Commit**

```powershell
git add web/app/globals.css web/app web/components docs/dashboard-responsive-checklist.md
git commit -m "style: polish dashboard responsiveness and hierarchy"
```

### Task 21: Align README, Pitch, Route Guide, And Canonical Metrics

**Files:**
- Modify: `README.md`
- Modify: `outputs/reports/final_judge_pitch.md`
- Modify: `outputs/reports/presentation_outline.md`
- Create: `docs/dashboard-demo-guide.md`
- Create: `docs/dashboard-data-contract.md`
- Modify: `open_dashboard.bat`

- [ ] **Step 1: Update the route and feature guide**

README must describe:

- landing page;
- guided demo;
- command center;
- patient review;
- batch intake capability by deployment mode;
- resource scenarios;
- Trust Center; and
- methodology.

- [ ] **Step 2: Write the judge demo guide**

The guide contains exact steps and fallback language:

1. Open `/demo?step=cohort`.
2. Advance through all five steps.
3. Open the urgent case.
4. Switch to high uncertainty.
5. Apply the safety-first resource preset.
6. Close with Trust Center generalization limits.

Include expected canonical values by reading the manifest during release, not by
copying quick-smoke numbers.

- [ ] **Step 3: Align claims**

Remove or qualify any claim not implemented. Explicitly distinguish:

- public static schema preview;
- local/controlled saved-model inference;
- held-out metrics;
- full-cohort OOF patient records;
- simulated resource outcomes.

- [ ] **Step 4: Update launcher behavior**

Open the landing page by default. Add console text showing:

```text
Landing page: http://localhost:3000
Command center: http://localhost:3000/command-center
Guided demo: http://localhost:3000/demo
```

- [ ] **Step 5: Commit**

```powershell
git add README.md outputs/reports/final_judge_pitch.md outputs/reports/presentation_outline.md docs/dashboard-demo-guide.md docs/dashboard-data-contract.md open_dashboard.bat
git commit -m "docs: align dashboard demo and competition claims"
```

### Task 22: Final Verification And Release Gate

**Files:**
- Modify only files required by failures found in this task
- Create: `outputs/reports/dashboard_release_verification.md`

- [ ] **Step 1: Regenerate canonical artifacts**

Run the full pipeline, not quick smoke:

```powershell
python run_pipeline.py
python scripts/export_web_data.py --require-canonical
```

Expected: schema-v2 artifacts with `canonical: true`.

- [ ] **Step 2: Run Python verification**

```powershell
pytest tests/test_web_export.py tests/test_web_inference.py -q
```

Expected: PASS.

- [ ] **Step 3: Run frontend verification**

```powershell
cd web
npm.cmd test
npm.cmd run lint
npm.cmd run build
```

Expected: all tests PASS, lint exits 0, and every route statically builds unless
explicitly documented as connected-mode only.

- [ ] **Step 4: Perform route-by-route smoke review**

Review:

- `/`
- `/demo?step=cohort`
- `/demo?step=leakage`
- `/demo?step=patient`
- `/demo?step=uncertainty`
- `/demo?step=resources`
- `/command-center`
- `/patients`
- `/patients?case=invalid`
- `/intake`
- `/resources?preset=safety`
- `/evidence?section=generalization`
- `/methodology`

For every route, record desktop, tablet, mobile, keyboard, empty/error state, and
canonical provenance result.

- [ ] **Step 5: Verify cross-artifact metric consistency**

Compare the dashboard manifest and headline values with:

- final notebook;
- technical report;
- final judge pitch; and
- presentation outline.

Fail release if the same metric has different values without an explicit evaluation
mode or run label.

- [ ] **Step 6: Write release verification report**

Record exact command results, canonical run ID, routes reviewed, known limitations,
and whether public live inference is enabled.

- [ ] **Step 7: Commit**

```powershell
git add outputs/reports/dashboard_release_verification.md web/public/data README.md outputs/reports
git commit -m "test: verify VECTRA-X dashboard release"
```

## Acceptance Checklist By Page

### Landing `/`

- [ ] Project purpose understood within one minute.
- [ ] Guided demo and command center are the two dominant actions.
- [ ] Canonical evidence and limitations appear before the final CTA.
- [ ] No operational sidebar.

### Guided Demo `/demo`

- [ ] Five shareable steps.
- [ ] Previous, next, and workspace links.
- [ ] Leakage and limitations cannot be skipped visually.
- [ ] Works without requiring free exploration.

### Command Center `/command-center`

- [ ] Situation, action queue, and resource pressure are immediately visible.
- [ ] Result counts, pagination, clear filters, and empty state work.
- [ ] Provenance is visible.

### Patient Review `/patients`

- [ ] Per-label thresholds are correct.
- [ ] Category tone is correct.
- [ ] Multi-label prediction and co-infection detector are distinguished.
- [ ] Unknown case and print report work.

### Batch Intake `/intake`

- [ ] Schema validation precedes inference.
- [ ] PRE_LAB is default and FULL is unavailable.
- [ ] Public static limitations are explicit.
- [ ] Results can be exported without private fields.

### Resource Scenarios `/resources`

- [ ] Shortfall semantics are non-negative and clear.
- [ ] Allocation has three states.
- [ ] Presets, numeric input, reset, and comparison work.
- [ ] Assumptions are visible.

### Trust Center `/evidence`

- [ ] Organized around six questions.
- [ ] Confidence intervals and support are shown.
- [ ] Typhoid and center-transfer failures are prominent.
- [ ] Every section includes a claim boundary.

### Methodology `/methodology`

- [ ] All major methods and assumptions are documented.
- [ ] Glossary terms are directly linkable.
- [ ] Contextual links from workspace pages resolve correctly.

## Recommended Execution Order

Execute Tasks 1–4 before any page work. Tasks 5–14 may then proceed in order, with
Tasks 15–17 treated as a separate inference subproject if model bundles need pipeline
changes. Finish with Tasks 18–22 as a single release-hardening sequence.
