# AGENTS.md — VECTRA-X

> Operational guide for AI agents (Claude Code, Codex, etc.) working in this repo.
> Keep this file current — see **Maintaining this file** at the bottom.

## What this project is

**VECTRA-X** — a leakage-aware, multi-label, uncertainty-conscious clinical triage
research prototype for vector-borne disease response (FIT Competition 2026, Track IV).
It turns model probabilities into transparent patient triage, conformal prediction
sets, and population-level resource projections. It is a **research decision-support
prototype**, not a diagnostic device.

The supervised cohort is **299 patients** (1 of 300 raw rows dropped: its full
diagnosis vector is unknown). **5 scored labels** (`class_order`): malaria,
other_diseases, dengue, typhoid, yellow_fever (zika, chikungunya, option_8 are dropped
as zero-positive). Two model tracks: **PRE_LAB** (primary prototype, Extra Trees) and
**LAB_AWARE** (post-test comparison, HistGradientBoosting).

## Golden rules (do not break these)

1. **No leakage.** The feature **schema** (column typing, near-constant drops,
   missingness indicators, high-cardinality handling — `FeatureFrameBuilder`) is fit
   on the **training pool only** for the frozen-test path and **refit inside each
   CV fold** (`fold_local_oof_proba`); the stateful imputer/encoder are likewise
   fold-local. Model selection, thresholds, and calibration are learned without
   frozen-test labels. The test set is evaluated **once**. Target-restating fields
   (e.g. `Autres maladies présentées par le
   patient`, the disease-named "Dengue (Dengua)" field) are excluded from model
   evidence — see `leakage.research_only_features` in [config/config.yaml](config/config.yaml).
2. **Multi-label, not multi-class.** Missing diagnosis targets stay *unknown* and are
   never converted to negatives. Zero-positive labels are reported as a limitation,
   never scored.
3. **Single scientific source of truth** is
   [notebooks/VECTRA_X_Final.ipynb](notebooks/VECTRA_X_Final.ipynb). The public web
   build derives **only** from the hash-verified release pointed to by
   [outputs/releases/latest.json](outputs/releases/latest.json) — historical CSVs and
   stale figures cannot influence it. Other markdown plans/audits are retained
   provenance, not current truth.
4. **Model-persistence contract.** `scikit-learn` is pinned `==1.8.0` in both
   [requirements.txt](requirements.txt) and [web/requirements.txt](web/requirements.txt);
   the notebook-exported `web/model/*.joblib` and the `web/api` inference **must** load
   under the same version. Quick mode never overwrites canonical tables or the release.
5. **Privacy & safety.** The public bundle carries no UUID, ground truth, or full
   target-restating results. The live assessment runs the locked joblib locally and is
   anonymous: not persisted, not written to browser storage, never logged as a request
   body (64 KiB request cap, `Cache-Control: no-store`). Production use stays blocked
   until rate limiting is enabled and both release validators pass.

## Repository map

```text
config/config.yaml               Main config: paths, label/leakage rules, preprocessing, modeling
config/notebook_experiment.json  Experiment contract: target policy, nested-CV folds/seeds, candidates, threshold grid, bootstrap
config/clinical_ranges.json      Hard input-validity guards per feature (used by assessment validation)
data/raw/                        Official files, unchanged: data.csv (';'-sep, decimal ','), desciption.xlsx
data/{interim,processed,external}  Derived data stages
notebooks/VECTRA_X_Final.ipynb   Executed scientific notebook (125 cells; SELF-CONTAINED — section-local functions lifted from src/, readable inlined config, robust dataset discovery, no src/config imports, no in-memory module bootstrap)
VECTRA_X_Final_Submission.ipynb  Repo-root copy of the above = the single-file, judge-facing self-contained submission (final deliverable)
src/                             Tested research workflow modules (~4.7k LOC) — see below; the notebook generator lifts these function defs verbatim into section-local cells
scripts/                         build_final_submission.py (CANONICAL generator: AST-lifts src/ defs into a 16-section notebook) · validate_final_notebook.py (validates the SELF-CONTAINED contract: clean+ordered execution, no over-claims, required computed evidence vars + language, no `from src`/release/bootstrap, self-marker present) · validate_web_bundle.py · build_submission*.py + build_final_notebook.py + _execute.py + _original_notebook.ipynb (SUPERSEDED black-box generators — would regenerate the old _MODULE_SOURCES architecture; do not run)
tests/                           Python contract/research tests (unittest)
outputs/releases/                Hash-verified scientific releases; latest.json points to the active run_id
outputs/tables/                  Canonical final_*.csv evidence tables
outputs/reports/                 Technical reports, audits, EDA, fairness, calibration summaries
outputs/{dashboard_data,submission}  Generated artifacts
schemas/                         JSON Schema for the scientific release bundle (scientific-release.schema.json)
web/                             Public dashboard: static evidence + local Python assessment API (see below)
run_pipeline.py                  CLI counterpart of the canonical notebook workflow
export_web_data.py               Builds the public bundle from outputs/releases/latest.json
PRODUCT.md / DESIGN.md           Product brief + dashboard design system
docs/                            Current docs + retained superpowers plans/specs
app/                             (currently empty)
```

