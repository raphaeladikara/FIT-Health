"""Feature lineage, availability stage, and clinical input validity contracts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


VALID_STAGES = {"PRE_LAB", "LAB_AWARE", "RESEARCH_ONLY"}


@dataclass(frozen=True)
class FeatureSpec:
    canonical_raw_name: str
    derived_representation: str
    stage: str
    transformation: str
    missingness_behavior: str
    unit: str | None
    hard_invalid_min: float | None
    hard_invalid_max: float | None
    soft_warning_policy: str
    leakage_rationale: str
    source_stage: str | None = None


@dataclass(frozen=True)
class FeatureContract:
    version: str
    features: tuple[FeatureSpec, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "features": [asdict(feature) for feature in self.features],
        }

    @property
    def content_hash(self) -> str:
        encoded = json.dumps(
            self.to_dict(), sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def validate_feature_contract(contract: FeatureContract) -> None:
    if not contract.version:
        raise ValueError("feature contract version is required")
    raw_stages: dict[str, set[str]] = {}
    for feature in contract.features:
        if not feature.canonical_raw_name:
            raise ValueError(
                f"{feature.derived_representation}: raw-source lineage is required"
            )
        if feature.stage not in VALID_STAGES:
            raise ValueError(f"invalid feature stage: {feature.stage}")
        source_stage = feature.source_stage or feature.stage
        if source_stage == "RESEARCH_ONLY" and feature.stage != "RESEARCH_ONLY":
            raise ValueError(
                f"RESEARCH_ONLY source cannot enter {feature.stage}: "
                f"{feature.canonical_raw_name}"
            )
        if (
            "diagnos" in feature.canonical_raw_name.lower()
            and feature.stage != "RESEARCH_ONLY"
        ):
            raise ValueError(
                "diagnosis-restating raw sources must remain RESEARCH_ONLY"
            )
        if (
            feature.hard_invalid_min is not None
            and feature.hard_invalid_max is not None
            and feature.hard_invalid_min >= feature.hard_invalid_max
        ):
            raise ValueError("hard-invalid minimum must be below maximum")
        raw_stages.setdefault(feature.canonical_raw_name, set()).add(feature.stage)
    contradictory = {
        raw: stages for raw, stages in raw_stages.items() if len(stages) > 1
    }
    if contradictory:
        raise ValueError(f"contradictory raw feature stages: {contradictory}")


def load_clinical_ranges(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
