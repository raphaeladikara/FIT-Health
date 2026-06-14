import nbformat


REQUIRED_HEADINGS = [
    "Executive Abstract",
    "FIT Notebook Scoring Map",
    "Data and Target Integrity",
    "Leakage and Staged Feature Governance",
    "Repeated Nested Validation Protocol",
    "Baselines and Ablation Studies",
    "Final Frozen-Test Evaluation",
    "Calibration and Prediction Sets",
    "Selective Prediction and Decision Utility",
    "Explanations of the Locked Model",
    "Fairness and Center Transfer",
    "Deployment Gates, Limitations, and Conclusion",
]


def test_final_notebook_has_complete_research_narrative():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final.ipynb",
        as_version=4,
    )
    markdown = "\n".join(
        cell.source for cell in nb.cells if cell.cell_type == "markdown"
    )

    for heading in REQUIRED_HEADINGS:
        assert heading in markdown
    assert markdown.count("**Interpretation.**") >= 15
    assert markdown.count("**Finding.**") >= 15
    assert markdown.count("**Operational Meaning.**") >= 15
    assert markdown.count("**Limitation.**") >= 10


def test_final_notebook_executes_workflow_from_raw_data():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final.ipynb",
        as_version=4,
    )
    code = "\n".join(
        cell.source for cell in nb.cells if cell.cell_type == "code"
    )

    assert "run_research_workflow(quick=False)" in code
    assert "export_release_bundle(result, ROOT)" in code
    assert "outputs/tables/model_leaderboard.csv" not in code
