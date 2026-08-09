#!/usr/bin/env python3
"""Guard the two inherited compiler-warning sites without changing behavior."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

pokemon = (ROOT / "src" / "pokemon.c").read_text(encoding="utf-8")
itemdata = (ROOT / "data" / "itemdata" / "itemdata.c").read_text(encoding="utf-8")

assert "exp >= (u32)GetExpByGrowthRateAndLevel" in pokemon
assert ".price = (u16)(250000 & 0xFFFF)," in itemdata

print("PASS: inherited warnings are explicit and byte-compatible")
