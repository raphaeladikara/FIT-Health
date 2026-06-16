import json
from pathlib import Path

import numpy as np
import pytest

import export_web_data
from web.api.inference import LockedInferenceService
from web.api.assess import handle_assessment
from web.api.validation import AssessmentValidationError, validate_assessment


ROOT = Path(__file__).resolve().parents[1]


def service():
    export_web_data.main()
    return LockedInferenceService(ROOT / "web")


def test_locked_inference_uses_bundle_thresholds_and_class_order():
    instance = service()
    schema = json.loads(
        (ROOT / "web" / "data" / "input-schema.json").read_text(encoding="utf-8")
    )
    values = {field["field_id"]: None for field in schema["fields"]}
    response = instance.assess("PRE_LAB", values)

    assert list(response["probabilities"]) == instance.class_order
    assert response["thresholds"] == instance.bundles["PRE_LAB"]["thresholds"]
    assert all(np.isfinite(list(response["probabilities"].values())))
    assert response["schema_version"] == "3.1.0"
    assert response["provenance"]["run_id"] == instance.run_id
    assert response["provenance"]["analysis_policy_id"] == instance.manifest[
        "analysis_policy_id"
    ]


def test_validation_rejects_unknown_identifier_and_hard_invalid_value():
    schema = {
        "fields": [
            {
                "field_id": "age",
                "type": "number",
                "required": True,
                "hard_bounds": {"minimum": 0, "maximum": 130},
                "soft_warning_bounds": None,
            }
        ],
        "forbidden_fields": ["patient_id"],
    }
    with pytest.raises(AssessmentValidationError, match="unknown"):
        validate_assessment({"age": 20, "extra": 1}, schema)
    with pytest.raises(AssessmentValidationError, match="forbidden"):
        validate_assessment({"age": 20, "patient_id": "x"}, schema)
    with pytest.raises(AssessmentValidationError, match="hard range"):
        validate_assessment({"age": 500}, schema)


def test_missing_input_forces_abstention():
    instance = service()
    response = instance.assess("PRE_LAB", {})
    assert response["abstention"]["required"] is True
    assert "INSUFFICIENT_INPUT" in response["abstention"]["reasons"]


def test_http_handler_rejects_content_type_and_never_caches():
    status, headers, payload = handle_assessment(b"{}", "text/plain")
    assert status == 415
    assert headers["Cache-Control"] == "no-store"
    assert "request" not in json.dumps(payload).lower()


def test_http_handler_returns_generic_invalid_input_without_health_values():
    secret_value = "private-health-value"
    status, _, payload = handle_assessment(
        json.dumps(
            {"mode": "PRE_LAB", "values": {"unknown": secret_value}}
        ).encode(),
        "application/json",
        service=service(),
    )
    assert status == 400
    assert secret_value not in json.dumps(payload)
