"""schema_audit — dataset structure, dtype inference, missingness & cardinality.

Produces the machine-readable backbone of the data-audit deliverables:
    * an auto data dictionary (one row per column),
    * a missingness summary,
    * dtype / cardinality classification (numeric | binary | categorical | id | text),
    * lists of constant / near-constant / high-cardinality columns.

Type inference here is *descriptive* (used for the audit report). Model-facing
numeric parsing happens in :mod:`preprocessing`.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd

from . import report_utils as ru

logger = ru.get_logger(__name__)

# Tokens that mark a column as effectively binary yes/no.
_YESNO = {"oui", "non", "positif", "négatif", "negatif", "positive", "negative",
          "yes", "no", "présent", "present", "absent"}


def _try_numeric(series: pd.Series) -> pd.Series:
    """Attempt to coerce a (string) series to float, tolerating decimal commas
    and stray characters; returns the coerced series (NaN where impossible)."""
    s = series.astype("string")
    s = s.str.replace(",", ".", regex=False)
    # Pull a leading numeric token out of values like '38,5' or '107'.
    s = s.str.extract(r"^\s*(-?\d+(?:\.\d+)?)", expand=False)
    return pd.to_numeric(s, errors="coerce")


def classify_column(series: pd.Series, name: str, uuid_col: str,
                    near_constant_threshold: float,
                    high_cardinality_threshold: float) -> dict[str, Any]:
    """Return a descriptive profile for a single column."""
    n = len(series)
    non_null = series.dropna()
    n_non_null = len(non_null)
    n_missing = n - n_non_null
    n_unique = non_null.nunique()

    # Value-share of the single most common value (near-constant detection).
    top_share = (non_null.value_counts(normalize=True).iloc[0]
                 if n_non_null else 1.0)

    lowered = {str(v).strip().lower() for v in non_null.unique()[:50]}
    is_yesno = bool(lowered) and lowered.issubset(_YESNO)

    numeric = _try_numeric(series)
    numeric_ratio = numeric.notna().sum() / n_non_null if n_non_null else 0.0

    # Decide a semantic role
    if name == uuid_col or (n_unique == n_non_null and n_non_null == n and "uuid" in name.lower()):
        role = "id"
    elif n_unique <= 1:
        role = "constant"
    elif is_yesno or n_unique == 2:
        role = "binary"
    elif numeric_ratio >= 0.80:
        role = "numeric"
    elif n_non_null and (n_unique / n_non_null) >= high_cardinality_threshold and n_unique > 15:
        role = "text_high_cardinality"
    else:
        role = "categorical"

    return {
        "column": name,
        "dtype_raw": str(series.dtype),
        "role": role,
        "n_non_null": int(n_non_null),
        "n_missing": int(n_missing),
        "missing_pct": round(100 * n_missing / n, 2),
        "n_unique": int(n_unique),
        "top_value": (str(non_null.value_counts().index[0]) if n_non_null else ""),
        "top_value_share": round(float(top_share), 4),
        "numeric_ratio": round(float(numeric_ratio), 3),
        "is_near_constant": bool(top_share >= near_constant_threshold and n_unique > 1),
        "is_constant": bool(n_unique <= 1),
        "example_values": " | ".join(map(str, non_null.unique()[:5])),
    }


def audit_schema(df: pd.DataFrame, dictionary: pd.DataFrame | None = None,
                 cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the full schema/missingness/cardinality audit.

    Returns a dict with: ``data_dictionary`` (DataFrame), ``missingness``
    (DataFrame), and convenience column lists.
    """
    cfg = cfg or ru.load_config()
    pp = cfg["preprocessing"]
    uuid_col = cfg["io"]["uuid_col"]

    rows = [
        classify_column(
            df[c], c, uuid_col,
            pp["near_constant_threshold"], pp["high_cardinality_threshold"],
        )
        for c in df.columns
    ]
    data_dict = pd.DataFrame(rows)

    # Optionally attach the EN alias / category from the spreadsheet via fuzzy
    # token overlap on the French/English column text.
    if dictionary is not None and not dictionary.empty:
        data_dict = _attach_dictionary(data_dict, dictionary)

    missingness = (data_dict[["column", "n_missing", "missing_pct", "role"]]
                   .sort_values("missing_pct", ascending=False)
                   .reset_index(drop=True))

    summary = {
        "data_dictionary": data_dict,
        "missingness": missingness,
        "shape": df.shape,
        "n_duplicate_rows": int(df.duplicated().sum()),
        "constant_columns": data_dict.loc[data_dict["is_constant"], "column"].tolist(),
        "near_constant_columns": data_dict.loc[data_dict["is_near_constant"], "column"].tolist(),
        "high_cardinality_columns": data_dict.loc[
            data_dict["role"] == "text_high_cardinality", "column"].tolist(),
        "numeric_columns": data_dict.loc[data_dict["role"] == "numeric", "column"].tolist(),
        "binary_columns": data_dict.loc[data_dict["role"] == "binary", "column"].tolist(),
        "categorical_columns": data_dict.loc[data_dict["role"] == "categorical", "column"].tolist(),
        "id_columns": data_dict.loc[data_dict["role"] == "id", "column"].tolist(),
    }
    logger.info(
        "Schema audit: %d cols -> %d numeric, %d binary, %d categorical, "
        "%d constant, %d high-cardinality; %d duplicate rows.",
        df.shape[1], len(summary["numeric_columns"]), len(summary["binary_columns"]),
        len(summary["categorical_columns"]), len(summary["constant_columns"]),
        len(summary["high_cardinality_columns"]), summary["n_duplicate_rows"],
    )
    return summary


def _normalise_tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Zàâçéèêëîïôûùü]+", str(text).lower()))


def _attach_dictionary(data_dict: pd.DataFrame, dictionary: pd.DataFrame) -> pd.DataFrame:
    """Fuzzy-join EN alias + Category from the dictionary onto the audit table."""
    # Identify the dictionary columns heuristically.
    cols = {c.lower(): c for c in dictionary.columns}
    fr_col = next((cols[c] for c in cols if c.startswith("attribut")), dictionary.columns[0])
    en_col = next((cols[c] for c in cols if "attribute" in c or "(en)" in c),
                  dictionary.columns[min(1, len(dictionary.columns) - 1)])
    cat_col = next((cols[c] for c in cols if "categ" in c), None)

    dict_tokens = []
    for _, r in dictionary.iterrows():
        toks = _normalise_tokens(r[fr_col]) | _normalise_tokens(r[en_col])
        dict_tokens.append((toks, r[en_col], r[cat_col] if cat_col else ""))

    aliases, categories = [], []
    for col in data_dict["column"]:
        col_toks = _normalise_tokens(col) - {"de", "la", "le", "des", "du", "ou",
                                                "of", "the", "and", "in", "median",
                                                "mean", "test", "blood", "count"}
        best, best_overlap = None, 0
        for toks, en, cat in dict_tokens:
            ov = len(col_toks & (toks - {"de", "la", "le", "des", "du", "ou", "of",
                                          "the", "and", "in", "median", "mean",
                                          "test", "blood", "count"}))
            if ov > best_overlap:
                best, best_overlap = (en, cat), ov
        # Require >=2 meaningful shared tokens to reduce spurious matches
        # (the dictionary is informational only, not a decision driver).
        if best and best_overlap >= 2:
            aliases.append(best[0])
            categories.append(best[1])
        else:
            aliases.append("")
            categories.append("")
    out = data_dict.copy()
    out["dict_en_alias"] = aliases
    out["dict_category"] = categories
    return out
