#!/usr/bin/env python3
"""Source-level integration contract for v2.4 starter choices."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    header = read("include/random_starters.h")
    source = read("src/random_starters.c")
    hooks = read("hooks")
    config = read("include/config.h")
    starter_patch = read("armips/data/starters.s")
    enemy_party = read("src/field/enemy_party.c")
    script_commands = read("src/script_new_cmds.c")
    kanto_script = read("armips/scr_seq/scr_seq_00740_T01R0301.s")

    for token in (
        "typedef enum StarterRegion",
        "typedef struct StarterChoices",
        "GenerateStarterChoices",
        "GetStarterChoice",
        "DetermineRivalStarter",
        "GetStarterEvolutionForLevel",
        "EnsureStarterHasOffensiveMove",
    ):
        assert token in header

    assert re.search(r"#define\s+RANDOMIZED_STARTERS_FLAG\s+2602\b", config)
    assert "LaunchStarterChoiceScene_Randomized" in source
    assert "LaunchStarterChoiceScene_Randomized" in hooks
    assert "0x02108514" in starter_patch
    assert "0x021E5E20" in starter_patch, "cry table must point at dynamic ARM9 choices"
    assert "RANDOMIZED_STARTERS_FLAG" in enemy_party
    assert "IsSilverStarterTrainer" in enemy_party
    silver_ids = re.search(r"sSilverTrainerIds\[\]\s*=\s*\{(.*?)\};", enemy_party, re.S)
    assert silver_ids is not None
    assert [int(value) for value in re.findall(r"\b\d+\b", silver_ids.group(1))] == [
        1, 2, 3,
        263, 264, 265, 266, 267, 268, 269, 270, 271, 272,
        285, 286, 287, 288, 289,
        489, 490, 491,
    ]
    assert "randomizedSilverStarter" in enemy_party
    assert "offset += 2" in enemy_party, "replaced Silver slots must still consume vanilla move bytes"
    assert "EnsureStarterHasOffensiveMoveFromBase(mons[i], randomizedSilverBase)" in enemy_party
    assert "NEW_COMMAND_GET_KANTO_STARTER" in kanto_script
    assert "VAR_SPECIAL_x8006" in kanto_script
    assert kanto_script.count("GetPartyCount VAR_SPECIAL_x8007") == 3
    assert "KANTO_PARTY_COUNT_VAR" in script_commands
    assert "party->count != previousPartyCount + 1" in script_commands

    encounters = read("armips/data/encounters.s")
    route34 = encounters[encounters.index("encounterdata  21   // Route 34"):]
    route34 = route34[:route34.index("encounterdata", 1)]
    morning, day_and_night = route34.split("// day encounter slots", 1)
    day, night = day_and_night.split("// night encounter slots", 1)
    night = night.split("// hoenn encounter slots", 1)[0]
    for species in ("SPECIES_BULBASAUR", "SPECIES_CHIKORITA"):
        assert species in morning
    for species in ("SPECIES_SQUIRTLE", "SPECIES_TOTODILE"):
        assert species in day
    for species in ("SPECIES_CHARMANDER", "SPECIES_CYNDAQUIL"):
        assert species in night

    print("PASS: Elm, Silver, Oak, save flag, cries, and Route 34 are wired for v2.4")


if __name__ == "__main__":
    main()
