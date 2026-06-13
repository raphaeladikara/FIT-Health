from __future__ import annotations

import unittest
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb"


class FinalNotebookTests(unittest.TestCase):
    def test_notebook_contains_all_required_sections_and_reproducibility_controls(self):
        self.assertTrue(NOTEBOOK.exists(), "Final competition notebook is missing.")
        notebook = nbformat.read(NOTEBOOK, as_version=4)
        markdown = "\n".join(
            cell.source for cell in notebook.cells if cell.cell_type == "markdown"
        )
        code = "\n".join(cell.source for cell in notebook.cells if cell.cell_type == "code")
        required = [
            "0. Title Page / Executive Summary",
            "1. Humanitarian Background",
            "2. Project Objective",
            "3. Data Loading and Dataset Overview",
            "4. Data Quality and Schema Audit",
            "5. Diagnostic Leakage Audit",
            "6. Exploratory Data Analysis",
            "7. Modeling Strategy",
            "8. Preprocessing Pipeline",
            "9. Baseline Models",
            "10. Advanced Model Benchmark",
            "11. Pre-Lab Triage Model",
            "12. Lab-Aware Confirmation Model",
            "13. Full-Feature Leakage Demonstration",
            "14. Threshold Optimization",
            "15. Calibration",
            "16. Uncertainty Estimation",
            "17. Conformal Prediction",
            "18. Explainability",
            "19. Fairness and Robustness Audit",
            "20. Co-Infection Detection",
            "21. VECTRA-X Triage Engine",
            "22. Resource Prioritization Simulation",
            "23. Dashboard Prototype Overview",
            "24. Final Discussion",
            "25. Limitations and Ethics",
            "26. Conclusion and Recommendations",
            "27. Appendix",
            "Why VECTRA-X Can Win",
        ]
        for heading in required:
            self.assertIn(heading, markdown)
        self.assertIn("RECOMPUTE_MODELS", code)
        self.assertIn('"final_notebook"', code)
        self.assertIn("FINAL_OUTPUT", code)
        self.assertIn("RANDOM_STATE", code)
        self.assertEqual(notebook.metadata.kernelspec.name, "python3")


if __name__ == "__main__":
    unittest.main()
