#!/usr/bin/env python3
"""Generate the audited v2.4 starter manifest and C initializer."""

from __future__ import annotations

import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPECIES_H = ROOT / "include/constants/species.h"
MOVES_H = ROOT / "include/constants/moves.h"
MONDATA = ROOT / "armips/data/mondata.s"
EVODATA = ROOT / "armips/data/evodata.s"
LEVELUP = ROOT / "armips/data/levelupdata.s"
EGGMOVES = ROOT / "armips/data/eggmoves.s"
TMLEARNSET = ROOT / "armips/data/tmlearnset.txt"
TUTORDATA = ROOT / "armips/data/tutordata.txt"
MOVES = ROOT / "armips/data/moves.s"
POKEGRA = ROOT / "data/graphics/pokegra.mk"
OVERWORLDS = ROOT / "armips/data/monoverworlds.s"
ICONS = ROOT / "armips/data/iconpalettetable.s"


EXPLICIT_SPECIAL = {
    # Correct the engine macros (which accidentally classify Shiinotic and omit Marshadow).
    "MEW", "CELEBI", "JIRACHI", "DEOXYS", "PHIONE", "MANAPHY", "DARKRAI",
    "SHAYMIN", "ARCEUS", "VICTINI", "KELDEO", "MELOETTA", "GENESECT",
    "DIANCIE", "HOOPA", "VOLCANION", "MARSHADOW", "MAGEARNA", "ZERAORA",
    "MELTAN", "MELMETAL", "ZARUDE", "PECHARUNT",
    "GOUGING_FIRE", "RAGING_BOLT", "IRON_BOULDER", "IRON_CROWN",
}
UNSAFE_MOVES = {
    "GUILLOTINE", "HORN_DRILL", "FISSURE", "SHEER_COLD", "SELF_DESTRUCT",
    "EXPLOSION", "MEMENTO", "FINAL_GAMBIT", "MISTY_EXPLOSION", "STEEL_BEAM",
    "MIND_BLOWN", "HEALING_WISH", "LUNAR_DANCE", "LAST_RESORT", "SUCKER_PUNCH",
    "DREAM_EATER", "SNORE", "FOCUS_PUNCH", "BIDE", "COUNTER", "MIRROR_COAT",
    "METAL_BURST", "ENDEAVOR", "REVERSAL", "FLAIL", "PRESENT",
}


def direct_constants(path: Path, prefix: str) -> tuple[dict[str, int], dict[int, str]]:
    by_name: dict[str, int] = {}
    by_id: dict[int, str] = {}
    for name, raw in re.findall(rf"^#define\s+{prefix}([A-Z0-9_]+)\s+(\d+)\b", path.read_text(encoding="utf-8"), re.MULTILINE):
        value = int(raw)
        by_name[name] = value
        by_id[value] = name
    return by_name, by_id


def blocks(path: Path, directive: str) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    found = list(re.finditer(rf"^{directive}\s+SPECIES_([A-Z0-9_]+).*?$", text, re.MULTILINE))
    return {
        ("MIME_JR" if match.group(1) == "MIMEJR" else match.group(1)): text[match.start() : found[index + 1].start() if index + 1 < len(found) else len(text)]
        for index, match in enumerate(found)
    }


def extract_special_names() -> set[str]:
    text = (ROOT / "include/pokemon.h").read_text(encoding="utf-8")
    section = text[text.index("#define IS_SPECIES_LEGENDARY"):text.index("// personal narc fields")]
    names = set(re.findall(r"SPECIES_([A-Z0-9_]+)", section))
    names.discard("SHIINOTIC")
    names.update(EXPLICIT_SPECIAL)
    return names


def evolution_paths(root: str, edges: dict[str, list[str]]) -> list[list[str]]:
    result: list[list[str]] = []

    def visit(node: str, path: list[str], seen: set[str]) -> None:
        targets = [target for target in edges.get(node, []) if target not in seen]
        if not targets:
            if path:
                result.append(path)
            return
        for target in targets:
            visit(target, path + [target], seen | {target})

    visit(root, [], {root})
    unique: list[list[str]] = []
    for path in result:
        if path not in unique:
            unique.append(path)
    return unique


