# VECTRA-X Next.js Command Center Design

## Purpose

Replace the Streamlit presentation layer with a production-shaped, Vercel-deployable
Next.js application called the VECTRA-X Outbreak Triage Command Center.

The application must work both as a memorable FIT Competition demonstration and as
a credible implementation reference for frontline health and humanitarian response
workflows. It remains decision support, not a diagnostic authority.

## Selected Architecture

VECTRA-X uses a static-first split:

1. The existing Python pipeline remains the source of truth for training, evaluation,
   calibration, conformal prediction, explainability, fairness, triage, and resource
   outputs.
2. `scripts/export_web_data.py` validates and converts approved outputs into
   privacy-safe JSON under `web/public/data/`.
3. A Next.js App Router application under `web/` renders those artifacts.
4. Resource-allocation what-if calculations run in the browser against precomputed,
   de-identified patient records.
5. Vercel serves the statically generated application. It does not run Python,
   retrain models, accept CSV uploads, or persist patient data.

This architecture avoids a deployment-time Python service while preserving a clean
future boundary for an authenticated inference API.

## Product Boundaries

### Included

- Cohort command overview and ranked triage queue.
- Anonymous patient exploration and curated representative scenarios.
- Per-disease calibrated probabilities.
- Confidence, entropy-based uncertainty, conformal caution sets, and co-infection risk.
- Four operational triage tiers and recommended human actions.
- Interactive capacity and rapid-test allocation simulation.
- Model performance, false-negative, calibration, conformal, fairness, center-transfer,
  explainability, and leakage evidence.
- Responsive desktop, tablet, and mobile layouts.
- Privacy-safe CSV export of current queues.
- Static Vercel deployment and a Windows local-development launcher.

### Excluded

- CSV upload.
- Live patient inference.
- Authentication, database storage, audit logs, or clinical-system integration.
- Model training or heavy numerical processing in Next.js.
- Claims of diagnosis or real-world clinical validation.

## Information Architecture

### `/` - Command Center

- Operational status header and safety context.
- Five high-value indicators: total cases, urgent response, confirmatory-test priority,
  high uncertainty, and potential co-infection.
- Ranked triage queue with search and priority filtering.
- Priority action list for cases requiring immediate review.
- Triage-demand and uncertainty-demand visual summaries.
- Capacity snapshot linking to the resource simulator.

### `/patients` - Patient Intelligence

- Representative scenario shortcuts: highest priority, high uncertainty,
  potential co-infection, and routine monitoring.
- Searchable anonymous case selector.
- Triage status, score, uncertainty, co-infection risk, and caution-set size.
- Calibrated per-disease probability visualization with thresholds.
- Decision-support record separating prediction, uncertainty, priority, and action.
- Local explanation panel when patient-level explanation data is available.
- Clear fallback copy when only global explanation evidence is available.

### `/resources` - Resource Allocation

- Controls for rapid tests, beds, monitoring slots, and staff-review slots.
- Demand, capacity, gap, and status per resource.
- Prioritized confirmatory-test queue with allocated or waiting state.
- Summary of which cases are displaced when capacity changes.
- Threshold-policy burden comparison.
- Privacy-safe queue download.

### `/evidence` - Trust and Evidence

- Held-out PRE_LAB headline metrics.
- Model and track comparison.
- Per-label support, precision, recall, F1, false negatives, and confidence intervals.
- Calibration and conformal reliability evidence.
- Fairness diagnostics by available demographic and health-center axes.
- Leave-one-center-out transfer stress test.
- Global feature importance and leakage controls.
- Explanatory text that translates metrics into operational implications.

### `/methodology` - Methodology and Limitations

- Clinical-stage feature model.
- Multi-label framing.
- Validation and threshold strategy.
- Leakage audit.
- Known limitations, ethics, prospective-validation requirement, and artifact provenance.

## Navigation

- Desktop uses a persistent 248-pixel side navigation with one icon family and visible
  labels.
- The current route is indicated by background, text, icon, and an accessible
  `aria-current` state, never color alone.
- Tablet collapses the rail to an icon-first variant.
- Mobile replaces the rail with a top bar and accessible navigation sheet.
- Every workspace has a stable URL and can be opened directly during judging.

## Data Contract

`scripts/export_web_data.py` produces:

- `manifest.json`: schema version, generation time, execution profile, source-artifact
  status, and public record counts.
- `summary.json`: project shape, labels, metrics, conformal results, co-infection
  results, uncertainty counts, and triage distribution.
- `patients.json`: de-identified patient decision-support records with generated
  `case_id`; no UUID or ground-truth label.
- `evidence.json`: approved leaderboard, per-label metrics, calibration, conformal,
  fairness, center-transfer, feature importance, leakage, confidence interval, and
  threshold-policy tables.

All numeric values are emitted as JSON numbers where possible. Missing optional
artifacts become empty arrays plus manifest warnings. Missing required patient or
summary artifacts fail export with one actionable error.

The browser validates the schema version and displays an artifact-error state rather
than rendering misleading empty charts.

## Resource Allocation Rules

- Rapid-test demand includes Confirmatory Test Priority and Urgent Response Priority.
- Bed demand includes Urgent Response Priority.
- Monitoring demand includes Clinical Review and Confirmatory Test Priority.
- Staff-review demand includes Clinical Review, Confirmatory Test Priority, and Urgent
  Response Priority, plus high-uncertainty cases.
