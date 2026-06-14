import numpy as np

from src.decision_analysis import net_benefit_table, risk_coverage_table


def test_risk_coverage_review_fraction_is_monotonic():
    table = risk_coverage_table(
        y_true=np.array([[1], [0], [1], [0]]),
        decisions=np.array([[1], [0], [0], [1]]),
        uncertainty=np.array([0.1, 0.4, 0.9, 0.8]),
        labels=["dengue"],
    )
    assert table["reviewed_fraction"].is_monotonic_increasing
    assert table["retained_fraction"].is_monotonic_decreasing


def test_net_benefit_is_deterministic_and_assumption_labeled():
    kwargs = dict(
        y_true=np.array([1, 0, 1, 0]),
        probabilities=np.array([0.9, 0.3, 0.6, 0.2]),
        threshold_probabilities=[0.2, 0.5],
        false_negative_cost=3.0,
        false_positive_cost=1.0,
    )
    first = net_benefit_table(**kwargs)
    second = net_benefit_table(**kwargs)
    assert first.equals(second)
    assert set(first["analysis_type"]) == {"scenario_analysis"}
