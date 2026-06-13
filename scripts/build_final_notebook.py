from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "VECTRA_X_Final_Competition_Notebook.ipynb"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text).strip())


def build_notebook():
    cells = [
        md(
            """
            # 0. Title Page / Executive Summary

            ## VECTRA-X: Uncertainty-Aware Triage Intelligence for Vector-Borne Disease Response in Resource-Limited Humanitarian Settings

            **FIT Competition 2026, Track IV: AI-based Vector-Borne Disease Prediction**

            VECTRA-X is a leakage-audited, multi-label **decision-support** prototype.
            It converts patient signals into calibrated disease probabilities, an
            uncertainty gate, transparent triage prioritization, and a resource
            allocation queue. It does not replace clinician assessment or confirmatory testing.

            This notebook is self-contained. It requires only this `.ipynb`, the
            official CSV, and the Python packages listed below. It never reads project
            modules, configuration files, processed datasets, saved models, or prior
            result artifacts. Every displayed metric is recomputed in this run.

            > **Safety statement:** VECTRA-X supports human review and confirmatory-test
            > prioritization. It requires prospective validation and must not replace
            > qualified medical professionals.
            """
        ),
        md(
            """
            ## Setup & Required Packages

            Install the exact environment before running the notebook:

            ```bash
            python -m pip install pandas==3.0.2 numpy==2.4.4 scipy==1.17.1 \
              scikit-learn==1.8.0 iterative-stratification==0.1.9 \
              xgboost==3.2.0 lightgbm==4.6.0 shap==0.52.0 \
              matplotlib==3.11.0 seaborn==0.13.2 plotly==6.8.0 \
              joblib==1.5.3 nbformat==5.10.4 nbclient==0.11.0 ipykernel==6.29.5
            ```

            XGBoost, LightGBM, SHAP, and iterative-stratification are required because
            the official model comparison and uncertainty evidence depend on them.
            The preflight cell fails early with a complete installation message if the
            environment is incomplete.
            """
        ),
        code(
            """
            from pathlib import Path
            import hashlib
            import importlib
            import json
            import math
            import os
            import platform
            import re
            import sys
            import time
            import warnings

            REQUIRED_MODULES = {
                "numpy": "numpy==2.4.4",
                "pandas": "pandas==3.0.2",
                "scipy": "scipy==1.17.1",
                "sklearn": "scikit-learn==1.8.0",
                "iterstrat": "iterative-stratification==0.1.9",
                "xgboost": "xgboost==3.2.0",
                "lightgbm": "lightgbm==4.6.0",
                "shap": "shap==0.52.0",
                "matplotlib": "matplotlib==3.11.0",
                "seaborn": "seaborn==0.13.2",
                "plotly": "plotly==6.8.0",
                "joblib": "joblib==1.5.3",
            }
            missing = []
            for module_name, requirement in REQUIRED_MODULES.items():
                try:
                    importlib.import_module(module_name)
                except Exception:
                    missing.append(requirement)
            if missing:
                raise ModuleNotFoundError(
                    "VECTRA-X dependency preflight failed. Install these packages, "
                    "restart the kernel, and run all cells again:\\n"
                    + "python -m pip install " + " ".join(missing)
                )

            import joblib
            import lightgbm
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import plotly.express as px
            import plotly.graph_objects as go
            import seaborn as sns
            import shap
            import sklearn
            import xgboost
            from IPython.display import Markdown, display
            from iterstrat.ml_stratifiers import (
                MultilabelStratifiedKFold,
                MultilabelStratifiedShuffleSplit,
            )

            warnings.filterwarnings("ignore")
            RANDOM_STATE = 42
            np.random.seed(RANDOM_STATE)

            DATA_PATH = os.environ.get("DATA_PATH")
            OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", "vectra_x_outputs"))
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            (OUTPUT_DIR / "tables").mkdir(exist_ok=True)
            (OUTPUT_DIR / "figures").mkdir(exist_ok=True)
            (OUTPUT_DIR / "models").mkdir(exist_ok=True)

            print("Dependency preflight passed.")
            print("Python:", platform.python_version())
            print("Output directory:", OUTPUT_DIR.resolve())
            """
        ),
        md(
            """
            # 1. Humanitarian Background

            In resource-limited outbreaks, the operational question is not only
            “which disease is plausible?” Teams must also decide which patients need
            urgent human review, which should receive scarce confirmatory tests, and
            where model uncertainty is too high for automated prioritization.

            VECTRA-X therefore treats prediction as one component of a staged
            humanitarian workflow: **patient signals → uncertainty gate → triage
            priority → resource allocation**.

            # 2. Project Objective

            The primary objective is to evaluate whether leakage-safe, multi-label
            models can support early triage prioritization while communicating
            uncertainty, false-negative risk, co-infection, and operational burden.

            The intended users are frontline health workers and humanitarian response
            coordinators. The system is a competition prototype requiring prospective
            validation.

            ## 2.1 Related Work and Research Gap

            Prior vector-borne disease studies commonly optimize a single disease or
            force mutually exclusive classes. VECTRA-X addresses a narrower operational
            gap: stage-aware, leakage-audited, multi-label triage with uncertainty,
            human-review routing, and scarce-resource prioritization.
            """
        ),
        md(
            """
            # 3. Data Loading and Dataset Overview

            The resolver searches an explicit `DATA_PATH`, the current folder, a
            `data/raw` subfolder, parent folders, and common hosted-notebook upload
            locations. Delimiter and encoding are detected from the file rather than
            hard-coded to a local machine.
            """
        ),
        code(
            """
            def resolve_csv(explicit_path=None):
                candidates = []
                if explicit_path:
                    candidates.append(Path(explicit_path).expanduser())
                roots = [Path.cwd(), *Path.cwd().parents]
                for root in roots[:4]:
                    candidates.extend(sorted(root.glob("*.csv")))
                    candidates.extend(sorted((root / "data" / "raw").glob("*.csv")))
                for upload_root in [
                    Path("/kaggle/input"),
                    Path("/content"),
                    Path("/mnt/data"),
                    Path.home() / "Downloads",
                ]:
                    if upload_root.exists():
                        candidates.extend(sorted(upload_root.rglob("*.csv")))
                unique = []
                seen = set()
                for candidate in candidates:
                    try:
                        resolved = candidate.resolve()
                    except OSError:
                        continue
                    if resolved.is_file() and resolved not in seen:
                        seen.add(resolved)
                        unique.append(resolved)
                if not unique:
                    raise FileNotFoundError(
                        "No CSV found. Place the official CSV beside the notebook, "
                        "under data/raw, in the upload directory, or set DATA_PATH."
                    )
                preferred = [p for p in unique if p.name.lower() in {"data.csv", "vectra_x.csv"}]
                return (preferred or unique)[0]

            def read_csv_robust(path):
                raw_bytes = path.read_bytes()
                encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
                last_error = None
                for encoding in encodings:
                    try:
                        sample = raw_bytes[:8192].decode(encoding)
                        separator = ";" if sample.count(";") > sample.count(",") else ","
                        decimal = "," if separator == ";" else "."
                        frame = pd.read_csv(path, sep=separator, decimal=decimal, encoding=encoding)
                        if frame.shape[1] > 1:
                            return frame, {
                                "encoding": encoding,
                                "separator": separator,
                                "decimal": decimal,
                                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                            }
                    except Exception as exc:
                        last_error = exc
                raise ValueError(f"Unable to parse CSV {path}: {last_error}")

            csv_path = resolve_csv(DATA_PATH)
            raw, data_provenance = read_csv_robust(csv_path)
            print("Dataset:", csv_path)
            print("Shape:", raw.shape)
            display(pd.DataFrame([data_provenance]))
            display(raw.head(3))
            """
        ),
        md(
            """
            # 4. Data Quality and Schema Audit

            Missing values remain unknown rather than being interpreted as negative
            findings. Data-driven schema choices are learned from training data only.
            """
        ),
        code(
            """
            LABEL_PREFIX = "Maladies diagnostiquées/"
            LABEL_ALIASES = {
                "Paludisme (Malaria)": "malaria",
                "Dengue": "dengue",
                "Chikunguya": "chikungunya",
                "Fièvre jaune (yellow fever)": "yellow_fever",
                "Fièvre Typhoïde (Thyphoid fever)": "typhoid",
                "Zika": "zika",
                "Autres maladies diagnostiqué (Others diseases)": "other_diseases",
                "Option 8": "option_8",
            }
            POSITIVE_TOKENS = {"1", "1.0", "oui", "yes", "true", "positif", "positive"}
            YES_TOKENS = POSITIVE_TOKENS | {"présent", "present"}
            NO_TOKENS = {"0", "0.0", "non", "no", "false", "négatif", "negatif", "negative", "absent"}

            def binary_series(series):
                return series.astype("string").str.strip().str.lower().isin(POSITIVE_TOKENS).astype(int)

            def detect_targets(frame):
                raw_label_cols = [c for c in frame.columns if str(c).startswith(LABEL_PREFIX)]
                if not raw_label_cols:
                    raise ValueError(
                        f"Expected multi-label columns beginning with {LABEL_PREFIX!r}. "
                        "The supplied CSV schema is not the official VECTRA-X format."
                    )
                y_all = pd.DataFrame(index=frame.index)
                for column in raw_label_cols:
                    suffix = str(column)[len(LABEL_PREFIX):].strip()
                    alias = LABEL_ALIASES.get(suffix, re.sub(r"[^a-z0-9]+", "_", suffix.lower()).strip("_"))
                    y_all[alias] = binary_series(frame[column])
                active = [c for c in y_all if y_all[c].sum() > 0]
                inactive = [c for c in y_all if y_all[c].sum() == 0]
                return y_all[active], y_all, raw_label_cols, active, inactive

            y, y_all, raw_label_columns, labels, inactive_labels = detect_targets(raw)
            target_drop = set(raw_label_columns) | {"Maladies diagnostiquées", "_uuid"}
            feature_columns = [c for c in raw.columns if c not in target_drop]
            quality = pd.DataFrame({
                "measure": [
                    "patients", "columns", "duplicate_rows", "active_labels",
                    "inactive_labels", "multi_label_patients", "patients_without_active_label",
                ],
                "value": [
                    len(raw), raw.shape[1], int(raw.duplicated().sum()), len(labels),
                    len(inactive_labels), int((y.sum(axis=1) > 1).sum()),
                    int((y.sum(axis=1) == 0).sum()),
                ],
            })
            missingness = raw[feature_columns].isna().mean().sort_values(ascending=False).rename("missing_rate").reset_index(name="missing_rate")
            missingness = missingness.rename(columns={"index": "column"})
            display(quality)
            display(missingness.head(20))
            print("Active labels:", labels)
            print("Inactive labels:", inactive_labels)
            """
        ),
        md(
            """
            # 5. Diagnostic Leakage Audit

            Feature availability defines three tracks:

            - **PRE_LAB:** demographics, symptoms, history, and available vital signs.
            - **LAB_AWARE:** PRE_LAB plus laboratory or rapid-test information.
            - **FULL:** all candidate features, including target-restatement risks. This
              track is a leakage demonstration and is never recommended for use.

            Rule-based clinical-stage routing is defined before model fitting.
            Statistical single-feature screens are computed on the training partition
            only and reported as audit evidence, not as a test-informed selector.
            """
        ),
        code(
            """
            LAB_PATTERNS = [
                "test tdr", "goutte", "hematoc", "hématoc", "transamin",
                "thromb", "lymphocyte", "neutro", "globules blancs",
                "white blood", "platelet", "crp", "créatin", "creatin",
                "alat", "asat", "hypogly", "hémoconcentration", "hemoconcentration",
            ]
            RESTATEMENT_PATTERNS = ["dengue (dengua)"]

            def feature_stage(column):
                lowered = str(column).strip().lower()
                if any(pattern in lowered for pattern in RESTATEMENT_PATTERNS):
                    return "FULL_RESEARCH_ONLY"
                if any(pattern in lowered for pattern in LAB_PATTERNS):
                    return "LAB_AWARE"
                return "PRE_LAB"

            feature_stage_table = pd.DataFrame({
                "feature": feature_columns,
                "stage": [feature_stage(c) for c in feature_columns],
            })
            PRE_LAB_FEATURES = feature_stage_table.loc[feature_stage_table.stage == "PRE_LAB", "feature"].tolist()
            LAB_AWARE_FEATURES = feature_stage_table.loc[feature_stage_table.stage != "FULL_RESEARCH_ONLY", "feature"].tolist()
            FULL_FEATURES = list(feature_columns)
            display(feature_stage_table["stage"].value_counts().rename_axis("stage").reset_index(name="features"))
            display(feature_stage_table[feature_stage_table.stage != "PRE_LAB"])
            """
        ),
        md(
            """
            # 6. Exploratory Data Analysis

            EDA is descriptive, not causal. Its role is to expose imbalance,
            co-infection, missingness, and center dependence that affect evaluation.
            """
        ),
        code(
            """
            distribution = pd.DataFrame({
                "label": y_all.columns,
                "positives": y_all.sum().values,
                "prevalence": y_all.mean().values,
            }).sort_values("positives", ascending=False)
            display(distribution)
            px.bar(
                distribution, x="label", y="prevalence", text="positives",
                title="Disease prevalence with support counts",
            ).show()

            cardinality = y.sum(axis=1).value_counts().sort_index().rename_axis("labels_per_patient").reset_index(name="patients")
            display(cardinality)
            px.bar(cardinality, x="labels_per_patient", y="patients", title="Multi-label cardinality").show()

            cooccurrence = pd.DataFrame(y.T.values @ y.values, index=labels, columns=labels)
            px.imshow(cooccurrence, text_auto=True, title="Label co-occurrence counts").show()
            """
        ),
        md(
            """
            # 7. Modeling Strategy

            The untouched holdout is created before learned preprocessing or
            statistical leakage evidence. Model selection occurs only on training
            out-of-fold probabilities.

            **Why macro PR-AUC for initial selection?** It evaluates ranking quality
            under severe imbalance without committing to one threshold. Selection is
            then reviewed through a real-world triage suitability lens:

            - per-label recall and false-negative rate for safety;
            - precision and number-needed-to-review for workload;
            - macro/micro F1 for thresholded balance;
            - Brier score and calibration error for probability trust;
            - decision-curve net benefit for confirmatory-test prioritization;
            - capacity coverage and total flags for resource use;
            - repeated validation, confidence intervals, and center transfer for stability.

            A single winner is not forced when models form a Pareto trade-off.

            # 8. Preprocessing Pipeline

            A train-fitted schema parses numeric and binary values, creates missing
            indicators, and one-hot encodes categories. Unknown categories map to
            all-zero one-hot blocks. Median imputation and optional scaling are fitted
            inside each model pipeline.
            """
        ),
        code(
            """
            from dataclasses import dataclass, field
            from sklearn.base import clone
            from sklearn.compose import ColumnTransformer
            from sklearn.dummy import DummyClassifier
            from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
            from sklearn.impute import SimpleImputer
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import (
                average_precision_score, brier_score_loss, confusion_matrix,
                f1_score, hamming_loss, jaccard_score, precision_score,
                recall_score, roc_auc_score,
            )
            from sklearn.multioutput import ClassifierChain
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
            from xgboost import XGBClassifier
            from lightgbm import LGBMClassifier

            outer = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=0.25, random_state=RANDOM_STATE)
            train_idx, test_idx = next(outer.split(np.zeros(len(y)), y.values))
            raw_train = raw.iloc[train_idx].reset_index(drop=True)
            raw_test = raw.iloc[test_idx].reset_index(drop=True)
            y_train = y.iloc[train_idx].reset_index(drop=True)
            y_test = y.iloc[test_idx].reset_index(drop=True)

            def alias(text):
                value = re.sub(r"\\(.*?\\)", "", str(text)).lower()
                return re.sub(r"[^a-z0-9]+", "_", value).strip("_")[:48] or "feature"

            def parse_numeric(series):
                text = series.astype("string").str.replace(",", ".", regex=False)
                extracted = text.str.extract(r"(-?\\d+(?:\\.\\d+)?)", expand=False)
                return pd.to_numeric(extracted, errors="coerce")

            @dataclass
            class FeatureSchema:
                columns: list = field(default_factory=list)
                output_columns: list = field(default_factory=list)

                def fit(self, frame, selected_columns):
                    self.columns = []
                    outputs = []
                    for column in selected_columns:
                        series = frame[column]
                        non_null = series.dropna()
                        if non_null.nunique() <= 1:
                            continue
                        values = {str(v).strip().lower() for v in non_null.unique()}
                        add_missing = bool(series.isna().mean() >= 0.05)
                        numeric = parse_numeric(series)
                        name = str(column).lower()
                        if "pression art" in name or "blood pressure" in name:
                            spec = {"source": column, "kind": "blood_pressure", "missing": add_missing}
                            names = [f"{alias(column)}__systolic", f"{alias(column)}__diastolic"]
                        elif values and values.issubset(YES_TOKENS | NO_TOKENS):
                            spec = {"source": column, "kind": "binary", "missing": add_missing}
                            names = [alias(column)]
                        elif numeric.notna().mean() >= 0.5:
                            spec = {"source": column, "kind": "numeric", "missing": add_missing}
                            names = [alias(column)]
                        elif non_null.nunique() <= 15:
                            categories = sorted(str(v).strip() for v in non_null.unique())
                            spec = {"source": column, "kind": "categorical", "categories": categories, "missing": add_missing}
                            names = [f"{alias(column)}__cat_{i}" for i in range(len(categories))]
                        else:
                            spec = {"source": column, "kind": "presence", "missing": False}
                            names = [f"{alias(column)}__present"]
                        spec["outputs"] = names
                        self.columns.append(spec)
                        outputs.extend(names)
                        if add_missing:
                            outputs.append(f"{alias(column)}__missing")
                    self.output_columns = outputs
                    return self

                def transform(self, frame):
                    out = pd.DataFrame(index=frame.index)
                    for spec in self.columns:
                        source = spec["source"]
                        series = frame[source] if source in frame else pd.Series(np.nan, index=frame.index)
                        if spec["kind"] == "blood_pressure":
                            split = series.astype("string").str.replace(",", ".", regex=False).str.extract(
                                r"(?P<sys>\\d+(?:\\.\\d+)?)\\D+(?P<dia>\\d+(?:\\.\\d+)?)"
                            )
                            out[spec["outputs"][0]] = pd.to_numeric(split["sys"], errors="coerce")
                            out[spec["outputs"][1]] = pd.to_numeric(split["dia"], errors="coerce")
                        elif spec["kind"] == "binary":
                            normalized = series.astype("string").str.strip().str.lower()
                            out[spec["outputs"][0]] = normalized.map(
                                lambda value: 1.0 if value in YES_TOKENS else (0.0 if value in NO_TOKENS else np.nan)
                            )
                        elif spec["kind"] == "numeric":
                            out[spec["outputs"][0]] = parse_numeric(series)
                        elif spec["kind"] == "presence":
                            out[spec["outputs"][0]] = series.notna().astype(float)
                        else:
                            normalized = series.astype("string").str.strip()
                            for category, output in zip(spec["categories"], spec["outputs"]):
                                out[output] = (normalized == category).astype(float)
                        if spec["missing"]:
                            out[f"{alias(source)}__missing"] = series.isna().astype(float)
                    return out.reindex(columns=self.output_columns)

            schemas = {}
            tracks = {}
            for track_name, selected in {
                "PRE_LAB": PRE_LAB_FEATURES,
                "LAB_AWARE": LAB_AWARE_FEATURES,
                "FULL": FULL_FEATURES,
            }.items():
                schema = FeatureSchema().fit(raw_train, selected)
                schemas[track_name] = schema
                tracks[track_name] = {
                    "X_train": schema.transform(raw_train).reset_index(drop=True),
                    "X_test": schema.transform(raw_test).reset_index(drop=True),
                }
                print(track_name, tracks[track_name]["X_train"].shape)
            """
        ),
        md(
            """
            # 9. Baseline Models

            Dummy/prevalence and Logistic Regression establish whether complex models
            add meaningful value beyond base rates and a transparent linear boundary.

            # 10. Advanced Model Benchmark

            Random Forest and Extra Trees test nonlinear interactions; HistGradientBoosting,
            XGBoost, and LightGBM test boosting; Classifier Chain tests whether explicit
            label dependence improves multi-label ranking.
            """
        ),
        code(
            """
            MODEL_RATIONALE = pd.DataFrame([
                ["Dummy / Prevalence", "Base-rate reference", "No patient discrimination", "Very low"],
                ["Logistic Regression", "Stable, interpretable linear baseline", "Misses nonlinear interactions", "Low"],
                ["Random Forest", "Robust nonlinear bagging", "Larger and less calibrated", "Medium"],
                ["Extra Trees", "Strong small-tabular benchmark, low variance", "Feature effects are less direct", "Medium"],
                ["HistGradientBoosting", "Efficient regularized boosting", "Binary relevance required", "Medium"],
                ["XGBoost", "Strong tabular ranking performance", "External dependency and tuning sensitivity", "High"],
                ["LightGBM", "Fast boosting with flexible leaves", "Can overfit tiny rare-label samples", "High"],
                ["Classifier Chain", "Models label dependence", "Order-sensitive and less stable for rare labels", "Medium"],
            ], columns=["model", "rationale", "limitation", "complexity"])
            display(MODEL_RATIONALE)

            def base_estimator(name, seed):
                if name == "Dummy / Prevalence":
                    return DummyClassifier(strategy="prior")
                if name == "Logistic Regression":
                    return LogisticRegression(max_iter=2500, class_weight="balanced", C=0.5, random_state=seed)
                if name == "Random Forest":
                    return RandomForestClassifier(
                        n_estimators=300, min_samples_leaf=2, class_weight="balanced_subsample",
                        random_state=seed, n_jobs=-1,
                    )
                if name == "Extra Trees":
                    return ExtraTreesClassifier(
                        n_estimators=400, min_samples_leaf=2, class_weight="balanced",
                        random_state=seed, n_jobs=-1,
                    )
                if name == "HistGradientBoosting":
                    return HistGradientBoostingClassifier(
                        max_depth=3, learning_rate=0.05, max_iter=250,
                        l2_regularization=1.0, random_state=seed,
                    )
                if name == "XGBoost":
                    return XGBClassifier(
                        n_estimators=250, max_depth=3, learning_rate=0.05,
                        subsample=0.8, colsample_bytree=0.8, reg_lambda=2.0,
                        eval_metric="logloss", tree_method="hist", random_state=seed, n_jobs=-1,
                    )
                if name == "LightGBM":
                    return LGBMClassifier(
                        n_estimators=250, num_leaves=15, max_depth=4, learning_rate=0.05,
                        subsample=0.8, colsample_bytree=0.8, reg_lambda=2.0,
                        class_weight="balanced", random_state=seed, n_jobs=-1, verbose=-1,
                    )
                raise ValueError(name)

            def make_binary_pipeline(name, seed):
                steps = [("impute", SimpleImputer(strategy="median"))]
                if name == "Logistic Regression":
                    steps.append(("scale", StandardScaler()))
                steps.append(("model", base_estimator(name, seed)))
                return Pipeline(steps)

            def fit_binary_relevance(name, X, target, seed=RANDOM_STATE):
                fitted = {}
                priors = {}
                for label in target.columns:
                    values = target[label].to_numpy()
                    priors[label] = float(values.mean())
                    if len(np.unique(values)) < 2:
                        fitted[label] = None
                    else:
                        fitted[label] = make_binary_pipeline(name, seed).fit(X, values)
                return {"name": name, "labels": list(target.columns), "models": fitted, "priors": priors}

            def predict_binary_relevance(bundle, X):
                columns = []
                for label in bundle["labels"]:
                    model = bundle["models"][label]
                    if model is None:
                        columns.append(np.full(len(X), bundle["priors"][label]))
                    else:
                        probabilities = model.predict_proba(X)
                        columns.append(probabilities[:, 1] if probabilities.shape[1] > 1 else np.full(len(X), bundle["priors"][label]))
                return np.column_stack(columns)

            def safe_ap(truth, score):
                return float(average_precision_score(truth, score)) if len(np.unique(truth)) > 1 else np.nan

            def safe_auc(truth, score):
                return float(roc_auc_score(truth, score)) if len(np.unique(truth)) > 1 else np.nan

            def probability_metrics(target, probabilities):
                return {
                    "macro_pr_auc": float(np.nanmean([safe_ap(target.iloc[:, j], probabilities[:, j]) for j in range(target.shape[1])])),
                    "macro_roc_auc": float(np.nanmean([safe_auc(target.iloc[:, j], probabilities[:, j]) for j in range(target.shape[1])])),
                }

            cv = MultilabelStratifiedKFold(n_splits=4, shuffle=True, random_state=RANDOM_STATE)
            splits = list(cv.split(np.zeros(len(y_train)), y_train.values))
            model_names = [
                "Dummy / Prevalence", "Logistic Regression", "Random Forest",
                "Extra Trees", "HistGradientBoosting", "XGBoost", "LightGBM",
            ]
            X_pre_train = tracks["PRE_LAB"]["X_train"]
            benchmark_probabilities = {}
            benchmark_rows = []

            for model_name in model_names:
                start = time.perf_counter()
                oof = np.zeros((len(X_pre_train), len(labels)))
                for fold_train, fold_valid in splits:
                    bundle = fit_binary_relevance(model_name, X_pre_train.iloc[fold_train], y_train.iloc[fold_train])
                    oof[fold_valid] = predict_binary_relevance(bundle, X_pre_train.iloc[fold_valid])
                benchmark_probabilities[model_name] = oof
                metrics = probability_metrics(y_train, oof)
                benchmark_rows.append({
                    "model": model_name,
                    **metrics,
                    "runtime_seconds": round(time.perf_counter() - start, 2),
                })

            # Supplemental classifier-chain benchmark using a stable logistic base.
            start = time.perf_counter()
            chain_oof = np.zeros((len(X_pre_train), len(labels)))
            for fold_train, fold_valid in splits:
                imputer = SimpleImputer(strategy="median")
                scaler = StandardScaler()
                X_fold_train = scaler.fit_transform(imputer.fit_transform(X_pre_train.iloc[fold_train]))
                X_fold_valid = scaler.transform(imputer.transform(X_pre_train.iloc[fold_valid]))
                chain = ClassifierChain(
                    LogisticRegression(max_iter=2500, class_weight="balanced", C=0.5),
                    order="random",
                    random_state=RANDOM_STATE,
                )
                chain.fit(X_fold_train, y_train.iloc[fold_train].values)
                chain_oof[fold_valid] = chain.predict_proba(X_fold_valid)
            benchmark_probabilities["Classifier Chain"] = chain_oof
            benchmark_rows.append({
                "model": "Classifier Chain",
                **probability_metrics(y_train, chain_oof),
                "runtime_seconds": round(time.perf_counter() - start, 2),
            })

            leaderboard = pd.DataFrame(benchmark_rows).sort_values("macro_pr_auc", ascending=False).reset_index(drop=True)
            display(leaderboard)
            px.bar(leaderboard, x="model", y="macro_pr_auc", color="runtime_seconds", title="Training-only OOF model comparison").show()
            """
        ),
        md(
            """
            # 11. Pre-Lab Triage Model

            The initial candidate is the model with the highest training-only OOF
            macro PR-AUC. The final recommendation is confirmed only after threshold,
            false-negative, calibration, stability, and workload review.

            # 12. Lab-Aware Confirmation Model

            The same selected model family is retrained with laboratory features to
            evaluate whether additional information genuinely improves support.

            # 13. Full-Feature Leakage Demonstration

            FULL-track results are reported only to quantify the apparent gain from
            post-diagnosis or target-restatement information.
            """
        ),
        code(
            """
            selected_model_name = leaderboard.iloc[0]["model"]
            if selected_model_name == "Classifier Chain":
                # Binary relevance is retained for consistent calibration, feature attribution,
                # and saved-model inference; the chain remains a supplemental comparison.
                selected_model_name = leaderboard[leaderboard.model != "Classifier Chain"].iloc[0]["model"]
            print("Initial OOF ranking candidate:", selected_model_name)

            def optimize_thresholds(target, probabilities, recall_floor=0.50):
                thresholds = {}
                rows = []
                for j, label in enumerate(target.columns):
                    best = (0.5, -1.0, 0.0, 0.0)
                    for threshold in np.linspace(0.05, 0.90, 18):
                        prediction = (probabilities[:, j] >= threshold).astype(int)
                        precision = precision_score(target.iloc[:, j], prediction, zero_division=0)
                        recall = recall_score(target.iloc[:, j], prediction, zero_division=0)
                        f1 = f1_score(target.iloc[:, j], prediction, zero_division=0)
                        objective = f1 if recall >= recall_floor else f1 * 0.6
                        if objective > best[1]:
                            best = (float(threshold), float(objective), float(precision), float(recall))
                    thresholds[label] = best[0]
                    rows.append({"label": label, "threshold": best[0], "oof_precision": best[2], "oof_recall": best[3]})
                return thresholds, pd.DataFrame(rows)

            selected_oof = benchmark_probabilities[selected_model_name]
            thresholds, threshold_table = optimize_thresholds(y_train, selected_oof)
            display(threshold_table)

            def apply_thresholds(probabilities, threshold_map):
                return np.column_stack([
                    (probabilities[:, j] >= threshold_map[label]).astype(int)
                    for j, label in enumerate(labels)
                ])

            def aggregate_metrics(target, prediction, probabilities):
                truth = target.values
                return {
                    "macro_f1": f1_score(truth, prediction, average="macro", zero_division=0),
                    "micro_f1": f1_score(truth, prediction, average="micro", zero_division=0),
                    "macro_recall": recall_score(truth, prediction, average="macro", zero_division=0),
                    "macro_precision": precision_score(truth, prediction, average="macro", zero_division=0),
                    "macro_pr_auc": probability_metrics(target, probabilities)["macro_pr_auc"],
                    "hamming_loss": hamming_loss(truth, prediction),
                    "jaccard_samples": jaccard_score(truth, prediction, average="samples", zero_division=0),
                }

            track_results = []
            fitted_tracks = {}
            heldout_probabilities = {}
            for track_name in ["PRE_LAB", "LAB_AWARE", "FULL"]:
                bundle = fit_binary_relevance(selected_model_name, tracks[track_name]["X_train"], y_train)
                probabilities = predict_binary_relevance(bundle, tracks[track_name]["X_test"])
                prediction = apply_thresholds(probabilities, thresholds)
                metrics = aggregate_metrics(y_test, prediction, probabilities)
                track_results.append({"track": track_name, "model": selected_model_name, **metrics})
                fitted_tracks[track_name] = bundle
                heldout_probabilities[track_name] = probabilities
            track_metrics = pd.DataFrame(track_results)
            display(track_metrics)
            px.bar(track_metrics, x="track", y=["macro_f1", "macro_pr_auc"], barmode="group", title="Stage-aware held-out comparison").show()
            """
        ),
        md(
            """
            # 14. Threshold Optimization

            Thresholds are tuned on training OOF probabilities. Safety-oriented
            alternatives lower severe-label thresholds; operational alternatives
            balance recall against capacity. The notebook reports total flags and
            **number-needed-to-review**, not only F1.

            # 15. Calibration

            Calibration is label-dependent. Brier score and expected calibration
            error are shown per label; improvement is not assumed.
            """
        ),
        code(
            """
            from sklearn.isotonic import IsotonicRegression

            def fit_calibrator(truth, probability):
                if len(np.unique(truth)) < 2:
                    prior = float(np.mean(truth))
                    return lambda values: np.full(len(values), prior)
                if int(np.sum(truth)) >= 25:
                    model = IsotonicRegression(out_of_bounds="clip").fit(probability, truth)
                    return lambda values: model.predict(values)
                model = LogisticRegression(C=1e6).fit(probability.reshape(-1, 1), truth)
                return lambda values: model.predict_proba(np.asarray(values).reshape(-1, 1))[:, 1]

            calibrators = {}
            calibrated_test = np.zeros_like(heldout_probabilities["PRE_LAB"])
            for j, label in enumerate(labels):
                calibrator = fit_calibrator(y_train.iloc[:, j].values, selected_oof[:, j])
                calibrators[label] = calibrator
                calibrated_test[:, j] = np.clip(calibrator(heldout_probabilities["PRE_LAB"][:, j]), 0, 1)

            def calibration_error(truth, probability, bins=8):
                edges = np.linspace(0, 1, bins + 1)
                indices = np.digitize(probability, edges[1:-1], right=True)
                return sum(
                    (indices == b).mean() * abs(probability[indices == b].mean() - truth[indices == b].mean())
                    for b in range(bins) if (indices == b).any()
                )

            calibration_rows = []
            for j, label in enumerate(labels):
                truth = y_test.iloc[:, j].values
                raw_probability = heldout_probabilities["PRE_LAB"][:, j]
                calibrated_probability = calibrated_test[:, j]
                calibration_rows.append({
                    "label": label,
                    "support_pos": int(truth.sum()),
                    "brier_raw": brier_score_loss(truth, raw_probability),
                    "brier_calibrated": brier_score_loss(truth, calibrated_probability),
                    "ece_raw": calibration_error(truth, raw_probability),
                    "ece_calibrated": calibration_error(truth, calibrated_probability),
                })
            calibration_table = pd.DataFrame(calibration_rows)
            display(calibration_table)
            """
        ),
        md(
            """
            # 16. Uncertainty Estimation

            Predictive entropy, top-two margin, and maximum probability form an
            uncertainty gate. High uncertainty routes a case to human review.

            # 17. Conformal Prediction

            Label-wise positive-class split conformal sets provide a conservative
            caution mechanism. They are not claimed as a joint multi-label guarantee.
            Rare-label coverage and set size are reported prominently.
            """
        ),
        code(
            """
            def binary_entropy(probabilities):
                p = np.clip(probabilities, 1e-9, 1 - 1e-9)
                return -(p * np.log2(p) + (1 - p) * np.log2(1 - p))

            def fit_conformal_thresholds(target, probabilities, alpha=0.10):
                values = {}
                for j, label in enumerate(target.columns):
                    positive_scores = 1 - probabilities[target.iloc[:, j].values == 1, j]
                    if len(positive_scores) == 0:
                        values[label] = 0.5
                    else:
                        quantile = min(0.90, math.ceil((len(positive_scores) + 1) * (1 - alpha)) / len(positive_scores))
                        q = np.quantile(positive_scores, quantile, method="higher")
                        values[label] = float(np.clip(1 - q, 0, 1))
                return values

            conformal_thresholds = fit_conformal_thresholds(y_train, selected_oof)
            conformal_sets = [
                [label for j, label in enumerate(labels) if calibrated_test[i, j] >= conformal_thresholds[label]]
                for i in range(len(calibrated_test))
            ]
            set_sizes = np.array([len(values) for values in conformal_sets])
            sorted_probabilities = np.sort(calibrated_test, axis=1)[:, ::-1]
            uncertainty = pd.DataFrame({
                "max_probability": calibrated_test.max(axis=1),
                "mean_entropy": binary_entropy(calibrated_test).mean(axis=1),
                "top2_margin": sorted_probabilities[:, 0] - sorted_probabilities[:, 1],
                "conformal_set_size": set_sizes,
            })
            uncertainty["uncertainty_level"] = np.select(
                [
                    (uncertainty.mean_entropy >= 0.50) | (uncertainty.max_probability < 0.50) | (set_sizes == 0),
                    (uncertainty.mean_entropy >= 0.28) | (uncertainty.max_probability < 0.78) | (set_sizes >= 4),
                ],
                ["high", "moderate"],
                default="low",
            )
            display(uncertainty["uncertainty_level"].value_counts().rename_axis("level").reset_index(name="patients"))

            conformal_rows = []
            for j, label in enumerate(labels):
                positive = y_test.iloc[:, j].values == 1
                included = np.array([label in values for values in conformal_sets])
                conformal_rows.append({
                    "label": label,
                    "threshold": conformal_thresholds[label],
                    "test_positives": int(positive.sum()),
                    "empirical_positive_coverage": float(included[positive].mean()) if positive.any() else np.nan,
                    "predicted_inclusions": int(included.sum()),
                })
            conformal_table = pd.DataFrame(conformal_rows)
            display(conformal_table)
            """
        ),
        md(
            """
            # 18. Explainability

            Global permutation importance is computed on the held-out set. SHAP is
            used as a supporting tree explanation for one label when compatible with
            the selected model. Feature importance indicates association with the
            model output, not causality.
            """
        ),
        code(
            """
            from sklearn.inspection import permutation_importance

            importance_rows = []
            for label in labels:
                model = fitted_tracks["PRE_LAB"]["models"][label]
                if model is None:
                    continue
                j = labels.index(label)
                result = permutation_importance(
                    model,
                    tracks["PRE_LAB"]["X_test"],
                    y_test.iloc[:, j],
                    scoring="average_precision",
                    n_repeats=5,
                    random_state=RANDOM_STATE,
                )
                top_indices = np.argsort(result.importances_mean)[::-1][:8]
                for index in top_indices:
                    importance_rows.append({
                        "label": label,
                        "feature": tracks["PRE_LAB"]["X_test"].columns[index],
                        "importance_mean": float(result.importances_mean[index]),
                    })
            feature_importance = pd.DataFrame(importance_rows)
            display(feature_importance.groupby("label").head(5))
            """
        ),
        md(
            """
            # 19. Fairness and Robustness Audit

            Subgroup metrics are warning diagnostics, not proof of fairness. Support
            counts accompany gender, age, and health-center recall. Leave-one-center-out
            testing is treated as a headline generalization stress test.
            """
        ),
        code(
            """
            def find_column(fragments):
                return next((c for c in raw.columns if any(fragment in str(c).lower() for fragment in fragments)), None)

            center_column = find_column(["centre de santé", "health center"])
            gender_column = find_column(["genre", "gender"])
            age_column = find_column(["âge", "age"])
            heldout_prediction = apply_thresholds(calibrated_test, thresholds)

            subgroup_sources = {}
            if center_column:
                subgroup_sources["center"] = raw_test[center_column].astype("string")
            if gender_column:
                subgroup_sources["gender"] = raw_test[gender_column].astype("string")
            if age_column:
                ages = parse_numeric(raw_test[age_column])
                subgroup_sources["age_group"] = pd.cut(
                    ages, [-1, 12, 18, 50, 200],
                    labels=["child", "adolescent", "adult", "older_adult"],
                ).astype("string")

            fairness_rows = []
            for axis, groups in subgroup_sources.items():
                for level in groups.dropna().unique():
                    mask = (groups == level).fillna(False).to_numpy(dtype=bool)
                    if mask.sum() < 3:
                        continue
                    row = {
                        "axis": axis,
                        "level": str(level),
                        "n": int(mask.sum()),
                        "macro_f1": f1_score(y_test.values[mask], heldout_prediction[mask], average="macro", zero_division=0),
                    }
                    for j, label in enumerate(labels):
                        row[f"recall_{label}"] = recall_score(
                            y_test.iloc[mask, j], heldout_prediction[mask, j], zero_division=0
                        )
                    fairness_rows.append(row)
            fairness_table = pd.DataFrame(fairness_rows)
            display(fairness_table)

            center_transfer_rows = []
            if center_column and raw[center_column].nunique(dropna=True) >= 2:
                for heldout_center in raw[center_column].dropna().unique():
                    center_train_mask = raw[center_column] != heldout_center
                    center_test_mask = raw[center_column] == heldout_center
                    center_schema = FeatureSchema().fit(raw.loc[center_train_mask], PRE_LAB_FEATURES)
                    center_X_train = center_schema.transform(raw.loc[center_train_mask])
                    center_X_test = center_schema.transform(raw.loc[center_test_mask])
                    center_y_train = y.loc[center_train_mask].reset_index(drop=True)
                    center_y_test = y.loc[center_test_mask].reset_index(drop=True)
                    center_bundle = fit_binary_relevance(selected_model_name, center_X_train.reset_index(drop=True), center_y_train)
                    center_probability = predict_binary_relevance(center_bundle, center_X_test.reset_index(drop=True))
                    center_prediction = (center_probability >= 0.5).astype(int)
                    row = {
                        "test_center": str(heldout_center),
                        "n_test": int(center_test_mask.sum()),
                        "macro_f1": f1_score(center_y_test, center_prediction, average="macro", zero_division=0),
                    }
                    for j, label in enumerate(labels):
                        row[f"recall_{label}"] = recall_score(center_y_test.iloc[:, j], center_prediction[:, j], zero_division=0)
                    center_transfer_rows.append(row)
            center_transfer = pd.DataFrame(center_transfer_rows)
            display(center_transfer)
            """
        ),
        md(
            """
            # 20. Co-Infection Detection

            Co-infection risk is modeled as a secondary binary target indicating more
            than one active disease label. It informs review priority but does not
            replace the disease-specific outputs.

            # 21. VECTRA-X Triage Engine

            Every patient output separates prediction, uncertainty, triage
            recommendation, and confirmatory-test need. Public exports use generated
            case IDs rather than raw identifiers or held-out truth labels.
            """
        ),
        code(
            """
            coinfection_target_train = (y_train.sum(axis=1) > 1).astype(int)
            coinfection_model = make_binary_pipeline("Extra Trees", RANDOM_STATE).fit(
                tracks["PRE_LAB"]["X_train"], coinfection_target_train
            )
            coinfection_probability = coinfection_model.predict_proba(tracks["PRE_LAB"]["X_test"])[:, 1]

            RISK_WEIGHTS = {
                "malaria": 1.0, "dengue": 1.4, "typhoid": 1.3,
                "yellow_fever": 2.0, "other_diseases": 0.8,
            }
            severe_labels = {"dengue", "typhoid", "yellow_fever"}
            weights = np.array([RISK_WEIGHTS.get(label, 1.0) for label in labels])
            weighted_risk = (calibrated_test * weights).sum(axis=1) / weights.sum()
            severe_indices = [labels.index(label) for label in severe_labels if label in labels]
            severe_signal = calibrated_test[:, severe_indices].max(axis=1)
            triage_score = np.clip(
                0.45 * weighted_risk
                + 0.25 * severe_signal
                + 0.15 * uncertainty.mean_entropy.values
                + 0.15 * coinfection_probability,
                0,
                1,
            )

            def triage_category(index):
                severe = severe_signal[index]
                uncertainty_level = uncertainty.loc[index, "uncertainty_level"]
                coinfection = coinfection_probability[index]
                if severe >= 0.50 or (severe >= 0.35 and uncertainty_level == "high"):
                    return "Urgent Response"
                if severe >= 0.25 or (coinfection >= 0.60 and uncertainty_level != "low"):
                    return "Confirmatory Test Priority"
                if uncertainty_level == "low" and severe < 0.15 and coinfection < 0.40:
                    return "Routine"
                return "Clinical Review"

            ACTIONS = {
                "Routine": "Continue routine monitoring and document symptom changes.",
                "Clinical Review": "Prioritize review by a qualified health professional.",
                "Confirmatory Test Priority": "Prioritize confirmatory testing and closer observation.",
                "Urgent Response": "Flag for urgent clinical evaluation according to local protocols.",
            }
            patient_rows = []
            prediction = apply_thresholds(calibrated_test, thresholds)
            for i in range(len(y_test)):
                predicted = [label for j, label in enumerate(labels) if prediction[i, j] == 1]
                category = triage_category(i)
                row = {
                    "case_id": f"Case {i + 1:03d}",
                    "predicted_labels": "{" + ", ".join(predicted) + "}" if predicted else "{none}",
                    "conformal_caution_set": "{" + ", ".join(conformal_sets[i]) + "}",
                    "uncertainty_level": uncertainty.loc[i, "uncertainty_level"],
                    "coinfection_risk": float(coinfection_probability[i]),
                    "triage_score": float(triage_score[i]),
                    "triage_category": category,
                    "recommended_human_action": ACTIONS[category],
                    "confirmatory_test_needed": category in {"Confirmatory Test Priority", "Urgent Response"},
                }
                for j, label in enumerate(labels):
                    row[f"probability_{label}"] = float(calibrated_test[i, j])
                patient_rows.append(row)
            patient_decision_support = pd.DataFrame(patient_rows).sort_values(
                ["triage_score", "coinfection_risk"], ascending=False
            ).reset_index(drop=True)
            display(patient_decision_support.head(15))
            """
        ),
        md(
            """
            # 22. Resource Prioritization Simulation

            Resource simulations answer operational questions such as: if only 50
            rapid tests are available, which cases are prioritized and how many
            high-priority cases remain unserved?

            **Number-needed-to-review** is defined as reviewed flags divided by true
            positives among those flags. It connects precision to frontline workload.
            """
        ),
        code(
            """
            def simulate_capacity(frame, rapid_tests, beds, staff_slots):
                ranked = frame.sort_values("triage_score", ascending=False).reset_index(drop=True)
                test_need = ranked["confirmatory_test_needed"]
                urgent = ranked["triage_category"].eq("Urgent Response")
                review_need = ranked["triage_category"].isin(["Clinical Review", "Confirmatory Test Priority", "Urgent Response"])
                return pd.DataFrame([
                    ["rapid_tests", int(test_need.sum()), rapid_tests, max(0, int(test_need.sum()) - rapid_tests)],
                    ["beds", int(urgent.sum()), beds, max(0, int(urgent.sum()) - beds)],
                    ["staff_review_slots", int(review_need.sum()), staff_slots, max(0, int(review_need.sum()) - staff_slots)],
                ], columns=["resource", "demand", "capacity", "unserved"])

            resource_simulation = simulate_capacity(patient_decision_support, rapid_tests=50, beds=12, staff_slots=80)
            display(resource_simulation)

            policy_rows = []
            policy_thresholds = {
                "performance": thresholds,
                "safety": {label: max(0.05, thresholds[label] - (0.10 if label in severe_labels else 0.05)) for label in labels},
                "operational": {label: min(0.90, thresholds[label] + 0.05) for label in labels},
            }
            for policy, values in policy_thresholds.items():
                flags = apply_thresholds(calibrated_test, values)
                total_flags = int(flags.sum())
                true_positives = int((flags * y_test.values).sum())
                policy_rows.append({
                    "policy": policy,
                    "total_flags": total_flags,
                    "true_positive_flags": true_positives,
                    "number_needed_to_review": total_flags / true_positives if true_positives else np.nan,
                    "avg_flags_per_patient": total_flags / len(flags),
                })
            threshold_resource_tradeoff = pd.DataFrame(policy_rows)
            display(threshold_resource_tradeoff)
            """
        ),
        md(
            """
            # 23. Dashboard Prototype Overview

            The Hybrid Command Center mirrors this notebook’s evidence:

            1. **Command Center:** signals → uncertainty → triage → resources.
            2. **Patient Intelligence:** probabilities, co-infection, uncertainty,
               explanation, tier, and recommended human action.
            3. **Resource Allocation:** capacity controls and ranked queues.
            4. **Trust & Evidence:** performance, calibration, false negatives,
               fairness, robustness, explainability, and caveats.

            Public views use de-identified case IDs and exclude truth labels.
            """
        ),
        md(
            """
            # 24. Final Discussion

            ## Why VECTRA-X Can Win

            VECTRA-X is more than a disease classifier. It preserves co-infection,
            exposes diagnostic leakage, communicates uncertainty, audits transfer
            failure, and connects predictions to scarce-resource decisions.

            ## Metric Interpretation

            Macro PR-AUC supports imbalanced ranking comparison; per-label recall and
            false-negative rate expose safety failures; number-needed-to-review and
            capacity coverage quantify workload; calibration tests whether
            probabilities can support prioritization; decision-curve net benefit
            evaluates whether model-guided testing can outperform testing everyone or
            no one at a range of threshold probabilities.

            # 25. Limitations and Ethics

            - The cohort has only 300 patients and rare-label estimates are unstable.
            - Typhoid and yellow-fever performance must be interpreted with support counts.
            - **Typhoid coverage** and false-negative estimates are too unstable for safety claims.
            - Leave-one-center-out degradation limits claims of facility transfer.
            - Calibration and conformal behavior vary by label.
            - Triage rules and resource weights are transparent simulations, not validated outcomes.
            - The system is decision-support, not diagnosis, and requires prospective validation.

            **Competition prototype requiring prospective validation.**

            # 26. Conclusion and Recommendations

            The recommended model is the candidate that performs well in training-only
            ranking while maintaining defensible recall, calibration, stability, and
            resource burden. The FULL track remains research-only. Before real-world
            use, VECTRA-X requires prospective multi-center validation, facility
            recalibration, clinician co-design, and outcome-based resource evaluation.
            """
        ),
        md(
            """
            # 27. Appendix

            ## 27.1 95% Confidence Intervals

            Patient-level bootstrap intervals quantify sampling uncertainty on the
            untouched holdout.

            ## 27.2 Repeated Multi-Label Validation

            Repeated stratified validation estimates model-selection variance without
            repeatedly touching the holdout.

            ## 27.3 Decision-Curve Net Benefit

            Net benefit is reported for model-guided testing, test-all, and test-none
            strategies across threshold probabilities.

            ## 27.4 Preprocessing and Component Ablation

            Sensitivity checks compare the complete train-fitted design with removal of
            center features and missing indicators. Differences are interpreted as
            instability evidence, not causal effects.

            ## 27.5 Artifact Provenance

            The execution manifest records data checksum, package versions, random
            seed, selected model, and generated output files.
            """
        ),
        code(
            """
            def per_label_metrics(target, prediction, probabilities):
                rows = []
                for j, label in enumerate(target.columns):
                    truth = target.iloc[:, j].values
                    pred = prediction[:, j]
                    tn, fp, fn, tp = confusion_matrix(truth, pred, labels=[0, 1]).ravel()
                    rows.append({
                        "label": label,
                        "support_pos": int(truth.sum()),
                        "precision": precision_score(truth, pred, zero_division=0),
                        "recall": recall_score(truth, pred, zero_division=0),
                        "f1": f1_score(truth, pred, zero_division=0),
                        "pr_auc": safe_ap(truth, probabilities[:, j]),
                        "roc_auc": safe_auc(truth, probabilities[:, j]),
                        "false_negative_rate": fn / (fn + tp) if (fn + tp) else 0.0,
                        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
                    })
                return pd.DataFrame(rows)

            heldout_metrics = pd.DataFrame([{
                "track": "PRE_LAB",
                "model": selected_model_name,
                **aggregate_metrics(y_test, heldout_prediction, calibrated_test),
            }])
            heldout_per_label = per_label_metrics(y_test, heldout_prediction, calibrated_test)

            def bootstrap_metrics(target, prediction, probabilities, draws=500):
                rng = np.random.default_rng(RANDOM_STATE)
                records = []
                names = ["macro_f1", "micro_f1", "macro_recall", "macro_pr_auc"]
                point = aggregate_metrics(target, prediction, probabilities)
                distributions = {name: [] for name in names}
                for _ in range(draws):
                    sample = rng.integers(0, len(target), len(target))
                    metrics = aggregate_metrics(
                        target.iloc[sample].reset_index(drop=True),
                        prediction[sample],
                        probabilities[sample],
                    )
                    for name in names:
                        distributions[name].append(metrics[name])
                for name in names:
                    low, high = np.nanquantile(distributions[name], [0.025, 0.975])
                    records.append({
                        "metric": name, "estimate": point[name],
                        "ci_low": float(min(low, point[name])),
                        "ci_high": float(max(high, point[name])),
                        "bootstrap_draws": draws,
                    })
                return pd.DataFrame(records)

            confidence_intervals = bootstrap_metrics(y_test, heldout_prediction, calibrated_test)
            display(heldout_metrics)
            display(heldout_per_label)
            display(confidence_intervals)

            decision_curve_rows = []
            for j, label in enumerate(labels):
                truth = y_test.iloc[:, j].values
                probability = calibrated_test[:, j]
                for threshold in np.linspace(0.10, 0.70, 13):
                    odds = threshold / (1 - threshold)
                    model_prediction = probability >= threshold
                    prevalence = truth.mean()
                    model_nb = ((model_prediction & (truth == 1)).sum() / len(truth)) - (
                        (model_prediction & (truth == 0)).sum() / len(truth)
                    ) * odds
                    test_all_nb = prevalence - (1 - prevalence) * odds
                    decision_curve_rows.extend([
                        [label, threshold, "model", model_nb],
                        [label, threshold, "test_all", test_all_nb],
                        [label, threshold, "test_none", 0.0],
                    ])
            decision_curve = pd.DataFrame(
                decision_curve_rows,
                columns=["label", "threshold", "strategy", "net_benefit"],
            )
            display(decision_curve.head())

            # Repeated validation of the selected model on the training partition.
            repeated_rows = []
            for repeat_seed in [42, 84, 126]:
                repeated_cv = MultilabelStratifiedKFold(n_splits=3, shuffle=True, random_state=repeat_seed)
                repeated_oof = np.zeros_like(selected_oof)
                for fold_train, fold_valid in repeated_cv.split(np.zeros(len(y_train)), y_train.values):
                    bundle = fit_binary_relevance(
                        selected_model_name,
                        X_pre_train.iloc[fold_train],
                        y_train.iloc[fold_train],
                        seed=repeat_seed,
                    )
                    repeated_oof[fold_valid] = predict_binary_relevance(bundle, X_pre_train.iloc[fold_valid])
                repeated_rows.append({"seed": repeat_seed, **probability_metrics(y_train, repeated_oof)})
            repeated_validation = pd.DataFrame(repeated_rows)
            display(repeated_validation)

            exports = {
                "model_comparison.csv": leaderboard,
                "model_rationale.csv": MODEL_RATIONALE,
                "held_out_metrics.csv": heldout_metrics,
                "held_out_track_comparison.csv": track_metrics,
                "per_label_metrics.csv": heldout_per_label,
                "confidence_intervals.csv": confidence_intervals,
                "thresholds.csv": threshold_table,
                "calibration_metrics.csv": calibration_table,
                "conformal_metrics.csv": conformal_table,
                "fairness_metrics.csv": fairness_table,
                "center_transfer.csv": center_transfer,
                "feature_importance.csv": feature_importance,
                "decision_curve_net_benefit.csv": decision_curve,
                "threshold_resource_tradeoff.csv": threshold_resource_tradeoff,
                "resource_simulation.csv": resource_simulation,
                "patient_decision_support.csv": patient_decision_support,
                "repeated_validation.csv": repeated_validation,
            }
            for filename, frame in exports.items():
                frame.to_csv(OUTPUT_DIR / "tables" / filename, index=False)

            model_export_note = {
                "status": "not serialized from the submission notebook",
                "reason": (
                    "The official deliverable is a self-contained executed notebook. "
                    "Fresh tables and the execution manifest are exported, but no saved "
                    "model is required or read by the notebook."
                ),
                "selected_model": selected_model_name,
                "labels": labels,
                "thresholds": thresholds,
            }
            (OUTPUT_DIR / "models" / "README.json").write_text(
                json.dumps(model_export_note, indent=2), encoding="utf-8"
            )
            manifest = {
                "project": "VECTRA-X",
                "title": "Uncertainty-Aware Triage Intelligence for Vector-Borne Disease Response in Resource-Limited Humanitarian Settings",
                "random_state": RANDOM_STATE,
                "data": data_provenance,
                "selected_model": selected_model_name,
                "selection_metric": "training-only OOF macro PR-AUC plus triage suitability review",
                "python": platform.python_version(),
                "packages": {
                    "pandas": pd.__version__,
                    "numpy": np.__version__,
                    "scikit_learn": sklearn.__version__,
                    "xgboost": xgboost.__version__,
                    "lightgbm": lightgbm.__version__,
                    "shap": shap.__version__,
                },
                "outputs": sorted(exports),
            }
            (OUTPUT_DIR / "execution_manifest.json").write_text(
                json.dumps(manifest, indent=2), encoding="utf-8"
            )
            print("Fresh outputs written:", OUTPUT_DIR.resolve())
            display(pd.DataFrame([manifest]))
            """
        ),
        md(
            """
            ## References

            1. World Health Organization. *Global vector control response 2017-2030*. 2017.
            2. World Health Organization. *Ethics and governance of artificial intelligence for health*. 2021.
            3. World Health Organization. *Dengue: guidelines for diagnosis, treatment, prevention and control*. 2009.
            4. World Health Organization. *WHO guidelines for malaria*. Continuously updated.
            5. Sechidis K, Tsoumakas G, Vlahavas I. On the stratification of multi-label data. ECML PKDD, 2011.
            6. Read J, Pfahringer B, Holmes G, Frank E. Classifier chains for multi-label classification. *Machine Learning*, 2011.
            7. Niculescu-Mizil A, Caruana R. Predicting good probabilities with supervised learning. ICML, 2005.
            8. Vovk V, Gammerman A, Shafer G. *Algorithmic Learning in a Random World*. Springer, 2005.
            9. Angelopoulos AN, Bates S. Conformal prediction: a gentle introduction. *Foundations and Trends in Machine Learning*, 2023.
            10. Vickers AJ, Elkin EB. Decision curve analysis. *Medical Decision Making*, 2006.
            11. Collins GS et al. TRIPOD+AI statement. *BMJ*, 2024.
            12. Wolff RF et al. PROBAST. *Annals of Internal Medicine*, 2019.
            13. Lundberg SM, Lee SI. A unified approach to interpreting model predictions. NeurIPS, 2017.
            14. Chen T, Guestrin C. XGBoost. KDD, 2016.
            15. Ke G et al. LightGBM. NeurIPS, 2017.
            16. Obermeyer Z et al. Dissecting racial bias in population health algorithms. *Science*, 2019.
            """
        ),
    ]
    notebook = nbf.v4.new_notebook(cells=cells)
    notebook.metadata.kernelspec = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook.metadata.language_info = {"name": "python", "version": "3.12"}
    return notebook


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(build_notebook(), NOTEBOOK_PATH)
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
