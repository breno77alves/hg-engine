# Generations V2.0 save compatibility

## Source-level result

Generations V2.1 preserves the persistent layouts used by the V2.0 base at
`c28e104a8ed664ce1a5dba6b0d8d83caded89b62`:

- `SaveData`, `BagData`, and their allocation/initialization code are unchanged;
- item, medicine, Ball, and TM/HM pocket capacities are unchanged;
- `ALLOW_SAVE_CHANGES`, `ITEM_POCKET_EXPANSION`, and `EXPAND_PC_BOXES` have the
  same enabled state as V2.0;
- new medicines and mints are stored in the existing Items pocket, while the bag
  code still recognizes legacy V2.0 stacks left in Medicine slots;
- expanded ability IDs reuse bits inside the existing 32-bit experience word.

The ability extension stores legal experience in 21 bits, leaves 10 bits unused,
and uses the previous high bit for the ninth ability-ID bit. This does not enlarge
the Pokémon record. Every legal level-100 experience value fits in 21 bits, and
the newly used high bit is zero in ordinary V2.0 records.

`scripts/test_save_compatibility.py` locks these structural invariants against the
V2.0 base commit.

## Playable fixture matrix

No V2.0 `.sav`, `.dsv`, or equivalent fixture was present in the workspace. The
following runtime checks are therefore **NOT RUN — BLOCKED BY MISSING FIXTURE**,
not passed:

| Fixture | Expected point | Runtime status |
| --- | --- | --- |
| Save A | beginning of the game | NOT RUN — fixture unavailable |
| Save B | 8 badges | NOT RUN — fixture unavailable |
| Save C | Champion completed | NOT RUN — fixture unavailable |
| Save D | 16 badges / Red | NOT RUN — fixture unavailable |

When fixtures are supplied, load each one directly in the release ROM and verify
party, PC boxes, held items, all bag pockets, badges, Pokédex, flags/variables,
Mega items, current map, save/reload, and continued story progression. Retain a
copy of each original fixture so the conversion check is reversible.

## Compatibility boundary

This audit covers compatibility with the configured Generations V2.0 base, not
stock HeartGold or PKHeX. V2.0 already enabled the engine's expanded-save options,
so stock-game and PKHeX compatibility were outside the inherited contract before
V2.1 work began.
