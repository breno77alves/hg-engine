#!/usr/bin/env python3
"""Ensure V2.2 never requires a real link trade for evolution."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    text = (ROOT / "armips/data/evodata.s").read_text(encoding="utf-8")
    trade_only: list[str] = []
    for match in re.finditer(
        r"^evodata\s+(SPECIES_[A-Z0-9_]+)\s*(.*?)(?=^terminateevodata)",
        text,
        re.MULTILINE | re.DOTALL,
    ):
        species, block = match.groups()
        if "EVO_TRADE" not in block:
            continue
        alternatives = (
            "ITEM_LINKING_CORD" in block
            or "EVO_LEVEL" in block
            or "EVO_STONE" in block
            or "EVO_ITEM" in block
        )
        if not alternatives:
            trade_only.append(species)

    if trade_only:
        print(
            "FAIL: trade-only evolutions remain: " + ", ".join(trade_only),
            file=sys.stderr,
        )
        return 1

    print("PASS: every trade evolution has a single-save alternative")
    return 0


if __name__ == "__main__":
    sys.exit(main())
