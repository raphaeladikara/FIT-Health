# VECTRA-X

**Leakage-aware, multi-label, and uncertainty-conscious clinical triage research
for vector-borne disease response**

FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction.

> VECTRA-X is a research decision-support prototype. It is not a diagnostic
> device, treatment recommendation system, or substitute for clinical judgment.

## Canonical Artifacts

- Scientific submission:
  `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`
- Concise technical report:
  `outputs/reports/final_technical_report_sketch.md`
- Audit closure:
  `outputs/reports/final_audit_resolution.md`
- Public static dashboard:
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
| PRE_LAB | Extra Trees | 0.4823 | 0.7673 | 0.5247 |
| LAB_AWARE | HistGradientBoosting | 0.4439 | 0.7321 | 0.5024 |

The supervised cohort contains **299 patients** from 300 raw rows. The LAB_AWARE
track does not improve aggregate frozen-test macro-F1 or macro PR-AUC. Yellow
fever has three positive frozen-test observations and zero recall. Leave-one-center-
out macro-F1 is approximately **0.26-0.31**, making center transfer the main
generalization warning.

Target-restating fields, including the other-disease presentation field and the
disease-named dengue field, are excluded from public model evidence. Exact and
pragmatic empirical inclusion-set policies are reported separately; the pragmatic
policy carries no formal coverage claim.

## Repository Structure

```text
config/                 Reproducible analysis configuration
data/raw/               Official competition files, unchanged
docs/                   Current documentation and retained improvement history
notebooks/              The single executed final competition notebook
outputs/reports/        Technical reports, audits, limitations, and project history
outputs/tables/         Canonical final evidence plus small web-support tables
scripts/                Notebook builder and release validators
src/                    Tested research workflow modules
tests/                  Python research and repository contract tests
web/                    Static landing page, guided demo, and analytics dashboard
export_web_data.py      Builds the public JSON evidence bundle
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
  --execute notebooks/VECTRA_X_Final_Competition_Notebook.ipynb \
  --output VECTRA_X_Final_Competition_Notebook.ipynb \
  --output-dir notebooks \
  --ExecutePreprocessor.timeout=-1
```

Or run the same research workflow from the command line:

```bash
python run_pipeline.py
python run_pipeline.py --quick --skip-web  # development check only
```

Quick mode never overwrites the canonical public web bundle.

## Static Dashboard

The dashboard is a zero-backend, Vercel-ready static application. It publishes
aggregate evidence and at most 12 curated anonymous cases. It does not publish
UUIDs, patient ground truth, or live inference.

```bash
python export_web_data.py
python scripts/validate_web_bundle.py
cd web
python -m http.server 8765
```

On Windows, `open_dashboard.bat` starts the same local static server. For Vercel,
use `web/` as the project root with no build command.

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
