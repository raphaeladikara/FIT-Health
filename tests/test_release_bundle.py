import json
import math

import pytest

from src.release_bundle import ReleaseValidationError, write_scientific_release


def minimal_release():
    return {
        "schema_version": "1.0.0",
        "run_id": "test-run",
        "source_commit": "abc123",
        "timestamp": "2026-06-14T00:00:00Z",
        "notebook_identity": "VECTRA_X_Final.ipynb",
        "notebook_sha256": "a" * 64,
        "analysis_policy_id": "policy-lock",
        "dataset": {"fingerprint": "datahash", "cohort_counts": {"training": 10, "frozen_test": 2}},
        "lock_manifest": {
            "source_commit": "abc123",
            "split_hash": "split",
            "feature_contract_hash": "features",
        },
        "policies": {
            "PRE_LAB": {
                "policy_id": "pre",
                "stage": "PRE_LAB",
                "thresholds": {"dengue": 0.4},
                "model_hash": "modelhash",
            }
        },
        "metrics": [
            {
                "partition": "frozen_test",
                "n_patients": 2,
                "positive_support": 1,
                "metric": "f1",
                "estimate": 0.5,
                "lower": 0.0,
                "upper": 1.0,
                "method": "patient_bootstrap",
            }
        ],
        "evidence": {},
        "feature_contract": {"version": "1", "features": []},
        "deployable_input_schema": {"fields": []},
        "safe_claims": [],
        "limitations": [],
        "deployment_gates": [],
        "artifacts": {"models": {"PRE_LAB": "modelhash"}, "figures": {}},
    }


def test_release_writer_is_canonical_and_private(tmp_path):
    path = write_scientific_release(minimal_release(), tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "test-run"
    assert "content_hash" in payload
    assert "patient_id" not in path.read_text(encoding="utf-8")


def test_release_writer_emits_strict_json_for_non_finite_values(tmp_path):
    release = minimal_release()
    release["evidence"] = {
        "python_nan": float("nan"),
        "python_infinity": float("inf"),
    }
    path = write_scientific_release(release, tmp_path)
    raw = path.read_text(encoding="utf-8")
    assert "NaN" not in raw
    assert "Infinity" not in raw
    payload = json.loads(raw, parse_constant=lambda value: math.nan)
    assert payload["evidence"] == {
        "python_infinity": None,
        "python_nan": None,
    }


def test_release_rejects_missing_intervals_and_commit_mismatch(tmp_path):
    release = minimal_release()
    release["metrics"][0].pop("lower")
    with pytest.raises(ReleaseValidationError, match="interval"):
        write_scientific_release(release, tmp_path)

    release = minimal_release()
    release["lock_manifest"]["source_commit"] = "different"
    with pytest.raises(ReleaseValidationError, match="source commit"):
        write_scientific_release(release, tmp_path)


def test_release_requires_notebook_and_policy_provenance(tmp_path):
    release = minimal_release()
    release.pop("notebook_sha256")
    with pytest.raises(ReleaseValidationError, match="missing release fields"):
        write_scientific_release(release, tmp_path)

    release = minimal_release()
    release["analysis_policy_id"] = ""
    with pytest.raises(ReleaseValidationError, match="analysis policy"):
        write_scientific_release(release, tmp_path)
