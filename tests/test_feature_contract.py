import pytest

from src.feature_contract import FeatureContract, FeatureSpec, validate_feature_contract


def spec(name, stage="PRE_LAB", source=None):
    return FeatureSpec(
        canonical_raw_name=source or name,
        derived_representation=name,
        stage=stage,
        transformation="identity",
        missingness_behavior="fold_local_imputation",
        unit=None,
        hard_invalid_min=None,
        hard_invalid_max=None,
        soft_warning_policy="training_distribution",
        leakage_rationale="available before target adjudication",
    )


def test_feature_contract_requires_lineage_and_valid_stages():
    contract = FeatureContract(version="1", features=(spec("age"), spec("lab", "LAB_AWARE"),))
    validate_feature_contract(contract)

    with pytest.raises(ValueError, match="raw-source lineage"):
        missing_source = spec("age")
        missing_source = missing_source.__class__(
            **{**missing_source.__dict__, "canonical_raw_name": ""}
        )
        validate_feature_contract(
            FeatureContract(version="1", features=(missing_source,))
        )


def test_research_only_lineage_cannot_enter_deployable_track():
    bad = spec("renamed_diagnosis", "PRE_LAB", source="diagnosis result")
    bad = bad.__class__(**{**bad.__dict__, "source_stage": "RESEARCH_ONLY"})
    with pytest.raises(ValueError, match="RESEARCH_ONLY"):
        validate_feature_contract(FeatureContract(version="1", features=(bad,)))


def test_same_raw_feature_cannot_have_contradictory_stages():
    contract = FeatureContract(
        version="1",
        features=(spec("age", "PRE_LAB", "raw age"), spec("age_lab", "LAB_AWARE", "raw age")),
    )
    with pytest.raises(ValueError, match="contradictory"):
        validate_feature_contract(contract)
