from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SubmissionArtifactTests(unittest.TestCase):
    def test_report_source_and_pdf_are_present(self):
        report_dir = ROOT / "outputs" / "submission"
        self.assertTrue((report_dir / "VECTRA_X_Technical_Report.docx").exists())
        pdf = report_dir / "VECTRA_X_Technical_Report.pdf"
        self.assertTrue(pdf.exists())
        self.assertGreater(pdf.stat().st_size, 10_000)

    def test_final_reassessment_is_present(self):
        reassessment = (
            ROOT
            / "outputs"
            / "reports"
            / "submission_hardening_reassessment_2026-06-13.md"
        )
        self.assertTrue(reassessment.exists())
        text = reassessment.read_text(encoding="utf-8")
        for heading in [
            "Defensible Score",
            "Remaining Deductions",
            "P0 Before Submission",
            "P1 Highest-Value Improvements",
            "Longer-Term Research",
        ]:
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
