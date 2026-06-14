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
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"
DASH = ROOT / "outputs" / "dashboard_data"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"
WEB_FIG = WEB / "figures"
SCHEMAS = WEB_DATA / "schemas"

PUBLIC_CASE_COLUMNS = [
    "case_id",
    "scenario",
    "triage_category",
    "triage_score",
    "uncertainty_category",
    "predicted_labels",
    "conformal_set",
    "calprob_malaria",
    "calprob_other_diseases",
    "calprob_dengue",
    "calprob_typhoid",
    "calprob_yellow_fever",
]


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


def _atomic_json(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(path)


def _source_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _scenario(row: pd.Series) -> str:
    labels = str(row.get("predicted_labels", ""))
    uncertainty = str(row.get("uncertainty_level", "")).lower()
    tier = str(row.get("triage_category", ""))
    if tier == "Urgent Response Priority":
        return "High-risk rare-label case"
    if uncertainty == "high" or labels.count(",") >= 1:
        return "Ambiguous multi-label case"
    if tier == "Routine Monitoring":
        return "Clear single-label case"
    return "Center-shift stress case"


def _public_cases(limit: int = 12) -> list[dict]:
    source = pd.read_csv(TABLES / "vectra_patient_level_predictions.csv")
    source = source.sort_values(
        ["triage_score", "uncertainty_level"],
        ascending=[False, True],
        kind="stable",
    )
    source["scenario"] = source.apply(_scenario, axis=1)
    scenario_order = [
        "Clear single-label case",
        "Ambiguous multi-label case",
        "High-risk rare-label case",
        "Center-shift stress case",
    ]
    selected = [
        source[source["scenario"] == scenario].head(3)
        for scenario in scenario_order
    ]
    source = pd.concat(selected, ignore_index=True).head(limit)
    source["case_id"] = [f"CASE-{index:03d}" for index in range(1, len(source) + 1)]
    source["uncertainty_category"] = source["uncertainty_level"]
    cases = source[PUBLIC_CASE_COLUMNS].copy()
    for column in cases.select_dtypes("float").columns:
        cases[column] = cases[column].round(4)
    return json.loads(cases.to_json(orient="records"))


def _thresholds(records: list[dict], policy: str = "operational") -> dict:
    return {
        "policy": policy,
        "values": {
            row["label"]: round(float(row[policy]), 4)
            for row in records
            if row.get("label") and row.get(policy) is not None
        },
    }


def main() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    WEB_FIG.mkdir(parents=True, exist_ok=True)
    SCHEMAS.mkdir(parents=True, exist_ok=True)

    summary = json.loads((DASH / "summary.json").read_text(encoding="utf-8"))

    threshold_policies = _records("threshold_policies.csv")
    dashboard = {
        "summary": summary,
        "label_distribution": _records("label_distribution.csv"),
        "top_combinations": _records("label_top_combinations.csv"),
        "leaderboard": _records("model_leaderboard.csv"),
        "per_label": _records("per_label_metrics.csv"),
        "threshold_opt": _records("threshold_optimization.csv"),
        "threshold_policies": threshold_policies,
        "thresholds": _thresholds(threshold_policies),
        "calibration": _records("calibration_metrics.csv"),
        "conformal_per_label": _records("conformal_metrics.csv"),
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
    _atomic_json(WEB_DATA / "dashboard.json", dashboard)

    cases = _public_cases()
    _atomic_json(WEB_DATA / "demo-cases.json", cases)
    legacy_patients = WEB_DATA / "patients.json"
    if legacy_patients.exists():
        legacy_patients.unlink()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    manifest = {
        "schema_version": "1.0.0",
        "run_id": f"{now.strftime('%Y-%m-%dT%H%M%SZ')}-prelab-et",
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "canonical": True,
        "model_track": "PRE_LAB",
        "model_name": summary["best_model_per_track"]["PRE_LAB"],
        "evaluation_split": "held-out test",
        "cohort_size": int(summary["shape"][0]),
        "active_labels": len(summary["active_labels"]),
        "source_commit": _source_commit(),
    }
    _atomic_json(WEB_DATA / "manifest.json", manifest)

    # copy figures
    n = 0
    for png in FIGURES.glob("*.png"):
        shutil.copy2(png, WEB_FIG / png.name)
        n += 1

    print(f"[web export] dashboard.json + demo-cases.json ({len(cases)} cases) written")
    print(f"[web export] {n} figures copied to {WEB_FIG}")


if __name__ == "__main__":
    main()
