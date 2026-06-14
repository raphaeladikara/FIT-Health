import numpy as np
import pandas as pd

from src.nested_validation import run_nested_validation
from src.preprocessing import FeatureMeta


def test_nested_validation_outputs_out_of_sample_predictions_and_is_deterministic():
    X = pd.DataFrame({"x": np.arange(30), "site": ["A", "B"] * 15})
    y = pd.DataFrame(
        {
            "common": ([0, 1] * 15),
            "rare": ([1, 0, 0, 0, 0] * 6),
        }
    )
    meta = FeatureMeta(numeric_cols=["x"], categorical_cols=["site"])
    first = run_nested_validation(
        X, y, meta, ["logreg_c0.1"], outer_folds=3, inner_folds=2, seeds=[7]
    )
    second = run_nested_validation(
        X, y, meta, ["logreg_c0.1"], outer_folds=3, inner_folds=2, seeds=[7]
    )

    predictions = first.outer_predictions
    assert len(predictions) == len(X) * y.shape[1]
    assert predictions.groupby(["seed", "patient_index", "label"]).size().max() == 1
    assert predictions.equals(second.outer_predictions)
    assert set(first.outer_policy_selections["candidate_id"]) == {"logreg_c0.1"}
    assert first.split_support["outer_train_overlap"].max() == 0


def test_nested_validation_records_fold_reduction_for_rare_support():
    X = pd.DataFrame({"x": np.arange(12)})
    y = pd.DataFrame({"rare": [1, 1] + [0] * 10})
    result = run_nested_validation(
        X,
        y,
        FeatureMeta(numeric_cols=["x"]),
        ["logreg_c0.1"],
        outer_folds=5,
        inner_folds=3,
        seeds=[3],
    )
    assert result.split_support["requested_outer_folds"].iloc[0] == 5
    assert result.split_support["effective_outer_folds"].iloc[0] == 2
