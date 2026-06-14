"""Execute and export the canonical VECTRA-X research workflow.

This is the command-line counterpart of the final competition notebook. It
starts from the raw competition files, writes only corrected final evidence
tables, and optionally refreshes the static dashboard bundle.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.notebook_workflow import ResearchWorkflowResult, run_research_workflow
from src.release_bundle import export_release_bundle

ROOT = Path(__file__).resolve().parent
TABLES = ROOT / "outputs" / "tables"


def export_final_tables(result: ResearchWorkflowResult) -> list[Path]:
    """Write the canonical evidence tables consumed by the notebook and web."""
    threshold_rows = []
    for label, performance in result.thresholds["PRE_LAB"].items():
        threshold_rows.append(
            {
                "label": label,
                "performance": performance,
                "safety": max(0.05, performance - 0.10),
                "operational": performance,
            }
        )

    exports = {
        "final_cohort_audit": pd.DataFrame([result.cohort_audit]),
        "final_target_distribution": result.target_distribution,
        "final_top_combinations": result.top_combinations,
        "final_feature_contract": result.feature_contract,
        "final_leakage_audit": result.leakage_audit,
        "final_baselines": result.baselines,
        "final_ablations": result.ablations,
        "final_model_comparison": result.model_comparison,
        "final_repeated_validation": result.repeated_validation,
        "final_test_metrics": result.final_test_metrics,
        "final_per_label_metrics": result.final_per_label,
        "final_metric_intervals": result.final_intervals,
        "final_coinfection_metrics": result.coinfection_results,
        "final_calibration_metrics": result.calibration_metrics,
        "final_conformal_exact": result.conformal_exact,
        "final_conformal_pragmatic": result.conformal_pragmatic,
        "final_fairness_metrics": result.fairness_metrics,
        "final_loco": result.leave_one_center_out,
        "final_global_importance": result.global_importance,
        "final_threshold_policies": pd.DataFrame(threshold_rows),
        "final_scenario_sensitivity": result.scenario_sensitivity,
    }
    TABLES.mkdir(parents=True, exist_ok=True)
    written = []
    for name, frame in exports.items():
        path = TABLES / f"{name}.csv"
        frame.to_csv(path, index=False, encoding="utf-8-sig")
        written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use the reduced validation configuration for development checks.",
    )
    parser.add_argument(
        "--write-release",
        action="store_true",
        help="Write a versioned scientific release even in quick mode.",
    )
    parser.add_argument(
        "--skip-web",
        action="store_true",
        help="Do not regenerate the static dashboard after a full run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_research_workflow(quick=args.quick)
    if args.quick and not args.write_release:
        print(
            "[pipeline] quick validation complete; canonical tables and web "
            "bundle were not overwritten"
        )
        return

    written = export_final_tables(result)
    release_path = export_release_bundle(result, ROOT)
    print(
        f"[pipeline] exported {len(written)} corrected tables; "
        f"supervised cohort n={result.cohort_audit['n_supervised']}; "
        f"release={release_path}"
    )
    if not args.skip_web:
        import export_web_data

        export_web_data.main()


if __name__ == "__main__":
    main()
