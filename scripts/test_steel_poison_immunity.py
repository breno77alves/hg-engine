#!/usr/bin/env python3

"""Regression contracts for Poison and Steel type poison immunity."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
BEFORE_MOVE = ROOT / "src/individual/BattleController_BeforeMove.c"


def function_body(source: str, name: str) -> str:
    start = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", source)
    assert start, f"function not found: {name}"
    depth = 0
    for index in range(start.end() - 1, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start.start() : index + 1]
    raise AssertionError(f"unterminated function: {name}")


def poison_move_is_immune(defender_types: set[str], attacker_has_corrosion: bool) -> bool:
    return bool(defender_types & {"POISON", "STEEL"}) and not attacker_has_corrosion


def main() -> int:
    try:
        source = BEFORE_MOVE.read_text(encoding="utf-8")
        immunity_check = function_body(
            source, "BattleController_CheckTypeBasedMoveConditionImmunities2"
        )

        assert re.search(
            r"MOVE_EFFECT_STATUS_POISON\s*\|\|\s*"
            r"moveEffect\s*==\s*MOVE_EFFECT_STATUS_BADLY_POISON.*?"
            r"HasType\(ctx,\s*defender,\s*TYPE_POISON\)\s*\|\|\s*"
            r"HasType\(ctx,\s*defender,\s*TYPE_STEEL\).*?"
            r"ABILITY_CORROSION",
            immunity_check,
            re.DOTALL,
        ), "the BeforeMove immunity gate must include both Poison and Steel types"

        assert poison_move_is_immune({"POISON"}, False)
        assert poison_move_is_immune({"STEEL"}, False)
        assert poison_move_is_immune({"STEEL", "FAIRY"}, False)
        assert not poison_move_is_immune({"STEEL"}, True)
        assert not poison_move_is_immune({"WATER"}, False)
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Poison and Steel immunity is enforced unless Corrosion applies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
