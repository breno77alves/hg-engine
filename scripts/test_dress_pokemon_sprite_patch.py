#!/usr/bin/env python3
"""Verify the Dress Pokemon screen uses the HGSS pokepic unscan path."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    global_asm = (ROOT / "armips/global.s").read_text(encoding="utf-8")
    patch_asm = (ROOT / "armips/asm/sprites.s").read_text(encoding="utf-8")

    if '.include "armips/asm/sprites.s"' not in global_asm:
        print("FAIL: Dress Pokemon sprite patch is not included by armips/global.s", file=sys.stderr)
        return 1

    expected_patch = re.compile(
        r"\.org\s+0x02009D2A\s+nop\s+nop\b",
        re.IGNORECASE | re.MULTILINE,
    )
    if not expected_patch.search(patch_asm):
        print("FAIL: expected two-NOP pokepic unscan patch was not found", file=sys.stderr)
        return 1

    print("PASS: Dress Pokemon sprites use the HGSS pokepic unscan path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
