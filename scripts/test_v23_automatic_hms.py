#!/usr/bin/env python3
"""Source contract for item-gated automatic HGSS field HMs."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_RULES = {
    "MOVE_CUT": ("ITEM_HM01", "BADGE_HIVE"),
    "MOVE_FLY": ("ITEM_HM02", "BADGE_STORM"),
    "MOVE_SURF": ("ITEM_HM03", "BADGE_FOG"),
    "MOVE_STRENGTH": ("ITEM_HM04", "BADGE_PLAIN"),
    "MOVE_WHIRLPOOL": ("ITEM_HM05", "BADGE_GLACIER"),
    "MOVE_ROCK_SMASH": ("ITEM_HM06", "BADGE_ZEPHYR"),
    "MOVE_WATERFALL": ("ITEM_HM07", "BADGE_RISING"),
    "MOVE_ROCK_CLIMB": ("ITEM_HM08", "BADGE_EARTH"),
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    header = read("include/automatic_hm.h")
    source = read("src/automatic_hm.c")
    hooks = read("hooks")

    assert "struct AutomaticHmRule" in header
    assert "IsAutomaticHm" in header
    assert "HasAutomaticHmAccess" in header
    assert "SelectAutomaticHmActor" in header
    assert "ScrCmd_CheckMoveInParty_AutomaticHm" in header

    for move, (item, badge) in EXPECTED_RULES.items():
        assert re.search(rf"\{{\s*{move},\s*{item},\s*{badge}\s*\}}", source)

    assert "Bag_HasItem" in source
    assert "PlayerProfile_TestBadgeFlag" in source
    assert "MON_DATA_IS_EGG" in source
    assert "MonHasMove" in source, "non-HM fallback must remain vanilla-compatible"
    assert "ScrCmd_CheckMoveInParty_AutomaticHm" in hooks
    assert "ALLOW_SAVE_CHANGES" not in source

    print("PASS: automatic HMs require item, badge, and a non-egg visual actor")


if __name__ == "__main__":
    main()
