# VECTRA-X

**A Multi-label, Explainable, and Uncertainty-Aware Clinical Triage Intelligence System for Vector-Borne Disease Response**

FIT Competition 2026 — Track IV: AI-based Vector-Borne Disease Prediction.

> *Prediction is not enough. In humanitarian health response, the model must know when
> it is uncertain, explain why, and help prioritise action.*

---

## 1. What this is

VECTRA-X reframes a deceptively simple disease-prediction dataset (300 patients ×
109 variables, 2 health centers) into a **stage-aware, multi-label, uncertainty-aware
triage system**. Instead of a single black-box classifier, it provides:

- a **pre-lab triage** model (demographics + symptoms + vitals — the honest,
  deployable model) and a separate **lab-aware confirmation** model;
- an explicit **diagnostic-leakage audit** that splits features by clinical stage;
- **co-infection** detection (>50% of patients carry more than one diagnosis);
- **calibrated probabilities**, **conformal prediction sets**, and patient
  **uncertainty** levels;
- **explainability** (permutation importance + local logistic attributions + optional SHAP);
- a **fairness / center-robustness** audit (incl. leave-one-center-out);
- a **triage priority engine** (4 tiers + decision-support actions) and a **resource
  simulation**;
- a **Streamlit dashboard** (10 pages).

## 2. Project objective

Build a reproducible, research- and product-grade decision-support system for
triaging vector-borne disease patients that is **clinically honest about what is
knowable before laboratory confirmation**, robust under severe class imbalance, and
transparent about uncertainty and fairness.

## 3. Repository layout

```
vectra_x_project/
├── config/config.yaml            # all paths, label/leakage/preprocessing/model settings
├── data/
│   ├── raw/                       # data.csv + desciption.xlsx (official, untouched)
│   ├── interim/                   # cleaned snapshot
│   └── processed/                 # y_multilabel + X_pre_lab / X_lab_aware / X_full / X_features_raw
├── notebooks/
│   ├── 01_data_audit_eda.ipynb
│   ├── 02_modeling_multilabel.ipynb
│   └── 03_explainability_uncertainty_triage.ipynb
├── src/                           # 14 single-responsibility modules (see below)
├── outputs/
│   ├── figures/  tables/  models/  reports/  dashboard_data/
├── app/streamlit_app.py           # 10-page Streamlit dashboard (local)
├── web/                           # static, Vercel-ready dashboard (no backend)
│   ├── index.html  assets/{styles.css,app.js}  data/*.json  figures/*.png  vercel.json
├── open_dashboard.bat             # one-click: serve web/ locally + open browser
├── run_pipeline.py                # end-to-end orchestrator (also builds web/ bundle)
├── export_web_data.py             # builds web/data/*.json + copies figures
├── requirements.txt
└── README.md
```

`src/` modules: `data_loader`, `schema_audit`, `label_detection`, `leakage_audit`,
`preprocessing`, `modeling`, `evaluation`, `calibration`, `conformal`,
`explainability`, `fairness`, `triage_engine`, `visualization`, `report_utils`.

## 4. Environment setup

Requires **Python 3.10+** (developed on 3.12, Windows 11).

```bash
cd vectra_x_project
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
```

The official data files must be present at `data/raw/data.csv` and
`data/raw/desciption.xlsx` (already included).

## 5. Run the pipeline

```bash
python run_pipeline.py            # full run (RANDOM_STATE = 42, ~6–8 min)
python run_pipeline.py --quick    # fewer permutation-importance repeats (faster)
python run_pipeline.py --use-cache  # reuse cached CV leaderboard (debugging)
```

This regenerates every table, figure, model, and programmatic report. The pipeline is
deterministic.

## 6. Launch the dashboard

There are **two** dashboards — both load precomputed artifacts (no retraining):

