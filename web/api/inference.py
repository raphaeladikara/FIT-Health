"""Inference using the exact exported preprocessing and model pipelines."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .validation import validate_assessment


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LockedInferenceService:
    def __init__(self, web_root: str | Path | None = None) -> None:
        self.web_root = Path(web_root or Path(__file__).resolve().parents[1])
        self.manifest = json.loads(
            (self.web_root / "data" / "manifest.json").read_text(encoding="utf-8")
        )
        self.input_schema = json.loads(
            (self.web_root / "data" / "input-schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.run_id = self.manifest["notebook_run_id"]
        self.class_order = list(self.manifest["class_order"])
        self.bundles: dict[str, dict[str, Any]] = {}
        for mode, artifact in self.manifest["models"].items():
            path = self.web_root / artifact["path"].removeprefix("web/")
            if not path.exists():
                path = self.web_root.parent / artifact["path"]
            if _sha256(path) != artifact["sha256"]:
                raise ValueError(f"{mode} model-manifest mismatch")
            bundle = joblib.load(path)
            if bundle["run_id"] != self.run_id:
                raise ValueError(f"{mode} model run mismatch")
            if bundle["class_order"] != self.class_order:
                raise ValueError(f"{mode} class order mismatch")
            if bundle["policy_id"] != self.manifest["policy_ids"][mode]:
                raise ValueError(f"{mode} policy mismatch")
            self.bundles[mode] = bundle

    def assess(self, mode: str, values: dict[str, Any]) -> dict[str, Any]:
        if mode not in self.bundles:
            return self._abstention_response(mode, ["UNSUPPORTED_MODE"])
        cleaned, warnings = validate_assessment(values, self.input_schema)
        bundle = self.bundles[mode]
        row = {}
        for column in bundle["design_columns"]:
            value = cleaned.get(column)
            row[column] = np.nan if value is None else value
        frame = pd.DataFrame([row], columns=bundle["design_columns"])
        probability = bundle["model"].predict_proba(frame)[0].astype(float)
        for index, label in enumerate(self.class_order):
            calibrator = bundle["calibrators"].get(label)
            if calibrator is not None:
                probability[index] = calibrator(
                    np.array([probability[index]])
                )[0]
        probability = np.clip(probability, 0.0, 1.0)
        thresholds = bundle["thresholds"]
        decisions = {
            label: bool(probability[index] >= thresholds[label])
            for index, label in enumerate(self.class_order)
        }
        entropy = -(
            probability * np.log2(np.clip(probability, 1e-12, 1))
            + (1 - probability)
            * np.log2(np.clip(1 - probability, 1e-12, 1))
        )
        prediction_set = [
            label
            for index, label in enumerate(self.class_order)
            if probability[index] >= max(0.05, thresholds[label] - 0.1)
        ]
        missing_fraction = (
            sum(value is None for value in cleaned.values()) / len(cleaned)
            if cleaned
            else 1.0
        )
        reasons = []
        if missing_fraction > 0.6:
            reasons.append("INSUFFICIENT_INPUT")
        if warnings:
            reasons.append("OUT_OF_DISTRIBUTION")
        if float(entropy.mean()) >= 0.75:
            reasons.append("HIGH_UNCERTAINTY")
        if len(prediction_set) >= max(4, len(self.class_order)):
            reasons.append("UNINFORMATIVE_SET")
        return {
            "schema_version": "3.0.0",
            "provenance": {
                "run_id": self.run_id,
                "policy_id": bundle["policy_id"],
                "model_hash": self.manifest["models"][mode]["sha256"],
            },
            "mode": mode,
            "probabilities": {
                label: float(probability[index])
                for index, label in enumerate(self.class_order)
            },
            "thresholds": thresholds,
            "decisions": decisions,
            "prediction_set": prediction_set,
            "uncertainty": {
                "mean_entropy": float(entropy.mean()),
                "category": (
                    "high"
                    if entropy.mean() >= 0.75
                    else "moderate"
                    if entropy.mean() >= 0.45
                    else "low"
                ),
            },
            "abstention": {"required": bool(reasons), "reasons": reasons},
            "triage_category": (
                "Clinical review required"
                if reasons or any(decisions.values())
                else "Routine monitoring under local protocol"
            ),
            "explanation": {
                "type": "model_behavior_only",
                "warning": "Feature effects are not causal medical explanations.",
            },
            "warnings": warnings,
            "safe_scope": self.manifest["safe_scope"],
        }

    def _abstention_response(
        self, mode: str, reasons: list[str]
    ) -> dict[str, Any]:
        return {
            "schema_version": "3.0.0",
            "provenance": {"run_id": self.run_id},
            "mode": mode,
            "probabilities": {},
            "thresholds": {},
            "decisions": {},
            "prediction_set": [],
            "uncertainty": {"mean_entropy": None, "category": "unknown"},
            "abstention": {"required": True, "reasons": reasons},
            "triage_category": "Clinical review required",
            "explanation": {
                "type": "unavailable",
                "warning": "No model explanation is available.",
            },
            "warnings": [],
            "safe_scope": self.manifest["safe_scope"],
        }
