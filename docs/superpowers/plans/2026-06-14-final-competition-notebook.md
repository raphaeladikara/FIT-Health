# VECTRA-X Final Competition Notebook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and execute one research-grade, leakage-free, fully reproducible competition notebook from raw data, plus a concise technical-report sketch aligned with its corrected results.

**Architecture:** Correct scientific behavior in focused, tested `src/` modules first; expose a notebook-oriented experiment API; generate the final notebook deterministically from a reviewed Python builder; execute it from a clean kernel; and verify its outputs, narrative structure, test isolation, and claims. The final notebook orchestrates raw-data analysis and presents evidence, while reusable computations remain in tested modules.

**Tech Stack:** Python 3.12, pandas, NumPy, scikit-learn, iterative-stratification, matplotlib, seaborn, SHAP when compatible, nbformat, nbclient, joblib, PyYAML.

---

## File Map

- Modify `src/label_detection.py`: preserve missing target values and construct the verified supervised cohort.
- Modify `src/leakage_audit.py`: screen raw and model-derived representations and enforce bilingual semantic aliases.
- Modify `src/preprocessing.py`: expose deterministic feature derivation metadata and center/missing-indicator ablations.
- Create `src/research_evaluation.py`: baselines, repeated validation, intervals, ablations, paired comparisons, selective-risk curves, and support-aware metrics.
- Modify `src/calibration.py`: cross-fitted calibration.
- Modify `src/conformal.py`: exact uncapped mode plus explicitly named pragmatic mode.
- Modify `src/fairness.py`: support, TP/FN, intervals, and insufficient-evidence status.
- Modify `src/explainability.py`: deployed-model local explanation and fidelity metadata.
- Modify `src/triage_engine.py`: scenario sensitivity analysis and prototype terminology.
- Create `src/notebook_workflow.py`: notebook-facing end-to-end research workflow.
- Create `scripts/build_final_notebook.py`: deterministic notebook builder.
- Create `scripts/validate_final_notebook.py`: structural, execution, and claim checks.
- Create `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`: canonical executed submission notebook.
- Create `outputs/reports/final_technical_report_sketch.md`: concise report outline populated from corrected results.
- Modify `requirements.txt`: add notebook execution dependencies.
- Modify `README.md`: designate the final notebook as the primary competition artifact.
- Create focused tests under `tests/`.

### Task 1: Target Integrity and Supervised Cohort

**Files:**
- Modify: `src/label_detection.py`
- Create: `tests/test_label_detection.py`

- [ ] **Step 1: Write failing tests**

```python
import pandas as pd

from src.label_detection import _to_binary, build_supervised_cohort


def test_to_binary_preserves_unknown_targets():
    result = _to_binary(pd.Series(["1", "0", None]))
    assert result.tolist()[:2] == [1, 0]
    assert pd.isna(result.iloc[2])


def test_supervised_cohort_excludes_any_row_with_all_targets_unknown():
    df = pd.DataFrame({"id": ["a", "b", "c"]})
    y_all = pd.DataFrame(
        {"malaria": [1, 0, pd.NA], "dengue": [0, 1, pd.NA]},
        dtype="Int64",
    )
    cohort = build_supervised_cohort(df, y_all)
    assert cohort.included_index.tolist() == [0, 1]
    assert cohort.excluded_index.tolist() == [2]
    assert cohort.exclusion_reason.iloc[0] == "all diagnosis targets missing"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_label_detection.py -v`  
Expected: FAIL because missing values are converted to zero and `build_supervised_cohort` does not exist.

- [ ] **Step 3: Implement nullable targets and cohort audit**

Add a `SupervisedCohort` dataclass containing `included_index`,
`excluded_index`, and `exclusion_reason`. Make `_to_binary` return nullable
`Int64`; map recognized positive tokens to 1, recognized negative tokens to 0,
and all other values to `pd.NA`. Add `build_supervised_cohort` and make
`detect_labels` calculate distributions only on included rows while returning
the exclusion audit.

- [ ] **Step 4: Verify GREEN**

