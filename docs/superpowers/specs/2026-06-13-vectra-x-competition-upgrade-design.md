# VECTRA-X Competition Upgrade Design

## Purpose

Upgrade the existing VECTRA-X repository into a polished, judge-ready competition
package while preserving all current notebooks, scripts, models, outputs, reports,
and dashboard assets.

The upgrade has three deliverables:

1. A comprehensive, narrative-driven, fully executable competition notebook.
2. A genuinely interactive Streamlit decision-support prototype.
3. A competitiveness audit and judge-pitch package grounded in the verified project
   results.

## Existing Foundation

The repository already contains a deterministic end-to-end pipeline, three technical
notebooks, saved pre-lab and lab-aware model bundles, patient-level predictions,
calibration and conformal outputs, fairness results, explainability artifacts,
resource simulation data, 27 or more output tables, and 26 presentation figures.

The upgrade will treat these artifacts as the current source of truth. It will not
silently replace metrics or claim new performance without fresh verification.

## Selected Approach

### Utility-first delivery

Functional correctness is the primary acceptance gate. Saved-model inference,
threshold switching, upload validation, patient selection, resource simulation,
downloads, notebook execution, and reproducibility must work before any optional
visual redesign. Styling changes are limited to clear hierarchy, readable status
semantics, and usable interactive charts. A separate visual-polish pass may follow
after all functional verification succeeds.

### Hybrid reproducibility

The final notebook will support two explicit execution paths:

- Default artifact-backed execution for a fast, stable judge demonstration.
- Full deterministic recomputation when `RECOMPUTE_MODELS = True`.

The notebook must remain executable top-to-bottom in both modes. The fast mode will
still load raw and processed project data, validate artifact presence and consistency,
recreate lightweight analysis views, and document artifact provenance. Full mode will
invoke the existing pipeline or its reusable modules to regenerate models and outputs
before rendering the report.

### Modular dashboard

The Streamlit dashboard will be separated into:

- `app/streamlit_app.py`: navigation and page composition.
- `app/dashboard_config.py`: paths, labels, colors, model modes, policy definitions,
  and user-facing copy.
- `app/dashboard_utils.py`: cached loading, validation, inference adapters, filtering,
  Plotly figure construction, resource simulation, and downloadable report creation.

Focused tests will cover reusable behavior without requiring a running Streamlit
server.

## Final Competition Notebook

Create `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`.

The notebook will:

- Use formal English and an academic research tone.
- Follow the required 0-27 narrative from humanitarian context through reproducibility.
- Use project-relative paths and a deterministic random seed.
- Detect the project root reliably when launched from the repository or `notebooks/`.
- Include environment and artifact checks near the beginning.
- Keep major logic in reusable functions or existing `src` modules rather than large
  code dumps.
- Place explanatory markdown before and after major code cells.
- Include titled, labeled, interpreted Plotly or existing high-quality figures.
- Add visible Key Takeaway callouts after important results.
- Write notebook-specific tables, charts, and exports to `outputs/final_notebook/`.
- Include patient case cards for high-confidence single disease, co-infection, high
  uncertainty, urgent priority, and false-negative risk.
- Present the pre-lab model as the primary operational model.
- Present the lab-aware model as confirmation support.
- Present the full-feature model only as a leakage demonstration.
- Include a clear Why VECTRA-X Can Win section.
- State consistently that VECTRA-X is decision support, not a replacement for medical
  professionals.

The notebook will open cleanly even when optional engines or SHAP are unavailable.
Optional features will show informative fallback text rather than breaking execution.

## Dashboard Information Architecture

The dashboard will use a sidebar or compact top-level navigation with ten views:

1. Executive Overview
2. Patient-level Prediction
3. Batch Prediction and Upload
4. Population Overview
5. Resource Prioritization
6. Model Trust
7. Explainability
8. Uncertainty and Conformal Prediction
9. Fairness and Robustness
10. Methodology and Limitations

### Global controls

The sidebar will contain:

- Model mode switch.
- Threshold policy selector.
- Safety disclaimer.
- Artifact status indicator.

