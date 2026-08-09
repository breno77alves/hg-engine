#!/usr/bin/env python3

"""Verify the Hall of Fame trainer portrait is generated as scanned 4bpp data."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
NARCS_MK = ROOT / "narcs.mk"


def main() -> int:
    source = NARCS_MK.read_text(encoding="utf-8")
    rule = re.search(
        r"\$\(TRAINER_GFX_DIR\)/8_%\-04\.NCGR:[^\n]+\n\s*\$\(GFX\)([^\n]+)",
        source,
    )
    if not rule:
        print("FAIL: trainer encounter portrait rule not found", file=sys.stderr)
        return 1

    arguments = rule.group(1).split()
    required = {"-bitdepth", "4", "-scanned", "-mwidth", "20"}
    forbidden = {"-clobbersize", "-version101", "-scanfronttoback"}
    missing = sorted(required.difference(arguments))
    present = sorted(forbidden.intersection(arguments))

    if missing or present:
        print(
            f"FAIL: missing={missing or 'none'} forbidden={present or 'none'}",
            file=sys.stderr,
        )
        return 1

    print("PASS: Hall of Fame portrait rule uses scanned 4bpp generation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