### src/ module map

| Module | Responsibility |
|---|---|
| `notebook_workflow.py` | Orchestrates the full research workflow; `run_research_workflow()` returns `ResearchWorkflowResult` consumed by the notebook and `run_pipeline.py` |
| `data_loader.py` | Loads the raw French/English semicolon CSV with encoding fallbacks |
| `label_detection.py` | Detects multi-label diagnosis columns, applies the French→English alias map, drops zero-positive labels |
| `leakage_audit.py` | Name-pattern + mutual-information / single-feature-AUC leakage screens; routes target-restating fields to research-only |
| `schema_audit.py` | Cohort/schema integrity and audit checks |
| `preprocessing.py` | `FeatureFrameBuilder` (fit/transform: train-only feature schema — typing, near-constant drops, `__missing` indicators, high-cardinality handling, yes/no token normalization) + `build_preprocessor` (fold-local imputer/one-hot ColumnTransformer) |
| `modeling.py` | Model training, PRE_LAB / LAB_AWARE track definitions, `cross_val_proba`, and `fold_local_oof_proba` (refits the whole schema inside each CV fold) |
| `evaluation.py` / `research_evaluation.py` | Metrics (macro/micro-F1, PR-AUC), repeated nested validation, LOCO |
| `calibration.py` | Probability calibration (sigmoid / isotonic) |
| `conformal.py` | Conformal prediction sets (exact + pragmatic policies, ~90% target coverage) |
| `fairness.py` | Subgroup fairness metrics and limitations |
| `explainability.py` | Global/feature importance |
| `triage_engine.py` | Converts probabilities into triage outputs using per-label risk weights |
| `nested_validation.py` | Repeated nested multi-label model + threshold selection |
| `feature_contract.py` | Feature lineage, availability stage, and clinical input-validity contracts |
| `decision_analysis.py` | Selective prediction + explicit-assumption decision scenario analyses |
| `release_bundle.py` | Canonical, privacy-checked scientific release-bundle writer (drives `outputs/releases/`) |
| `visualization.py` | Figures |
| `report_utils.py` | Report/table helpers |

## Self-contained competition submission

The final FIT deliverable is **one file**: `VECTRA_X_Final_Submission.ipynb` (repo root),
an identical executed copy of `notebooks/VECTRA_X_Final.ipynb`. Judges receive only that
`.ipynb` plus the official dataset — never `src/`, `config/`, the release bundle, or web
files. It is organised as a natural **16-section scientific report** (Sec. 1 Exec summary /
reproducibility → Sec. 16 readiness checklist), where helper functions are defined as
**ordinary `def`s in the section that uses them** — there is no raw-string module dump, no
`exec`-bootstrapped in-memory package, and no single black-box workflow entry point.

- `config/*` → inlined as small, readable, commented Python dicts (`CONFIG`, plus named
  constants `RANDOM_STATE`, `VALIDATION_SEEDS`, `CANDIDATE_MODELS`, …). No external file.
- The tested `src/` functions are **AST-lifted verbatim** into section-local code cells by
  the generator: relative imports are stripped and sibling-module alias prefixes
  (`ev.`, `M.`, `pp.`, …) are flattened to bare names so they live in the notebook
  namespace. The monolithic `run_research_workflow` is decomposed into transparent
  per-section orchestration that exposes intermediate variables (`df_raw`, `df_supervised`,
  `y`, `feature_contract`, `final_test_metrics`, …). **No `src` package is ever imported.**
- Dataset discovery (`find_dataset`/`load_official_dataset`) searches `data.csv`,
  `data/raw/data.csv`, `/kaggle/input/**`, etc., handles the `;`-sep / decimal-`,` format,
  and raises a clear error if absent.
- Sec. 16 runs **result invariants** (recomputed from the run — 299-patient cohort, five
  active labels, disjoint split, one-shot frozen-test evaluation, training-only selection,
  train-only feature schema, fold-local CV, evidence-limited yellow fever) and a
  **self-containment scan** (asserts no `_MODULE_SOURCES` / `_vectra_lib` /
  `run_research_workflow` / `from src` / release-bundle / absolute-path dependency); it
  locates itself by the `VECTRA_X_SELF_CONTAINED_SUBMISSION_MARKER` sentinel.
