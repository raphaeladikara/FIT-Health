from pathlib import Path


def test_report_sketch_is_concise_and_aligned():
    text = Path(
        "outputs/reports/final_technical_report_sketch.md"
    ).read_text(encoding="utf-8")

    assert 800 <= len(text.split()) <= 2500
    assert "299" in text
    assert "target-restatement" in text.lower()
    assert "VECTRA_X_Final_Competition_Notebook.ipynb" in text
    assert "placeholder" not in text.lower()
