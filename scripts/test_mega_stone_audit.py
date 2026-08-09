#!/usr/bin/env python3

"""Source contracts for every Generations V2.1 Mega Stone."""

from pathlib import Path
import re
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def record_for(mon_data: str, species: str) -> str:
    match = re.search(
        rf"^mondata SPECIES_{species},.*?(?=^mondata |\Z)",
        mon_data,
        re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing personal record for {species}"
    return match.group(0)


def main() -> int:
    try:
        item_h = read("include/constants/item.h")
        stone_defines = re.findall(
            r"^#define (ITEM_[A-Z0-9_]+)\s+\(ITEM_MEGA_STONES_START(?: \+ (\d+))?\)",
            item_h,
            re.MULTILINE,
        )
        stones = {
            name: int(offset or 0)
            for name, offset in stone_defines
            if name != "ITEM_PIXIE_PLATE"
        }
        assert len(stones) == 47, f"expected 47 stones, found {len(stones)}"
        assert sorted(stones.values()) == list(range(47))

        mega_c = read("src/battle/mega.c")
        table = re.search(
            r"const struct MegaStruct sMegaTable\[\] =\s*\{(.*?)\n\};",
            mega_c,
            re.DOTALL,
        )
        assert table, "missing item-based Mega table"
        table_stones = re.findall(r"\.itemindex\s*=\s*(ITEM_[A-Z0-9_]+)", table.group(1))
        assert len(table_stones) == 47, f"expected 47 Mega mappings, found {len(table_stones)}"
        assert set(table_stones) == set(stones), "Mega table and stone constants differ"

        mon_data = read("armips/data/mondata.s")
        mart_items = read("armips/asm/custom/mart_items.s")
        acquisition_sources = mon_data + mart_items
        assigned = set(re.findall(r"\bITEM_[A-Z0-9_]+", acquisition_sources)) & set(stones)
        assert assigned == set(stones), f"unobtainable stones: {sorted(set(stones) - assigned)}"

        legendary_mart = re.search(
            r"\.org 0x020FBC68(.*?)(?=\.org |\.close)",
            mart_items,
            re.DOTALL,
        )
        assert legendary_mart, "missing Celadon Dept Store 3F inventory"
        for stone in (
            "ITEM_MEWTWONITE_X",
            "ITEM_MEWTWONITE_Y",
            "ITEM_LATIASITE",
            "ITEM_LATIOSITE",
            "ITEM_DIANCITE",
        ):
            assert f".halfword {stone}" in legendary_mart.group(1), f"mart omits {stone}"

        charmander = record_for(mon_data, "CHARMANDER")
        assert "items ITEM_CHARIZARDITE_X, ITEM_CHARIZARDITE_Y" in charmander
        ralts = record_for(mon_data, "RALTS")
        assert "items ITEM_GALLADITE, ITEM_GARDEVOIRITE" in ralts

        battle_input = read("src/battle/battle_input.c")
        assert re.search(
            r"DPadSelectTouchDataIndexMega\[\].*?\{\s*1,\s*2,\s*3,\s*4,\s*0,\s*5,?\s*\}",
            battle_input,
            re.DOTALL,
        ), "Mega D-pad table changed"

        test_plan = read("docs/V21_TEST_PLAN.md")
        assert "docs/MEGA_STONE_AUDIT.md" in test_plan
        audit = read("docs/MEGA_STONE_AUDIT.md")
        for stone in stones:
            assert stone in audit, f"audit omits {stone}"
    except (AssertionError, OSError, ValueError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        traceback.print_exc()
        return 1

    print("PASS: all 47 Mega Stones have engine mappings and acquisition paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
