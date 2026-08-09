# HeartGold Generations V2.1 move and ability audit

This audit prioritizes mechanics that the Generations campaign actually exposes.
It does not equate every move constant in the expanded engine with campaign use,
and it does not import the modern upstream battle controller wholesale.

## Audited surface

At the V2.0 preservation boundary, `trainers.s` references 358 distinct moves on
322 species. Only two trainer-selected moves are beyond the original Gen 4 move
range: Hone Claws and Hex. Those trainer records expose 126 distinct normal
abilities through their species data. Hidden abilities, player-owned learnsets,
TMs, tutors, and egg moves expand the playable surface beyond this boss/trainer
critical subset.

The combined learnset, trainer, TM, tutor, and egg-move sources reference 326 moves
above the original Gen 4 range. A reference is not proof that a move is fully
implemented: some expanded records are placeholders, while others use ordinary
move data plus C-side special handling. For that reason the audit records proven
paths and known gaps instead of classifying moves from their descriptions alone.

## Trainer-critical moves

| Move | Generations state | Upstream finding | V2.1 decision | Verification |
| --- | --- | --- | --- | --- |
| Hone Claws | Dedicated `MOVE_EFFECT_ATK_ACC_UP` status effect | No later isolated correctness patch found for the local path | Preserve | Move-data contract PASS; playable trainer fixture pending |
| Hex | Dedicated status-damage effect; C calculator doubles power for any major status | Local behavior matches intended modern mechanic | Preserve | Move-data/calculator contract PASS; playable trainer fixture pending |

## Requested and reported move fixes

| Move/system | V2.0 state | V2.1 result | Verification |
| --- | --- | --- | --- |
| Absorb-family drain | One-damage and 3/4 arithmetic edge cases incorrect | Final applicable drain arithmetic backported | Dedicated regression, clean build, JIT boot PASS |
| Power Trip | Move data present; scaling calculator missing | Shares Stored Power positive-stage scaling | Dedicated regression, clean build, JIT boot PASS |
| Reversal | Modern move present without Flail HP-band handling | Shares final Flail HP bands | Dedicated regression, clean build, JIT boot PASS |
| Body Press | Modern move present without Defense-derived damage | Uses attacker's Defense and Defense stage | Dedicated regression, clean build, JIT boot PASS |
| Infestation | Plain-hit placeholder | Uses the existing bind system and local messages | Dedicated regression, clean build, JIT boot PASS |
| Dragon Tail / Circle Throw | Incomplete forced-switch chain | Final behavior reconstructed for the older MoveEnd controller | Dedicated regression, clean build, JIT boot PASS |
| Sparkling Aria | Local MoveEnd loop cures burned battlers actually hit, excluding failed/fainted targets | Later upstream moves this behavior into the modern performance pipeline | Preserve local semantic implementation; do not import pipeline-only reorder | Source inspection PASS; doubles fixture pending |
| Struggle | Older type calculator exits before type effectiveness | Later upstream fixes a replacement type helper | Already correct locally; no backport | Source inspection PASS |

## Ability audit decisions

| Ability/system | V2.0 state | V2.1 result | Verification |
| --- | --- | --- | --- |
| No Guard | Semi-invulnerability gate inverted and attacker-only | Symmetric attacker/defender bypass restored | Dedicated regression, clean build, JIT boot PASS |
| Water Absorb | Required nonzero move power | Water status moves are intercepted in modern generations | Dedicated regression, clean build, JIT boot PASS |
| Defiant / Competitive | Shared Attack cap blocked Competitive | Independent Attack/Special Attack caps | Dedicated regression, clean build, JIT boot PASS |
| Frigibax family / abilities 256-511 | Personal records contained Thermal Exchange (270), but the V2.0 `u8` path discarded or truncated it | Personal, Box/Party, battle, summary, PC, gift, and trainer paths retain 9-bit IDs; Thermal Exchange is 270 and Ice Body remains the hidden ability | Dedicated regression, generated-NARC inspection, full clean build, and JIT boot PASS; wild/trainer/gift/evolution/save fixture pending |
| Steel poison immunity / Corrosion | Early poison gate omitted Steel | Steel and Poison are immune; Corrosion remains the bypass | Dedicated regression, clean build, JIT boot PASS |
| Clear Body | Local gate already permits self-inflicted drops | Upstream fix already represented semantically | Preserve | Source inspection PASS |
| Anger Point | Older critical-hit script directly sets Attack to +6 | Newer upstream +6/+12 constant bug does not exist in this script | Preserve | Source inspection PASS; critical-hit fixture pending |
| Sturdy / Life Orb modern ordering | Local sequential post-damage/faint controller | Upstream fixes require the newer batch damage and performance pipeline | Do not mix pipelines; keep as documented fixture-dependent risk | Static audit complete; spread/recoil fixtures pending |

## Items and general move activation

Type Gems now require a damaging move and no longer activate on status moves. The
change is covered by a dedicated contract and applies across the move set without
altering move data or campaign balance.

Expanded ability storage reuses the previously unused top bit of BoxPokemon EXP:
EXP remains 21 bits (more than every legal level-100 total), the next ten bits stay
unused, and bit 31 stores the ability's ninth bit. The BoxPokemon/save structure
size is unchanged, so valid V2.0 saves keep their exact EXP and decode legacy
abilities with a zero high bit.

## Deliberately excluded work

- Dynamax, Max Moves, Terastal, and their dependencies remain outside V2.1.
- Placeholder records for mechanics not used by campaign trainers are not treated
  as release blockers unless the Generations design documents or distributes them
  as functional content.
- Broad modern move-performance and test-harness refactors are not imported solely
  to obtain a single behavior; applicable deltas must be isolated on the Generations
  controller.

## Remaining playable evidence

The source and behavior contracts prove the integrated code paths, but do not
replace an in-battle fixture. The matrices in `docs/V21_TEST_PLAN.md` remain pending
where no compatible save or battle fixture is available, especially Sparkling Aria
doubles, Anger Point, Sturdy/recoil ordering, and the reported boss scenarios.
