from scripts.validate_final_notebook import validate_notebook


def test_executed_notebook_is_clean_and_claim_safe():
    result = validate_notebook(
        "notebooks/VECTRA_X_Final.ipynb"
    )

    assert result["error_outputs"] == 0
    assert result["code_cells_without_execution_count"] == 0
    assert result["stale_execution_order"] is False
    assert result["forbidden_claims"] == []
    assert result["required_result_tables_missing"] == []
    assert result["required_language_missing"] == []
