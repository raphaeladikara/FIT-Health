import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

import export_web_data
from web.api.inference import LockedInferenceService


ROOT = Path(__file__).resolve().parents[1]


def test_api_matches_direct_locked_bundle_probabilities():
    export_web_data.main()
    service = LockedInferenceService(ROOT / "web")
    schema = json.loads(
        (ROOT / "web" / "data" / "input-schema.json").read_text(encoding="utf-8")
    )
    values = {field["field_id"]: None for field in schema["fields"]}
    response = service.assess("PRE_LAB", values)

    bundle = joblib.load(ROOT / "web" / "model" / "pre_lab.joblib")
    frame = pd.DataFrame(
        [{column: np.nan for column in bundle["design_columns"]}]
    )
    direct = bundle["model"].predict_proba(frame)[0]
    for index, label in enumerate(bundle["class_order"]):
        calibrator = bundle["calibrators"].get(label)
        if calibrator is not None:
            direct[index] = calibrator(np.array([direct[index]]))[0]
        assert abs(response["probabilities"][label] - direct[index]) < 1e-10
