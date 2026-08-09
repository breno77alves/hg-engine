#!/usr/bin/env python3

"""Regression contracts for Defiant and Competitive activation caps."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = ROOT / "src/battle/battle_script_commands.c"


def activates(ability: str, attack_stage: int, special_attack_stage: int) -> bool:
    if ability == "DEFIANT":
        return attack_stage < 12
    if ability == "COMPETITIVE":
        return special_attack_stage < 12
    return False


def main() -> int:
    try:
        source = COMMANDS.read_text(encoding="utf-8")
        start = source.index("BOOL btl_scr_cmd_FF_checkcanactivatedefiantorcompetitive")
        end = source.index("#ifdef DEBUG_ENTRY_HAZARD_PRINTS", start)
        command = source[start:end]

        outer_condition = command[: command.index("switch (GetBattlerAbility")]
        assert not re.search(
            r"states\[STAT_ATTACK\]\s*<\s*12", outer_condition
        ), "the shared activation gate must not use Defiant's Attack cap"
        assert re.search(
            r"case ABILITY_DEFIANT:.*?states\[STAT_ATTACK\]\s*<\s*12",
            command,
            re.DOTALL,
        ), "Defiant must retain its own Attack-stage cap"
        assert re.search(
            r"case ABILITY_COMPETITIVE:.*?states\[STAT_SPATK\]\s*<\s*12",
            command,
            re.DOTALL,
        ), "Competitive must retain its own Special Attack-stage cap"

        assert activates("DEFIANT", 11, 12)
        assert not activates("DEFIANT", 12, 6)
        assert activates("COMPETITIVE", 12, 11)
        assert not activates("COMPETITIVE", 6, 12)
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Defiant and Competitive use their independent stat caps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
