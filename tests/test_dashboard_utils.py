from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from app import dashboard_utils as du


class FakeProbabilityModel:
    def predict_proba(self, frame):
        self.rows_seen = len(frame)
        return np.array([[0.8, 0.2], [0.4, 0.7]])[: len(frame)]


class DashboardUtilsTests(unittest.TestCase):
    def test_load_json_returns_default_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(du.load_json(Path(tmp) / "missing.json", {"ok": False}), {"ok": False})

    def test_load_json_reads_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(json.dumps({"patients": 300}), encoding="utf-8")
            self.assertEqual(du.load_json(path)["patients"], 300)

    def test_validate_upload_schema_reports_missing_and_extra_columns(self):
        frame = pd.DataFrame({"age": [20], "fever": [1], "extra": ["x"]})
        result = du.validate_upload_schema(frame, ["age", "fever", "center"])
        self.assertFalse(result.is_valid)
        self.assertEqual(result.missing, ("center",))
        self.assertEqual(result.extra, ("extra",))

    def test_apply_thresholds_uses_named_policy(self):
        probabilities = np.array([[0.7, 0.3], [0.4, 0.8]])
        thresholds = {"malaria": 0.5, "dengue": 0.4}
        result = du.apply_thresholds(probabilities, ["malaria", "dengue"], thresholds)
        np.testing.assert_array_equal(result, np.array([[1, 0], [0, 1]]))

    def test_resource_capacity_calculates_gaps(self):
        patients = pd.DataFrame(
            {
                "triage_category": [
                    "Urgent Response Priority",
                    "Confirmatory Test Priority",
                    "Clinical Review",
                ],
                "uncertainty_level": ["high", "moderate", "low"],
                "predicted_labels": ["{dengue}", "{malaria, dengue}", "{malaria}"],
            }
        )
        result = du.calculate_resource_capacity(
            patients,
            rapid_tests=1,
            beds=0,
            monitoring_capacity=2,
            staff_capacity=1,
        )
        indexed = result.set_index("resource")
        self.assertEqual(indexed.loc["Rapid tests", "demand"], 2)
        self.assertEqual(indexed.loc["Rapid tests", "gap"], -1)
        self.assertEqual(indexed.loc["Beds", "demand"], 1)
        self.assertEqual(indexed.loc["Beds", "gap"], -1)

    def test_patient_markdown_report_contains_safety_language(self):
        report = du.patient_markdown_report(
            pd.Series(
                {
                    "uuid": "patient-1",
                    "predicted_labels": "{malaria}",
                    "conformal_set": "{malaria, dengue}",
                    "triage_category": "Clinical Review",
                    "triage_score": 0.42,
                    "uncertainty_level": "moderate",
                    "coinfection_prob": 0.31,
                    "recommended_action": "Manual clinician review.",
                }
            )
        )
        self.assertIn("patient-1", report)
        self.assertIn("decision support", report.lower())
        self.assertIn("not a confirmed diagnosis", report.lower())

    def test_available_model_modes_marks_missing_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            modes = du.available_model_modes(Path(tmp))
            self.assertFalse(modes["Pre-lab Triage"]["available"])
            self.assertFalse(modes["Lab-aware Confirmation"]["available"])
            self.assertFalse(modes["Full-feature Research-only"]["available"])

    def test_predict_with_bundle_returns_downloadable_prediction_table(self):
        frame = pd.DataFrame({"age": [20, 40]})
        bundle = {
            "model": FakeProbabilityModel(),
            "labels": ["malaria", "dengue"],
            "thresholds": {"malaria": 0.5, "dengue": 0.5},
        }
        result = du.predict_with_bundle(
            frame,
            bundle,
            thresholds={"malaria": 0.3, "dengue": 0.3},
        )
        self.assertEqual(result.loc[0, "predicted_labels"], "{malaria}")
        self.assertEqual(result.loc[1, "predicted_labels"], "{malaria, dengue}")
        self.assertIn("prob_malaria", result.columns)
        self.assertIn("uncertainty_level", result.columns)
        self.assertIn("inference_scope", result.columns)

    def test_threshold_policy_reads_requested_column(self):
        table = pd.DataFrame(
            {
                "label": ["malaria", "dengue"],
                "performance": [0.5, 0.4],
                "safety": [0.4, 0.2],
            }
        )
        result = du.threshold_policy(table, "safety", ["malaria", "dengue"])
        self.assertEqual(result, {"malaria": 0.4, "dengue": 0.2})

    def test_predict_uploaded_frame_rejects_research_only_mode(self):
        with self.assertRaisesRegex(ValueError, "research-only"):
            du.predict_uploaded_frame(
                pd.DataFrame({"feature": [1]}),
                "Full-feature Research-only",
                "performance",
            )


if __name__ == "__main__":
    unittest.main()
