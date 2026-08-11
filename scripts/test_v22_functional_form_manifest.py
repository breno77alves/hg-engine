#!/usr/bin/env python3
"""Validate the shared V2.2 manifest covers species and supported functional forms."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "armips/data/v22_availability.json"
MANIFEST = ROOT / "docs/v22_availability_manifest.csv"


def main() -> int:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    with MANIFEST.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    species_rows = [row for row in rows if row.get("scope") == "species"]
    form_rows = [row for row in rows if row.get("scope") == "functional_form"]
    expected_forms = {
        entry.get("form_name", entry.get("evolution_source"))
        for entry in config.get("functional_form_sources", []) + config.get("item_form_sources", [])
    }
    actual_forms = {row.get("display_name") for row in form_rows}
    failures: list[str] = []
    if len(species_rows) != 1025:
        failures.append(f"manifest has {len(species_rows)} species rows, expected 1025")
    missing = sorted(expected_forms - actual_forms)
    if missing:
        failures.append("functional forms missing from manifest: " + ", ".join(missing))

    required_item_forms = {
        "Oricorio (Pom-Pom Style)", "Silvally (Fire type)",
        "Ogerpon (Wellspring Mask)", "Urshifu (Rapid Strike Style)",
    }
    absent = sorted(required_item_forms - actual_forms)
    if absent:
        failures.append("explicit item forms missing: " + ", ".join(absent))

    if failures:
        print("FAIL: " + "\n".join(failures), file=sys.stderr)
        return 1
    print(f"PASS: manifest covers 1025 species and {len(form_rows)} functional forms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
