import pandas as pd

from src.label_detection import _to_binary, build_supervised_cohort


def test_to_binary_preserves_unknown_targets():
    result = _to_binary(pd.Series(["1", "0", None]))

    assert result.tolist()[:2] == [1, 0]
    assert pd.isna(result.iloc[2])


def test_supervised_cohort_excludes_any_row_with_all_targets_unknown():
    df = pd.DataFrame({"id": ["a", "b", "c"]})
    y_all = pd.DataFrame(
        {"malaria": [1, 0, pd.NA], "dengue": [0, 1, pd.NA]},
        dtype="Int64",
    )

    cohort = build_supervised_cohort(df, y_all)

    assert cohort.included_index.tolist() == [0, 1]
    assert cohort.excluded_index.tolist() == [2]
    assert cohort.exclusion_reason.iloc[0] == "all diagnosis targets missing"
