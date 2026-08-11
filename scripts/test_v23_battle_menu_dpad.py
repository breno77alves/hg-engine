#!/usr/bin/env python3
"""Regression contract for RUN + Up on the battle command menu."""

from pathlib import Path
import argparse
import re


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "armips" / "asm" / "battle_menu_dpad.s"
GLOBAL_ASM = ROOT / "armips" / "global.s"
BATTLE_INPUT = ROOT / "src" / "battle" / "battle_input.c"

RUN_UP_BRANCH = 0x02269B5C
OVERLAY_BASE = 0x022378C0
ORIGINAL_BRANCH = bytes.fromhex("23 d1")
PATCHED_NOP = bytes.fromhex("c0 46")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expect",
        choices=("auto", "vanilla", "built"),
        default="auto",
        help="expected state of the extracted overlay bytes",
    )
    args = parser.parse_args()

    overlay = (ROOT / "base" / "overlay" / "overlay_0012.bin").read_bytes()
    offset = RUN_UP_BRANCH - OVERLAY_BASE
    actual = overlay[offset : offset + 2]
    expected = {
        "vanilla": (ORIGINAL_BRANCH,),
        "built": (PATCHED_NOP,),
        "auto": (ORIGINAL_BRANCH, PATCHED_NOP),
    }[args.expect]
    assert actual in expected, (
        f"unexpected RUN+Up bytes: {actual.hex(' ')}; "
        f"expected one of {[value.hex(' ') for value in expected]}"
    )

    patch = PATCH.read_text(encoding="utf-8")
    assert '.open "base/overlay/overlay_0012.bin", 0x022378C0' in patch
    assert ".org 0x02269B5C" in patch
    assert "nop" in patch
    assert '.include "armips/asm/battle_menu_dpad.s"' in GLOBAL_ASM.read_text(
        encoding="utf-8"
    )

    battle_input = BATTLE_INPUT.read_text(encoding="utf-8")
    assert "DPadSelectTouchDataIndexActive[TOUCH_DATA_MEGA]" in battle_input
    assert "0x02269B5C" not in battle_input
    assert not re.search(
        r"\*\s*\(\s*u32\s*\*\s*\)\s*\(\s*0x02269F4C\s*\)", battle_input
    )

    print("PASS: RUN + Up reaches FIGHT without touching Mega/JIT state")


if __name__ == "__main__":
    main()
