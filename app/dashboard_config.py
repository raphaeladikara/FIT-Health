from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
REPORTS = ROOT / "outputs" / "reports"
MODELS = ROOT / "outputs" / "models"
DASHBOARD_DATA = ROOT / "outputs" / "dashboard_data"
PROCESSED = ROOT / "data" / "processed"

MODEL_MODES = {
    "Pre-lab Triage": {
        "file": "pre_lab_model.joblib",
        "track": "PRE_LAB",
        "description": "Primary deployable model using information available before laboratory confirmation.",
    },
    "Lab-aware Confirmation": {
        "file": "lab_aware_model.joblib",
        "track": "LAB_AWARE",
        "description": "Secondary model for use after laboratory or rapid-test information is available.",
    },
    "Full-feature Research-only": {
        "file": None,
        "track": "FULL",
        "description": "Leakage demonstration only. It is not available for patient inference.",
    },
}

TRIAGE_ORDER = [
    "Routine Monitoring",
    "Clinical Review",
    "Confirmatory Test Priority",
    "Urgent Response Priority",
]

TRIAGE_COLORS = {
    "Routine Monitoring": "#2a9d8f",
    "Clinical Review": "#457b9d",
    "Confirmatory Test Priority": "#f4a261",
    "Urgent Response Priority": "#e76f51",
}

DISEASE_COLORS = {
    "malaria": "#2a9d8f",
    "other_diseases": "#7b61a8",
    "dengue": "#e76f51",
    "typhoid": "#f4a261",
    "yellow_fever": "#d4a017",
}

SAFETY_NOTE = (
    "VECTRA-X is a decision-support prototype. Its outputs are not a confirmed "
    "diagnosis and do not replace review by qualified medical professionals."
)
