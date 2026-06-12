# VECTRA-X — Static Web Dashboard (Vercel-ready)

A **zero-backend** static dashboard for the VECTRA-X clinical triage system. It
fetches the precomputed pipeline artifacts (`data/dashboard.json`,
`data/patients.json`) and renders 10 interactive sections with Chart.js + the
generated figures. Because there is no server, it deploys to **Vercel** (or any
static host) as-is.

> The Streamlit app (`../app/streamlit_app.py`) is the *local* interactive
> version. Streamlit needs a long-running Python/WebSocket server and **cannot**
> run on Vercel — this static site is the Vercel-deployable counterpart.

## Folder

```
web/
├── index.html          # shell (sidebar + section containers)
├── assets/
│   ├── styles.css      # design system (clinical dark/teal theme)
│   └── app.js          # data load, navigation, tables, Chart.js charts
├── data/
│   ├── dashboard.json  # metrics + all summary tables
│   └── patients.json   # 300 patient-level predictions (explorer/triage)
├── figures/            # PNGs copied from outputs/figures
└── vercel.json         # static caching + cleanUrls config
```

## Regenerate the data

From the project root, after training:

```bash
py run_pipeline.py        # produces outputs/*
py export_web_data.py     # builds web/data/*.json and copies web/figures/*
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
