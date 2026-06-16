# VECTRA-X Integrated Operational Prototype

The `web/` directory is the maintained public implementation prototype for VECTRA-X.
It preserves the landing page, guided demo, analytics views, and visual identity while
adding an end-to-end workspace from anonymous intake through response projection.

The evidence layer is static. The live assessment uses the exact exported
joblib pipeline through a small Python API. Assessment values are anonymous,
not persisted, not written to browser storage, and never logged as request bodies.

## Data Contract

```text
web/data/evidence.json       Release-backed scientific evidence
web/data/input-schema.json   Deployable field contract, never patient values
web/data/demo-cases.json     Anonymous synthetic demonstrations
web/data/manifest.json       Run, policy, model, document, and figure hashes
web/model/                   Exact locked model bundles
```

Public schema `3.1.0` includes the notebook hash, analysis policy ID, primary-track
summary, release-backed narrative, rare-label summary, and center-transfer warning.
The bundle contains no UUID, patient identifier, ground truth, or research-only
target-restating features.

## Operational Workspace

`prototype.html` is the report-ready workflow:

1. Anonymous case intake with range validation and availability-stage filtering.
2. Locked joblib model assessment with calibration, thresholds, support, uncertainty,
   prediction set, and abstention.
3. Operational review and confirmatory-test routing without diagnosis or treatment.
4. Assumption-bound response projection for review, tests, urgent capacity, and unmet
   demand.

Deterministic states for demonstrations and technical-report screenshots:

```text
prototype.html?case=SYNTH-LOW-UNCERTAINTY&stage=assessment
prototype.html?case=SYNTH-MISSING&stage=decision
prototype.html?case=SYNTH-OOD&stage=response
```

Each state includes a figure title, “what this demonstrates” caption, evidence scope,
and provenance. Print CSS only simplifies capture layout.

## Regenerate and Validate

Execute the final notebook or full canonical pipeline first, then:

```bash
python export_web_data.py
python scripts/validate_notebook_release_parity.py
python scripts/validate_web_bundle.py
```

The exporter reads only `outputs/releases/latest.json` and its referenced,
hash-verified scientific release. Historical CSVs and stale figures cannot
influence the public build.

## Run Locally

Browsers block JSON loading over `file://`, so serve the folder over HTTP:

```bash
python web/serve_live.py --port 4173
```

Open `http://localhost:4173/prototype.html`. The run ID must match
`outputs/releases/latest.json`.

From the repository root on Windows, `open_dashboard.bat` starts this same live
server and opens `http://127.0.0.1:4173/index.html` for the landing page.

## Test

```bash
npm test
npm run check
npm run test:browser
```

The browser smoke covers desktop/mobile layout, keyboard focus, deterministic
synthetic flows, OOD/abstention, capacity overload, API failure, and dashboard routes.

## Deploy to Vercel

Use `web/` as the Vercel project root:

- Framework preset: Other
- Build command: none
- Output directory: `.`

Production use remains blocked. Before public deployment, enable platform rate
limiting, retain the 64 KiB request limit, preserve `Cache-Control: no-store`,
and pass the notebook-release-web parity and public-bundle validators. The competition
prototype makes no diagnosis, treatment, discharge, or measured-impact claim.
