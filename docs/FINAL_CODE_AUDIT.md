# V2.1 final code audit

## Scope and result

The release-candidate audit searched every tracked text file for `TODO`, `FIXME`,
`UNIMPLEMENTED`, `HACK`, and the former D-pad literal address. Generated build
outputs were not counted. Documentation and regression scripts were excluded from
the backlog totals so that audit prose did not count itself.

| Marker | Matches | Files | Disposition |
| --- | ---: | ---: | --- |
| `TODO` | 228 | 34 | reviewed inherited backlog; not a release blocker by itself |
| `FIXME` | 0 | 0 | none |
| `UNIMPLEMENTED` | 0 | 0 | none |
| `HACK` | 4 | 2 | prose in `CONFIG.md`/`README.md`, not hidden runtime patches |

The TODO distribution is 163 in `src/individual`, 28 in `src/battle`, 14 in battle
scripts, 8 in `armips`, 7 in headers, 3 in tools, and 5 elsewhere. Most describe
the upstream modern-mechanics backlog: raids, Dynamax/Terastal dependencies,
third types, Pledge/terrain refactors, absent Gen 9 interactions, message polish,
or alternative evolution gimmicks. V2.1 deliberately does not import these merely
to erase comments; that would violate the selective-backport rule and could change
Generations balance.

The audited fixes and features used by Generations are covered by the dedicated
regressions and audit tables. Remaining comments are not evidence that their code
path is broken, but they remain candidates for a future release when a reachable
Generations scenario and a test fixture justify the work.

## D-pad literal

No runtime write to `0x02269F4C` remains. Its only product-code occurrence is a
comment in `src/battle/battle_input.c` documenting why the address must not be
self-patched. Other occurrences are analysis and regression-test references. The
battle overlay now uses a permanent pointer and changes only the contents of the
active D-pad table.

## Build-warning review

The two inherited clean-build warnings were made explicit without changing the
serialized ROM behavior:

- the level-up comparison now casts the non-negative growth-table result to the
  unsigned EXP type;
- Ability Patch's 250,000 source price is explicitly masked to the same 16-bit
  value (`53,392`) that V2.0 already serialized.

The Ability Patch is not placed in a Generations shop or acquisition script. The
upstream wide-price series (`18159ea9b`, `83685c6f1`) was not backported because it
changes the item record and multiple bag/shop consumers for an unreachable price.
If Ability Patch becomes obtainable later, port the complete wide-price subsystem
rather than silently depending on the legacy 16-bit value.

## Runtime validation boundary

Static contracts, clean builds, final-ROM byte checks, and available emulator boot
smokes can be automated here. The detailed playthrough, battle, animation,
DeSmuME, V2.0 save-fixture, and DS/flashcart matrices remain exactly as recorded in
`V21_TEST_PLAN.md`; unavailable fixtures are never promoted to passes.
