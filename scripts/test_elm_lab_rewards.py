#!/usr/bin/env python3

"""Regression contracts for deterministic Elm-lab QoL rewards."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "armips/scr_seq/scr_seq_00843_elms_lab_rewards.s"
ITEMS = ROOT / "include/constants/item.h"
ITEM_DATA = ROOT / "data/itemdata/itemdata.c"
BAG = ROOT / "src/bag.c"


def main() -> int:
    try:
        patch = PATCH.read_text(encoding="utf-8")
        items = ITEMS.read_text(encoding="utf-8")
        item_data = ITEM_DATA.read_text(encoding="utf-8")
        bag = BAG.read_text(encoding="utf-8")

        assert re.search(
            r'^\s*\.open\s+"build/a012/2_843"\s*,\s*0\s*$',
            patch,
            re.MULTILINE,
        ), "the patch must target Elm's Lab 1F script archive 843"
        assert re.search(
            r"^\s*\.org\s+0x6DD\s*$", patch, re.MULTILINE
        ), "the patch must replace the original five-Potion reward block"

        reward_lines = re.findall(
            r"^\s*giveitem_no_check\s+(ITEM_[A-Z0-9_]+)\s*,\s*1\s*$",
            patch,
            re.MULTILINE,
        )
        assert reward_lines == [
            "ITEM_INFINITE_CANDY",
            "ITEM_INFINITE_REJUVINATOR",
        ], "both save-order flows must execute the same two fixed rewards"
        assert "ITEM_POTION" not in patch, "the QoL reward path must not give Potions"
        assert re.search(
            r"^\s*goto\s+0x70E\s*$", patch, re.MULTILINE
        ), "the replacement must rejoin before the original scene-state update"

        for item in ("ITEM_INFINITE_CANDY", "ITEM_INFINITE_REJUVINATOR"):
            assert re.search(rf"^#define\s+{item}\b", items, re.MULTILINE), (
                f"missing item constant: {item}"
            )
            assert re.search(rf"^\[{item}\b", item_data, re.MULTILINE), (
                f"missing item data: {item}"
            )

        assert re.search(
            r"\[ITEM_INFINITE_CANDY[^]]*\]\s*=\s*\{.*?\.fieldPocket\s*=\s*POCKET_KEY_ITEMS",
            item_data,
            re.DOTALL,
        ), "Infinite Candy must remain a persistent key item"
        assert re.search(
            r"\[ITEM_INFINITE_REJUVINATOR[^]]*\]\s*=\s*\{.*?\.fieldPocket\s*=\s*POCKET_KEY_ITEMS",
            item_data,
            re.DOTALL,
        ), "Pocket Heal must remain a persistent key item"
        assert re.search(
            r"itemId\s*==\s*ITEM_INFINITE_CANDY.*?"
            r"itemId\s*==\s*ITEM_INFINITE_REJUVINATOR",
            bag,
            re.DOTALL,
        ), "the two infinite rewards must not be consumed by Bag_TakeItem"
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Elm-lab rewards are fixed and independent of save/reload order")
    return 0


if __name__ == "__main__":
    sys.exit(main())
