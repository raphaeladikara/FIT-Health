# -*- coding: utf-8 -*-
"""Generator: transform notebooks/VECTRA_X_Final.ipynb into a fully self-contained
single-file scientific submission notebook (no src/ imports, no config/ files,
no release bundles, robust dataset discovery). Run with the project python.

This is a DEVELOPMENT tool. It is NOT part of the submission.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
# The pristine pre-transformation notebook is stashed under scripts/ so it is
# never matched by the in-notebook integrity scan (which only globs the cwd and
# notebooks/). The transformed copy is written into notebooks/.
NB_IN = ROOT / "scripts" / "_original_notebook.ipynb"
NB_OUT = ROOT / "notebooks" / "VECTRA_X_Final.ipynb"

MODULE_ORDER = [
    "report_utils", "preprocessing", "evaluation", "schema_audit",
    "label_detection", "leakage_audit", "modeling", "calibration", "conformal",
    "research_evaluation", "fairness", "explainability", "triage_engine",
    "data_loader", "notebook_workflow",
]


def _new_id() -> str:
    return uuid.uuid4().hex[:8]


def md(source: str) -> dict:
    return {"cell_type": "markdown", "id": _new_id(), "metadata": {},
            "source": source.strip("\n").splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "id": _new_id(), "metadata": {},
            "execution_count": None, "outputs": [],
            "source": source.strip("\n").splitlines(keepends=True)}


def callout(title, shows, matters, decision, risk, limitation,
            color="#0f766e", bg="#f0fdfa") -> str:
    return (
        f'<div style="border-left: 5px solid {color}; padding: 12px 16px; '
        f'background-color: {bg}; border-radius: 8px; margin: 12px 0;">\n\n'
        f'### {title}\n\n'
        f'**What the result shows.**  \n{shows}\n\n'
        f'**Why it matters.**  \n{matters}\n\n'
        f'**Decision supported by this evidence.**  \n{decision}\n\n'
        f'**Risk controlled.**  \n{risk}\n\n'
        f'**Remaining limitation.**  \n{limitation}\n\n'
        f'</div>'
    )


# --------------------------------------------------------------------------- #
# 1. Read and lightly transform module sources for in-notebook embedding.
# --------------------------------------------------------------------------- #
def load_module_sources() -> dict[str, str]:
    sources = {}
    for name in MODULE_ORDER:
        text = (SRC / f"{name}.py").read_text(encoding="utf-8")
        assert "'''" not in text, f"{name} contains triple-single-quote"
        sources[name] = text
    return sources


MODULE_SOURCES = load_module_sources()

# --------------------------------------------------------------------------- #
# 2. Library cell sources (config, robust loader, package build, overrides).
# --------------------------------------------------------------------------- #
CONFIG_CELL = r'''
# ---------------------------------------------------------------------------
# Inlined configuration (was config/config.yaml + config/notebook_experiment.json
# + config/clinical_ranges.json). Editing any value here changes behaviour
# without touching the analysis code below.
# ---------------------------------------------------------------------------
VECTRA_CONFIG = {
    "project": {
        "name": "VECTRA-X",
        "full_name": ("VECTRA-X: A Multi-label, Explainable, and Uncertainty-Aware "
                      "Clinical Triage Intelligence System for Vector-Borne Disease Response"),
        "competition": "FIT Competition 2026 - Track IV: AI-based Vector-Borne Disease Prediction",
        "random_state": 42,
    },
    "paths": {
        "raw_csv": "data/raw/data.csv",
        "raw_dict": "data/raw/desciption.xlsx",
        "interim": "data/interim", "processed": "data/processed",
        "figures": "outputs/figures", "tables": "outputs/tables",
        "models": "outputs/models", "reports": "outputs/reports",
        "dashboard_data": "outputs/dashboard_data",
    },
    "io": {
        "sep": ";", "decimal": ",",
        "encodings_to_try": ["utf-8", "utf-8-sig", "latin1", "cp1252"],
        "uuid_col": "_uuid",
    },
    "labels": {
        "binary_prefix": "Maladies diagnostiquées/",
        "text_label_col": "Maladies diagnostiquées",
        "alias_map": {
            "Paludisme (Malaria)": "malaria",
            "Dengue": "dengue",
            "Chikunguya": "chikungunya",
            "Fièvre jaune (yellow fever)": "yellow_fever",
            "Fièvre Typhoïde (Thyphoid fever)": "typhoid",
            "Zika": "zika",
            "Autres maladies diagnostiqué (Others diseases)": "other_diseases",
            "Option 8": "option_8",
        },
        "drop_if_no_positives": True,
    },
    "leakage": {
        "research_only_features": [
            "Autres maladies presentees par le patient",
            "Autres maladies présentées par le patient",
        ],
        "target_aliases": {
            "malaria": ["malaria", "paludisme", "palu"],
            "dengue": ["dengue", "dengua"],
            "yellow_fever": ["yellow", "jaune", "fievre jaune", "fièvre jaune"],
            "typhoid": ["typhoid", "thyphoid", "typhoide", "typhoïde"],
            "other_diseases": ["other", "others", "autres", "autre maladie"],
        },
        "name_patterns": [
            "dengue", "dengua", "malaria", "palu", "typh", "typhus", "yellow",
            "jaune", "fever", "fièvre", "diagnos", "test", "tdr", "goutte",
            "thick", "smear", "microscopy", "pcr", "positive", "positif",
            "result", "résultat", "serolog", "antigen", "igm", "igg",
            "ns1", "lab", "confirm",
        ],
        "mi_flag_threshold": 0.30,
        "single_feature_auc_flag": 0.90,
        "known_lab_confirmation": ["Test TDR", "Goutte épaisse "],
    },
    "preprocessing": {
        "yes_tokens": ["oui", "positif", "positive", "yes", "1", "true", "présent", "present"],
        "no_tokens": ["non", "négatif", "negatif", "negative", "no", "0", "false", "absent"],
        "gender_col_fragment": "Genre",
        "center_col_fragment": "Centre de santé",
        "age_col_fragment": "Âge",
        "high_missing_threshold": 0.60,
        "near_constant_threshold": 0.99,
        "high_cardinality_threshold": 0.50,
    },
    "modeling": {
        "cv_folds": 5, "test_size": 0.25, "calibration_size": 0.5,
        "conformal_alpha": 0.10,
        "risk_weights": {"malaria": 1.0, "dengue": 1.4, "typhoid": 1.3,
                         "yellow_fever": 2.0, "other_diseases": 0.8},
        "severe_labels": ["yellow_fever", "dengue", "typhoid"],
    },
}

# Experiment protocol (was config/notebook_experiment.json).
EXPERIMENT_CONFIG_RAW = {
    "dataset_path": "data/raw/data.csv",
    "target_policy": "complete_multilabel_only",
    "frozen_test": {"size": 0.25, "seed": 42},
    "validation": {"outer_folds": 5, "inner_folds": 3, "repeated_seeds": [42, 43, 44]},
    "candidates": [
        {"id": "logreg_c0.1", "enabled": True}, {"id": "logreg_c0.5", "enabled": True},
        {"id": "logreg_c2.0", "enabled": True}, {"id": "extra_trees_leaf2", "enabled": True},
        {"id": "extra_trees_leaf5", "enabled": True},
    ],
    "threshold": {
        "grid": [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5,
                 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95],
        "objective": "f1", "tie_break": "higher_recall_then_lower_threshold",
    },
    "calibration_methods": ["sigmoid", "isotonic"],
    "bootstrap": {"repetitions": 2000, "confidence_level": 0.95},
    "minimum_subgroup_support": 5,
    "release_schema_version": "1.0.0",
}
print("Inlined configuration ready (no external YAML/JSON config files required).")
'''

LOADER_CELL = r'''
# ---------------------------------------------------------------------------
# Robust dataset discovery (replaces a fixed repository path). The judges
# already hold the official FIT dataset; this searches common locations and
# handles the semicolon-separated, decimal-comma export format.
# ---------------------------------------------------------------------------
import csv
import glob as _glob

_DATASET_CANDIDATES = [
    "data.csv", "train.csv",
    "data/raw/data.csv", "../data/raw/data.csv", "../../data/raw/data.csv",
    "data/data.csv", "input/data.csv", "./input/data.csv",
    "dataset.csv", "vectra_x.csv", "FIT_data.csv",
]
_DATASET_GLOBS = [
    "/kaggle/input/**/data.csv", "/kaggle/input/**/train.csv",
    "/kaggle/input/**/*.csv", "data/raw/*.csv", "input/**/*.csv", "./*.csv",
]


def _discover_dataset():
    for rel in _DATASET_CANDIDATES:
        p = Path(rel)
        if p.is_file():
            return p
    for pattern in _DATASET_GLOBS:
        for hit in sorted(_glob.glob(pattern, recursive=True)):
            ph = Path(hit)
            if ph.is_file() and ph.suffix.lower() == ".csv" and "desc" not in ph.stem.lower():
                return ph
    raise FileNotFoundError(
        "Official FIT dataset not found. Please place the dataset as `data.csv` in the "
        "same folder as this notebook, or place it under `data/raw/data.csv`, then rerun "
        "all cells."
    )


def _detect_separator(sample: str, configured: str = ";") -> str:
    first = sample.splitlines()[0] if sample else ""
    if configured and first.count(configured) > 0:
        return configured
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t|").delimiter
    except Exception:
        counts = {d: first.count(d) for d in [";", ",", "\t", "|"]}
        return max(counts, key=counts.get)


def robust_load_raw(cfg=None):
    """Discover and load the official CSV as strings (typing happens later)."""
    cfg = cfg or VECTRA_CONFIG
    path = _discover_dataset()
    encodings = cfg.get("io", {}).get("encodings_to_try",
                                      ["utf-8", "utf-8-sig", "latin1", "cp1252"])
    configured_sep = cfg.get("io", {}).get("sep", ";")
    df, last_err = None, None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="strict") as fh:
                sample = fh.read(8192)
            sep = _detect_separator(sample, configured_sep)
            df = pd.read_csv(
                path, sep=sep, dtype=str, keep_default_na=True,
                na_values=["", " ", "NA", "N/A", "nan", "NaN"],
                encoding=enc, engine="python",
            )
            break
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_err = exc
            continue
    if df is None:
        raise RuntimeError(f"Could not read {path} with encodings {encodings}: {last_err}")
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.replace({"": pd.NA})
    print(f"Loaded official dataset: {path.as_posix()}  ->  "
          f"{df.shape[0]} rows x {df.shape[1]} columns")
    return df


print("Dataset-discovery helpers ready.")
'''


def build_modules_cell() -> str:
    parts = [
        "# ---------------------------------------------------------------------------",
        "# Inlined analysis library. Each entry below is the verbatim source of one",
        "# module from the original modular codebase. They are stored as text here and",
        "# executed into an in-memory package a few cells down, so this single .ipynb",
        "# carries every helper function it uses (no `src/` package is imported).",
        "# ---------------------------------------------------------------------------",
        "_MODULE_SOURCES = {}",
    ]
    for name in MODULE_ORDER:
        parts.append(f"\n_MODULE_SOURCES[{name!r}] = r'''\n{MODULE_SOURCES[name]}'''")
    parts.append("\nprint(f'Inlined {len(_MODULE_SOURCES)} analysis modules as source text.')")
    return "\n".join(parts)


BUILD_CELL = r'''
# ---------------------------------------------------------------------------
# Build the inlined library into an in-memory package and execute it. Module
# objects are pre-created so that intra-library imports resolve, then each
# source is executed (report_utils first because the others log through it).
# ---------------------------------------------------------------------------
import sys as _sys
import types as _types

_PKG = "_vectra_lib"
for _stale in [m for m in list(_sys.modules) if m == _PKG or m.startswith(_PKG + ".")]:
    del _sys.modules[_stale]

_pkg = _types.ModuleType(_PKG)
_pkg.__path__ = []  # marks it as a package
_sys.modules[_PKG] = _pkg

_ORDER = [
    "report_utils", "preprocessing", "evaluation", "schema_audit",
    "label_detection", "leakage_audit", "modeling", "calibration", "conformal",
    "research_evaluation", "fairness", "explainability", "triage_engine",
    "data_loader", "notebook_workflow",
]
for _name in _ORDER:
    _mod = _types.ModuleType(f"{_PKG}.{_name}")
    _mod.__package__ = _PKG
    _mod.__file__ = f"{_PKG}/{_name}.py"
    _sys.modules[f"{_PKG}.{_name}"] = _mod
    setattr(_pkg, _name, _mod)

for _name in _ORDER:
    _src = _MODULE_SOURCES[_name].replace("from . import ", f"from {_PKG} import ")
    _src = _src.replace("import yaml\n", "")  # YAML is replaced by the inlined dict
    exec(compile(_src, f"{_PKG}/{_name}.py", "exec"),
         _sys.modules[f"{_PKG}.{_name}"].__dict__)

# --- Bind the inlined config / dataset / experiment loaders ----------------
_ru = _sys.modules[f"{_PKG}.report_utils"]
_dl = _sys.modules[f"{_PKG}.data_loader"]
_nw = _sys.modules[f"{_PKG}.notebook_workflow"]

_ru._CONFIG_CACHE = VECTRA_CONFIG
_ru.load_config = lambda path=None: VECTRA_CONFIG
_dl.load_raw = robust_load_raw
_dl.load_dictionary = lambda cfg=None: pd.DataFrame()


def _inlined_experiment_config(path=None):
    raw = EXPERIMENT_CONFIG_RAW
    seeds = tuple(int(s) for s in raw["validation"]["repeated_seeds"])
    candidates = tuple(c for c in raw["candidates"] if c.get("enabled", True))
    grid = tuple(float(v) for v in raw["threshold"]["grid"])
    return _nw.ExperimentConfig(
        dataset_path=str(raw["dataset_path"]),
        target_policy=str(raw["target_policy"]),
        frozen_test=_nw.FrozenTestConfig(float(raw["frozen_test"]["size"]),
                                         int(raw["frozen_test"]["seed"])),
        validation=_nw.ValidationConfig(int(raw["validation"]["outer_folds"]),
                                        int(raw["validation"]["inner_folds"]), seeds),
        candidates=candidates,
        threshold=_nw.ThresholdConfig(grid, str(raw["threshold"]["objective"]),
                                      str(raw["threshold"]["tie_break"])),
        calibration_methods=tuple(raw["calibration_methods"]),
        bootstrap=_nw.BootstrapConfig(int(raw["bootstrap"]["repetitions"]),
                                      float(raw["bootstrap"]["confidence_level"])),
        minimum_subgroup_support=int(raw["minimum_subgroup_support"]),
        release_schema_version=str(raw["release_schema_version"]),
        source_path=Path("inlined://notebook_experiment.json"),
    )


_nw.load_experiment_config = _inlined_experiment_config

# The single public entry point used by the rest of the notebook.
run_research_workflow = _nw.run_research_workflow
print(f"Self-contained analysis library ready: {len(_ORDER)} modules inlined "
      f"and bound. Entry point: run_research_workflow().")
'''


def main():
    nb = json.loads(NB_IN.read_text(encoding="utf-8"))
    print("loaded", len(nb["cells"]), "cells")
    # Placeholder: cell editing happens in build_submission_cells.py (imported).
    import build_submission_cells as bsc
    bsc.transform(nb, md, code, callout, CONFIG_CELL, LOADER_CELL,
                  build_modules_cell(), BUILD_CELL)
    NB_OUT.write_text(json.dumps(nb, ensure_ascii=True, indent=1), encoding="utf-8")
    print("wrote", NB_OUT, "with", len(nb["cells"]), "cells")


if __name__ == "__main__":
    main()
