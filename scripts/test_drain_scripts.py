#!/usr/bin/env python3

"""Regression contracts for half- and three-quarter drain battle scripts."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
HALF_DRAIN = (
    ROOT
    / "data/battle_scripts/subscripts/subscript_0024_DRAIN_HALF_DAMAGE_DEALT.s"
)
THREE_QUARTER_DRAIN = (
    ROOT
    / "data/battle_scripts/subscripts/subscript_0437_DRAIN_THREE_QUARTERS.s"
)


def require(source: str, pattern: str, message: str) -> None:
    if not re.search(pattern, source, re.MULTILINE):
        raise AssertionError(message)


def main() -> int:
    half = HALF_DRAIN.read_text(encoding="utf-8")
    three_quarter = THREE_QUARTER_DRAIN.read_text(encoding="utf-8")

    try:
        require(
            half,
            r"CompareVarToValue\s+OPCODE_GT,\s*BSCRIPT_VAR_HP_CALC,\s*-1,",
            "half drain must reject zero/positive HP_CALC but accept one damage",
        )
        require(
            three_quarter,
            r"CompareVarToValue\s+OPCODE_GT,\s*BSCRIPT_VAR_HP_CALC,\s*-1,",
            "three-quarter drain must reject zero/positive HP_CALC",
        )

        multiply = three_quarter.index(
            "UpdateVar OPCODE_MUL, BSCRIPT_VAR_HP_CALC, 3"
        )
        divide = three_quarter.index("DivideVarByValue BSCRIPT_VAR_HP_CALC, 4")
        assert multiply < divide, "three-quarter drain must multiply before division"

        for name, source in (("half", half), ("three-quarter", three_quarter)):
            require(source, r"HOLD_EFFECT_LEECH_BOOST", f"{name} drain lost Big Root")
            require(source, r"ABILITY_LIQUID_OOZE", f"{name} drain lost Liquid Ooze")
            require(
                source,
                r"BMON_DATA_HEAL_BLOCK_TURNS",
                f"{name} drain lost Generations Heal Block handling",
            )
    except (AssertionError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: drain scripts handle one damage and preserve interactions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
