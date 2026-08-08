# HeartGold Generations V2.1 upstream audit

This document is the decision ledger for selective backports from `BluRosie/hg-engine`.
It deliberately does not treat upstream `main` as a replacement for the Generations
engine or data.

## Audit snapshot

| Item | Revision |
| --- | --- |
| Generations V2.0 base | `c28e104a8ed664ce1a5dba6b0d8d83caded89b62` |
| Upstream audited | `c6d63fd8a34f63431214284dc08c3b7942ab0593` |
| Common ancestor | `a6e00404c91e158fb353d3e8e5eaa00eefeabb3e` |
| Snapshot date | 2026-08-08 |

The common ancestor is dated 2025-08-03. The Generations base has 20 commits after
that ancestor, ending on 2025-08-09. Upstream has 2,219 commits in its first-parent
and merged history after the same ancestor. `git cherry` reports 1,858 non-merge
upstream patches without a patch-equivalent in the Generations tip.

The absence of a patch-equivalent is not proof that a feature is absent. Generations
contains upstream work inherited before the common ancestor and local equivalents.
Every candidate below is checked against source state as well as commit ancestry.

## Preservation boundary

The following Generations-owned areas are protected unless a narrowly scoped fix
requires a reviewed change:

- encounters and progression in `armips/data/encounters.s`;
- trainers and difficulty curve in `armips/data/trainers/`;
- evolution, species, form, level-up, and ability choices in `armips/data/`;
- marts, custom items, gifts, and event scripts;
- existing Mega Evolution availability and UX;
- hard level-cap progression;
- save layouts and persistent data.

No `git merge upstream/main`, directory replacement, or bulk copy is permitted.
Backports are made as small logical patches, followed by a build and the subsystem's
test gate.

## Classification rules

- **A** — applicable correctness, crash, corruption, softlock, or compatibility fix.
- **B** — feature explicitly requested for V2.1.
- **C** — dependency needed by an accepted A or B change.
- **D** — unsolicited behavior, balance, or generation change; excluded by default.
- **E** — not applicable because the affected feature is absent and remains disabled.
- **Present** — behavior already exists in the Generations base; audit later fixes only.
- **Pending** — accepted for investigation, but not yet safe to port.
- **Excluded** — deliberately outside the V2.1 scope.

## Generations delta inventory

The 20 Generations commits after the common ancestor are predominantly data and
campaign work: configuration, evolution and item data, forms, starters, trainers,
level curve, encounters, marts, custom QoL items, PC Anywhere, and hooks. Across the
ancestor-to-base diff, 23 files changed with 2,327 insertions and 1,709 deletions.
These local commits are the content identity that selective backporting must retain.

## High-confidence bugfix candidates

| Area | Upstream revision(s) | Class | Base state | Decision / dependency | Test gate |
| --- | --- | --- | --- | --- | --- |
| Hall of Fame 4bpp generation | `e45e1ab475b23e4aafda472d6a13d8248d17e5a9` | A | Old `narcs.mk` arguments present | Small, isolated build fix; accepted | Enter Hall of Fame in melonDS and DeSmuME |
| Half and 3/4 drain scripts | `245aa5e38e99b2b4668985277cf23d4d85d501d9` plus earlier drain guards | A | Patch absent | Audit full drain chain before applying the final script state | Full drain matrix including 1 damage, resisted damage, Liquid Ooze, Big Root, Heal Block |
| Power Trip | `f4fd450447c458bad4230649e6a19a8552f65678` | A | Patch absent | Small move-data and damage-calculator change; accepted | Zero and multiple positive boosts; compare Stored Power |
| Infestation | `ddabadb780cf1bdfba8c1d8d03b1855067c0ae83`, `42496dbd9`, `7d26f57fe` and later bind fixes | A | Initial patch absent | Port final coherent bind behavior, not only the first tag change | Residual damage, messages, four trapping moves, switch restriction |
| Dragon Tail / Circle Throw | `531222a5e`, `22686956f`, `12cf75b8b`, `8242d462b`, `87d34f105`, `a18db2ce6`, `f5b5488e0` | A/C | Modern chain absent | Broad controller/post-move dependency; reconstruct final behavior rather than cherry-pick an intermediate commit | Substitute, no reserve, fainted target, abilities, doubles |
| Simultaneous faint and EXP | `c67ac01faafc2d5d00763ca444d239024156ff8c`, `5418b65cf`, merge `d4f0b1a8c` | A/C | Absent | Requires final-state diff because `5418b65cf` contains mass formatting | Same-trainer double KO, spread damage, EXP and replacement |
| Two fainted battlers from same trainer | `031c579a4698f43832f75cb3cf11ba043fd6e229` | A | Absent | Accepted as part of the faint subsystem; includes `TRAINER_BOTH` OR correction | Ariana double-KO regression |
| Critical Capture generation guard | `22df8b40f3fe374675589e81d5e55390e51d1451` | A/B | Critical Capture already enabled; generation macro and equivalent check are present locally | Verify whether local source is semantically final before claiming a backport | Capture animation and generation-specific probability |
| Capture EXP fixes | `8b448a7e`, `153045c54`, `07fe8db4b` | B | All three are ancestors/present in base | No implementation backport; regression-test with level cap | Participants, EXP Share, full party, level-up/evolution, cap |

