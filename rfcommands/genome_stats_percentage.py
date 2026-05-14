from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PERCENTAGE_ROWS = [
    ("clipped_reads",             "total_reads",               "clipped_reads_%"),
    ("filtered_out",              "clipped_reads",             "filtered_out_%"),
    ("filter_kept",               "clipped_reads",             "filter_kept_%"),
    ("genome_primary_alignments", "filter_kept",               "genome_primary_alignments_%"),
    ("genome_primary_alignments", "genome_total_alignments",   "genome_pct_primary"),
    ("qpass_primary_alignments",  "genome_primary_alignments", "qpass_primary_alignments_%"),
    ("qpass_primary_alignments",  "qpass_total_alignments",    "qpass_pct_primary"),
    ("dedup_primary_alignments",  "qpass_primary_alignments",  "dedup_primary_alignments_%"),
    ("dedup_primary_alignments",  "dedup_total_alignments",    "dedup_pct_primary"),
]

OUTPUT_ROW_ORDER = [
    "total_reads",
    "clipped_reads",
    "clipped_reads_%",
    "filtered_out",
    "filtered_out_%",
    "filter_kept",
    "filter_kept_%",
    "genome_aligned_once",
    "genome_aligned_many",
    "genome_unaligned",
    "genome_primary_alignments",
    "genome_primary_alignments_%",
    "genome_secondary_alignments",
    "genome_total_alignments",
    "genome_pct_primary",
    "qpass_primary_alignments",
    "qpass_primary_alignments_%",
    "qpass_secondary_alignments",
    "qpass_total_alignments",
    "qpass_pct_primary",
    "dedup_primary_alignments",
    "dedup_primary_alignments_%",
    "dedup_secondary_alignments",
    "dedup_total_alignments",
    "dedup_pct_primary",
]


def _safe_pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    num = pd.to_numeric(numerator, errors="coerce").fillna(0)
    den = pd.to_numeric(denominator, errors="coerce").fillna(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        pct = np.where(den == 0, 0.0, 100.0 * num / den)
    return pd.Series(np.round(pct, 2), index=numerator.index)


def genome_stats_percentage(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(input_csv, header=0, index_col=0)

    for num_row, denom_row, derived_row in PERCENTAGE_ROWS:
        missing = [r for r in (num_row, denom_row) if r not in df.index]
        if missing:
            raise KeyError(
                f"Cannot compute {derived_row}: missing row(s) {missing} in "
                f"{input_csv}. Found rows: {list(df.index)}"
            )
        df.loc[derived_row] = _safe_pct(df.loc[num_row], df.loc[denom_row])

    extras = [r for r in df.index if r not in OUTPUT_ROW_ORDER]
    final_order = [r for r in OUTPUT_ROW_ORDER if r in df.index] + extras
    df = df.loc[final_order]
    df.to_csv(output_csv)
    return df