Run: `python -m pytest tests/test_label_detection.py -v`  
Expected: all target-integrity tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/label_detection.py tests/test_label_detection.py
git commit -m "fix: preserve unknown diagnosis targets"
```

### Task 2: Representation-Aware Leakage Governance

**Files:**
- Modify: `src/leakage_audit.py`
- Modify: `src/preprocessing.py`
- Modify: `config/config.yaml`
- Create: `tests/test_leakage_governance.py`

- [ ] **Step 1: Write failing tests**

```python
import pandas as pd

from src.leakage_audit import audit_leakage
from src.preprocessing import make_feature_frame


def test_other_disease_presentation_is_research_only():
    feature = "Autres maladies presentees par le patient"
    df = pd.DataFrame({feature: ["text", None, "other", None]})
    y = pd.DataFrame({"other_diseases": [1, 0, 1, 0]})
    result = audit_leakage(df, y, [feature], cfg=minimal_cfg())
    row = result["audit"].set_index("feature").loc[feature]
    assert row["decision"] == "research_only"
    assert row["derived_representation"] == "presence"


def test_deployable_frame_cannot_contain_research_only_derived_columns():
    feature = "Autres maladies presentees par le patient"
    df = pd.DataFrame({feature: ["text", None]})
    frame, _ = make_feature_frame(df, [], cfg=minimal_cfg())
    assert not any("autres_maladies" in c for c in frame.columns)
```

The test helper `minimal_cfg()` must define label aliases, leakage thresholds,
and preprocessing fragments using the same keys as `config/config.yaml`.

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_leakage_governance.py -v`  
Expected: FAIL because the existing audit ordinal-encodes text and lacks the
`other/autres` semantic rule.

- [ ] **Step 3: Implement aligned representation screening**

Add a representation descriptor that screens each raw feature using every
derived representation the model may consume: numeric parse, binary parse,
category encoding, missing indicator, and high-cardinality presence indicator.
Record `derived_representation`, target label, AUC, mutual information, semantic
alias match, and final stage decision. Add explicit bilingual target aliases to
configuration and a forced `research_only_features` list containing the audited
other-disease field.

- [ ] **Step 4: Add deployable-set assertions**

Expose a function:

```python
def assert_no_research_features(
    model_columns: list[str],
    source_map: dict[str, str],
    research_only: set[str],
) -> None:
    ...
```

It must raise `ValueError` naming every violating derived column and its raw
source.

- [ ] **Step 5: Verify GREEN**

Run: `python -m pytest tests/test_leakage_governance.py -v`  
Expected: all leakage-governance tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/leakage_audit.py src/preprocessing.py config/config.yaml tests/test_leakage_governance.py
git commit -m "fix: align leakage audit with model representations"
```

### Task 3: Baselines, Repeated Validation, Intervals, and Ablations

**Files:**
- Create: `src/research_evaluation.py`
- Create: `tests/test_research_evaluation.py`

- [ ] **Step 1: Write failing tests**

```python
import numpy as np
import pandas as pd

from src.research_evaluation import (
    baseline_predictions,
    bootstrap_metric_interval,
    paired_bootstrap_difference,
    selective_risk_curve,
)


def test_always_malaria_baseline_flags_only_malaria():
    pred = baseline_predictions(
        "always_malaria", n_rows=3, labels=["malaria", "dengue"]
    )
    assert pred.tolist() == [[1, 0], [1, 0], [1, 0]]


def test_bootstrap_interval_is_reproducible():
    y = np.array([0, 1, 1, 0, 1])
    p = np.array([0, 1, 0, 0, 1])
    first = bootstrap_metric_interval(y, p, metric="f1", n_boot=200, random_state=7)
    second = bootstrap_metric_interval(y, p, metric="f1", n_boot=200, random_state=7)
    assert first == second
    assert first["lower"] <= first["estimate"] <= first["upper"]


