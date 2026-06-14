from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_retired_streamlit_runtime_is_absent():
    assert not (ROOT / "app" / "streamlit_app.py").exists()
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "streamlit" not in requirements


def test_final_notebook_is_the_only_tracked_notebook():
    notebooks = sorted(path.name for path in (ROOT / "notebooks").glob("*.ipynb"))
    assert notebooks == ["VECTRA_X_Final_Competition_Notebook.ipynb"]


def test_markdown_improvement_history_is_retained():
    required = [
        ROOT / "outputs" / "reports" / "project_full_competition_audit.md",
        ROOT / "outputs" / "reports" / "final_audit_resolution.md",
        ROOT / "docs" / "superpowers" / "specs"
        / "2026-06-14-final-competition-notebook-design.md",
        ROOT / "docs" / "superpowers" / "plans"
        / "2026-06-14-final-competition-notebook.md",
    ]
    assert all(path.exists() for path in required)
    report_index = (
        ROOT / "outputs" / "reports" / "README.md"
    ).read_text(encoding="utf-8")
    assert "Historical Generated Reports" in report_index
    assert "VECTRA_X_Final_Competition_Notebook.ipynb" in report_index


def test_pipeline_is_a_canonical_notebook_workflow_runner():
    source = (ROOT / "run_pipeline.py").read_text(encoding="utf-8")
    assert "run_research_workflow" in source
    assert "FULL_RESEARCH_ONLY" not in source
    assert "dashboard_data" not in source
    assert "outputs/models" not in source
    assert source.index("if args.quick:") < source.index(
        "written = export_final_tables(result)"
    )
    assert "return" in source[
        source.index("if args.quick:"):
        source.index("written = export_final_tables(result)")
    ]
