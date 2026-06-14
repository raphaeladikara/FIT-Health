# VECTRA-X Static Dashboard

The `web/` directory is the maintained public dashboard for VECTRA-X. It preserves
the existing landing page, guided demo, analytics views, and deterministic resource
simulator while sourcing scientific claims from the final competition notebook.

The application is fully static: it runs no model, stores no patient data, and
requires no backend.

## Data Contract

```text
web/data/dashboard.json   Aggregate final evidence and scenario inputs
web/data/demo-cases.json  At most 12 curated anonymous demonstrations
web/data/manifest.json    Canonical run and source provenance
web/figures/              Static explanatory figures
```

The public bundle contains no UUID, ground truth, or FULL target-restating model
results. PRE_LAB and LAB_AWARE frozen-test results are reported separately. Exact
and pragmatic empirical inclusion-set policies are also separated.

## Regenerate and Validate

Execute the final notebook or full canonical pipeline first, then:

```bash
python export_web_data.py
python scripts/validate_web_bundle.py
```

The exporter reads corrected `outputs/tables/final_*.csv` evidence and retains the
curated anonymous case fixture.

## Run Locally

Browsers block JSON loading over `file://`, so serve the folder over HTTP:

```bash
cd web
python -m http.server 8765
```

Open `http://localhost:8765`. On Windows, `open_dashboard.bat` provides the same
workflow.

## Test

```bash
npm test
npm run check
```

The optional browser smoke test requires its browser automation dependency.

## Deploy to Vercel

Use `web/` as the Vercel project root:

- Framework preset: Other
- Build command: none
- Output directory: `.`

Commit `web/data/*.json` and `web/figures/*.png`; the deployment has no server-side
generation step.
