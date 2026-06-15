"""preprocessing — numeric parsing, OUI/NON encoding, missing indicators.

Two layers, kept separate to avoid CV leakage:

1. ``make_feature_frame`` — *stateless* deterministic cleaning that does not
   depend on cross-validation statistics: decimal-comma numeric parsing, blood
   pressure systolic/diastolic extraction, OUI/NON -> 1/0, raw categorical
   strings preserved verbatim (no factorisation / ordinal codes), high-cardinality
   text -> presence flag, and per-column ``__missing`` indicators (so "unknown"
   is never confused with "negative").

2. ``build_preprocessor`` — a *stateful* sklearn ``ColumnTransformer`` (median
   imputation for numeric, constant-0 for binary, and
   ``OneHotEncoder(handle_unknown="ignore")`` for nominal categories, optional
   scaling) that is fit INSIDE each CV fold via a Pipeline, so neither imputation
   statistics nor one-hot categories ever leak from validation/test rows.

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
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import report_utils as ru

logger = ru.get_logger(__name__)

_YES = {"oui", "positif", "positive", "yes", "true", "présent", "present", "1", "1.0"}
_NO = {"non", "négatif", "negatif", "negative", "no", "false", "absent", "0", "0.0"}


@dataclass
class FeatureMeta:
    numeric_cols: list[str] = field(default_factory=list)
    binary_cols: list[str] = field(default_factory=list)
    categorical_cols: list[str] = field(default_factory=list)
    indicator_cols: list[str] = field(default_factory=list)
    dropped_constant: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    source_map: dict[str, str] = field(default_factory=dict)
    availability_stage: dict[str, str] = field(default_factory=dict)
    missingness_indicators: dict[str, str] = field(default_factory=dict)

    @property
    def all_cols(self) -> list[str]:
        return (
            self.numeric_cols
            + self.binary_cols
            + self.categorical_cols
            + self.indicator_cols
        )


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


@dataclass
class _ColumnPlan:
    """A single learned instruction: how one raw column becomes model columns."""
    kind: str           # bp | gender | categorical | highcard | binary | numeric
    source: str         # raw column name
    outputs: list[str]  # derived column names, in output order
    has_missing: bool = False


class FeatureFrameBuilder:
    """Learn the deployable feature schema from TRAINING ROWS ONLY, then apply it
    deterministically to any frame.

    ``fit(df_train)`` inspects the training rows to decide, for each raw column:
    its type (numeric / binary / categorical), whether it is near-constant and
    therefore dropped, whether a high-cardinality free-text field collapses to a
    presence flag, and whether the column earns an explicit ``<col>__missing``
    indicator. ``transform(df)`` reproduces exactly those columns, in the learned
    order, for *any* frame:

    * unseen category levels are preserved verbatim (the fold-local one-hot encoder
      ignores them at fit time, so no global vocabulary is needed);
    * an unrecognised binary token maps to missing and is imputed inside the fold;
    * an absent source column yields all-missing derived columns; and
    * extra columns in the input are ignored.

    No held-out validation row and no frozen-test row ever influences a schema
    decision, which closes the test-distribution leakage channel that fitting the
    schema on the full cohort would open.
    """

    def __init__(self, feature_cols, cfg: dict[str, Any] | None = None,
                 missing_indicator_threshold: float = 0.05):
        self.feature_cols = list(feature_cols)
        self.cfg = cfg
        self.missing_indicator_threshold = missing_indicator_threshold
        self.meta_: FeatureMeta | None = None
        self.plan_: list[_ColumnPlan] | None = None
        self.output_columns_: list[str] | None = None
        self.n_fit_rows_: int | None = None

    # Schema learning (training rows only)
    def fit(self, df: pd.DataFrame, y=None) -> "FeatureFrameBuilder":
        cfg = self.cfg or ru.load_config()
        pp = cfg["preprocessing"]
        gender_frag = pp["gender_col_fragment"].lower()
        center_frag = pp["center_col_fragment"].lower()
        thr = self.missing_indicator_threshold

        meta = FeatureMeta()
        plan: list[_ColumnPlan] = []
        for col in self.feature_cols:
            if col not in df.columns:
                # A declared feature absent from the fitting frame cannot be typed.
                continue
            s = df[col]
            non_null = s.dropna()
            # Drop near-constant columns (logged)
            if non_null.nunique() <= 1:
                meta.dropped_constant.append(col)
                continue

            name = col.lower()
            has_missing = bool(s.isna().mean() > thr)

            # Blood pressure -> systolic/diastolic
            if ("pression art" in name) or ("blood pressure" in name):
                outs = ["bp_systolic", "bp_diastolic", "bp_parse_failed"]
                meta.numeric_cols += ["bp_systolic", "bp_diastolic"]
                meta.binary_cols.append("bp_parse_failed")
                for c in outs:
                    meta.source_map[c] = col
                if has_missing:
                    outs.append("bp__missing")
                    meta.indicator_cols.append("bp__missing")
                    meta.source_map["bp__missing"] = col
                plan.append(_ColumnPlan("bp", col, outs, has_missing))
                continue

            # Gender
            if gender_frag in name:
                meta.binary_cols.append("gender_female")
                meta.source_map["gender_female"] = col
                plan.append(_ColumnPlan("gender", col, ["gender_female"]))
                continue

            # Health center
            if center_frag in name:
                meta.categorical_cols.append(col)
                meta.source_map[col] = col
                plan.append(_ColumnPlan("categorical", col, [col]))
                continue

            # High-cardinality free text -> presence flag
            if non_null.nunique() > 15 and (non_null.astype(str).str.len().mean() > 8):
                derived = f"{_alias(col)}__present"
                meta.binary_cols.append(derived)
                meta.source_map[derived] = col
                meta.notes.append(
                    f"high-cardinality text '{col}' -> presence flag (raw text dropped from model)"
                )
                plan.append(_ColumnPlan("highcard", col, [derived]))
                continue

            # Binary yes/no
            if _is_binary_col(s):
                meta.binary_cols.append(col)
                meta.source_map[col] = col
                outs = [col]
                if has_missing:
                    outs.append(f"{col}__missing")
                    meta.indicator_cols.append(f"{col}__missing")
                    meta.source_map[f"{col}__missing"] = col
                plan.append(_ColumnPlan("binary", col, outs, has_missing))
                continue

            # Numeric (incl. age, weight, vitals, labs)
            num = _parse_numeric(s)
            if num.notna().mean() >= 0.5:
                meta.numeric_cols.append(col)
                meta.source_map[col] = col
                outs = [col]
                if has_missing:
                    outs.append(f"{col}__missing")
                    meta.indicator_cols.append(f"{col}__missing")
                    meta.source_map[f"{col}__missing"] = col
                plan.append(_ColumnPlan("numeric", col, outs, has_missing))
                continue

            # Fallback: preserve categories for fold-local encoding
            meta.categorical_cols.append(col)
            meta.source_map[col] = col
            meta.notes.append(f"categorical '{col}' preserved for fold-local encoding")
            plan.append(_ColumnPlan("categorical", col, [col]))

        self.meta_ = meta
        self.plan_ = plan
        self.output_columns_ = [c for p in plan for c in p.outputs]
        self.n_fit_rows_ = int(len(df))
        logger.info(
            "Feature schema (fit on %d rows): %d cols (%d numeric, %d binary, "
            "%d categorical, %d indicators); dropped %d near-constant columns.",
            self.n_fit_rows_, len(self.output_columns_), len(meta.numeric_cols),
            len(meta.binary_cols), len(meta.categorical_cols),
            len(meta.indicator_cols), len(meta.dropped_constant),
        )
        if meta.dropped_constant:
            logger.info("Dropped near-constant columns: %s", meta.dropped_constant)
        return self

    # Deterministic application (any rows)
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.plan_ is None:
            raise RuntimeError("FeatureFrameBuilder.transform called before fit")
        out = pd.DataFrame(index=df.index)
        for p in self.plan_:
            present = p.source in df.columns
            s = df[p.source] if present else pd.Series(np.nan, index=df.index)
            if p.kind == "bp":
                if present:
                    bp = parse_blood_pressure(s)
                    out["bp_systolic"] = bp["bp_systolic"]
                    out["bp_diastolic"] = bp["bp_diastolic"]
                    out["bp_parse_failed"] = bp["bp_parse_failed"]
                else:
                    out["bp_systolic"] = np.nan
                    out["bp_diastolic"] = np.nan
                    out["bp_parse_failed"] = np.nan
                if p.has_missing:
                    out["bp__missing"] = s.isna().astype(float)
            elif p.kind == "gender":
                g = s.astype("string").str.strip().str.lower()
                out["gender_female"] = g.map(
                    lambda v: 1.0 if isinstance(v, str) and v.startswith("f")
                    else (0.0 if isinstance(v, str) and v.startswith("h") else np.nan)
                )
            elif p.kind == "categorical":
                category = s.astype("string").str.strip()
                out[p.source] = category.astype(object).where(category.notna(), np.nan)
            elif p.kind == "highcard":
                out[p.outputs[0]] = s.notna().astype(float)
            elif p.kind == "binary":
                out[p.source] = _encode_binary(s)
                if p.has_missing:
                    out[f"{p.source}__missing"] = s.isna().astype(float)
            elif p.kind == "numeric":
                out[p.source] = _parse_numeric(s)
                if p.has_missing:
                    out[f"{p.source}__missing"] = s.isna().astype(float)
        # Deterministic, learned column order regardless of the rows transformed.
        return out.reindex(columns=self.output_columns_)

    def fit_transform(self, df: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(df).transform(df)


def make_feature_frame(df: pd.DataFrame, feature_cols: list[str],
                       cfg: dict[str, Any] | None = None,
                       missing_indicator_threshold: float = 0.05) -> tuple[pd.DataFrame, FeatureMeta]:
    """Deterministically clean ``feature_cols`` into a numeric design frame.

    Convenience wrapper that fits a :class:`FeatureFrameBuilder` on ``df`` and
    transforms the same ``df``. When the rows used to *decide* the schema differ
    from the rows being transformed (e.g. fit on the training pool, transform the
    full cohort), use :class:`FeatureFrameBuilder` directly so that the schema
    never sees held-out rows.

    Returns ``(X, meta)`` where X may still contain NaN for genuine missing
    values (imputed later, inside CV). Adds ``<col>__missing`` indicators for
    columns missing in more than ``missing_indicator_threshold`` of rows.
    """
    builder = FeatureFrameBuilder(
        feature_cols, cfg=cfg, missing_indicator_threshold=missing_indicator_threshold
    ).fit(df)
    return builder.transform(df), builder.meta_


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
    numeric_steps: list[tuple[str, Any]] = [
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True))
    ]
    if scale_numeric:
        numeric_steps.append(("scale", StandardScaler()))
    numeric_pipe = Pipeline(numeric_steps)
    binary_pipe = Pipeline([
        (
            "impute",
            SimpleImputer(
                strategy="constant",
                fill_value=0.0,
                keep_empty_features=True,
            ),
        )
    ])
    categorical_pipe = Pipeline(
        [
            (
                "impute",
                SimpleImputer(
                    strategy="constant",
                    fill_value="__MISSING__",
                    keep_empty_features=True,
                ),
            ),
            (
                "encode",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                    dtype=float,
                ),
            ),
        ]
    )

    transformers = []
    if meta.numeric_cols:
        transformers.append(("num", numeric_pipe, meta.numeric_cols))
    if meta.categorical_cols:
        transformers.append(("cat", categorical_pipe, meta.categorical_cols))
    bin_all = meta.binary_cols + meta.indicator_cols
    if bin_all:
        transformers.append(("bin", binary_pipe, bin_all))
    return ColumnTransformer(transformers, remainder="drop", verbose_feature_names_out=False)
