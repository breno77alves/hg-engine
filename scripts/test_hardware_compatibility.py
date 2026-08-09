#!/usr/bin/env python3
"""Static contract for the current DSpico/TWiLight/R4 antipiracy patch."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    config = read("include/config.h")
    assert re.search(r"^#define APPLY_ANTIPIRACY\b", config, re.M)

    armips_config = read("armips/include/config.s")
    assert ".definelabel APPLY_ANTIPIRACY" not in armips_config
    global_asm = read("armips/global.s")
    assert 'include "armips/asm/antipiracy.s"' not in global_asm
    assert not (ROOT / "armips/asm/antipiracy.s").exists()

    replacements = read("bytereplacement")
    ap = replacements.split("#ifdef APPLY_ANTIPIRACY", 1)[1].split("#endif", 1)[0]
    assert "0001 021E662C 01 20 70 47" in ap
    assert "0123 0225F0CC E0 FC FF FF" in ap
    assert "0123 0225F184 E0 FC FF FF" in ap
    assert "arm9 02000A18 1E FF 2F E1" in replacements

    make_script = read("scripts/make.py")
    match = re.search(r"OVERLAYS_TO_DECOMPRESS = \[(.*?)\]", make_script)
    assert match and "123" in {value.strip() for value in match.group(1).split(",")}

    synthetic = read("armips/asm/syntheticoverlay.s")
    assert ".area 0x02110358-." in synthetic and ".endarea" in synthetic
    assert ".org 0x21102C4" not in synthetic

    armips_options = read("armips/include/config.s")
    assert re.search(r"ALWAYS_UNCAPPED_FRAME_RATE equ 0\b", armips_options)
    assert re.search(r"BATTLES_UNCAPPED_FRAME_RATE equ 0\b", armips_options)

    print("PASS: current non-runtime antipiracy patch is installed without 60 FPS hacks")


if __name__ == "__main__":
    main()
