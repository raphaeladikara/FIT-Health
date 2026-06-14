"""modeling — multi-label tracks, co-infection, and rare-label models.

Design choices driven by the data reality (300 raw rows, 299 supervised patients,
approximately 90% malaria prevalence,
yellow fever with only 12 positives):

* **Binary Relevance** is implemented manually (one calibratable pipeline per
  label) so that rare labels with single-class CV folds are handled gracefully
  (fall back to the training prior) instead of crashing OneVsRest.
* **Multi-label stratified** splits (``iterstrat``) preserve per-label
  prevalence and co-occurrence in every fold; a documented fallback stratifies
  on label cardinality if ``iterstrat`` is unavailable.
* A **ClassifierChain** variant is offered as a supplemental model (exploits
  co-diagnosis dependency) and is skipped gracefully if it fails on rare labels.

Optional engines (XGBoost / LightGBM) are used when importable; otherwise the
sklearn ensembles + HistGradientBoosting provide a complete fallback.
"""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from . import preprocessing as pp
from . import report_utils as ru

logger = ru.get_logger(__name__)

_HAS_XGB = importlib.util.find_spec("xgboost") is not None
_HAS_LGBM = importlib.util.find_spec("lightgbm") is not None

try:  # multi-label stratification
    from iterstrat.ml_stratifiers import (
        MultilabelStratifiedKFold,
        MultilabelStratifiedShuffleSplit,
    )
    _HAS_ITERSTRAT = True
except Exception:  # pragma: no cover
    _HAS_ITERSTRAT = False


# --------------------------------------------------------------------------- #
# Splitting
# --------------------------------------------------------------------------- #
def train_test_indices(y: pd.DataFrame, test_size: float, random_state: int
                       ) -> tuple[np.ndarray, np.ndarray]:
    """Multi-label stratified train/test split (iterstrat) with fallback."""
    n = len(y)
    if _HAS_ITERSTRAT:
        splitter = MultilabelStratifiedShuffleSplit(
            n_splits=1, test_size=test_size, random_state=random_state)
        train_idx, test_idx = next(splitter.split(np.zeros(n), y.values))
        return train_idx, test_idx
    # Fallback: stratify on label cardinality (preserves multi-label mix).
    from sklearn.model_selection import train_test_split
    strat = y.sum(axis=1).clip(upper=2)
    idx = np.arange(n)
    tr, te = train_test_split(idx, test_size=test_size, random_state=random_state,
                              stratify=strat)
    logger.warning("iterstrat unavailable; used cardinality-stratified fallback split.")
    return tr, te


def make_cv_splits(y: pd.DataFrame, n_folds: int, random_state: int) -> list[tuple[np.ndarray, np.ndarray]]:
    """K folds preserving label prevalence (iterstrat) with fallback."""
    n = len(y)
    if _HAS_ITERSTRAT:
        kf = MultilabelStratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
        return list(kf.split(np.zeros(n), y.values))
    from sklearn.model_selection import StratifiedKFold
    strat = y.sum(axis=1).clip(upper=2)
    kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)
    return list(kf.split(np.zeros(n), strat))


# --------------------------------------------------------------------------- #
# Model zoo
# --------------------------------------------------------------------------- #
def available_model_names() -> list[str]:
    names = ["logreg", "random_forest", "extra_trees", "hist_gb"]
    if _HAS_XGB:
        names.append("xgboost")
    if _HAS_LGBM:
        names.append("lightgbm")
    return names


def _base_estimator(name: str, random_state: int):
    if name == "logreg" or name.startswith("logreg_c"):
        c_value = 0.5 if name == "logreg" else float(name.removeprefix("logreg_c"))
        return LogisticRegression(
            max_iter=2000, class_weight="balanced", C=c_value
        )
    if name == "random_forest":
        return RandomForestClassifier(
            n_estimators=400, max_depth=None, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=random_state, n_jobs=-1)
    if name == "extra_trees" or name.startswith("extra_trees_leaf"):
        leaf = (
            2
            if name == "extra_trees"
            else int(name.removeprefix("extra_trees_leaf"))
        )
        return ExtraTreesClassifier(
            n_estimators=500, min_samples_leaf=leaf, class_weight="balanced",
            random_state=random_state, n_jobs=-1)
    if name == "hist_gb":
        return HistGradientBoostingClassifier(
            max_depth=3, learning_rate=0.05, max_iter=300,
            l2_regularization=1.0, random_state=random_state)
    if name == "xgboost":
        from xgboost import XGBClassifier
        return XGBClassifier(
            n_estimators=300, max_depth=3, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, reg_lambda=2.0, eval_metric="logloss",
            tree_method="hist", random_state=random_state, n_jobs=-1)
    if name == "lightgbm":
        from lightgbm import LGBMClassifier
        return LGBMClassifier(
            n_estimators=300, num_leaves=15, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=2.0,
            class_weight="balanced", random_state=random_state, n_jobs=-1, verbose=-1)
    raise ValueError(f"Unknown model {name!r}")


def make_pipeline(name: str, meta: pp.FeatureMeta, random_state: int) -> Pipeline:
    """Pipeline(preprocessor -> base classifier). Numeric scaling only for the
    linear model; tree/boosting models are scale-invariant."""
    scale = name.startswith("logreg")
    pre = pp.build_preprocessor(meta, scale_numeric=scale)
    return Pipeline([("pre", pre), ("clf", _base_estimator(name, random_state))])


