#!/usr/bin/env python3
"""Lock representative lore and habitat placements for the V2.2 rare roster."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "SPECIES_ARCEUS": "Mt. Silver (Top, snowy area)",
    "SPECIES_ARTICUNO": "Seafoam Islands 1F",
    "SPECIES_ZAPDOS": "Rock Tunnel 1F",
    "SPECIES_MOLTRES": "Mt. Silver (Moltres room)",
    "SPECIES_MEWTWO": "Cerulean Cave 1F",
    "SPECIES_LUGIA": "Whirl Islands B3F (Ledge overlooking Lugia room)",
    "SPECIES_HO_OH": "Bell Tower 10F",
}


def main() -> int:
    config = json.loads((ROOT / "armips/data/v22_availability.json").read_text(encoding="utf-8"))
    sources = {entry["species"]: entry for entry in config["encounter_sources"]}
    failures: list[str] = []
    for species, location in EXPECTED.items():
        actual = sources.get(species, {}).get("location")
        if actual != location:
            failures.append(f"{species}: expected {location}, got {actual}")
        elif sources[species]["chance"] != 1 or sources[species]["period"] != "all":
            failures.append(f"{species}: habitat source is not 1% in all periods")
    if failures:
        print("FAIL: habitat distribution:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: iconic legends and rare habitats are anchored at 1% in every period")
    return 0


if __name__ == "__main__":
    sys.exit(main())
