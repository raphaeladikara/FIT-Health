"""Validate execution integrity and claim safety of the final notebook."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import nbformat


REQUIRED_RESULT_REFERENCES = {
    "final_test_metrics": "result.final_test_metrics",
    "final_per_label": "result.final_per_label",
    "final_intervals": "result.final_intervals",
    "calibration_metrics": "result.calibration_metrics",
    "conformal_exact": "result.conformal_exact",
    "fairness_metrics": "result.fairness_metrics",
    "leave_one_center_out": "result.leave_one_center_out",
    "scenario_sensitivity": "result.scenario_sensitivity",
}

FORBIDDEN_CLAIMS = [
    "PRE_LAB macro-F1=0.6467",
    "PRE_LAB macro-F1 of 0.6467",
    "other_diseases F1=0.9796",
    "94.8% empirical coverage",
    "formal 90% conformal guarantee",
    "lab-aware/full score higher",
]


def validate_notebook(path: str | Path) -> dict[str, Any]:
    notebook = nbformat.read(path, as_version=4)
    code_cells = [c for c in notebook.cells if c.cell_type == "code"]
    markdown = "\n".join(c.source for c in notebook.cells if c.cell_type == "markdown")
    code = "\n".join(c.source for c in code_cells)
    execution_counts = [
        c.execution_count for c in code_cells if c.source.strip()
    ]
    error_outputs = sum(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )
    non_null_counts = [count for count in execution_counts if count is not None]
    stale_order = non_null_counts != sorted(non_null_counts) or len(
        non_null_counts
    ) != len(set(non_null_counts))
    forbidden = [claim for claim in FORBIDDEN_CLAIMS if claim in markdown]
    missing_tables = [
        name
        for name, reference in REQUIRED_RESULT_REFERENCES.items()
        if reference not in code
    ]
    required_language = {
        "verified cohort n=299": "299" in markdown or "299" in code,
        "other-disease leakage": "other-disease restatement" in markdown.lower(),
        "LAB_AWARE negative result": "negative result" in markdown.lower(),
        "exact/pragmatic separation": (
            "exact empirical policy" in markdown.lower()
            and "pragmatic policy" in markdown.lower()
        ),
    }
    report = {
        "error_outputs": int(error_outputs),
        "code_cells_without_execution_count": sum(
            count is None for count in execution_counts
        ),
        "stale_execution_order": bool(stale_order),
        "forbidden_claims": forbidden,
        "required_result_tables_missing": missing_tables,
        "required_language_missing": [
            name for name, present in required_language.items() if not present
        ],
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
    if report["required_result_tables_missing"]:
        report["errors"].append("notebook omits required release-backed tables")
    if report["required_language_missing"]:
        report["errors"].append("notebook omits required scientific language")
    report["warnings"] = []
    report["passed_checks"] = [
        "required result references present"
        if not report["required_result_tables_missing"]
        else ""
    ]
    report["passed_checks"] = [item for item in report["passed_checks"] if item]
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
