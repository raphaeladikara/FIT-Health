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


def _fixture_outputs(root: Path, execution_profile: str = "full") -> tuple[Path, Path]:
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
                "execution_profile": execution_profile,
                "best_model_per_track": {"PRE_LAB": "extra_trees", "LAB_AWARE": "hist_gb"},
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
    _write_csv(
        tables / "threshold_policies.csv",
        [
            {"label": "malaria", "performance": 0.05, "safety": 0.05, "operational": 0.05},
            {"label": "dengue", "performance": 0.5, "safety": 0.2, "operational": 0.5},
        ],
    )
    return outputs, root / "web" / "public" / "data"


class WebExportTests(unittest.TestCase):
    def test_export_manifest_contains_canonical_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory), execution_profile="full")

            manifest = export_web_data.export_dashboard_data(
                outputs, destination, require_canonical=True
            )

            self.assertEqual(manifest["schema_version"], 2)
            self.assertTrue(manifest["canonical"])
            self.assertTrue(manifest["run_id"])
            self.assertTrue(manifest["data_checksum"])
            self.assertTrue(manifest["config_checksum"])
            self.assertEqual(manifest["evaluation_mode"], "held_out")
            self.assertEqual(manifest["model_versions"]["PRE_LAB"], "extra_trees")

    def test_official_export_rejects_quick_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(
                Path(directory), execution_profile="quick_smoke"
            )

            with self.assertRaisesRegex(ValueError, "canonical"):
                export_web_data.export_dashboard_data(
                    outputs, destination, require_canonical=True
                )

    def test_development_export_flags_non_canonical_warning(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(
                Path(directory), execution_profile="quick_smoke"
            )

            manifest = export_web_data.export_dashboard_data(outputs, destination)

            self.assertFalse(manifest["canonical"])
            self.assertTrue(
                any("Development artifact" in warning for warning in manifest["warnings"])
            )

    def test_export_attaches_per_label_decisions_from_thresholds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))

            export_web_data.export_dashboard_data(outputs, destination)

            patients = json.loads((destination / "patients.json").read_text(encoding="utf-8"))
            first = patients[0]
            self.assertEqual(first["model_track"], "PRE_LAB")
            self.assertEqual(first["threshold_policy"], "operational")
            self.assertEqual(first["record_source"], "full_cohort_oof")
            dengue = first["label_decisions"]["dengue"]
            self.assertEqual(dengue["threshold"], 0.5)
            # calprob_dengue 0.1 < operational threshold 0.5 -> not predicted.
            self.assertFalse(dengue["predicted"])
            # predicted_labels is regenerated to agree with the shown thresholds.
            self.assertEqual(first["predicted_labels"], "{malaria}")

    def test_export_fails_when_active_label_has_no_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outputs, destination = _fixture_outputs(Path(directory))
            policies = outputs / "tables" / "threshold_policies.csv"
            policies.write_text("label,operational\nmalaria,0.05\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "threshold"):
                export_web_data.export_dashboard_data(outputs, destination)

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
