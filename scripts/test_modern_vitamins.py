#!/usr/bin/env python3
"""Static contract for modern 252-per-stat vitamins and the 510 total cap."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def item_block(source: str, item: str) -> str:
    start = source.index(f"[{item}] =")
    return source[start : source.index("\n},", start)]


def main() -> None:
    assert "#define UPDATE_VITAMIN_EV_CAPS" in read("include/config.h")

    replacements = read("bytereplacement")
    modern = replacements.split("#ifdef UPDATE_VITAMIN_EV_CAPS", 1)[1].split("#else", 1)[0]
    vitamin_checks = [
        "02090034", "020900A0", "0209010C", "0209017A", "020901E8",
        "02090254", "02090A96", "02090ABC", "02090AC0",
    ]
    for address in vitamin_checks:
        assert re.search(rf"arm9 {address} FC\b", modern), f"missing modern cap at {address}"
    for address in ("0204B948", "0204B94C", "0224655C"):
        assert re.search(rf"(?:arm9|0012) {address} FC\b", replacements)

    itemdata = read("data/itemdata/itemdata.c")
    vitamins = {
        "ITEM_HP_UP": "hp",
        "ITEM_PROTEIN": "atk",
        "ITEM_IRON": "def",
        "ITEM_CARBOS": "speed",
        "ITEM_CALCIUM": "spatk",
        "ITEM_ZINC": "spdef",
    }
    for item, stat in vitamins.items():
        block = item_block(itemdata, item)
        assert f".{stat}_ev_up = TRUE," in block
        assert f".{stat}_ev_up_param = 10," in block

    # These patches replace only per-stat comparisons. The original item-use
    # routine's independent six-stat sum check (510) is deliberately untouched.
    assert "01FE" not in modern and "FE 01" not in modern

    print("PASS: vitamins use 252 per stat while preserving the independent 510 total cap")


if __name__ == "__main__":
    main()
