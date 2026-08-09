# HeartGold Generations V2.1 test plan

This plan records repeatable acceptance tests for the selective V2.1 update. A test
is not marked passed from source inspection alone. Emulator, save, and hardware
results must record the build SHA, ROM hash, environment, fixture, and evidence.

## Result vocabulary

- **PASS** — observed result matches the expected result.
- **FAIL** — reproducible mismatch; link the defect and reproduction evidence.
- **BLOCKED** — required fixture or hardware is unavailable.
- **NOT RUN** — test has not been executed.
- **N/A** — feature is deliberately absent; include the audit decision.

## Build gates

Run after every source subsystem:

```sh
export DEVKITARM=/opt/gcc-arm-none-eabi-10.3-2021.10
make clean_code
make -j"$(nproc)"
```

Run a full clean build after graphics, generated data, build rules, hooks, or linker
changes:

```sh
export DEVKITARM=/opt/gcc-arm-none-eabi-10.3-2021.10
make clean
make -j1
```

On this Windows/MSYS2 host, parallel full asset generation intermittently returns
error 127 while several `nitrogfx` NANR conversions run concurrently; the reported
target is valid when retried. Serial full generation completes reliably. Incremental
source builds may still use `-j"$(nproc)"`.

For every release-candidate build, record size, SHA-256, MD5, warnings, and whether
the warning set changed from `docs/BASELINE_V2.0.md`.

## Environment matrix

| Environment | Required mode | Status |
| --- | --- | --- |
| melonDS 1.1 | JIT enabled | Opening-sequence visual smoke PASS; multi-battle D-pad matrix NOT RUN |
| melonDS 1.1 | interpreter/JIT disabled | Baseline title boot PASS |
| DeSmuME 0.9.13 x64 | default CPU mode | Baseline title boot PASS |
| TWiLight Menu++ on DS/3DS | current available setup | BLOCKED pending hardware |
| R4/flashcart | available supported cart | BLOCKED pending hardware |

No 60 FPS patch may be enabled during compatibility testing.

## Save fixtures

| Fixture | Progress | Source | Required checks |
| --- | --- | --- | --- |
| Save A | New game / Elm lab | V2.0 | party, bag, event flags, Candy/Heal reward |
| Save B | 8 badges | V2.0 | party/PC, bag, Pokédex, badges, Johto completion flags |
| Save C | Champion complete | V2.0 | Hall of Fame, Kanto unlocks, cap state, rematches |
| Save D | 16 badges / Red | V2.0 | full progression, cap, Mega items, rematches |

Each fixture must first load in the unmodified V2.0 baseline and then in the exact
V2.1 release candidate. Compare party data, PC boxes, items, Pokédex, badges, event
flags, variables, Mega items, and progression. Keep original fixture copies.

## Boot and campaign smoke tests

For every required emulator:

1. boot through title and load/new-game transition;
2. save and reload;
3. enter and exit a wild battle;
4. complete a trainer single battle;
5. complete a trainer double battle;
6. smoke-test a Gym Leader, Elite Four, Champion, rematch, and Red using fixtures.

Expected: no crash, softlock, graphical corruption, Bad Egg, save corruption, or
unexpected trainer/encounter/progression change.

## D-pad and Mega regression

Primary environment: melonDS with JIT enabled.

1. Start from a deterministic save with a non-Mega Pokémon and a Mega-capable
   Pokémon.
2. Complete at least 10 consecutive battles, mixing wild and trainer battles.
3. In each battle, open Fight, move across all four attacks, cancel, and repeat.
4. Switch party Pokémon at least once and repeat navigation.
5. Toggle fast-forward between battles and repeat with it off.
6. With Mega unavailable, verify four moves and Cancel by D-pad and touch.
7. With Mega available, verify Mega selection by D-pad and touch.
8. Mega Evolve, then verify move navigation and Cancel for the remainder of that
   battle and in the next battle.
9. Repeat with multiple Mega species.

Expected: input works identically in battle 1 and battle 10+, the Mega control never
aliases a move or Cancel, and no runtime write to `0x02269F4C` remains in source or
generated hooks. Repeat a smaller smoke test in melonDS interpreter and DeSmuME.

## Hall of Fame

Using a Champion-ready fixture, enter the Hall of Fame and proceed through the full
registration and save sequence in melonDS and DeSmuME.

Expected: all portraits render, the sequence completes, the game saves, and the
postgame loads without changing emulator settings.

## Move and ability matrix

