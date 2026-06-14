import numpy as np
import pandas as pd

from src.calibration import cross_fitted_calibration, reliability_curve
from src.conformal import conformal_metrics, fit_conformal


def test_cross_fitted_calibration_never_trains_on_target_row():
    y = pd.DataFrame({"dengue": [0, 1, 0, 1, 0, 1]})
    p = np.array([[0.1], [0.7], [0.2], [0.8], [0.3], [0.9]])

    calibrated, audit = cross_fitted_calibration(
        y, p, n_splits=3, random_state=11
    )

    assert calibrated.shape == p.shape
    for row in audit.itertuples():
        assert row.target_index not in row.calibration_indices


def test_exact_conformal_does_not_cap_quantile_level():
    y = pd.DataFrame({"rare": [1, 1, 1, 0]})
    p = np.array([[0.1], [0.2], [0.3], [0.9]])

    info = fit_conformal(y, p, ["rare"], alpha=0.10, mode="exact")

    assert info["rare"]["quantile_level_used"] == 1.0
    assert info["rare"]["mode"] == "exact"


def test_reliability_bins_include_count_and_positive_support():
    table = reliability_curve(
        np.array([0, 1, 1, 0]), np.array([0.1, 0.8, 0.7, 0.3]), n_bins=2
    )
    assert {"count", "positive_support"}.issubset(table.columns)


def test_prediction_set_summary_names_policy_and_efficiency():
    y = pd.DataFrame({"rare": [1, 0]})
    p = np.array([[0.8], [0.2]])
    info = fit_conformal(y, p, ["rare"], mode="pragmatic")
    _, summary = conformal_metrics(y, p, info, ["rare"])
    assert summary["policy_name"] == "pragmatic_efficiency_policy"
    assert "singleton_rate" in summary
