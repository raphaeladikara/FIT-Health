from __future__ import annotations

import re
import unittest
from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb"


class FinalNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = nbformat.read(NOTEBOOK, as_version=4)
        cls.markdown = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "markdown"
        )
        cls.code = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "code"
        )

    def test_notebook_contains_all_required_sections_and_reproducibility_controls(self):
        self.assertTrue(NOTEBOOK.exists(), "Final competition notebook is missing.")
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
            "Related Work and Research Gap",
            "95% Confidence Intervals",
            "Repeated Multi-Label Validation",
            "Preprocessing and Component Ablation",
            "Decision-Curve Net Benefit",
            "Artifact Provenance",
        ]
        for heading in required:
            self.assertIn(heading, self.markdown)
        self.assertIn("DATA_PATH", self.code)
        self.assertIn("OUTPUT_DIR", self.code)
        self.assertIn("RANDOM_STATE", self.code)
        self.assertEqual(self.notebook.metadata.kernelspec.name, "python3")

    def test_notebook_is_runtime_self_contained(self):
        forbidden_patterns = [
            r"from\s+src\s+import",
            r"import\s+src(?:\s|$)",
            r"from\s+run_pipeline\s+import",
            r"config[/\\]config\.yaml",
            r"outputs[/\\](?:tables|models|dashboard_data|final_notebook)",
            r"data[/\\]processed",
            r"[A-Za-z]:\\Users\\",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(
                re.search(pattern, self.code, flags=re.IGNORECASE),
                f"Notebook contains forbidden runtime dependency: {pattern}",
            )

    def test_notebook_documents_required_dependencies_and_models(self):
        required_dependencies = [
            "xgboost",
            "lightgbm",
            "shap",
            "iterative-stratification",
        ]
        required_models = [
            "Dummy",
            "Logistic Regression",
            "Random Forest",
            "Extra Trees",
            "HistGradientBoosting",
            "XGBoost",
            "LightGBM",
            "Classifier Chain",
        ]
        combined = f"{self.markdown}\n{self.code}".lower()
        for dependency in required_dependencies:
            self.assertIn(dependency.lower(), combined)
        for model in required_models:
            self.assertIn(model.lower(), combined)

    def test_notebook_uses_decision_support_language_and_metric_rationale(self):
        required_phrases = [
            "decision-support",
            "triage prioritization",
            "macro pr-auc",
            "false-negative rate",
            "decision-curve net benefit",
            "number-needed-to-review",
            "requires prospective validation",
        ]
        combined = f"{self.markdown}\n{self.code}".lower()
        for phrase in required_phrases:
            self.assertIn(phrase, combined)
        self.assertNotIn("primary deployable model", combined)


if __name__ == "__main__":
    unittest.main()