- Test allocation ranks cases by triage score, then co-infection probability, then
  stable case ID.
- The simulator changes allocation state only. It never recalculates disease
  probabilities or presents capacity changes as model evidence.

## Visual System

### Physical scene

The primary operator uses the interface on a shared laptop in a bright field office
or judging room, scanning quickly while discussing limited tests and referral
capacity. This favors a light, high-contrast operational surface rather than a
decorative dark interface.

### Direction

- Restrained clinical operations UI with a cool near-white canvas and deep ink text.
- Cyan-blue is reserved for navigation, focus, links, and selected controls.
- Teal communicates sufficient capacity and routine status.
- Amber and orange communicate review and testing needs.
- Red communicates urgent response and destructive/error states.
- Violet is reserved for co-infection evidence.
- Status always includes text or an icon in addition to color.
- The interface avoids glassmorphism, gradient text, excessive card grids, oversized
  radii, decorative animation, and consumer-diagnostic styling.

### Typography

- Inter Variable is the single interface family.
- Tabular figures are enabled for metrics and table columns.
- Fixed product type scale: 12, 14, 16, 18, 24, and 32 pixels.
- Body text remains at least 16 pixels on mobile.

### Components

- Application shell and responsive navigation.
- Page header and context strip.
- Metric strip with varied widths rather than identical card grids.
- Status badge with icon and visible text.
- Data table with responsive compact-card fallback.
- Probability bars with labels, percentages, and threshold markers.
- Capacity controls and capacity ledger.
- Chart panel with adjacent textual insight.
- Safety callout and artifact-status callout.
- Empty, loading, and error states.

### Motion

- State transitions use 150-220 ms ease-out motion.
- Navigation and filter changes use opacity or transform only.
- Charts do not replay decorative entrance animations on every state change.
- `prefers-reduced-motion` removes nonessential transitions.

## Accessibility

- WCAG 2.1 AA contrast targets.
- Skip link and semantic landmarks.
- Sequential heading hierarchy.
- Visible focus states.
- Controls have explicit labels and minimum 44-pixel targets.
- Tables remain keyboard accessible.
- Chart regions include concise text summaries.
- No state is communicated by color alone.
- Mobile layouts do not require horizontal page scrolling.

## Technical Stack

- Next.js App Router and TypeScript.
- React Server Components by default; client components only for filters, patient
  selection, simulator controls, and interactive charts.
- Tailwind CSS for tokens and layout.
- Lucide React for a consistent SVG icon set.
- Recharts for accessible, responsive data visualization.
- Zod for public-data validation.
- Vitest and Testing Library for unit and component behavior.
- ESLint and the Next.js production build as release gates.

## File Structure

```text
web/
  app/
    layout.tsx
    page.tsx
    patients/page.tsx
    resources/page.tsx
    evidence/page.tsx
    methodology/page.tsx
    globals.css
  components/
    shell/
    command-center/
    patients/
    resources/
    evidence/
    ui/
  lib/
    data.ts
    resource-allocation.ts
    schema.ts
    types.ts
    format.ts
  public/data/
  tests/
  package.json
  next.config.ts
  tsconfig.json
  vitest.config.ts
  vercel.json
scripts/export_web_data.py
```

Files are split by product responsibility rather than placed in one dashboard page.

## Streamlit Removal

- Delete `app/` and `.streamlit/`.
- Remove Streamlit from Python requirements.
- Delete Streamlit-specific tests and specifications that are no longer authoritative.
- Remove Streamlit launch and usage text from README and related product documentation.
- Preserve reusable pipeline, outputs, models, notebooks, reports, and Python tests.

## Windows Launcher

`open_dashboard.bat` will:

1. Resolve and enter the repository root.
2. Confirm `web/package.json` exists.
3. Find `npm.cmd`.
4. Install dependencies when `web/node_modules` is missing.
5. Export public web data when required JSON is missing, using the available Python
   3.12 runtime.
6. Start `npm run dev` in `web/`.
7. Open `http://localhost:3000` after a brief wait.
8. Pass additional arguments to the Next.js development command.
9. Keep actionable error output visible.
10. Support `VECTRA_X_LAUNCHER_TEST=1` without starting a server.

## Testing and Verification

- Python export tests verify privacy stripping, required artifacts, optional warnings,
  JSON types, and stable allocation inputs.
- TypeScript unit tests verify label parsing, patient selection, capacity calculation,
  deterministic ranking, and schema rejection.
- Component tests verify navigation semantics, filters, simulator updates, safety
  language, and empty/error states.
- `npm test`, `npm run lint`, and `npm run build` must pass.
- The local application is inspected at desktop and mobile viewport sizes.
- No completion claim is made without a fresh build and test run.

## Deployment

- Vercel project root is `web`.
- The application uses static artifact files committed under `web/public/data`.
- No secrets or environment variables are required for the public prototype.
- `npm run build` is the build command.
- A future authenticated inference service may be configured through a separate API
  origin without changing the public artifact contract.

## Completion Criteria

- All five routes work directly and through navigation.
- The four required product workspaces are complete.
- Patient data is de-identified in every public artifact and download.
- Resource controls deterministically update allocation and shortage states.
- Trust panels expose uncertainty, fairness, robustness, explainability, and leakage.
- Streamlit infrastructure and documentation are removed.
- `open_dashboard.bat` launches the Next.js app.
- Tests, lint, and production build pass.
- Desktop and mobile browser inspection reveals no blocking layout or interaction issue.
