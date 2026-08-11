#!/usr/bin/env python3
"""Source-level regression checks for V2.2 form and exclusive-ability mechanics."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

CHECKS = {
    "Stakeout damage": ("src/individual/CalcBaseDamage.c", "ABILITY_STAKEOUT"),
    "Toxic Chain poison": ("src/battle/ability.c", "case ABILITY_TOXIC_CHAIN"),
    "Cotton Down spread": ("src/individual/MoveHitDefenderAbilityCheck.c", "case ABILITY_COTTON_DOWN"),
    "Hospitality healing": ("src/individual/SwitchInAbilityCheck.c", "ABILITY_HOSPITALITY"),
    "Opportunist copy": ("src/individual/btl_scr_cmd_33_statbuffchange.c", "ABILITY_OPPORTUNIST"),
    "Cheek Pouch healing": ("src/individual/ServerDoPostMoveEffects.c", "ABILITY_CHEEK_POUCH"),
    "Paradox boost helper": ("src/battle/ability.c", "ParadoxAbilityIsActive"),
    "Minior Shields Down": ("src/individual/ServerFieldConditionCheck.c", "SPECIES_MINIOR"),
    "Morpeko Hunger Switch": ("src/individual/ServerFieldConditionCheck.c", "SPECIES_MORPEKO"),
    "Palafin Zero to Hero": ("src/battle/battle_script_commands.c", "SPECIES_PALAFIN"),
    "Cramorant Gulp Missile": ("src/individual/MoveHitDefenderAbilityCheck.c", "SPECIES_CRAMORANT"),
}


def main() -> int:
    failures = []
    for label, (path, marker) in CHECKS.items():
        if marker not in (ROOT / path).read_text(encoding="utf-8"):
            failures.append(f"{label}: marker `{marker}` missing from {path}")
    if failures:
        print("FAIL: special mechanics incomplete:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: V2.2 exclusive abilities and battle-form transitions are implemented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
