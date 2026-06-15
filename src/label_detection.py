"""label_detection — discover and build the multi-label target matrix.

Decision logic (verified against the data, not assumed):
    1. If explicit per-disease binary columns exist under the configured prefix
       (``Maladies diagnostiquées/<disease>``), treat the task as MULTI-LABEL.
    2. Map each French suffix to a canonical English alias.
    3. Parse 0/1 values; a label is *active* iff it has >=1 positive sample.
       Inactive labels (e.g. Chikungunya, Zika, Option 8 with 0 positives) are
       reported as a limitation and excluded from primary scoring.
    4. Cross-validate the binary encoding against the free-text diagnosis column.

Outputs the y matrix (active labels), label distribution, cardinality and the
co-occurrence matrix.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from . import report_utils as ru

logger = ru.get_logger(__name__)

_POS_TOKENS = {"1", "1.0", "oui", "positif", "yes", "true"}
_NEG_TOKENS = {"0", "0.0", "non", "negatif", "négatif", "no", "false"}


@dataclass(frozen=True)
class SupervisedCohort:
    """Indices retained for supervised learning and an audit of exclusions."""

    included_index: pd.Index
    excluded_index: pd.Index
    exclusion_reason: pd.Series


def _to_binary(series: pd.Series) -> pd.Series:
    """Coerce a label column to nullable {0,1}; preserve unknown targets."""
    s = series.astype("string").str.strip().str.lower()
    out = pd.Series(pd.NA, index=series.index, dtype="Int64")
    out.loc[s.isin(_POS_TOKENS)] = 1
    out.loc[s.isin(_NEG_TOKENS)] = 0
    return out


def build_supervised_cohort(df: pd.DataFrame, y_all: pd.DataFrame) -> SupervisedCohort:
    """Return rows with complete diagnosis targets plus explicit exclusions."""
    all_missing = y_all.isna().all(axis=1)
    partly_missing = y_all.isna().any(axis=1) & ~all_missing
    excluded = all_missing | partly_missing
    reasons = pd.Series(index=y_all.index[excluded], dtype="string", name="reason")
    reasons.loc[all_missing[all_missing].index] = "all diagnosis targets missing"
    reasons.loc[partly_missing[partly_missing].index] = "one or more diagnosis targets missing"
    return SupervisedCohort(
        included_index=df.index[~excluded],
        excluded_index=df.index[excluded],
        exclusion_reason=reasons.reset_index(drop=True),
    )


def detect_labels(df: pd.DataFrame, cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Detect and assemble the multi-label target.

    Returns a dict with keys:
        ``y`` (active-label binary DataFrame, index aligned to df),
        ``y_all`` (all detected labels incl. inactive),
        ``active_labels`` / ``inactive_labels`` (lists of aliases),
        ``alias_to_raw`` (mapping),
        ``distribution`` / ``cardinality`` / ``cooccurrence`` (DataFrames),
        ``text_validation`` (DataFrame comparing text vs binary encoding).
    """
    cfg = cfg or ru.load_config()
    prefix = cfg["labels"]["binary_prefix"]
    alias_map = cfg["labels"]["alias_map"]
    text_col = cfg["labels"]["text_label_col"]

    label_cols = [c for c in df.columns if c.startswith(prefix)]
    if not label_cols:
        raise ValueError(
            f"No multi-label columns found with prefix {prefix!r}. "
            "Re-inspect the dataset: target framing may differ."
        )

    alias_to_raw: dict[str, str] = {}
    y_all = pd.DataFrame(index=df.index)
    for col in label_cols:
        suffix = col[len(prefix):].strip()
        alias = alias_map.get(suffix, suffix.lower().replace(" ", "_"))
        alias_to_raw[alias] = col
        y_all[alias] = _to_binary(df[col])

    cohort = build_supervised_cohort(df, y_all)
    y_all_supervised = y_all.loc[cohort.included_index].astype(int)

    positives = y_all_supervised.sum().sort_values(ascending=False)
    active_labels = positives[positives > 0].index.tolist()
    inactive_labels = positives[positives == 0].index.tolist()

    if cfg["labels"].get("drop_if_no_positives", True):
        y = y_all_supervised[active_labels].copy()
    else:
        y = y_all_supervised.copy()

    logger.info("Detected %d label columns -> %d ACTIVE %s, %d INACTIVE %s",
                len(label_cols), len(active_labels), active_labels,
                len(inactive_labels), inactive_labels)

    # Distribution
    n = len(y)
    distribution = pd.DataFrame({
        "label": positives.index,
        "positives": positives.values,
        "prevalence_pct": (positives.values / n * 100).round(2),
        "status": ["active" if positives.index[i] in active_labels else "inactive"
                   for i in range(len(positives))],
    })

    # Cardinality (number of active labels per patient)
    card = y.sum(axis=1)
    cardinality = (card.value_counts().sort_index()
                   .rename_axis("n_labels").reset_index(name="n_patients"))
    cardinality["pct"] = (cardinality["n_patients"] / n * 100).round(2)

    # Co-occurrence (active labels only)
    cooc = pd.DataFrame(
        np.dot(y.T.values, y.values), index=y.columns, columns=y.columns
    ).astype(int)

    # Validate binary encoding against the free-text diagnosis
    text_validation = _validate_against_text(
        df.loc[cohort.included_index], y_all_supervised, alias_map, text_col
    )

    return {
        "y": y,
        "y_all": y_all,
        "y_all_supervised": y_all_supervised,
        "supervised_index": cohort.included_index,
        "excluded_target_index": cohort.excluded_index,
        "target_exclusion_reasons": cohort.exclusion_reason,
        "active_labels": active_labels,
        "inactive_labels": inactive_labels,
        "alias_to_raw": alias_to_raw,
        "label_columns_raw": label_cols,
        "distribution": distribution,
        "cardinality": cardinality,
        "cooccurrence": cooc,
        "n_multilabel_patients": int((card > 1).sum()),
        "n_no_label_patients": int((card == 0).sum()),
        "text_validation": text_validation,
        "top_combinations": _top_combinations(y),
    }


