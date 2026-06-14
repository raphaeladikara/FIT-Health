import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "web" / "data"


class ExportContractTest(unittest.TestCase):
    def test_manifest_has_canonical_provenance(self):
        manifest = json.loads((WEB_DATA / "manifest.json").read_text(encoding="utf-8"))
        required = {
            "schema_version", "run_id", "generated_at", "canonical", "model_track",
            "model_name", "evaluation_split", "cohort_size", "active_labels", "source_commit",
        }
        self.assertTrue(required.issubset(manifest))
        self.assertTrue(manifest["canonical"])
        self.assertEqual(manifest["model_track"], "PRE_LAB")

    def test_demo_cases_are_curated_and_anonymous(self):
        cases = json.loads((WEB_DATA / "demo-cases.json").read_text(encoding="utf-8"))
        self.assertLessEqual(len(cases), 12)
        self.assertGreater(len(cases), 0)
        self.assertTrue(all(case["case_id"].startswith("CASE-") for case in cases))
        self.assertGreaterEqual(len({case["scenario"] for case in cases}), 3)

    def test_operational_thresholds_are_complete(self):
        dashboard = json.loads((WEB_DATA / "dashboard.json").read_text(encoding="utf-8"))
        self.assertEqual(set(dashboard["thresholds"]["values"]), set(dashboard["summary"]["active_labels"]))


if __name__ == "__main__":
    unittest.main()
