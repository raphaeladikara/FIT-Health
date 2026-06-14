# VECTRA-X — Static Web Dashboard (Vercel-ready)

A **zero-backend** public decision-support prototype for VECTRA-X. It separates the
experience into a product landing page, a five-step guided demo, and a deeper
analytics dashboard. Public case data is curated and anonymized; UUIDs and recorded
ground-truth labels are not published.

> The Streamlit app (`../app/streamlit_app.py`) is the *local* interactive
> version. Streamlit needs a long-running Python/WebSocket server and **cannot**
> run on Vercel — this static site is the Vercel-deployable counterpart.

## Folder

```
web/
├── index.html          # product landing page
├── demo.html           # guided five-step walkthrough
├── dashboard.html      # analytical dashboard
├── assets/             # local CSS and JavaScript modules
├── data/
│   ├── dashboard.json  # aggregate metrics and evidence
│   ├── demo-cases.json # maximum 12 curated public cases
│   └── manifest.json   # canonical run provenance
├── figures/            # PNGs copied from outputs/figures
└── vercel.json         # static caching + cleanUrls config
```

## Regenerate the data

From the project root, after training:

```bash
py run_pipeline.py        # produces outputs/*
py export_web_data.py
py scripts/validate_web_bundle.py
```

## Run locally

Browsers block `fetch()` over `file://`, so serve over HTTP:

- **Easiest:** double-click `../open_dashboard.bat` (starts a local server + opens the browser).
- **Manual:**
  ```bash
  cd web
  py -m http.server 8765
  # open http://localhost:8765
  ```

## Deploy to Vercel

The `web/` folder is the deployable root (pure static — no build step).

**Option A — CLI**
```bash
npm i -g vercel
cd web
vercel            # preview
vercel --prod     # production
```

**Option B — Git import (vercel.com)**
1. Import the repository.
2. Set **Root Directory** = `vectra_x_project/web`.
3. Framework preset = **Other**; Build command = *(none)*; Output dir = *(leave default / `.`)*.
4. Deploy.

Commit `web/data/*.json` and `web/figures/*.png` so Vercel has the artifacts
(they are produced by `export_web_data.py`).
