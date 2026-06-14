"""calibration — probability calibration + reliability assessment.

For triage, probabilities must be trustworthy, not just rank-correct. We assess
calibration on out-of-fold / held-out probabilities (Brier score, Expected
Calibration Error, reliability curves) and provide light Platt/isotonic
recalibration fit on a dedicated calibration split (so it never leaks into the
model's own training data).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold


def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    return float(np.mean((y_prob - y_true) ** 2))


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray,
                               n_bins: int = 10) -> float:
    """Binned ECE: weighted |confidence - accuracy| across probability bins."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(y_prob, bins[1:-1], right=True)
    ece, n = 0.0, len(y_true)
    for b in range(n_bins):
        mask = idx == b
        if not mask.any():
            continue
        conf = y_prob[mask].mean()
        acc = y_true[mask].mean()
        ece += (mask.sum() / n) * abs(conf - acc)
    return float(ece)


def reliability_curve(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10
                      ) -> pd.DataFrame:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(y_prob, bins[1:-1], right=True)
    rows = []
    for b in range(n_bins):
        mask = idx == b
        if not mask.any():
            continue
        rows.append({
            "bin_mid": (bins[b] + bins[b + 1]) / 2,
            "mean_pred": float(y_prob[mask].mean()),
            "frac_pos": float(y_true[mask].mean()),
            "count": int(mask.sum()),
        })
    return pd.DataFrame(rows)


def calibration_metrics(y_true: pd.DataFrame, y_proba: np.ndarray,
                        labels: list[str], n_bins: int = 10) -> pd.DataFrame:
    """Per-label Brier + ECE (+ base rate for context)."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    rows = []
    for j, lab in enumerate(labels):
        t, p = yt[:, j], y_proba[:, j]
        rows.append({
            "label": lab,
            "base_rate": round(float(t.mean()), 4),
            "brier": round(brier_score(t, p), 4),
            "ece": round(expected_calibration_error(t, p, n_bins), 4),
            "mean_pred": round(float(p.mean()), 4),
        })
    return pd.DataFrame(rows)


def fit_calibrator(y_true: np.ndarray, y_prob: np.ndarray, method: str = "auto"):
    """Fit a 1-D calibrator on (prob -> calibrated prob).

    'sigmoid' (Platt) is the default for tiny positive counts; isotonic is used
    only when there is enough signal. Returns a callable prob -> prob.
    """
    n_pos = int(y_true.sum())
    if method == "auto":
        method = "isotonic" if n_pos >= 25 and len(y_true) >= 100 else "sigmoid"
    if len(np.unique(y_true)) < 2:
        const = float(y_true.mean())
        return lambda p: np.full_like(np.asarray(p, dtype=float), const)
    if method == "isotonic":
        iso = IsotonicRegression(out_of_bounds="clip")
        iso.fit(y_prob, y_true)
        return lambda p: iso.predict(np.clip(p, 0, 1))
    lr = LogisticRegression(C=1e6, solver="lbfgs")
    lr.fit(y_prob.reshape(-1, 1), y_true)
    return lambda p: lr.predict_proba(np.asarray(p).reshape(-1, 1))[:, 1]


def calibrate_matrix(y_true_cal: pd.DataFrame, proba_cal: np.ndarray,
                     proba_target: np.ndarray, labels: list[str],
                     method: str = "auto") -> tuple[np.ndarray, dict]:
    """Fit per-label calibrators on a calibration split and apply to a target
    probability matrix. Returns (calibrated_matrix, calibrators)."""
    yt = y_true_cal.values if isinstance(y_true_cal, pd.DataFrame) else y_true_cal
    out = np.zeros_like(proba_target)
    calibrators = {}
    for j, lab in enumerate(labels):
        cal = fit_calibrator(yt[:, j], proba_cal[:, j], method=method)
        calibrators[lab] = cal
        out[:, j] = np.clip(cal(proba_target[:, j]), 0, 1)
    return out, calibrators


def cross_fitted_calibration(
    y_true: pd.DataFrame,
    proba: np.ndarray,
    n_splits: int = 5,
    random_state: int = 42,
    method: str = "auto",
) -> tuple[np.ndarray, pd.DataFrame]:
    """Calibrate every row using a calibrator fitted on complementary rows."""
    yt = y_true.to_numpy() if isinstance(y_true, pd.DataFrame) else np.asarray(y_true)
    labels = (
        list(y_true.columns)
        if isinstance(y_true, pd.DataFrame)
        else [f"label_{j}" for j in range(yt.shape[1])]
    )
    out = np.zeros_like(proba, dtype=float)
    rows = []
    splitter = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for fold, (cal_idx, target_idx) in enumerate(splitter.split(yt)):
        for j, label in enumerate(labels):
            calibrator = fit_calibrator(
                yt[cal_idx, j], proba[cal_idx, j], method=method
            )
            out[target_idx, j] = np.clip(
                calibrator(proba[target_idx, j]), 0.0, 1.0
            )
            for idx in target_idx:
                rows.append(
                    {
                        "target_index": int(idx),
                        "label": label,
                        "fold": fold,
                        "calibration_indices": tuple(int(i) for i in cal_idx),
                        "n_calibration": len(cal_idx),
                        "support_pos": int(yt[cal_idx, j].sum()),
                    }
                )
    return out, pd.DataFrame(rows)
