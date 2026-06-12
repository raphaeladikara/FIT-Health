"""export_web_data.py — build the static web bundle for the Vercel dashboard.

Reads the precomputed pipeline artifacts (``outputs/tables`` + ``summary.json``),
serialises the needed tables to compact JSON, and copies the figures into
``web/figures``. The static site (``web/index.html``) consumes these — so the
dashboard needs **no backend** and deploys to Vercel as plain static files.

Run AFTER ``run_pipeline.py``:   python export_web_data.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
DASH = ROOT / "outputs" / "dashboard_data"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"
WEB_FIG = WEB / "figures"


def _records(name: str, cols: list[str] | None = None, round_to: int = 4):
    p = TABLES / name
    if not p.exists():
        return []
    df = pd.read_csv(p)
    if cols:
        df = df[[c for c in cols if c in df.columns]]
    # round floats for a smaller, cleaner payload
    for c in df.select_dtypes("float").columns:
        df[c] = df[c].round(round_to)
    return json.loads(df.to_json(orient="records"))


def main() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    WEB_FIG.mkdir(parents=True, exist_ok=True)

    summary = json.loads((DASH / "summary.json").read_text(encoding="utf-8"))

    dashboard = {
        "summary": summary,
        "label_distribution": _records("label_distribution.csv"),
        "top_combinations": _records("label_top_combinations.csv"),
        "leaderboard": _records("model_leaderboard.csv"),
        "per_label": _records("per_label_metrics.csv"),
        "threshold_opt": _records("threshold_optimization.csv"),
        "threshold_policies": _records("threshold_policies.csv"),
        "calibration": _records("calibration_metrics.csv"),
        "conformal_per_label": _records("conformal_metrics.csv"),
        "conformal_examples": _records("conformal_prediction_examples.csv"),
        "importance_global": _records("feature_importance_global.csv"),
        "importance_per_label": _records("feature_importance_per_label.csv"),
        "fairness": _records("fairness_metrics.csv"),
        "fairness_gaps": _records("fairness_recall_gaps.csv"),
        "loco": _records("leave_one_center_out.csv"),
        "resource": _records("resource_simulation.csv"),
        "policy_tradeoff": _records("threshold_policy_resource_tradeoff.csv"),
        "coinfection_models": _records("coinfection_model_metrics.csv"),
        "leakage": _records("leakage_candidates.csv",
                            ["feature", "decision", "best_label",
                             "max_single_feature_auc", "mutual_info", "rationale"]),
    }
    (WEB_DATA / "dashboard.json").write_text(
        json.dumps(dashboard, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    patients = _records("vectra_patient_level_predictions.csv")
    (WEB_DATA / "patients.json").write_text(
        json.dumps(patients, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # copy figures
    n = 0
    for png in FIGURES.glob("*.png"):
        shutil.copy2(png, WEB_FIG / png.name)
        n += 1

    print(f"[web export] dashboard.json + patients.json ({len(patients)} patients) written")
    print(f"[web export] {n} figures copied to {WEB_FIG}")


if __name__ == "__main__":
    main()
