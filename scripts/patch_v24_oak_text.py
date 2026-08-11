#!/usr/bin/env python3
"""Turn Oak's three fixed starter confirmations into one buffered template."""

from pathlib import Path
import sys


def main() -> None:
    path = Path(sys.argv[1])
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 58:
        raise SystemExit(f"expected 58 messages in bank 451, found {len(lines)}")
    expected = ("CHARMANDER", "SQUIRTLE", "BULBASAUR")
    for index, species in zip((43, 44, 45), expected):
        if species not in lines[index]:
            raise SystemExit(f"message {index} no longer contains {species}")
        lines[index] = "Do you want {STRVAR_1 0, 1, 0}? {YESNO 0}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
