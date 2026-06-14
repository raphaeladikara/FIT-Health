from src.notebook_workflow import run_research_workflow


def test_workflow_uses_verified_cohort_and_leakage_free_pre_lab():
    result = run_research_workflow(quick=True)

    assert result.cohort_audit["n_supervised"] == 299
    assert result.cohort_audit["n_excluded_unknown_target"] == 1
    assert any(
        "Autres maladies" in feature
        for feature in result.research_only_features
    )
    assert not any(
        "autres_maladies" in c for c in result.design_frames["PRE_LAB"].columns
    )


def test_workflow_keeps_test_out_of_selection_audit():
    result = run_research_workflow(quick=True)

    assert set(result.selection_audit["data_partition"]) == {"training_only"}
    assert result.final_test_audit["evaluations_per_track"].max() == 1
