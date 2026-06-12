"""data_loader — robust ingestion of the official vector-borne disease CSV.

The official export (``data/raw/data.csv``) is a French/English bilingual file:
    * semicolon-separated,
    * decimal-comma in numeric fields (e.g. ``3,84``),
    * trailing whitespace in several column names and category values
      (e.g. ``"Récurrente "``, ``"Goutte épaisse "``),
    * blank strings that mean *unknown* — NEVER the negative class ``NON``.

This module loads the file defensively (encoding + separator fallbacks),
preserves the raw file untouched, lightly cleans column names / string cells,
and writes an interim parquet/CSV snapshot. It does NOT impute or encode —
that is the job of :mod:`preprocessing`.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from . import report_utils as ru

logger = ru.get_logger(__name__)


def _sniff_separator(sample: str, candidates: tuple[str, ...] = (";", ",", "\t", "|")) -> str:
    """Best-effort delimiter detection from a text sample."""
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(candidates))
        return dialect.delimiter
    except Exception:
        # Fall back to the most frequent candidate on the header line.
        header = sample.splitlines()[0] if sample else ""
        counts = {c: header.count(c) for c in candidates}
        return max(counts, key=counts.get)


def load_raw(cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    """Load the raw CSV, trying multiple encodings and auto-detecting the
    separator if the configured one yields a single column.

    Returns a DataFrame with stripped column names and stripped string values.
    Empty strings are converted to ``NA`` (genuine missing), but tokens such as
    ``NON`` / ``Négatif`` are left intact for stage-aware encoding downstream.
    """
    cfg = cfg or ru.load_config()
    csv_path = ru.resolve(cfg["paths"]["raw_csv"])
    sep = cfg["io"]["sep"]
    decimal = cfg["io"]["decimal"]
    encodings = cfg["io"]["encodings_to_try"]

    last_err: Exception | None = None
    df: pd.DataFrame | None = None
    for enc in encodings:
        try:
            with open(csv_path, "r", encoding=enc, errors="strict") as fh:
                sample = fh.read(8192)
            use_sep = sep
            # If the configured separator does not appear, sniff one.
            if sample and sample.splitlines()[0].count(sep) == 0:
                use_sep = _sniff_separator(sample)
                logger.warning("Configured sep %r not found; sniffed %r", sep, use_sep)
            df = pd.read_csv(
                csv_path,
                sep=use_sep,
                decimal=decimal,
                encoding=enc,
                dtype=str,            # parse everything as string first; type later
                keep_default_na=True,
                na_values=["", " ", "NA", "N/A", "nan", "NaN"],
            )
            logger.info("Loaded raw CSV with encoding=%s sep=%r -> %d rows x %d cols",
                        enc, use_sep, df.shape[0], df.shape[1])
            break
        except (UnicodeDecodeError, UnicodeError) as exc:
            last_err = exc
            logger.warning("Encoding %s failed: %s", enc, exc)
            continue
    if df is None:
        raise RuntimeError(f"Could not read {csv_path} with encodings {encodings}: {last_err}")

    # --- light, non-destructive cleaning --------------------------------- #
    df.columns = [str(c).strip() for c in df.columns]

    obj_cols = df.columns
    for col in obj_cols:
        # Strip surrounding whitespace in string cells (e.g. 'Récurrente ').
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)
    # Re-apply NA conversion on now-empty strings created by stripping.
    df = df.replace({"": pd.NA})

    return df


def load_dictionary(cfg: dict[str, Any] | None = None) -> pd.DataFrame:
    """Load the data-dictionary spreadsheet (best effort)."""
    cfg = cfg or ru.load_config()
    dict_path = ru.resolve(cfg["paths"]["raw_dict"])
    try:
        d = pd.read_excel(dict_path)
        d.columns = [str(c).strip() for c in d.columns]
        logger.info("Loaded data dictionary: %d rows x %d cols", *d.shape)
        return d
    except Exception as exc:  # pragma: no cover - dictionary is supplementary
        logger.warning("Could not load data dictionary (%s); continuing without it.", exc)
        return pd.DataFrame()


def save_interim(df: pd.DataFrame, cfg: dict[str, Any] | None = None) -> Path:
    """Persist a cleaned snapshot to ``data/interim`` (parquet if possible)."""
    cfg = cfg or ru.load_config()
    interim = ru.resolve(cfg["paths"]["interim"])
    interim.mkdir(parents=True, exist_ok=True)
    csv_out = interim / "cleaned_patient_table.csv"
    df.to_csv(csv_out, index=False, encoding="utf-8-sig")
    try:
        df.to_parquet(interim / "cleaned_patient_table.parquet", index=False)
    except Exception as exc:
        logger.info("Parquet snapshot skipped (%s); CSV interim written.", exc)
    return csv_out


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    cfg = ru.load_config()
    df = load_raw(cfg)
    print(df.shape)
    print(df.columns.tolist()[:5], "...")
    save_interim(df, cfg)
