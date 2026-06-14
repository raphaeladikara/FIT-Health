"""Validate public provenance, privacy, parity metadata, and security gates."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DATA = WEB / "data"
MODEL = WEB / "model"
FORBIDDEN_KEYS = {
    "uuid",
    "patient_id",
    "true_labels",
    "ground_truth",
    "name",
    "email",
    "phone",
}
FORBIDDEN_CLAIMS = {
    "confirmed diagnosis",
    "treatment recommendation",
    "safe to discharge",
    "validated clinical impact",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def validate_web_bundle() -> dict[str, list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    passed: list[str] = []
    payloads = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in DATA.glob("*.json")
    }
    required = {
        "manifest.json",
        "evidence.json",
        "input-schema.json",
        "demo-cases.json",
    }
    missing = required - set(payloads)
    if missing:
        errors.append(f"missing public documents: {sorted(missing)}")
        return {"errors": errors, "warnings": warnings, "passed_checks": passed}
    manifest = payloads["manifest.json"]
    evidence = payloads["evidence.json"]
    input_schema = payloads["input-schema.json"]
    cases = payloads["demo-cases.json"]
    for name, payload in payloads.items():
        forbidden = [key for key in walk(payload) if key.lower() in FORBIDDEN_KEYS]
        if forbidden:
            errors.append(f"{name}: forbidden keys {sorted(set(forbidden))}")
    if len({
        manifest["notebook_run_id"],
        evidence["run_id"],
        input_schema["run_id"],
    }) != 1:
        errors.append("run ID mismatch")
    else:
        passed.append("run IDs agree")
    for document_name, document in manifest["documents"].items():
        filename = Path(document["path"]).name
        payload = payloads.get(filename)
        if payload is None:
            errors.append(f"manifest document missing: {document_name}")
        elif hashlib.sha256(canonical_bytes(payload)).hexdigest() != document["sha256"]:
            errors.append(f"{document_name} hash mismatch")
    for mode, artifact in manifest["models"].items():
        path = WEB / artifact["path"].removeprefix("web/")
        if not path.exists() or sha256(path) != artifact["sha256"]:
            errors.append(f"{mode} model hash mismatch")
    public_text = json.dumps(payloads, ensure_ascii=False).lower()
    for claim in FORBIDDEN_CLAIMS:
        if claim in public_text:
            errors.append(f"forbidden public claim: {claim}")
    if "RESEARCH_ONLY" in public_text or '"FULL"' in public_text:
        errors.append("research-only evidence is public")
    if not all(case.get("provenance") == "illustrative_synthetic" for case in cases):
        errors.append("all demo cases must be illustrative_synthetic")
    if not manifest.get("production_rate_limit_required"):
        errors.append("production rate-limit declaration missing")
    vercel = json.loads((WEB / "vercel.json").read_text(encoding="utf-8"))
    vercel_text = json.dumps(vercel)
    if "no-store" not in vercel_text or "Content-Security-Policy" not in vercel_text:
        errors.append("API caching or CSP security gate missing")
    if not errors:
        passed.extend(
            [
                "privacy keys absent",
                "document and model hashes agree",
                "synthetic cases verified",
                "security headers declared",
            ]
        )
    return {"errors": errors, "warnings": warnings, "passed_checks": passed}


def main() -> None:
    report = validate_web_bundle()
    print(json.dumps(report, indent=2))
    raise SystemExit(1 if report["errors"] else 0)


if __name__ == "__main__":
    main()
