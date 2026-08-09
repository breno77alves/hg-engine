#!/usr/bin/env python3

"""Regression checks for the battle move-menu D-pad pointer.

The vanilla overlay keeps the move-grid address in a literal pool at 0x02269F4C.
Changing that literal while the overlay is executing can leave a JIT-compiled block
using stale state. V2.1 must repoint the literal during ROM construction and only
mutate ordinary table data at runtime.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BATTLE_INPUT = ROOT / "src" / "battle" / "battle_input.c"
REPOINTS = ROOT / "repoints"
LINKED_OBJECT = ROOT / "build" / "battle_linked.o"
OVERLAY = ROOT / "base" / "overlay" / "overlay_0012.bin"

OVERLAY_RAM_ADDRESS = 0x022378C0
DPAD_LITERAL_ADDRESS = 0x02269F4C
VANILLA_MAP_ADDRESS = 0x0226E218
EXPECTED_VANILLA_MAP = bytes((1, 2, 3, 4, 0, 0))
EXPECTED_MEGA_MAP = bytes((1, 2, 3, 4, 0, 5))


def source_initializer(source: str, symbol: str) -> bytes:
    match = re.search(
        rf"\b{re.escape(symbol)}\s*\[\s*\]\s*=\s*\{{([^}}]+)\}}", source
    )
    assert match, f"missing initializer for {symbol}"
    return bytes(int(value) for value in re.findall(r"\b\d+\b", match.group(1)))


def check_source_contract() -> None:
    source = BATTLE_INPUT.read_text(encoding="utf-8")
    pointers = REPOINTS.read_text(encoding="utf-8")

    assert "DPadSelectTouchDataIndexVanilla" in source, "missing vanilla map"
    assert "DPadSelectTouchDataIndexMega" in source, "missing Mega map"
    assert re.search(
        r"\bu8\s+DPadSelectTouchDataIndexActive\s*\[", source
    ), "active map must be mutable data"
    assert (
        "SetDPadSelectTouchDataIndexActive" in source
    ), "callbacks must update the active map"
    assert (
        source_initializer(source, "DPadSelectTouchDataIndexVanilla")
        == EXPECTED_VANILLA_MAP
    )
    assert (
        source_initializer(source, "DPadSelectTouchDataIndexMega")
        == EXPECTED_MEGA_MAP
    )
    assert (
        source_initializer(source, "DPadSelectTouchDataIndexActive")
        == EXPECTED_VANILLA_MAP
    )
    assert not re.search(
        r"\*\s*\(\s*u32\s*\*\s*\)\s*\(\s*0x02269F4C\s*\)", source
    ), "runtime writes to the overlay literal are forbidden"
    assert (
        "0012 DPadSelectTouchDataIndexActive 02269F4C" in pointers
    ), "the overlay literal must be repointed at ROM construction time"


def find_nm() -> str:
    executable = "arm-none-eabi-nm.exe" if os.name == "nt" else "arm-none-eabi-nm"
    found = shutil.which(executable)
    if found:
        return found

    devkitarm = os.environ.get("DEVKITARM")
    if devkitarm:
        candidate = Path(devkitarm) / "bin" / executable
        if candidate.is_file():
            return str(candidate)

    raise AssertionError("arm-none-eabi-nm is required for built-ROM verification")


def linked_symbol_address(symbol: str) -> int:
    assert LINKED_OBJECT.is_file(), f"missing linked object: {LINKED_OBJECT}"
    output = subprocess.check_output([find_nm(), str(LINKED_OBJECT)], text=True)
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[-1] == symbol:
            return int(fields[0], 16)
    raise AssertionError(f"symbol not found: {symbol}")


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def check_built_overlay(path: Path) -> None:
    overlay = path.read_bytes()
    literal_offset = DPAD_LITERAL_ADDRESS - OVERLAY_RAM_ADDRESS
    pointer = read_u32(overlay, literal_offset)
    active_address = linked_symbol_address("DPadSelectTouchDataIndexActive")
    assert pointer == active_address, (
        f"D-pad literal points to 0x{pointer:08X}, expected active table "
        f"0x{active_address:08X}"
    )


def check_vanilla_overlay(path: Path) -> None:
    overlay = path.read_bytes()
    literal_offset = DPAD_LITERAL_ADDRESS - OVERLAY_RAM_ADDRESS
    pointer = read_u32(overlay, literal_offset)
    assert pointer == VANILLA_MAP_ADDRESS

    table_offset = VANILLA_MAP_ADDRESS - OVERLAY_RAM_ADDRESS
    assert overlay[table_offset : table_offset + 6] == EXPECTED_VANILLA_MAP


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--overlay", type=Path, default=OVERLAY, help="decompressed overlay 12"
    )
    parser.add_argument(
        "--expect-vanilla", action="store_true", help="expect the original pointer"
    )
    parser.add_argument(
        "--expect-built", action="store_true", help="expect the linked active table"
    )
    args = parser.parse_args()

    try:
        check_source_contract()
        if args.expect_vanilla:
            check_vanilla_overlay(args.overlay)
        if args.expect_built:
            check_built_overlay(args.overlay)
    except (AssertionError, OSError, subprocess.SubprocessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: D-pad literal is static and uses the mutable active table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