def _top_combinations(y: pd.DataFrame, top: int = 20) -> pd.DataFrame:
    """Most frequent active-label combinations (label-powerset view)."""
    def combo(row):
        labs = [c for c in y.columns if row[c] == 1]
        return "+".join(labs) if labs else "None"

    combos = y.apply(combo, axis=1).value_counts().head(top)
    return combos.rename_axis("combination").reset_index(name="n_patients")


def _validate_against_text(df: pd.DataFrame, y_all: pd.DataFrame,
                           alias_map: dict[str, str], text_col: str) -> pd.DataFrame:
    """Compare the free-text diagnosis string with the binary encoding to
    confirm the labels were decoded correctly (sanity check, not a feature)."""
    if text_col not in df.columns:
        return pd.DataFrame()
    # English keyword used to detect each disease inside the free text.
    keywords = {
        "malaria": ["paludisme", "malaria"],
        "dengue": ["dengue"],
        "yellow_fever": ["jaune", "yellow"],
        "typhoid": ["typhoïde", "typhoid", "thyphoid"],
        "chikungunya": ["chikun"],
        "zika": ["zika"],
        "other_diseases": ["autres", "other"],
    }
    text = df[text_col].astype("string").str.lower().fillna("")
    rows = []
    for alias in y_all.columns:
        kws = keywords.get(alias, [alias])
        text_pos = text.apply(lambda t: any(k in t for k in kws))
        bin_pos = y_all[alias] == 1
        agree = int((text_pos == bin_pos).sum())
        rows.append({
            "label": alias,
            "binary_positives": int(bin_pos.sum()),
            "text_positives": int(text_pos.sum()),
            "agreement_rows": agree,
            "agreement_pct": round(100 * agree / len(df), 2),
        })
    return pd.DataFrame(rows)


def feature_columns(df: pd.DataFrame, label_cols: list[str],
                    cfg: dict[str, Any] | None = None) -> list[str]:
    """Return the raw feature columns: everything that is not a label/target or
    the UUID identifier. Diagnostic *text* and per-disease binaries are removed
    because they are targets, never features."""
    cfg = cfg or ru.load_config()
    uuid_col = cfg["io"]["uuid_col"]
    text_col = cfg["labels"]["text_label_col"]
    drop = set(label_cols) | {uuid_col, text_col}
    return [c for c in df.columns if c not in drop]
