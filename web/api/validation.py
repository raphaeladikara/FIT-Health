"""Schema-driven assessment input validation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AssessmentValidationError(ValueError):
    message: str
    field_errors: dict[str, str] | None = None

    def __str__(self) -> str:
        return self.message


def validate_assessment(
    values: dict[str, Any], schema: dict[str, Any]
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    if not isinstance(values, dict):
        raise AssessmentValidationError("assessment values must be an object")
    fields = {field["field_id"]: field for field in schema["fields"]}
    forbidden = set(schema.get("forbidden_fields", []))
    forbidden_present = forbidden.intersection(values)
    if forbidden_present:
        raise AssessmentValidationError(
            f"forbidden fields: {sorted(forbidden_present)}"
        )
    unknown = set(values) - set(fields)
    if unknown:
        raise AssessmentValidationError(f"unknown fields: {sorted(unknown)}")
    cleaned = {}
    warnings = []
    errors = {}
    for field_id, field in fields.items():
        value = values.get(field_id)
        if value in ("", None):
            if field.get("required"):
                errors[field_id] = "required"
            cleaned[field_id] = None
            continue
        if field.get("type") == "number":
            try:
                value = float(value)
            except (TypeError, ValueError):
                errors[field_id] = "must be numeric"
                continue
            hard = field.get("hard_bounds")
            if hard and (
                value < hard.get("minimum", float("-inf"))
                or value > hard.get("maximum", float("inf"))
            ):
                errors[field_id] = "outside hard range"
                continue
            soft = field.get("soft_warning_bounds")
            if soft and (
                value < soft.get("minimum", float("-inf"))
                or value > soft.get("maximum", float("inf"))
            ):
                warnings.append(
                    {"field_id": field_id, "code": "OUT_OF_DISTRIBUTION"}
                )
        allowed = field.get("allowed_values")
        if allowed and value not in allowed:
            warnings.append({"field_id": field_id, "code": "UNSEEN_CATEGORY"})
        cleaned[field_id] = value
    if errors:
        raise AssessmentValidationError(
            "one or more fields are invalid: "
            + "; ".join(f"{field} {reason}" for field, reason in errors.items()),
            errors,
        )
    return cleaned, warnings
