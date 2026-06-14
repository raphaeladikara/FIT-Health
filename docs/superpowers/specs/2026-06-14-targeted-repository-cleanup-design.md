# Targeted Repository Cleanup Design

## Objective

Produce the cleanest competition repository that preserves the final research
notebook, the static web dashboard, reproducible source code, verification tests,
official raw data, canonical outputs, and the complete Markdown improvement history.

## Canonical Sources

- `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb` is the sole scientific
  notebook and authoritative competition narrative.
- `outputs/tables/final_*.csv` are the authoritative evaluation results.
- `web/` remains the public dashboard. Its layout and visual design are unchanged.
- Markdown specifications, plans, audits, and reports remain as historical evidence.

## Removal Scope

Remove the retired Streamlit application and dependency, the three superseded
notebooks, local caches, duplicate generated datasets, serialized local models,
legacy dashboard caches, and output files that are neither canonical evidence nor
required by the static dashboard.

Raw competition files remain tracked. Generated public JSON and figures remain
tracked because the static Vercel deployment has no build backend.

## Web Data Contract

`export_web_data.py` will construct the public evidence bundle from canonical
`final_*` tables. It must report a supervised cohort of 299, expose only PRE_LAB
and LAB_AWARE frozen-test evidence, separate exact and pragmatic prediction-set
policies, and describe resource results as deterministic scenario projections.
No FULL model result, patient identifier, or ground truth may enter the public
bundle.

The current HTML and CSS structure remains untouched. Existing JavaScript receives
only the smallest compatibility edits needed to consume the corrected contract and
present the latest terminology.

## Documentation

The root README and web README will describe one canonical notebook, one static
dashboard, the latest leakage-safe results, the retained historical Markdown record,
and the exact regeneration and verification commands. Streamlit and superseded
notebook instructions will be removed.

## Verification

The release gate requires:

1. Python tests and compilation pass.
2. The final notebook validator reports no execution or content errors.
3. The web exporter and bundle validator pass.
4. Node unit tests and JavaScript syntax checks pass.
5. Repository checks find no Streamlit runtime, obsolete notebooks, FULL public
   evidence, stale cohort size, cache files, or untracked generated clutter.

