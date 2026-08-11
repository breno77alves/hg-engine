#!/usr/bin/env python3
"""Ensure every V2.2 encounter source is represented by the in-game Pokédex map."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
AREA_DATA = ROOT / "armips/data/pokedex/areadata.s"
CONFIG = ROOT / "armips/data/v22_availability.json"


def block(text: str, kind: str, species: str, period: str) -> str:
    match = re.search(
        rf"^{kind}\s+{species},\s+DEX_{period}\s*(.*?)^\s*dexendareadata",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match else ""


def main() -> int:
    text = AREA_DATA.read_text(encoding="utf-8")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    failures: list[str] = []

    # User-locked placements must be visible in the Pokédex at the exact times.
    for period in ("MORNING", "DAY"):
        if "DEX_ROUTE_29" not in block(text, "routesandcities", "SPECIES_YAMPER", period):
            failures.append(f"Yamper: Route 29 missing at {period.lower()}")
    if "DEX_ROUTE_29" not in block(text, "routesandcities", "SPECIES_YAMPER", "NIGHT"):
        failures.append("Yamper: Route 29 missing at night")

    for species, period in (
        ("SPECIES_DRACOZOLT", "MORNING"),
        ("SPECIES_ARCTOZOLT", "MORNING"),
        ("SPECIES_DRACOVISH", "DAY"),
        ("SPECIES_ARCTOVISH", "DAY"),
        ("SPECIES_AERODACTYL", "NIGHT"),
    ):
        if "DEX_NATIONAL_PARK" not in block(text, "specialareas", species, period):
            failures.append(f"{species}: National Park missing at {period.lower()}")

    # Every generated source records the exact Pokédex category/area it expects.
    for entry in config["encounter_sources"]:
        area_kind = entry.get("dex_kind")
        area = entry.get("dex_area")
        if not area_kind or not area:
            failures.append(f"{entry['species']}: generated source lacks Pokédex metadata")
            continue
        line_species = re.search(r"SPECIES_[A-Z0-9_]+", entry["line"]).group(0)
        periods = ("MORNING", "DAY", "NIGHT") if entry["period"] == "all" else (entry["period"].upper(),)
        for period in periods:
            if area not in block(text, area_kind, line_species, period):
                failures.append(
                    f"{entry['species']}: {area} missing from {line_species} {period.lower()}"
                )

    if failures:
        print("FAIL: Pokédex area data is stale:\n" + "\n".join(failures[:40]), file=sys.stderr)
        return 1
    print("PASS: Pokédex maps match Yamper, fossils, forms, and every V2.2 encounter source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
