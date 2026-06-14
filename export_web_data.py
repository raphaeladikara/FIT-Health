"""Build the static VECTRA-X dashboard from canonical notebook evidence.

Run after executing ``notebooks/VECTRA_X_Final_Competition_Notebook.ipynb``.
The exporter reads the corrected ``outputs/tables/final_*.csv`` tables, adds
only the supporting aggregate scenario artifacts required by the existing
dashboard, and publishes no identifiers or patient ground truth.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"
WEB = ROOT / "web"
WEB_DATA = WEB / "data"
WEB_FIG = WEB / "figures"
SCHEMAS = WEB_DATA / "schemas"

ACTIVE_LABELS = [
    "malaria",
    "other_diseases",
    "dengue",
    "typhoid",
    "yellow_fever",
]
PUBLIC_CASE_COLUMNS = [
    "case_id",
    "scenario",
    "triage_category",
    "triage_score",
    "uncertainty_category",
    "predicted_labels",
    "conformal_set",
    *[f"calprob_{label}" for label in ACTIVE_LABELS],
]


def _frame(name: str) -> pd.DataFrame:
    path = TABLES / name
    if not path.exists():
        raise FileNotFoundError(f"Required dashboard source is missing: {path}")
    return pd.read_csv(path)


def _records(
    name: str,
    cols: list[str] | None = None,
    round_to: int = 4,
) -> list[dict]:
    frame = _frame(name)
    if cols:
        missing = set(cols) - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")
        frame = frame[cols]
    for column in frame.select_dtypes("float").columns:
        frame[column] = frame[column].round(round_to)
    return json.loads(frame.to_json(orient="records"))


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


def _public_cases(limit: int = 12) -> list[dict]:
    path = WEB_DATA / "demo-cases.json"
    if not path.exists():
        raise FileNotFoundError(
            "The curated anonymous demo case fixture is missing: "
            f"{path}"
        )
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not 0 < len(cases) <= limit:
        raise ValueError(f"Expected 1-{limit} curated public cases")
    missing = [
        (case.get("case_id", f"row-{index}"), sorted(set(PUBLIC_CASE_COLUMNS) - set(case)))
        for index, case in enumerate(cases)
        if set(PUBLIC_CASE_COLUMNS) - set(case)
    ]
    if missing:
        raise ValueError(f"Curated public cases do not match the contract: {missing}")
    return cases


def _thresholds(records: list[dict], policy: str = "operational") -> dict:
    return {
        "policy": policy,
        "values": {
            row["label"]: round(float(row[policy]), 4)
            for row in records
            if row.get("label") in ACTIVE_LABELS and row.get(policy) is not None
        },
    }


def _prediction_set_summary(rows: list[dict], cohort_size: int) -> dict[str, float]:
    positives = sum(int(row["test_positives"]) for row in rows)
    covered = sum(int(row["covered_positives"]) for row in rows)
    return {
        "avg_set_size": round(
            sum(int(row["predicted_inclusions"]) for row in rows) / cohort_size,
            4,
        ),
        "overall_coverage": round(covered / positives, 4),
        "macro_label_coverage": round(
            sum(float(row["empirical_coverage"]) for row in rows) / len(rows),
            4,
        ),
        "false_negative_risk": round(1 - covered / positives, 4),
        "policy": "exact_uncapped_empirical",
    }


def _label_distribution(cohort_size: int) -> list[dict]:
    frame = _frame("label_distribution.csv")
    frame["prevalence_pct"] = (
        100 * frame["positives"].astype(float) / cohort_size
    ).round(2)
    return json.loads(frame.to_json(orient="records"))


def _summary(
    final_metrics: list[dict],
    conformal_exact: list[dict],
    cohort_size: int,
) -> dict:
    metrics = {row["track"]: row for row in final_metrics}
    combinations = _frame("label_top_combinations.csv")
    feature_sets = _frame("feature_sets.csv").set_index("feature_set")["n_features"]
    resource = _frame("resource_simulation.csv").set_index("metric")["count"]
    coinfection_rows = _frame("final_coinfection_metrics.csv")
    coinfection = coinfection_rows[
        coinfection_rows["partition"] == "frozen_test_once"
    ].iloc[0]
    loco = _frame("final_loco.csv")
    n_multilabel = int(
        combinations.loc[
            combinations["combination"].str.contains(r"\+", regex=True),
            "n_patients",
        ].sum()
    )
    triage_distribution = {
        name.removeprefix("tier_").replace("_", " "): int(value)
        for name, value in resource.items()
        if name.startswith("tier_")
    }
    return {
        "project": "VECTRA-X",
        "shape": [cohort_size, 109],
        "supervised_cohort": cohort_size,
        "excluded_unknown_target_rows": 1,
        "active_labels": ACTIVE_LABELS,
        "inactive_labels": ["chikungunya", "zika", "option_8"],
        "n_multilabel_patients": n_multilabel,
        "feature_set_sizes": {
            "PRE_LAB_TRIAGE": int(feature_sets["PRE_LAB_TRIAGE"]),
            "LAB_AWARE_CONFIRMATION": int(
                feature_sets["LAB_AWARE_CONFIRMATION"]
            ),
        },
        "n_train": cohort_size - 78,
        "n_test": 78,
        "best_model_per_track": {
            track: row["model"] for track, row in metrics.items()
        },
        "test_metrics": {
            track: {
                key: value
                for key, value in row.items()
                if key not in {"track", "model"}
            }
            for track, row in metrics.items()
        },
        "conformal": _prediction_set_summary(conformal_exact, 78),
        "coinfection": {
            "best_model": str(coinfection["model"]),
            "roc_auc": round(float(coinfection["roc_auc"]), 4),
            "pr_auc": round(float(coinfection["pr_auc"]), 4),
            "recall": round(float(coinfection["recall"]), 4),
            "evidence_scope": "single frozen-test evaluation",
        },
        "triage_distribution": triage_distribution,
        "loco_macro_f1": [round(float(value), 4) for value in loco["macro_f1"]],
        "governance_note": (
            "PRE_LAB is the primary research prototype. LAB_AWARE is a post-test "
            "comparison and did not improve aggregate frozen-test macro-F1 or "
            "macro-PR-AUC. Target-restating FULL evidence is not public."
        ),
    }


def main() -> None:
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    WEB_FIG.mkdir(parents=True, exist_ok=True)
    SCHEMAS.mkdir(parents=True, exist_ok=True)

    cohort = _frame("final_cohort_audit.csv").iloc[0]
    cohort_size = int(cohort["n_supervised"])
    if cohort_size != 299:
        raise ValueError(f"Expected canonical supervised cohort 299, got {cohort_size}")

    final_metrics = _records("final_test_metrics.csv")
    if {row["track"] for row in final_metrics} != {"PRE_LAB", "LAB_AWARE"}:
        raise ValueError("Final metrics must contain only PRE_LAB and LAB_AWARE")

    conformal_exact = _records("final_conformal_exact.csv")
    conformal_pragmatic = _records("final_conformal_pragmatic.csv")
    threshold_policies = _records("threshold_policies.csv")
    dashboard = {
        "summary": _summary(final_metrics, conformal_exact, cohort_size),
        "label_distribution": _label_distribution(cohort_size),
        "top_combinations": _records("label_top_combinations.csv"),
        "leaderboard": _records("final_model_comparison.csv"),
        "per_label": _records("final_per_label_metrics.csv"),
        "threshold_policies": threshold_policies,
        "thresholds": _thresholds(threshold_policies),
        "calibration": _records("final_calibration_metrics.csv"),
        "conformal_exact": conformal_exact,
        "conformal_pragmatic": conformal_pragmatic,
        "importance_global": _records("feature_importance_global.csv"),
        "fairness": _records("final_fairness_metrics.csv"),
        "loco": _records("final_loco.csv"),
        "resource": _records("resource_simulation.csv"),
        "policy_tradeoff": _records("threshold_policy_resource_tradeoff.csv"),
        "scenario_sensitivity": _records("final_scenario_sensitivity.csv"),
        "leakage": _records(
            "final_leakage_audit.csv",
            [
                "feature",
                "decision",
                "best_label",
                "max_single_feature_auc",
                "mutual_info",
                "rationale",
            ],
        ),
    }
    _atomic_json(WEB_DATA / "dashboard.json", dashboard)

    cases = _public_cases()
    _atomic_json(WEB_DATA / "demo-cases.json", cases)
    legacy_patients = WEB_DATA / "patients.json"
    if legacy_patients.exists():
        legacy_patients.unlink()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    manifest = {
        "schema_version": "2.0.0",
        "run_id": f"{now.strftime('%Y-%m-%dT%H%M%SZ')}-final-prelab-et",
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "canonical": True,
        "model_track": "PRE_LAB",
        "model_name": dashboard["summary"]["best_model_per_track"]["PRE_LAB"],
        "evaluation_split": "single frozen held-out test",
        "cohort_size": cohort_size,
        "active_labels": len(ACTIVE_LABELS),
        "source_commit": _source_commit(),
        "scientific_source": "VECTRA_X_Final_Competition_Notebook.ipynb",
    }
    _atomic_json(WEB_DATA / "manifest.json", manifest)

    print(
        f"[web export] canonical cohort n={cohort_size}; "
        f"{len(cases)} anonymous cases; static figures retained"
    )


if __name__ == "__main__":
    main()
