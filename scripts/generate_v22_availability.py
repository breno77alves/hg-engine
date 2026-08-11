#!/usr/bin/env python3
"""Generate V2.2 encounters, source manifest, and the V2.1.1 regression fixture.

The v2.1.1 encounter table is the immutable input.  This keeps regeneration
idempotent and makes every replaced slot reviewable in the JSON/CSV outputs.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ENCOUNTERS = ROOT / "armips/data/encounters.s"
CONFIG = ROOT / "armips/data/v22_availability.json"
BASELINE_FIXTURE = ROOT / "scripts/fixtures/v211_wild_species.txt"
MANIFEST = ROOT / "docs/v22_availability_manifest.csv"
POKEDEX_AREAS = ROOT / "armips/data/pokedex/areadata.s"

PERIODS = ("morning", "day", "night")
SLOT_CHANCES = (20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1)

# Confirmed vanilla HGSS renewable/static sources that are not represented by
# armips/data/encounters.s.  Both remain available in Generations v2.1.1.
EXTERNAL_SOURCES = {
    "SPECIES_LAPRAS": {
        "method": "static",
        "location": "Union Cave B2F",
        "period": "Friday",
        "chance": "guaranteed",
        "requirement": "Surf",
    },
    "SPECIES_TOGEPI": {
        "method": "gift egg",
        "location": "Violet City Poké Mart",
        "period": "any",
        "chance": "guaranteed",
        "requirement": "defeat Falkner",
    },
}

# Ordinary missing families belong in Johto.  Every other missing seed is a
# legendary, mythical, Ultra Beast, paradox, synthetic, or similarly special
# post-game encounter and therefore receives a 1% all-period slot.
JOHTO_ROOTS = {
    "SPECIES_MIMEJR", "SPECIES_DEDENNE", "SPECIES_YUNGOOS",
    "SPECIES_ORICORIO", "SPECIES_WISHIWASHI", "SPECIES_BOUNSWEET",
    "SPECIES_PASSIMIAN", "SPECIES_SANDYGAST", "SPECIES_PYUKUMUKU",
    "SPECIES_MINIOR", "SPECIES_KOMALA", "SPECIES_SKWOVET",
    "SPECIES_NICKIT", "SPECIES_GOSSIFLEUR", "SPECIES_YAMPER",
    "SPECIES_CRAMORANT", "SPECIES_PINCURCHIN", "SPECIES_EISCUE",
    "SPECIES_MORPEKO", "SPECIES_LECHONK", "SPECIES_TAROUNTULA",
    "SPECIES_SMOLIV", "SPECIES_SQUAWKABILLY", "SPECIES_NACLI",
    "SPECIES_TADBULB", "SPECIES_BRAMBLIN", "SPECIES_KLAWF",
    "SPECIES_FLITTLE", "SPECIES_FINIZEN", "SPECIES_ORTHWORM",
    "SPECIES_DONDOZO", "SPECIES_TATSUGIRI", "SPECIES_GIMMIGHOUL",
    "SPECIES_POLTCHAGEIST",
}

WATER_ROOTS = {
    "SPECIES_WISHIWASHI", "SPECIES_PYUKUMUKU", "SPECIES_FINIZEN",
    "SPECIES_DONDOZO", "SPECIES_TATSUGIRI", "SPECIES_PINCURCHIN",
    "SPECIES_EISCUE",
}

# First stages of regional lines plus permanent standalone regional forms.
# The form index is derived from data/PokeFormDataTbl.c, never duplicated here.
REGIONAL_FORM_SOURCES = {
    "SPECIES_RATTATA_ALOLAN", "SPECIES_RAICHU_ALOLAN",
    "SPECIES_SANDSHREW_ALOLAN", "SPECIES_VULPIX_ALOLAN",
    "SPECIES_DIGLETT_ALOLAN", "SPECIES_MEOWTH_ALOLAN",
    "SPECIES_GEODUDE_ALOLAN", "SPECIES_GRIMER_ALOLAN",
    "SPECIES_EXEGGUTOR_ALOLAN", "SPECIES_MAROWAK_ALOLAN",
    "SPECIES_MEOWTH_GALARIAN", "SPECIES_PONYTA_GALARIAN",
    "SPECIES_SLOWPOKE_GALARIAN", "SPECIES_FARFETCHD_GALARIAN",
    "SPECIES_WEEZING_GALARIAN", "SPECIES_MR_MIME_GALARIAN",
    "SPECIES_ARTICUNO_GALARIAN", "SPECIES_ZAPDOS_GALARIAN",
    "SPECIES_MOLTRES_GALARIAN", "SPECIES_CORSOLA_GALARIAN",
    "SPECIES_ZIGZAGOON_GALARIAN", "SPECIES_DARUMAKA_GALARIAN",
    "SPECIES_YAMASK_GALARIAN", "SPECIES_STUNFISK_GALARIAN",
    "SPECIES_GROWLITHE_HISUIAN", "SPECIES_VOLTORB_HISUIAN",
    "SPECIES_TYPHLOSION_HISUIAN", "SPECIES_QWILFISH_HISUIAN",
    "SPECIES_SNEASEL_HISUIAN", "SPECIES_SAMUROTT_HISUIAN",
    "SPECIES_LILLIGANT_HISUIAN", "SPECIES_ZORUA_HISUIAN",
    "SPECIES_BRAVIARY_HISUIAN", "SPECIES_SLIGGOO_HISUIAN",
    "SPECIES_AVALUGG_HISUIAN", "SPECIES_DECIDUEYE_HISUIAN",
    "SPECIES_WOOPER_PALDEAN",
}

POSTGAME_FORM_SOURCES = {
    "SPECIES_ARTICUNO_GALARIAN", "SPECIES_ZAPDOS_GALARIAN",
    "SPECIES_MOLTRES_GALARIAN", "SPECIES_TYPHLOSION_HISUIAN",
    "SPECIES_SAMUROTT_HISUIAN", "SPECIES_LILLIGANT_HISUIAN",
    "SPECIES_BRAVIARY_HISUIAN", "SPECIES_SLIGGOO_HISUIAN",
    "SPECIES_AVALUGG_HISUIAN", "SPECIES_DECIDUEYE_HISUIAN",
}

# Functional forms produced by repeatable items.  These are manifest targets,
# not extra wild catches, so the canonical base species remains the seed.
ITEM_FORM_SOURCES = [
    {
        "form_name": "Oricorio (Pom-Pom Style)",
        "base_species": "SPECIES_ORICORIO",
        "method": "form change item",
        "requirement": "Yellow Nectar (repeatable mart)",
    },
    {
        "form_name": "Oricorio (Pa'u Style)",
        "base_species": "SPECIES_ORICORIO",
        "method": "form change item",
        "requirement": "Pink Nectar (repeatable mart)",
    },
    {
        "form_name": "Oricorio (Sensu Style)",
        "base_species": "SPECIES_ORICORIO",
        "method": "form change item",
        "requirement": "Purple Nectar (repeatable mart)",
    },
] + [
    {
        "form_name": f"Silvally ({type_name} type)",
        "base_species": "SPECIES_SILVALLY",
        "method": "held item battle form",
        "requirement": f"{type_name} Memory (repeatable mart)",
    }
    for type_name in (
        "Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost",
        "Steel", "Fire", "Water", "Grass", "Electric", "Psychic", "Ice",
        "Dragon", "Dark", "Fairy",
    )
] + [
    {
        "form_name": "Ogerpon (Wellspring Mask)",
        "base_species": "SPECIES_OGERPON",
        "method": "held item battle form",
        "requirement": "Wellspring Mask (repeatable mart)",
    },
    {
        "form_name": "Ogerpon (Hearthflame Mask)",
        "base_species": "SPECIES_OGERPON",
        "method": "held item battle form",
        "requirement": "Hearthflame Mask (repeatable mart)",
    },
    {
        "form_name": "Ogerpon (Cornerstone Mask)",
        "base_species": "SPECIES_OGERPON",
        "method": "held item battle form",
        "requirement": "Cornerstone Mask (repeatable mart)",
    },
    {
        "form_name": "Urshifu (Rapid Strike Style)",
        "base_species": "SPECIES_KUBFU",
        "method": "evolution",
        "requirement": "Scroll of Waters (repeatable mart)",
    },
]

JOHTO_IDS = tuple(
    i for i in range(1, 72)
    if i not in {5, 10, 11, 12, 13, 23, 24, 45, 47, 49, 50, 64}
)
POSTGAME_IDS = tuple(
    # Kanto and true post-game areas are always filled first.
    list(range(72, 90)) + list(range(92, 142))
    # The remaining capacity is limited to late, themed Johto dungeons.
    + list(range(30, 38)) + [43, 44, 46, 48]
    + list(range(53, 57)) + list(range(60, 64)) + [66, 69, 70, 71]
)

# Lore-significant anchors and type-driven habitat pools keep the 1% roster
# from becoming an alphabetical dump.  Every pool falls back to POSTGAME_IDS
# after its most appropriate areas fill up.
RARE_FIXED_IDS = {
    "SPECIES_ARCEUS": (89,),                       # Mt. Silver summit
    "SPECIES_ARTICUNO": (74,),                    # Seafoam Islands
    "SPECIES_ZAPDOS": (108,),                     # Rock Tunnel / Route 10
    "SPECIES_MOLTRES": (79,),                     # Mt. Silver Moltres room
    "SPECIES_MEWTWO": (139,),                     # Cerulean Cave
    "SPECIES_LUGIA": (48,),                       # Whirl Islands depths
    "SPECIES_HO_OH": (84,),                       # Bell Tower 10F
}

HABITAT_IDS = {
    "ice": (74, 75, 76, 77, 78, 80, 89, 60, 61, 62, 63),
    "water": (74, 75, 76, 77, 78, 43, 44, 46, 48, 132),
    "ghost_psychic_dark": (139, 140, 141, 106, 107, 30, 31, 32, 33, 34, 35, 36, 37, 84),
    "rock_ground_steel": (79, 80, 81, 86, 88, 106, 107, 108, 109, 110, 132, 133, 134, 135),
    "dragon": (86, 88, 89, 139, 140, 141, 66),
    "fire": (79, 80, 81, 86, 88, 89, 110, 134, 135),
    "electric": (108, 109, 119, 120, 139, 140, 141),
    "grass_bug": (137, 112, 136, 111, 113, 114, 130, 131),
    "fairy_normal": (106, 107, 130, 131, 111, 112, 113, 114, 115, 116),
    "fighting_flying": (110, 134, 135, 103, 104, 105, 125, 126, 127),
}


def git_v211_encounters() -> str:
    return subprocess.check_output(
        ["git", "show", "v2.1.1:armips/data/encounters.s"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def git_v211_areadata() -> str:
    return subprocess.check_output(
        ["git", "show", "v2.1.1:armips/data/pokedex/areadata.s"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def national_species() -> list[str]:
    text = (ROOT / "armips/data/pokedex/sortlists/nationalnum.s").read_text(encoding="utf-8")
    return re.findall(r"^\.halfword\s+(SPECIES_[A-Z0-9_]+)\s*$", text, re.MULTILINE)


def species_types() -> dict[str, tuple[str, str]]:
    text = (ROOT / "armips/data/mondata.s").read_text(encoding="utf-8")
    result: dict[str, tuple[str, str]] = {}
    for match in re.finditer(
        r'^mondata\s+(SPECIES_[A-Z0-9_]+),.*?^\s*types\s+(TYPE_[A-Z0-9_]+),\s*(TYPE_[A-Z0-9_]+)',
        text,
        re.MULTILINE | re.DOTALL,
    ):
        result[match.group(1)] = (match.group(2), match.group(3))
    return result


def habitat_ids(species: str, types: dict[str, tuple[str, str]]) -> tuple[int, ...]:
    fixed = RARE_FIXED_IDS.get(species, ())
    mon_types = set(types.get(species, ("TYPE_NORMAL", "TYPE_NORMAL")))
    keys: list[str] = []
    if "TYPE_ICE" in mon_types:
        keys.append("ice")
    if "TYPE_WATER" in mon_types:
        keys.append("water")
    if mon_types & {"TYPE_GHOST", "TYPE_PSYCHIC", "TYPE_DARK"}:
        keys.append("ghost_psychic_dark")
    if mon_types & {"TYPE_ROCK", "TYPE_GROUND", "TYPE_STEEL"}:
        keys.append("rock_ground_steel")
    if "TYPE_DRAGON" in mon_types:
        keys.append("dragon")
    if "TYPE_FIRE" in mon_types:
        keys.append("fire")
    if "TYPE_ELECTRIC" in mon_types:
        keys.append("electric")
    if mon_types & {"TYPE_GRASS", "TYPE_BUG"}:
        keys.append("grass_bug")
    if mon_types & {"TYPE_FAIRY", "TYPE_NORMAL"}:
        keys.append("fairy_normal")
    if mon_types & {"TYPE_FIGHTING", "TYPE_FLYING"}:
        keys.append("fighting_flying")

    ordered = list(fixed)
    for key in keys:
        ordered.extend(HABITAT_IDS[key])
    ordered.extend(POSTGAME_IDS)
    return tuple(dict.fromkeys(ordered))


def evolution_edges() -> dict[str, set[str]]:
    text = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    reverse_forms = {value: key for key, value in form_map().items()}
    result: dict[str, set[str]] = {}
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
            resolved = reverse_forms.get((base, int(index)))
            if resolved:
                result.setdefault(current, set()).add(resolved)
            continue
        if current and target and target.group(1) != "SPECIES_NONE":
            result.setdefault(current, set()).add(target.group(1))
    return result


def reachable(seeds: set[str], edges: dict[str, set[str]]) -> set[str]:
    result = set(seeds)
    while True:
        expanded = result | {
            target for source, targets in edges.items() if source in result for target in targets
        }
        if expanded == result:
            return result
        result = expanded


def wild_species(text: str) -> set[str]:
    return set(re.findall(
        r"^(?:pokemon|monwithform|encounter|encounterwithform)\s+(SPECIES_[A-Z0-9_]+)",
        text, re.MULTILINE
    )) - {"SPECIES_NONE"}


def split_blocks(text: str) -> tuple[str, dict[int, str], list[int]]:
    matches = list(re.finditer(r"^encounterdata\s+(\d+)\s+//", text, re.MULTILINE))
    prefix = text[:matches[0].start()]
    blocks: dict[int, str] = {}
    order: list[int] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        encounter_id = int(match.group(1))
        blocks[encounter_id] = text[match.start():end]
        order.append(encounter_id)
    return prefix, blocks, order


def grass_lines(block: str, period: str) -> list[str]:
    match = re.search(rf"(// {period} encounter slots\s*)(.*?)(?=\n//)", block, re.DOTALL)
    if not match:
        raise ValueError(f"missing {period} slots")
    return [line for line in match.group(2).splitlines() if line.strip()]


def species_on_line(line: str) -> str:
    match = re.match(
        r"(?:pokemon|monwithform|encounter|encounterwithform)\s+(SPECIES_[A-Z0-9_]+)",
        line,
    )
    if not match:
        raise ValueError(f"invalid grass line: {line}")
    return match.group(1)


def set_grass_line(block: str, period: str, slot: int, line: str) -> str:
    pattern = re.compile(rf"(// {period} encounter slots\s*)(.*?)(?=\n//)", re.DOTALL)
    match = pattern.search(block)
    if not match:
        raise ValueError(f"missing {period} slots")
    lines = [entry for entry in match.group(2).splitlines() if entry.strip()]
    if len(lines) != 12:
        raise ValueError(f"{period} has {len(lines)} slots")
    lines[slot] = line
    replacement = match.group(1) + "\n".join(lines) + "\n"
    return block[:match.start()] + replacement + block[match.end():]


def encounter_lines(block: str, section: str) -> list[str]:
    match = re.search(rf"(// {section} encounters\s*)(.*?)(?=\n//)", block, re.DOTALL)
    if not match:
        raise ValueError(f"missing {section} encounters")
    return [line for line in match.group(2).splitlines() if line.strip()]


def set_encounter_line(block: str, section: str, slot: int, line: str) -> str:
    pattern = re.compile(rf"(// {section} encounters\s*)(.*?)(?=\n//)", re.DOTALL)
    match = pattern.search(block)
    if not match:
        raise ValueError(f"missing {section} encounters")
    lines = [entry for entry in match.group(2).splitlines() if entry.strip()]
    if len(lines) != 5:
        raise ValueError(f"{section} has {len(lines)} slots")
    lines[slot] = line
    replacement = match.group(1) + "\n".join(lines) + "\n"
    return block[:match.start()] + replacement + block[match.end():]


def walkrate(block: str) -> int:
    return int(re.search(r"^walkrate\s+(\d+)", block, re.MULTILINE).group(1))


def form_map() -> dict[str, tuple[str, int]]:
    text = (ROOT / "data/PokeFormDataTbl.c").read_text(encoding="utf-8")
    result: dict[str, tuple[str, int]] = {}
    for match in re.finditer(
        r"\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*\{(.*?)\n\s*\}", text, re.DOTALL
    ):
        base, body = match.groups()
        forms = re.findall(r"\b(SPECIES_[A-Z0-9_]+)\b", body)
        for index, form in enumerate(forms, start=1):
            result[form] = (base, index)
    return result


def source_line(species: str, forms: dict[str, tuple[str, int]]) -> str:
    if species in forms:
        base, form = forms[species]
        return f"monwithform {base}, {form}"
    return f"pokemon {species}"


def location_name(block: str) -> str:
    return re.search(r"^encounterdata\s+\d+\s+//\s*(.+)$", block, re.MULTILINE).group(1).strip()


SPECIAL_DEX_AREAS = {
    "Sprout Tower": "DEX_SPROUT_TOWER",
    "Ruins of Alph": "DEX_RUINS_OF_ALPH",
    "Union Cave": "DEX_UNION_CAVE",
    "Slowpoke Well": "DEX_SLOWPOKE_WELL",
    "Ilex Forest": "DEX_ILEX_FOREST",
    "National Park": "DEX_NATIONAL_PARK",
    "Burned Tower": "DEX_BURNED_TOWER",
    "Bell Tower": "DEX_BELL_TOWER",
    "Whirl Islands": "DEX_WHIRL_ISLANDS",
    "Mt. Mortar": "DEX_MT_MORTAR",
    "Ice Path": "DEX_ICE_PATH",
    "Dragons Den": "DEX_DRAGONS_DEN",
    "Dark Cave": "DEX_DARK_CAVE",
    "Mt. Moon": "DEX_MT_MOON",
    "Seafoam Islands": "DEX_SEAFOAM_ISLANDS",
    "Cliff Edge Gate": "DEX_CLIFF_EDGE_GATE",
    "Cliff Cave": "DEX_CLIFF_CAVE",
    "Rock Tunnel": "DEX_ROCK_TUNNEL",
    "Victory Road": "DEX_VICTORY_ROAD",
    "Tohjo Falls": "DEX_TOHJO_FALLS",
    "Digletts Cave": "DEX_DIGLETTS_CAVE",
    "Viridian Forest": "DEX_VIRIDIAN_FOREST",
    "Cerulean Cave": "DEX_CERULEAN_CAVE",
}

ROUTE_DEX_AREAS = {
    "New Bark Town": "DEX_NEW_BARK_TOWN",
    "Cherrygrove City": "DEX_CHERRYGROVE_CITY",
    "Violet City": "DEX_VIOLET_CITY",
    "Ecruteak City": "DEX_ECRUTEAK_CITY",
    "Olivine City": "DEX_OLIVINE_CITY",
    "Cianwood City": "DEX_CIANWOOD_CITY",
    "Lake of Rage": "DEX_LAKE_OF_RAGE",
    "Blackthorn City": "DEX_BLACKTHORN_CITY",
    "Pallet Town": "DEX_PALLET_TOWN",
    "Viridian City": "DEX_VIRIDIAN_CITY",
    "Cerulean City": "DEX_CERULEAN_CITY",
    "Vermilion City": "DEX_VERMILION_CITY",
    "Celadon City": "DEX_CELADON_CITY",
    "Fuchsia City": "DEX_FUCHSIA_CITY",
    "Cinnabar Island": "DEX_CINNABAR_CITY",
}

SPECIAL_DEX_ORDER = (
    "DEX_SPROUT_TOWER", "DEX_RUINS_OF_ALPH", "DEX_UNION_CAVE",
    "DEX_SLOWPOKE_WELL", "DEX_ILEX_FOREST", "DEX_NATIONAL_PARK",
    "DEX_BURNED_TOWER", "DEX_BELL_TOWER", "DEX_WHIRL_ISLANDS",
    "DEX_MT_MORTAR", "DEX_ICE_PATH", "DEX_DRAGONS_DEN", "DEX_DARK_CAVE",
    "DEX_MT_MOON", "DEX_SEAFOAM_ISLANDS", "DEX_MT_SILVER_CAVE",
    "DEX_CLIFF_EDGE_GATE", "DEX_CLIFF_CAVE", "DEX_OLIVINE_CITY_SPECIAL",
    "DEX_ROCK_TUNNEL", "DEX_VICTORY_ROAD", "DEX_TOHJO_FALLS",
    "DEX_DIGLETTS_CAVE", "DEX_VIRIDIAN_FOREST", "DEX_CERULEAN_CAVE",
)

ROUTE_DEX_ORDER = (
    "DEX_NEW_BARK_TOWN", "DEX_ROUTE_29", "DEX_CHERRYGROVE_CITY",
    "DEX_ROUTE_30", "DEX_ROUTE_31", "DEX_VIOLET_CITY", "DEX_ROUTE_32",
    "DEX_ROUTE_33", "DEX_ROUTE_34", "DEX_ROUTE_35", "DEX_ROUTE_36",
    "DEX_ROUTE_37", "DEX_ECRUTEAK_CITY", "DEX_ROUTE_38", "DEX_ROUTE_39",
    "DEX_OLIVINE_CITY", "DEX_ROUTE_40", "DEX_ROUTE_41", "DEX_CIANWOOD_CITY",
    "DEX_ROUTE_42", "DEX_ROUTE_43", "DEX_LAKE_OF_RAGE", "DEX_ROUTE_44",
    "DEX_BLACKTHORN_CITY", "DEX_ROUTE_45", "DEX_ROUTE_46", "DEX_ROUTE_47",
    "DEX_MT_SILVER", "DEX_ROUTE_12", "DEX_ROUTE_19", "DEX_ROUTE_20",
    "DEX_PALLET_TOWN", "DEX_VIRIDIAN_CITY", "DEX_CERULEAN_CITY",
    "DEX_VERMILION_CITY", "DEX_CELADON_CITY", "DEX_FUCHSIA_CITY",
    "DEX_CINNABAR_CITY", "DEX_ROUTE_48", "DEX_ROUTE_26", "DEX_ROUTE_27",
    "DEX_ROUTE_28", "DEX_ROUTE_1", "DEX_ROUTE_2", "DEX_ROUTE_3",
    "DEX_ROUTE_4", "DEX_ROUTE_5", "DEX_ROUTE_6", "DEX_ROUTE_7",
    "DEX_ROUTE_8", "DEX_ROUTE_9", "DEX_ROUTE_10", "DEX_ROUTE_11",
    "DEX_ROUTE_13", "DEX_ROUTE_14", "DEX_ROUTE_15", "DEX_ROUTE_16",
    "DEX_ROUTE_17", "DEX_ROUTE_18", "DEX_ROUTE_21", "DEX_ROUTE_22",
    "DEX_ROUTE_24", "DEX_ROUTE_25", "DEX_ROUTE_2_2", "DEX_PEWTER_CITY",
    "DEX_AZALEA_TOWN", "DEX_SAFARI_ZONE_GATE", "DEX_ROUTE_16_2",
)


def dex_location(encounter_id: int, location: str) -> tuple[str, str] | None:
    """Map an encounter header to the category and marker used by HGSS's map."""
    if location == "???" or location.startswith("Safari Zone"):
        return None
    if location.startswith("Mt. Silver"):
        if encounter_id in {85, 87, 89}:
            return "routesandcities", "DEX_MT_SILVER"
        return "specialareas", "DEX_MT_SILVER_CAVE"
    route = re.match(r"Route\s+(\d+)", location)
    if route:
        if encounter_id == 136:
            return "routesandcities", "DEX_ROUTE_2_2"
        return "routesandcities", f"DEX_ROUTE_{route.group(1)}"
    if location in ROUTE_DEX_AREAS:
        return "routesandcities", ROUTE_DEX_AREAS[location]
    for prefix, area in SPECIAL_DEX_AREAS.items():
        if location.startswith(prefix):
            return "specialareas", area
    raise ValueError(f"no Pokedex area mapping for encounter {encounter_id}: {location}")


