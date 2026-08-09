#!/usr/bin/env python3
"""Static regressions for Generations-specific event and data repairs."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def item_block(source: str, item: str) -> str:
    match = re.search(
        rf"\[{item} - NUM_UNKNOWN_SLOTS_EXPLORER_KIT\]\s*=\s*\{{(.*?)\n\}},",
        source,
        re.S,
    )
    assert match, f"missing item data block for {item}"
    return match.group(1)


def dex_entry(source: str, species: str) -> str:
    match = re.search(rf'mondexentry {species}, "((?:[^"\\]|\\.)*)"', source)
    assert match, f"missing Pokédex entry for {species}"
    return match.group(1)


def main() -> None:
    item_constants = read("include/constants/item.h")
    assert re.search(r"#define NUM_BAG_MEDICINE\s+40\b", item_constants)

    items = read("data/itemdata/itemdata.c")
    assert items.count(".fieldPocket = POCKET_MEDICINE,") == 40, (
        "the fixed-size medicine save pocket must contain exactly its 40 vanilla items"
    )
    migrated_items = [
        "ITEM_ABILITY_CAPSULE",
        "ITEM_LUMIOSE_GALETTE",
        "ITEM_SHALOUR_SABLE",
        "ITEM_BIG_MALASADA",
        "ITEM_ABILITY_PATCH",
        "ITEM_MOOMOO_CHEESE",
        "ITEM_PEWTER_CRUNCHIES",
    ]
    mint_constants = re.findall(
        r"#define (ITEM_[A-Z]+_MINT)\s+\(ITEM_PIXIE_PLATE \+ \d+\)", item_constants
    )
    assert len(mint_constants) == 21
    for item in migrated_items + mint_constants:
        assert ".fieldPocket = POCKET_ITEMS," in item_block(items, item), (
            f"{item} still consumes a medicine save slot"
        )

    bag = read("src/bag.c")
    assert "Bag_IsLegacyMedicineItem" in bag
    assert "IS_ITEM_NATURE_MINT(itemId)" in bag
    for item in migrated_items:
        assert item in bag, f"legacy save fallback omits {item}"
    assert "Bag_GetLegacyMedicineSlotForAdd" in bag
    assert "Bag_GetLegacyMedicineSlotForRemove" in bag
    assert "slot >= bag->medicine" in bag and "PocketCompaction(bag->medicine" in bag

    falkner = read("data/text/558.txt")
    assert "TM51 contains Roost" in falkner
    assert "used only once" not in falkner.lower()
    assert "used any number of times" in falkner.lower()
    assert "'" not in falkner, "msgenc requires the game's curly apostrophe glyph"

    encounters = read("armips/data/encounters.s")
    route33 = encounters.split("encounterdata  17   // Route 33", 1)[1].split(".close", 1)[0]
    assert route33.count("monwithform SPECIES_ROCKRUFF, 1") == 3
    evolutions = read("armips/data/evodata.s")
    own_tempo_evo = evolutions.split("evodata SPECIES_ROCKRUFF_OWN_TEMPO", 1)[1].split("evoentry 0", 1)[0]
    assert "evolutionwithform EVO_LEVEL_DUSK, 25, SPECIES_LYCANROC, 2" in own_tempo_evo

    mondata = read("armips/data/mondata.s")
    wrapped_entries = [
        "SPECIES_SKELEDIRGE",
        "SPECIES_QUAXWELL",
        "SPECIES_QUAQUAVAL",
        "SPECIES_LOKIX",
        "SPECIES_PAWMI",
        "SPECIES_PAWMO",
        "SPECIES_SMOLIV",
        "SPECIES_NACLI",
        "SPECIES_BOMBIRDIER",
        "SPECIES_VAROOM",
        "SPECIES_VELUZA",
    ]
    for species in wrapped_entries:
        description = dex_entry(mondata, species)
        lines = description.split(r"\n")
        assert len(lines) == 3, f"{species} should use the three Pokédex lines"
        assert max(map(len, lines)) <= 44, f"{species} still has an overflowing line"

    audit = read("docs/GENERATIONS_BUGS.md")
    for status in ("Fixed", "Fixture pending", "Won't fix"):
        assert status in audit, f"bug audit is missing the {status!r} classification"

    print("PASS: Generations event/data regressions")


if __name__ == "__main__":
    main()
