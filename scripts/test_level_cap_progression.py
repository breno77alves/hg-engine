#!/usr/bin/env python3

"""Regression contracts for post-Red level caps and cap-bound evolution."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
POKEMON = ROOT / "src/pokemon.c"
EVOLUTION = ROOT / "src/individual/GetMonEvolutionInternal.c"


def function_body(source: str, name: str) -> str:
    start = re.search(rf"\b{name}\s*\([^)]*\)\s*\{{", source)
    assert start, f"function not found: {name}"
    depth = 0
    for index in range(start.end() - 1, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start.start() : index + 1]
    raise AssertionError(f"unterminated function: {name}")


def effective_cap(stored_cap: int, red_defeated: bool) -> int:
    cap = stored_cap if 1 <= stored_cap <= 100 else 100
    if red_defeated and cap < 100:
        cap = 100
    return cap


def main() -> int:
    try:
        config = CONFIG.read_text(encoding="utf-8")
        pokemon = POKEMON.read_text(encoding="utf-8")
        evolution = EVOLUTION.read_text(encoding="utf-8")

        for enabled_macro in (
            "IMPLEMENT_LEVEL_CAP",
            "ALLOW_LEVEL_CAP_EVOLVE",
        ):
            assert re.search(
                rf"^\s*#define\s+{enabled_macro}\b", config, re.MULTILINE
            ), f"{enabled_macro} must be enabled"

        assert not re.search(
            r"^\s*#define\s+UNCAP_CANDIES_FROM_LEVEL_CAP\b",
            config,
            re.MULTILINE,
        ), "candies must not be allowed to exceed the hard cap"
        assert re.search(
            r"^\s*#define\s+LEVEL_CAP_RED_DEFEATED_VARIABLE\s+0x40FD\b",
            config,
            re.MULTILINE,
        ), "the persistent vanilla Red-defeated variable must be documented"
        assert re.search(
            r"^\s*#define\s+LEVEL_CAP_AFTER_RED\s+100\b",
            config,
            re.MULTILINE,
        ), "the post-Red cap must be 100"

        get_cap = function_body(pokemon, "GetLevelCap")
        assert re.search(
            r"GetScriptVar\(LEVEL_CAP_RED_DEFEATED_VARIABLE\)\s*!=\s*0",
            get_cap,
        ), "GetLevelCap must recognize the persistent post-Red state"
        assert re.search(
            r"levelCap\s*<\s*LEVEL_CAP_AFTER_RED",
            get_cap,
        ), "the post-Red safeguard must only prevent a cap decrease"
        assert re.search(
            r"levelCap\s*=\s*LEVEL_CAP_AFTER_RED",
            get_cap,
        ), "an Elite Four rematch must not leave a post-Red save capped at 65"

        assert re.search(
            r"defined\(IMPLEMENT_LEVEL_CAP\)\s*&&\s*"
            r"defined\(ALLOW_LEVEL_CAP_EVOLVE\).*?"
            r"level\s*==\s*GetLevelCap\(\).*?"
            r"usedItem\s*==\s*ITEM_RARE_CANDY",
            evolution,
            re.DOTALL,
        ), "a Rare Candy at the active cap must be allowed to trigger evolution"

        assert effective_cap(65, False) == 65
        assert effective_cap(65, True) == 100
        assert effective_cap(100, True) == 100
        assert effective_cap(0, False) == 100
        assert effective_cap(101, False) == 100
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: post-Red rematches cannot lower the cap and cap evolution is enabled")
    return 0


if __name__ == "__main__":
    sys.exit(main())