def generate_pokedex_areas(rendered: str) -> None:
    """Regenerate morning/day/night area markers from the encounter source."""
    _, blocks, order = split_blocks(rendered)
    areas: dict[str, dict[str, dict[str, set[str]]]] = {}

    def add(species: str, period: str, kind: str, area: str) -> None:
        if species == "SPECIES_NONE":
            return
        areas.setdefault(species, {}).setdefault(period, {}).setdefault(kind, set()).add(area)

    for encounter_id in order:
        encounter_block = blocks[encounter_id]
        mapped = dex_location(encounter_id, location_name(encounter_block))
        if mapped is None:
            continue
        kind, area = mapped
        if walkrate(encounter_block):
            for period in PERIODS:
                for line in grass_lines(encounter_block, period):
                    add(species_on_line(line), period, kind, area)
        for section in ("surf", "rock smash", "old rod", "good rod", "super rod"):
            rate_name = section.replace(" ", "") + "rate"
            rate = re.search(rf"^{rate_name}\s+(\d+)", encounter_block, re.MULTILINE)
            if not rate or int(rate.group(1)) == 0:
                continue
            for line in encounter_lines(encounter_block, section):
                for period in PERIODS:
                    add(species_on_line(line), period, kind, area)

    # HGSS shows the capture area for every member of an evolution family, not
    # only the directly encountered seed.  Propagate the same markers through
    # the single-save evolution graph so modern evolutions remain discoverable.
    edges = evolution_edges()
    changed = True
    while changed:
        changed = False
        for source, targets in edges.items():
            if source not in areas:
                continue
            for target in targets:
                before = sum(
                    len(values)
                    for by_kind in areas.get(target, {}).values()
                    for values in by_kind.values()
                )
                for period, by_kind in areas[source].items():
                    for kind, values in by_kind.items():
                        areas.setdefault(target, {}).setdefault(period, {}).setdefault(kind, set()).update(values)
                after = sum(
                    len(values)
                    for by_kind in areas.get(target, {}).values()
                    for values in by_kind.values()
                )
                changed |= after != before

    text = git_v211_areadata()
    for species in national_species():
        for period in PERIODS:
            period_constant = period.upper()
            for kind in ("specialareas", "routesandcities"):
                pattern = re.compile(
                    rf"(^[ \t]*{kind}[ \t]+{species},[ \t]+DEX_{period_constant}[ \t]*\r?\n)"
                    rf"(.*?)(^[ \t]*dexendareadata[ \t]*$)",
                    re.MULTILINE | re.DOTALL,
                )
                order = SPECIAL_DEX_ORDER if kind == "specialareas" else ROUTE_DEX_ORDER
                rank = {entry: index for index, entry in enumerate(order)}
                entries = sorted(
                    areas.get(species, {}).get(period, {}).get(kind, set()),
                    key=lambda entry: rank[entry],
                )
                body = "".join(f"    .word {entry}\n" for entry in entries)
                text, count = pattern.subn(
                    lambda match: match.group(1) + body + "    dexendareadata",
                    text,
                    count=1,
                )
                if count != 1:
                    raise RuntimeError(f"missing Pokedex block: {kind} {species} {period}")
    POKEDEX_AREAS.write_text(text, encoding="utf-8")