def test_selective_risk_decreases_when_high_error_cases_are_deferred():
    correct = np.array([1, 1, 1, 0])
    uncertainty = np.array([0.1, 0.2, 0.3, 0.9])
    curve = selective_risk_curve(correct, uncertainty)
    assert curve.iloc[-1]["risk"] <= curve.iloc[0]["risk"]
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_research_evaluation.py -v`  
Expected: FAIL because `src/research_evaluation.py` does not exist.

- [ ] **Step 3: Implement evaluation primitives**

Implement:

```python
baseline_predictions(kind, n_rows, labels, prevalence=None, random_state=42)
bootstrap_metric_interval(y_true, y_pred_or_score, metric, n_boot, random_state)
paired_bootstrap_difference(y_true, pred_a, pred_b, metric, n_boot, random_state)
repeated_multilabel_validation(model_factory, X, y, seeds, n_folds)
evaluate_feature_ablation(model_factory, feature_groups, X, y, splits)
selective_risk_curve(correct, uncertainty)
```

Every result must include sample count, positive support where applicable, mean,
standard deviation, lower 95% bound, and upper 95% bound. Bootstrap resampling
must retry samples lacking both classes and record the number of valid draws.

- [ ] **Step 4: Verify GREEN**

Run: `python -m pytest tests/test_research_evaluation.py -v`  
Expected: all research-evaluation tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/research_evaluation.py tests/test_research_evaluation.py
git commit -m "feat: add research-grade evaluation utilities"
```

### Task 4: Cross-Fitted Calibration and Exact Prediction Sets

**Files:**
- Modify: `src/calibration.py`
- Modify: `src/conformal.py`
- Create: `tests/test_calibration_conformal.py`

- [ ] **Step 1: Write failing tests**

```python
import numpy as np
import pandas as pd

from src.calibration import cross_fitted_calibration
from src.conformal import fit_conformal


def test_cross_fitted_calibration_never_trains_on_target_row():
    y = pd.DataFrame({"dengue": [0, 1, 0, 1, 0, 1]})
    p = np.array([[0.1], [0.7], [0.2], [0.8], [0.3], [0.9]])
    calibrated, audit = cross_fitted_calibration(y, p, n_splits=3, random_state=11)
    assert calibrated.shape == p.shape
    for row in audit.itertuples():
        assert row.target_index not in row.calibration_indices


def test_exact_conformal_does_not_cap_quantile_level():
    y = pd.DataFrame({"rare": [1, 1, 1, 0]})
    p = np.array([[0.1], [0.2], [0.3], [0.9]])
    info = fit_conformal(y, p, ["rare"], alpha=0.10, mode="exact")
    assert info["rare"]["quantile_level_used"] == 1.0
    assert info["rare"]["mode"] == "exact"
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_calibration_conformal.py -v`  
Expected: FAIL because cross-fitting and conformal modes are absent.

- [ ] **Step 3: Implement cross-fitted calibration**

Use deterministic stratified folds per label. Fit each fold's calibrator only on
the complementary rows and record an audit DataFrame containing target index,
fold, calibration indices, method, and positive support.

- [ ] **Step 4: Implement exact and pragmatic conformal modes**

Change the signature to:

```python
fit_conformal(y_cal, proba_cal, labels, alpha=0.10, mode="exact", pragmatic_cap=0.90)
```

`mode="exact"` uses the finite-sample corrected quantile without a cap.
`mode="pragmatic"` applies the explicitly recorded cap and must never be labeled
as guaranteed coverage. Add macro coverage, micro coverage, false-negative risk,
and calibration/test support to `conformal_metrics`.

- [ ] **Step 5: Verify GREEN**

Run: `python -m pytest tests/test_calibration_conformal.py -v`  
Expected: all calibration and conformal tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/calibration.py src/conformal.py tests/test_calibration_conformal.py
git commit -m "fix: cross-fit calibration and separate conformal policies"
```

### Task 5: Support-Aware Fairness, Deployed-Model Explanations, and Scenario Sensitivity

**Files:**
- Modify: `src/fairness.py`
- Modify: `src/explainability.py`
- Modify: `src/triage_engine.py`
- Create: `tests/test_trust_analysis.py`

- [ ] **Step 1: Write failing tests**

```python
import numpy as np
import pandas as pd

from src.fairness import subgroup_metrics
from src.triage_engine import scenario_sensitivity


def test_fairness_includes_support_counts_and_evidence_status():
    y = pd.DataFrame({"dengue": [1, 0, 1, 0]})
    pred = np.array([[1], [0], [0], [0]])
    result = subgroup_metrics(
        y, pred, ["dengue"], {"center": pd.Series(["A", "A", "B", "B"])}
    )
    required = {"support_pos_dengue", "tp_dengue", "fn_dengue",
                "recall_low_dengue", "recall_high_dengue",
                "evidence_dengue"}
    assert required.issubset(result.columns)
    assert set(result["evidence_dengue"]) == {"insufficient evidence"}


