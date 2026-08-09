#!/usr/bin/env python3

"""Regression contracts for Capture EXP and the hard level cap."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
BATTLE_COMMANDS = ROOT / "src/battle/battle_script_commands.c"
POKEMON = ROOT / "src/pokemon.c"
HOOKS = ROOT / "hooks"


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


def try_level_up(current_level: int, experience: int, cap: int) -> tuple[int, int]:
    """Model the cap boundary enforced by Pokemon_TryLevelUp."""

    def threshold(level: int) -> int:
        return level**3

    experience = min(experience, threshold(cap))
    next_level = current_level + 1
    if next_level > cap:
        return current_level, experience
    if experience >= threshold(next_level):
        return next_level, experience
    return current_level, experience


def main() -> int:
    try:
        config = CONFIG.read_text(encoding="utf-8")
        battle_commands = BATTLE_COMMANDS.read_text(encoding="utf-8")
        pokemon = POKEMON.read_text(encoding="utf-8")
        hooks = HOOKS.read_text(encoding="utf-8")

        assert re.search(
            r"^\s*#define\s+IMPLEMENT_CAPTURE_EXPERIENCE\b", config, re.MULTILINE
        ), (
            "Capture EXP must remain enabled"
        )
        assert re.search(
            r"^\s*#define\s+IMPLEMENT_LEVEL_CAP\b", config, re.MULTILINE
        ), (
            "the hard level cap must remain enabled"
        )
        assert not re.search(r"^\s*#define\s+UNCAP_CANDIES_FROM_LEVEL_CAP\b", config, re.MULTILINE), (
            "the requested hard-cap policy must not be bypassed by candies"
        )

        capture = function_body(
            battle_commands, "Task_DistributeExp_capture_experience"
        )
        distributor = function_body(battle_commands, "Task_DistributeExp_Extend")
        level_up = function_body(pokemon, "Pokemon_TryLevelUp")

        assert re.search(r"\bTask_DistributeExp_Extend\s*\(\s*arg0\s*,\s*expcalc\s*\)", capture), (
            "Capture EXP must reuse the shared EXP distributor"
        )
        assert re.search(r"\bTask_DistributeExp\s*\(\s*arg0\s*,\s*work\s*\)", distributor), (
            "the extended distributor must return to the engine EXP task"
        )
        assert "trackPartyExperience = 0" not in capture, (
            "the final upstream fix forbids resetting the capture tracker here"
        )
        assert re.search(r"arm9\s+Pokemon_TryLevelUp\s+02070DB4\s+1", hooks), (
            "all engine level-up attempts must pass through the capped implementation"
        )
        assert re.search(r"0012\s+ImplementLevelCap_hook\s+02245A28\s+3", hooks), (
            "battle EXP must keep the active-cap eligibility hook"
        )
        assert re.search(
            r"maxexp\s*=\s*GetExpByGrowthRateAndLevel\([^;]*GetLevelCap\(\)\)",
            level_up,
        ), "the maximum stored EXP must be derived from the active cap"
        assert re.search(
            r"if\s*\(exp\s*>\s*maxexp\).*?SetMonData\([^;]*MON_DATA_EXPERIENCE",
            level_up,
            re.DOTALL,
        ), "overflow EXP must be clamped before another level-up is considered"
        assert re.search(
            r"if\s*\(level\s*>\s*GetLevelCap\(\)\)\s*return\s+FALSE",
            level_up,
        ), "a level above the active cap must be rejected"

        # A large capture award may reach the cap, but may neither store EXP nor
        # raise the Pokemon beyond that boundary.
        assert try_level_up(64, 1_000_000, 65) == (65, 65**3)
        assert try_level_up(65, 1_000_000, 65) == (65, 65**3)
        assert try_level_up(49, 50**3 - 1, 50) == (49, 50**3 - 1)
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Capture EXP shares the engine path and obeys the hard level cap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
