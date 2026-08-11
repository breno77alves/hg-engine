#!/usr/bin/env python3
"""Contract for the seven interaction-driven automatic HMs."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

CONTEXTUAL_HMS = (
    "MOVE_CUT",
    "MOVE_SURF",
    "MOVE_STRENGTH",
    "MOVE_ROCK_SMASH",
    "MOVE_WHIRLPOOL",
    "MOVE_WATERFALL",
    "MOVE_ROCK_CLIMB",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    source = read("src/automatic_hm.c")
    hooks = read("hooks")

    # Script command 141 is the vanilla shared "find this move in the party"
    # gate used by the obstacle scripts.  Hooking it once preserves each
    # script's original map/story/state checks and field animation.
    assert re.search(
        r"^arm9\s+ScrCmd_CheckMoveInParty_AutomaticHm\s+0204D3CC\s+1$",
        hooks,
        re.MULTILINE,
    )
    for move in CONTEXTUAL_HMS:
        assert re.search(rf"\{{\s*{move},", source), f"missing {move} rule"

    # Fly deliberately has a separate bag entry point; non-HM moves must still
    # take the exact learned-move fallback.
    assert "MOVE_FLY" in source
    assert "MonHasMove" in source
    assert "if (rule == NULL)" in source

    print("PASS: seven contextual HMs share the automatic gate; vanilla field checks remain upstream")


if __name__ == "__main__":
    main()
