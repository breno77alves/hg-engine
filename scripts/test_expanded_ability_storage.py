#!/usr/bin/env python3

"""Contracts for storing 9-bit abilities without changing the V2.0 save size."""

from pathlib import Path
import re
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    try:
        constants = read("include/constants/ability.h")
        assert re.search(r"#define ABILITY_THERMAL_EXCHANGE\s+270\b", constants)

        mon_data = read("armips/data/mondata.s")
        for species in ("FRIGIBAX", "ARCTIBAX", "BAXCALIBUR"):
            record = re.search(
                rf"^mondata SPECIES_{species},.*?(?=^mondata |\Z)",
                mon_data,
                re.MULTILINE | re.DOTALL,
            )
            assert record, f"missing {species} personal record"
            assert "abilities ABILITY_THERMAL_EXCHANGE, ABILITY_NONE" in record.group(0)

        macros = read("armips/include/macros.s")
        ability_macro = re.search(
            r"\.macro abilities,abi1,abi2(.*?)\.endmacro", macros, re.DOTALL
        )
        assert ability_macro
        assert ".orga 0x16" in ability_macro.group(1)
        assert ".halfword abi1" in ability_macro.group(1)
        assert ".orga 0x1A" in ability_macro.group(1)
        assert ".halfword abi2" in ability_macro.group(1)

        pokemon_h = read("include/pokemon.h")
        assert re.search(r"u32 exp\s*:21", pokemon_h)
        assert re.search(r"u32 abilityMSB\s*:1", pokemon_h)
        assert re.search(r"GiveMon\(.*?u16 ability", pokemon_h)
        assert "CalcLevelBySpeciesAndExp(u32 species, u32 exp)" in pokemon_h

        pokemon_c = read("src/pokemon.c")
        assert "SetBoxMonData_EditedCases" in pokemon_c
        assert "GetBoxMonData_EditedCases" in pokemon_c
        assert "AddBoxMonData_EditedCases" in pokemon_c
        assert "blockA->abilityMSB = (ability >> 8) & 0x01" in pokemon_c
        assert "(blockA->abilityMSB << 8) | (blockA->ability)" in pokemon_c
        assert "case MON_DATA_LEVEL:" in pokemon_c
        assert "CalcLevelBySpeciesAndExp(blockA->species, blockA->exp)" in pokemon_c
        assert "blockA->exp >= maximum" in pokemon_c
        assert re.search(r"GiveMon\(.*?u16 ability", pokemon_c)

        linker = read("rom.ld")
        assert "CalcLevelBySpeciesAndExp = 0x0206FDA8 | 1;" in linker

        battle_h = read("include/battle.h")
        assert re.search(r"u8 dummy;\s*/\*\*< free - used to be ability index", battle_h)
        assert re.search(r"/\* 0x7a \*/ u16 ability;", battle_h)

        switch_in = read("src/individual/SwitchInAbilityCheck.c")
        assert re.search(r"for \(num = 0; num <= (?:\(int\))?0x26", switch_in)
        assert "offsetof(struct BattlePokemon, ability)" not in switch_in

        abilities_asm = read("armips/asm/abilities.s")
        assert "ABILITY_OFFSET_WITHIN_BATTLESTRUCT" in abilities_asm
        assert "0x0224EF36" in abilities_asm
        assert "add r4, #NEW_ABILITY_OFFSET" in abilities_asm
        assert "ldrh r0, [r4]" in abilities_asm
        assert "SetBattlerVar" in abilities_asm
        assert "0x0204D132" in abilities_asm
        assert "0x02089A2A" in abilities_asm

        global_asm = read("armips/global.s")
        assert '.include "armips/asm/abilities.s"' in global_asm

        hooks = read("hooks")
        for hook in (
            "GetBoxMonData_EditedCases_hook",
            "SetBoxMonData_EditedCases_hook",
            "AddBoxMonData_EditedCases_hook",
            "BoxDisplayMon_StoreAbility",
            "BoxDisplayMon_GrabAbility",
        ):
            assert hook in hooks, f"missing {hook}"

        enemy_party = read("src/field/enemy_party.c")
        assert re.search(r"u16 .*?ab1 = 0, ab2 = 0", enemy_party)
        assert "MON_DATA_ABILITY, (u16 *)&ab1" in enemy_party
        assert "MON_DATA_ABILITY, (u16 *)&ab2" in enemy_party

        summary = read("include/summary.h")
        assert re.search(r"/\* 0x32 \*/ u8\s+form;", summary)
        assert re.search(r"/\* 0x4E \*/ u16 ability;", summary)

        hidden = read("data/HiddenAbilityTable.c")
        for species in ("FRIGIBAX", "ARCTIBAX", "BAXCALIBUR"):
            assert re.search(
                rf"\[SPECIES_{species}\s*\]\s*=\s*ABILITY_ICE_BODY", hidden
            )

        evolution = read("armips/data/evodata.s")
        assert re.search(
            r"evodata SPECIES_FRIGIBAX\s+evolution EVO_LEVEL, 30, SPECIES_ARCTIBAX",
            evolution,
        )
        assert re.search(
            r"evodata SPECIES_ARCTIBAX\s+evolution EVO_LEVEL, 45, SPECIES_BAXCALIBUR",
            evolution,
        )
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        traceback.print_exc()
        return 1

    print("PASS: expanded abilities and the Frigibax family retain valid IDs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
