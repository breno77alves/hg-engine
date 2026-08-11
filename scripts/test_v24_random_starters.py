#!/usr/bin/env python3
"""Determinism and eligibility contract for v2.4 randomized starters."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "random_starters.json"
JOHTO_SALT = 0x4A6F6874
KANTO_SALT = 0x4B616E74


def mix32(value: int) -> int:
    value &= 0xFFFFFFFF
    value ^= value >> 16
    value = (value * 0x7FEB352D) & 0xFFFFFFFF
    value ^= value >> 15
    value = (value * 0x846CA68B) & 0xFFFFFFFF
    value ^= value >> 16
    return value & 0xFFFFFFFF


def choices(pool: list[dict], trainer_id: int, salt: int, excluded: set[int]) -> tuple[int, int, int]:
    result: list[int] = []
    types: set[str] = set()
    state = mix32(trainer_id ^ salt)
    for draw in range(len(pool) * 4):
        state = mix32(state + 0x9E3779B9 + draw)
        entry = pool[state % len(pool)]
        if entry["id"] in excluded or entry["id"] in result or entry["primary_type"] in types:
            continue
        result.append(entry["id"])
        types.add(entry["primary_type"])
        if len(result) == 3:
            return tuple(result)
    start = state % len(pool)
    for draw in range(len(pool)):
        entry = pool[(start + draw) % len(pool)]
        if entry["id"] in excluded or entry["id"] in result or entry["primary_type"] in types:
            continue
        result.append(entry["id"])
        types.add(entry["primary_type"])
        if len(result) == 3:
            return tuple(result)
    raise AssertionError("eligible starter pool could not form a three-type trio")


def main() -> None:
    raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pool = raw["pool"]
    c_source = (ROOT / "src" / "random_starters.c").read_text(encoding="utf-8")
    generated_include = (ROOT / "include" / "random_starter_pool.inc").read_text(encoding="utf-8")
    assert len(pool) >= 150, "starter pool is unexpectedly small"
    assert raw["algorithm"] == "mix32-v1"
    assert raw["canonical_count"] == 1025
    assert raw["internal_species_range"] == [1, 1075]

    ids = [entry["id"] for entry in pool]
    assert len(ids) == len(set(ids))
    by_id = {entry["id"]: entry for entry in pool}
    names = {entry["species"] for entry in pool}
    for forbidden in (
        "SPECIES_POIPOLE", "SPECIES_TYPE_NULL", "SPECIES_COSMOG",
        "SPECIES_KUBFU", "SPECIES_MELTAN", "SPECIES_GREAT_TUSK",
    ):
        assert forbidden not in names, f"special-category starter leaked into pool: {forbidden}"
    for entry in pool:
        assert 1 <= entry["id"] <= 1075 and not 494 <= entry["id"] <= 543
        assert entry["first_form"] is True
        assert entry["has_evolution"] is True
        assert entry["special_category"] is False
        assert entry["alternate_form"] is False
        assert entry["resources"] == {"sprite": True, "icon": True, "cry": True, "follower": True}
        assert entry["safe_move"] > 0
        assert entry["evolution_paths"]

    assert f"#define JOHTO_STARTER_SALT 0x{JOHTO_SALT:08X}" in c_source
    assert f"#define KANTO_STARTER_SALT 0x{KANTO_SALT:08X}" in c_source
    for constant in ("0x7FEB352D", "0x846CA68B", "0x9E3779B9"):
        assert constant in c_source
    assert "if (count < 3)" in c_source, "all 32-bit Trainer IDs need a guaranteed fallback scan"
    generated_entries = re.findall(
        r"\{\s*(SPECIES_[A-Z0-9_]+),\s*(MOVE_[A-Z0-9_]+)\s*\}",
        generated_include,
    )
    assert len(generated_entries) == len(pool)
    assert [species for species, _ in generated_entries] == [entry["species"] for entry in pool]

    golden = {
        0x00000000: ((453, 874, 567), (179, 111, 679)),
        0x00000001: ((90, 797, 325), (433, 418, 609)),
        0x12345678: ((786, 860, 270), (427, 679, 732)),
        0xFFFFFFFF: ((630, 347, 582), (585, 561, 425)),
    }
    for trainer_id, expected in golden.items():
        johto = choices(pool, trainer_id, JOHTO_SALT, set())
        kanto = choices(pool, trainer_id, KANTO_SALT, set(johto))
        assert (johto, kanto) == expected, (trainer_id, johto, kanto)

    for trainer_id in range(100_000):
        johto = choices(pool, trainer_id, JOHTO_SALT, set())
        kanto = choices(pool, trainer_id, KANTO_SALT, set(johto))
        assert len(set(johto)) == len({by_id[value]["primary_type"] for value in johto}) == 3
        assert len(set(kanto)) == len({by_id[value]["primary_type"] for value in kanto}) == 3
        assert set(johto).isdisjoint(kanto)
        assert johto == choices(pool, trainer_id, JOHTO_SALT, set())

    print(f"PASS: {len(pool)} eligible starters satisfy 100,000 deterministic ID trials")


if __name__ == "__main__":
    main()
