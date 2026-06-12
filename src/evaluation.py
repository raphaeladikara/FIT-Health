"""evaluation — multi-label and per-label metrics + threshold optimisation.

Accuracy is deliberately de-emphasised: malaria covers 90% of rows, so subset
accuracy and micro metrics can hide failure on rare labels. The reporting set
follows the blueprint's evaluation protocol (macro F1, per-label recall, AUCPR,
Hamming loss, Jaccard) with threshold-aware variants.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    hamming_loss,
    jaccard_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def _safe_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    try:
        return float(roc_auc_score(y_true, y_score))
    except Exception:
        return float("nan")


def _safe_ap(y_true: np.ndarray, y_score: np.ndarray) -> float:
    if len(np.unique(y_true)) < 2:
        return float("nan")
    try:
        return float(average_precision_score(y_true, y_score))
    except Exception:
        return float("nan")


def multilabel_summary(y_true: pd.DataFrame, y_pred: np.ndarray,
                       y_proba: np.ndarray | None = None) -> dict[str, float]:
    """Aggregate multi-label metrics (threshold already applied to y_pred)."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    out = {
        "micro_f1": f1_score(yt, y_pred, average="micro", zero_division=0),
        "macro_f1": f1_score(yt, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(yt, y_pred, average="weighted", zero_division=0),
        "samples_f1": f1_score(yt, y_pred, average="samples", zero_division=0),
        "hamming_loss": hamming_loss(yt, y_pred),
        "subset_accuracy": float((yt == y_pred).all(axis=1).mean()),
        "jaccard_samples": jaccard_score(yt, y_pred, average="samples", zero_division=0),
        "macro_recall": recall_score(yt, y_pred, average="macro", zero_division=0),
        "macro_precision": precision_score(yt, y_pred, average="macro", zero_division=0),
    }
    if y_proba is not None:
        aucs = [_safe_auc(yt[:, j], y_proba[:, j]) for j in range(yt.shape[1])]
        aps = [_safe_ap(yt[:, j], y_proba[:, j]) for j in range(yt.shape[1])]
        out["macro_roc_auc"] = float(np.nanmean(aucs))
        out["macro_pr_auc"] = float(np.nanmean(aps))
    return {k: round(float(v), 4) for k, v in out.items()}


def per_label_metrics(y_true: pd.DataFrame, y_pred: np.ndarray,
                      y_proba: np.ndarray, labels: list[str]) -> pd.DataFrame:
    """Per-label precision/recall/F1/ROC-AUC/PR-AUC + confusion counts."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    rows = []
    for j, lab in enumerate(labels):
        t, p, s = yt[:, j], y_pred[:, j], y_proba[:, j]
        cm = confusion_matrix(t, p, labels=[0, 1])
        tn, fp, fn, tp = (cm.ravel() if cm.size == 4 else (0, 0, 0, 0))
        rows.append({
            "label": lab,
            "support_pos": int(t.sum()),
            "precision": round(precision_score(t, p, zero_division=0), 4),
            "recall": round(recall_score(t, p, zero_division=0), 4),
            "f1": round(f1_score(t, p, zero_division=0), 4),
            "roc_auc": round(_safe_auc(t, s), 4),
            "pr_auc": round(_safe_ap(t, s), 4),
            "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
            "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) else 0.0,
        })
    return pd.DataFrame(rows)


def optimise_threshold(y_true: np.ndarray, y_score: np.ndarray,
                       objective: str = "f1",
                       recall_floor: float = 0.0,
                       grid: np.ndarray | None = None) -> tuple[float, float]:
    """Find the probability threshold maximising an objective for one label.

    objective:
        'f1'             maximise F1
        'recall_at_prec' maximise recall subject to precision >= recall_floor
        'balanced'       maximise (precision*recall) balance (F1 with floor)
    Returns ``(threshold, achieved_objective_value)``.
    """
    if grid is None:
        grid = np.linspace(0.05, 0.95, 19)
    best_t, best_v = 0.5, -1.0
    for t in grid:
        pred = (y_score >= t).astype(int)
        if len(np.unique(y_true)) < 2:
            continue
        prec = precision_score(y_true, pred, zero_division=0)
        rec = recall_score(y_true, pred, zero_division=0)
        f1 = f1_score(y_true, pred, zero_division=0)
        if objective == "recall_at_prec":
            value = rec if prec >= recall_floor else rec * 0.5
        elif objective == "balanced":
            value = f1 if rec >= recall_floor else f1 * 0.5
        else:
            value = f1
        if value > best_v:
            best_v, best_t = value, float(t)
    return best_t, round(best_v, 4)


def apply_thresholds(y_proba: np.ndarray, thresholds: dict[str, float],
                     labels: list[str]) -> np.ndarray:
    """Apply per-label thresholds to a probability matrix -> binary matrix."""
    out = np.zeros_like(y_proba, dtype=int)
    for j, lab in enumerate(labels):
        out[:, j] = (y_proba[:, j] >= thresholds.get(lab, 0.5)).astype(int)
    return out
