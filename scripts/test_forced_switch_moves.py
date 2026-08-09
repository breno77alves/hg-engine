#!/usr/bin/env python3

"""Regression contracts for damaging forced-switch moves."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MOVE_EFFECTS_H = ROOT / "include/constants/move_effects.h"
MOVE_EFFECTS_INC = ROOT / "asm/include/move_effects.inc"
MOVES = ROOT / "armips/data/moves.s"
EFFECT_SCRIPT = (
    ROOT / "data/battle_scripts/effects/effect_script_0372_FORCE_SWITCH_HIT.s"
)
MOVE_END = ROOT / "src/individual/BattleController_MoveEnd.c"
BATTLE_H = ROOT / "include/battle.h"
FORCE_OUT = (
    ROOT
    / "data/battle_scripts/subscripts/subscript_0091_FORCE_TARGET_TO_SWITCH_OR_FLEE.s"
)


def move_block(source: str, move: str) -> str:
    match = re.search(rf"movedata {move},.*?terminatedata", source, re.DOTALL)
    assert match, f"move-data entry not found for {move}"
    return match.group(0)


def should_force_switch(
    effect: int,
    attacker_hp: int,
    defender_hp: int,
    physical_damage: int,
    special_damage: int,
    substitute: bool,
    already_processed: bool,
) -> bool:
    return (
        effect == 372
        and attacker_hp > 0
        and defender_hp > 0
        and bool(physical_damage or special_damage)
        and not substitute
        and not already_processed
    )


def main() -> int:
    try:
        effects_h = MOVE_EFFECTS_H.read_text(encoding="utf-8")
        effects_inc = MOVE_EFFECTS_INC.read_text(encoding="utf-8")
        moves = MOVES.read_text(encoding="utf-8")
        effect_script = EFFECT_SCRIPT.read_text(encoding="utf-8")
        move_end = MOVE_END.read_text(encoding="utf-8")
        battle_h = BATTLE_H.read_text(encoding="utf-8")
        force_out = FORCE_OUT.read_text(encoding="utf-8")

        assert re.search(
            r"#define MOVE_EFFECT_FORCE_SWITCH_HIT\s+372", effects_h
        ), "C move-effect constants must assign forced-switch hits ID 372"
        assert re.search(
            r"#define MAX_BASE_MOVE_EFFECT_NUM\s+372", effects_h
        ), "C maximum move-effect ID must include forced-switch hits"
        assert re.search(
            r"\.equ MOVE_EFFECT_FORCE_SWITCH_HIT,\s*372", effects_inc
        ), "assembly move-effect constants must assign forced-switch hits ID 372"
        assert re.search(
            r"\.equ MAX_BASE_MOVE_EFFECT_NUM,\s*372", effects_inc
        ), "assembly maximum move-effect ID must include forced-switch hits"

        for move in ("MOVE_CIRCLE_THROW", "MOVE_DRAGON_TAIL"):
            block = move_block(moves, move)
            assert re.search(
                r"\bbattleeffect\s+MOVE_EFFECT_FORCE_SWITCH_HIT\b", block
            ), f"{move} must use the damaging forced-switch effect"
            assert re.search(r"\bpriority\s+-6\b", block), (
                f"{move} must retain -6 priority"
            )
            assert "FLAG_UNUSABLE_UNIMPLEMENTED" not in block, (
                f"{move} must remain selectable"
            )

        assert re.fullmatch(
            r"\s*\.include \"asm/include/battle_commands\.inc\"\s*"
            r"\.data\s*_000:\s*CalcCrit\s*CalcDamage\s*End\s*",
            effect_script,
        ), "forced-switch move effect must only calculate critical hits and damage"

        assert re.search(
            r"forceSwitchProcessedFlag\s*:\s*1", battle_h
        ), "move state must expose a one-execution forced-switch guard"
        assert re.search(
            r"moveTbl\[ctx->current_move_index\]\.effect\s*==\s*"
            r"MOVE_EFFECT_FORCE_SWITCH_HIT",
            move_end,
        ), "MoveEnd must dispatch forced switching by effect, not by move ID"
        for guard in (
            r"ctx->attack_client\s*!=\s*BATTLER_NONE",
            r"ctx->defence_client\s*!=\s*BATTLER_NONE",
            r"ctx->battlemon\[ctx->attack_client\]\.hp\s*>\s*0",
            r"ctx->battlemon\[ctx->defence_client\]\.hp\s*>\s*0",
            r"oneSelfFlag\[ctx->defence_client\]\.physical_damage",
            r"oneSelfFlag\[ctx->defence_client\]\.special_damage",
            r"STATUS2_SUBSTITUTE",
            r"!ctx->oneTurnFlag\[ctx->attack_client\]\.forceSwitchProcessedFlag",
        ):
            assert re.search(guard, move_end), f"MoveEnd is missing guard: {guard}"
        assert re.search(
            r"forceSwitchProcessedFlag\s*=\s*1;.*?"
            r"LoadBattleSubSeqScript\([^;]*SUB_SEQ_FORCE_OUT\)",
            move_end,
            re.DOTALL,
        ), "MoveEnd must latch the guard before starting the forced-switch script"
        assert re.search(
            r"forceSwitchProcessedFlag\s*=\s*0;.*?BattleStructureInit\(ctx\)",
            move_end,
            re.DOTALL,
        ), "MoveEnd must clear the forced-switch guard after the move completes"

        battle_type_check = re.search(
            r"CompareVarToValue OPCODE_EQU, BSCRIPT_VAR_BATTLE_TYPE,\s*([^,\n]+),\s*_097",
            force_out,
        )
        assert battle_type_check, "forced-switch script must retain its battle-type gate"
        rejected_types = battle_type_check.group(1)
        assert "BATTLE_TYPE_AI" in rejected_types
        assert "BATTLE_TYPE_MULTI" in rejected_types
        assert "BATTLE_TYPE_DOUBLES" not in rejected_types, (
            "forced-switch moves must work in ordinary double battles"
        )
        for contract in (
            "ABILITY_SUCTION_CUPS",
            "MOVE_EFFECT_FLAG_INGRAIN",
            "TryReplaceFaintedMon",
            "TryWhirlwind",
            "IsAttackerLevelLowerThanDefender",
        ):
            assert contract in force_out, f"forced-switch script lost {contract} handling"
        ability_check = force_out.index("Call BATTLE_SUBSCRIPT_SWITCH_IN_ABILITY_CHECK")
        hazard_check = force_out.index("Call BATTLE_SUBSCRIPT_HAZARDS_CHECK")
        assert ability_check < hazard_check, (
            "switch-in abilities must run before entry hazards on the dragged-in battler"
        )

        positive_cases = (
            (372, 100, 100, 25, 0, False, False),
            (372, 1, 1, 0, 25, False, False),
        )
        negative_cases = (
            (371, 100, 100, 25, 0, False, False),
            (372, 0, 100, 25, 0, False, False),
            (372, 100, 0, 25, 0, False, False),
            (372, 100, 100, 0, 0, False, False),
            (372, 100, 100, 25, 0, True, False),
            (372, 100, 100, 25, 0, False, True),
        )
        assert all(should_force_switch(*case) for case in positive_cases)
        assert not any(should_force_switch(*case) for case in negative_cases)
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Circle Throw and Dragon Tail forced-switch behavior is coherent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
