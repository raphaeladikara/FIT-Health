"""Validate execution integrity and claim safety of the self-contained final notebook.

The FIT submission is a single, self-contained ``.ipynb``: it imports no analysis
package, reads no external configuration, and depends on no precomputed release.
This validator therefore checks the *current* contract:

1. the executed notebook is clean (no error outputs) and fully executed in order;
2. it contains no known over-claim that earlier drafts made (anti-regression);
3. the computed evidence objects the scientific narrative relies on are present as
   ordinary notebook variables (not a removed ``result.*`` workflow object);
4. the required scientific language is present; and
5. the notebook is genuinely self-contained (no analysis-package imports, no
   release-bundle dependency, no in-memory module bootstrap) and carries the
   self-contained submission marker.

Run: ``python scripts/validate_final_notebook.py [notebook.ipynb]``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nbformat


# Computed evidence objects that must exist (as bare notebook variables) so that
# every scientific claim is backed by an executed result in this same notebook.
REQUIRED_RESULT_VARIABLES = [
    "final_test_metrics",
    "final_per_label",
    "final_intervals",
    "calibration_metrics_df",
    "exact_summary",
    "pragmatic_summary",
    "fairness_metrics",
    "leave_one_center_out_results",
    "scenario_sensitivity_table",
    "preprocessing_integrity",
    "fit_rubric_readiness",
    "triage_table",
]

# Over-claims earlier drafts made; their reappearance is a regression.
FORBIDDEN_CLAIMS = [
    "PRE_LAB macro-F1=0.6467",
    "PRE_LAB macro-F1 of 0.6467",
    "other_diseases F1=0.9796",
    "94.8% empirical coverage",
    "formal 90% conformal guarantee",
    "lab-aware/full score higher",
]

# Self-containment red flags. Assembled by concatenation so this validator's own
# source never contains a literal forbidden string.
SELF_CONTAINMENT_FORBIDDEN = [
    "_MODULE" + "_SOURCES",
    "_vectra" + "_lib",
    "run_research" + "_workflow",
    "from " + "src",
    "import " + "src",
    "outputs/" + "releases",
    "sys.path." + "append",
]

SELF_MARKER = "VECTRA_X_SELF_CONTAINED" + "_SUBMISSION_MARKER"


def validate_notebook(path: str | Path) -> dict[str, Any]:
    notebook = nbformat.read(path, as_version=4)
    code_cells = [c for c in notebook.cells if c.cell_type == "code"]
    markdown = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    code = "\n".join(c.source for c in code_cells)
    full_text = markdown + "\n" + code

    execution_counts = [c.execution_count for c in code_cells if c.source.strip()]
    non_null_counts = [count for count in execution_counts if count is not None]
    stale_order = non_null_counts != sorted(non_null_counts) or len(
        non_null_counts
    ) != len(set(non_null_counts))
    error_outputs = sum(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )

    forbidden = [claim for claim in FORBIDDEN_CLAIMS if claim in markdown]
    missing_variables = [v for v in REQUIRED_RESULT_VARIABLES if v not in code]

    lower_md = markdown.lower()
    required_language = {
        "verified cohort n=299": "299" in markdown,
        "other-disease leakage": "other-disease restatement" in lower_md,
        "LAB_AWARE negative result": "negative result" in lower_md,
        "exact/pragmatic separation": (
            "uncapped empirical policy" in lower_md and "pragmatic" in lower_md
        ),
        "decision-support scope": (
            "decision support" in lower_md or "decision-support" in lower_md
        ),
    }
    self_containment_hits = [s for s in SELF_CONTAINMENT_FORBIDDEN if s in full_text]
    marker_present = SELF_MARKER in full_text

    report = {
        "error_outputs": int(error_outputs),
        "code_cells_without_execution_count": sum(
            count is None for count in execution_counts
        ),
        "stale_execution_order": bool(stale_order),
        "forbidden_claims": forbidden,
        "required_result_variables_missing": missing_variables,
        "required_language_missing": [
            name for name, present in required_language.items() if not present
        ],
        "self_containment_violations": self_containment_hits,
        "self_contained_marker_present": bool(marker_present),
        "code_cells": len(code_cells),
        "markdown_cells": sum(c.cell_type == "markdown" for c in notebook.cells),
    }

    report["errors"] = []
    if report["error_outputs"]:
        report["errors"].append("notebook contains error outputs")
    if report["code_cells_without_execution_count"]:
        report["errors"].append("notebook has unexecuted code cells")
    if report["stale_execution_order"]:
        report["errors"].append("notebook execution order is stale")
    if report["forbidden_claims"]:
        report["errors"].append("notebook contains forbidden hard-coded claims")
    if report["required_result_variables_missing"]:
        report["errors"].append("notebook omits required computed evidence variables")
    if report["required_language_missing"]:
        report["errors"].append("notebook omits required scientific language")
    if report["self_containment_violations"]:
        report["errors"].append("notebook is not self-contained")
    if not report["self_contained_marker_present"]:
        report["errors"].append("notebook is missing the self-contained submission marker")

    report["passed_checks"] = [
        name
        for name, ok in {
            "no error outputs": report["error_outputs"] == 0,
            "all cells executed in order": not report["stale_execution_order"]
            and report["code_cells_without_execution_count"] == 0,
            "no forbidden claims": not report["forbidden_claims"],
            "required evidence variables present": not report[
                "required_result_variables_missing"
            ],
            "required language present": not report["required_language_missing"],
            "self-contained": not report["self_containment_violations"]
            and report["self_contained_marker_present"],
        }.items()
        if ok
    ]
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "notebook",
        nargs="?",
        default="notebooks/VECTRA_X_Final.ipynb",
    )
    args = parser.parse_args()
    result = validate_notebook(args.notebook)
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
