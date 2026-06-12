"""visualization — all VECTRA-X figures (headless / Agg backend).

Each function takes prepared data + an output Path and returns the Path it
wrote. Styling is centralised for a consistent report-grade look.
"""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import precision_recall_curve, roc_curve

sns.set_theme(style="whitegrid", context="talk")
PALETTE = "viridis"
PRIMARY = "#2a6f97"
ACCENT = "#e36414"


def _save(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# Audit / EDA
# --------------------------------------------------------------------------- #
def target_distribution(distribution: pd.DataFrame, path: Path) -> Path:
    d = distribution.sort_values("positives", ascending=True)
    colors = [ACCENT if s == "inactive" else PRIMARY for s in d["status"]]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(d["label"], d["positives"], color=colors)
    for i, (v, p) in enumerate(zip(d["positives"], d["prevalence_pct"])):
        ax.text(v + 1, i, f"{v} ({p:.1f}%)", va="center", fontsize=11)
    ax.set_title("Disease label prevalence (orange = inactive, 0 positives)")
    ax.set_xlabel("Positive patients")
    return _save(fig, path)


def label_cardinality(cardinality: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(cardinality["n_labels"].astype(str), cardinality["n_patients"], color=PRIMARY)
    for i, (v, p) in enumerate(zip(cardinality["n_patients"], cardinality["pct"])):
        ax.text(i, v + 1, f"{v}\n({p:.0f}%)", ha="center", fontsize=11)
    ax.set_title("Diagnosis cardinality (number of diseases per patient)")
    ax.set_xlabel("# active labels"); ax.set_ylabel("Patients")
    return _save(fig, path)


def cooccurrence_heatmap(cooc: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 7))
    sns.heatmap(cooc, annot=True, fmt="d", cmap="rocket_r", ax=ax, cbar_kws={"label": "co-diagnoses"})
    ax.set_title("Label co-occurrence (diagonal = total positives)")
    return _save(fig, path)


def missingness_top(missingness: pd.DataFrame, path: Path, top: int = 20) -> Path:
    d = missingness.head(top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(d)), d["missing_pct"], color=ACCENT)
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels([c[:48] for c in d["column"]], fontsize=9)
    ax.set_xlabel("% missing"); ax.set_title(f"Top {top} columns by missingness")
    return _save(fig, path)


def data_type_summary(data_dict: pd.DataFrame, path: Path) -> Path:
    counts = data_dict["role"].value_counts()
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.bar(counts.index, counts.values, color=sns.color_palette(PALETTE, len(counts)))
    for i, v in enumerate(counts.values):
        ax.text(i, v + 0.5, str(v), ha="center")
    ax.set_title("Column roles (descriptive type inference)")
    ax.set_ylabel("# columns"); plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    return _save(fig, path)


def missingness_by_label(X_clean: pd.DataFrame, y: pd.DataFrame, lab_cols: list[str],
                         path: Path) -> Path:
    """Mean missing-indicator rate per disease (workflow availability signal)."""
    ind_cols = [c for c in X_clean.columns if c.endswith("__missing")]
    if not ind_cols:
        fig, ax = plt.subplots(figsize=(8, 4)); ax.text(0.5, 0.5, "no missing indicators", ha="center")
        return _save(fig, path)
    data = []
    for lab in lab_cols:
        mask = y[lab] == 1
        data.append(X_clean.loc[mask, ind_cols].mean().values)
    mat = pd.DataFrame(data, index=lab_cols, columns=[c.replace("__missing", "")[:20] for c in ind_cols])
    fig, ax = plt.subplots(figsize=(min(16, 1 + 0.5 * len(ind_cols)), 5))
    sns.heatmap(mat, cmap="mako", ax=ax, cbar_kws={"label": "mean missing rate"})
    ax.set_title("Missingness by disease (clinical-availability signal)")
    return _save(fig, path)


