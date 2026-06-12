"""report_utils — shared infrastructure for the VECTRA-X pipeline.

Centralises:
    * project-root / config resolution (no hard-coded absolute paths),
    * logging setup,
    * small helpers for writing markdown reports and tables.

Every other module imports paths and config from here so the project is
relocatable and reproducible on any machine (Windows paths handled via
``pathlib``).
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import yaml

# --------------------------------------------------------------------------- #
# Path / config resolution
# --------------------------------------------------------------------------- #
# This file lives at <project_root>/src/report_utils.py
PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
CONFIG_PATH: Path = PROJECT_ROOT / "config" / "config.yaml"

_CONFIG_CACHE: dict[str, Any] | None = None


def load_config(path: Path | str | None = None) -> dict[str, Any]:
    """Load (and cache) the YAML config."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None and path is None:
        return _CONFIG_CACHE
    cfg_path = Path(path) if path is not None else CONFIG_PATH
    with open(cfg_path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    if path is None:
        _CONFIG_CACHE = cfg
    return cfg


def resolve(rel: str) -> Path:
    """Resolve a config-relative path to an absolute :class:`Path`."""
    return (PROJECT_ROOT / rel).resolve()


def get_paths(cfg: dict[str, Any] | None = None) -> dict[str, Path]:
    """Return a dict of resolved, existing output/data directories."""
    cfg = cfg or load_config()
    paths = {k: resolve(v) for k, v in cfg["paths"].items()}
    for key, p in paths.items():
        # Only mkdir directories, not files (raw_csv / raw_dict are files).
        if p.suffix == "":
            p.mkdir(parents=True, exist_ok=True)
    return paths


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #
def get_logger(name: str = "vectra_x") -> logging.Logger:
    """Return a configured logger (idempotent)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


# --------------------------------------------------------------------------- #
# Report / table helpers
# --------------------------------------------------------------------------- #
def save_table(df: pd.DataFrame, path: Path | str, index: bool = False) -> Path:
    """Persist a DataFrame to CSV (utf-8-sig so Excel renders accents)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index, encoding="utf-8-sig")
    return path


def df_to_markdown(df: pd.DataFrame, max_rows: int | None = None,
                   floatfmt: str = "{:.4f}") -> str:
    """Render a DataFrame as a GitHub-flavoured markdown table.

    Falls back to a manual renderer if the optional ``tabulate`` dependency
    is unavailable (keeps the pipeline dependency-light).
    """
    view = df if max_rows is None else df.head(max_rows)
    try:
        return view.to_markdown(index=False, floatfmt=floatfmt.replace("{:", "").replace("}", ""))
    except Exception:
        cols = list(view.columns)
        lines = ["| " + " | ".join(map(str, cols)) + " |",
                 "| " + " | ".join("---" for _ in cols) + " |"]
        for _, row in view.iterrows():
            cells = []
            for v in row:
                if isinstance(v, float):
                    cells.append(floatfmt.format(v))
                else:
                    cells.append(str(v))
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)


class MarkdownReport:
    """Tiny builder for assembling markdown report files section-by-section."""

    def __init__(self, title: str, subtitle: str | None = None):
        self.parts: list[str] = [f"# {title}\n"]
        if subtitle:
            self.parts.append(f"*{subtitle}*\n")
        self.parts.append(
            f"_Generated: {datetime.now():%Y-%m-%d %H:%M} — VECTRA-X pipeline_\n"
        )

    def h2(self, text: str) -> "MarkdownReport":
        self.parts.append(f"\n## {text}\n")
        return self

    def h3(self, text: str) -> "MarkdownReport":
        self.parts.append(f"\n### {text}\n")
        return self

    def p(self, text: str) -> "MarkdownReport":
        self.parts.append(text + "\n")
        return self

    def bullets(self, items: Iterable[str]) -> "MarkdownReport":
        self.parts.append("\n".join(f"- {it}" for it in items) + "\n")
        return self

    def table(self, df: pd.DataFrame, max_rows: int | None = None,
              floatfmt: str = "{:.4f}") -> "MarkdownReport":
        self.parts.append(df_to_markdown(df, max_rows=max_rows, floatfmt=floatfmt) + "\n")
        return self

    def code(self, text: str, lang: str = "") -> "MarkdownReport":
        self.parts.append(f"```{lang}\n{text}\n```\n")
        return self

    def figure(self, rel_path: str, caption: str = "") -> "MarkdownReport":
        self.parts.append(f"\n![{caption}]({rel_path})\n")
        if caption:
            self.parts.append(f"*{caption}*\n")
        return self

    def render(self) -> str:
        return "\n".join(self.parts)

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.render(), encoding="utf-8")
        return path
