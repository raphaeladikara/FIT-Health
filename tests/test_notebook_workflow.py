import json

import pytest

from src.notebook_workflow import (
    ScientificWorkflowState,
    load_experiment_config,
    run_research_workflow,
)


def test_experiment_config_is_explicit_and_validated(tmp_path):
    config = load_experiment_config()

    assert config.dataset_path.endswith("data/raw/data.csv")
    assert config.target_policy == "complete_multilabel_only"
    assert config.frozen_test.size == 0.25
    assert config.validation.outer_folds == 5
    assert config.validation.inner_folds == 3
    assert len(config.validation.repeated_seeds) == 3
    assert config.candidates
    assert config.threshold.grid
    assert config.calibration_methods
    assert config.bootstrap.repetitions == 2000
    assert config.release_schema_version

    raw = json.loads(
        (config.source_path).read_text(encoding="utf-8")
    )
    raw["unexpected"] = True
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="Unknown experiment keys"):
        load_experiment_config(invalid)


def test_experiment_config_rejects_duplicate_seeds(tmp_path):
    config = load_experiment_config()
    raw = json.loads(config.source_path.read_text(encoding="utf-8"))
    raw["validation"]["repeated_seeds"] = [42, 42]
    invalid = tmp_path / "duplicate-seeds.json"
    invalid.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate"):
        load_experiment_config(invalid)


def test_frozen_test_state_machine_locks_policy_and_allows_one_evaluation():
    state = ScientificWorkflowState()
    with pytest.raises(RuntimeError, match="locked"):
        state.evaluate_frozen_test_once(lambda manifest: {"ok": True})

    state.prepare_training_pool("split-hash")
    state.run_nested_validation({"candidate": "logreg"})
    manifest = state.select_and_lock_policy(
        {
            "feature_contract_hash": "features",
            "selected_config": "logreg",
            "thresholds": {"dengue": 0.4},
            "calibration_method": "sigmoid",
            "seeds": [42],
            "source_commit": "abc",
        }
    )
    assert manifest["split_hash"] == "split-hash"
    with pytest.raises(RuntimeError, match="locked"):
        state.select_and_lock_policy({"selected_config": "other"})

    state.fit_locked_policy({"model": "fitted"})
    assert state.evaluate_frozen_test_once(lambda lock: {"lock": lock})["lock"] == manifest
    with pytest.raises(RuntimeError, match="already"):
        state.evaluate_frozen_test_once(lambda lock: {})


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


def test_center_ablation_removes_center_derived_columns_by_lineage():
    result = run_research_workflow(quick=True)
    ablations = result.ablations.set_index("ablation")

    assert {"all_pre_lab", "without_center"} <= set(ablations.index)
    # The center column must actually be removed (the previous bug filtered on a
    # transformed-name string "center_code" that never existed, removing nothing).
    assert (
        ablations.loc["without_center", "n_features"]
        < ablations.loc["all_pre_lab", "n_features"]
    )
    assert ablations.loc["without_center", "n_removed_columns"] >= 1
    removed_sources = ablations.loc["without_center", "raw_sources_removed"]
    assert any("Centre de santé" in src for src in removed_sources)
    # all_pre_lab removes nothing.
    assert ablations.loc["all_pre_lab", "n_removed_columns"] == 0


def test_preprocessing_summary_proves_fold_local_onehot_no_factorization():
    result = run_research_workflow(quick=True)
    summary = result.preprocessing_summary.set_index("track")

    pre = summary.loc["PRE_LAB"]
    assert pre["n_categorical"] >= 1
    assert pre["uses_global_factorization"] is False or pre["uses_global_factorization"] == False  # noqa: E712
    assert pre["unseen_categories_ignored"]
    assert "OneHotEncoder" in pre["strategy"]
    assert pre["n_transformed_features"] >= pre["n_categorical"]
