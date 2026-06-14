"""preprocessing — numeric parsing, OUI/NON encoding, missing indicators.

Two layers, kept separate to avoid CV leakage:

1. ``make_feature_frame`` — *stateless* deterministic cleaning that does not
   depend on cross-validation statistics: decimal-comma numeric parsing, blood
   pressure systolic/diastolic extraction, OUI/NON -> 1/0, categorical
   factorisation, high-cardinality text -> presence flag, and per-column
   ``__missing`` indicators (so "unknown" is never confused with "negative").

2. ``build_preprocessor`` — a *stateful* sklearn ``ColumnTransformer`` (median
   imputation for numeric, constant-0 for binary, optional scaling) that is fit
   INSIDE each CV fold via a Pipeline, so imputation never leaks.

Constant columns are dropped here — but logged with the reason, never silently.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from . import report_utils as ru

logger = ru.get_logger(__name__)

_YES = {"oui", "positif", "positive", "yes", "true", "présent", "present", "1", "1.0"}
_NO = {"non", "négatif", "negatif", "negative", "no", "false", "absent", "0", "0.0"}


@dataclass
class FeatureMeta:
    numeric_cols: list[str] = field(default_factory=list)
    binary_cols: list[str] = field(default_factory=list)
    indicator_cols: list[str] = field(default_factory=list)
    dropped_constant: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_map: dict[str, str] = field(default_factory=dict)

    @property
    def all_cols(self) -> list[str]:
        return self.numeric_cols + self.binary_cols + self.indicator_cols


def _parse_numeric(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.replace(",", ".", regex=False)
    s = s.str.extract(r"(-?\d+(?:\.\d+)?)", expand=False)
    return pd.to_numeric(s, errors="coerce")


def parse_blood_pressure(series: pd.Series) -> pd.DataFrame:
    """Extract systolic / diastolic from values like ``77/61``, ``104|58`` or a
    single number, plus a ``bp_parse_failed`` flag."""
    sys_, dia_, failed = [], [], []
    for v in series:
        if pd.isna(v):
            sys_.append(np.nan); dia_.append(np.nan); failed.append(0); continue
        txt = str(v).replace(",", ".")
        nums = re.findall(r"\d+(?:\.\d+)?", txt)
        if len(nums) >= 2:
            sys_.append(float(nums[0])); dia_.append(float(nums[1])); failed.append(0)
        elif len(nums) == 1:
            sys_.append(float(nums[0])); dia_.append(np.nan); failed.append(0)
        else:
            sys_.append(np.nan); dia_.append(np.nan); failed.append(1)
    return pd.DataFrame({
        "bp_systolic": sys_, "bp_diastolic": dia_, "bp_parse_failed": failed
    }, index=series.index)


def _is_binary_col(series: pd.Series) -> bool:
    vals = {str(v).strip().lower() for v in series.dropna().unique()}
    return bool(vals) and vals.issubset(_YES | _NO)


def _encode_binary(series: pd.Series) -> pd.Series:
    s = series.astype("string").str.strip().str.lower()
    return s.map(lambda v: 1.0 if v in _YES else (0.0 if v in _NO else np.nan))


def make_feature_frame(df: pd.DataFrame, feature_cols: list[str],
                       cfg: dict[str, Any] | None = None,
                       missing_indicator_threshold: float = 0.05) -> tuple[pd.DataFrame, FeatureMeta]:
    """Deterministically clean ``feature_cols`` into a numeric design frame.

    Returns ``(X, meta)`` where X may still contain NaN for genuine missing
    values (imputed later, inside CV). Adds ``<col>__missing`` indicators for
    columns missing in more than ``missing_indicator_threshold`` of rows.
    """
    cfg = cfg or ru.load_config()
    pp = cfg["preprocessing"]
    age_frag = pp["age_col_fragment"]
    gender_frag = pp["gender_col_fragment"]
    center_frag = pp["center_col_fragment"]

    out = pd.DataFrame(index=df.index)
    meta = FeatureMeta()
    n = len(df)

    for col in feature_cols:
        s = df[col]
        non_null = s.dropna()
        # --- drop constant columns (logged) --------------------------- #
        if non_null.nunique() <= 1:
            meta.dropped_constant.append(col)
            continue

        name = col.lower()
        missing_rate = s.isna().mean()

        # --- blood pressure -> systolic/diastolic --------------------- #
        if ("pression art" in name) or ("blood pressure" in name):
            bp = parse_blood_pressure(s)
            for c in ["bp_systolic", "bp_diastolic"]:
                out[c] = bp[c]; meta.numeric_cols.append(c); meta.source_map[c] = col
            out["bp_parse_failed"] = bp["bp_parse_failed"]; meta.binary_cols.append("bp_parse_failed")
            meta.source_map["bp_parse_failed"] = col
            if missing_rate > missing_indicator_threshold:
                out["bp__missing"] = s.isna().astype(float); meta.indicator_cols.append("bp__missing")
                meta.source_map["bp__missing"] = col
            continue

        # --- gender ---------------------------------------------------- #
        if gender_frag.lower() in name:
            g = s.astype("string").str.strip().str.lower()
            out["gender_female"] = g.map(lambda v: 1.0 if isinstance(v, str) and v.startswith("f")
                                         else (0.0 if isinstance(v, str) and v.startswith("h") else np.nan))
            meta.binary_cols.append("gender_female")
            meta.source_map["gender_female"] = col
            continue

        # --- health center -------------------------------------------- #
        if center_frag.lower() in name:
            codes, uniques = pd.factorize(s.astype("string").str.strip())
            out["center_code"] = pd.Series(codes, index=s.index).replace(-1, np.nan).astype(float)
            meta.numeric_cols.append("center_code")
            meta.source_map["center_code"] = col
            meta.notes.append(f"center_code factorised: {list(uniques)}")
            continue

        # --- high-cardinality free text -> presence flag -------------- #
        if non_null.nunique() > 15 and (non_null.astype(str).str.len().mean() > 8):
            derived = f"{_alias(col)}__present"
            out[derived] = s.notna().astype(float)
            meta.binary_cols.append(derived)
            meta.source_map[derived] = col
            meta.notes.append(f"high-cardinality text '{col}' -> presence flag (raw text dropped from model)")
            continue

        # --- binary yes/no -------------------------------------------- #
        if _is_binary_col(s):
            out[col] = _encode_binary(s)
            meta.binary_cols.append(col)
            meta.source_map[col] = col
            if missing_rate > missing_indicator_threshold:
                out[f"{col}__missing"] = s.isna().astype(float)
                meta.indicator_cols.append(f"{col}__missing")
                meta.source_map[f"{col}__missing"] = col
            continue

        # --- numeric (incl. age, weight, vitals, labs) ---------------- #
        num = _parse_numeric(s)
        if num.notna().mean() >= 0.5:
            out[col] = num
            meta.numeric_cols.append(col)
            meta.source_map[col] = col
            if missing_rate > missing_indicator_threshold:
                out[f"{col}__missing"] = s.isna().astype(float)
                meta.indicator_cols.append(f"{col}__missing")
                meta.source_map[f"{col}__missing"] = col
            continue

        # --- fallback: low-cardinality categorical -> factorise -------- #
        codes, uniques = pd.factorize(s.astype("string").str.strip())
        out[col] = pd.Series(codes, index=s.index).replace(-1, np.nan).astype(float)
        meta.numeric_cols.append(col)
        meta.source_map[col] = col
        meta.notes.append(f"categorical '{col}' factorised: {list(uniques)[:6]}")

    logger.info(
        "Feature frame: %d cols (%d numeric, %d binary, %d indicators); "
        "dropped %d constant columns.",
        out.shape[1], len(meta.numeric_cols), len(meta.binary_cols),
        len(meta.indicator_cols), len(meta.dropped_constant),
    )
    if meta.dropped_constant:
        logger.info("Dropped constant columns: %s", meta.dropped_constant)
    return out, meta


def assert_no_research_features(
    model_columns: list[str],
    source_map: dict[str, str],
    research_only: set[str],
) -> None:
    """Reject deployable columns derived from a research-only raw feature."""
    violations = [
        f"{column} <- {source_map.get(column, column)}"
        for column in model_columns
        if source_map.get(column, column) in research_only
    ]
    if violations:
        raise ValueError(
            "Deployable design frame contains research-only derived features: "
            + "; ".join(violations)
        )


def _alias(col: str) -> str:
    """Short snake_case alias for a noisy bilingual column name."""
    txt = re.sub(r"\(.*?\)", "", col).strip().lower()
    txt = re.sub(r"[^a-z0-9]+", "_", txt).strip("_")
    return txt[:40] or "feature"


def build_preprocessor(meta: FeatureMeta, scale_numeric: bool = False) -> ColumnTransformer:
    """sklearn ColumnTransformer: median-impute numeric (+optional scale),
    constant-0 impute binary/indicators. Fit inside CV to avoid leakage."""
    numeric_steps: list[tuple[str, Any]] = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    numeric_pipe = Pipeline(numeric_steps)
    binary_pipe = Pipeline([("impute", SimpleImputer(strategy="constant", fill_value=0.0))])

    transformers = []
    if meta.numeric_cols:
        transformers.append(("num", numeric_pipe, meta.numeric_cols))
    bin_all = meta.binary_cols + meta.indicator_cols
    if bin_all:
        transformers.append(("bin", binary_pipe, bin_all))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)
