"""Export privacy-safe dashboard artifacts for the static Next.js application."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUTS = ROOT / "outputs"
DEFAULT_DESTINATION = ROOT / "web" / "public" / "data"
CONFIG_PATH = ROOT / "config" / "config.yaml"
SCHEMA_VERSION = 2

# The execution profile that produces competition-grade, reproducible artifacts.
CANONICAL_PROFILE = "full"
# Headline test_metrics are computed on the held-out split (patient records remain OOF).
DEFAULT_EVALUATION_MODE = "held_out"
# Per-label thresholds applied to patient decisions by default.
DEFAULT_THRESHOLD_POLICY = "operational"
# The deployable model track that produces the triage dashboard records.
DASHBOARD_MODEL_TRACK = "PRE_LAB"
# Patient records are out-of-fold predictions over the full cohort, not held-out test rows.
DASHBOARD_RECORD_SOURCE = "full_cohort_oof"

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


def _sha256(path: Path) -> str:
    """Stream a file through SHA-256 so large artifacts do not load into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _model_versions(summary: dict[str, Any]) -> dict[str, str]:
    """Honest per-track model identity from the pipeline's best-model selection."""
    tracks = summary.get("best_model_per_track", {})
    if not isinstance(tracks, dict):
        return {}
    return {str(track): str(model) for track, model in tracks.items()}


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


def _load_thresholds(
    tables_dir: Path, policy: str, active_labels: list[str]
) -> dict[str, float]:
    """Per-label decision thresholds for ``policy`` from threshold_policies.csv.

    Fails the export when an active label has no tuned threshold so the dashboard
    can never silently fall back to a misleading fixed 0.50 cutoff.
    """
    path = tables_dir / "threshold_policies.csv"
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard artifact is missing: {path}")
    frame = pd.read_csv(path)
    if "label" not in frame.columns or policy not in frame.columns:
        raise ValueError(
            f"threshold_policies.csv must contain 'label' and {policy!r} columns; "
            f"found {list(frame.columns)}"
        )
    mapping = {str(row["label"]): float(row[policy]) for _, row in frame.iterrows()}
    missing = [label for label in active_labels if label not in mapping]
    if missing:
        raise ValueError(
            f"No {policy!r} threshold for active label(s): {missing}"
        )
    return {label: mapping[label] for label in active_labels}


def _public_patients(
    frame: pd.DataFrame,
    thresholds: dict[str, float],
    active_labels: list[str],
    threshold_policy: str,
) -> list[dict[str, Any]]:
    public = frame.drop(columns=list(PRIVATE_COLUMNS), errors="ignore").copy()
    public.insert(0, "case_id", [f"Case {index + 1:03d}" for index in range(len(public))])
    records = _records(public)

    for record in records:
        decisions: dict[str, dict[str, Any]] = {}
        predicted: list[str] = []
        for label in active_labels:
            raw = record.get(f"calprob_{label}")
            probability = float(raw) if raw is not None else 0.0
            threshold = thresholds[label]
            is_predicted = probability >= threshold
            decisions[label] = {
                "probability": probability,
                "threshold": threshold,
                "predicted": is_predicted,
            }
            if is_predicted:
                predicted.append(label)
        # Keep the displayed prediction set consistent with the thresholds we show,
        # so the chip, the probability bar, and the threshold marker never disagree.
        record["label_decisions"] = decisions
        record["predicted_labels"] = (
            "{" + (", ".join(predicted) if predicted else "none") + "}"
        )
        record["model_track"] = DASHBOARD_MODEL_TRACK
        record["threshold_policy"] = threshold_policy
        record["record_source"] = DASHBOARD_RECORD_SOURCE
    return records


def export_dashboard_data(
    outputs_dir: Path,
    destination: Path,
    *,
    require_canonical: bool = False,
) -> dict[str, Any]:
    """Export validated public artifacts and return the generated manifest.

    When ``require_canonical`` is set, the export refuses to publish artifacts that
    were not produced by the canonical (``full``) pipeline profile, so that headline
    competition metrics can never be replaced by a quick-smoke development run.
    """
    outputs_dir = Path(outputs_dir)
    destination = Path(destination)
    tables_dir = outputs_dir / "tables"
    summary_path = outputs_dir / "dashboard_data" / "summary.json"
    patient_path = tables_dir / "vectra_triage_dashboard_data.csv"

    summary = _load_required_json(summary_path)
    patient_frame = _load_required_csv(patient_path)

    active_labels = list(summary.get("active_labels", []))
    threshold_policy = summary.get("threshold_policy", DEFAULT_THRESHOLD_POLICY)
    thresholds = _load_thresholds(tables_dir, threshold_policy, active_labels)
    patients = _public_patients(
        patient_frame, thresholds, active_labels, threshold_policy
    )

    execution_profile = summary.get("execution_profile", "unknown")
    canonical = execution_profile == CANONICAL_PROFILE
    if require_canonical and not canonical:
        raise ValueError(
            "Refusing official export: artifacts are not canonical "
            f"(execution_profile={execution_profile!r}, expected {CANONICAL_PROFILE!r}). "
            "Run the full pipeline before exporting with --require-canonical."
        )

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

    generated_at = datetime.now(UTC).isoformat()
    git_commit = _git_commit()
    data_checksum = _sha256(patient_path)
    config_checksum = _sha256(CONFIG_PATH) if CONFIG_PATH.exists() else "unavailable"
    evaluation_mode = summary.get("evaluation_mode", DEFAULT_EVALUATION_MODE)
    run_id = "-".join(
        [
            generated_at[:10].replace("-", ""),
            git_commit[:8],
            data_checksum[:8],
            config_checksum[:8],
        ]
    )

    if not canonical:
        warnings.insert(
            0,
            f"Development artifact: execution_profile={execution_profile!r} "
            "is not the canonical competition run.",
        )

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "git_commit": git_commit,
        "data_checksum": data_checksum,
        "config_checksum": config_checksum,
        "generated_at": generated_at,
        "execution_profile": execution_profile,
        "canonical": canonical,
        "evaluation_mode": evaluation_mode,
        "threshold_policy": threshold_policy,
        "model_versions": _model_versions(summary),
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
    parser.add_argument(
        "--require-canonical",
        action="store_true",
        help="Fail unless artifacts come from the canonical (full) pipeline profile.",
    )
    args = parser.parse_args()
    manifest = export_dashboard_data(
        args.outputs, args.destination, require_canonical=args.require_canonical
    )
    print(
        f"Exported {manifest['patient_count']} public patient records to "
        f"{args.destination.resolve()}"
    )
    print(
        f"  run_id={manifest['run_id']} canonical={manifest['canonical']} "
        f"profile={manifest['execution_profile']}"
    )
    if manifest["warnings"]:
        print(f"Completed with {len(manifest['warnings'])} warning(s).")


if __name__ == "__main__":
    main()
