# Generations V2.0 public bug audit

Audit date: 2026-08-09. The main report source is the public
[V2.0 release thread](https://www.reddit.com/r/PokemonROMhacks/comments/1n814q5/pok%C3%A9mon_heartgold_generations_v20_full_trainergym/),
cross-checked against this branch, the V2.0 base commit, upstream hg-engine,
and the original HeartGold decompilation where applicable.

Status meanings:

- **Fixed**: a deterministic source/data cause was found and a regression test
  covers the V2.1 repair.
- **Fixture pending**: the report is plausible, but proving or safely changing it
  requires an in-game save/state at the affected scene.
- **Won't fix**: intended behavior, an external-tool/base-ROM problem, or a change
  that would alter Generations campaign design without enough evidence.

## Fixed in V2.1

| Report | Finding and repair |
|---|---|
| D-pad/fast-forward crash | Unsafe JIT-sensitive input path repaired. |
| Hall of Fame crash/graphics | Hall of Fame graphics allocation and scan path repaired. |
| Elm's postgame rewards/save behavior | Event-state and reward flow repaired without changing save layout. |
| Elite Four level cap resetting after Red | Post-Red progression state now retains the intended cap. |
| Infestation, Power Trip, Reversal, Body Press | Battle scripts/formulas repaired and regression-tested. |
| Dragon Tail/Circle Throw | Forced-switch failure and edge cases repaired. |
| Double faint against Ariana | Simultaneous-faint outcome ordering repaired. |
| Frigibax missing ability | Expanded ability storage now preserves all 9 bits without enlarging boxed Pokémon data. |
| Missing Mega Stones | All 47 item-based Mega Evolutions now have a postgame acquisition route. |
| Falkner says TMs are single-use | Gym text now describes reusable TMs. |
| Medicine pocket reports "no room" | 28 added remedies/mints no longer overfill the 40-slot save array; legacy V2.0 stacks remain readable and consumable. |
| Own Tempo Rockruff unavailable | A 1% form-aware Route 33 encounter was added to each time period by replacing a duplicated rare slot. |
| Unwrapped modern Pokédex descriptions | Eleven entries that had no line breaks now use three bounded lines. |

## Fixture pending

| Report | Current evidence / required fixture |
|---|---|
| A caught wild Mega can remain Mega in the party | The form is reported to self-correct on its next battle. A save immediately before catching a wild Mega is needed to validate party insertion and battle-end reversion. |
| Heliolisk Hall of Fame visual corruption | The general Hall of Fame graphics path is repaired, but this species-specific scene still needs a Hall of Fame fixture. |
| Dry Skin AI repeatedly selects Water moves | The AI does not fully model every ability immunity. A deterministic trainer/battle fixture is needed before changing scoring globally. |
| Bug-Catching Contest can exceed Whitney's cap | The report is credible, but the contest's temporary-party rules and intended cap policy need an event fixture/design decision. |
| Bad Egg after healing Mega Mawile near Lance | No deterministic source path or reproducible save was supplied. Expanded ability storage removed one known corruption risk, but this exact report is not claimed fixed. |
| Route 48 wild levels feel too low | Levels 20–25 are inherited from vanilla while Route 47 reaches 31–40. This may be map-progression design; change only after a playthrough fixture confirms the route ordering makes it erroneous. |
| Night evolution failures | The report lacks species, time, map, and save-state details. A pre-evolution fixture is required. |

## Won't fix

| Report | Reason |
|---|---|
| Hail does not deal chip damage | Generations intentionally uses the modern Snow behavior; this is not a battle-engine regression. |
| Expanded Pokédex lacks full encounter locations | Area data was not authored for every added species/form. Generating speculative locations would be less accurate than leaving them absent. |
| PKHeX marks or corrupts the save | Stock PKHeX does not understand this ROM hack's expanded data contract. External-editor compatibility is outside the ROM's supported save path. |
| Patch/boot failure with an arbitrary ROM | The patch requires the documented clean base ROM. A mismatched base is not an engine defect. |

## Compatibility notes

- `NUM_BAG_MEDICINE` remains 40 and `BAG_DATA` is not resized.
- Existing V2.0 Ability Capsules, regional medicines, Ability Patches, cheese,
  crunchies, and Nature Mints that already reside in Medicine remain usable.
  Newly obtained copies use Items; the code prevents duplicate simultaneous
  stacks across the legacy and current pockets.
- Route 33's encounter change removes only duplicate 1% entries and does not
  remove any species from the route.
