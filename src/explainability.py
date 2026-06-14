"""explainability — global + local model interpretation (leakage-aware).

Primary, always-available method: **permutation importance** (model-agnostic,
robust at n=300). Optional **SHAP** is attempted for a tree model and degrades
gracefully if the bleeding-edge numpy/pandas stack breaks it.

Local explanations use a transparent **logistic surrogate** per label: the
contribution of a feature for a patient is ``coef * standardised_value``. This
is exact for the linear pre-lab model and serves as a defensible local
attribution for any model.

IMPORTANT: features are anonymised/encoded clinical signals. Explanations
describe *model behaviour*, never medical causation.
"""
from __future__ import annotations

import importlib.util
from typing import Any

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from . import preprocessing as pp
from . import report_utils as ru

logger = ru.get_logger(__name__)
_HAS_SHAP = importlib.util.find_spec("shap") is not None


def permutation_importance_per_label(model, X: pd.DataFrame, y: pd.DataFrame,
                                     labels: list[str], random_state: int,
                                     n_repeats: int = 10) -> pd.DataFrame:
    """Permutation importance for each label's fitted pipeline.

    ``model`` is a fitted BinaryRelevanceModel. Returns a long DataFrame
    (label, feature, importance_mean, importance_std)."""
    rows = []
    for lab in labels:
        kind, obj = model.models_.get(lab, ("const", 0.0))
        if kind != "model" or y[lab].nunique() < 2:
            continue
        try:
            r = permutation_importance(
                obj, X, y[lab].values, scoring="average_precision",
                n_repeats=n_repeats, random_state=random_state, n_jobs=1)
        except Exception as exc:  # pragma: no cover
            logger.warning("Permutation importance failed for %s (%s).", lab, exc)
            continue
        for f, m, s in zip(X.columns, r.importances_mean, r.importances_std):
            rows.append({"label": lab, "feature": f,
                         "importance_mean": round(float(m), 5),
                         "importance_std": round(float(s), 5)})
    return pd.DataFrame(rows)


def global_importance(per_label: pd.DataFrame, top: int = 25) -> pd.DataFrame:
    """Aggregate per-label importance into a single global ranking."""
    if per_label.empty:
        return pd.DataFrame(columns=["feature", "importance_mean"])
    g = (per_label.groupby("feature")["importance_mean"].mean()
         .sort_values(ascending=False).reset_index())
    return g.head(top)


def fit_linear_explainers(meta: pp.FeatureMeta, X: pd.DataFrame, y: pd.DataFrame,
                          labels: list[str], random_state: int) -> dict[str, Any]:
    """Fit a transparent scaled-logistic surrogate per label for local
    attribution. Returns dict label -> {pipeline, feature_names, coef}."""
    out: dict[str, Any] = {}
    for lab in labels:
        if y[lab].nunique() < 2:
            continue
        pre = pp.build_preprocessor(meta, scale_numeric=True)
        clf = LogisticRegression(max_iter=2000, class_weight="balanced", C=0.5)
        pipe = Pipeline([("pre", pre), ("clf", clf)])
        pipe.fit(X, y[lab].values)
        feat_names = pipe.named_steps["pre"].get_feature_names_out()
        coef = pipe.named_steps["clf"].coef_.ravel()
        out[lab] = {"pipeline": pipe, "feature_names": list(feat_names), "coef": coef}
    return out


def explain_patient(explainers: dict[str, Any], X_row: pd.DataFrame,
                    label: str, top_k: int = 6) -> pd.DataFrame:
    """Top positive/negative local contributions for one patient & label."""
    if label not in explainers:
        return pd.DataFrame()
    info = explainers[label]
    pre = info["pipeline"].named_steps["pre"]
    x = pre.transform(X_row)[0]
    contrib = info["coef"] * x
    df = pd.DataFrame({"feature": info["feature_names"], "contribution": contrib})
    df = df.reindex(df["contribution"].abs().sort_values(ascending=False).index)
    return df.head(top_k).reset_index(drop=True)


def try_shap(model, X: pd.DataFrame, label: str, max_samples: int = 150):
    """Best-effort SHAP for a tree-based label model. Returns (shap_values, X)
    or None. Never raises."""
    if not _HAS_SHAP:
        return None
    kind, obj = model.models_.get(label, ("const", 0.0))
    if kind != "model":
        return None
    try:
        import shap
        clf = obj.named_steps["clf"]
        pre = obj.named_steps["pre"]
        Xt = pd.DataFrame(pre.transform(X), columns=pre.get_feature_names_out())
        Xt = Xt.iloc[:max_samples]
        explainer = shap.TreeExplainer(clf)
        sv = explainer.shap_values(Xt)
        if isinstance(sv, list):  # binary -> take positive class
            sv = sv[1]
        return sv, Xt
    except Exception as exc:  # pragma: no cover
        logger.info("SHAP unavailable/failed for %s (%s); using permutation importance.", label, exc)
        return None


def explain_deployed_tree(
    model,
    X_background: pd.DataFrame,
    X_rows: pd.DataFrame,
    label: str,
    method: str = "auto",
) -> dict[str, Any]:
    """Explain the fitted deployed label model and report the explanation target."""
    kind, obj = model.models_.get(label, ("const", 0.0))
    if kind != "model":
        return {
            "method": "constant_prior",
            "label": label,
            "contributions": pd.DataFrame(),
            "fidelity": "exact constant output",
        }
    pre = obj.named_steps["pre"]
    clf = obj.named_steps["clf"]
    feature_names = list(pre.get_feature_names_out())
    transformed = pd.DataFrame(
        pre.transform(X_rows), columns=feature_names, index=X_rows.index
    )
    if _HAS_SHAP and method in {"auto", "tree_shap"}:
        try:
            import shap

            explainer = shap.TreeExplainer(clf)
            values = explainer.shap_values(transformed)
            if isinstance(values, list):
                values = values[1]
            return {
                "method": "TreeSHAP",
                "label": label,
                "contributions": pd.DataFrame(
                    np.asarray(values), columns=feature_names, index=X_rows.index
                ),
                "fidelity": "model-native additive tree explanation",
            }
        except Exception as exc:
            logger.info("TreeSHAP local explanation failed for %s: %s", label, exc)
    baseline = obj.predict_proba(X_rows)[:, 1]
    raw_features = list(X_rows.columns)
    contributions = np.zeros((len(X_rows), len(raw_features)))
    for j, feature in enumerate(X_rows.columns):
        permuted = X_rows.copy()
        permuted[feature] = X_background[feature].median() if pd.api.types.is_numeric_dtype(
            X_background[feature]
        ) else X_background[feature].mode(dropna=True).iloc[0]
        contributions[:, j] = baseline - obj.predict_proba(permuted)[:, 1]
    return {
        "method": "local permutation attribution",
        "label": label,
        "contributions": pd.DataFrame(
            contributions,
            columns=raw_features,
            index=X_rows.index,
        ),
        "fidelity": "perturbation-based approximation of deployed probability",
    }