def demographics(raw_df: pd.DataFrame, age_col: str | None, gender_col: str | None,
                 center_col: str | None, path: Path) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    if age_col:
        age = pd.to_numeric(raw_df[age_col].astype("string").str.replace(",", "."), errors="coerce")
        axes[0].hist(age.dropna(), bins=20, color=PRIMARY)
        axes[0].set_title("Age distribution"); axes[0].set_xlabel("Age (years)")
    if gender_col:
        raw_df[gender_col].value_counts().plot(kind="bar", ax=axes[1], color=ACCENT)
        axes[1].set_title("Gender"); plt.setp(axes[1].get_xticklabels(), rotation=0)
    if center_col:
        raw_df[center_col].value_counts().plot(kind="bar", ax=axes[2], color=PRIMARY)
        axes[2].set_title("Health center"); plt.setp(axes[2].get_xticklabels(), rotation=15)
    return _save(fig, path)


def correlation_matrix(X_clean: pd.DataFrame, path: Path, top: int = 30) -> Path:
    var = X_clean.var(numeric_only=True).sort_values(ascending=False)
    cols = var.head(top).index.tolist()
    corr = X_clean[cols].corr()
    fig, ax = plt.subplots(figsize=(13, 11))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax, square=False,
                xticklabels=[c[:16] for c in cols], yticklabels=[c[:16] for c in cols])
    ax.set_title(f"Feature association matrix (top {top} by variance)")
    plt.setp(ax.get_xticklabels(), fontsize=7, rotation=90)
    plt.setp(ax.get_yticklabels(), fontsize=7)
    return _save(fig, path)


def projection_2d(X_proj: np.ndarray, color_by: pd.Series, title: str, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(9, 7))
    cats = pd.Series(color_by).astype("category")
    sc = ax.scatter(X_proj[:, 0], X_proj[:, 1], c=cats.cat.codes, cmap="viridis", alpha=0.75, s=40)
    ax.set_title(title); ax.set_xlabel("dim 1"); ax.set_ylabel("dim 2")
    handles = [plt.Line2D([], [], marker="o", ls="", color=plt.cm.viridis(i / max(1, len(cats.cat.categories) - 1)),
               label=str(c)) for i, c in enumerate(cats.cat.categories)]
    ax.legend(handles=handles, title=color_by.name, fontsize=9, loc="best")
    return _save(fig, path)


def coinfection_profile(top_combinations: pd.DataFrame, path: Path, top: int = 12) -> Path:
    d = top_combinations.head(top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(d["combination"], d["n_patients"], color=sns.color_palette("flare", len(d)))
    for i, v in enumerate(d["n_patients"]):
        ax.text(v + 0.3, i, str(v), va="center")
    ax.set_title("Top diagnosis combinations (co-infection profile)")
    ax.set_xlabel("Patients")
    return _save(fig, path)


# --------------------------------------------------------------------------- #
# Modeling / evaluation
# --------------------------------------------------------------------------- #
def model_leaderboard(leaderboard: pd.DataFrame, metric: str, path: Path) -> Path:
    d = leaderboard.sort_values(metric, ascending=True)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    colors = [ACCENT if "FULL" in str(t) else (PRIMARY if "PRE_LAB" in str(t) else "#5a189a")
              for t in d.get("track", d.index)]
    labels = d["model_track"] if "model_track" in d else d.index.astype(str)
    ax.barh(labels, d[metric], color=colors)
    for i, v in enumerate(d[metric]):
        ax.text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=10)
    ax.set_title(f"Model leaderboard — {metric}")
    ax.set_xlabel(metric)
    return _save(fig, path)


def per_label_bar(per_label: pd.DataFrame, metric: str, path: Path, title: str) -> Path:
    d = per_label.sort_values(metric, ascending=True)
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.barh(d["label"], d[metric], color=PRIMARY)
    for i, v in enumerate(d[metric]):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center")
    ax.set_xlim(0, 1.05); ax.set_title(title); ax.set_xlabel(metric)
    return _save(fig, path)


def confusion_matrices(per_label: pd.DataFrame, path: Path) -> Path:
    labels = per_label["label"].tolist()
    n = len(labels)
    cols = min(3, n); rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 3.8 * rows))
    axes = np.atleast_1d(axes).ravel()
    for k, (_, r) in enumerate(per_label.iterrows()):
        cm = np.array([[r["tn"], r["fp"]], [r["fn"], r["tp"]]])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[k])
        axes[k].set_title(f"{r['label']}\nrecall={r['recall']:.2f}")
        axes[k].set_xlabel("pred"); axes[k].set_ylabel("true")
        axes[k].set_xticklabels(["0", "1"]); axes[k].set_yticklabels(["0", "1"])
    for k in range(len(per_label), len(axes)):
        axes[k].axis("off")
    fig.suptitle("Per-label confusion matrices", y=1.02)
    return _save(fig, path)