# --------------------------------------------------------------------------- #
# Binary-relevance multi-label model (rare-label safe)
# --------------------------------------------------------------------------- #
@dataclass
class BinaryRelevanceModel:
    """One pipeline per label; constant-prior fallback for single-class folds."""
    name: str
    meta: pp.FeatureMeta
    random_state: int
    labels: list[str] = field(default_factory=list)
    models_: dict[str, Any] = field(default_factory=dict)
    priors_: dict[str, float] = field(default_factory=dict)

    def fit(self, X: pd.DataFrame, y: pd.DataFrame) -> "BinaryRelevanceModel":
        self.labels = list(y.columns)
        for lab in self.labels:
            yc = y[lab].values
            self.priors_[lab] = float(yc.mean())
            if len(np.unique(yc)) < 2:
                self.models_[lab] = ("const", self.priors_[lab])
            else:
                pipe = make_pipeline(self.name, self.meta, self.random_state)
                pipe.fit(X, yc)
                self.models_[lab] = ("model", pipe)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        cols = []
        for lab in self.labels:
            kind, obj = self.models_[lab]
            if kind == "const":
                cols.append(np.full(len(X), obj))
            else:
                cols.append(obj.predict_proba(X)[:, 1])
        return np.column_stack(cols)


def cross_val_proba(model_name: str, meta: pp.FeatureMeta, X: pd.DataFrame,
                    y: pd.DataFrame, splits: list[tuple[np.ndarray, np.ndarray]],
                    random_state: int) -> np.ndarray:
    """Out-of-fold predicted probabilities via binary relevance over CV folds."""
    oof = np.zeros((len(X), y.shape[1]))
    for tr, va in splits:
        m = BinaryRelevanceModel(model_name, meta, random_state)
        m.fit(X.iloc[tr], y.iloc[tr])
        oof[va] = m.predict_proba(X.iloc[va])
    return oof


# --------------------------------------------------------------------------- #
# Classifier chain (supplemental: exploits co-diagnosis dependency)
# --------------------------------------------------------------------------- #
def classifier_chain_proba(meta: pp.FeatureMeta, X: pd.DataFrame, y: pd.DataFrame,
                           splits, random_state: int, base: str = "hist_gb"):
    """OOF probabilities from an order-averaged ClassifierChain. Returns None if
    it cannot be fit (e.g. a rare label is single-class within a fold)."""
    from sklearn.multioutput import ClassifierChain
    try:
        oof = np.zeros((len(X), y.shape[1]))
        for tr, va in splits:
            pre = pp.build_preprocessor(meta, scale_numeric=False)
            Xtr = pd.DataFrame(pre.fit_transform(X.iloc[tr]), columns=pre.get_feature_names_out())
            Xva = pd.DataFrame(pre.transform(X.iloc[va]), columns=pre.get_feature_names_out())
            chains = []
            for k in range(3):
                cc = ClassifierChain(_base_estimator(base, random_state),
                                     order="random", random_state=random_state + k)
                cc.fit(Xtr, y.iloc[tr].values)
                chains.append(cc.predict_proba(Xva))
            oof[va] = np.mean(chains, axis=0)
        return oof
    except Exception as exc:  # pragma: no cover
        logger.warning("ClassifierChain skipped (%s).", exc)
        return None


# --------------------------------------------------------------------------- #
# Co-infection model (Track 4): binary target = (#labels > 1)
# --------------------------------------------------------------------------- #
def coinfection_target(y: pd.DataFrame) -> pd.Series:
    return (y.sum(axis=1) > 1).astype(int)


def coinfection_cv_proba(model_name: str, meta: pp.FeatureMeta, X: pd.DataFrame,
                         y_co: pd.Series, splits, random_state: int) -> np.ndarray:
    oof = np.zeros(len(X))
    for tr, va in splits:
        pipe = make_pipeline(model_name, meta, random_state)
        if len(np.unique(y_co.iloc[tr])) < 2:
            oof[va] = float(y_co.iloc[tr].mean())
        else:
            pipe.fit(X.iloc[tr], y_co.iloc[tr].values)
            oof[va] = pipe.predict_proba(X.iloc[va])[:, 1]
    return oof


# --------------------------------------------------------------------------- #
# Rare-label sentinel (Track 5): recall-oriented, class-weighted
# --------------------------------------------------------------------------- #
def rare_label_cv_proba(meta: pp.FeatureMeta, X: pd.DataFrame, y: pd.DataFrame,
                        rare_labels: list[str], splits, random_state: int,
                        model_name: str = "logreg") -> dict[str, np.ndarray]:
    """OOF probabilities for rare labels using a class-balanced linear model
    (most stable under tiny positive counts)."""
    out: dict[str, np.ndarray] = {}
    for lab in rare_labels:
        if lab not in y.columns:
            continue
        oof = np.zeros(len(X))
        for tr, va in splits:
            yc = y[lab].iloc[tr].values
            if len(np.unique(yc)) < 2:
                oof[va] = float(yc.mean())
            else:
                pipe = make_pipeline(model_name, meta, random_state)
                pipe.fit(X.iloc[tr], yc)
                oof[va] = pipe.predict_proba(X.iloc[va])[:, 1]
        out[lab] = oof
    return out
