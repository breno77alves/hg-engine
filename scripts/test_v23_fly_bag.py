#!/usr/bin/env python3
"""Contract for HM02's FLY / TEACH / CANCEL bag flow."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    item = read("src/item.c")
    fly = read("src/automatic_hm_fly.c")
    header = read("include/automatic_hm_fly.h")
    new_commands = read("src/script_new_cmds.c")
    macros = read("armips/include/scriptmacros.s")
    common = read("armips/scr_seq/scr_seq_00003_commonscript.s")
    text = read("data/text/040.txt")
    linker = read("rom.ld")

    assert "ItemMenuUseFunc_AutomaticHmTmHm" in header
    assert re.search(
        r"\{\s*ItemMenuUseFunc_AutomaticHmTmHm,\s*NULL,\s*NULL\s*\}", item
    )
    assert "if (data->itemId != ITEM_HM02)" in fly
    assert "ItemMenuUseFunc_TMHM(data, checkData);" in fly
    assert "struct ItemCheckUseData itemCheckData;" in fly
    assert "sAutomaticHmFlyPending.itemCheckData = *checkData;" in fly
    assert "const struct ItemCheckUseData *itemCheckData;" not in fly

    for option in ("FLY", "TEACH", "CANCEL"):
        assert option in text
        assert option in common

    assert "NEW_COMMAND_AUTOMATIC_HM_FLY" in macros
    assert "SCRIPT_NEW_CMD_AUTOMATIC_HM_FLY" in new_commands
    assert "AutomaticHmFly_SetChoice" in new_commands

    assert "HasAutomaticHmAccess" in fly
    assert "SelectAutomaticHmActor" in fly
    assert "FIELD_MOVE_FUNC_CHECK" in fly
    assert "FIELD_MOVE_FLY" in fly
    assert "FieldMove_GetMoveFunc" in fly
    assert "FIELD_MOVE_RESPONSE_OK" in fly
    assert "FIELD_MOVE_RESPONSE_NEED_BADGE" in fly
    assert "FIELD_MOVE_RESPONSE_HAVE_FOLLOWER" in header
    assert "FIELD_MOVE_RESPONSE_NOT_NOW" in header

    assert "ItemMenuUseFunc_TMHM" in fly, "TEACH must remain vanilla"
    assert "Task_StartMenu_ReopenBag" in fly, "CANCEL and errors must return to the bag"
    assert "QueueScript(taskManager, AUTOMATIC_HM_FLY_SCRIPT" in fly
    assert "FieldMove_GetMoveFunc = 0x02067DF4 | 1;" in linker
    assert "Task_StartMenu_ReopenBag = 0x0203CA68 | 1;" in linker
    assert "QueueScript = 0x0203FED4 | 1;" in linker

    print("PASS: HM02 exposes FLY / TEACH / CANCEL and delegates restrictions/use to vanilla")


if __name__ == "__main__":
    main()
