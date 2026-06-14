# VECTRA-X

**Leakage-aware, multi-label, and uncertainty-conscious clinical triage research
for vector-borne disease response**

FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction.

> VECTRA-X is a research decision-support prototype. It is not a diagnostic
> device, treatment recommendation system, or substitute for clinical judgment.

## Canonical Artifacts

- Scientific submission:
  `notebooks/VECTRA_X_Final.ipynb`
- Concise technical report:
  `outputs/reports/final_technical_report_sketch.md`
- Audit closure:
  `outputs/reports/final_audit_resolution.md`
- Public dashboard (static evidence + local assessment API):
  `web/`
- Corrected evidence tables:
  `outputs/tables/final_*.csv`

The final notebook is the only scientific notebook in the repository. It executes
from the official raw files, excludes one row whose complete diagnosis vector is
unknown, performs all feature and model decisions on training data, and evaluates
the locked models once on a frozen test set.

## Current Evidence

| Track | Selected model | Macro-F1 | Micro-F1 | Macro PR-AUC |
|---|---|---:|---:|---:|
| PRE_LAB | Extra Trees | 0.4624 | 0.7440 | 0.5416 |
| LAB_AWARE | HistGradientBoosting | 0.4777 | 0.7299 | 0.5141 |

The supervised cohort contains **299 patients** from 300 raw rows. PRE_LAB remains the
primary prototype: the LAB_AWARE track does not establish operational superiority on
aggregate frozen-test micro-F1 or macro PR-AUC and depends on confirmatory inputs.
Yellow fever has very few positive frozen-test observations and near-zero recall.
Leave-one-center-out macro-F1 is approximately **0.26-0.31**, making center transfer
the main generalization warning.

Target-restating fields, including the other-disease presentation field and the
disease-named dengue field, are excluded from public model evidence. Exact and
pragmatic empirical inclusion-set policies are reported separately; the pragmatic
policy carries no formal coverage claim.

## Repository Structure

```text
config/                 Analysis config + experiment & clinical-range contracts (config.yaml, *.json)
data/raw/               Official competition files, unchanged
docs/                   Current documentation and retained improvement history
notebooks/              The single executed final notebook: VECTRA_X_Final.ipynb
outputs/releases/       Hash-verified scientific releases; latest.json marks the active run
outputs/reports/        Technical reports, audits, limitations, and project history
outputs/tables/         Canonical final evidence plus small web-support tables
schemas/                JSON Schema for the scientific release bundle
scripts/                Notebook builder and release validators
src/                    Tested research workflow modules
tests/                  Python research and repository contract tests
web/                    Public dashboard: static evidence + local Python assessment API
export_web_data.py      Builds the public bundle from outputs/releases/latest.json
run_pipeline.py         CLI counterpart of the canonical notebook workflow
```

Markdown design documents, plans, audits, and reports are intentionally retained.
Some historical documents describe intermediate architectures or findings; they are
provenance records, not the current scientific source of truth.

## Setup

Requires Python 3.10 or newer. The verified development environment used Python
3.12.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce the Research

Execute the final notebook:

```bash
python -m jupyter nbconvert \
  --to notebook \
  --execute notebooks/VECTRA_X_Final.ipynb \
  --output VECTRA_X_Final.ipynb \
  --output-dir notebooks \
  --ExecutePreprocessor.timeout=-1
```

Or run the same research workflow from the command line:

```bash
python run_pipeline.py
python run_pipeline.py --quick --skip-web  # development check only
```

Quick mode never overwrites the canonical public web bundle.

## Dashboard

The dashboard is a Vercel-ready application with two layers: a static evidence bundle
and a local Python assessment API that runs the exact exported joblib pipeline. The
public bundle publishes aggregate evidence and curated anonymous cases only — never
UUIDs or patient ground truth. Live assessment values are anonymous: not persisted,
not stored in the browser, and never logged.

```bash
python export_web_data.py             # rebuilds from outputs/releases/latest.json
python scripts/validate_web_bundle.py
python web/serve_live.py --port 4173  # serves static files + the local assessment API
```

Open `http://localhost:4173`. For Vercel, use `web/` as the project root with no build
command (output directory `.`).

## Verification

```bash
python -m pytest -q
python scripts/validate_final_notebook.py
python scripts/validate_web_bundle.py
cd web
npm test
npm run check
```

## Research Boundaries

- The task is multi-label, not multi-class.
- Missing diagnosis targets remain unknown and are never converted to negatives.
- Stateful preprocessing, model selection, thresholds, and calibration are learned
  without access to frozen-test labels.
- PRE_LAB is the primary research prototype; LAB_AWARE is a post-test comparison.
- Resource and triage outputs are deterministic scenario projections, not measured
  staffing, treatment, or outcome effects.
- External, prospective, multi-center validation is required before clinical use.
