#!/usr/bin/env python3
"""Reject empty/Bulbasaur placeholder assets for every canonical Gen 9 species."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
SPECIES = ROOT / "include/constants/species.h"
MONDATA = ROOT / "armips/data/mondata.s"
POKEGRA = ROOT / "data/graphics/pokegra.mk"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def battle_png_format(path: Path) -> tuple[int, int, int, int]:
    data = path.read_bytes()[:29]
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return 0, 0, 0, 0
    return struct.unpack(">IIBB", data[16:26])


def main() -> int:
    constants = {
        int(number): name
        for name, number in re.findall(
            r"^#define\s+SPECIES_([A-Z0-9_]+)\s+(\d+)$",
            SPECIES.read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        if 956 <= int(number) <= 1075
    }
    assert len(constants) == 120, "expected all 120 canonical Gen 9 species"

    mondata = MONDATA.read_text(encoding="utf-8")
    ratios = {
        name: int(ratio)
        for name, ratio in re.findall(
            r"^mondata\s+SPECIES_([A-Z0-9_]+),.*?^\s+genderratio\s+(\d+)",
            mondata,
            re.MULTILINE | re.DOTALL,
        )
    }

    rules: dict[int, dict[str, Path]] = {}
    for line in POKEGRA.read_text(encoding="utf-8").splitlines():
        picture = re.match(
            r"^build/pokemonpic/(\d{4})-(00|01|02|03)\.NCGR:\s+(.+)$", line
        )
        icon = re.match(r"^build/pokemonicon/1_(\d{4})\.NCGR:\s+(.+)$", line)
        if picture:
            number = int(picture.group(1))
            if number in constants:
                rules.setdefault(number, {})[picture.group(2)] = ROOT / picture.group(3)
        elif icon:
            number = int(icon.group(1))
            if number in constants:
                rules.setdefault(number, {})["icon"] = ROOT / icon.group(2)

    placeholder_hashes = {
        digest(ROOT / "data/graphics/sprites/bulbasaur/male/front.png"),
        digest(ROOT / "data/graphics/sprites/bulbasaur/male/back.png"),
        digest(ROOT / "data/graphics/sprites/none/icon.png"),
    }
    failures: list[str] = []
    for number, species in sorted(constants.items()):
        ratio = ratios[species]
        if ratio == 254:  # female only
            required = ("00", "02", "icon")
        elif ratio in (0, 255):  # male only or genderless
            required = ("01", "03", "icon")
        else:
            required = ("00", "01", "02", "03", "icon")

        for slot in required:
            path = rules.get(number, {}).get(slot)
            if path is None or not path.is_file():
                failures.append(f"SPECIES_{species}: missing slot {slot}")
            elif path.stat().st_size == 0:
                failures.append(f"SPECIES_{species}: empty slot {slot}")
            elif digest(path) in placeholder_hashes:
                failures.append(f"SPECIES_{species}: placeholder slot {slot}")
            elif slot != "icon" and battle_png_format(path) != (160, 80, 4, 3):
                failures.append(
                    f"SPECIES_{species}: slot {slot} must be a 160x80 4bpp indexed PNG"
                )

    if failures:
        print("FAIL: Gen 9 placeholder assets remain:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("PASS: all 120 canonical Gen 9 species use non-placeholder battle sprites and icons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
