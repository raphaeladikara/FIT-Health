import numpy as np

from src.research_evaluation import (
    baseline_predictions,
    bootstrap_metric_interval,
    paired_bootstrap_difference,
    selective_risk_curve,
)


def test_always_malaria_baseline_flags_only_malaria():
    pred = baseline_predictions(
        "always_malaria", n_rows=3, labels=["malaria", "dengue"]
    )

    assert pred.tolist() == [[1, 0], [1, 0], [1, 0]]


def test_bootstrap_interval_is_reproducible():
    y = np.array([0, 1, 1, 0, 1])
    p = np.array([0, 1, 0, 0, 1])

    first = bootstrap_metric_interval(
        y, p, metric="f1", n_boot=200, random_state=7
    )
    second = bootstrap_metric_interval(
        y, p, metric="f1", n_boot=200, random_state=7
    )

    assert first == second
    assert first["lower"] <= first["estimate"] <= first["upper"]


def test_paired_bootstrap_reports_direction():
    y = np.array([0, 1, 1, 0, 1, 0])
    weak = np.array([0, 0, 1, 0, 0, 0])
    strong = np.array([0, 1, 1, 0, 1, 0])

    result = paired_bootstrap_difference(
        y, strong, weak, metric="f1", n_boot=200, random_state=9
    )

    assert result["estimate"] > 0


def test_selective_risk_decreases_when_high_error_cases_are_deferred():
    correct = np.array([1, 1, 1, 0])
    uncertainty = np.array([0.1, 0.2, 0.3, 0.9])

    curve = selective_risk_curve(correct, uncertainty)

    assert curve.iloc[-1]["risk"] <= curve.iloc[0]["risk"]