| Area | Cases |
| --- | --- |
| Drain | Absorb, Mega Drain, Giga Drain, Drain Punch, Horn Leech, Draining Kiss if present; 1 damage, resisted, neutral, super-effective, zero/negative guard, Liquid Ooze, Big Root, Heal Block |
| Power Trip | no boosts; one and multiple positive stages across stats; negative stages ignored; parity with Stored Power |
| Infestation/bind | Infestation and the other trapping moves; initial hit, residual damage/duration, messages, faint, switching and immunity cases |
| Dragon Tail/Circle Throw | normal forced switch, Substitute, fainted target, no reserve, switch-in abilities/hazards, doubles and already-pending replacement |
| No Guard | attacker ability, defender ability, 50% accuracy, OHKO restrictions, positive/negative accuracy and evasion, Fury Cutter, Fly, Dig, Dive and applicable special-hit moves |
| Body Press | defense-derived damage across boosts/drops, burn and relevant abilities/items |
| Faint handling | spread moves, Explosion/self-KO, recoil, Destiny Bond if applicable, multi-hit, Pursuit, forced switch, replacement and EXP |

Where upstream supplies a battle-test fixture, reproduce its setup on the V2.1
engine or port only the test harness dependencies needed to make the result
repeatable. Manual tests require screenshots/video and exact party/move data.

## Ariana and simultaneous-faint regression

Use the original Ariana encounter if a save fixture can reach it, plus a minimal
controlled doubles setup.

Required cases:

- both opposing Pokémon faint from one spread move;
- two Pokémon owned by the same trainer faint simultaneously;
- both allies faint simultaneously;
- attacker also faints from recoil, Explosion, or another self-KO path;
- one or two replacement Pokémon are available, and no replacement is available;
- EXP Share and multiple participants are present.

Expected: exactly one appropriate faint message per battler, correct EXP once per
eligible party member, valid replacement slots, and no crash, softlock, Bad Egg, or
duplicate/missing EXP.

## Level-cap progression

Record the cap variable and displayed/observed cap before and after every transition:

- new game and each Johto badge;
- Elite Four entry and Champion completion;
- Kanto progression and each relevant badge;
- Elite Four rematch paths, including the reported regression to 65;
- 16 badges and Red;
- later rematches and save/reload at each critical state.

At the cap, test battle EXP, Capture EXP, Rare Candy, and Infinite Candy. A candy may
trigger an eligible evolution when `ALLOW_LEVEL_CAP_EVOLVE` is enabled, but no path
may raise the Pokémon above the active hard cap. `UNCAP_CANDIES_FROM_LEVEL_CAP` must
remain disabled.

Automated regression status: **PASS** for the post-Red invariant (stored 65 resolves
to 100 only after persistent variable `0x40FD` is set), invalid cap fallback, enabled
cap-bound evolution, and disabled candy uncapping. The full badge, Elite Four, Red,
rematch, evolution-animation, and save/reload matrix remains **NOT RUN** pending the
required campaign fixtures.

## Elm-lab reward determinism

Run both flows from equivalent new-game states:

- speak to the NPC without saving/reloading first;
- save immediately before the NPC, reload, then speak.

Repeat after checking relevant item ownership and event flags. Expected: the same
intended Infinite Candy and Pocket Heal rewards in both flows; Potions or duplicated
rewards must not depend on save order.

Automated regression status: **PASS**. The Elm's Lab 1F script archive (`843`) now
replaces the inherited five-Potion block with unconditional Infinite Candy and
Infinite Rejuv rewards, rejoins before the original close-message and scene-state
commands, and preserves both items as non-consuming Key Items. A clean ROM build and
melonDS JIT boot smoke pass. The two playable new-save/save-reload flows remain
**NOT RUN** pending equivalent early-game save fixtures.

## Frigibax family

Inspect and test wild, trainer-owned, and script-gift instances when applicable.
Verify valid normal/hidden ability IDs for Frigibax, Arctibax, and Baxcalibur, then
evolve through both stages and save/reload. Expected: no invalid ability, unexpected
slot remap, or loss/change outside the intended evolution mapping.

Automated regression status: **PASS**. The generated 44-byte Frigibax personal
record stores Thermal Exchange as ID 270 (`0x010E`) and ability slot 2 as zero;
Arctibax and Baxcalibur share that normal ability, while the hidden table retains
Ice Body. The full 9-bit path through Box/Party save data, battle data, summaries,
PC, gifts, trainers, and evolution data is source-locked; a full clean build and
melonDS JIT boot pass. Wild/trainer/gift acquisition, both evolution animations,
PC/party summary display, and V2.0 save/reload remain **NOT RUN** pending fixtures.

## Mega Stone audit tests

For every stone listed in `docs/MEGA_STONE_AUDIT.md`, verify the intended acquisition
method, chance/conditions, bag result, compatible species, battle activation, D-pad,
touch, summary display, save/reload, and progression timing. Do not add a stone that
the Generations design intentionally omits.

