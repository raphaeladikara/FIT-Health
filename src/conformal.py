"""conformal — split-conformal multi-label prediction sets.

In a clinical triage setting the model should not be forced to commit to one
disease when the evidence is ambiguous. We implement a documented one-vs-rest
(label-wise) split-conformal procedure that is recall-oriented — it controls
the probability of *missing* a truly present disease:

    For each label j, on a held-out calibration set restricted to the TRUE
    POSITIVES of label j, compute nonconformity s = 1 - p_j. Take the
    (1-alpha) empirical quantile q_j (finite-sample corrected). Include label j
    in a patient's prediction set iff  1 - p_j <= q_j  <=>  p_j >= 1 - q_j.

This guarantees marginal coverage >= 1-alpha for truly-positive cases per label
(i.e. we keep true diseases in the set ~(1-alpha) of the time). Prediction sets
can be empty (=> "no confident disease, escalate for review") or multi-label
(=> "ambiguous, request confirmatory testing").

Limitation (documented): with 300 raw rows, 299 supervised patients, and rare labels
(yellow fever has ~3 test
positives), per-label coverage is a small-sample estimate; we report it with
that caveat rather than claiming a strict guarantee.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def fit_conformal(y_cal: pd.DataFrame, proba_cal: np.ndarray, labels: list[str],
                  alpha: float = 0.10, mode: str = "exact",
                  pragmatic_cap: float = 0.90) -> dict[str, dict[str, float]]:
    """Return per-label conformal info: probability inclusion threshold + q."""
    yt = y_cal.values if isinstance(y_cal, pd.DataFrame) else y_cal
    info: dict[str, dict[str, float]] = {}
    for j, lab in enumerate(labels):
        pos_mask = yt[:, j] == 1
        n_pos = int(pos_mask.sum())
        if n_pos == 0:
            info[lab] = {
                "prob_threshold": 0.5,
                "q": 0.5,
                "n_calibration_pos": 0,
                "quantile_level_finite_sample": np.nan,
                "quantile_level_used": np.nan,
                "mode": mode,
            }
            continue
        scores = 1.0 - proba_cal[pos_mask, j]            # nonconformity on positives
        level = min(1.0, np.ceil((n_pos + 1) * (1 - alpha)) / n_pos)
        if mode not in {"exact", "pragmatic"}:
            raise ValueError("mode must be 'exact' or 'pragmatic'")
        level_used = level if mode == "exact" else min(level, pragmatic_cap)
        q = float(np.quantile(scores, level_used, method="higher"))
        info[lab] = {
            "prob_threshold": float(np.clip(1.0 - q, 0.0, 1.0)),
            "q": q,
            "n_calibration_pos": n_pos,
            "quantile_level_finite_sample": float(level),
            "quantile_level_used": float(level_used),
            "mode": mode,
        }
    return info


def predict_sets(proba: np.ndarray, conformal_info: dict[str, dict[str, float]],
                 labels: list[str]) -> list[list[str]]:
    """Return the conformal prediction set (list of labels) for each row."""
    thresholds = np.array([conformal_info[lab]["prob_threshold"] for lab in labels])
    sets = []
    for row in proba:
        sets.append([labels[j] for j in range(len(labels)) if row[j] >= thresholds[j]])
    return sets


def conformal_metrics(y_true: pd.DataFrame, proba: np.ndarray,
                      conformal_info: dict[str, dict[str, float]],
                      labels: list[str]) -> tuple[pd.DataFrame, dict[str, float]]:
    """Per-label empirical coverage (on true positives) + global summary."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    sets = predict_sets(proba, conformal_info, labels)
    set_label_matrix = np.zeros_like(yt)
    for i, s in enumerate(sets):
        for lab in s:
            set_label_matrix[i, labels.index(lab)] = 1

    rows = []
    for j, lab in enumerate(labels):
        pos = yt[:, j] == 1
        n_pos = int(pos.sum())
        covered = int(set_label_matrix[pos, j].sum()) if n_pos else 0
        rows.append({
            "label": lab,
            "prob_threshold": round(conformal_info[lab]["prob_threshold"], 4),
            "test_positives": n_pos,
            "covered_positives": covered,
            "empirical_coverage": round(covered / n_pos, 4) if n_pos else np.nan,
            "predicted_inclusions": int(set_label_matrix[:, j].sum()),
        })
    per_label = pd.DataFrame(rows)

    set_sizes = np.array([len(s) for s in sets])
    summary = {
        "avg_set_size": round(float(set_sizes.mean()), 4),
        "pct_empty_sets": round(float((set_sizes == 0).mean()) * 100, 2),
        "pct_singletons": round(float((set_sizes == 1).mean()) * 100, 2),
        "singleton_rate": round(float((set_sizes == 1).mean()), 4),
        "pct_ambiguous_multi": round(float((set_sizes > 1).mean()) * 100, 2),
        "overall_coverage": round(
            float(set_label_matrix[yt == 1].mean()) if (yt == 1).any() else np.nan, 4),
        "macro_label_coverage": round(
            float(per_label["empirical_coverage"].mean()), 4
        ),
        "false_negative_risk": round(
            float(1.0 - set_label_matrix[yt == 1].mean())
            if (yt == 1).any() else np.nan,
            4,
        ),
        "policy_name": (
            "exact_uncapped_empirical_policy"
            if next(iter(conformal_info.values())).get("mode") == "exact"
            else "pragmatic_efficiency_policy"
        ),
    }
    return per_label, summary


def set_examples(uuids: pd.Series, proba: np.ndarray, y_true: pd.DataFrame,
                 conformal_info: dict[str, dict[str, float]], labels: list[str],
                 max_rows: int = 40) -> pd.DataFrame:
    """Human-readable prediction-set examples for the report/dashboard."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    sets = predict_sets(proba, conformal_info, labels)
    rows = []
    for i in range(min(max_rows, len(proba))):
        truth = [labels[j] for j in range(len(labels)) if yt[i, j] == 1]
        pset = sets[i]
        if len(pset) == 0:
            interp = "abstain — no confident disease; escalate review"
        elif len(pset) == 1:
            interp = "confident single diagnosis"
        else:
            interp = "ambiguous — request confirmatory testing"
        rows.append({
            "uuid": uuids.iloc[i] if uuids is not None else i,
            "prediction_set": "{" + ", ".join(pset) + "}",
            "set_size": len(pset),
            "true_labels": "{" + ", ".join(truth) + "}",
            "interpretation": interp,
            "max_prob": round(float(proba[i].max()), 3),
        })
    return pd.DataFrame(rows)
