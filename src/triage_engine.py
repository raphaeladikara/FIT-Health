"""triage_engine — VECTRA-X decision-support layer.

Turns calibrated multi-label probabilities + uncertainty + conformal sets +
co-infection risk into a transparent triage priority score and a 4-tier
category with a recommended *decision-support* action (never a treatment).

Triage score (documented, bounded to [0,1]):

    risk      = sum_j p_cal_j * w_j / sum_j w_j          (label risk-weighted)
    severe    = max_{j in severe} p_cal_j                (rare/severe sensitivity)
    uncert    = normalised predictive entropy            (model uncertainty)
    coinf     = P(co-infection)                          (multi-disease burden)

    score = 0.45*risk + 0.25*severe + 0.15*uncert + 0.15*coinf

Tiers (mapped to the four required categories) are then assigned by transparent
rules on severe-disease probability, uncertainty, co-infection and the conformal
prediction set — see ``assign_tier``.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

TIER_ORDER = ["Routine Monitoring", "Clinical Review",
              "Confirmatory Test Priority", "Urgent Response Priority"]

TIER_ACTION = {
    "Routine Monitoring": "Routine monitoring; document symptoms, no immediate escalation.",
    "Clinical Review": "Manual clinician review and symptom monitoring.",
    "Confirmatory Test Priority": "Prioritise confirmatory testing (rapid test / laboratory) and closer observation.",
    "Urgent Response Priority": "Flag for urgent clinical evaluation / referral.",
}


def _binary_entropy(p: np.ndarray) -> np.ndarray:
    eps = 1e-9
    p = np.clip(p, eps, 1 - eps)
    return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))


def uncertainty_scores(proba: np.ndarray, labels: list[str],
                       set_sizes: np.ndarray | None = None) -> pd.DataFrame:
    """Per-patient uncertainty descriptors + low/moderate/high category."""
    max_prob = proba.max(axis=1)
    mean_entropy = _binary_entropy(proba).mean(axis=1)          # in [0,1]
    sorted_p = np.sort(proba, axis=1)[:, ::-1]
    top2_margin = sorted_p[:, 0] - (sorted_p[:, 1] if proba.shape[1] > 1 else 0)
    n_above = (proba >= 0.5).sum(axis=1)

    df = pd.DataFrame({
        "max_prob": np.round(max_prob, 4),
        "mean_entropy": np.round(mean_entropy, 4),
        "top2_margin": np.round(top2_margin, 4),
        "n_labels_above_0_5": n_above.astype(int),
    })
    if set_sizes is not None:
        df["conformal_set_size"] = set_sizes.astype(int)

    def categorise(r) -> str:
        size = r.get("conformal_set_size", 1)
        # Tuned for a 5-label endemic problem where malaria (~0.9 prob) sets a
        # high entropy floor; thresholds chosen on the calibrated probabilities.
        if (size == 0) or (r["mean_entropy"] >= 0.50) or (r["max_prob"] < 0.50):
            return "high"
        if (size >= 4) or (r["mean_entropy"] >= 0.28) or (r["max_prob"] < 0.78):
            return "moderate"
        return "low"

    df["uncertainty_level"] = df.apply(categorise, axis=1)
    return df


def triage_score(proba_cal: np.ndarray, labels: list[str], cfg: dict[str, Any],
                 uncertainty: pd.DataFrame, coinf_prob: np.ndarray) -> np.ndarray:
    weights = cfg["modeling"]["risk_weights"]
    severe = cfg["modeling"]["severe_labels"]
    w = np.array([weights.get(lab, 1.0) for lab in labels])
    risk = (proba_cal * w).sum(axis=1) / w.sum()
    severe_idx = [labels.index(s) for s in severe if s in labels]
    severe_signal = proba_cal[:, severe_idx].max(axis=1) if severe_idx else np.zeros(len(proba_cal))
    uncert = uncertainty["mean_entropy"].values
    score = 0.45 * risk + 0.25 * severe_signal + 0.15 * uncert + 0.15 * coinf_prob
    return np.clip(score, 0, 1)


def assign_tier(proba_cal: np.ndarray, labels: list[str], cfg: dict[str, Any],
                uncertainty: pd.DataFrame, coinf_prob: np.ndarray,
                conformal_sets: list[list[str]]) -> list[str]:
    severe = set(cfg["modeling"]["severe_labels"])
    severe_idx = [labels.index(s) for s in severe if s in labels]
    mal_idx = labels.index("malaria") if "malaria" in labels else None
    other_idx = labels.index("other_diseases") if "other_diseases" in labels else None
    tiers = []
    for i in range(len(proba_cal)):
        p = proba_cal[i]
        # Severe = non-malaria vector-borne disease signal (dengue / typhoid /
        # yellow fever). Malaria is endemic here (90% prevalence) and is the
        # treatment baseline, NOT by itself an escalation trigger.
        sev_p = p[severe_idx].max() if severe_idx else 0.0
        unc = uncertainty.iloc[i]["uncertainty_level"]
        coinf = coinf_prob[i]
        p_mal = p[mal_idx] if mal_idx is not None else 0.0
        p_other = p[other_idx] if other_idx is not None else 0.0
        pset = conformal_sets[i] if conformal_sets is not None else []
        set_has_severe = any(s in severe for s in pset)

        if (sev_p >= 0.50) or (sev_p >= 0.35 and unc == "high"):
            tiers.append("Urgent Response Priority")
        elif (sev_p >= 0.25) or (coinf >= 0.6 and set_has_severe) or (sev_p >= 0.15 and unc == "high"):
            tiers.append("Confirmatory Test Priority")
        elif (unc == "low") and (sev_p < 0.15) and (coinf < 0.4) and (p_other < 0.4):
            # Stable, confident single-disease (malaria) case with no severe
            # signal and low co-infection risk -> routine management/monitoring.
            tiers.append("Routine Monitoring")
        else:
            tiers.append("Clinical Review")
    return tiers


def build_patient_table(uuids: pd.Series, proba: np.ndarray, proba_cal: np.ndarray,
                        y_true: pd.DataFrame | None, labels: list[str],
                        thresholds: dict[str, float], cfg: dict[str, Any],
                        uncertainty: pd.DataFrame, coinf_prob: np.ndarray,
                        conformal_sets: list[list[str]],
                        explanation_summaries: list[str] | None = None) -> pd.DataFrame:
    """Assemble the full per-patient VECTRA-X output table."""
    n = len(proba)
    pred = np.zeros_like(proba, dtype=int)
    for j, lab in enumerate(labels):
        pred[:, j] = (proba[:, j] >= thresholds.get(lab, 0.5)).astype(int)

    scores = triage_score(proba_cal, labels, cfg, uncertainty, coinf_prob)
    tiers = assign_tier(proba_cal, labels, cfg, uncertainty, coinf_prob, conformal_sets)

    rows = []
    for i in range(n):
        predicted = [labels[j] for j in range(len(labels)) if pred[i, j] == 1]
        row = {
            "uuid": uuids.iloc[i] if uuids is not None else i,
            "predicted_labels": "{" + ", ".join(predicted) + "}" if predicted else "{none}",
            "conformal_set": "{" + ", ".join(conformal_sets[i]) + "}",
            "conformal_set_size": len(conformal_sets[i]),
            "coinfection_prob": round(float(coinf_prob[i]), 4),
            "uncertainty_level": uncertainty.iloc[i]["uncertainty_level"],
            "max_prob": round(float(proba[i].max()), 4),
            "triage_score": round(float(scores[i]), 4),
            "triage_category": tiers[i],
            "recommended_action": TIER_ACTION[tiers[i]],
        }
        for j, lab in enumerate(labels):
            row[f"prob_{lab}"] = round(float(proba[i, j]), 4)
            row[f"calprob_{lab}"] = round(float(proba_cal[i, j]), 4)
        if y_true is not None:
            truth = [labels[j] for j in range(len(labels)) if y_true.iloc[i, j] == 1]
            row["true_labels"] = "{" + ", ".join(truth) + "}" if truth else "{none}"
        if explanation_summaries is not None:
            row["explanation_summary"] = explanation_summaries[i]
        rows.append(row)
    return pd.DataFrame(rows)


def resource_simulation(patient_table: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """Aggregate the patient table into an operational resource view."""
    n = len(patient_table)
    rows = [{"metric": "total_patients", "count": n, "pct": 100.0}]

    for lab in labels:
        col = f"prob_{lab}"
        if col in patient_table:
            # predicted positive = appears in predicted_labels string
            c = int(patient_table["predicted_labels"].str.contains(lab).sum())
            rows.append({"metric": f"predicted_{lab}", "count": c, "pct": round(100 * c / n, 2)})

    cat_counts = patient_table["triage_category"].value_counts()
    for tier in TIER_ORDER:
        c = int(cat_counts.get(tier, 0))
        rows.append({"metric": f"tier_{tier.replace(' ', '_')}", "count": c, "pct": round(100 * c / n, 2)})

    high_priority = int(patient_table["triage_category"].isin(
        ["Confirmatory Test Priority", "Urgent Response Priority"]).sum())
    rows.append({"metric": "high_priority_patients", "count": high_priority, "pct": round(100 * high_priority / n, 2)})

    confirm = int((patient_table["triage_category"] == "Confirmatory Test Priority").sum())
    rows.append({"metric": "require_confirmatory_test", "count": confirm, "pct": round(100 * confirm / n, 2)})

    uncertain = int((patient_table["uncertainty_level"] == "high").sum())
    rows.append({"metric": "high_uncertainty_cases", "count": uncertain, "pct": round(100 * uncertain / n, 2)})

    coinf = int((patient_table["conformal_set_size"] >= 2).sum())
    rows.append({"metric": "ambiguous_or_coinfection_cases", "count": coinf, "pct": round(100 * coinf / n, 2)})

    return pd.DataFrame(rows)


def policy_resource_tradeoff(proba: np.ndarray, labels: list[str],
                             policies: dict[str, dict[str, float]]) -> pd.DataFrame:
    """Compare how many positive predictions each threshold policy produces
    per label (operational burden trade-off)."""
    rows = []
    n = len(proba)
    for pol_name, thr in policies.items():
        row = {"policy": pol_name}
        total = 0
        for j, lab in enumerate(labels):
            c = int((proba[:, j] >= thr.get(lab, 0.5)).sum())
            row[f"flagged_{lab}"] = c
            total += c
        row["total_flags"] = total
        row["avg_flags_per_patient"] = round(total / n, 3)
        rows.append(row)
    return pd.DataFrame(rows)


def scenario_sensitivity(
    proba: np.ndarray,
    labels: list[str],
    weight_scenarios: dict[str, dict[str, float]],
    threshold_scenarios: dict[str, dict[str, float]],
    capacities: list[int],
    false_negative_costs: list[float],
) -> pd.DataFrame:
    """Transparent operational projections under explicitly labeled assumptions."""
    rows = []
    for weight_name, weights in weight_scenarios.items():
        w = np.array([weights.get(label, 1.0) for label in labels], dtype=float)
        weighted_risk = (proba * w).sum(axis=1) / max(w.sum(), 1e-12)
        order = np.argsort(weighted_risk)[::-1]
        for threshold_name, thresholds in threshold_scenarios.items():
            flags = np.column_stack(
                [
                    proba[:, j] >= thresholds.get(label, 0.5)
                    for j, label in enumerate(labels)
                ]
            )
            for capacity in capacities:
                selected = order[: min(capacity, len(order))]
                deferred_flags = int(flags[selected].sum())
                for fn_cost in false_negative_costs:
                    rows.append(
                        {
                            "weight_scenario": weight_name,
                            "threshold_scenario": threshold_name,
                            "capacity": int(capacity),
                            "false_negative_cost": float(fn_cost),
                            "projected_patients_prioritised": int(len(selected)),
                            "projected_label_flags_reviewed": deferred_flags,
                            "projected_unreviewed_flag_cost": round(
                                float((flags.sum() - deferred_flags) * fn_cost), 4
                            ),
                            "interpretation": "scenario projection; not measured clinical impact",
                        }
                    )
    return pd.DataFrame(rows)