def duplicate_candidate(
    blocks: dict[int, str], ids: tuple[int, ...], slots: tuple[int, ...],
    reserved: set[tuple[int, str, int]], all_periods: bool,
) -> tuple[int, str, int]:
    for encounter_id in ids:
        block = blocks[encounter_id]
        if walkrate(block) == 0:
            continue
        for slot in slots:
            if all_periods:
                keys = {(encounter_id, period, slot) for period in PERIODS}
                if keys & reserved:
                    continue
                if all(
                    grass_lines(block, period).count(grass_lines(block, period)[slot]) > 1
                    for period in PERIODS
                ):
                    return encounter_id, "all", slot
            else:
                for period in PERIODS:
                    key = (encounter_id, period, slot)
                    lines = grass_lines(block, period)
                    if key not in reserved and lines.count(lines[slot]) > 1:
                        return encounter_id, period, slot
    raise RuntimeError("no duplicate encounter slot remains for allocation")


def duplicate_water_candidate(
    blocks: dict[int, str], reserved: set[tuple[int, str, int]],
) -> tuple[int, str, int]:
    for encounter_id in JOHTO_IDS:
        block = blocks[encounter_id]
        for section in ("surf", "good rod", "super rod"):
            rate_name = section.replace(" ", "") + "rate"
            rate = re.search(rf"^{rate_name}\s+(\d+)", block, re.MULTILINE)
            if not rate or int(rate.group(1)) == 0:
                continue
            lines = encounter_lines(block, section)
            species = [species_on_line(line) for line in lines]
            for slot in (2, 3, 4):
                key = (encounter_id, section, slot)
                if key not in reserved and species.count(species[slot]) > 1:
                    return encounter_id, section, slot
    raise RuntimeError("no duplicate aquatic encounter slot remains for allocation")