def roc_curves(y_true: pd.DataFrame, y_proba: np.ndarray, labels: list[str], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 7))
    yt = y_true.values
    for j, lab in enumerate(labels):
        if len(np.unique(yt[:, j])) < 2:
            continue
        fpr, tpr, _ = roc_curve(yt[:, j], y_proba[:, j])
        ax.plot(fpr, tpr, label=lab, lw=2)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set_xlabel("FPR"); ax.set_ylabel("TPR"); ax.set_title("Per-label ROC curves")
    ax.legend(fontsize=10)
    return _save(fig, path)


def pr_curves(y_true: pd.DataFrame, y_proba: np.ndarray, labels: list[str], path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 7))
    yt = y_true.values
    for j, lab in enumerate(labels):
        if len(np.unique(yt[:, j])) < 2:
            continue
        prec, rec, _ = precision_recall_curve(yt[:, j], y_proba[:, j])
        ax.plot(rec, prec, label=lab, lw=2)
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title("Per-label PR curves")
    ax.legend(fontsize=10)
    return _save(fig, path)


def threshold_tradeoff(thr_df: pd.DataFrame, path: Path) -> Path:
    """thr_df columns: label, threshold, f1 (best per label)."""
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    ax.scatter(thr_df["threshold"], thr_df["f1"], s=120, color=ACCENT, zorder=3)
    for _, r in thr_df.iterrows():
        ax.annotate(r["label"], (r["threshold"], r["f1"]), fontsize=10,
                    xytext=(5, 5), textcoords="offset points")
    ax.set_xlabel("Optimal threshold"); ax.set_ylabel("Best F1")
    ax.set_title("Per-label optimal threshold vs achieved F1")
    return _save(fig, path)


# --------------------------------------------------------------------------- #
# Calibration / uncertainty
# --------------------------------------------------------------------------- #
def calibration_curves(y_true: pd.DataFrame, y_proba: np.ndarray, labels: list[str],
                       path: Path, reliability_fn=None) -> Path:
    from . import calibration as cal
    fig, ax = plt.subplots(figsize=(8.5, 7))
    yt = y_true.values
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="perfect")
    for j, lab in enumerate(labels):
        if len(np.unique(yt[:, j])) < 2:
            continue
        rc = cal.reliability_curve(yt[:, j], y_proba[:, j], n_bins=8)
        if not rc.empty:
            ax.plot(rc["mean_pred"], rc["frac_pos"], marker="o", label=lab, lw=2)
    ax.set_xlabel("Mean predicted probability"); ax.set_ylabel("Observed frequency")
    ax.set_title("Reliability curves (per label)"); ax.legend(fontsize=10)
    return _save(fig, path)