Automated acquisition audit: **PASS**. All 47 stone constants match the 47 engine
mappings; the 42 wild-holder stones and five Celadon 3F legendary stones have source
contracts. The generated ARM9 inventory contains item IDs 550, 551, 575, 576, and
583, the build succeeds, and melonDS JIT boots. Purchases and all gameplay cases
above remain **NOT RUN** pending deterministic fixtures.

## QoL matrix

| System | Required cases |
| --- | --- |
| EV/IV Viewer | normal stats, EVs, IVs via L/R/Select; nature indicators; forms; Mega-capable species; early and modern species |
| Reusable Repels | normal/Super/Max inventory priority, none available, cave, route, building transition, bike, Surf, save/load |
| Critical Capture | activation and failure animation, low/high caught count where configurable, no capture-rate data change |
| Capture EXP | single/multiple participants, EXP Share, full party, level-up, evolution, capture failure, hard-cap boundary |
| Vitamins | all six vitamins to 252 per stat, 510 total, already-capped stat, EV-reducing berries, viewer consistency |
| Friendship | Eevee day/night, Golbat, Togetic, Budew, Riolu and other available evolutions at threshold 160; audit event dependencies |

EV/IV Viewer automated regression status: **PASS**. The guarded ARM9 hooks map L,
R, and Select to EV, IV, and raw-stat modes only on the stats page; party and boxed
Pokémon use their respective access paths, mint-adjusted nature colors include the
upstream Sassy correction, and raw values are restored before a page transition.
The cross-species/form visual and input matrix remains **NOT RUN** pending a summary
screen fixture.

Reusable Repels automated regression status: **PASS**. The final upstream field
hook, yes/no common script, inventory check, and Max → Super → normal priority are
present. A successful choice consumes exactly one selected Repel and loads its
100/200/250-step item parameter; with no Repel, the normal wore-off script is used.
Traversal, Surf, transition, and save/reload cases remain **NOT RUN** pending a
field fixture.

Modern vitamins automated regression status: **PASS**. All nine item-use checks and
all three general per-stat caps are patched to 252, and HP Up, Protein, Iron,
Carbos, Calcium, and Zinc each target the correct EV by 10. The separate vanilla
six-stat sum check remains 510 because this backport changes only per-stat compare
operands. Item-use boundary cases, EV-reducing berries, and Viewer agreement remain
**NOT RUN** pending a party fixture.

Friendship evolution automated regression status: **PASS**. The normal, daytime,
and nighttime methods all use the configured threshold of 160 across the 16 current
evolution records. No campaign script reads friendship, and the unrelated modern
affection battle bonuses remain disabled. Level-up/evolution-animation checks for
the representative species remain **NOT RUN** pending party and clock fixtures.

## Compatibility and antipiracy

Automated regression status: **PASS** for the current upstream source contract. The
legacy runtime decompression hook was removed, the original ARM9 path is restored,
overlay 123 is decompressed at build time, and direct card-check/dsprotect patches
from `b15b01c9f` are enabled. Both 60 FPS options remain disabled.

Emulator passes do not substitute for hardware.
On available DS/3DS and flashcart setups test boot, save/load, repeated battles,
overlays used by summary/bag/PC, Hall of Fame, and extended play. Record exact device,
firmware, loader, and ROM hash.

## Excluded feature guard

Automated regression status: **PASS**. Wild double battles, global and battle-only
60 FPS, Force Set Mode, restore-items-at-battle-end, Z-Moves, Dynamax, and Terastal
remain disabled. This guard prevents an upstream backport from silently changing
Generations balance or enabling an incomplete battle gimmick.

## Save compatibility

Automated structural regression status: **PASS** against Generations V2.0 commit
`c28e104a8`. Save, bag, pocket-capacity, PC-expansion, and Pokémon-record sizes are
preserved; expanded abilities reuse the existing EXP word, and legacy Medicine
slots have a V2.0 fallback. See `SAVE_COMPATIBILITY.md`.

Playable Save A/B/C/D results remain **NOT RUN — BLOCKED BY MISSING FIXTURE**. No
V2.0 save file is available in the workspace, so party, PC, items, badges, flags,
Pokédex, Mega items, and progression cannot honestly be certified at runtime yet.

## Release-candidate checks

- full clean build succeeds from documented prerequisites;
- warnings are classified and no unexplained new warning exists (see
  `FINAL_CODE_AUDIT.md`);
- global searches for `TODO`, `FIXME`, `UNIMPLEMENTED`, `HACK`, and `0x02269F4C`
  are reviewed and recorded rather than blindly removed;
- no runtime write to `0x02269F4C` remains;
- excluded features remain disabled;
- V2.0 save fixtures pass;
- trainer, encounter, progression, and difficulty diffs are either absent or tied to
  a documented Generations-specific fix;
- source revision, upstream audit revision, ROM size, SHA-256, MD5, emulator results,
  hardware results, known issues, and distribution-patch hash are recorded in the
  release changelog.