def main() -> None:
    species_by_name, species_by_id = direct_constants(SPECIES_H, "SPECIES_")
    moves_by_name, _ = direct_constants(MOVES_H, "MOVE_")
    mon_blocks = blocks(MONDATA, "mondata")
    evo_blocks = blocks(EVODATA, "evodata")
    level_blocks = blocks(LEVELUP, "levelup")
    egg_blocks = blocks(EGGMOVES, "eggmoveentry")

    canonical = {
        name: number for name, number in species_by_name.items()
        if 1 <= number <= 1075 and not 494 <= number <= 543
    }
    assert len(canonical) == 1025, len(canonical)

    types: dict[str, tuple[str, str]] = {}
    for name in canonical:
        match = re.search(r"^\s+types\s+(.+)$", mon_blocks[name], re.MULTILINE)
        if not match:
            raise AssertionError(f"missing types for {name}")
        fields = match.group(1).split(",", 1)
        parsed = []
        for field in fields:
            candidates = [value for value in re.findall(r"TYPE_([A-Z]+)", field) if value != "IMPLEMENTED"]
            parsed.append(candidates[0] if candidates else None)
        if len(parsed) != 2 or any(value is None for value in parsed):
            raise AssertionError(f"unparseable types for {name}: {match.group(1)}")
        types[name] = (parsed[0], parsed[1])

    edges: dict[str, list[str]] = {}
    for name, body in evo_blocks.items():
        edges[name] = [
            ("MIME_JR" if target == "MIMEJR" else target) for method, target in re.findall(
                r"^\s+evolution\s+(EVO_[A-Z0-9_]+),\s*[^,]+,\s*SPECIES_([A-Z0-9_]+)", body, re.MULTILINE
            ) if method != "EVO_NONE" and target != "NONE"
        ]
    incoming = {target for targets in edges.values() for target in targets}

    move_text = MOVES.read_text(encoding="utf-8")
    move_matches = list(re.finditer(r"^movedata\s+MOVE_([A-Z0-9_]+),", move_text, re.MULTILINE))
    move_blocks = {
        match.group(1): move_text[match.start():move_matches[index + 1].start() if index + 1 < len(move_matches) else len(move_text)]
        for index, match in enumerate(move_matches)
    }
    move_info: dict[str, tuple[int, int, str]] = {}
    for name, body in move_blocks.items():
        power = re.search(r"^\s+basepower\s+(\d+)", body, re.MULTILINE)
        accuracy = re.search(r"^\s+accuracy\s+(\d+)", body, re.MULTILINE)
        move_type = re.search(r"^\s+type\s+TYPE_([A-Z]+)", body, re.MULTILINE)
        if power and accuracy and move_type:
            move_info[name] = (int(power.group(1)), int(accuracy.group(1)), move_type.group(1))

    pokegra = POKEGRA.read_text(encoding="utf-8")
    overworlds = OVERWORLDS.read_text(encoding="utf-8")
    icons = ICONS.read_text(encoding="utf-8")
    special = extract_special_names()
    for first, last in (("NIHILEGO", "BLACEPHALON"), ("GREAT_TUSK", "IRON_THORNS")):
        first_id = species_by_name[first]
        last_id = species_by_name[last]
        special.update(species_by_id[number] for number in range(first_id, last_id + 1))
    tm_text = TMLEARNSET.read_text(encoding="utf-8")
    tutor_text = TUTORDATA.read_text(encoding="utf-8")
    tm_matches = list(re.finditer(r"^TM\d+:\s+MOVE_([A-Z0-9_]+)", tm_text, re.MULTILINE))
    tutor_matches = list(re.finditer(r"^TUTOR_[A-Z0-9_]+:\s+MOVE_([A-Z0-9_]+)", tutor_text, re.MULTILINE))

    def compatible_moves(text: str, matches: list[re.Match[str]], species: str) -> list[str]:
        result: list[str] = []
        for index, match in enumerate(matches):
            body = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
            if re.search(rf"^\s+SPECIES_{re.escape(species)}\s*$", body, re.MULTILINE):
                result.append(match.group(1))
        return result

    pool: list[dict] = []
    rejected_no_safe_move: list[str] = []

    for number, name in sorted(species_by_id.items()):
        if name not in canonical or name in special or name in incoming or not edges.get(name):
            continue
        paths = evolution_paths(name, edges)
        if not paths:
            continue

        primary, secondary = types[name]
        data_name = "MIMEJR" if name == "MIME_JR" else name
        level_moves = [move for move, _level in re.findall(r"^\s+learnset\s+MOVE_([A-Z0-9_]+),\s*(\d+)", level_blocks.get(name, ""), re.MULTILINE)]
        egg_moves = re.findall(r"^\s+eggmove\s+MOVE_([A-Z0-9_]+)", egg_blocks.get(name, ""), re.MULTILINE)
        move_sources = (
            ("level-up", level_moves),
            ("egg", egg_moves),
            ("tm-hm", compatible_moves(tm_text, tm_matches, data_name)),
            ("tutor", compatible_moves(tutor_text, tutor_matches, data_name)),
        )
        safe_move = ""
        safe_source = ""
        for source_name, source_moves in move_sources:
            legal: list[tuple[str, int, int, str, int]] = []
            for order, move in enumerate(source_moves):
                power, accuracy, move_type = move_info.get(move, (0, 0, ""))
                if power > 0 and move not in UNSAFE_MOVES:
                    legal.append((move, power, accuracy, move_type, order))
            if not legal:
                continue
            legal.sort(key=lambda item: (
                item[3] in (primary, secondary),
                item[2] == 0 or item[2] >= 90,
                35 <= item[1] <= 60,
                -item[4],
            ), reverse=True)
            safe_move = legal[0][0]
            safe_source = source_name
            break
        if not safe_move:
            rejected_no_safe_move.append(f"SPECIES_{name}")
            continue

        number4 = f"{number:04d}"
        sprite = f"build/pokemonpic/{number4}-02.NCGR:" in pokegra or f"build/pokemonpic/{number4}-03.NCGR:" in pokegra
        icon = f"build/pokemonicon/1_{number4}.NCGR:" in pokegra
        follower = re.search(rf"^overworlddata\s+[^\n]+// SPECIES_{re.escape(data_name)}\s*$", overworlds, re.MULTILINE) is not None
        icon_palette = f"SPECIES_{data_name}" in icons
        if not (sprite and icon and follower and icon_palette):
            raise AssertionError(f"missing starter resources for {name}: sprite={sprite} icon={icon} follower={follower} palette={icon_palette}")

        pool.append({
            "id": number,
            "species": f"SPECIES_{name}",
            "primary_type": primary,
            "secondary_type": secondary,
            "first_form": True,
            "has_evolution": True,
            "special_category": False,
            "alternate_form": False,
            "resources": {"sprite": True, "icon": True, "cry": True, "follower": True},
            "safe_move": moves_by_name[safe_move],
            "safe_move_name": f"MOVE_{safe_move}",
            "safe_move_source": safe_source,
            "evolution_paths": [[f"SPECIES_{value}" for value in path] for path in paths],
        })

    manifest = {
        "version": "v2.4",
        "algorithm": "mix32-v1",
        "canonical_count": 1025,
        "internal_species_range": [1, 1075],
        "excluded_internal_gap": [494, 543],
        "rejected_no_safe_move": rejected_no_safe_move,
        "pool": pool,
    }
    (ROOT / "data/random_starters.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = ["/* Autogenerated by scripts/generate_v24_starter_pool.py. */"]
    for entry in pool:
        lines.append("    { %s, %s }," % (entry["species"], entry["safe_move_name"]))
    (ROOT / "include/random_starter_pool.inc").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated {len(pool)} eligible starter families")


if __name__ == "__main__":
    main()
