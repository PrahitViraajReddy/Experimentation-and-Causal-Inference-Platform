#!/usr/bin/env python3
"""Download and validate the Cookie Cats reference dataset.

The CSV is downloaded on demand instead of being committed to Git because its
upstream redistribution terms are not clearly specified and raw data does not
belong in the application image.
"""
from __future__ import annotations

import csv
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "data" / "raw" / "cookie_cats.csv"
SOURCE_URL = (
    "https://raw.githubusercontent.com/"
    "ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats/master/cookie_cats.csv"
)
EXPECTED_COLUMNS = [
    "userid",
    "version",
    "sum_gamerounds",
    "retention_1",
    "retention_7",
]
EXPECTED_ROWS = 90_189


def validate_csv(path: Path) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                f"Unexpected columns: {reader.fieldnames!r}; expected {EXPECTED_COLUMNS!r}"
            )

        rows = 0
        seen_ids: set[str] = set()
        versions: set[str] = set()
        for row in reader:
            rows += 1
            user_id = row["userid"]
            if not user_id or user_id in seen_ids:
                raise ValueError(f"Missing or duplicate userid at data row {rows}")
            seen_ids.add(user_id)
            versions.add(row["version"])
            if row["version"] not in {"gate_30", "gate_40"}:
                raise ValueError(f"Unexpected experiment arm: {row['version']!r}")
            if int(row["sum_gamerounds"]) < 0:
                raise ValueError("sum_gamerounds cannot be negative")
            for column in ("retention_1", "retention_7"):
                if row[column].strip().lower() not in {"true", "false", "0", "1"}:
                    raise ValueError(f"Invalid boolean in {column}: {row[column]!r}")

    if rows != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS:,} data rows; found {rows:,}")
    if versions != {"gate_30", "gate_40"}:
        raise ValueError(f"Expected both experiment arms; found {versions!r}")


def main() -> int:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    if DESTINATION.exists():
        try:
            validate_csv(DESTINATION)
            print(f"Dataset already exists and passed validation: {DESTINATION}")
            return 0
        except (OSError, ValueError, csv.Error) as error:
            print(f"Existing dataset failed validation: {error}", file=sys.stderr)
            print("Move or delete it before downloading a fresh copy.", file=sys.stderr)
            return 1

    temporary = DESTINATION.with_suffix(".csv.part")
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "experimentation-causal-platform/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        validate_csv(temporary)
        temporary.replace(DESTINATION)
    except (OSError, urllib.error.URLError, ValueError, csv.Error) as error:
        temporary.unlink(missing_ok=True)
        print(f"Dataset download/validation failed: {error}", file=sys.stderr)
        return 1

    print(f"Downloaded and validated {EXPECTED_ROWS:,} rows: {DESTINATION}")
    print("Review docs/datasets.md for provenance and usage notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
