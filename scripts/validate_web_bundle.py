from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DATA = WEB / "data"
FORBIDDEN_KEYS = {
    "uuid", "patient_id", "true_labels", "ground_truth", "name", "email", "phone",
}


def walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    payloads = {}
    for path in DATA.glob("*.json"):
        payloads[path.name] = json.loads(path.read_text(encoding="utf-8"))
        for key in walk(payloads[path.name]):
            require(key.lower() not in FORBIDDEN_KEYS, f"{path.name}: forbidden key {key}")

    dashboard = payloads["dashboard.json"]
    cases = payloads["demo-cases.json"]
    manifest = payloads["manifest.json"]
    labels = dashboard["summary"]["active_labels"]
    thresholds = dashboard["thresholds"]["values"]

    require(manifest["canonical"] is True, "manifest must be canonical")
    require(manifest["model_track"] != "FULL", "FULL cannot be deployable")
    require(set(labels) == set(thresholds), "threshold labels are incomplete")
    require(dashboard["summary"]["test_metrics"]["PRE_LAB"], "canonical metrics are empty")
    require(0 < len(cases) <= 12, "public case count must be between 1 and 12")

    for case in cases:
        require(case["case_id"].startswith("CASE-"), "invalid public case id")
        for label in labels:
            probability = case[f"calprob_{label}"]
            require(0 <= probability <= 1, f"{case['case_id']}: invalid {label} probability")

    for image in WEB.joinpath("figures").glob("*.png"):
        require(image.stat().st_size > 0, f"empty figure: {image.name}")

    print(f"[validate] {len(payloads)} JSON files, {len(cases)} public cases, {len(labels)} thresholds: OK")


if __name__ == "__main__":
    main()
