# VECTRA-X Locked Evidence And Live Assessment

The `web/` directory is the maintained public dashboard for VECTRA-X. It preserves
the existing landing page, guided demo, analytics views, and deterministic resource
simulator while sourcing scientific claims from the final competition notebook.

The evidence layer is static. The live assessment uses the exact exported
joblib pipeline through a small Python API. Assessment values are anonymous,
not persisted, not written to browser storage, and never logged as request bodies.

## Data Contract

```text
web/data/evidence.json       Release-backed scientific evidence
web/data/input-schema.json   Deployable field contract, never patient values
web/data/demo-cases.json     Anonymous synthetic demonstrations
web/data/manifest.json       Run, policy, model, document, and figure hashes
web/model/                  Exact locked model bundles
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

The exporter reads only `outputs/releases/latest.json` and its referenced,
hash-verified scientific release. Historical CSVs and stale figures cannot
influence the public build.

## Run Locally

Browsers block JSON loading over `file://`, so serve the folder over HTTP:

```bash
python web/serve_live.py --port 4173
```

Open `http://localhost:4173`. The run ID must match `outputs/releases/latest.json`.

## Test

```bash
npm test
npm run check
npm run test:browser
```

The optional browser smoke test requires its browser automation dependency.

## Deploy to Vercel

Use `web/` as the Vercel project root:

- Framework preset: Other
- Build command: none
- Output directory: `.`

Production use remains blocked. Before public deployment, enable platform rate
limiting, retain the 64 KiB request limit, preserve `Cache-Control: no-store`,
and pass both release validators. The competition prototype makes no diagnosis,
treatment, discharge, or measured-impact claim.
