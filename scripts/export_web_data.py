"""Export privacy-safe dashboard artifacts for the static Next.js application."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUTS = ROOT / "outputs"
DEFAULT_DESTINATION = ROOT / "web" / "public" / "data"
SCHEMA_VERSION = 1

PRIVATE_COLUMNS = {
    "uuid",
    "_uuid",
    "true_labels",
    "ground_truth",
    "patient_id",
}

EVIDENCE_TABLES = {
    "model_leaderboard": "model_leaderboard.csv",
    "per_label_metrics": "per_label_metrics.csv",
    "calibration_metrics": "calibration_metrics.csv",
    "conformal_metrics": "conformal_metrics.csv",
    "fairness_metrics": "fairness_metrics.csv",
    "fairness_recall_gaps": "fairness_recall_gaps.csv",
    "center_transfer": "leave_one_center_out.csv",
    "feature_importance_global": "feature_importance_global.csv",
    "leakage_candidates": "leakage_candidates.csv",
    "confidence_intervals": "headline_metric_bootstrap_ci.csv",
    "label_prevalence_intervals": "label_prevalence_confidence_intervals.csv",
    "threshold_policy_tradeoff": "threshold_policy_resource_tradeoff.csv",
}


def _json_value(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, float) and np.isnan(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _load_required_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard artifact is missing: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Required dashboard artifact is not valid JSON: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Required dashboard artifact must contain an object: {path}")
    return value


def _load_required_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard artifact is missing: {path}")
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"Required dashboard artifact is empty: {path}")
    return frame


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _public_patients(frame: pd.DataFrame) -> list[dict[str, Any]]:
    public = frame.drop(columns=list(PRIVATE_COLUMNS), errors="ignore").copy()
    public.insert(0, "case_id", [f"Case {index + 1:03d}" for index in range(len(public))])
    return _records(public)


def export_dashboard_data(outputs_dir: Path, destination: Path) -> dict[str, Any]:
    """Export validated public artifacts and return the generated manifest."""
    outputs_dir = Path(outputs_dir)
    destination = Path(destination)
    tables_dir = outputs_dir / "tables"
    summary_path = outputs_dir / "dashboard_data" / "summary.json"
    patient_path = tables_dir / "vectra_triage_dashboard_data.csv"

    summary = _load_required_json(summary_path)
    patient_frame = _load_required_csv(patient_path)
    patients = _public_patients(patient_frame)

    destination.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []
    evidence: dict[str, list[dict[str, Any]]] = {}
    available: list[str] = []

    for key, filename in EVIDENCE_TABLES.items():
        path = tables_dir / filename
        if not path.exists():
            warnings.append(f"Optional dashboard artifact is missing: {filename}")
            evidence[key] = []
            continue
        frame = pd.read_csv(path)
        evidence[key] = _records(frame)
        available.append(filename)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "execution_profile": summary.get("execution_profile", "unknown"),
        "patient_count": len(patients),
        "active_labels": summary.get("active_labels", []),
        "available_evidence": available,
        "warnings": warnings,
    }

    _write_json(destination / "manifest.json", manifest)
    _write_json(destination / "summary.json", summary)
    _write_json(destination / "patients.json", patients)
    _write_json(destination / "evidence.json", evidence)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    manifest = export_dashboard_data(args.outputs, args.destination)
    print(
        f"Exported {manifest['patient_count']} public patient records to "
        f"{args.destination.resolve()}"
    )
    if manifest["warnings"]:
        print(f"Completed with {len(manifest['warnings'])} optional-artifact warning(s).")


if __name__ == "__main__":
    main()
