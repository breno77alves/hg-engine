#!/usr/bin/env python3
"""Static guards for the Generations V2.0 save-layout contract."""

from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE = "c28e104a8ed664ce1a5dba6b0d8d83caded89b62"


def current(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def at_base(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True, encoding="utf-8"
    )


for stable_file in ("include/save.h", "include/bag.h", "src/save.c"):
    assert current(stable_file) == at_base(stable_file), f"save layout changed: {stable_file}"

config = current("include/config.h")
base_config = at_base("include/config.h")
for define in ("ALLOW_SAVE_CHANGES", "ITEM_POCKET_EXPANSION", "EXPAND_PC_BOXES"):
    pattern = rf"^\s*#\s*define\s+{define}\b"
    assert bool(re.search(pattern, config, re.MULTILINE)) == bool(
        re.search(pattern, base_config, re.MULTILINE)
    ), f"persistent feature setting changed: {define}"

items = current("include/constants/item.h")
base_items = at_base("include/constants/item.h")
for count in ("NUM_BAG_ITEMS", "NUM_BAG_MEDICINE", "NUM_BAG_BALLS", "NUM_BAG_TMHMS"):
    pattern = rf"^#define\s+{count}\s+(.+)$"
    now = re.findall(pattern, items, re.MULTILINE)
    before = re.findall(pattern, base_items, re.MULTILINE)
    assert now == before, f"bag capacity changed: {count}"

pokemon = current("include/pokemon.h")
assert re.search(
    r"u32\s+exp\s*:\s*21\s*;.*?u32\s+unused\s*:\s*10\s*;.*?u32\s+abilityMSB\s*:\s*1\s*;",
    pokemon,
    re.DOTALL,
), "expanded ability storage must reuse the existing 32-bit EXP word"

bag = current("src/bag.c")
assert "Bag_GetLegacyMedicineSlotForRemove" in bag
assert "PocketCompaction(bag->medicine, NUM_BAG_MEDICINE)" in bag

print("PASS: V2.0 persistent layouts are preserved; playable save fixtures remain required")
