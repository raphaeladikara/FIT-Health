import nbformat


# Section headings the current self-contained scientific notebook must carry.
REQUIRED_HEADINGS = [
    "Executive abstract",
    "Executive snapshot",
    "FIT notebook scoring map",
    "1. Executive Summary, Scope, and Reproducibility",
    "2. Dataset Discovery and Loading",
    "3. Target Construction and Multi-Label Policy",
    "4. Leakage Governance and Feature Availability",
    "5. EDA and Data Integrity",
    "5.2 Dataset challenge map",
    "5.3 Top clinical signals per disease",
    "6. Fold-Local Preprocessing",
    "6.2 Preprocessing decision table",
    "6.3 Preprocessing integrity assertions",
    "7. Baselines and Metrics",
    "8. Validation and Policy Selection",
    "9. Final Training and Frozen-Test Evaluation",
    "9.3 Rare-label reliability and triage-safe routing",
    "10. Calibration, Reliability, and Uncertainty",
    "11. Prediction Sets / Review-Routing Layer",
    "12. Fairness, Subgroup, and Center Transfer",
    "13. Explainability",
    "14. Operational Triage and Resource Planning",
    "14.1 Patient-level triage case card",
    "14.2 Population-level response insight",
    "15. Limitations as Governance",
    "16. Final Submission Readiness Checklist",
    "16.1 FIT rubric readiness map",
    "16.2 Result invariants",
]

# The notebook is a single self-contained submission: these forbidden strings
# (assembled by concatenation so this test file never contains a literal one)
# mark a dependency on the superseded modular / release-bundle architecture.
FORBIDDEN_SELF_CONTAINMENT = [
    "run_research" + "_workflow",
    "export_release" + "_bundle",
    "from " + "src",
    "import " + "src",
    "_MODULE" + "_SOURCES",
    "_vectra" + "_lib",
]


def _load():
    nb = nbformat.read("notebooks/VECTRA_X_Final.ipynb", as_version=4)
    markdown = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown")
    code = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
    return markdown, code


def test_final_notebook_has_complete_research_narrative():
    markdown, _ = _load()
    for heading in REQUIRED_HEADINGS:
        assert heading in markdown, f"missing heading: {heading}"
    # Restrained evidence callouts replaced the old "**Interpretation.**" markers.
    assert markdown.count("What the result shows.") >= 8
    assert markdown.count("Remaining limitation.") >= 8


def test_final_notebook_is_self_contained():
    markdown, code = _load()
    full = markdown + "\n" + code
    for needle in FORBIDDEN_SELF_CONTAINMENT:
        assert needle not in full, f"self-containment violation: {needle}"
    assert "VECTRA_X_SELF_CONTAINED" + "_SUBMISSION_MARKER" in full
    # Dataset discovery, not a hard-coded path, is the only external input.
    assert "find_dataset" in code
