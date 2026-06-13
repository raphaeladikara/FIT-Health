from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import export_web_data


def _write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


def _fixture_outputs(root: Path) -> tuple[Path, Path]:
    outputs = root / "outputs"
    tables = outputs / "tables"
    dashboard = outputs / "dashboard_data"
    dashboard.mkdir(parents=True)
    (dashboard / "summary.json").write_text(
        json.dumps(
            {
                "project": "VECTRA-X",
                "shape": [2, 10],
                "active_labels": ["malaria", "dengue"],
                "test_metrics": {"PRE_LAB": {"macro_f1": 0.61}},
                "triage_distribution": {"Clinical Review": 1, "Routine Monitoring": 1},
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        tables / "vectra_triage_dashboard_data.csv",
        [
            {
                "uuid": "private-a",
                "true_labels": "{malaria}",
                "predicted_labels": "{malaria}",
                "conformal_set": "{malaria, dengue}",
                "coinfection_prob": 0.2,
                "uncertainty_level": "low",
                "triage_score": 0.3,
                "triage_category": "Routine Monitoring",
                "recommended_action": "Monitor.",
                "calprob_malaria": 0.8,
                "calprob_dengue": 0.1,
            },
            {
                "uuid": "private-b",
                "true_labels": "{dengue}",
                "predicted_labels": "{dengue}",
                "conformal_set": "{dengue}",
                "coinfection_prob": 0.7,
                "uncertainty_level": "high",
                "triage_score": 0.9,
                "triage_category": "Clinical Review",
                "recommended_action": "Review.",
                "calprob_malaria": 0.2,
                "calprob_dengue": 0.9,
            },
        ],
    )
    _write_csv(tables / "model_leaderboard.csv", [{"track": "PRE_LAB", "macro_f1": 0.61}])
    return outputs, root / "web" / "public" / "data"


class WebExportTests(unittest.TestCase):
    def test_export_removes_private_patient_fields_and_generates_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))

            manifest = export_web_data.export_dashboard_data(outputs, destination)

            patients = json.loads((destination / "patients.json").read_text(encoding="utf-8"))
            self.assertEqual([row["case_id"] for row in patients], ["Case 001", "Case 002"])
            self.assertTrue(
                all("uuid" not in row and "true_labels" not in row for row in patients)
            )
            self.assertIsInstance(patients[0]["triage_score"], float)
            self.assertEqual(manifest["patient_count"], 2)

    def test_export_records_optional_artifact_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))

            manifest = export_web_data.export_dashboard_data(outputs, destination)

            self.assertTrue(
                any("fairness_metrics.csv" in warning for warning in manifest["warnings"])
            )
            evidence = json.loads((destination / "evidence.json").read_text(encoding="utf-8"))
            self.assertEqual(evidence["fairness_metrics"], [])

    def test_export_fails_when_required_summary_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))
            (outputs / "dashboard_data" / "summary.json").unlink()

            with self.assertRaisesRegex(FileNotFoundError, "summary.json"):
                export_web_data.export_dashboard_data(outputs, destination)

    def test_export_fails_when_required_patient_table_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))
            (outputs / "tables" / "vectra_triage_dashboard_data.csv").unlink()

            with self.assertRaisesRegex(
                FileNotFoundError, "vectra_triage_dashboard_data.csv"
            ):
                export_web_data.export_dashboard_data(outputs, destination)


if __name__ == "__main__":
    unittest.main()
