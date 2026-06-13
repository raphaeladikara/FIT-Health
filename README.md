# VECTRA-X

**A Multi-label, Explainable, and Uncertainty-Aware Clinical Triage Intelligence
System for Vector-Borne Disease Response**

FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction.

> Prediction is not enough. In humanitarian health response, the model must know when
> it is uncertain, explain why, and help prioritize action.

## What This Is

VECTRA-X turns a 300-patient, 109-variable dataset from two health centers into a
stage-aware clinical triage decision-support system. It provides:

- a deployable **PRE_LAB** triage model and separate LAB_AWARE confirmation track;
- an explicit diagnostic-leakage audit;
- multi-label and co-infection modeling;
- calibrated probabilities and conformal caution sets;
- patient uncertainty;
- global and local explainability artifacts;
- fairness and leave-one-center-out robustness diagnostics;
- four operational triage tiers and resource-capacity simulation;
- a privacy-safe **Next.js Outbreak Triage Command Center** deployable to Vercel.

VECTRA-X supports medical review. It does not provide a confirmed diagnosis and does
not replace qualified healthcare professionals.

## Repository Layout

```text
vectra_x_project/
|-- config/config.yaml
|-- data/
|   |-- raw/
|   |-- interim/
|   `-- processed/
|-- notebooks/
|-- src/
|-- outputs/
|-- scripts/
|   |-- build_final_notebook.py
|   |-- build_technical_report.py
|   `-- export_web_data.py
|-- web/                         # Next.js command center
|-- tests/
|-- open_dashboard.bat
|-- run_pipeline.py
|-- requirements.txt
`-- README.md
```

The Python pipeline is the analytical source of truth. The web application consumes
only exported, de-identified JSON artifacts.

## Requirements

- Python 3.10 or newer, developed with Python 3.12.
- Node.js 20 or newer.
- Windows, macOS, or Linux for the pipeline and web app.

Install Python dependencies:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install web dependencies:

```bash
cd web
npm install
```

## Run the Pipeline

The official input files are already located at:

- `data/raw/data.csv`
- `data/raw/desciption.xlsx`

Run:

```bash
python run_pipeline.py
python run_pipeline.py --quick
python run_pipeline.py --use-cache
```

The pipeline is deterministic with `RANDOM_STATE = 42` and regenerates the model,
table, figure, report, and dashboard artifacts under `outputs/`.

## Launch the Command Center

Export privacy-safe public artifacts:

```bash
python scripts/export_web_data.py
```

Start Next.js:

```bash
cd web
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

On Windows, double-click `open_dashboard.bat`. The launcher:

1. checks Node.js and npm;
2. installs web dependencies when needed;
3. exports public data when it is missing;
4. starts the Next.js development server;
5. opens the command center in the default browser.

### Workspaces

- **Command Center**: operational indicators, ranked triage queue, immediate actions,
  triage demand, uncertainty burden, and capacity interpretation.
- **Patient Intelligence**: representative cases, calibrated disease probabilities,
  conformal caution sets, uncertainty, co-infection risk, and recommended action.
- **Resource Allocation**: rapid-test, bed, monitoring, and staff-review capacity;
  deterministic prioritized allocation; threshold-policy burden.
- **Trust & Evidence**: held-out metrics, false negatives, calibration, conformal
  coverage, fairness, center transfer, explainability, and leakage controls.
- **Methodology**: multi-label framing, clinical-stage controls, validation,
  uncertainty, limitations, and ethics.

The public web artifacts contain generated case IDs, never source UUIDs or
ground-truth diagnosis labels.

## Test and Build the Web App

```bash
cd web
npm test
npm run lint
npm run build
```

The production build statically prerenders every route.

## Deploy to Vercel

1. Import the repository in Vercel.
2. Set **Root Directory** to `web`.
3. Keep the Next.js framework preset.
4. Use `npm run build`.
5. Deploy.

The public prototype requires no secret, database, Python runtime, or serverless
inference function. Commit `web/public/data/*.json` whenever pipeline evidence is
refreshed.

## Final Competition Notebook

Generate or refresh the notebook:

```bash
python scripts/build_final_notebook.py
```

Execute the artifact-backed notebook:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/VECTRA_X_Final_Competition_Notebook.ipynb --ExecutePreprocessor.timeout=900
```

Execute with a deterministic full pipeline rebuild:

```powershell
$env:VECTRA_X_RECOMPUTE="1"
jupyter nbconvert --to notebook --execute --inplace notebooks/VECTRA_X_Final_Competition_Notebook.ipynb --ExecutePreprocessor.timeout=1800
Remove-Item Env:VECTRA_X_RECOMPUTE
```

Notebook-specific exports are written to `outputs/final_notebook/`.

## Key Results

| Track | Best model | Macro F1 | Micro F1 | Macro PR-AUC |
|---|---|---:|---:|---:|
| PRE_LAB, deployable | Extra Trees | 0.65 | 0.84 | 0.61 |
| LAB_AWARE, confirmation | XGBoost | 0.56 | 0.81 | 0.57 |
| FULL, leakage demonstration | HistGB | 0.70 | 0.89 | 0.68 |

- Co-infection detector ROC-AUC: approximately 0.86.
- Conformal empirical coverage: approximately 94.8%.
- More than half of the cohort has more than one diagnosis label.
- Leave-one-center-out performance is materially lower and requires
  facility-specific validation.

Metrics may change when the pipeline is regenerated. The exported summary and
technical report are the current source for exact values.

## Modeling Assumptions

- The task is multi-label, not multi-class.
- Five labels are active; chikungunya, zika, and option 8 have zero positives.
- Missing values mean unknown, never negative.
- Diagnostic and laboratory features are separated by the stage at which they become
  available.
- Patient timestamps and coordinates are unavailable, so external data is not merged
  into patient-level training.

## Leakage Warning

The raw dataset contains diagnostic-test and current-disease features such as
`Dengue (Dengua)`, `Test TDR`, and `Goutte epaisse`. These are never used by the
deployable PRE_LAB model when they are unavailable at triage time.

The FULL track intentionally demonstrates how leakage can inflate performance. It is
research-only and must not be used for patient inference.

## Limitations

The cohort is small, labels are imbalanced, rare-label estimates have wide
uncertainty, and health-center transfer is weak. VECTRA-X has not undergone
prospective clinical validation, workflow safety testing, regulatory review, or
production health-system integration.
