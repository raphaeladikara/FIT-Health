"""fairness — subgroup robustness & domain-shift audit.

Axes available in this dataset: health center (CMA de DAFRA / CMA de DO),
gender, and age group. We report per-subgroup macro-F1, per-label recall and
false-negative rate, plus a Leave-One-Center-Out (LOCO) stress test — the
strongest generalisation check for a 2-facility clinical dataset.

Aligned with the competition's well-being / humanitarian theme: the goal is to
show the model does not systematically under-detect a disease for one subgroup.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, recall_score

from . import modeling as M
from . import preprocessing as pp
from . import report_utils as ru

logger = ru.get_logger(__name__)


def age_groups(age: pd.Series) -> pd.Series:
    bins = [-0.1, 5, 12, 18, 50, 200]
    names = ["infant_<=5", "child_6_12", "adolescent_13_18", "adult_19_50", "elderly_>50"]
    return pd.cut(pd.to_numeric(age, errors="coerce"), bins=bins, labels=names)


def subgroup_metrics(y_true: pd.DataFrame, y_pred: np.ndarray, labels: list[str],
                     subgroups: dict[str, pd.Series]) -> pd.DataFrame:
    """Macro-F1, per-label recall & FNR for each subgroup level."""
    yt = y_true.values if isinstance(y_true, pd.DataFrame) else y_true
    rows = []
    for axis, series in subgroups.items():
        series = series.reset_index(drop=True)
        for level in series.dropna().unique():
            mask = (series == level).to_numpy(dtype=bool, na_value=False)
            if mask.sum() < 3:
                continue
            sub_t, sub_p = yt[mask], y_pred[mask]
            row = {"axis": axis, "level": str(level), "n": int(mask.sum()),
                   "macro_f1": round(f1_score(sub_t, sub_p, average="macro", zero_division=0), 4)}
            for j, lab in enumerate(labels):
                pos = int(sub_t[:, j].sum())
                row[f"recall_{lab}"] = (round(recall_score(sub_t[:, j], sub_p[:, j],
                                        zero_division=0), 4) if pos else np.nan)
            rows.append(row)
    return pd.DataFrame(rows)


def recall_gap(subgroup_df: pd.DataFrame, axis: str, labels: list[str]) -> pd.DataFrame:
    """Max-min recall gap across the levels of one axis, per label."""
    sub = subgroup_df[subgroup_df["axis"] == axis]
    rows = []
    for lab in labels:
        col = f"recall_{lab}"
        if col not in sub.columns:
            continue
        vals = sub[["level", col]].dropna()
        if len(vals) < 2:
            continue
        rows.append({
            "axis": axis, "label": lab,
            "max_recall": round(float(vals[col].max()), 4),
            "min_recall": round(float(vals[col].min()), 4),
            "recall_gap": round(float(vals[col].max() - vals[col].min()), 4),
            "worst_level": str(vals.loc[vals[col].idxmin(), "level"]),
        })
    return pd.DataFrame(rows)


def leave_one_center_out(model_name: str, meta: pp.FeatureMeta, X: pd.DataFrame,
                         y: pd.DataFrame, center: pd.Series, labels: list[str],
                         random_state: int) -> pd.DataFrame:
    """Train on one center, evaluate on the other (both directions)."""
    center = center.reset_index(drop=True)
    centers = [c for c in center.dropna().unique()]
    rows = []
    if len(centers) < 2:
        return pd.DataFrame()
    for test_c in centers:
        tr = (center != test_c).to_numpy(dtype=bool, na_value=False)
        te = (center == test_c).to_numpy(dtype=bool, na_value=False)
        if tr.sum() < 10 or te.sum() < 5:
            continue
        m = M.BinaryRelevanceModel(model_name, meta, random_state)
        m.fit(X.iloc[tr], y.iloc[tr])
        proba = m.predict_proba(X.iloc[te])
        pred = (proba >= 0.5).astype(int)
        yt = y.iloc[te].values
        row = {"train_on": "others", "test_on": str(test_c), "n_test": int(te.sum()),
               "macro_f1": round(f1_score(yt, pred, average="macro", zero_division=0), 4),
               "micro_f1": round(f1_score(yt, pred, average="micro", zero_division=0), 4)}
        for j, lab in enumerate(labels):
            pos = int(yt[:, j].sum())
            row[f"recall_{lab}"] = (round(recall_score(yt[:, j], pred[:, j],
                                    zero_division=0), 4) if pos else np.nan)
        rows.append(row)
    return pd.DataFrame(rows)


def build_subgroups(df_features_raw: pd.DataFrame, X_clean: pd.DataFrame,
                    raw_df: pd.DataFrame, cfg: dict) -> dict[str, pd.Series]:
    """Assemble subgroup series (gender, center, age group) from available cols."""
    subs: dict[str, pd.Series] = {}
    pp_cfg = cfg["preprocessing"]
    # gender
    gcol = next((c for c in raw_df.columns if pp_cfg["gender_col_fragment"].lower() in c.lower()), None)
    if gcol is not None:
        subs["gender"] = raw_df[gcol].astype("string").str.strip()
    # center
    ccol = next((c for c in raw_df.columns if pp_cfg["center_col_fragment"].lower() in c.lower()), None)
    if ccol is not None:
        subs["center"] = raw_df[ccol].astype("string").str.strip()
    # age group
    acol = next((c for c in raw_df.columns if pp_cfg["age_col_fragment"].lower() in c.lower()), None)
    if acol is not None:
        subs["age_group"] = age_groups(raw_df[acol]).astype("string")
    return subs
