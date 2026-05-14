from __future__ import annotations

import csv
import sys
from pathlib import Path


def _read_first_int(path: Path) -> str:
    with path.open() as fh:
        return fh.read().strip().split()[0]


def update_dedup_counts(
    dedup_total_file: Path,
    dedup_primary_file: Path,
    dedup_secondary_file: Path,
    input_csv: Path,
    output_csv: Path,
) -> int:
    """Override dedup_* alignment-count rows in a per-sample merged stats CSV."""
    overrides = {
        "dedup_total_alignments":     _read_first_int(dedup_total_file),
        "dedup_primary_alignments":   _read_first_int(dedup_primary_file),
        "dedup_secondary_alignments": _read_first_int(dedup_secondary_file),
    }

    if not input_csv.exists():
        print(f"Error: input CSV {input_csv} not found", file=sys.stderr)
        return 1

    with input_csv.open(newline="") as fh:
        rows = list(csv.reader(fh))

    for row in rows[1:]:
        if row and len(row) >= 2 and row[0] in overrides:
            row[1] = overrides[row[0]]

    with output_csv.open("w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return 0