def main() -> None:
    baseline = git_v211_encounters()
    prefix, blocks, order = split_blocks(baseline)
    baseline_wild = sorted(wild_species(baseline))
    BASELINE_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FIXTURE.write_text(
        "# Wild species parsed from the immutable v2.1.1 encounter table.\n"
        + "\n".join(baseline_wild) + "\n",
        encoding="utf-8",
    )

    forms = form_map()
    types = species_types()
    unknown_forms = sorted(REGIONAL_FORM_SOURCES - forms.keys())
    if unknown_forms:
        raise RuntimeError("forms missing from PokeFormDataTbl.c: " + ", ".join(unknown_forms))

    assignments: list[dict[str, object]] = []
    reserved: set[tuple[int, str, int]] = set()

    def assign(encounter_id: int, period: str, slot: int, species: str, category: str) -> None:
        target_periods = PERIODS if period == "all" else (period,)
        line = source_line(species, forms)
        for target_period in target_periods:
            blocks[encounter_id] = set_grass_line(blocks[encounter_id], target_period, slot, line)
            reserved.add((encounter_id, target_period, slot))
        mapped = dex_location(encounter_id, location_name(blocks[encounter_id]))
        if mapped is None:
            raise RuntimeError(f"V2.2 assignment uses an unmapped encounter: {encounter_id}")
        assignments.append({
            "species": species,
            "encounter_id": encounter_id,
            "location": location_name(blocks[encounter_id]),
            "period": period,
            "slot": slot,
            "chance": SLOT_CHANCES[slot],
            "category": category,
            "line": line,
            "dex_kind": mapped[0],
            "dex_area": mapped[1],
        })

    def assign_water(encounter_id: int, section: str, slot: int, species: str) -> None:
        old_line = encounter_lines(blocks[encounter_id], section)[slot]
        levels = re.search(r",\s*(\d+)\s*,\s*(\d+)\s*$", old_line)
        if not levels:
            raise ValueError(f"cannot preserve levels from {old_line}")
        minimum, maximum = levels.groups()
        line = f"encounter {species}, {minimum}, {maximum}"
        blocks[encounter_id] = set_encounter_line(blocks[encounter_id], section, slot, line)
        reserved.add((encounter_id, section, slot))
        mapped = dex_location(encounter_id, location_name(blocks[encounter_id]))
        if mapped is None:
            raise RuntimeError(f"V2.2 assignment uses an unmapped encounter: {encounter_id}")
        assignments.append({
            "species": species,
            "encounter_id": encounter_id,
            "location": location_name(blocks[encounter_id]),
            "period": "all",
            "slot": slot,
            "chance": (60, 30, 5, 4, 1)[slot],
            "category": "aquatic",
            "method": section,
            "line": line,
            "dex_kind": mapped[0],
            "dex_area": mapped[1],
        })

    # User-locked early-game and fossil placements.
    assign(1, "morning", 4, "SPECIES_YAMPER", "common")
    assign(1, "day", 4, "SPECIES_YAMPER", "common")
    assign(1, "night", 6, "SPECIES_YAMPER", "uncommon")
    assign(23, "morning", 10, "SPECIES_DRACOZOLT", "fossil")
    assign(23, "morning", 11, "SPECIES_ARCTOZOLT", "fossil")
    assign(23, "day", 10, "SPECIES_DRACOVISH", "fossil")
    assign(23, "day", 11, "SPECIES_ARCTOVISH", "fossil")
    assign(23, "night", 10, "SPECIES_AERODACTYL", "fossil")

    edges = evolution_edges()
    initial_reachable = reachable(
        set(baseline_wild) | set(EXTERNAL_SOURCES) | set(REGIONAL_FORM_SOURCES), edges
    )
    incoming = {target for targets in edges.values() for target in targets}
    missing_roots = {
        species for species in national_species()
        if species not in initial_reachable and species not in incoming
    }
    # Fixed placements above already cover these roots.
    missing_roots -= {
        "SPECIES_YAMPER", "SPECIES_DRACOZOLT", "SPECIES_ARCTOZOLT",
        "SPECIES_DRACOVISH", "SPECIES_ARCTOVISH",
    }

    for species in sorted(missing_roots & WATER_ROOTS):
        encounter_id, section, slot = duplicate_water_candidate(blocks, reserved)
        assign_water(encounter_id, section, slot, species)

    for species in sorted((missing_roots & JOHTO_ROOTS) - WATER_ROOTS):
        encounter_id, period, slot = duplicate_candidate(
            blocks, JOHTO_IDS, (2, 3, 4, 5, 6, 7, 8, 9), reserved, False
        )
        assign(encounter_id, period, slot, species, "common" if slot < 6 else "uncommon")

    rare_roots = missing_roots - JOHTO_ROOTS - set(EXTERNAL_SOURCES)
    # Reserve lore-specific destinations before generic habitat allocation can
    # consume their duplicate slots (notably Zapdos and Mewtwo, alphabetically
    # late in the National Dex source list).
    fixed_rare_roots = sorted(rare_roots & set(RARE_FIXED_IDS))
    generic_rare_roots = sorted(rare_roots - set(RARE_FIXED_IDS))
    for species in fixed_rare_roots + generic_rare_roots:
        encounter_id, period, slot = duplicate_candidate(
            blocks, habitat_ids(species, types), (10, 11), reserved, True
        )
        assign(encounter_id, period, slot, species, "postgame rare")

    # Regional first stages use duplicate Johto slots. Standalone/final regional
    # forms and regional legendary birds remain rare post-game sources.
    for species in sorted(REGIONAL_FORM_SOURCES):
        if species in POSTGAME_FORM_SOURCES:
            encounter_id, period, slot = duplicate_candidate(
                blocks, habitat_ids(species, types), (10, 11), reserved, True
            )
            assign(encounter_id, period, slot, species, "functional form postgame")
        else:
            encounter_id, period, slot = duplicate_candidate(
                blocks, JOHTO_IDS, (6, 7, 8, 9), reserved, False
            )
            assign(encounter_id, period, slot, species, "functional regional form")

    rendered = prefix + "".join(blocks[encounter_id] for encounter_id in order)
    ENCOUNTERS.write_text(rendered, encoding="utf-8")
    generate_pokedex_areas(rendered)

    current_wild = wild_species(rendered)
    form_entries = [
        {
            "evolution_source": species,
            "base_species": forms[species][0],
            "form": forms[species][1],
            "method": "wild form encounter",
        }
        for species in sorted(REGIONAL_FORM_SOURCES)
    ]
    legendary_sources = [
        {key: entry[key] for key in ("species", "encounter_id", "location", "slot", "chance")}
        for entry in assignments if entry["category"] == "postgame rare"
    ]
    config = {
        "version": "2.2",
        "national_dex_count": 1025,
        "slot_chances": list(SLOT_CHANCES),
        "external_species_sources": sorted(EXTERNAL_SOURCES),
        "functional_form_sources": form_entries,
        "item_form_sources": ITEM_FORM_SOURCES,
        "evolved_wild_exceptions": sorted({
            forms[species][0]
            for species in REGIONAL_FORM_SOURCES
            if forms[species][0] in incoming
        }),
        "legendary_sources": legendary_sources,
        "encounter_sources": assignments,
        "notes": {
            "automatic_battle_forms": "not separate capture targets",
            "cosmetic_forms": "not separate capture targets",
            "frame_rate": "60 FPS hacks remain disabled",
        },
        "ability_substitutions": [
            {"species": "SPECIES_YAMPER", "original": "ABILITY_BALL_FETCH", "replacement": "ABILITY_PICKUP"},
            {"species": "SPECIES_TATSUGIRI", "original": "ABILITY_COMMANDER", "replacement": "ABILITY_STORM_DRAIN"},
            {"species": "SPECIES_ORICORIO", "original": "ABILITY_DANCER", "replacement": "ABILITY_OWN_TEMPO"},
            {"species": "SPECIES_ORICORIO_POM_POM", "original": "ABILITY_DANCER", "replacement": "ABILITY_OWN_TEMPO"},
            {"species": "SPECIES_ORICORIO_PAU", "original": "ABILITY_DANCER", "replacement": "ABILITY_OWN_TEMPO"},
            {"species": "SPECIES_ORICORIO_SENSU", "original": "ABILITY_DANCER", "replacement": "ABILITY_OWN_TEMPO"},
            {"species": "SPECIES_STUNFISK_GALARIAN", "original": "ABILITY_MIMICRY", "replacement": "ABILITY_MAGNET_PULL"},
            {"species": "SPECIES_TERAPAGOS", "original": "ABILITY_TERA_SHIFT", "replacement": "ABILITY_FILTER"},
        ],
    }
    CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # One canonical row per National Dex species plus one row per supported
    # functional form, backed by the same graph and sources as the tests.
    source_by_species = {entry["species"]: entry for entry in assignments}
    parent: dict[str, str] = {}
    seeds = current_wild | set(EXTERNAL_SOURCES) | set(REGIONAL_FORM_SOURCES)
    reached = set(seeds)
    frontier = list(sorted(seeds))
    while frontier:
        source = frontier.pop(0)
        for target in sorted(edges.get(source, set())):
            if target not in reached:
                reached.add(target)
                parent[target] = source
                frontier.append(target)

    rows: list[dict[str, object]] = []
    for species in national_species():
        if species in EXTERNAL_SOURCES:
            detail = EXTERNAL_SOURCES[species]
            rows.append({
                "scope": "species", "display_name": species,
                "base_species": species, "species": species,
                **detail, "evolution_from": "",
            })
        elif species in source_by_species:
            detail = source_by_species[species]
            rows.append({
                "scope": "species", "display_name": species,
                "base_species": species, "species": species,
                "method": "wild", "location": detail["location"],
                "period": detail["period"], "chance": f"{detail['chance']}%",
                "requirement": "post-game" if "postgame" in str(detail["category"]) else "none",
                "evolution_from": "",
            })
        elif species in baseline_wild:
            rows.append({
                "scope": "species", "display_name": species,
                "base_species": species, "species": species,
                "method": "wild (preserved v2.1.1)",
                "location": "see Wild Encounters", "period": "varies", "chance": "varies",
                "requirement": "none", "evolution_from": "",
            })
        else:
            rows.append({
                "scope": "species", "display_name": species,
                "base_species": species, "species": species,
                "method": "evolution", "location": "same save",
                "period": "any", "chance": "guaranteed", "requirement": "see Evolution Changes",
                "evolution_from": parent.get(species, ""),
            })

    for form_entry in form_entries:
        species = form_entry["evolution_source"]
        detail = source_by_species[species]
        rows.append({
            "scope": "functional_form", "display_name": species,
            "base_species": form_entry["base_species"], "species": species,
            "method": "wild form encounter", "location": detail["location"],
            "period": detail["period"], "chance": f"{detail['chance']}%",
            "requirement": "none", "evolution_from": "",
        })

    for form_entry in ITEM_FORM_SOURCES:
        rows.append({
            "scope": "functional_form", "display_name": form_entry["form_name"],
            "base_species": form_entry["base_species"], "species": "",
            "method": form_entry["method"], "location": "repeatable marts",
            "period": "any", "chance": "guaranteed",
            "requirement": form_entry["requirement"], "evolution_from": "",
        })

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=(
            "scope", "display_name", "base_species", "species", "method",
            "location", "period", "chance", "requirement", "evolution_from"
        ))
        writer.writeheader()
        writer.writerows(rows)

    unreachable = sorted(set(national_species()) - reachable(seeds, edges))
    if unreachable:
        raise RuntimeError(f"generator left {len(unreachable)} species unreachable: {unreachable[:20]}")

    print(
        f"generated {len(assignments)} encounter sources, {len(rows)} manifest rows "
        f"({len(national_species())} species + {len(rows) - len(national_species())} forms), "
        f"and preserved {len(baseline_wild)} v2.1.1 wild species"
    )


if __name__ == "__main__":
    main()