def uncertainty_distribution(uncertainty: pd.DataFrame, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    axes[0].hist(uncertainty["mean_entropy"], bins=20, color=PRIMARY)
    axes[0].set_title("Predictive entropy distribution"); axes[0].set_xlabel("mean binary entropy")
    order = ["low", "moderate", "high"]
    counts = uncertainty["uncertainty_level"].value_counts().reindex(order).fillna(0)
    axes[1].bar(order, counts.values, color=["#2a9d8f", "#e9c46a", "#e76f51"])
    for i, v in enumerate(counts.values):
        axes[1].text(i, v + 0.5, int(v), ha="center")
    axes[1].set_title("Patient uncertainty categories")
    return _save(fig, path)


# --------------------------------------------------------------------------- #
# Explainability
# --------------------------------------------------------------------------- #
def importance_global(global_imp: pd.DataFrame, path: Path, top: int = 20) -> Path:
    d = global_imp.head(top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh([f[:45] for f in d["feature"]], d["importance_mean"], color=PRIMARY)
    ax.set_title("Global permutation importance (mean over labels)")
    ax.set_xlabel("Δ average precision when permuted")
    return _save(fig, path)


def importance_per_label(per_label_imp: pd.DataFrame, labels: list[str], path: Path,
                         top: int = 6) -> Path:
    labs = [l for l in labels if l in per_label_imp["label"].unique()]
    n = len(labs)
    if n == 0:
        fig, ax = plt.subplots(); ax.text(0.5, 0.5, "no importance", ha="center"); return _save(fig, path)
    cols = min(2, n); rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(8 * cols, 3.5 * rows))
    axes = np.atleast_1d(axes).ravel()
    for k, lab in enumerate(labs):
        d = (per_label_imp[per_label_imp["label"] == lab]
             .sort_values("importance_mean", ascending=False).head(top).iloc[::-1])
        axes[k].barh([f[:32] for f in d["feature"]], d["importance_mean"], color=ACCENT)
        axes[k].set_title(lab, fontsize=13)
        axes[k].tick_params(labelsize=8)
    for k in range(n, len(axes)):
        axes[k].axis("off")
    fig.suptitle("Top features per disease (permutation importance)", y=1.01)
    return _save(fig, path)


def shap_summary(shap_values, X_sample: pd.DataFrame, label: str, path: Path) -> Path:
    import shap
    fig = plt.figure(figsize=(10, 7))
    shap.summary_plot(shap_values, X_sample, show=False, max_display=15)
    plt.title(f"SHAP summary — {label}")
    return _save(fig, path)


def local_explanations(cases: dict[str, pd.DataFrame], path: Path) -> Path:
    n = len(cases)
    fig, axes = plt.subplots(1, n, figsize=(6.5 * n, 5))
    axes = np.atleast_1d(axes).ravel()
    for k, (title, d) in enumerate(cases.items()):
        if d is None or d.empty:
            axes[k].axis("off"); axes[k].set_title(title); continue
        colors = ["#2a9d8f" if c > 0 else "#e76f51" for c in d["contribution"]]
        axes[k].barh([f[:28] for f in d["feature"]][::-1], d["contribution"][::-1], color=colors[::-1])
        axes[k].axvline(0, color="k", lw=0.8)
        axes[k].set_title(title, fontsize=12); axes[k].tick_params(labelsize=8)
    fig.suptitle("Local explanations (logistic surrogate contributions)", y=1.03)
    return _save(fig, path)


# --------------------------------------------------------------------------- #
# Fairness / resource
# --------------------------------------------------------------------------- #
def fairness_recall_gap(gap_df: pd.DataFrame, path: Path) -> Path:
    if gap_df.empty:
        fig, ax = plt.subplots(); ax.text(0.5, 0.5, "no subgroup data", ha="center"); return _save(fig, path)
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot = gap_df.pivot_table(index="label", columns="axis", values="recall_gap")
    pivot.plot(kind="bar", ax=ax, colormap="viridis")
    ax.set_title("Recall gap across subgroups (max - min)"); ax.set_ylabel("recall gap")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    return _save(fig, path)


def resource_priority(resource_df: pd.DataFrame, path: Path) -> Path:
    tiers = resource_df[resource_df["metric"].str.startswith("tier_")].copy()
    tiers["tier"] = tiers["metric"].str.replace("tier_", "").str.replace("_", " ")
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]
    ax.bar(tiers["tier"], tiers["count"], color=colors[:len(tiers)])
    for i, v in enumerate(tiers["count"]):
        ax.text(i, v + 0.3, int(v), ha="center")
    ax.set_title("Triage priority distribution"); ax.set_ylabel("Patients")
    plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    return _save(fig, path)


def policy_tradeoff(tradeoff_df: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    flag_cols = [c for c in tradeoff_df.columns if c.startswith("flagged_")]
    x = np.arange(len(tradeoff_df)); width = 0.8 / max(1, len(flag_cols))
    for i, c in enumerate(flag_cols):
        ax.bar(x + i * width, tradeoff_df[c], width, label=c.replace("flagged_", ""))
    ax.set_xticks(x + width * (len(flag_cols) - 1) / 2)
    ax.set_xticklabels(tradeoff_df["policy"], rotation=10)
    ax.set_title("Threshold-policy resource trade-off (flags per label)")
    ax.set_ylabel("# patients flagged"); ax.legend(fontsize=9)
    return _save(fig, path)
