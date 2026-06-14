import nbformat


REQUIRED_HEADINGS = [
    "Executive Abstract",
    "Data Integrity and Target Audit",
    "Leakage Discovery and Clinical-Stage Governance",
    "Experimental Protocol",
    "Baselines and Ablation Studies",
    "Final Frozen-Test Evaluation",
    "Calibration and Prediction Sets",
    "Selective Prediction and Uncertainty",
    "Explainability of the Selected Model",
    "Fairness and Center-Shift Validation",
    "Limitations, Ethics, and Conclusion",
]


def test_final_notebook_has_complete_research_narrative():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb",
        as_version=4,
    )
    markdown = "\n".join(
        cell.source for cell in nb.cells if cell.cell_type == "markdown"
    )

    for heading in REQUIRED_HEADINGS:
        assert heading in markdown
    assert markdown.count("**Interpretation.**") >= 15
    assert markdown.count("**Limitation.**") >= 10


def test_final_notebook_executes_workflow_from_raw_data():
    nb = nbformat.read(
        "notebooks/VECTRA_X_Final_Competition_Notebook.ipynb",
        as_version=4,
    )
    code = "\n".join(
        cell.source for cell in nb.cells if cell.cell_type == "code"
    )

    assert "run_research_workflow(quick=False)" in code
    assert "outputs/tables/model_leaderboard.csv" not in code
