from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src import evaluation
from src import leakage_audit
from src import preprocessing
from src import scientific_analysis


ROOT = Path(__file__).resolve().parents[1]


class TrainOnlyFeatureTransformerTests(unittest.TestCase):
    def test_schema_and_categories_are_learned_from_train_only(self):
        train = pd.DataFrame(
            {
                "category": ["A", "B", "A", None],
                "train_constant": ["same"] * 4,
                "sometimes_missing": [1, None, 2, 3],
            }
        )
        test = pd.DataFrame(
            {
                "category": ["C"],
                "train_constant": ["changed_in_test"],
                "sometimes_missing": [4],
            }
        )

        transformer = preprocessing.FittedFeatureFrame(
            missing_indicator_threshold=0.20
        ).fit(train, list(train.columns))
        train_x = transformer.transform(train)
        test_x = transformer.transform(test)

        self.assertEqual(list(train_x.columns), list(test_x.columns))
        self.assertEqual(len(train_x.columns), len(set(train_x.columns)))
        self.assertNotIn("train_constant", " ".join(test_x.columns))
        self.assertIn("sometimes_missing__missing", test_x.columns)
        category_columns = [c for c in test_x if c.startswith("category__")]
        self.assertEqual(float(test_x[category_columns].sum(axis=1).iloc[0]), 0.0)


class EvaluationEvidenceTests(unittest.TestCase):
    def test_leakage_screen_accepts_nullable_integer_with_fractional_median(self):
        values = pd.Series([100, 119, None], dtype="Int64")
        encoded = leakage_audit._encode_for_screen(values)
        self.assertEqual(encoded.dtype, float)
        self.assertAlmostEqual(float(encoded.iloc[2]), 109.5)

    def test_bootstrap_summary_is_reproducible_and_bounded(self):
        y_true = pd.DataFrame({"a": [1, 1, 0, 0, 1, 0], "b": [0, 1, 0, 1, 0, 1]})
        y_pred = np.array([[1, 0], [1, 1], [0, 0], [0, 1], [1, 0], [0, 0]])
        y_proba = y_pred * 0.8 + 0.1

        first = evaluation.bootstrap_multilabel_metrics(
            y_true, y_pred, y_proba, n_bootstrap=100, random_state=42
        )
        second = evaluation.bootstrap_multilabel_metrics(
            y_true, y_pred, y_proba, n_bootstrap=100, random_state=42
        )

        pd.testing.assert_frame_equal(first, second)
        self.assertTrue({"metric", "estimate", "ci_low", "ci_high"}.issubset(first.columns))
        self.assertTrue((first["ci_low"] <= first["estimate"]).all())
        self.assertTrue((first["estimate"] <= first["ci_high"]).all())

    def test_provenance_manifest_contains_checksums_and_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "data.csv"
            config = root / "config.yaml"
            data.write_text("a\n1\n", encoding="utf-8")
            config.write_text("x: 1\n", encoding="utf-8")

            manifest = scientific_analysis.build_provenance_manifest(
                root=root,
                data_path=data,
                config_path=config,
                execution_mode="test",
            )

        self.assertEqual(len(manifest["data_sha256"]), 64)
        self.assertEqual(len(manifest["config_sha256"]), 64)
        self.assertIn("python", manifest["package_versions"])
        self.assertEqual(manifest["execution_mode"], "test")


class PrivacyAndNotebookTests(unittest.TestCase):
    def test_notebook_requires_scientific_upgrade_sections(self):
        notebook = json.loads(
            (ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb").read_text(
                encoding="utf-8"
            )
        )
        text = "\n".join(
            "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
        )
        required = [
            "Related Work and Research Gap",
            "95% Confidence Intervals",
            "Repeated Multi-Label Validation",
            "Preprocessing and Component Ablation",
            "Decision-Curve Net Benefit",
            "Artifact Provenance",
            "Typhoid coverage",
            "Competition prototype requiring prospective validation",
        ]
        for phrase in required:
            self.assertIn(phrase, text)
        self.assertNotIn("References Placeholder", text)


if __name__ == "__main__":
    unittest.main()
