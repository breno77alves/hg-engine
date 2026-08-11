#!/usr/bin/env python3
"""Lock stable implemented substitutes for obtainable non-operational abilities."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

NORMAL_REPLACEMENTS = {
    "SPECIES_ARBOLIVA": "ABILITY_GRASSY_SURGE",
    "SPECIES_KORAIDON": "ABILITY_DROUGHT",
    "SPECIES_MIRAIDON": "ABILITY_ELECTRIC_SURGE",
    "SPECIES_GHOLDENGO": "ABILITY_MAGIC_BOUNCE",
    "SPECIES_PECHARUNT": "ABILITY_POISON_TOUCH",
}

HIDDEN_REPLACEMENTS = {
    "SPECIES_FLAMIGO": "ABILITY_DOWNLOAD",
    "SPECIES_TAUROS_COMBAT": "ABILITY_SHEER_FORCE",
    "SPECIES_TAUROS_BLAZE": "ABILITY_SHEER_FORCE",
    "SPECIES_TAUROS_AQUA": "ABILITY_SHEER_FORCE",
}

OPERATIONAL_MARKERS = {
    "ABILITY_GRASSY_SURGE": "src/individual/SwitchInAbilityCheck.c",
    "ABILITY_DROUGHT": "src/individual/SwitchInAbilityCheck.c",
    "ABILITY_ELECTRIC_SURGE": "src/individual/SwitchInAbilityCheck.c",
    "ABILITY_MAGIC_BOUNCE": "src/battle/ability.c",
    "ABILITY_POISON_TOUCH": "src/battle/ability.c",
    "ABILITY_DOWNLOAD": "src/individual/SwitchInAbilityCheck.c",
    "ABILITY_SHEER_FORCE": "src/individual/CalcBaseDamage.c",
}


def block(source: str, species: str) -> str:
    match = re.search(
        rf"^mondata\s+{species},.*?(?=^mondata\s+|\Z)",
        source,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else ""


def main() -> int:
    mondata = (ROOT / "armips/data/mondata.s").read_text(encoding="utf-8")
    hidden = (ROOT / "data/HiddenAbilityTable.c").read_text(encoding="utf-8")
    failures: list[str] = []

    for species, ability in NORMAL_REPLACEMENTS.items():
        if not re.search(rf"^\s+abilities\s+{ability},\s+ABILITY_NONE", block(mondata, species), re.MULTILINE):
            failures.append(f"{species} must use {ability}")
    for species, ability in HIDDEN_REPLACEMENTS.items():
        if not re.search(rf"\[{species}\s*\]\s*=\s*{ability},", hidden):
            failures.append(f"{species} hidden ability must use {ability}")
    for ability, path in OPERATIONAL_MARKERS.items():
        if ability not in (ROOT / path).read_text(encoding="utf-8"):
            failures.append(f"{ability} lacks its operational marker in {path}")

    if failures:
        print("FAIL: v2.2.1 ability substitution policy mismatch:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: every obtainable known non-operational ability uses an implemented substitute")
    return 0


if __name__ == "__main__":
    sys.exit(main())
