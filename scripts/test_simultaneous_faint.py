#!/usr/bin/env python3

"""Regression contracts for faint/EXP handling in double battles."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
BATTLE_COMMANDS = ROOT / "src/battle/battle_script_commands.c"
BATTLE_POKEMON = ROOT / "src/battle/battle_pokemon.c"
BATTLE_H = ROOT / "include/battle.h"
BATTLE_HOOKS = ROOT / "asm/battle/battle_hooks.s"
HOOKS = ROOT / "hooks"
ROM_LD = ROOT / "rom.ld"


SPECIES_NONE = 0
SPECIES_BAD_EGG = 495


def should_process_faint(hp: int, species: int, processed: bool) -> bool:
    return (
        hp == 0
        and species not in (SPECIES_NONE, SPECIES_BAD_EGG)
        and not processed
    )


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


def assembly_label_body(source: str, name: str) -> str:
    start = re.search(rf"^\s*{name}:\s*$", source, re.MULTILINE)
    assert start, f"assembly label not found: {name}"
    end = re.search(r"^\s*\.pool\s*$", source[start.end() :], re.MULTILINE)
    assert end, f"assembly label has no terminating pool: {name}"
    return source[start.start() : start.end() + end.end()]


def main() -> int:
    try:
        commands = BATTLE_COMMANDS.read_text(encoding="utf-8")
        pokemon = BATTLE_POKEMON.read_text(encoding="utf-8")
        battle_h = BATTLE_H.read_text(encoding="utf-8")
        battle_hooks = BATTLE_HOOKS.read_text(encoding="utf-8")
        hooks = HOOKS.read_text(encoding="utf-8")
        rom_ld = ROM_LD.read_text(encoding="utf-8")

        assert re.search(
            r"u8\s+faintProcessed\[CLIENT_MAX\]", battle_h
        ), "BattleStruct must track faint processing independently per active slot"
        assert re.search(
            r"BOOL\s+BtlCmd_TryFaintMon\s*\(", commands
        ), "the corrected TryFaintMon command must be implemented locally"
        faint = function_body(commands, "BtlCmd_TryFaintMon")
        for guard in (
            r"battlemon\[battlerId\]\.hp\s*!=\s*0",
            r"battlemon\[battlerId\]\.species\s*==\s*SPECIES_NONE",
            r"battlemon\[battlerId\]\.species\s*==\s*SPECIES_BAD_EGG",
            r"faintProcessed\[battlerId\]",
        ):
            assert re.search(guard, faint), f"TryFaintMon is missing guard: {guard}"
        assert not re.search(
            r"battlemon\[battlerId\]\.species\s*=\s*SPECIES_NONE", faint
        ), "faint handling must retain species data until EXP is calculated"
        assert re.search(
            r"faintProcessed\[battlerId\]\s*=\s*TRUE;.*?"
            r"fainting_client\s*=\s*battlerId;",
            faint,
            re.DOTALL,
        ), "the duplicate-faint guard must latch before faint processing starts"
        for behavior in (
            r"server_status_flag\s*\|=",
            r"total_hinshi\[battlerId\]\+\+",
            r"UpdateFriendshipFainted\(bsys,\s*ctx,\s*battlerId\)",
        ):
            assert re.search(behavior, faint), (
                f"corrected faint command must preserve vanilla behavior: {behavior}"
            )

        assert re.search(
            r"0012\s+BtlCmd_TryFaintMon\s+0223E22C\s+3", hooks
        ), "overlay 12 must hook command 28 to the corrected TryFaintMon"
        assert re.search(
            r"UpdateFriendshipFainted\s*=\s*0x02248558\s*\|\s*1", rom_ld
        ), "the corrected command must link the vanilla friendship update"

        reset = function_body(pokemon, "ClearBattleMonFlagsOnSwitch")
        assert "ClearBattleMonFlags(sp, client)" in reset
        assert re.search(
            r"faintProcessed\[client\]\s*=\s*FALSE", reset
        ), "a newly loaded battler must clear the duplicate-faint guard"
        switch_hook = assembly_label_body(battle_hooks, "ClearBattleMonFlags_hook")
        faint_hook = assembly_label_body(battle_hooks, "ClearBattleMonFlags_hook2")
        assert "bl ClearBattleMonFlagsOnSwitch" in switch_hook, (
            "the switch-in hook must reset faint processing"
        )
        assert "bl ClearBattleMonFlags" in faint_hook
        assert "ClearBattleMonFlagsOnSwitch" not in faint_hook, (
            "InitFaintedWork must not clear the guard for the Pokémon still fainting"
        )

        assert should_process_faint(0, 25, False)
        assert should_process_faint(0, 26, False)
        assert not should_process_faint(0, 25, True)
        assert not should_process_faint(1, 25, False)
        assert not should_process_faint(0, SPECIES_NONE, False)
        assert not should_process_faint(0, SPECIES_BAD_EGG, False)

        processed = [False, False, False, False]
        assert should_process_faint(0, 25, processed=False)
        processed[1] = True
        assert should_process_faint(0, 26, processed=processed[3])
        processed[3] = True
        assert processed[1] and processed[3], (
            "both opposing slots must be independently processable for Ariana's double KO"
        )
        processed[1] = False
        assert should_process_faint(0, 27, processed=processed[1]), (
            "a replacement in the same battler slot must be able to faint later"
        )
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: simultaneous faint and EXP handling is coherent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
