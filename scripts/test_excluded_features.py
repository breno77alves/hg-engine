#!/usr/bin/env python3
"""Keep balance-changing features outside the Generations V2.1 scope."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def active_define(text: str, name: str) -> bool:
    return re.search(rf"^\s*#\s*define\s+{re.escape(name)}\b", text, re.MULTILINE) is not None


def armips_value(text: str, name: str) -> int:
    match = re.search(rf"^\s*{re.escape(name)}\s+equ\s+(\d+)\b", text, re.MULTILINE)
    assert match, f"missing {name} setting"
    return int(match.group(1))


config = (ROOT / "include" / "config.h").read_text(encoding="utf-8")
armips = (ROOT / "armips" / "include" / "config.s").read_text(encoding="utf-8")

for excluded in (
    "IMPLEMENT_WILD_DOUBLE_BATTLES",
    "RESTORE_ITEMS_AT_BATTLE_END",
    "FLAG_Z_MOVE_ENABLED",
    "FLAG_DYNAMAX_ENABLED",
    "FLAG_TERASTALIZATION_ENABLED",
):
    assert not active_define(config, excluded), f"excluded feature enabled: {excluded}"

assert armips_value(armips, "BATTLE_MODE_FORCE_SET") == 0
assert armips_value(armips, "ALWAYS_UNCAPPED_FRAME_RATE") == 0
assert armips_value(armips, "BATTLES_UNCAPPED_FRAME_RATE") == 0

print("PASS: excluded balance-changing features remain disabled")
