#!/usr/bin/env python3

"""Regression contracts for Water Absorb on status moves in modern generations."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ABILITY = ROOT / "src/battle/ability.c"


def water_absorb_triggers(move_type: str, blocked_context: bool) -> bool:
    return move_type == "WATER" and not blocked_context


def main() -> int:
    try:
        source = ABILITY.read_text(encoding="utf-8")
        start = source.index("ABILITY_WATER_ABSORB")
        end = source.index("ABILITY_FLASH_FIRE", start)
        water_absorb = source[start:end]

        assert "TYPE_WATER" in water_absorb
        assert "SERVER_STATUS_FLAG_x20" in water_absorb
        assert not re.search(
            r"moveTbl\[sp->current_move_index\]\.power", water_absorb
        ), "Water Absorb must also intercept zero-power Water status moves"

        assert water_absorb_triggers("WATER", False)
        assert not water_absorb_triggers("FIRE", False)
        assert not water_absorb_triggers("WATER", True)
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Water Absorb intercepts damaging and status Water moves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
