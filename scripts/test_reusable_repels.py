#!/usr/bin/env python3
"""Static contract for the final upstream reusable-Repel flow."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def item_block(source: str, item: str) -> str:
    start = source.index(f"[{item}] =")
    return source[start : source.index("\n},", start)]


def main() -> None:
    assert "#define IMPLEMENT_REUSABLE_REPELS" in read("include/config.h")
    assert "0002 PlayerStepEvent_RepelCounterDecrement 0224BAE4 2" in read("hooks")

    source = read("src/repel.c")
    max_pos = source.index("Bag_HasItem(bag, ITEM_MAX_REPEL")
    super_pos = source.index("Bag_HasItem(bag, ITEM_SUPER_REPEL")
    normal_pos = source.index("item_id = ITEM_REPEL", super_pos)
    assert max_pos < super_pos < normal_pos
    assert "u16 currentRepel = Repel_GetMostRecent();" in source
    assert "EventSet_Script(fieldSystem, 2072, NULL);" in source
    assert "EventSet_Script(fieldSystem, 2022, NULL);" in source
    assert "if (Bag_TakeItem(bag, item_id, 1, heap_id))" in source
    assert "*repel_addr = Repel_GetSteps(item_id, heap_id);" in source
    assert "GetItemData(item_id, ITEM_PARAM_ATTACK, heap_id)" in source

    itemdata = read("data/itemdata/itemdata.c")
    expected_steps = {
        "ITEM_REPEL": 100,
        "ITEM_SUPER_REPEL": 200,
        "ITEM_MAX_REPEL": 250,
    }
    for item, steps in expected_steps.items():
        block = item_block(itemdata, item)
        assert re.search(rf"\.holdEffectParam = {steps},", block)

    script = read("armips/scr_seq/scr_seq_00003_commonscript.s")
    prompt = script.split("scr_seq_0003_072_repels:", 1)[1].split("scr_seq_0003_072_end:", 1)[0]
    assert "yesno VAR_SPECIAL_RESULT" in prompt
    assert "QueueNewRepel" in prompt
    assert "buffer_item_name 1, VAR_SPECIAL_RESULT" in prompt
    messages = read("data/text/040.txt")
    assert "Would you like to use another one?" in messages

    print("PASS: reusable Repels select, consume, and queue the final upstream flow")


if __name__ == "__main__":
    main()