- Callouts use a restrained scientific palette (evidence=blue, method=purple,
  decision=teal, risk=amber, governance=red).
- **Judge-facing rubric layer**: a scannable **executive snapshot** + **environment
  compatibility guard** (Sec. 1), feature-governance + **dataset challenge map** figures
  (Sec. 5), a **preprocessing decision table** + executable **integrity-assertion** cell
  carrying the train-only/fold-local schema checks (Sec. 6), macro-vs-micro explainer +
  candidate **leaderboard** plot (Sec. 7–8), per-label scorecard / confusion visuals + a
  **rare-label reliability** table with triage-safe routing (Sec. 9, 9.3), a **reliability
  diagram** (Sec. 10), an anonymised **patient triage case card** + **population-response**
  figure (Sec. 14), computed **result invariants** + a **FIT rubric evidence map**
  (Sec. 16.1–16.2).

**Regenerate + re-execute** (after any `src/`, config, or narrative change):

```bash
python scripts/build_final_submission.py   # AST-lifts src/ defs -> writes notebooks/VECTRA_X_Final.ipynb (unexecuted)
copy notebooks/VECTRA_X_Final.ipynb VECTRA_X_Final_Submission.ipynb
python -m jupyter nbconvert --to notebook --execute VECTRA_X_Final_Submission.ipynb \
  --output VECTRA_X_Final_Submission.ipynb --ExecutePreprocessor.timeout=-1   # clean-kernel run from repo root
copy VECTRA_X_Final_Submission.ipynb notebooks/VECTRA_X_Final.ipynb           # keep both in sync (executed)
```

The build script is a dev tool, **not** part of the submission. `_original_notebook.ipynb`
is the pristine (pre-inlining) notebook the generator transforms; do not delete it.

## Web app architecture (`web/`)

Two layers, both sourced from the same hash-verified release:

- **Static evidence (no backend):** `web/data/{evidence.json, input-schema.json,
  demo-cases.json, manifest.json}` (+ `data/schemas/`). `manifest.json`
  (`schema_version` 3.1.0) carries sha256 hashes for every doc/figure/model, plus
  `notebook_sha256`, `analysis_policy_id`, `policy_ids`, `run_id`, `safe_scope`,
  and `production_rate_limit_required`.
- **Live local assessment (small Python API):** `web/api/{inference.py, assess.py,
  validation.py}` runs the **exact exported** `web/model/{pre_lab,lab_aware}.joblib`
  pipelines. `inference.py` (`LockedInferenceService`) hash-checks models against
  `web/model/model-manifest.json`; `assess.py` is a Vercel-compatible JSON-only
  endpoint; `validation.py` validates inputs against `input-schema.json` +
  `config/clinical_ranges.json`.

Pages: `index.html` (landing), `prototype.html` (integrated operational workflow),
`dashboard.html` (analytics), `demo.html` (guided demo), and `assessment.html`
(focused live assessment). Vanilla HTML/CSS/JS — `assets/router.js` routes;
supporting modules include `prototype.js`, `prototype-state.js`, `data-client.js`,
`evidence-views.js`, `schema-form.js`, `resource-simulator.js`, `thresholds.js`,
`provenance.js`, `formatters.js`, and `components.js`. Design system:
[DESIGN.md](DESIGN.md). Project-local visual assets live in `web/assets/images/`
(currently the generated command-center hero used by the landing, dashboard, and
prototype hero surfaces).

