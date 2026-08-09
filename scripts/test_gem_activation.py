#!/usr/bin/env python3

"""Regression contracts for one-use type Gem activation."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
BEFORE_MOVE = ROOT / "src/individual/BattleController_BeforeMove.c"


def gem_activates(
    move_split: str,
    gem_type: str,
    move_type: str,
    move_hits: bool,
) -> bool:
    return (
        move_split != "STATUS"
        and gem_type == move_type
        and move_hits
    )


def main() -> int:
    try:
        source = BEFORE_MOVE.read_text(encoding="utf-8")
        start = source.index("case BEFORE_MOVE_STATE_GEM_ACTIVATION:")
        end = source.index("case BEFORE_MOVE_STATE_TRIGGER_STRONG_WINDS:", start)
        gem_state = source[start:end]

        assert re.search(
            r"HeldItemHoldEffectGet\([^;]*HOLD_EFFECT_POWERING_UP_MOVE_ONCE.*?"
            r"moveTbl\[ctx->current_move_index\]\.split\s*!=\s*SPLIT_STATUS.*?"
            r"BattleItemDataGet\([^;]*==\s*ctx->move_type.*?"
            r"IsAnyBattleMonHit\(ctx\)",
            gem_state,
            re.DOTALL,
        ), "Gem activation must explicitly reject status moves"

        assert not gem_activates("STATUS", "PSYCHIC", "PSYCHIC", True)
        assert gem_activates("SPECIAL", "PSYCHIC", "PSYCHIC", True)
        assert gem_activates("PHYSICAL", "FIRE", "FIRE", True)
        assert not gem_activates("SPECIAL", "PSYCHIC", "WATER", True)
        assert not gem_activates("SPECIAL", "PSYCHIC", "PSYCHIC", False)
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Gems activate only for matching damaging moves that hit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
