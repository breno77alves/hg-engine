#!/usr/bin/env python3
"""Check that every V2.2 form/evolution item has a repeatable source."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]

ITEMS = [
    "ITEM_LINKING_CORD",
    "ITEM_AMULET_COIN", "ITEM_BOOSTER_ENERGY", "ITEM_CHIPPED_POT",
    "ITEM_FIGHTING_MEMORY", "ITEM_FLYING_MEMORY", "ITEM_POISON_MEMORY",
    "ITEM_GROUND_MEMORY", "ITEM_ROCK_MEMORY", "ITEM_BUG_MEMORY",
    "ITEM_GHOST_MEMORY", "ITEM_STEEL_MEMORY", "ITEM_FIRE_MEMORY",
    "ITEM_WATER_MEMORY", "ITEM_GRASS_MEMORY", "ITEM_ELECTRIC_MEMORY",
    "ITEM_PSYCHIC_MEMORY", "ITEM_ICE_MEMORY", "ITEM_DRAGON_MEMORY",
    "ITEM_DARK_MEMORY", "ITEM_FAIRY_MEMORY",
    "ITEM_RED_NECTAR", "ITEM_YELLOW_NECTAR", "ITEM_PINK_NECTAR", "ITEM_PURPLE_NECTAR",
    "ITEM_SCROLL_OF_DARKNESS", "ITEM_SCROLL_OF_WATERS",
    "ITEM_CORNERSTONE_MASK", "ITEM_WELLSPRING_MASK", "ITEM_HEARTHFLAME_MASK",
]


def main() -> int:
    mart = (ROOT / "armips/asm/custom/mart_items.s").read_text(encoding="utf-8")
    missing = [item for item in ITEMS if not re.search(rf"^\.halfword\s+{item}$", mart, re.MULTILINE)]
    failures = [f"not sold: {item}" for item in missing]

    evodata = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    kubfu = re.search(
        r"^evodata\s+SPECIES_KUBFU\s*(.*?)(?=^terminateevodata)",
        evodata, re.MULTILINE | re.DOTALL,
    )
    if not kubfu or "ITEM_SCROLL_OF_DARKNESS, SPECIES_URSHIFU" not in kubfu.group(1):
        failures.append("Darkness Scroll does not evolve Kubfu into Urshifu")
    if not kubfu or "ITEM_SCROLL_OF_WATERS, SPECIES_URSHIFU, 1" not in kubfu.group(1):
        failures.append("Waters Scroll does not evolve Kubfu into Rapid Strike form")

    itemdata = (ROOT / "data/itemdata/itemdata.c").read_text(encoding="utf-8")
    for item in ("ITEM_SCROLL_OF_DARKNESS", "ITEM_SCROLL_OF_WATERS"):
        match = re.search(rf"\[{item}[^]]*\]\s*=\s*\{{(.*?)\n\}},", itemdata, re.DOTALL)
        if not match or ".fieldUseFunc = 20" not in match.group(1) or ".evolve = TRUE" not in match.group(1):
            failures.append(f"{item} is not configured as an evolution item")

    if failures:
        print("FAIL: repeatable item contract mismatch:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: Linking Cord and all functional form items have repeatable shop sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
