#!/usr/bin/env python3
"""Lock documented stable substitutions and implemented exclusive abilities."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

SUBSTITUTIONS = {
    "SPECIES_YAMPER": "ABILITY_PICKUP",
    "SPECIES_TATSUGIRI": "ABILITY_STORM_DRAIN",
    "SPECIES_ORICORIO": "ABILITY_OWN_TEMPO",
    "SPECIES_ORICORIO_POM_POM": "ABILITY_OWN_TEMPO",
    "SPECIES_ORICORIO_PAU": "ABILITY_OWN_TEMPO",
    "SPECIES_ORICORIO_SENSU": "ABILITY_OWN_TEMPO",
    "SPECIES_STUNFISK_GALARIAN": "ABILITY_MAGNET_PULL",
    "SPECIES_TERAPAGOS": "ABILITY_FILTER",
}


def main() -> int:
    mondata = (ROOT / "armips/data/mondata.s").read_text(encoding="utf-8")
    failures: list[str] = []
    for species, ability in SUBSTITUTIONS.items():
        match = re.search(
            rf"^mondata\s+{species},.*?(?=^mondata\s+|\Z)",
            mondata, re.MULTILINE | re.DOTALL,
        )
        if not match or f"abilities {ability}, ABILITY_NONE" not in match.group(0):
            failures.append(f"{species} must use {ability}")

    config = (ROOT / "armips/data/v22_availability.json").read_text(encoding="utf-8")
    for species, ability in SUBSTITUTIONS.items():
        if species not in config or ability not in config:
            failures.append(f"substitution missing from manifest source: {species} -> {ability}")

    if failures:
        print("FAIL: ability policy mismatch:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: every high-risk exclusive ability has its documented stable substitution")
    return 0


if __name__ == "__main__":
    sys.exit(main())
