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

    @property
    def all_cols(self) -> list[str]:
        return self.numeric_cols + self.binary_cols + self.indicator_cols


@dataclass
class _FittedColumn:
    source: str
    kind: str
    outputs: list[str]
    categories: list[str] = field(default_factory=list)
    add_missing: bool = False


@dataclass
class FittedFeatureFrame:
    """Train-fitted deterministic feature-frame transformer.

    Unlike :func:`make_feature_frame`, every data-dependent decision is learned
    in ``fit`` and then frozen. Unknown categories at transform time map to an
    all-zero one-hot block and never create new columns.
    """

    missing_indicator_threshold: float = 0.05
    cfg: dict[str, Any] | None = None
    columns_: list[_FittedColumn] = field(default_factory=list)
    meta_: FeatureMeta = field(default_factory=FeatureMeta)
    feature_cols_: list[str] = field(default_factory=list)

    @property
    def meta(self) -> FeatureMeta:
        return self.meta_

    def fit(self, df: pd.DataFrame, feature_cols: list[str]) -> "FittedFeatureFrame":
        self.cfg = self.cfg or ru.load_config()
        self.feature_cols_ = list(feature_cols)
        self.columns_ = []
        self.meta_ = FeatureMeta()
        pp_cfg = self.cfg["preprocessing"]
        gender_frag = pp_cfg["gender_col_fragment"].lower()

        for col in self.feature_cols_:
            s = df[col]
            non_null = s.dropna()
            if non_null.nunique() <= 1:
                self.meta_.dropped_constant.append(col)
                continue

            name = col.lower()
            add_missing = s.isna().mean() > self.missing_indicator_threshold
            if ("pression art" in name) or ("blood pressure" in name):
                outputs = [f"{_alias(col)}__systolic", f"{_alias(col)}__diastolic"]
                self.columns_.append(_FittedColumn(col, "blood_pressure", outputs, add_missing=add_missing))
                self.meta_.numeric_cols.extend(outputs)
                parse_flag = f"{_alias(col)}__parse_failed"
                self.meta_.binary_cols.append(parse_flag)
                if add_missing:
                    self.meta_.indicator_cols.append(f"{_alias(col)}__missing")
                continue

            if gender_frag in name:
                output = f"{_alias(col)}__female"
                self.columns_.append(_FittedColumn(col, "gender", [output], add_missing=add_missing))
                self.meta_.binary_cols.append(output)
                if add_missing:
                    self.meta_.indicator_cols.append(f"{_alias(col)}__missing")
                continue

            if _is_binary_col(s):
                self.columns_.append(_FittedColumn(col, "binary", [col], add_missing=add_missing))
                self.meta_.binary_cols.append(col)
                if add_missing:
                    self.meta_.indicator_cols.append(f"{col}__missing")
                continue

            numeric = _parse_numeric(s)
            if numeric.notna().mean() >= 0.5:
                self.columns_.append(_FittedColumn(col, "numeric", [col], add_missing=add_missing))
                self.meta_.numeric_cols.append(col)
                if add_missing:
                    self.meta_.indicator_cols.append(f"{col}__missing")
                continue

            if non_null.nunique() > 15 and non_null.astype(str).str.len().mean() > 8:
                output = f"{_alias(col)}__present"
                self.columns_.append(_FittedColumn(col, "presence", [output]))
                self.meta_.binary_cols.append(output)
                self.meta_.notes.append(f"high-cardinality text '{col}' -> presence flag")
                continue

            categories = sorted(str(v).strip() for v in non_null.unique())
            outputs = [
                f"{_alias(col)}__cat_{index}_{_alias(value)}"
                for index, value in enumerate(categories)
            ]
            self.columns_.append(
                _FittedColumn(col, "categorical", outputs, categories=categories, add_missing=add_missing)
            )
            self.meta_.binary_cols.extend(outputs)
            self.meta_.notes.append(
                f"categorical '{col}' one-hot encoded from train categories: {categories[:8]}"
            )
            if add_missing:
                self.meta_.indicator_cols.append(f"{_alias(col)}__missing")
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if not self.feature_cols_:
            raise RuntimeError("FittedFeatureFrame must be fit before transform.")
        missing_sources = [c for c in self.feature_cols_ if c not in df.columns]
        if missing_sources:
            raise ValueError(f"Missing fitted source columns: {missing_sources}")

        out = pd.DataFrame(index=df.index)
        for spec in self.columns_:
            s = df[spec.source]
            alias = _alias(spec.source)
            if spec.kind == "blood_pressure":
                parsed = parse_blood_pressure(s)
                out[spec.outputs[0]] = parsed["bp_systolic"]
                out[spec.outputs[1]] = parsed["bp_diastolic"]
                out[f"{alias}__parse_failed"] = parsed["bp_parse_failed"].astype(float)
            elif spec.kind == "gender":
                values = s.astype("string").str.strip().str.lower()
                out[spec.outputs[0]] = values.map(
                    lambda v: 1.0 if isinstance(v, str) and v.startswith("f")
                    else (0.0 if isinstance(v, str) and v.startswith("h") else np.nan)
                )
            elif spec.kind == "binary":
                out[spec.outputs[0]] = _encode_binary(s)
            elif spec.kind == "numeric":
                out[spec.outputs[0]] = _parse_numeric(s)
            elif spec.kind == "presence":
                out[spec.outputs[0]] = s.notna().astype(float)
            elif spec.kind == "categorical":
                values = s.astype("string").str.strip()
                for category, output in zip(spec.categories, spec.outputs):
                    out[output] = (values == category).astype(float)
            if spec.add_missing:
                missing_name = (
                    f"{spec.source}__missing"
                    if spec.kind in {"binary", "numeric"}
                    else f"{alias}__missing"
                )
                out[missing_name] = s.isna().astype(float)
        return out.reindex(columns=self.meta_.all_cols)

    def fit_transform(self, df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
        return self.fit(df, feature_cols).transform(df)


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
                out[c] = bp[c]; meta.numeric_cols.append(c)
            out["bp_parse_failed"] = bp["bp_parse_failed"]; meta.binary_cols.append("bp_parse_failed")
            if missing_rate > missing_indicator_threshold:
                out["bp__missing"] = s.isna().astype(float); meta.indicator_cols.append("bp__missing")
            continue

        # --- gender ---------------------------------------------------- #
        if gender_frag.lower() in name:
            g = s.astype("string").str.strip().str.lower()
            out["gender_female"] = g.map(lambda v: 1.0 if isinstance(v, str) and v.startswith("f")
                                         else (0.0 if isinstance(v, str) and v.startswith("h") else np.nan))
            meta.binary_cols.append("gender_female")
            continue

        # --- health center -------------------------------------------- #
        if center_frag.lower() in name:
            codes, uniques = pd.factorize(s.astype("string").str.strip())
            out["center_code"] = pd.Series(codes, index=s.index).replace(-1, np.nan).astype(float)
            meta.numeric_cols.append("center_code")
            meta.notes.append(f"center_code factorised: {list(uniques)}")
            continue

        # --- high-cardinality free text -> presence flag -------------- #
        if non_null.nunique() > 15 and (non_null.astype(str).str.len().mean() > 8):
            out[f"{_alias(col)}__present"] = s.notna().astype(float)
            meta.binary_cols.append(f"{_alias(col)}__present")
            meta.notes.append(f"high-cardinality text '{col}' -> presence flag (raw text dropped from model)")
            continue

        # --- binary yes/no -------------------------------------------- #
        if _is_binary_col(s):
            out[col] = _encode_binary(s)
            meta.binary_cols.append(col)
            if missing_rate > missing_indicator_threshold:
                out[f"{col}__missing"] = s.isna().astype(float)
                meta.indicator_cols.append(f"{col}__missing")
            continue

        # --- numeric (incl. age, weight, vitals, labs) ---------------- #
        num = _parse_numeric(s)
        if num.notna().mean() >= 0.5:
            out[col] = num
            meta.numeric_cols.append(col)
            if missing_rate > missing_indicator_threshold:
                out[f"{col}__missing"] = s.isna().astype(float)
                meta.indicator_cols.append(f"{col}__missing")
            continue

        # --- fallback: low-cardinality categorical -> factorise -------- #
        codes, uniques = pd.factorize(s.astype("string").str.strip())
        out[col] = pd.Series(codes, index=s.index).replace(-1, np.nan).astype(float)
        meta.numeric_cols.append(col)
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
