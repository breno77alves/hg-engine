#!/usr/bin/env python3
"""Validate the generated v2.2 documentation set and its shared data sources."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXPECTED = {
    "Ability Changes.pdf",
    "Evolution Changes.pdf",
    "Features,QoL, and Known Bugs.pdf",
    "Gym Leader Teams and Level Caps.pdf",
    "New Item Locations.pdf",
    "Pokemon Availability.pdf",
    "Pokemon Type Changes.pdf",
    "Wild Encounters.pdf",
}


def main() -> int:
    failures: list[str] = []
    actual = {path.name for path in DOCS.glob("*.pdf")}
    if actual != EXPECTED:
        failures.append(f"PDF set mismatch: expected {sorted(EXPECTED)}, got {sorted(actual)}")
    for name in EXPECTED:
        path = DOCS / name
        if not path.exists() or path.stat().st_size < 1000:
            failures.append(f"missing or empty PDF: {name}")
        elif path.read_bytes()[:5] != b"%PDF-":
            failures.append(f"invalid PDF signature: {name}")

    config = json.loads((ROOT / "armips/data/v22_availability.json").read_text(encoding="utf-8"))
    with (DOCS / "v22_availability_manifest.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if sum(row["scope"] == "species" for row in rows) != 1025:
        failures.append("availability manifest does not contain 1025 species rows")
    if sum(row["scope"] == "functional_form" for row in rows) != 61:
        failures.append("availability manifest does not contain 61 functional-form rows")
    if config["notes"].get("frame_rate") != "60 FPS hacks remain disabled":
        failures.append("documentation source does not preserve the disabled 60 FPS contract")

    generator = (ROOT / "scripts/generate_v22_pdfs.py").read_text(encoding="utf-8")
    for marker in ("MANIFEST", "CONFIG", "armips/data/encounters.s", "armips/data/evodata.s", "armips/data/mondata.s"):
        if marker not in generator:
            failures.append(f"PDF generator is not tied to source marker: {marker}")

    if failures:
        print("FAIL: v2.2 documentation:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: 8 PDFs, 1025 species rows, and 61 functional forms share the v2.2 sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
