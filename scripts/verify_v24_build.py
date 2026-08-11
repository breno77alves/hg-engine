#!/usr/bin/env python3
"""Post-build byte contract for HeartGold Generations v2.4."""

from __future__ import annotations

from pathlib import Path
import json
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
site_packages = next((ROOT / ".venv" / "lib").glob("python*/site-packages"))
sys.path.insert(0, str(site_packages))

from ndspy import code, codeCompression  # noqa: E402
from ndspy.narc import NARC  # noqa: E402
from ndspy.rom import NintendoDSRom  # noqa: E402


ARM9_BASE = 0x02000000
ELM_LAUNCH_HOOK = 0x0209600C
OVERLAY_61_ID = 61
OVERLAY_61_CRY_POINTER = 0x021E5E20
OVERLAY_61_TEXT_HOOK = 0x021E6D78
DYNAMIC_STARTER_TABLE = 0x02108514
CRY_PSEUDOBANK_START = 778


def main() -> None:
    base_rom_path = ROOT / "rom.nds"
    built_rom_path = ROOT / "test.nds"
    assert base_rom_path.exists() and base_rom_path.stat().st_size == 134_217_728
    assert built_rom_path.exists() and built_rom_path.stat().st_size > base_rom_path.stat().st_size

    original = NintendoDSRom.fromFile(str(base_rom_path))
    original_arm9 = codeCompression.decompress(original.arm9)
    built_arm9 = (ROOT / "base/arm9.bin").read_bytes()
    elm_offset = ELM_LAUNCH_HOOK - ARM9_BASE
    assert built_arm9[elm_offset : elm_offset + 8] != original_arm9[elm_offset : elm_offset + 8]

    overlays = code.loadOverlayTable(
        original.arm9OverlayTable,
        lambda _overlay_id, file_id: original.files[file_id],
    )
    original_overlay = overlays[OVERLAY_61_ID]
    built_overlay = (ROOT / "base/overlay/overlay_0061.bin").read_bytes()
    cry_offset = OVERLAY_61_CRY_POINTER - original_overlay.ramAddress
    text_offset = OVERLAY_61_TEXT_HOOK - original_overlay.ramAddress
    assert struct.unpack_from("<I", built_overlay, cry_offset)[0] == DYNAMIC_STARTER_TABLE
    assert built_overlay[text_offset : text_offset + 8] != original_overlay.data[text_offset : text_offset + 8]

    script_narc_id = original.filenames.idOf("a/0/1/2")
    original_script = NARC(original.files[script_narc_id]).files[740]
    built_script = (ROOT / "build/a012/2_740").read_bytes()
    assert len(built_script) > len(original_script)
    for offset in (0x0816, 0x0831, 0x08BA, 0x08D5):
        assert struct.unpack_from("<H", built_script, offset)[0] == 0x8006
    assert built_script[len(original_script) :].count(struct.pack("<H", 0x8007)) >= 3

    oak_text = (ROOT / "build/rawtext/451.txt").read_text(encoding="utf-8").splitlines()
    assert len(oak_text) == 58
    for index in (43, 44, 45):
        assert oak_text[index] == "Do you want {STRVAR_1 0, 1, 0}? {YESNO 0}"

    starter_object = ROOT / "build/random_starters.o"
    assert starter_object.exists() and starter_object.stat().st_size < 8192

    sound_data = (ROOT / "base/root/data/sound/gs_sound_data.sdat").read_bytes()
    block_count = struct.unpack_from("<H", sound_data, 14)[0]
    header_position = 16 + (8 if block_count == 4 else 0)
    info_offset = struct.unpack_from("<I", sound_data, header_position)[0]
    wavarc_relative = struct.unpack_from("<I", sound_data, info_offset + 8 + (3 * 4))[0]
    wavarc_count = struct.unpack_from("<I", sound_data, info_offset + wavarc_relative)[0]
    manifest = json.loads((ROOT / "data/random_starters.json").read_text(encoding="utf-8"))
    cry_indices = [
        entry["id"] if entry["id"] <= 493 else entry["id"] + CRY_PSEUDOBANK_START - 544
        for entry in manifest["pool"]
    ]
    assert max(cry_indices) < wavarc_count

    print("PASS: final hooks, Oak flow, starter budget and every pool cry exist in the v2.4 build")


if __name__ == "__main__":
    main()
