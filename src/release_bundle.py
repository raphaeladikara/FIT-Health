"""Canonical, privacy-checked scientific release bundle writer."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any

import joblib
import numpy as np
import pandas as pd

FORBIDDEN_KEYS = {
    "patient_id",
    "uuid",
    "row_level_targets",
    "raw_assessment_data",
    "ground_truth",
}


class ReleaseValidationError(ValueError):
    pass


def _walk(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        _json_value(payload),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def content_hash(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_scientific_release(release: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "run_id",
        "source_commit",
        "timestamp",
        "notebook_identity",
        "notebook_sha256",
        "analysis_policy_id",
        "dataset",
        "lock_manifest",
        "policies",
        "metrics",
        "evidence",
        "feature_contract",
        "deployable_input_schema",
        "safe_claims",
        "limitations",
        "deployment_gates",
        "artifacts",
    }
    missing = required - set(release)
    if missing:
        raise ReleaseValidationError(f"missing release fields: {sorted(missing)}")
    if release["source_commit"] != release["lock_manifest"].get("source_commit"):
        raise ReleaseValidationError("source commit disagrees with lock manifest")
    if not release["analysis_policy_id"]:
        raise ReleaseValidationError("analysis policy ID is missing")
    if len(release["notebook_sha256"]) != 64:
        raise ReleaseValidationError("notebook SHA-256 is invalid")
    for metric in release["metrics"]:
        metric_required = {
            "partition",
            "n_patients",
            "positive_support",
            "metric",
            "estimate",
            "lower",
            "upper",
            "method",
        }
        if metric_required - set(metric):
            raise ReleaseValidationError(
                "metric support or interval metadata is missing"
            )
    for policy in release["policies"].values():
        if policy.get("stage") in {"FULL", "RESEARCH_ONLY"}:
            raise ReleaseValidationError(
                "deployable policy contains research-only evidence"
            )
        if not policy.get("model_hash"):
            raise ReleaseValidationError("model hash is missing")
    forbidden = [key for key in _walk(release) if key.lower() in FORBIDDEN_KEYS]
    if forbidden:
        raise ReleaseValidationError(f"private release keys found: {forbidden}")


def write_scientific_release(
    release: dict[str, Any], output_directory: str | Path
) -> Path:
    payload = dict(release)
    payload.pop("content_hash", None)
    validate_scientific_release(payload)
    payload["content_hash"] = hashlib.sha256(
        canonical_json_bytes(payload)
    ).hexdigest()
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "scientific-release.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_bytes(canonical_json_bytes(payload))
    temporary.replace(path)
    return path


def _hash_values(values: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(values)).hexdigest()


def _source_commit(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        numeric = float(value)
        return None if not math.isfinite(numeric) else numeric
    if isinstance(value, np.ndarray):
        return _json_value(value.tolist())
    if isinstance(value, dict):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(child) for child in value]
    return value


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [_json_value(row) for row in frame.to_dict(orient="records")]


def _write_release_figures(
    release: dict[str, Any], release_dir: Path
) -> dict[str, dict[str, str]]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figures_dir = release_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, dict[str, str]] = {}

    per_label = release.get("evidence", {}).get("per_label", [])
    if per_label:
        labels = [str(row["label"]) for row in per_label]
        f1_values = [float(row["f1"]) for row in per_label]
        recall_values = [float(row["recall"]) for row in per_label]
        positions = list(range(len(labels)))
        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.bar([value - 0.18 for value in positions], f1_values, 0.36, label="F1")
        ax.bar(
            [value + 0.18 for value in positions],
            recall_values,
            0.36,
            label="Recall",
        )
        ax.set_xticks(positions, labels, rotation=30, ha="right")
        ax.set_ylim(0, 1)
        ax.set_ylabel("Score")
        ax.set_title("Frozen Test Performance by Label")
        ax.legend()
        fig.tight_layout()
        path = figures_dir / "frozen-test-per-label.png"
        fig.savefig(path, dpi=160, metadata={"Software": "VECTRA-X"})
        plt.close(fig)
        artifacts["frozen_test_per_label"] = {
            "path": path.relative_to(release_dir).as_posix(),
            "sha256": content_hash(path),
        }

    risk_coverage = release.get("evidence", {}).get("risk_coverage", [])
    if risk_coverage:
        fig, ax = plt.subplots(figsize=(7.5, 4.8))
        ax.plot(
            [float(row["coverage"]) for row in risk_coverage],
            [float(row.get("selective_risk", row["risk"])) for row in risk_coverage],
            marker="o",
        )
        ax.set_xlabel("Coverage")
        ax.set_ylabel("Selective risk")
        ax.set_title("Risk-Coverage Profile")
        ax.grid(alpha=0.25)
        fig.tight_layout()
        path = figures_dir / "risk-coverage.png"
        fig.savefig(path, dpi=160, metadata={"Software": "VECTRA-X"})
        plt.close(fig)
        artifacts["risk_coverage"] = {
            "path": path.relative_to(release_dir).as_posix(),
            "sha256": content_hash(path),
        }

    calibration = release.get("evidence", {}).get("calibration", [])
    if calibration:
        by_label: dict[str, dict[str, float]] = {}
        for row in calibration:
            variant = str(row.get("variant", ""))
            slot = "calibrated" if variant.startswith("calibrated") else "raw"
            by_label.setdefault(str(row["label"]), {})[slot] = float(
                row.get(f"{slot}_brier", row["brier"])
            )
        labels = [
            label
            for label, values in by_label.items()
            if {"raw", "calibrated"} <= set(values)
        ]
        raw = [by_label[label]["raw"] for label in labels]
        calibrated = [by_label[label]["calibrated"] for label in labels]
        positions = list(range(len(labels)))
        fig, ax = plt.subplots(figsize=(9, 4.8))
        ax.bar([value - 0.18 for value in positions], raw, 0.36, label="Raw")
        ax.bar(
            [value + 0.18 for value in positions],
            calibrated,
            0.36,
            label="Calibrated",
        )
        ax.set_xticks(positions, labels, rotation=30, ha="right")
        ax.set_ylabel("Brier score (lower is better)")
        ax.set_title("Calibration Quality by Label")
        ax.legend()
        fig.tight_layout()
        path = figures_dir / "calibration-brier.png"
        fig.savefig(path, dpi=160, metadata={"Software": "VECTRA-X"})
        plt.close(fig)
        artifacts["calibration_brier"] = {
            "path": path.relative_to(release_dir).as_posix(),
            "sha256": content_hash(path),
        }

    return artifacts


def export_release_bundle(
    result,
    root: str | Path,
    *,
    schema_version: str = "1.1.0",
    run_id: str | None = None,
) -> Path:
    """Export the workflow result as the sole scientific source of truth."""
    root_path = Path(root)
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    run_id = run_id or timestamp.strftime("%Y%m%dT%H%M%SZ")
    release_dir = root_path / "outputs" / "releases" / run_id
    model_dir = release_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    source_commit = _source_commit(root_path)
    split_hash = _hash_values(
        {
            name: np.asarray(indices).tolist()
            for name, indices in result.frozen_indices.items()
        }
    )
    feature_contract_records = _records(result.feature_contract)
    feature_contract_hash = _hash_values(feature_contract_records)
    policies = {}
    model_artifacts = {}
    input_fields: dict[str, dict[str, Any]] = {}
    for track, model in result.fitted_models.items():
        bundle = {
            "track": track,
            "policy_id": f"{run_id}:{track}",
            "model": model,
            "calibrators": result.calibrators.get(track, {}),
            "thresholds": result.thresholds[track],
            "class_order": result.active_labels,
            "feature_contract_version": feature_contract_hash,
            "design_columns": model.meta.all_cols,
            "run_id": run_id,
            "source_commit": source_commit,
        }
        path = model_dir / f"{track.lower()}.joblib"
        joblib.dump(bundle, path)
        model_hash = content_hash(path)
        model_artifacts[track] = {
            "path": str(path.relative_to(release_dir)).replace("\\", "/"),
            "sha256": model_hash,
        }
        policies[track] = {
            "policy_id": bundle["policy_id"],
            "stage": track,
            "thresholds": result.thresholds[track],
            "calibration": {
                label: getattr(calibrator, "method", "identity")
                for label, calibrator in result.calibrators.get(track, {}).items()
            },
            "model_hash": model_hash,
            "class_order": result.active_labels,
        }
        for column in model.meta.all_cols:
            input_fields.setdefault(
                column,
                {
                    "name": column,
                    "display_label": column,
                    "type": (
                        "category"
                        if column in model.meta.categorical_cols
                        else "number"
                    ),
                    "stage": track,
                    "unit": None,
                    "required": False,
                    "allowed_values": None,
                    "hard_bounds": None,
                    "soft_warning_bounds": None,
                    "missingness_behavior": "allowed; handled by locked pipeline",
                    "clinical_help": "Research input used by the locked model.",
                },
            )
    metrics = []
    intervals = result.final_intervals
    for row in _records(intervals):
        metrics.append(
            {
                "track": row.get("track"),
                "label": row.get("label"),
                "partition": "frozen_test",
                "n_patients": row.get("n"),
                "positive_support": row.get("support_pos"),
                "metric": row.get("metric"),
                "estimate": row.get("estimate"),
                "lower": row.get("lower"),
                "upper": row.get("upper"),
                "method": "patient_percentile_bootstrap",
            }
        )
    lock_manifest = {
        "source_commit": source_commit,
        "split_hash": split_hash,
        "feature_contract_hash": feature_contract_hash,
        "selected_config": {
            row["track"]: row["selected_model"]
            for row in _records(result.selection_audit)
        },
        "thresholds": result.thresholds,
        "calibration_method": "training_oof_per_label",
        "seeds": result.config.get("project", {}).get("random_state", 42),
    }
    analysis_policy_id = _hash_values(
        {
            "active_labels": result.active_labels,
            "selected_policy": lock_manifest["selected_config"],
            "thresholds": {
                track: {
                    label: round(float(value), 6)
                    for label, value in thresholds.items()
                }
                for track, thresholds in result.thresholds.items()
            },
            "n_supervised": result.cohort_audit["n_supervised"],
        }
    )[:16]
    notebook_path = root_path / "VECTRA_X_Final_Submission.ipynb"
    release = {
        "schema_version": schema_version,
        "run_id": run_id,
        "source_commit": source_commit,
        "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
        "notebook_identity": "VECTRA_X_Final_Submission.ipynb",
        "notebook_sha256": content_hash(notebook_path),
        "analysis_policy_id": analysis_policy_id,
        "dataset": {
            "fingerprint": content_hash(root_path / "data" / "raw" / "data.csv"),
            "cohort_counts": {
                **result.cohort_audit,
                "training": len(result.frozen_indices["train"]),
                "frozen_test": len(result.frozen_indices["test"]),
            },
            "partition_labels": ["training_pool", "frozen_test"],
            "split_hash": split_hash,
        },
        "lock_manifest": lock_manifest,
        "policies": policies,
        "metrics": metrics,
        "evidence": {
            "cohort_audit": result.cohort_audit,
            "leakage": _records(result.leakage_audit),
            "baselines": _records(result.baselines),
            "ablations": _records(result.ablations),
            "validation": _records(result.repeated_validation),
            "frozen_test": _records(result.final_test_metrics),
            "per_label": _records(result.final_per_label),
            "calibration": _records(result.calibration_metrics),
            "prediction_sets": {
                "exact": _records(result.conformal_exact),
                "exact_summary": result.conformal_exact_summary,
                "pragmatic": _records(result.conformal_pragmatic),
                "pragmatic_summary": result.conformal_pragmatic_summary,
            },
            "risk_coverage": _records(result.selective_risk),
            "fairness": _records(result.fairness_metrics),
            "center_transfer": _records(result.leave_one_center_out),
            "scenarios": _records(result.scenario_sensitivity),
        },
        "feature_contract": {
            "version": feature_contract_hash,
            "features": feature_contract_records,
        },
        "deployable_input_schema": {"fields": list(input_fields.values())},
        "safe_claims": _records(result.safe_claims),
        "limitations": [
            "Small frozen-test support for rare labels.",
            "Two-center evidence does not establish broad transportability.",
            "No prospective clinical validation or measured treatment impact.",
        ],
        "deployment_gates": [
            "External prospective validation",
            "Platform rate limiting",
            "Clinical governance approval",
        ],
        "artifacts": {"models": model_artifacts, "figures": {}},
    }
    release["artifacts"]["figures"] = _write_release_figures(release, release_dir)
    release_path = write_scientific_release(release, release_dir)
    latest = root_path / "outputs" / "releases" / "latest.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_bytes(
        canonical_json_bytes(
            {
                "run_id": run_id,
                "release_path": str(release_path.relative_to(root_path)).replace(
                    "\\", "/"
                ),
                "content_hash": content_hash(release_path),
            }
        )
    )
    return release_path


def refresh_release_figures(release_path: str | Path, root: str | Path) -> Path:
    """Regenerate hashed presentation figures without changing scientific values."""
    path = Path(release_path).resolve()
    release = json.loads(path.read_text(encoding="utf-8"))
    release.pop("content_hash", None)
    release["artifacts"]["figures"] = _write_release_figures(release, path.parent)
    written_path = write_scientific_release(release, path.parent)

    root_path = Path(root).resolve()
    latest_path = root_path / "outputs" / "releases" / "latest.json"
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    latest["content_hash"] = content_hash(written_path)
    latest_path.write_bytes(canonical_json_bytes(latest))
    return written_path
