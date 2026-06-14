import pandas as pd
import pytest

from src import report_utils as ru
from src.leakage_audit import audit_leakage
from src.preprocessing import assert_no_research_features, make_feature_frame


def test_other_disease_presentation_is_research_only():
    feature = "Autres maladies presentees par le patient"
    df = pd.DataFrame({feature: ["clinical text", None, "other text", None]})
    y = pd.DataFrame({"other_diseases": [1, 0, 1, 0]})

    result = audit_leakage(df, y, [feature], cfg=ru.load_config())
    row = result["audit"].set_index("feature").loc[feature]

    assert row["decision"] == "research_only"
    assert row["derived_representation"] == "presence"


def test_deployable_frame_cannot_contain_research_only_derived_columns():
    feature = "Autres maladies presentees par le patient"
    values = [f"clinical narrative {i}" for i in range(18)] + [None, None]
    df = pd.DataFrame({feature: values})
    frame, meta = make_feature_frame(df, [feature], cfg=ru.load_config())

    with pytest.raises(ValueError, match="autres_maladies"):
        assert_no_research_features(
            list(frame.columns),
            meta.source_map,
            {feature},
        )
