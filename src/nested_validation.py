"""Repeated nested multi-label model and threshold selection."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import evaluation as ev
from . import modeling as M
from .preprocessing import FeatureMeta


@dataclass
class NestedValidationResult:
    outer_predictions: pd.DataFrame
    outer_policy_selections: pd.DataFrame
    inner_candidate_scores: pd.DataFrame
    split_support: pd.DataFrame
    policy_stability: pd.DataFrame


def _effective_folds(y: pd.DataFrame, requested: int) -> int:
    positive = [int(y[column].sum()) for column in y if int(y[column].sum()) > 0]
    negative = [
        int((1 - y[column]).sum())
        for column in y
        if int((1 - y[column]).sum()) > 0
    ]
    support = min(positive + negative) if positive or negative else 0
    return max(2, min(int(requested), support)) if support >= 2 else 2


def _thresholds(y: pd.DataFrame, probabilities: np.ndarray) -> dict[str, float]:
    return {
        label: ev.optimise_threshold(
            y[label].to_numpy(), probabilities[:, j], objective="f1"
        )[0]
        for j, label in enumerate(y.columns)
    }


def run_nested_validation(
    X: pd.DataFrame,
    y: pd.DataFrame,
    meta: FeatureMeta,
    candidate_ids: list[str],
    *,
    outer_folds: int,
    inner_folds: int,
    seeds: list[int],
) -> NestedValidationResult:
    if not candidate_ids:
        raise ValueError("candidate_ids must not be empty")
    prediction_rows = []
    selection_rows = []
    candidate_rows = []
    support_rows = []
    for seed in seeds:
        effective_outer = _effective_folds(y, outer_folds)
        outer_splits = M.make_cv_splits(y, effective_outer, seed)
        for outer_fold, (outer_train, outer_validation) in enumerate(outer_splits):
            X_train = X.iloc[outer_train]
            y_train = y.iloc[outer_train]
            effective_inner = _effective_folds(y_train, inner_folds)
            inner_splits = M.make_cv_splits(y_train, effective_inner, seed + outer_fold)
            policies = []
            for candidate_id in candidate_ids:
                inner_probability = M.cross_val_proba(
                    candidate_id,
                    meta,
                    X_train,
                    y_train,
                    inner_splits,
                    seed + outer_fold,
                )
                thresholds = _thresholds(y_train, inner_probability)
                decisions = ev.apply_thresholds(
                    inner_probability, thresholds, list(y.columns)
                )
                score = ev.multilabel_summary(
                    y_train, decisions, inner_probability
                )
                policies.append((candidate_id, thresholds, score))
                candidate_rows.append(
                    {
                        "seed": seed,
                        "outer_fold": outer_fold,
                        "candidate_id": candidate_id,
                        **score,
                    }
                )
            selected_id, thresholds, selected_score = sorted(
                policies,
                key=lambda item: (
                    -item[2].get("macro_pr_auc", float("-inf")),
                    -item[2]["macro_f1"],
                    item[0],
                ),
            )[0]
            model = M.BinaryRelevanceModel(
                selected_id, meta, seed + outer_fold
            ).fit(X_train, y_train)
            probability = model.predict_proba(X.iloc[outer_validation])
            decisions = ev.apply_thresholds(
                probability, thresholds, list(y.columns)
            )
            selection_rows.append(
                {
                    "seed": seed,
                    "outer_fold": outer_fold,
                    "candidate_id": selected_id,
                    "thresholds": thresholds,
                    "inner_macro_pr_auc": selected_score.get("macro_pr_auc"),
                }
            )
            support_rows.append(
                {
                    "seed": seed,
                    "outer_fold": outer_fold,
                    "requested_outer_folds": outer_folds,
                    "effective_outer_folds": effective_outer,
                    "requested_inner_folds": inner_folds,
                    "effective_inner_folds": effective_inner,
                    "n_outer_train": len(outer_train),
                    "n_outer_validation": len(outer_validation),
                    "outer_train_overlap": len(
                        set(outer_train).intersection(set(outer_validation))
                    ),
                    "positive_support": y.iloc[outer_validation].sum().to_dict(),
                }
            )
            for local_index, patient_index in enumerate(outer_validation):
                for label_index, label in enumerate(y.columns):
                    prediction_rows.append(
                        {
                            "seed": seed,
                            "outer_fold": outer_fold,
                            "patient_index": int(patient_index),
                            "label": label,
                            "target": int(y.iloc[patient_index, label_index]),
                            "probability": float(
                                probability[local_index, label_index]
                            ),
                            "decision": int(
                                decisions[local_index, label_index]
                            ),
                            "threshold": float(thresholds[label]),
                            "candidate_id": selected_id,
                        }
                    )
    selections = pd.DataFrame(selection_rows)
    stability = (
        selections.groupby("candidate_id")
        .size()
        .rename("selection_count")
        .reset_index()
    )
    stability["selection_fraction"] = (
        stability["selection_count"] / stability["selection_count"].sum()
    )
    return NestedValidationResult(
        outer_predictions=pd.DataFrame(prediction_rows).sort_values(
            ["seed", "patient_index", "label"]
        ).reset_index(drop=True),
        outer_policy_selections=selections,
        inner_candidate_scores=pd.DataFrame(candidate_rows),
        split_support=pd.DataFrame(support_rows),
        policy_stability=stability,
    )
