import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "web" / "data"
FORBIDDEN_KEYS = {
    "uuid",
    "patient_id",
    "true_labels",
    "ground_truth",
    "name",
    "email",
    "phone",
}


def walk(value, location="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, f"{location}.{key}"
            yield from walk(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{location}[{index}]")


class PublicBundlePrivacyTest(unittest.TestCase):
    def test_public_json_contains_no_patient_identifiers_or_ground_truth(self):
        failures = []
        for path in WEB_DATA.glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for key, location in walk(payload):
                if key.lower() in FORBIDDEN_KEYS:
                    failures.append(f"{path.name}:{location}")
        self.assertEqual(failures, [], "Forbidden public keys found:\n" + "\n".join(failures))

    def test_legacy_patient_bundle_is_not_published(self):
        self.assertFalse((WEB_DATA / "patients.json").exists())

    def test_public_bundle_contains_only_synthetic_cases(self):
        cases = json.loads((WEB_DATA / "demo-cases.json").read_text(encoding="utf-8"))
        self.assertTrue(
            all(case.get("provenance") == "illustrative_synthetic" for case in cases)
        )


if __name__ == "__main__":
    unittest.main()
