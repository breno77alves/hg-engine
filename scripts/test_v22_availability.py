#!/usr/bin/env python3
"""Regression contracts for the V2.2 single-save availability project."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "armips/data/v22_availability.json"
BASELINE = ROOT / "scripts/fixtures/v211_wild_species.txt"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def national_species() -> list[str]:
    text = (ROOT / "armips/data/pokedex/sortlists/nationalnum.s").read_text(
        encoding="utf-8"
    )
    return re.findall(r"^\.halfword\s+(SPECIES_[A-Z0-9_]+)\s*$", text, re.MULTILINE)


def encounter_blocks(text: str) -> dict[int, str]:
    blocks: dict[int, str] = {}
    matches = list(re.finditer(r"^encounterdata\s+(\d+)\s+//", text, re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks[int(match.group(1))] = text[match.start() : end]
    return blocks


def period_species(block: str, period: str) -> list[str]:
    match = re.search(
        rf"// {period} encounter slots\s*(.*?)(?=\n//|\n\.close)",
        block,
        re.DOTALL,
    )
    if not match:
        return []
    return re.findall(
        r"^(?:pokemon|monwithform)\s+(SPECIES_[A-Z0-9_]+)",
        match.group(1),
        re.MULTILINE,
    )


def wild_species(text: str) -> set[str]:
    return set(
        re.findall(
            r"^(?:pokemon|monwithform|encounter|encounterwithform)\s+(SPECIES_[A-Z0-9_]+)",
            text,
            re.MULTILINE,
        )
    ) - {"SPECIES_NONE"}


def form_species() -> dict[tuple[str, int], str]:
    text = (ROOT / "data/PokeFormDataTbl.c").read_text(encoding="utf-8")
    result: dict[tuple[str, int], str] = {}
    for match in re.finditer(
        r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n\s*\}", text, re.DOTALL
    ):
        base, body = match.groups()
        for index, form in enumerate(
            re.findall(r"\b(SPECIES_[A-Z0-9_]+)\b", body), start=1
        ):
            result[(base, index)] = form
    return result


def evolution_edges() -> dict[str, set[str]]:
    text = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    forms = form_species()
    edges: dict[str, set[str]] = {}
    current = ""
    for line in text.splitlines():
        header = re.match(r"evodata\s+(SPECIES_[A-Z0-9_]+)", line)
        if header:
            current = header.group(1)
            continue
        formed = re.search(
            r"evolutionwithform\s+[^,]+,\s*[^,]+,\s*(SPECIES_[A-Z0-9_]+),\s*(\d+)",
            line,
        )
        target = re.search(r"evolution\s+[^,]+,\s*[^,]+,\s*(SPECIES_[A-Z0-9_]+)", line)
        if current and formed:
            base, index = formed.groups()
            resolved = forms.get((base, int(index)))
            if resolved:
                edges.setdefault(current, set()).add(resolved)
            continue
        if current and target and target.group(1) != "SPECIES_NONE":
            edges.setdefault(current, set()).add(target.group(1))
    return edges


def reachable_species(seeds: set[str], edges: dict[str, set[str]]) -> set[str]:
    reachable = set(seeds)
    while True:
        expanded = reachable | {
            target
            for source, targets in edges.items()
            if source in reachable
            for target in targets
        }
        if expanded == reachable:
            return reachable
        reachable = expanded


def main() -> int:
    national = national_species()
    if len(national) != 1025 or len(set(national)) != 1025:
        return fail(f"National Dex contract is {len(national)}, expected 1025 unique species")

    if not CONFIG.exists():
        return fail("armips/data/v22_availability.json has not been created")
    if not BASELINE.exists():
        return fail("scripts/fixtures/v211_wild_species.txt has not been created")

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    encounters_text = (ROOT / "armips/data/encounters.s").read_text(encoding="utf-8")
    blocks = encounter_blocks(encounters_text)
    current_wild = wild_species(encounters_text)
    baseline_wild = {
        line.strip()
        for line in BASELINE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }
    lost = sorted(baseline_wild - current_wild)
    if lost:
        return fail(f"V2.1.1 wild species were removed: {', '.join(lost)}")

    route_29 = blocks[1]
    expected_yamper = {"morning": 1, "day": 1, "night": 1}
    for period, count in expected_yamper.items():
        actual = period_species(route_29, period).count("SPECIES_YAMPER")
        if actual != count:
            return fail(f"Route 29 {period} has {actual} Yamper slots, expected {count}")
    morning = period_species(route_29, "morning")
    day = period_species(route_29, "day")
    night = period_species(route_29, "night")
    if morning[2:6].count("SPECIES_YAMPER") != 1 or day[2:6].count("SPECIES_YAMPER") != 1:
        return fail("Yamper must occupy a 10% Route 29 slot in morning and day")
    if night[6:8].count("SPECIES_YAMPER") != 1:
        return fail("Yamper must occupy a 5% Route 29 slot at night")

    national_park = blocks[23]
    fossil_slots = {
        "morning": {"SPECIES_DRACOZOLT", "SPECIES_ARCTOZOLT"},
        "day": {"SPECIES_DRACOVISH", "SPECIES_ARCTOVISH"},
    }
    for period, expected in fossil_slots.items():
        actual = set(period_species(national_park, period)[10:12])
        if actual != expected:
            return fail(f"National Park {period} 1% fossils are {sorted(actual)}, expected {sorted(expected)}")
    if "SPECIES_AERODACTYL" not in period_species(national_park, "night"):
        return fail("Aerodactyl must remain available in National Park at night")

    edges = evolution_edges()
    form_sources = {
        entry["evolution_source"] for entry in config.get("functional_form_sources", [])
    }
    external_sources = set(config.get("external_species_sources", []))
    reachable = reachable_species(current_wild | form_sources | external_sources, edges)
    missing = [species for species in national if species not in reachable]
    if missing:
        preview = ", ".join(missing[:20])
        return fail(f"{len(missing)} National Dex species are unreachable: {preview}")

    added_wild = current_wild - baseline_wild
    evolved_exceptions = set(config.get("evolved_wild_exceptions", []))
    incoming = {target for targets in edges.values() for target in targets}
    invalid_evolved = sorted((added_wild & incoming) - evolved_exceptions)
    if invalid_evolved:
        return fail(f"new evolved species were added directly to the wild: {', '.join(invalid_evolved)}")

    legendary_sources = config.get("legendary_sources", [])
    for source in legendary_sources:
        block = blocks[source["encounter_id"]]
        for period in ("morning", "day", "night"):
            slots = period_species(block, period)
            if source["species"] not in slots[10:12]:
                return fail(
                    f"{source['species']} is not in a 1% slot for {period} "
                    f"of encounter {source['encounter_id']}"
                )

    config_text = (ROOT / "armips/include/config.s").read_text(encoding="utf-8")
    if "ALWAYS_UNCAPPED_FRAME_RATE equ 0" not in config_text:
        return fail("global uncapped frame rate must remain disabled")
    if "BATTLES_UNCAPPED_FRAME_RATE equ 0" not in config_text:
        return fail("battle-only uncapped frame rate must remain disabled")

    print(
        "PASS: all 1025 National Dex species are obtainable in one save; "
        "V2.1.1 encounters and V2.2 rarity contracts are preserved"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
