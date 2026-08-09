#!/usr/bin/env python3

"""Preservation contracts for the Generations trainer move/ability surface."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MOVE_CONSTANTS = ROOT / "include/constants/moves.h"
MOVE_DATA = ROOT / "armips/data/moves.s"
TRAINERS = ROOT / "armips/data/trainers/trainers.s"
MON_DATA = ROOT / "armips/data/mondata.s"
DAMAGE = ROOT / "src/individual/CalcBaseDamage.c"


def move_numbers(source: str) -> dict[str, int]:
    return {
        name: int(number)
        for name, number in re.findall(
            r"^#define\s+(MOVE_[A-Z0-9_]+)\s+(\d+)", source, re.MULTILINE
        )
    }


def move_block(source: str, move: str) -> str:
    match = re.search(
        rf"^movedata\s+{re.escape(move)},.*?(?=^movedata\s+|\Z)",
        source,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing movedata block for {move}")
    return match.group(0)


def main() -> int:
    try:
        constants = move_numbers(MOVE_CONSTANTS.read_text(encoding="utf-8"))
        moves = MOVE_DATA.read_text(encoding="utf-8")
        trainers = TRAINERS.read_text(encoding="utf-8")
        mon_data = MON_DATA.read_text(encoding="utf-8")
        damage = DAMAGE.read_text(encoding="utf-8")

        trainer_moves = set(re.findall(r"\bMOVE_[A-Z0-9_]+\b", trainers))
        assert len(trainer_moves) == 358, "trainer move surface changed unexpectedly"
        modern_trainer_moves = sorted(
            (move for move in trainer_moves if constants.get(move, 0) > 467),
            key=constants.get,
        )
        assert modern_trainer_moves == ["MOVE_HONE_CLAWS", "MOVE_HEX"]

        hone_claws = move_block(moves, "MOVE_HONE_CLAWS")
        assert "battleeffect MOVE_EFFECT_ATK_ACC_UP" in hone_claws
        assert "pss SPLIT_STATUS" in hone_claws

        hex_block = move_block(moves, "MOVE_HEX")
        assert "battleeffect MOVE_EFFECT_DOUBLE_DAMAGE_ON_STATUS" in hex_block
        assert "basepower 65" in hex_block
        assert re.search(
            r"case MOVE_HEX:\s*if \(sp->battlemon\[defender\]\.condition & STATUS_ALL\)\s*"
            r"\{\s*movepower \*= 2;",
            damage,
        ), "Hex must double power against a major-status target"

        trainer_species = set(re.findall(r"\bSPECIES_[A-Z0-9_]+\b", trainers))
        assert len(trainer_species) == 322, "trainer species surface changed unexpectedly"
        abilities: set[str] = set()
        for species in trainer_species:
            record = re.search(
                rf"^mondata\s+{re.escape(species)},.*?(?=^mondata\s+|\Z)",
                mon_data,
                re.MULTILINE | re.DOTALL,
            )
            if not record:
                continue
            slots = re.search(
                r"^\s*abilities\s+(ABILITY_[A-Z0-9_]+),\s*(ABILITY_[A-Z0-9_]+)",
                record.group(0),
                re.MULTILINE,
            )
            if slots:
                abilities.update(slots.groups())
        abilities.discard("ABILITY_NONE")
        assert len(abilities) == 126, "trainer normal-ability surface changed unexpectedly"
    except (AssertionError, KeyError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: trainer move and normal-ability surface remains audited and stable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
