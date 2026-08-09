#!/usr/bin/env python3

"""Regression contracts for generation-specific Critical Capture behavior."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "include/config.h"
CAPTURE = ROOT / "src/individual/CalculateBallShakes.c"

CRITICAL_CAPTURE_MASK = 0x80


def finalize_shakes(
    shakes: int,
    generation: int,
    critical_capture_enabled: bool,
    species_already_caught: bool,
) -> int:
    if (
        critical_capture_enabled
        and generation >= 9
        and species_already_caught
        and shakes in (4, 1 | CRITICAL_CAPTURE_MASK)
    ):
        return 1 | CRITICAL_CAPTURE_MASK
    return shakes & ~CRITICAL_CAPTURE_MASK


def main() -> int:
    try:
        config = CONFIG.read_text(encoding="utf-8")
        capture = CAPTURE.read_text(encoding="utf-8")

        assert re.search(
            r"#define\s+CRITICAL_CAPTURE_GENERATION\s+GEN_LATEST", config
        ), "Critical Capture must expose a configured mechanics generation"
        assert re.search(
            r"#if\s+CRITICAL_CAPTURE_GENERATION\s*>=\s*9.*?"
            r"Pokedex_CountJohtoDexOwned.*?#else.*?Pokedex_CountDexOwned.*?#endif",
            capture,
            re.DOTALL,
        ), "Gen 9 Critical Capture must use the regional caught-species count"

        final_override = re.search(
            r"#else\s*\n"
            r"\s*// if the capture is successful,.*?"
            r"return\s+i\s*&\s*~CRITICAL_CAPTURE_MASK;",
            capture,
            re.DOTALL,
        )
        assert final_override, "final Critical Capture animation override not found"
        assert re.search(
            r"#if\s+defined\(IMPLEMENT_CRITICAL_CAPTURE\)\s*&&\s*"
            r"CRITICAL_CAPTURE_GENERATION\s*>=\s*9",
            final_override.group(0),
        ), "the already-caught animation override must be restricted to Gen 9+"

        assert finalize_shakes(4, 8, True, True) == 4
        assert finalize_shakes(4, 9, True, True) == (1 | CRITICAL_CAPTURE_MASK)
        assert finalize_shakes(2, 9, True, True) == 2
        assert finalize_shakes(4, 9, False, True) == 4
        assert finalize_shakes(4, 9, True, False) == 4
    except (AssertionError, OSError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Critical Capture animation obeys its configured generation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
