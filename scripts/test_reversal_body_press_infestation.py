#!/usr/bin/env python3

"""Regression contracts for Reversal, Body Press, and binding moves."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CALC_BASE_DAMAGE = ROOT / "src/individual/CalcBaseDamage.c"
MOVES = ROOT / "armips/data/moves.s"
INFESTATION_SCRIPT = (
    ROOT / "data/battle_scripts/moves/move_script_0614_INFESTATION.s"
)
BIND_EFFECT = ROOT / "data/battle_scripts/effects/effect_script_0042_BIND_HIT.s"
WHIRLPOOL_EFFECT = (
    ROOT / "data/battle_scripts/effects/effect_script_0261_WHIRLPOOL.s"
)
BATTLE_COMMANDS = ROOT / "src/battle/battle_script_commands.c"
FIELD_CONDITIONS = ROOT / "src/individual/ServerFieldConditionCheck.c"
SWITCH_CHECKS = ROOT / "src/battle/other_battle_calculators.c"
BATTLE_POKEMON = ROOT / "src/battle/battle_pokemon.c"
MESSAGES = ROOT / "data/text/197.txt"


def move_block(source: str, move: str) -> str:
    match = re.search(
        rf'movedata {move},.*?terminatedata', source, re.DOTALL
    )
    assert match, f"move-data entry not found for {move}"
    return match.group(0)


def flail_family_power(hp: int, max_hp: int) -> int:
    ratio = (48 * hp) // max_hp
    for floor, power in ((32, 20), (17, 40), (10, 80), (5, 100), (2, 150)):
        if ratio >= floor:
            return power
    return 200


def main() -> int:
    calc = CALC_BASE_DAMAGE.read_text(encoding="utf-8")
    moves = MOVES.read_text(encoding="utf-8")
    infestation_script = INFESTATION_SCRIPT.read_text(encoding="utf-8")
    bind_effect = BIND_EFFECT.read_text(encoding="utf-8")
    whirlpool_effect = WHIRLPOOL_EFFECT.read_text(encoding="utf-8")
    battle_commands = BATTLE_COMMANDS.read_text(encoding="utf-8")
    field_conditions = FIELD_CONDITIONS.read_text(encoding="utf-8")
    switch_checks = SWITCH_CHECKS.read_text(encoding="utf-8")
    battle_pokemon = BATTLE_POKEMON.read_text(encoding="utf-8")
    messages = MESSAGES.read_text(encoding="utf-8").splitlines()

    try:
        assert re.search(
            r"case MOVE_REVERSAL:\s*case MOVE_FLAIL:.*?"
            r"p = \(48 \* AttackingMon\.hp\) / AttackingMon\.maxhp;",
            calc,
            re.DOTALL,
        ), "Reversal must share Flail's HP-based power bands"
        expected_bands = {48: 20, 31: 40, 16: 80, 9: 100, 4: 150, 1: 200}
        for hp, expected in expected_bands.items():
            assert flail_family_power(hp, 48) == expected, (
                f"incorrect Reversal power band at {hp}/48 HP"
            )

        assert re.search(
            r"AttackingMon\.defense\s*=\s*"
            r"BattlePokemonParamGet\(sp, attacker, BATTLE_MON_DATA_DEF, NULL\);",
            calc,
        ), "Body Press must read Defense from the attacker, not the defender"
        assert re.search(
            r"else if \(moveno == MOVE_BODY_PRESS\) \{\s*"
            r"AttackingMon\.attack = AttackingMon\.defense;\s*"
            r"AttackingMon\.atkstate = AttackingMon\.defstate;\s*\}",
            calc,
        ), "Body Press must use the attacker's Defense stat and Defense stage"

        expected_effects = {
            "MOVE_WRAP": "MOVE_EFFECT_BIND_HIT",
            "MOVE_FIRE_SPIN": "MOVE_EFFECT_BIND_HIT",
            "MOVE_WHIRLPOOL": "MOVE_EFFECT_WHIRLPOOL",
            "MOVE_INFESTATION": "MOVE_EFFECT_BIND_HIT",
        }
        for move, effect in expected_effects.items():
            block = move_block(moves, move)
            assert re.search(rf"\bbattleeffect\s+{effect}\b", block), (
                f"{move} must use its binding effect"
            )
            assert "FLAG_UNUSABLE_UNIMPLEMENTED" not in block, (
                f"{move} must be selectable in battle"
            )

        message_command = re.search(
            r"BufferMessage\s+(\d+),\s*TAG_NICKNAME_NICKNAME,\s*"
            r"BATTLER_CATEGORY_DEFENDER,\s*BATTLER_CATEGORY_ATTACKER",
            infestation_script,
        )
        assert message_command, "Infestation must buffer its attacker/defender message"
        message_id = int(message_command.group(1))
        expected_messages = [
            "{STRVAR_1 1, 0, 0} has been\\nafflicted with an infestation by\\f{STRVAR_1 1, 1, 0}!",
            "{STRVAR_1 1, 0, 0} has been\\nafflicted with an infestation by\\fthe wild {STRVAR_1 1, 1, 0}!",
            "{STRVAR_1 1, 0, 0} has been\\nafflicted with an infestation by\\fthe opposing {STRVAR_1 1, 1, 0}!",
            "The wild {STRVAR_1 1, 0, 0} has\\nbeen afflicted with an infestation by\\f{STRVAR_1 1, 1, 0}!",
            "The wild {STRVAR_1 1, 0, 0} has\\nbeen afflicted with an infestation by\\fthe wild {STRVAR_1 1, 1, 0}!",
            "The opposing {STRVAR_1 1, 0, 0}\\nhas been afflicted with an infestation by\\f{STRVAR_1 1, 1, 0}!",
            "The opposing {STRVAR_1 1, 0, 0}\\nhas been afflicted with an infestation by\\fthe opposing {STRVAR_1 1, 1, 0}!",
        ]
        assert messages[message_id : message_id + len(expected_messages)] == expected_messages, (
            "Infestation's localized message variants must match its buffered message ID"
        )

        for source, name in (
            (bind_effect, "standard binding effect"),
            (whirlpool_effect, "Whirlpool effect"),
        ):
            assert "MOVE_SUBSCRIPT_PTR_BIND_TARGET" in source, (
                f"{name} must schedule the bind-target subscript"
            )
        assert "turns = 5 + (BattleRand(bw) & 1)" in battle_commands, (
            "binding moves must last four to five damaging turns"
        )
        assert "turns = 8" in battle_commands, (
            "Grip Claw must extend binding to seven damaging turns"
        )
        assert re.search(
            r"binding_turns\[battlerId\].*?maxhp \* -1, 8",
            field_conditions,
            re.DOTALL,
        ), "binding residual damage must be one eighth of max HP"
        assert re.search(
            r"binding_turns\[battlerId\]\s*!=\s*0", switch_checks
        ), "an actively bound battler must be prevented from switching"
        assert re.search(
            r"battlerIdBinding == client.*?binding_turns\[i\] = 0",
            battle_pokemon,
            re.DOTALL,
        ), "binding must clear when the binding battler leaves or faints"
    except (AssertionError, IndexError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Reversal, Body Press, and the four binding moves are coherent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
