"""Selective prediction and explicit-assumption decision scenario analyses."""
from __future__ import annotations

import numpy as np
import pandas as pd


def risk_coverage_table(
    y_true: np.ndarray,
    decisions: np.ndarray,
    uncertainty: np.ndarray,
    labels: list[str],
) -> pd.DataFrame:
    yt = np.asarray(y_true)
    pred = np.asarray(decisions)
    uncertainty = np.asarray(uncertainty, dtype=float)
    order = np.argsort(uncertainty)[::-1]
    rows = []
    n = len(yt)
    for reviewed in range(0, n + 1):
        retained_mask = np.ones(n, dtype=bool)
        retained_mask[order[:reviewed]] = False
        retained = int(retained_mask.sum())
        false_negatives = (
            int(((yt[retained_mask] == 1) & (pred[retained_mask] == 0)).sum())
            if retained
            else 0
        )
        positive_support = int((yt[retained_mask] == 1).sum()) if retained else 0
        rows.append(
            {
                "reviewed_fraction": reviewed / n,
                "retained_fraction": retained / n,
                "retained_patients": retained,
                "false_negative_risk": (
                    false_negatives / positive_support
                    if positive_support
                    else 0.0
                ),
                "positive_support": positive_support,
                "labels": tuple(labels),
            }
        )
    return pd.DataFrame(rows)


def net_benefit_table(
    y_true: np.ndarray,
    probabilities: np.ndarray,
    threshold_probabilities: list[float],
    false_negative_cost: float,
    false_positive_cost: float,
) -> pd.DataFrame:
    y = np.asarray(y_true, dtype=int)
    p = np.asarray(probabilities, dtype=float)
    rows = []
    for threshold in threshold_probabilities:
        decision = p >= threshold
        tp = int(((y == 1) & decision).sum())
        fp = int(((y == 0) & decision).sum())
        fn = int(((y == 1) & ~decision).sum())
        utility = (
            tp - false_positive_cost * fp - false_negative_cost * fn
        ) / len(y)
        rows.append(
            {
                "threshold_probability": float(threshold),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "false_negative_cost": float(false_negative_cost),
                "false_positive_cost": float(false_positive_cost),
                "net_benefit": float(utility),
                "analysis_type": "scenario_analysis",
            }
        )
    return pd.DataFrame(rows)