def test_scenario_sensitivity_returns_assumption_labeled_rows():
    result = scenario_sensitivity(
        proba=np.array([[0.8, 0.2], [0.6, 0.7]]),
        labels=["malaria", "dengue"],
        weight_scenarios={"base": {"malaria": 1.0, "dengue": 1.4}},
        threshold_scenarios={"base": {"malaria": 0.5, "dengue": 0.5}},
        capacities=[1, 2],
        false_negative_costs=[1.0, 5.0],
    )
    assert {"weight_scenario", "threshold_scenario", "capacity",
            "false_negative_cost"}.issubset(result.columns)
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_trust_analysis.py -v`  
Expected: FAIL because interval columns, evidence status, and sensitivity
analysis do not exist.

- [ ] **Step 3: Implement support-aware fairness**

Add Wilson recall intervals, per-label support, TP, FN, and
`insufficient evidence` when positive support is below five. Keep recall gaps
but exclude insufficient cells from strong comparative claims.

- [ ] **Step 4: Implement deployed-model local explanations**

Add:

```python
explain_deployed_tree(model, X_background, X_rows, label, method="auto")
```

Prefer TreeSHAP for supported tree estimators and fall back to local permutation
attribution. Return the explanation method, output being explained, and a
fidelity/reconstruction field. Rename existing direct-label logistic models as
`alternate_linear_models`; never call them surrogates.

- [ ] **Step 5: Implement scenario sensitivity**

Add `scenario_sensitivity` returning labeled scenario rows across risk weights,
decision thresholds, capacity limits, and false-negative costs. Ensure all
outputs are called projections and contain the governing assumptions.

- [ ] **Step 6: Verify GREEN**

Run: `python -m pytest tests/test_trust_analysis.py -v`  
Expected: all trust-analysis tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/fairness.py src/explainability.py src/triage_engine.py tests/test_trust_analysis.py
git commit -m "feat: strengthen trust and scenario analyses"
```

### Task 6: Notebook Research Workflow

**Files:**
- Create: `src/notebook_workflow.py`
- Create: `tests/test_notebook_workflow.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write failing integration tests**

```python
from src.notebook_workflow import run_research_workflow


def test_workflow_uses_verified_cohort_and_leakage_free_pre_lab():
    result = run_research_workflow(quick=True)
    assert result.cohort_audit["n_supervised"] == 299
    assert result.cohort_audit["n_excluded_unknown_target"] == 1
    assert "Autres maladies presentees par le patient" in result.research_only_features
    assert not any(
        "autres_maladies" in c for c in result.design_frames["PRE_LAB"].columns
    )


def test_workflow_keeps_test_out_of_selection_audit():
    result = run_research_workflow(quick=True)
    assert set(result.selection_audit["data_partition"]) == {"training_only"}
    assert result.final_test_audit["evaluations_per_track"].max() == 1
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_notebook_workflow.py -v`  
Expected: FAIL because the notebook workflow API does not exist.

- [ ] **Step 3: Implement workflow result contract**

Create a `ResearchWorkflowResult` dataclass with named tables and artifacts:
cohort audit, schema audit, target tables, leakage tables, feature contracts,
design frames, frozen indices, baselines, ablations, repeated-CV results,
selection audit, final-test metrics, co-infection results, calibration,
prediction sets, selective-risk curves, explanations, fairness, LOCO,
scenario sensitivity, conclusions, and artifact manifest.

- [ ] **Step 4: Implement quick and full execution modes**

`quick=True` uses two seeds, three folds, small model grids, 100 bootstrap draws,
and reduced permutation repeats for tests. Full mode uses at least ten seeds,
five folds, the reviewed search grids, at least 2,000 bootstrap draws, and all
notebook figures. Both modes must follow identical partition rules.

- [ ] **Step 5: Add notebook dependencies**

Add:

```text
nbformat>=5.10
nbclient>=0.10
ipykernel>=6.29
pytest>=8.0
```

- [ ] **Step 6: Verify GREEN**

Run: `python -m pytest tests/test_notebook_workflow.py -v`  
Expected: workflow integration tests PASS.

- [ ] **Step 7: Commit**

```bash
git add src/notebook_workflow.py tests/test_notebook_workflow.py requirements.txt
git commit -m "feat: add canonical notebook research workflow"
```

### Task 7: Build the Final Academic Notebook

**Files:**
- Create: `scripts/build_final_notebook.py`
- Create: `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`
- Create: `tests/test_final_notebook_structure.py`

- [ ] **Step 1: Write failing notebook-structure tests**

```python
import nbformat


