"""Judge-facing scientific evidence helpers for VECTRA-X."""
from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(package: str) -> str:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def build_provenance_manifest(
    root: Path,
    data_path: Path,
    config_path: Path,
    execution_mode: str,
) -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        commit = "unavailable"
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "execution_mode": execution_mode,
        "git_commit": commit,
        "data_path": str(data_path.relative_to(root)),
        "data_sha256": sha256_file(data_path),
        "config_path": str(config_path.relative_to(root)),
        "config_sha256": sha256_file(config_path),
        "package_versions": {
            "python": platform.python_version(),
            "pandas": _version("pandas"),
            "numpy": _version("numpy"),
            "scikit-learn": _version("scikit-learn"),
            "iterative-stratification": _version("iterative-stratification"),
            "xgboost": _version("xgboost"),
            "lightgbm": _version("lightgbm"),
        },
    }


def wilson_interval(positive: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        return np.nan, np.nan
    p = positive / total
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    return max(0.0, center - margin), min(1.0, center + margin)


def prevalence_intervals(y: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label in y.columns:
        positives = int(y[label].sum())
        low, high = wilson_interval(positives, len(y))
        rows.append(
            {
                "label": label,
                "positives": positives,
                "total": len(y),
                "prevalence": positives / len(y),
                "ci_low": low,
                "ci_high": high,
            }
        )
    return pd.DataFrame(rows)


def center_label_prevalence(
    centers: pd.Series, y: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    clean_centers = centers.astype("string").fillna("Missing")
    for center in sorted(clean_centers.unique()):
        mask = clean_centers == center
        for label in y.columns:
            positives = int(y.loc[mask, label].sum())
            low, high = wilson_interval(positives, int(mask.sum()))
            rows.append(
                {
                    "center": center,
                    "label": label,
                    "positives": positives,
                    "support": int(mask.sum()),
                    "prevalence": positives / max(1, int(mask.sum())),
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    return pd.DataFrame(rows)


def missingness_dependence(
    frame: pd.DataFrame,
    groups: dict[str, pd.Series],
    top_n: int = 20,
) -> pd.DataFrame:
    missing_rates = frame.isna().mean().sort_values(ascending=False)
    columns = list(missing_rates.head(top_n).index)
    rows = []
    for axis, values in groups.items():
        clean = values.astype("string").fillna("Missing")
        for level in sorted(clean.unique()):
            mask = clean == level
            for column in columns:
                rows.append(
                    {
                        "axis": axis,
                        "level": level,
                        "feature": column,
                        "support": int(mask.sum()),
                        "missing_rate": float(frame.loc[mask, column].isna().mean()),
                    }
                )
    return pd.DataFrame(rows)


def decision_curve_net_benefit(
    y_true: Iterable[int],
    y_score: Iterable[float],
    thresholds: Iterable[float] | None = None,
) -> pd.DataFrame:
    truth = np.asarray(list(y_true), dtype=int)
    score = np.asarray(list(y_score), dtype=float)
    thresholds = list(thresholds or np.linspace(0.05, 0.80, 16))
    prevalence = float(truth.mean())
    rows = []
    for threshold in thresholds:
        pred = score >= threshold
        tp = int(((pred == 1) & (truth == 1)).sum())
        fp = int(((pred == 1) & (truth == 0)).sum())
        weight = threshold / (1 - threshold)
        rows.extend(
            [
                {
                    "threshold": threshold,
                    "strategy": "model",
                    "net_benefit": tp / len(truth) - fp / len(truth) * weight,
                },
                {
                    "threshold": threshold,
                    "strategy": "test_all",
                    "net_benefit": prevalence - (1 - prevalence) * weight,
                },
                {"threshold": threshold, "strategy": "test_none", "net_benefit": 0.0},
            ]
        )
    return pd.DataFrame(rows)