The mode switch will clearly mark the full-feature model as research-only. If a saved
model bundle is missing, the corresponding mode remains visible but disabled or
explained rather than crashing.

### Interaction model

- Patient selection updates probabilities, prediction set, uncertainty, co-infection,
  triage, action, and local explanation dynamically.
- Batch upload validates required columns against the selected saved pipeline.
- Successful inference creates a downloadable CSV.
- When inference cannot run, the UI explains the missing dependency or schema mismatch
  and offers a clearly labeled demonstration using precomputed patients.
- Population filters are generated only for columns that exist.
- Resource assumptions update demand, capacity gaps, recommendations, and policy
  comparisons immediately.
- Downloads are generated from the currently filtered or simulated state.

## Visual Direction (Secondary)

After functional acceptance criteria pass, use the approved presentation-forward
hybrid where it improves clarity:

- Dark navy application shell.
- High-contrast content surfaces.
- Teal primary accent.
- Coral/red urgent state.
- Amber confirmatory-test and moderate-uncertainty state.
- Green routine or sufficient-capacity state.
- Consistent Plotly templates and disease colors.
- Strong judge-facing hierarchy without resembling a consumer diagnostic product.

The interface must remain readable, use color-blind-safe chart palettes, and never
rely on color alone. Visual novelty is not a completion criterion.

## Data and Error Handling

All paths are project-relative and resolved from `Path(__file__)` or a notebook root
detector.

Loaders return typed empty states or structured status objects for missing optional
files. Required artifact failures produce one actionable message. Optional figures,
SHAP data, subgroup columns, date fields, and location fields degrade gracefully.

Uploaded CSV files are checked for:

- Readability and non-empty content.
- Required feature columns for the selected mode.
- Unexpected duplicate columns.
- Useful schema differences reported to the user.

No heavy model retraining occurs inside Streamlit.

## Testing Strategy

Use test-driven development for reusable dashboard behavior:

- Table and summary loading.
- Model-mode availability.
- Uploaded-schema validation.
- Threshold-policy application.
- Resource demand and capacity calculation.
- Patient report generation.
- Missing-artifact fallbacks.

Notebook generation is programmatic and validated by:

- JSON/nbformat structural checks.
- Required section-title checks.
- Execution with the available project Python runtime.
- Verification that expected notebook outputs are created.

Dashboard verification includes:

- Unit tests.
- `py_compile` for all dashboard modules.
- Import smoke test.
- Brief Streamlit launch and browser inspection when the runtime is available.

## Reports and Documentation

Create:

- `outputs/reports/project_competitiveness_audit.md`
- `outputs/reports/final_judge_pitch.md`

The audit will score each FIT criterion out of 10, identify jury attack points, compare
VECTRA-X with likely generic competitor approaches, and separate quick, medium,
advanced, presentation, and report improvements.

The pitch document will contain a 60-second pitch, 3-minute pitch, 7-minute flow,
technical and humanitarian claims, and concise answers to likely judge questions.

Update `README.md` with:

- Final notebook purpose and execution modes.
- Environment setup.
- Notebook run instructions.
- Dashboard run instructions.
- Required and optional artifacts.
- Windows-compatible commands.

## Screenshots and Presentation Assets

Save presentation-ready outputs under:

- `outputs/final_notebook/`
- `outputs/dashboard_screenshots/`

Screenshots will cover the executive overview, patient triage view, resource simulator,
and model trust or uncertainty view when browser capture is available. If automated
capture is unavailable, the limitation will be reported explicitly without blocking
the functional deliverables.

## Completion Criteria

The upgrade is complete only when:

- The new notebook exists, opens, contains every required section, and executes
  top-to-bottom with fresh evidence.
- Notebook-specific outputs are generated.
- Dashboard helper tests pass.
- Dashboard modules compile and import.
- Streamlit loads available outputs without retraining.
- Upload, patient selection, policy simulation, model mode, filtering, and downloads
  have working paths or explicit tested fallbacks.
- The competitiveness audit and judge pitch exist and contain all requested sections.
- README instructions are accurate.
- Existing notebooks, scripts, outputs, and reports remain preserved.