REQUIRED_HEADINGS = [
    "Executive Abstract",
    "Data Integrity and Target Audit",
    "Leakage Discovery and Clinical-Stage Governance",
    "Experimental Protocol",
    "Baselines and Ablation Studies",
    "Final Frozen-Test Evaluation",
    "Calibration and Prediction Sets",
    "Selective Prediction and Uncertainty",
    "Explainability of the Selected Model",
    "Fairness and Center-Shift Validation",
    "Limitations, Ethics, and Conclusion",
]


def test_final_notebook_has_complete_research_narrative():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb",
        as_version=4,
    )
    markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
    for heading in REQUIRED_HEADINGS:
        assert heading in markdown
    assert markdown.count("**Interpretation.**") >= 15
    assert markdown.count("**Limitation.**") >= 10


def test_final_notebook_executes_workflow_from_raw_data():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb",
        as_version=4,
    )
    code = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
    assert "run_research_workflow(quick=False)" in code
    assert "outputs/tables/model_leaderboard.csv" not in code
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_final_notebook_structure.py -v`  
Expected: FAIL because the final notebook does not exist.

- [ ] **Step 3: Implement deterministic notebook builder**

Use `nbformat` to create the notebook with:

- a polished title and metadata block;
- a single root-bootstrap cell;
- reproducibility/version output;
- `run_research_workflow(quick=False)`;
- research-question markdown before each analysis;
- evidence tables and plotting cells;
- explicit `Interpretation` and `Limitation` prose after each result;
- final safe-claims table and reproducibility manifest;
- appendix cells for grids and expanded diagnostics.

Notebook markdown must be formal academic English and must describe the exact
partition used by each result.

- [ ] **Step 4: Generate notebook**

Run: `python scripts/build_final_notebook.py`  
Expected: creates a valid unexecuted notebook with all required headings.

- [ ] **Step 5: Verify GREEN**

Run: `python -m pytest tests/test_final_notebook_structure.py -v`  
Expected: all structural tests PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/build_final_notebook.py notebooks/VECTRA_X_Final_Competition_Notebook.ipynb tests/test_final_notebook_structure.py
git commit -m "feat: build final competition research notebook"
```

### Task 8: Execute, Validate, and Refine the Notebook

**Files:**
- Create: `scripts/validate_final_notebook.py`
- Modify: `notebooks/VECTRA_X_Final_Competition_Notebook.ipynb`
- Create: `tests/test_final_notebook_execution.py`

- [ ] **Step 1: Write failing execution validation tests**

```python
from scripts.validate_final_notebook import validate_notebook


def test_executed_notebook_is_clean_and_claim_safe():
    result = validate_notebook(
        "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb"
    )
    assert result["error_outputs"] == 0
    assert result["code_cells_without_execution_count"] == 0
    assert result["stale_execution_order"] is False
    assert result["forbidden_claims"] == []
    assert result["required_result_tables_missing"] == []
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_final_notebook_execution.py -v`  
Expected: FAIL because validation and executed outputs are absent.

- [ ] **Step 3: Implement notebook validator**

Validate:

- monotonic execution counts;
- zero error outputs;
- no traceback text in markdown;
- no old contaminated metric claims;
- no formal conformal guarantee language;
- explicit n=299 supervised cohort;
- explicit other-disease leakage discussion;
- explicit LAB_AWARE negative-result handling;
- required evidence tables and final manifest.

- [ ] **Step 4: Execute from a clean kernel**

Run:

