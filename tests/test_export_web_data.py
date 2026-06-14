import json
from pathlib import Path

import export_web_data as exporter


ROOT = Path(__file__).resolve().parents[1]
WEB_DATA = ROOT / "web" / "data"


def test_exporter_reads_locked_release_and_writes_versioned_contracts():
    exporter.main()
    manifest = json.loads((WEB_DATA / "manifest.json").read_text(encoding="utf-8"))
    evidence = json.loads((WEB_DATA / "evidence.json").read_text(encoding="utf-8"))
    input_schema = json.loads((WEB_DATA / "input-schema.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "3.0.0"
    assert manifest["notebook_run_id"] == evidence["run_id"] == input_schema["run_id"]
    assert set(manifest["policy_ids"]) == {"PRE_LAB", "LAB_AWARE"}
    assert "FULL" not in json.dumps(evidence)


def test_demo_cases_are_explicitly_synthetic():
    exporter.main()
    cases = json.loads((WEB_DATA / "demo-cases.json").read_text(encoding="utf-8"))
    assert 3 <= len(cases) <= 5
    assert all(case["provenance"] == "illustrative_synthetic" for case in cases)
    assert all("expected_output" not in case for case in cases)


def test_historical_csv_cannot_change_public_evidence(tmp_path):
    exporter.main()
    before = (WEB_DATA / "evidence.json").read_bytes()
    stale = ROOT / "outputs" / "tables" / "final_test_metrics.csv"
    original = stale.read_bytes()
    try:
        stale.write_text("conflicting,legacy\n1,2\n", encoding="utf-8")
        exporter.main()
        assert (WEB_DATA / "evidence.json").read_bytes() == before
    finally:
        stale.write_bytes(original)
