"""Research-grade evaluation helpers for the final competition notebook."""
from __future__ import annotations

from collections.abc import Callable, Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    recall_score,
    roc_auc_score,
)


def baseline_predictions(
    kind: str,
    n_rows: int,
    labels: list[str],
    prevalence: dict[str, float] | None = None,
    random_state: int = 42,
) -> np.ndarray:
    """Generate transparent multi-label reference predictions."""
    out = np.zeros((n_rows, len(labels)), dtype=int)
    if kind == "always_malaria":
        if "malaria" in labels:
            out[:, labels.index("malaria")] = 1
        return out
    if kind == "prevalence":
        prevalence = prevalence or {}
        out[:] = np.array(
            [int(prevalence.get(label, 0.0) >= 0.5) for label in labels],
            dtype=int,
        )
        return out
    if kind == "random_prevalence":
        prevalence = prevalence or {}
        rng = np.random.default_rng(random_state)
        for j, label in enumerate(labels):
            out[:, j] = rng.binomial(1, prevalence.get(label, 0.0), n_rows)
        return out
    raise ValueError(f"Unknown baseline kind: {kind}")


def _metric_value(y_true: np.ndarray, values: np.ndarray, metric: str) -> float:
    if metric == "f1":
        return float(f1_score(y_true, values, zero_division=0))
    if metric == "recall":
        return float(recall_score(y_true, values, zero_division=0))
    if metric == "roc_auc":
        return float(roc_auc_score(y_true, values))
    if metric == "pr_auc":
        return float(average_precision_score(y_true, values))
    if metric == "accuracy":
        return float(np.mean(y_true == values))
    raise ValueError(f"Unsupported metric: {metric}")


def bootstrap_metric_interval(
    y_true: np.ndarray,
    y_pred_or_score: np.ndarray,
    metric: str,
    n_boot: int = 2000,
    random_state: int = 42,
) -> dict[str, float | int]:
    """Percentile bootstrap interval with deterministic invalid-draw handling."""
    y_true = np.asarray(y_true)
    values = np.asarray(y_pred_or_score)
    estimate = _metric_value(y_true, values, metric)
    rng = np.random.default_rng(random_state)
    draws: list[float] = []
    attempts = 0
    max_attempts = max(n_boot * 10, 100)
    while len(draws) < n_boot and attempts < max_attempts:
        idx = rng.integers(0, len(y_true), len(y_true))
        attempts += 1
        if metric in {"roc_auc", "pr_auc"} and np.unique(y_true[idx]).size < 2:
            continue
        draws.append(_metric_value(y_true[idx], values[idx], metric))
    if not draws:
        lower = upper = float("nan")
    else:
        lower, upper = np.quantile(draws, [0.025, 0.975])
    return {
        "estimate": round(estimate, 6),
        "lower": round(float(lower), 6),
        "upper": round(float(upper), 6),
        "n": int(len(y_true)),
        "support_pos": int(y_true.sum()),
        "valid_draws": len(draws),
    }


def paired_bootstrap_difference(
    y_true: np.ndarray,
    pred_a: np.ndarray,
    pred_b: np.ndarray,
    metric: str,
    n_boot: int = 2000,
    random_state: int = 42,
) -> dict[str, float | int]:
    """Paired interval for metric(A) - metric(B) on identical patients."""
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    estimate = _metric_value(y_true, pred_a, metric) - _metric_value(
        y_true, pred_b, metric
    )
    rng = np.random.default_rng(random_state)
    draws = []
    attempts = 0
    while len(draws) < n_boot and attempts < max(n_boot * 10, 100):
        idx = rng.integers(0, len(y_true), len(y_true))
        attempts += 1
        if metric in {"roc_auc", "pr_auc"} and np.unique(y_true[idx]).size < 2:
            continue
        draws.append(
            _metric_value(y_true[idx], pred_a[idx], metric)
            - _metric_value(y_true[idx], pred_b[idx], metric)
        )
    lower, upper = (
        np.quantile(draws, [0.025, 0.975]) if draws else (np.nan, np.nan)
    )
    return {
        "estimate": round(float(estimate), 6),
        "lower": round(float(lower), 6),
        "upper": round(float(upper), 6),
        "valid_draws": len(draws),
    }


def selective_risk_curve(
    correct: np.ndarray,
    uncertainty: np.ndarray,
) -> pd.DataFrame:
    """Observed error after deferring progressively uncertain cases."""
    correct = np.asarray(correct, dtype=float)
    uncertainty = np.asarray(uncertainty, dtype=float)
    order = np.argsort(uncertainty)
    rows = []
    for retained in range(len(correct), 0, -1):
        idx = order[:retained]
        rows.append(
            {
                "coverage": retained / len(correct),
                "retained": retained,
                "risk": float(1.0 - correct[idx].mean()),
                "uncertainty_cutoff": float(uncertainty[idx].max()),
            }
        )
    return pd.DataFrame(rows)


def repeated_multilabel_validation(
    evaluate_seed: Callable[[int], dict[str, float]],
    seeds: Iterable[int],
) -> pd.DataFrame:
    """Collect seed-level metrics and append mean/interval summaries."""
    rows = [{"seed": seed, **evaluate_seed(seed)} for seed in seeds]
    return pd.DataFrame(rows)


def evaluate_feature_ablation(
    evaluate_columns: Callable[[list[str]], dict[str, float]],
    feature_groups: dict[str, list[str]],
) -> pd.DataFrame:
    """Evaluate cumulative named feature groups through a caller-owned protocol."""
    rows = []
    cumulative: list[str] = []
    for group, columns in feature_groups.items():
        cumulative.extend(c for c in columns if c not in cumulative)
        rows.append(
            {
                "feature_group": group,
                "n_features": len(cumulative),
                **evaluate_columns(cumulative),
            }
        )
    return pd.DataFrame(rows)
