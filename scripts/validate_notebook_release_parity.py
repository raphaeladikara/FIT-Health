"""Validate parity across the executed notebook, scientific release, and web."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MARKER = "VECTRA_X_EVIDENCE_SNAPSHOT="


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _notebook_snapshot(path: Path) -> dict[str, Any]:
    notebook = _read_json(path)
    for cell in notebook.get("cells", []):
        for output in cell.get("outputs", []):
            text = output.get("text", [])
            joined = "".join(text) if isinstance(text, list) else str(text)
            for line in joined.splitlines():
                if line.startswith(MARKER):
                    return json.loads(line[len(MARKER):])
    raise ValueError("executed notebook evidence snapshot is missing")


def _indexed(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[tuple, dict]:
    return {tuple(row[key] for key in keys): row for row in rows}


def _compare_rows(
    expected: list[dict[str, Any]],
    actual: list[dict[str, Any]],
    keys: tuple[str, ...],
    fields: tuple[str, ...],
    tolerance: float = 1e-9,
) -> list[str]:
    errors = []
    expected_index = _indexed(expected, keys)
    actual_index = _indexed(actual, keys)
    if set(expected_index) != set(actual_index):
        return [f"row keys differ for {keys}"]
    for key, expected_row in expected_index.items():
        actual_row = actual_index[key]
        for field in fields:
            left = expected_row[field]
            right = actual_row[field]
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if abs(float(left) - float(right)) > tolerance:
                    errors.append(f"{key} {field}: {left} != {right}")
            elif left != right:
                errors.append(f"{key} {field}: {left!r} != {right!r}")
    return errors


def validate_parity(
    notebook_path: str | Path,
    release_path: str | Path,
    manifest_path: str | Path,
    evidence_path: str | Path,
    *,
    verify_notebook_hash: bool = True,
) -> dict[str, list[str]]:
    notebook_path = Path(notebook_path)
    snapshot = _notebook_snapshot(notebook_path)
    release = _read_json(Path(release_path))
    manifest = _read_json(Path(manifest_path))
    evidence = _read_json(Path(evidence_path))
    errors: list[str] = []
    passed: list[str] = []

    policy_ids = {
        snapshot["analysis_policy_id"],
        release["analysis_policy_id"],
        manifest["analysis_policy_id"],
    }
    if len(policy_ids) != 1:
        errors.append("analysis policy IDs differ")
    else:
        passed.append("analysis policy IDs agree")

    if verify_notebook_hash:
        digest = hashlib.sha256(notebook_path.read_bytes()).hexdigest()
        if digest != release["notebook_sha256"] or digest != manifest["notebook_sha256"]:
            errors.append("notebook hashes differ")
        else:
            passed.append("notebook hashes agree")

    aggregate_fields = (
        "model",
        "macro_f1",
        "macro_pr_auc",
        "macro_recall",
        "micro_f1",
    )
    release_aggregate = release["evidence"]["frozen_test"]
    web_aggregate = evidence["validation_and_frozen_test"]["frozen_test"]
    errors.extend(
        _compare_rows(
            snapshot["frozen_test"],
            release_aggregate,
            ("track",),
            aggregate_fields,
        )
    )
    errors.extend(
        _compare_rows(
            release_aggregate,
            web_aggregate,
            ("track",),
            aggregate_fields,
        )
    )
    if not errors:
        passed.append("aggregate metrics agree")

    per_label_fields = (
        "support_pos",
        "precision",
        "recall",
        "f1",
        "pr_auc",
        "fn",
        "fp",
    )
    errors.extend(
        _compare_rows(
            snapshot["per_label"],
            release["evidence"]["per_label"],
            ("track", "label"),
            per_label_fields,
        )
    )
    errors.extend(
        _compare_rows(
            release["evidence"]["per_label"],
            evidence["validation_and_frozen_test"]["per_label"],
            ("track", "label"),
            per_label_fields,
        )
    )
    if not errors:
        passed.append("per-label metrics agree")

    if release["run_id"] != manifest["notebook_run_id"] or release["run_id"] != evidence["run_id"]:
        errors.append("run IDs differ")
    else:
        passed.append("run IDs agree")
    return {"errors": errors, "passed_checks": passed}


def main() -> None:
    latest = _read_json(ROOT / "outputs" / "releases" / "latest.json")
    report = validate_parity(
        ROOT / "VECTRA_X_Final_Submission.ipynb",
        ROOT / latest["release_path"],
        ROOT / "web" / "data" / "manifest.json",
        ROOT / "web" / "data" / "evidence.json",
    )
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
