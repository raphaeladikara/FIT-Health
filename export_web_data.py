"""Publish a verified web bundle from one locked scientific release only."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from src.release_bundle import canonical_json_bytes, content_hash


ROOT = Path(__file__).resolve().parent
LATEST = ROOT / "outputs" / "releases" / "latest.json"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"
WEB_MODEL = WEB / "model"
WEB_FIGURES = WEB / "figures"
PUBLIC_SCHEMA_VERSION = "3.1.0"
NOTEBOOK = ROOT / "VECTRA_X_Final_Submission.ipynb"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json_bytes(payload))
    temporary.replace(path)


def _json_hash(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _analysis_policy_id(release: dict[str, Any]) -> str:
    if release.get("analysis_policy_id"):
        return str(release["analysis_policy_id"])
    selected = {
        track: {
            "policy_id": policy["policy_id"],
            "thresholds": policy["thresholds"],
            "model_hash": policy["model_hash"],
        }
        for track, policy in release["policies"].items()
    }
    return _json_hash(selected)[:16]


def _primary_track_summary(release: dict[str, Any]) -> dict[str, Any]:
    rows = {
        row["track"]: row for row in release["evidence"]["frozen_test"]
    }
    primary = rows["PRE_LAB"]
    comparison = rows["LAB_AWARE"]
    return {
        "track": "PRE_LAB",
        "model": primary["model"],
        "macro_f1": primary["macro_f1"],
        "micro_f1": primary["micro_f1"],
        "macro_pr_auc": primary["macro_pr_auc"],
        "macro_recall": primary["macro_recall"],
        "comparison_track": "LAB_AWARE",
        "comparison_macro_f1": comparison["macro_f1"],
        "comparison_micro_f1": comparison["micro_f1"],
        "comparison_macro_pr_auc": comparison["macro_pr_auc"],
        "decision": (
            "PRE_LAB remains the primary operational prototype because it leads "
            "micro-F1 and macro PR-AUC without requiring laboratory inputs."
        ),
    }


def _rare_label_summary(release: dict[str, Any]) -> dict[str, Any]:
    rows = {
        row["label"]: row
        for row in release["evidence"]["per_label"]
        if row["track"] == "PRE_LAB"
    }
    return {
        label: {
            "frozen_support": int(rows[label]["support_pos"]),
            "recall": rows[label]["recall"],
            "f1": rows[label]["f1"],
            "false_negatives": int(rows[label]["fn"]),
            "routing": "confirmatory_testing_and_clinician_review",
        }
        for label in ("typhoid", "yellow_fever")
    }


def _center_transfer_summary(release: dict[str, Any]) -> dict[str, Any]:
    rows = release["evidence"]["center_transfer"]
    values = [float(row["macro_f1"]) for row in rows]
    return {
        "macro_f1_min": min(values),
        "macro_f1_max": max(values),
        "n_centers": len(rows),
        "interpretation": (
            "Center transfer is the principal generalization warning; local "
            "validation is required before operational use."
        ),
    }


def load_locked_release(
    latest_path: str | Path = LATEST,
) -> tuple[dict[str, Any], Path]:
    latest_file = Path(latest_path)
    latest = _read_json(latest_file)
    release_path = ROOT / latest["release_path"]
    release = _read_json(release_path)
    if content_hash(release_path) != latest["content_hash"]:
        raise ValueError("latest.json scientific release hash mismatch")
    return release, release_path


def verify_release_provenance(
    release: dict[str, Any], release_path: Path
) -> None:
    lock = release["lock_manifest"]
    if release["source_commit"] != lock["source_commit"]:
        raise ValueError("source commit mismatch")
    if release["dataset"]["split_hash"] != lock["split_hash"]:
        raise ValueError("frozen split hash mismatch")
    if release["feature_contract"]["version"] != lock["feature_contract_hash"]:
        raise ValueError("feature contract hash mismatch")
    for track, artifact in release["artifacts"]["models"].items():
        source = release_path.parent / artifact["path"]
        if content_hash(source) != artifact["sha256"]:
            raise ValueError(f"{track} model hash mismatch")
        policy = release["policies"][track]
        if policy["model_hash"] != artifact["sha256"]:
            raise ValueError(f"{track} policy/model mismatch")
        if policy["stage"] in {"FULL", "RESEARCH_ONLY"}:
            raise ValueError("research-only evidence cannot be public deployable evidence")


def build_public_evidence(release: dict[str, Any]) -> dict[str, Any]:
    evidence = release["evidence"]
    primary = _primary_track_summary(release)
    return {
        "schema_version": PUBLIC_SCHEMA_VERSION,
        "run_id": release["run_id"],
        "notebook_sha256": release.get(
            "notebook_sha256", content_hash(NOTEBOOK)
        ),
        "analysis_policy_id": _analysis_policy_id(release),
        "safe_scope": (
            "Differential-risk review and confirmatory-testing support only. "
            "This prototype does not diagnose disease or recommend treatment."
        ),
        "executive_summary": {
            "primary_track": "PRE_LAB",
            "cohort": release["dataset"]["cohort_counts"],
            "policies": release["policies"],
            "safe_claims": release["safe_claims"],
        },
        "primary_track_summary": primary,
        "narrative": {
            "prototype_positioning": (
                "A single-file scientific submission with an executed "
                "submission-dependency audit, implemented as a live operational "
                "prototype for differential-risk review."
            ),
            "patient_workflow": (
                "Anonymous intake is converted into calibrated differential risk, "
                "uncertainty, review routing, and an assumption-bound resource projection."
            ),
            "primary_track_decision": primary["decision"],
        },
        "rare_label_summary": _rare_label_summary(release),
        "center_transfer_summary": _center_transfer_summary(release),
        "cohort_and_partitions": {
            "counts": release["dataset"]["cohort_counts"],
            "partition_labels": release["dataset"]["partition_labels"],
        },
        "data_quality_and_leakage": {
            "cohort_audit": evidence["cohort_audit"],
            "leakage": evidence["leakage"],
        },
        "validation_and_frozen_test": {
            "nested_validation": evidence["validation"],
            "frozen_test": evidence["frozen_test"],
            "metrics": release["metrics"],
            "per_label": evidence["per_label"],
        },
        "baselines_and_ablations": {
            "baselines": evidence["baselines"],
            "ablations": evidence["ablations"],
        },
        "calibration_and_prediction_sets": {
            "calibration": evidence["calibration"],
            "prediction_sets": evidence["prediction_sets"],
        },
        "risk_coverage_and_decision_scenarios": {
            "risk_coverage": evidence["risk_coverage"],
            "scenarios": evidence["scenarios"],
        },
        "fairness_and_center_transfer": {
            "fairness": evidence["fairness"],
            "center_transfer": evidence["center_transfer"],
        },
        "limitations": release["limitations"],
        "deployment_gates": release["deployment_gates"],
    }


def build_public_input_schema(release: dict[str, Any]) -> dict[str, Any]:
    fields = []
    for source in release["deployable_input_schema"]["fields"]:
        field = dict(source)
        field["field_id"] = field.pop("name")
        fields.append(field)
    return {
        "schema_version": PUBLIC_SCHEMA_VERSION,
        "run_id": release["run_id"],
        "modes": ["PRE_LAB", "LAB_AWARE"],
        "fields": fields,
        "forbidden_fields": [
            "name",
            "email",
            "phone",
            "patient_id",
            "uuid",
            "notes",
            "free_text",
        ],
    }


def copy_verified_models(
    release: dict[str, Any], release_path: Path
) -> dict[str, dict[str, str]]:
    WEB_MODEL.mkdir(parents=True, exist_ok=True)
    expected = set()
    copied = {}
    for track, artifact in release["artifacts"]["models"].items():
        source = release_path.parent / artifact["path"]
        destination = WEB_MODEL / f"{track.lower()}.joblib"
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(source.read_bytes())
        temporary.replace(destination)
        if content_hash(destination) != artifact["sha256"]:
            raise ValueError(f"{track} copied model hash mismatch")
        expected.add(destination.name)
        copied[track] = {
            "path": f"model/{destination.name}",
            "sha256": artifact["sha256"],
        }
    for stale in WEB_MODEL.glob("*.joblib"):
        if stale.name not in expected:
            stale.unlink()
    return copied


def copy_verified_figures(
    release: dict[str, Any], release_path: Path
) -> dict[str, dict[str, str]]:
    WEB_FIGURES.mkdir(parents=True, exist_ok=True)
    expected = set()
    copied = {}
    for name, artifact in release["artifacts"].get("figures", {}).items():
        source = release_path.parent / artifact["path"]
        destination = WEB_FIGURES / Path(artifact["path"]).name
        if content_hash(source) != artifact["sha256"]:
            raise ValueError(f"{name} figure hash mismatch")
        shutil.copyfile(source, destination)
        expected.add(destination.name)
        copied[name] = {
            "path": f"figures/{destination.name}",
            "sha256": artifact["sha256"],
        }
    for stale in WEB_FIGURES.glob("*"):
        if stale.is_file() and stale.name not in expected:
            stale.unlink()
    return copied


def _synthetic_cases(input_schema: dict[str, Any]) -> list[dict[str, Any]]:
    numeric = [
        field for field in input_schema["fields"] if field["type"] == "number"
    ]
    base = {field["field_id"]: None for field in input_schema["fields"]}
    low = dict(base)
    for index, field in enumerate(numeric[:6]):
        low[field["field_id"]] = 35.0 + index
    ood = dict(low)
    if numeric:
        ood[numeric[0]["field_id"]] = 10000
    return [
        {
            "case_id": "SYNTH-LOW-UNCERTAINTY",
            "label": "Illustrative complete pre-lab example",
            "mode": "PRE_LAB",
            "provenance": "illustrative_synthetic",
            "values": low,
        },
        {
            "case_id": "SYNTH-MISSING",
            "label": "Illustrative missing-input review example",
            "mode": "PRE_LAB",
            "provenance": "illustrative_synthetic",
            "values": base,
        },
        {
            "case_id": "SYNTH-OOD",
            "label": "Illustrative out-of-distribution example",
            "mode": "PRE_LAB",
            "provenance": "illustrative_synthetic",
            "values": ood,
        },
    ]


def write_public_manifest(
    release: dict[str, Any],
    evidence: dict[str, Any],
    input_schema: dict[str, Any],
    cases: list[dict[str, Any]],
    models: dict[str, Any],
    figures: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "schema_version": PUBLIC_SCHEMA_VERSION,
        "notebook_run_id": release["run_id"],
        "notebook_sha256": release.get("notebook_sha256", content_hash(NOTEBOOK)),
        "analysis_policy_id": _analysis_policy_id(release),
        "scientific_schema_version": release["schema_version"],
        "source_commit": release["source_commit"],
        "generated_at": release["timestamp"],
        "documents": {
            "evidence": {
                "path": "data/evidence.json",
                "sha256": _json_hash(evidence),
            },
            "input_schema": {
                "path": "data/input-schema.json",
                "sha256": _json_hash(input_schema),
            },
            "demo_cases": {
                "path": "data/demo-cases.json",
                "sha256": _json_hash(cases),
            },
        },
        "models": models,
        "figures": figures,
        "policy_ids": {
            track: policy["policy_id"]
            for track, policy in release["policies"].items()
        },
        "class_order": release["policies"]["PRE_LAB"]["class_order"],
        "safe_scope": evidence["safe_scope"],
        "production_rate_limit_required": True,
    }
    _write_json(WEB_DATA / "manifest.json", manifest)
    _write_json(WEB_MODEL / "model-manifest.json", {
        "run_id": release["run_id"],
        "notebook_sha256": manifest["notebook_sha256"],
        "analysis_policy_id": manifest["analysis_policy_id"],
        "models": models,
        "policy_ids": manifest["policy_ids"],
        "class_order": manifest["class_order"],
    })
    return manifest


def main() -> None:
    release, release_path = load_locked_release()
    verify_release_provenance(release, release_path)
    evidence = build_public_evidence(release)
    input_schema = build_public_input_schema(release)
    cases = _synthetic_cases(input_schema)
    models = copy_verified_models(release, release_path)
    figures = copy_verified_figures(release, release_path)
    _write_json(WEB_DATA / "evidence.json", evidence)
    _write_json(WEB_DATA / "input-schema.json", input_schema)
    _write_json(WEB_DATA / "demo-cases.json", cases)
    legacy = WEB_DATA / "dashboard.json"
    if legacy.exists():
        legacy.unlink()
    manifest = write_public_manifest(
        release, evidence, input_schema, cases, models, figures
    )
    print(
        f"[web export] run={manifest['notebook_run_id']} "
        f"models={len(models)} synthetic_cases={len(cases)}"
    )


if __name__ == "__main__":
    main()
