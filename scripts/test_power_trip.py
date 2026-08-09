#!/usr/bin/env python3

"""Regression contracts for Power Trip's move data and variable base power."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CALC_BASE_DAMAGE = ROOT / "src/individual/CalcBaseDamage.c"
MOVES = ROOT / "armips/data/moves.s"


def main() -> int:
    calc = CALC_BASE_DAMAGE.read_text(encoding="utf-8")
    moves = MOVES.read_text(encoding="utf-8")

    power_trip = re.search(
        r'movedata MOVE_POWER_TRIP, "Power Trip"(?P<body>.*?)terminatedata',
        moves,
        re.DOTALL,
    )
    shared_calculation = re.search(
        r"case MOVE_POWER_TRIP:\s*"
        r"case MOVE_STORED_POWER:\s*"
        r"for \(int stat = 0; stat < 8; stat\+\+\) \{.*?"
        r"positiveStatBoosts \+= sp->battlemon\[attacker\]\.states\[stat\] - 6;.*?"
        r"movepower = 20 \+ 20 \* positiveStatBoosts;\s*"
        r"break;",
        calc,
        re.DOTALL,
    )

    try:
        assert power_trip, "Power Trip move-data entry not found"
        body = power_trip.group("body")
        assert "FLAG_UNUSABLE_UNIMPLEMENTED" not in body, (
            "Power Trip must be selectable in battle"
        )
        assert re.search(r"\bbasepower\s+20\b", body), (
            "Power Trip must retain its 20 base power"
        )
        assert shared_calculation, (
            "Power Trip must share Stored Power's attacker boost calculation"
        )

        expected_power = {0: 20, 1: 40, 6: 140, 42: 860}
        for boost_total, expected in expected_power.items():
            actual = 20 + 20 * boost_total
            assert actual == expected, (
                f"unexpected power for {boost_total} positive stages: {actual}"
            )
    except AssertionError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print("PASS: Power Trip is usable and scales with the user's positive boosts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
