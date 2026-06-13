from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import joblib

from app import dashboard_config as cfg


@dataclass(frozen=True)
class SchemaValidation:
    is_valid: bool
    missing: tuple[str, ...]
    extra: tuple[str, ...]
    duplicate: tuple[str, ...] = ()


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {} if default is None else default


def load_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, **kwargs)
    except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError):
        return pd.DataFrame()


def available_model_modes(models_dir: Path = cfg.MODELS) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, metadata in cfg.MODEL_MODES.items():
        model_file = metadata["file"]
        result[name] = {
            **metadata,
            "available": bool(model_file and (models_dir / model_file).exists()),
            "path": models_dir / model_file if model_file else None,
        }
    return result


def validate_upload_schema(frame: pd.DataFrame, required_columns: Iterable[str]) -> SchemaValidation:
    required = list(required_columns)
    present = list(frame.columns)
    duplicates = tuple(sorted({c for c in present if present.count(c) > 1}))
    missing = tuple(c for c in required if c not in present)
    extra = tuple(c for c in present if c not in required)
    return SchemaValidation(not missing and not duplicates and not frame.empty, missing, extra, duplicates)


def apply_thresholds(
    probabilities: np.ndarray,
    labels: list[str],
    thresholds: dict[str, float],
) -> np.ndarray:
    values = np.asarray(probabilities, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(labels):
        raise ValueError("Probability matrix shape does not match labels.")
    threshold_array = np.array([float(thresholds.get(label, 0.5)) for label in labels])
    return (values >= threshold_array).astype(int)


def threshold_policy(
    policy_table: pd.DataFrame,
    policy_name: str,
    labels: list[str],
    fallback: dict[str, float] | None = None,
) -> dict[str, float]:
    fallback = fallback or {}
    if policy_table.empty or policy_name not in policy_table.columns or "label" not in policy_table.columns:
        return {label: float(fallback.get(label, 0.5)) for label in labels}
    indexed = policy_table.set_index("label")
    return {
        label: float(indexed.loc[label, policy_name])
        if label in indexed.index and pd.notna(indexed.loc[label, policy_name])
        else float(fallback.get(label, 0.5))
        for label in labels
    }


def load_model_bundle(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Saved model bundle not found: {path}")
    bundle = joblib.load(path)
    required = {"model", "labels", "thresholds"}
    if not isinstance(bundle, dict) or not required.issubset(bundle):
        raise ValueError(f"Incompatible model bundle: expected keys {sorted(required)}.")
    return bundle


def _uncertainty_levels(probabilities: np.ndarray) -> tuple[np.ndarray, list[str]]:
    eps = 1e-9
    clipped = np.clip(probabilities, eps, 1 - eps)
    entropy = -(clipped * np.log2(clipped) + (1 - clipped) * np.log2(1 - clipped)).mean(axis=1)
    levels = [
        "high" if value >= 0.65 else "moderate" if value >= 0.35 else "low"
        for value in entropy
    ]
    return entropy, levels


def predict_with_bundle(
    model_frame: pd.DataFrame,
    bundle: dict[str, Any],
    thresholds: dict[str, float] | None = None,
) -> pd.DataFrame:
    labels = list(bundle["labels"])
    probabilities = np.asarray(bundle["model"].predict_proba(model_frame), dtype=float)
    chosen_thresholds = thresholds or bundle.get("thresholds", {})
    predictions = apply_thresholds(probabilities, labels, chosen_thresholds)
    entropy, uncertainty = _uncertainty_levels(probabilities)
    rows: list[dict[str, Any]] = []
    for row_index in range(len(model_frame)):
        predicted = [labels[j] for j, value in enumerate(predictions[row_index]) if value]
        row: dict[str, Any] = {
            "row_index": row_index,
            "predicted_labels": "{" + ", ".join(predicted) + "}" if predicted else "{none}",
            "max_confidence": round(float(probabilities[row_index].max()), 4),
            "mean_entropy": round(float(entropy[row_index]), 4),
            "uncertainty_level": uncertainty[row_index],
            "inference_scope": (
                "Saved-model probability inference. Cohort conformal and co-infection "
                "models are not applied to uploaded records."
            ),
        }
        for label_index, label in enumerate(labels):
            row[f"prob_{label}"] = round(float(probabilities[row_index, label_index]), 4)
        rows.append(row)
    return pd.DataFrame(rows)


def predict_uploaded_frame(
    raw_frame: pd.DataFrame,
    mode_name: str,
    policy_name: str,
    models_dir: Path = cfg.MODELS,
    policy_path: Path = cfg.TABLES / "threshold_policies.csv",
) -> tuple[pd.DataFrame, SchemaValidation]:
    if mode_name not in cfg.MODEL_MODES:
        raise ValueError(f"Unknown model mode: {mode_name}")
    mode = cfg.MODEL_MODES[mode_name]
    if mode["file"] is None:
        raise ValueError("The full-feature model is research-only and unavailable for uploaded inference.")

    bundle = load_model_bundle(models_dir / mode["file"])
    required = list(bundle.get("feature_set", []))
    validation = validate_upload_schema(raw_frame, required)
    if not validation.is_valid:
        missing_text = ", ".join(validation.missing[:12])
        suffix = " ..." if len(validation.missing) > 12 else ""
        raise ValueError(f"Upload is missing {len(validation.missing)} required columns: {missing_text}{suffix}")

    from src import data_loader
    from src import preprocessing as preprocessing
    from src import report_utils

    project_config = report_utils.load_config()
    reference = data_loader.load_raw(project_config)[required]
    combined = pd.concat([reference, raw_frame[required]], ignore_index=True)
    combined_frame, _ = preprocessing.make_feature_frame(combined, required, project_config)
    expected_columns = list(bundle["model"].meta.all_cols)
    model_frame = combined_frame.iloc[-len(raw_frame) :].copy().reindex(columns=expected_columns)
    policies = load_csv(policy_path)
    thresholds = threshold_policy(policies, policy_name, list(bundle["labels"]), bundle["thresholds"])
    predictions = predict_with_bundle(model_frame, bundle, thresholds)
    uuid_col = project_config["io"]["uuid_col"]
    if uuid_col in raw_frame.columns:
        predictions.insert(0, "uuid", raw_frame[uuid_col].astype(str).values)
    predictions.insert(1 if "uuid" in predictions.columns else 0, "model_mode", mode_name)
    predictions.insert(2 if "uuid" in predictions.columns else 1, "threshold_policy", policy_name)
    return predictions, validation


def parse_label_set(value: Any) -> list[str]:
    text = str(value or "").strip().strip("{}")
    if not text or text.lower() == "none":
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def calculate_resource_capacity(
    patients: pd.DataFrame,
    rapid_tests: int,
    beds: int,
    monitoring_capacity: int,
    staff_capacity: int,
) -> pd.DataFrame:
    triage = patients.get("triage_category", pd.Series(dtype=str)).fillna("")
    uncertainty = patients.get("uncertainty_level", pd.Series(dtype=str)).fillna("")
    urgent = int((triage == "Urgent Response Priority").sum())
    confirm = int(triage.isin(["Confirmatory Test Priority", "Urgent Response Priority"]).sum())
    monitored = int(triage.isin(["Clinical Review", "Confirmatory Test Priority"]).sum())
    manual_review = int(
        triage.isin(["Clinical Review", "Confirmatory Test Priority", "Urgent Response Priority"]).sum()
        + (uncertainty == "high").sum()
    )
    rows = [
        ("Rapid tests", confirm, int(rapid_tests)),
        ("Beds", urgent, int(beds)),
        ("Monitoring slots", monitored, int(monitoring_capacity)),
        ("Staff review slots", manual_review, int(staff_capacity)),
    ]
    return pd.DataFrame(
        [
            {
                "resource": name,
                "demand": demand,
                "capacity": capacity,
                "gap": capacity - demand,
                "status": "Sufficient" if capacity >= demand else "Insufficient",
            }
            for name, demand, capacity in rows
        ]
    )


def dominant_predicted_disease(patients: pd.DataFrame) -> str:
    counts: dict[str, int] = {}
    for value in patients.get("predicted_labels", pd.Series(dtype=str)):
        for label in parse_label_set(value):
            counts[label] = counts.get(label, 0) + 1
    return max(counts, key=counts.get) if counts else "Unavailable"


def patient_markdown_report(patient: pd.Series) -> str:
    return f"""# VECTRA-X Patient Triage Report

**Patient ID:** {patient.get('uuid', 'Unavailable')}

| Decision-support field | Result |
|---|---|
| Predicted labels | {patient.get('predicted_labels', 'Unavailable')} |
| Conformal prediction set | {patient.get('conformal_set', 'Unavailable')} |
| Triage category | {patient.get('triage_category', 'Unavailable')} |
| Triage score | {patient.get('triage_score', 'Unavailable')} |
| Uncertainty | {patient.get('uncertainty_level', 'Unavailable')} |
| Co-infection probability | {patient.get('coinfection_prob', 'Unavailable')} |
| Recommended action | {patient.get('recommended_action', 'Clinical review required.')} |

## Safety Note

This report is generated by a decision support prototype. The predicted labels are
not a confirmed diagnosis and must be reviewed by qualified medical professionals.
"""


def dataframe_csv_bytes(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")
