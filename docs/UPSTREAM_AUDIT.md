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
| Hall of Fame 4bpp generation | `e45e1ab475b23e4aafda472d6a13d8248d17e5a9` | A | Backported in V2.1 | Exact semantic patch applied; clean build and JIT boot PASS | Actual Hall of Fame sequence in melonDS and DeSmuME NOT RUN pending Champion save |
| Half and 3/4 drain scripts | `3919379e838bf07f39659769b19ecedc70262eda`, `245aa5e38e99b2b4668985277cf23d4d85d501d9` | A | Backported in V2.1; earlier negative-damage guard `150168153` was already present | Final arithmetic ported while preserving the base's pre-modern Heal Block path | Automated contract, clean build, and JIT boot PASS; full battle matrix NOT RUN |
| Power Trip | `f4fd450447c458bad4230649e6a19a8552f65678` | A | Backported in V2.1; move-data flags were already final locally | Added the missing damage-calculator case while preserving the base's newer inline boost counting | Automated contract and clean build PASS; JIT boot PASS; zero/multiple-boost battle comparison with Stored Power pending fixture |
| Reversal / Body Press / Infestation | `ddabadb780cf1bdfba8c1d8d03b1855067c0ae83`, `42496dbd9`, `7d26f57fe`, `207f93c92` and later bind fixes | A | Backported in V2.1; the local bind counter, residual, switch, cleanup, and Whirlpool paths were already final | Reversal shares Flail's HP bands; Body Press uses the attacker's Defense/stat stage; Infestation uses the existing bind effect with a local message group | Automated contract, full clean build, and JIT boot PASS; full in-battle power/bind matrix pending fixture |
| Dragon Tail / Circle Throw | `531222a5e`, `22686956f`, `12cf75b8b`, `8242d462b`, `87d34f105`, `a18db2ce6`, `f5b5488e0` | A/C | Backported in V2.1 | Final semantics reconstructed on the older MoveEnd pipeline: dedicated damaging effect, real-damage/alive/Substitute/re-entry gates, doubles support, and switch-in ability ordering | Automated contract, full clean build, and JIT boot PASS; full in-battle switch matrix pending fixture |
| Simultaneous faint and EXP | `c67ac01faafc2d5d00763ca444d239024156ff8c`, `031c579a4698f43832f75cb3cf11ba043fd6e229`, finalized by `5418b65cf` with hook dependency `3265d051c` | A/C | Backported semantically in V2.1 | The older Generations controller applies spread damage sequentially, so the final behavior is reconstructed with a per-active-slot faint latch instead of importing the newer batch-damage pipeline; species remains intact for EXP and the latch resets only when a replacement is loaded | Automated same-trainer double-KO/duplicate/replacement contract, full clean build, and JIT boot PASS; Ariana in-battle fixture pending |
| Two fainted battlers from same trainer | `031c579a4698f43832f75cb3cf11ba043fd6e229`, superseded by final `5418b65cf` semantics | A | Backported as part of the faint subsystem | Each opposing active slot can faint independently even when both belong to one trainer; the intermediate `TRAINER_BOTH` bookkeeping is not imported because final upstream removed it | Ariana double-KO regression covered by source/behavior contract; in-battle fixture pending |
| Critical Capture generation guard | `22df8b40f3fe374675589e81d5e55390e51d1451` | A/B | Backported in V2.1; Critical Capture and its generation macro were already enabled | Restricted the already-caught one-shake animation override to Gen 9+ without changing capture probabilities; regional-versus-national caught-species counting was already generation-gated locally | Gen 8/9 source/behavior contract and clean-code build PASS; current Gen 9 ROM is byte-identical to the prior JIT-tested artifact; in-battle capture animation fixture pending |
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
| Critical Capture | `IMPLEMENT_CRITICAL_CAPTURE`; generation configured | Final Gen 9 guard applied without changing capture rates; in-battle animation fixture pending |
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

## Applied upstream patches

| Upstream revision | V2.1 status | Verification |
| --- | --- | --- |
| `e45e1ab475b23e4aafda472d6a13d8248d17e5a9` | Applied: Hall of Fame encounter portraits use scanned 4bpp generation | Source contract PASS; full clean build PASS; melonDS JIT boot PASS; Hall of Fame sequence pending save fixture |
| `3919379e838bf07f39659769b19ecedc70262eda`, finalized by `245aa5e38e99b2b4668985277cf23d4d85d501d9` | Applied: half and 3/4 drain accept one point of dealt damage and reject zero/positive HP calculations; 3/4 arithmetic order fixed | Script contract PASS; full clean build PASS; melonDS JIT boot PASS; in-battle interaction matrix pending fixture |
| `f4fd450447c458bad4230649e6a19a8552f65678` | Applied semantically: Power Trip now shares Stored Power's positive-stat-stage scaling; its move-data flags were already usable and final in this base | Source contract PASS; full clean build PASS; melonDS JIT boot PASS; in-battle boost matrix pending fixture |
| `ddabadb780cf1bdfba8c1d8d03b1855067c0ae83`, with Infestation message semantics from `42496dbd9`, `7d26f57fe`, and `207f93c92` | Applied semantically: Reversal shares Flail scaling; Body Press reads the attacker's Defense and Defense stage; Infestation joins the existing binding system with side-aware messages | Source/infrastructure contract PASS; full clean build PASS; melonDS JIT boot PASS; in-battle HP-band, stat-stage, duration, residual, and switch matrix pending fixture |
| `531222a5e`, `22686956f`, `12cf75b8b`, `8242d462b`, `87d34f105`, `a18db2ce6`, finalized by `f5b5488e0` | Applied semantically: Circle Throw and Dragon Tail use a dedicated damage-only effect and force a valid surviving target out only after real damage; the local MoveEnd path prevents re-entry, supports ordinary doubles, and runs switch-in abilities before hazards | Source/behavior contract PASS; full clean build PASS; melonDS JIT boot PASS; in-battle Substitute, reserve, faint, ability, Red Card, and doubles matrix pending fixture |
| `c67ac01faafc2d5d00763ca444d239024156ff8c`, `031c579a4698f43832f75cb3cf11ba043fd6e229`, finalized by `5418b65cf`, with command hook from `3265d051c` | Applied semantically for the older sequential-damage controller: faint handling preserves species for EXP, latches each active battler slot against duplicate processing, permits both same-trainer opponents to faint, and clears the latch on replacement | Source/behavior contract PASS; full clean build PASS; melonDS JIT boot PASS; Ariana in-battle fixture pending |
| `22df8b40f3fe374675589e81d5e55390e51d1451` | Applied: the already-caught one-shake Critical Capture animation override now obeys `CRITICAL_CAPTURE_GENERATION >= 9`; the existing probability formula is unchanged | Gen 8/9 source/behavior contract PASS; clean-code build PASS; current Gen 9 ROM SHA-256 remains `FC727FE9FF47A461691C4D391E61192D01643239FB1CBD9D770B5523CF5C4CE7`, matching the prior melonDS JIT-tested artifact; in-battle animation fixture pending |