```bash
python -m jupyter nbconvert --to notebook --execute notebooks/VECTRA_X_Final_Competition_Notebook.ipynb --output VECTRA_X_Final_Competition_Notebook.ipynb --ExecutePreprocessor.timeout=-1
```

Expected: exit code 0 and a fully executed notebook at the same canonical path.

- [ ] **Step 5: Inspect and refine**

Read every markdown section and inspect every output. Correct truncated tables,
unreadable figures, redundant output, unsupported language, or missing
interpretation by editing `scripts/build_final_notebook.py`, rebuilding, and
re-executing until validation passes.

- [ ] **Step 6: Verify GREEN**

Run:

```bash
python scripts/validate_final_notebook.py notebooks/VECTRA_X_Final_Competition_Notebook.ipynb
python -m pytest tests/test_final_notebook_execution.py -v
```

Expected: zero validation findings and all execution tests PASS.

- [ ] **Step 7: Commit**

```bash
git add scripts/validate_final_notebook.py notebooks/VECTRA_X_Final_Competition_Notebook.ipynb tests/test_final_notebook_execution.py
git commit -m "test: execute and validate final competition notebook"
```

### Task 9: Concise Report Sketch and Repository Documentation

**Files:**
- Create: `outputs/reports/final_technical_report_sketch.md`
- Modify: `README.md`
- Create: `tests/test_report_sketch.py`

- [ ] **Step 1: Write failing report tests**

```python
from pathlib import Path


def test_report_sketch_is_concise_and_aligned():
    text = Path("outputs/reports/final_technical_report_sketch.md").read_text(
        encoding="utf-8"
    )
    assert 800 <= len(text.split()) <= 2500
    assert "299" in text
    assert "target-restatement" in text.lower()
    assert "VECTRA_X_Final_Competition_Notebook.ipynb" in text
    assert "placeholder" not in text.lower()
```

- [ ] **Step 2: Verify RED**

Run: `python -m pytest tests/test_report_sketch.py -v`  
Expected: FAIL because the corrected sketch does not exist.

- [ ] **Step 3: Generate the report sketch**

Create a concise formal-English report containing:

1. title and structured abstract;
2. problem and contributions;
3. methods overview;
4. corrected leakage-free findings loaded from notebook workflow outputs;
5. limitations and conclusion;
6. a compact peer-reviewed reference list.

Do not duplicate detailed grids, subgroup tables, or appendix diagnostics.

- [ ] **Step 4: Update README**

Make the final notebook the canonical competition artifact, document its full
execution command, state the n=299 supervised cohort rule, and remove obsolete
contaminated headline metrics.

- [ ] **Step 5: Verify GREEN**

Run: `python -m pytest tests/test_report_sketch.py -v`  
Expected: report tests PASS.

- [ ] **Step 6: Commit**

```bash
git add outputs/reports/final_technical_report_sketch.md README.md tests/test_report_sketch.py
git commit -m "docs: add corrected competition report sketch"
```

### Task 10: Full Verification and Final Audit

**Files:**
- Modify only if verification reveals defects.

- [ ] **Step 1: Run all Python tests**

Run: `python -m pytest tests -v`  
Expected: all tests PASS with zero failures and zero errors.

- [ ] **Step 2: Run static web tests**

Run: `npm.cmd test --prefix web`  
Expected: all web tests PASS.

- [ ] **Step 3: Validate notebook freshness**

Run:

```bash
python scripts/validate_final_notebook.py notebooks/VECTRA_X_Final_Competition_Notebook.ipynb
```

Expected: zero errors, no missing sections, no forbidden claims, and all code
cells executed.

- [ ] **Step 4: Inspect repository diff**

Run:

```bash
git diff --check
git status --short
git diff --stat
```

Expected: no whitespace errors; only intentional files remain modified.

- [ ] **Step 5: Reconcile audit requirements**

Create a final checklist mapping every notebook-priority audit item to a notebook
section, test, table, or explicit limitation. Correct any uncovered gap before
claiming completion.

- [ ] **Step 6: Final commit**

```bash
git add src tests scripts notebooks outputs/reports/final_technical_report_sketch.md requirements.txt README.md config/config.yaml
git commit -m "feat: finalize leakage-free FIT competition notebook"
```
