#!/usr/bin/env python3
"""Lock the V2.2 evolution methods that replace unavailable modern mechanics."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


EXPECTED = {
    "SPECIES_KARRABLAST": ("EVO_LEVEL", "30", "SPECIES_ESCAVALIER"),
    "SPECIES_SHELMET": ("EVO_LEVEL", "30", "SPECIES_ACCELGOR"),
    "SPECIES_PAWMO": ("EVO_LEVEL", "32", "SPECIES_PAWMOT"),
    "SPECIES_BRAMBLIN": ("EVO_LEVEL", "32", "SPECIES_BRAMBLEGHAST"),
    "SPECIES_RELLOR": ("EVO_LEVEL", "32", "SPECIES_RABSCA"),
    "SPECIES_FINIZEN": ("EVO_LEVEL", "38", "SPECIES_PALAFIN"),
    "SPECIES_GIMMIGHOUL": ("EVO_ITEM_DAY", "ITEM_AMULET_COIN", "SPECIES_GHOLDENGO"),
    "SPECIES_MELTAN": ("EVO_LEVEL", "40", "SPECIES_MELMETAL"),
    "SPECIES_YAMPER": ("EVO_LEVEL", "25", "SPECIES_BOLTUND"),
}


def main() -> int:
    text = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    failures: list[str] = []
    for species, (method, parameter, target) in EXPECTED.items():
        match = re.search(
            rf"^evodata\s+{species}\s*(.*?)(?=^terminateevodata)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        expected = f"evolution {method}, {parameter}, {target}"
        if not match or expected not in match.group(1):
            failures.append(f"{species}: expected `{expected}`")

    if failures:
        print("FAIL: adapted evolution contract mismatch:\n" + "\n".join(failures), file=sys.stderr)
        return 1

    print("PASS: all unavailable modern evolution methods have stable HGSS alternatives")
    return 0


if __name__ == "__main__":
    sys.exit(main())
