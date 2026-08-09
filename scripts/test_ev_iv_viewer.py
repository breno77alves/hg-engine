#!/usr/bin/env python3
"""Static contract for the upstream EV/IV summary viewer."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    config = read("include/config.h")
    assert "#define IMPLEMENT_NEW_EV_IV_VIEWER" in config

    hooks = read("hooks")
    viewer_hooks = hooks.split("#ifdef IMPLEMENT_NEW_EV_IV_VIEWER", 1)[1].split("#endif", 1)[0]
    assert "arm9 Summary_IVEV 02088B60 1" in viewer_hooks
    assert "arm9 Summary_Entry_Hook 0208D2C4 1" in viewer_hooks

    assembly = read("asm/other_hook.s")
    handler = assembly.split("Summary_IVEV:", 1)[1].split("Summary_StatsPage_Return:", 1)[0]
    assert "Summary_Check_LButton:" in handler
    assert "Summary_Check_RButton:" in handler
    assert "Summary_Check_SELButton:" in handler
    for mode in ("mov     r1, #1", "mov     r1, #2", "mov     r1, #0"):
        assert mode in handler
    assert handler.count("bl      Summary_ChangeStatScreenState") == 3
    assert handler.count("cmp     r1, #1") == 3, "viewer must only replace the stats page"

    summary = read("src/summary.c")
    assert "MON_DATA_HP_EV" in summary and "MON_DATA_HP_IV" in summary
    assert "CopyBoxPokemonToPokemon" in summary and "sys_FreeMemoryEz(pokemon)" in summary
    assert "GetBoxMonNatureCountMints" in summary
    assert "{  0,  0,  0,  0,  1, -1  },    // Sassy" in summary
    assert "UpdatePokemonData(summary, 0);" in summary, "raw stats must be restored before page changes"

    messages = read("data/text/302.txt").splitlines()
    assert messages[206] == "EV" and messages[207] == "IV"

    print("PASS: EV/IV viewer matches the final upstream input and display contract")


if __name__ == "__main__":
    main()
