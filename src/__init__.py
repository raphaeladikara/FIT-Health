"""VECTRA-X — Multi-label, leakage-aware clinical triage intelligence system.

FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction.

The package is organised as a sequence of single-responsibility modules that
are orchestrated by ``run_pipeline.py`` and re-used by the notebooks and the
Next.js command center:

    data_loader      raw CSV ingestion (sep=';', decimal=',') + cleaning
    schema_audit     dtype / missingness / cardinality audit
    label_detection  multi-label target discovery + co-occurrence
    leakage_audit    name + statistical leakage screen, stage-gated feature sets
    preprocessing    numeric parsing, OUI/NON encoding, missing indicators
    modeling         multi-label / co-infection / rare-label model tracks
    evaluation       multi-label + per-label metrics
    calibration      probability calibration + reliability
    conformal        split-conformal multi-label prediction sets
    explainability   permutation importance (+ optional SHAP)
    fairness         subgroup recall / FNR gaps, leave-one-center-out
    triage_engine    risk + uncertainty -> triage tier + actions
    visualization    all figures
    report_utils     config / paths / logging / markdown helpers
"""

__version__ = "1.0.0"
RANDOM_STATE = 42