**A. Static web dashboard (Vercel-ready) — recommended for sharing**
A zero-backend single-page app under `web/` (clinical dark/teal theme, Chart.js,
interactive patient lookup). `run_pipeline.py` auto-builds its data bundle via
`export_web_data.py`.
```bash
# one-click on Windows (starts a local server + opens the browser):
open_dashboard.bat
# or manually:
py export_web_data.py        # if you haven't run the full pipeline
cd web && py -m http.server 8765   # then open http://localhost:8765
```
Deploy to **Vercel**: set the project **Root Directory** to `vectra_x_project/web`
(framework = Other, no build step) — see `web/README.md`. A local server is needed
because browsers block `fetch()` over `file://`.

**B. Streamlit app (local interactive)**
```bash
streamlit run app/streamlit_app.py
```
Streamlit needs a long-running Python server and **cannot** run on Vercel — the
`web/` static site is the Vercel-deployable counterpart.

## 7. Outputs generated

- **Reports** (`outputs/reports/`): blueprint execution summary, data audit, leakage
  audit, EDA insights, modeling summary, threshold strategy, calibration, uncertainty,
  conformal, explainability, fairness, triage, resource, **final technical report
  draft**, presentation outline, jury Q&A bank, limitations & ethics.
- **Tables** (`outputs/tables/`, ~27 CSVs): leaderboard, per-label metrics, threshold
  optimisation & policies, calibration, conformal, fairness, feature importance,
  patient-level predictions, triage dashboard data, resource simulation, etc.
- **Figures** (`outputs/figures/`, ~26 PNGs): target/cardinality/co-occurrence,
  missingness, leaderboard, per-label F1/recall, ROC/PR, confusion, calibration,
  uncertainty, importance, SHAP, fairness, resource.
- **Models** (`outputs/models/`): `pre_lab_model.joblib`, `lab_aware_model.joblib`
  (each bundles the fitted binary-relevance model, labels, thresholds, feature set).
- **Processed data** (`data/processed/`): `y_multilabel.csv`, `X_pre_lab.csv`,
  `X_lab_aware.csv`, `X_full.csv`, `X_features_raw.csv`.

## 8. Key results (held-out test, reproducible)

| Track | Best model | macro-F1 | micro-F1 | macro-PR-AUC |
|---|---|---|---|---|
| **PRE_LAB (deploy this)** | Extra Trees | 0.65 | 0.84 | 0.61 |
| LAB_AWARE (after tests) | XGBoost | 0.56 | 0.81 | 0.57 |
| FULL (leakage demo only) | HistGB | 0.70 | 0.89 | 0.68 |

Co-infection detector: ROC-AUC 0.86. Conformal: 94.8% empirical coverage, avg set size
2.9. The large FULL-track gain is a **leakage artefact** (the *Dengue (Dengua)* feature
restates the dengue outcome — dengue F1 rises 0.57 → 0.92) and is **not** deployable.

## 9. Important assumptions

- The task is **multi-label** (158/300 patients have >1 diagnosis), not multi-class.
- Five labels are active; **chikungunya, zika, option 8 have zero positives** and are
  excluded from scoring.
- Missing values mean *unknown*, never *negative*; they are kept with `__missing`
  indicator flags. Constant columns are dropped **with logging**.
- No patient timestamp/coordinate exists → **external data is supplementary only**
  (literature/context/dashboard), never merged into patient-level training.

## 10. ⚠️ Leakage warning

The dataset contains diagnostic-test / current-disease features (*Dengue (Dengua)*,
*Test TDR*, *Goutte épaisse*, and the diagnosis label columns themselves). These are
**never** used by the pre-lab triage model. `outputs/reports/leakage_audit.md` and
`outputs/tables/leakage_candidates.csv` document every decision. Any model that
includes the leakage features will look excellent and be clinically worthless at
triage time.

## 11. Model limitations

Small sample (n=300), severe imbalance, rare-label metrics are estimates,
center-to-center shift (leave-one-center-out macro-F1 ≈ 0.38), and conformal coverage
for rare labels is approximate. **VECTRA-X is decision support, not a diagnostic
authority** — see `outputs/reports/limitations_and_ethics.md`.
