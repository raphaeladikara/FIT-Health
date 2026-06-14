import numpy as np
import pandas as pd

from src.fairness import subgroup_metrics
from src.triage_engine import scenario_sensitivity


def test_fairness_includes_support_counts_and_evidence_status():
    y = pd.DataFrame({"dengue": [1, 0, 1, 0]})
    pred = np.array([[1], [0], [0], [0]])
    result = subgroup_metrics(
        y, pred, ["dengue"], {"center": pd.Series(["A", "A", "B", "B"])}
    )

    required = {
        "support_pos_dengue",
        "tp_dengue",
        "fn_dengue",
        "recall_low_dengue",
        "recall_high_dengue",
        "evidence_dengue",
    }
    assert required.issubset(result.columns)
    assert set(result["evidence_dengue"]) == {"insufficient evidence"}


def test_scenario_sensitivity_returns_assumption_labeled_rows():
    result = scenario_sensitivity(
        proba=np.array([[0.8, 0.2], [0.6, 0.7]]),
        labels=["malaria", "dengue"],
        weight_scenarios={"base": {"malaria": 1.0, "dengue": 1.4}},
        threshold_scenarios={"base": {"malaria": 0.5, "dengue": 0.5}},
        capacities=[1, 2],
        false_negative_costs=[1.0, 5.0],
    )

    assert {
        "weight_scenario",
        "threshold_scenario",
        "capacity",
        "false_negative_cost",
    }.issubset(result.columns)