## No Guard finding

The No Guard issue cannot be represented by a single issue-number commit.

1. `b9b9cab7363b492ebb13ce010a70a45d767079dd` modernized accuracy and is already
   present in the Generations base. Its sure-hit path checks No Guard on both the
   attacker and target.
2. The Generations `BattleController_CheckSemiInvulnerability` path predates that
   commit (`ee3870ccf0`) and independently checks only the attacker's No Guard.
   Because this check runs in the BeforeMove pipeline, a defender with No Guard may
   still be rejected while using Fly, Dig, Dive, or a similar state.
3. Upstream's final helper, `CanHitThroughSemiInvulnerability`, explicitly checks
   both attacker and defender. The semantic change first appears inside the broad
   Dragon Darts draft `8d780780b7881a426417162c8d783ee09d248a91`; a later formatting
   commit obscures it in `git blame`.

The safe V2.1 backport is therefore the minimal defender-side ability check in the
existing Generations semi-invulnerability function, not the Dragon Darts refactor.
It remains gated on dedicated attacker/defender, ordinary accuracy, OHKO,
accuracy/evasion, Fury Cutter, and semi-invulnerability tests.

## Requested systems already present in Generations V2.0

The base has these options enabled in `include/config.h`:

| System | Base configuration | V2.1 action |
| --- | --- | --- |
| EV/IV summary viewer | `IMPLEMENT_NEW_EV_IV_VIEWER` | Audit species/forms and upstream fixes; preserve UI |
| Reusable Repels | `IMPLEMENT_REUSABLE_REPELS` | Audit later fixes and run traversal/save tests |
| Critical Capture | `IMPLEMENT_CRITICAL_CAPTURE`; generation configured | Verify final logic and animation; preserve capture rates |
| Capture EXP | `IMPLEMENT_CAPTURE_EXPERIENCE` | Verify final known fixes and hard-cap interaction |
| Modern vitamins | `UPDATE_VITAMIN_EV_CAPS` | Verify 252 per stat and 510 total |
| Friendship evolution | threshold `160` | Audit event assumptions and regression-test evolutions |
| Hard level cap | `IMPLEMENT_LEVEL_CAP` | Preserve Generations variable/scripts; fix the level-65 regression |

`ALLOW_LEVEL_CAP_EVOLVE` is currently disabled and is a requested B change.
`UNCAP_CANDIES_FROM_LEVEL_CAP` is disabled and must remain disabled by default.

## Behavior explicitly excluded by the V2.1 specification

| Behavior | Class | Decision |
| --- | --- | --- |
| Wild double battles | D | Keep disabled |
| Global or battle-only 60 FPS | D | Do not add/enable |
| Force Set Mode | D | Do not add/enable |
| Dynamax | D/E | Do not activate or import dependencies solely for it |
| Terastal | D/E | Do not activate or import dependencies solely for it |
| New Gen 9 balance/mechanics | D | Exclude unless they are a dependency of an explicit V2.1 feature and can be isolated |
| Restore consumed held items after battle | D | `RESTORE_ITEMS_AT_BATTLE_END` is unexpectedly enabled in the base; disable for V2.1 unless campaign evidence proves it is intentional Generations behavior |

## Mandatory local investigations

These are Generations-specific and cannot be solved by assuming an upstream commit
applies:

- melonDS JIT D-pad failure caused by runtime writes to `0x02269F4C`;
- level cap reverting to 65 after Elite Four rematch paths;
- Elm-lab Infinite Candy / Pocket Heal reward depending on save/reload order;
- Frigibax family ability IDs and evolution persistence;
- availability and functionality of every intended Mega Stone;
- Ariana's simultaneous opponent faint crash;
- save compatibility at early game, 8 badges, Champion, and 16 badges/Red.

## Audit workflow for remaining upstream commits

The remaining upstream-only patch set is reviewed in slices, not accepted by keyword
alone:

1. identify commits by affected subsystem and bug-oriented subject;
2. inspect the entire ancestry from initial implementation through later fixes;
3. compare the base source with both sides of each candidate patch;
4. reject feature-only fixes when the feature is absent and remains disabled;
5. reconstruct minimal semantic patches where formatting/refactors dominate;
6. record the decision and test gate here;
7. build and test before moving to the next subsystem.

This document is intentionally live. A candidate marked Pending is not permission to
bulk-port its directory or all of its dependencies.