Serve with `python web/serve_live.py --port 4173` (static files **and** the local API;
`file://` can't load the JSON). Deploy to Vercel with `web/` as root, framework
preset **Other**, no build command, output dir `.`.

## How to run & verify

Python 3.10+ (verified on 3.12). Tests are **pytest**-style bare functions (run
with `pytest`, not `unittest discover`). On this Windows machine pass
`--basetemp=.pytmp` so pytest does not hit the `%TEMP%\pytest-of-*` permission
error. See `MEMORY.md` for the absolute python path.

```bash
# Reproduce research (CLI)
python run_pipeline.py                      # full run: writes final_*.csv + web bundle
python run_pipeline.py --quick --skip-web   # dev check only (no canonical/release overwrite)

# Reproduce research (notebook)
python -m jupyter nbconvert --to notebook --execute \
  notebooks/VECTRA_X_Final.ipynb --output VECTRA_X_Final.ipynb \
  --output-dir notebooks --ExecutePreprocessor.timeout=-1

# Rebuild + validate the public web bundle (reads outputs/releases/latest.json only)
python export_web_data.py
python scripts/validate_notebook_release_parity.py
python scripts/validate_web_bundle.py

# Serve the dashboard + local assessment API
python web/serve_live.py --port 4173        # open http://localhost:4173
open_dashboard.bat                          # Windows: open index.html via live server

# Verify everything
python -m pytest tests/ -q --basetemp=.pytmp   # pytest-style; .pytmp avoids a Windows temp ACL error
python scripts/validate_final_notebook.py
python scripts/validate_notebook_release_parity.py
python scripts/validate_web_bundle.py
cd web && npm test && npm run check          # node --test (tests/*.test.js) + tools/check-js.mjs
# optional browser smoke: cd web && npm run test:browser
```

## Current evidence (frozen test — executed notebook, Sec. 9)

Once-only frozen-test evaluation in
[notebooks/VECTRA_X_Final.ipynb](notebooks/VECTRA_X_Final.ipynb) **after the train-only /
fold-local schema fix** (train pool 221, frozen test 78; split seed unchanged):

| Track | Model | Macro-F1 | Micro-F1 | Macro PR-AUC | Macro recall |
|---|---|---:|---:|---:|---:|
| PRE_LAB | Extra Trees | 0.476 | 0.756 | 0.539 | 0.506 |
| LAB_AWARE | HistGradientBoosting | 0.478 | 0.730 | 0.514 | 0.587 |

Active scientific release: **`20260615T211254Z`** (scientific schema `1.1.0`, public
schema `3.1.0`, analysis policy `3117420567f127a8`).

**PRE_LAB stays the primary prototype** (leads micro-F1 and macro PR-AUC); LAB_AWARE's
small macro-F1 edge does not establish operational superiority and depends on
confirmatory inputs. Yellow fever has **3** frozen-test positives and **0.00** recall
(flagged evidence-limited; routed to confirmatory testing — Sec. 9.3). LOCO macro-F1
≈ **0.27–0.30** → center transfer is the main generalization warning. These come from
the executed notebook, canonical `outputs/tables/*.csv`, release bundle, model
artifacts, and public web evidence; parity is enforced by
`scripts/validate_notebook_release_parity.py`.

## Skill-first workflow (for agents)

This environment is configured (global `~/.claude/settings.json` `UserPromptSubmit`
hook → `~/.claude/skill-doctrine.md`) to **invoke the most relevant skill before
acting**. Quick routing:

- Clarify ambiguity → **grill-me** · Plan → **writing-plans** / Plan agent / EnterPlanMode
- Build feature → **brainstorming** → **writing-plans** → **test-driven-development**
  → **verification-before-completion** → **finishing-a-development-branch**
- Debug a failure → **systematic-debugging** · Parallel/independent tasks →
  **dispatching-parallel-agents** / **subagent-driven-development**
- Frontend/UI → **impeccable** (shape/craft/polish/audit), **frontend-design**,
  **ui-ux-pro-max**, **ui-styling**, **design** · Hi-fi prototypes/slides/animation →
  **huashu-design** · Extract a design system from a site/repo → `skillui` CLI
- Review diff/PR → **requesting-code-review** / **code-review** (+ **simplify**);
  handle feedback → **receiving-code-review** · Security → **vibe-security** /
  **security-review** · Git branch+PR → **git-branch-pr** · Deploy → **vercel-deploy**
- Browser automation / localhost verification → `browser-use` CLI · Clean a web page
  to markdown → **defuddle** · Notes/canvas → **obsidian-markdown** / **json-canvas** /
  **obsidian-bases** / **obsidian-cli** · Google Workspace → `gws` CLI
- Confirm a change works before claiming done → **verify** / **verification-before-completion**

**Installed skill families** (`~/.claude/skills`, 38 skills): the Anthropic design
set, 10 portable workflow skills, all 14 **Superpowers** skills, **Impeccable**,
**Huashu-Design**, and 5 **Obsidian** skills. **CLI tools** on PATH: `skillui`,
`defuddle`, `browser-use` (chromium already installed), `gws`. Sources are cloned in
`C:\Users\rapha\Documents\VSCode\AI Skills\_third_party_src`.

Still **manual** (account/runtime, not installable for you): `browser-use` needs an
LLM API key (env var) to drive agents; `gws` needs `gws auth login` + a Google Cloud
**Desktop-app** OAuth client JSON; `obsidian-cli` needs the Obsidian app running.

## Maintaining this file

**Whenever you make a non-trivial improvement** (new feature, module, script,
workflow, dependency, or structural change), **update AGENTS.md in the same change**
so it stays the accurate map of the repo. Specifically:

- New/removed `src/` module or `web/` layer → update the relevant map/section.
- New run/verify/deploy command → update **How to run & verify**.
- New metrics, model decision, or release `run_id` → update **Current evidence**.
- Keep it concise; this is a navigation map, not a changelog.
```
