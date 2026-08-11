# HeartGold Generations v2.4 test plan

## Automated contracts

- audit every eligible starter against canonical family roots, evolution data,
  special categories, alternative forms, sprites, icons, cries and followers;
- require a safe damaging move for every pool entry;
- run at least 100,000 full Trainer IDs and require deterministic results,
  three species and three primary types per trio, and no overlap between Johto
  and Kanto;
- preserve fixed golden vectors for the selection algorithm;
- verify the Elm launch hook, dynamic species/cry table and generic messages;
- verify the exact 21 Silver trainer variants, the v2.4 save-flag gate,
  evolution staging and regenerated moves;
- verify all three Oak balls keep independent physical positions while their
  species, sprite, cry, name and confirmation are dynamic;
- reject Oak finalization unless the party count increased by exactly one;
- preserve the six classic starters in the required Route 34 periods;
- preserve save ABI, Mega, battle D-pad, automatic HMs and frame-rate config.

## Build gates

- incremental and clean builds with Arm GNU Toolchain 10.3-2021.10;
- zero new C compiler warnings or assembler errors;
- generated starter core fits the injected code budget;
- final ROM contains the generated scripts, messages and hook bytes;
- xdelta encode/decode round trip reproduces the final ROM SHA-256 exactly.

## Playable matrix

- new-save Elm selection: inspect, rotate, cancel and confirm all three balls;
- reload the same save and confirm that the trio is unchanged;
- exercise all seven Silver battles with one-, two-, three-stage and branched
  starter families;
- inspect and accept all three Oak balls, including nickname and full-party
  behavior;
- boot saves from v2.0 through v2.3 before and after Elm/Oak milestones;
- verify Mega, battle D-pad and automatic HMs in JIT and interpreter modes.

No disposable campaign or historical-save fixtures are currently present.
Those playable cases must stay marked fixture-dependent until exercised with
appropriate test saves; source and build contracts are not a substitute.
