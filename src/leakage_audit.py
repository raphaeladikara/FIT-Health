"""leakage_audit — the methodological core of VECTRA-X.

Detects features that directly encode the diagnosis or a confirmatory lab
result, then partitions features into three stage-gated sets:

    A. PRE_LAB_TRIAGE          features available *before* any lab/test
                               (demographics, symptoms, vitals). No leakage.
    B. LAB_AWARE_CONFIRMATION  pre-lab features + ordered lab/rapid tests
                               (TDR, thick smear, haematology). Confirmation
                               support, NOT early triage.
    C. FULL_RESEARCH_ONLY      everything incl. target-restatement features
                               (e.g. "Dengue (Dengua)" ~ the dengue outcome).
                               Used only to demonstrate the cost of leakage.

Each feature is classified by BOTH its name (config patterns) and statistics
(mutual information + single-feature ROC-AUC vs every active label), so the
decisions are evidence-based rather than assumed.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import roc_auc_score

from . import report_utils as ru

logger = ru.get_logger(__name__)

# Name fragments that specifically denote an ordered lab / rapid diagnostic test
# (a subset of the broader leakage list — these are the legitimate T2 features
# used by the lab-aware confirmation model).
# NB: deliberately excludes the bare token "test" — it would mis-flag the
# bedside *tourniquet test* (a clinical symptom, per the data dictionary).
_LAB_TEST_PATTERNS = [
    "tdr", "goutte", "smear", "microscopy", "pcr", "rt-pcr", "serolog", "sérolog",
    "antigen", "ns1", "igm", "igg", "hematocrit", "hématocrit", "hematrocrit",
    "thrombocyto", "lymphocyt", "neutro", "globules blancs", "wbc", "platelet",
    "plaquettaire", "crp", "créatinine", "creatinine", "transaminase", "alat", "asat",
    "hémoconcentration", "hemoconcentration", "hématocrite", "leucopenia", "leucocytes",
]
# Vital-sign fragments -> T1 stage (still pre-lab).
_VITAL_PATTERNS = [
    "température axillaire", "axillary", "fréquence respiratoire", "respiratory rate",
    "pouls", "pulse", "pression artérielle", "blood pressure", "remplissage capillaire",
    "capillary refill",
]
# Active target disease tokens (used to spot target-restatement features).
_DISEASE_TOKENS = ["paludisme", "malaria", "dengue", "dengua", "typhoïde", "typhoid",
                   "thyphoid", "jaune", "yellow"]


def _encode_for_screen(series: pd.Series) -> pd.Series:
    """Encode any column to a numeric vector for the statistical screen.

    Binary yes/no -> 1/0; numeric (decimal comma) -> float; categorical ->
    ordinal factorisation. Missing values are filled with the median so that
    ROC-AUC / MI can be computed (this encoding is for screening ONLY)."""
    s = series.astype("string").str.strip().str.lower()
    yesno = {"oui": 1, "positif": 1, "positive": 1, "yes": 1, "présent": 1,
             "non": 0, "négatif": 0, "negatif": 0, "negative": 0, "no": 0, "absent": 0}
    if s.dropna().isin(yesno).mean() > 0.8:
        out = s.map(yesno)
    else:
        num = pd.to_numeric(
            s.str.replace(",", ".", regex=False).str.extract(r"^\s*(-?\d+(?:\.\d+)?)", expand=False),
            errors="coerce",
        )
        if num.notna().mean() > 0.6:
            out = num
        else:
            codes, _ = pd.factorize(s, use_na_sentinel=True)
            out = pd.Series(codes, index=s.index).replace(-1, np.nan)
    out = pd.to_numeric(out, errors="coerce")
    if out.notna().any():
        out = out.fillna(out.median())
    else:
        out = out.fillna(0.0)
    return out.astype(float)


def _single_feature_auc(x: pd.Series, y: pd.Series) -> float:
    """Best achievable single-feature ROC-AUC (direction-agnostic)."""
    if y.nunique() < 2 or x.nunique() < 2:
        return float("nan")
    try:
        auc = roc_auc_score(y, x)
        return float(max(auc, 1 - auc))
    except Exception:
        return float("nan")


def _screen_representations(
    series: pd.Series,
    force_presence: bool = False,
) -> dict[str, pd.Series]:
    """Return each deterministic representation that may reach a model."""
    representations: dict[str, pd.Series] = {}
    if force_presence:
        representations["presence"] = series.notna().astype(float)
    representations["model_encoding"] = _encode_for_screen(series)
    representations["missing_indicator"] = series.isna().astype(float)
    if not force_presence:
        non_null = series.dropna()
        if len(non_null) and (
            non_null.nunique() > 15
            and non_null.astype(str).str.len().mean() > 8
        ):
            representations["presence"] = series.notna().astype(float)
    return representations


def audit_leakage(df: pd.DataFrame, y: pd.DataFrame, feature_cols: list[str],
                  dictionary_categories: dict[str, str] | None = None,
                  cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the name + statistical leakage screen and build the three feature sets."""
    cfg = cfg or ru.load_config()
    lk = cfg["leakage"]
    name_patterns = [p.lower() for p in lk["name_patterns"]]
    known_lab = set(lk.get("known_lab_confirmation", []))
    forced_research = set(lk.get("research_only_features", []))
    target_aliases = lk.get("target_aliases", {})
    auc_flag = lk["single_feature_auc_flag"]
    mi_flag = lk["mi_flag_threshold"]
    dictionary_categories = dictionary_categories or {}

    # Encode features once for the screen.
    enc = pd.DataFrame({c: _encode_for_screen(df[c]) for c in feature_cols})

    rows = []
    for c in feature_cols:
        name = c.lower()
        matched = [p for p in name_patterns if p in name]
        # Lab-test decision rests on a curated clinical pattern list + an
        # explicit known-tests list. The (noisy, incomplete) data-dictionary
        # category is recorded for transparency but is NOT a decision driver,
        # to avoid fuzzy-match false positives (e.g. blood pressure matching
        # "White blood cell count" on the token "blood").
        is_lab_test = (
            any(p in name for p in _LAB_TEST_PATTERNS)
            or c in known_lab
        )
        is_vital = any(p in name for p in _VITAL_PATTERNS)
        contains_disease = any(tok in name for tok in _DISEASE_TOKENS)
        semantic_labels = [
            label
            for label, aliases in target_aliases.items()
            if any(str(alias).lower() in name for alias in aliases)
        ]

        representations = _screen_representations(
            df[c], force_presence=c in forced_research
        )
        candidates = [
            (rep_name, lab, _single_feature_auc(values, y[lab]))
            for rep_name, values in representations.items()
            for lab in y.columns
        ]
        derived_representation, best_label, max_auc = max(
            candidates,
            key=lambda item: item[2] if not np.isnan(item[2]) else -1,
        )
        best_values = representations[derived_representation]
        try:
            mi_vals = mutual_info_classif(
                best_values.to_numpy().reshape(-1, 1),
                y[best_label].values,
                random_state=cfg["project"]["random_state"],
            )
            mi = float(mi_vals[0])
        except Exception:
            mi = float("nan")

        rows.append({
            "feature": c,
            "name_patterns_matched": ";".join(matched),
            "is_lab_test": is_lab_test,
            "is_vital": is_vital,
            "contains_disease_token": contains_disease,
            "semantic_target_labels": ";".join(semantic_labels),
            "forced_research_only": c in forced_research,
            "derived_representation": derived_representation,
            "best_label": best_label,
            "max_single_feature_auc": round(max_auc, 4) if not np.isnan(max_auc) else np.nan,
            "mutual_info": round(mi, 4) if not np.isnan(mi) else np.nan,
        })

    audit = pd.DataFrame(rows)

    # ---- decision rules ---------------------------------------------- #
    def decide(r) -> tuple[str, str, str]:
        auc = r["max_single_feature_auc"]
        auc = -1 if pd.isna(auc) else auc
        if r["forced_research_only"]:
            return (
                "T3_restate",
                "research_only",
                "Explicitly governed target-restatement / post-diagnosis field",
            )
        if r["is_lab_test"]:
            return "T2_lab", "lab_aware", "Ordered lab / rapid diagnostic test"
        # target-restatement: encodes a disease name AND near-perfectly predicts it
        if (r["contains_disease_token"] or r["semantic_target_labels"]) and auc >= auc_flag:
            return "T3_restate", "research_only", "Disease-named feature ~ target (post-diagnosis)"
        # generic statistical leak: extremely high single-feature AUC, non-lab
        if auc >= 0.97:
            return "T3_restate", "research_only", "Near-perfect single-feature predictor (suspected leak)"
        if r["is_vital"]:
            return "T1_vital", "pre_lab", "Vital sign (pre-lab)"
        return "T0_intake", "pre_lab", "Demographic / symptom / history (pre-lab)"

    decisions = audit.apply(decide, axis=1, result_type="expand")
    decisions.columns = ["stage", "decision", "rationale"]
    audit = pd.concat([audit, decisions], axis=1)

    pre_lab = audit.loc[audit["decision"] == "pre_lab", "feature"].tolist()
    lab_only = audit.loc[audit["decision"] == "lab_aware", "feature"].tolist()
    research_only = audit.loc[audit["decision"] == "research_only", "feature"].tolist()

    feature_sets = {
        "PRE_LAB_TRIAGE": pre_lab,
        "LAB_AWARE_CONFIRMATION": pre_lab + lab_only,
        "FULL_RESEARCH_ONLY": pre_lab + lab_only + research_only,
    }

    # Leakage candidates = anything flagged by name pattern OR statistics.
    leakage_candidates = audit[
        (audit["decision"] != "pre_lab")
        | (audit["mutual_info"] >= mi_flag)
        | (audit["max_single_feature_auc"] >= auc_flag)
    ].sort_values("max_single_feature_auc", ascending=False).reset_index(drop=True)

    fs_long = pd.DataFrame(
        [{"feature_set": k, "n_features": len(v), "features": ";".join(v)}
         for k, v in feature_sets.items()]
    )

    logger.info(
        "Leakage audit -> PRE_LAB=%d, LAB_AWARE=%d, FULL=%d features "
        "(lab-test=%d, research-only=%d).",
        len(feature_sets["PRE_LAB_TRIAGE"]),
        len(feature_sets["LAB_AWARE_CONFIRMATION"]),
        len(feature_sets["FULL_RESEARCH_ONLY"]),
        len(lab_only), len(research_only),
    )

    return {
        "audit": audit,
        "leakage_candidates": leakage_candidates,
        "feature_sets": feature_sets,
        "feature_sets_long": fs_long,
        "encoded_features_for_screen": enc,
    }
