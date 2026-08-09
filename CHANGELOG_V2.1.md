# Pokémon HeartGold Generations V2.1

V2.1 preserves the content, trainers, encounters, progression, difficulty, and
save layout of Generations V2.0 while selectively backporting applicable fixes
from audited hg-engine revision `c6d63fd8a34f63431214284dc08c3b7942ab0593`.
The exact V2.0 base is `c28e104a8ed664ce1a5dba6b0d8d83caded89b62`.

## Critical Fixes

- Replaced battle-menu runtime self-patching with a permanent D-pad table pointer,
  preventing the melonDS JIT navigation failure across later battles while keeping
  four moves, Cancel, Mega D-pad input, and touch input.
- Backported the Hall of Fame 4bpp scan-order correction.
- Reconstructed simultaneous-faint handling for the older Generations controller,
  including two opposing slots owned by the same trainer and EXP de-duplication.
- Replaced the legacy runtime AP/decompression hook with current direct card-check
  and dsprotect patches compatible with the upstream DSpico design.

## Battle Engine Fixes

- Corrected drain arithmetic for one-damage and fractional-drain cases.
- Corrected damaging forced switches for Dragon Tail and Circle Throw, including
  Substitute, faint, reserve, doubles, and switch-in ordering gates.
- Made No Guard symmetric for attacker/defender semi-invulnerable checks.
- Fixed Poison/Steel immunity consistency while preserving Corrosion.
- Prevented type Gems from activating on status moves.
- Allowed Water Absorb to intercept modern Water-type status moves.
- Decoupled Defiant's Attack cap from Competitive's Special Attack cap.
- Kept hard level-cap behavior shared by ordinary and capture EXP.

## Move / Ability Fixes

- Implemented Power Trip's 20 + 20-per-positive-stage scaling.
- Implemented Reversal's Flail-style HP bands.
- Made Body Press use the attacker's Defense and Defense stage.
- Changed Infestation to the binding move effect and audited the complete local
  bind/residual/switch/message flow.
- Expanded ability storage to nine bits without changing Pokémon/save record size,
  fixing Frigibax, Arctibax, and Baxcalibur ability IDs through evolution.
- Audited every move used by trainers and every normal ability reachable in the
  campaign; results are in `docs/MOVE_ABILITY_AUDIT.md`.

## Generations-specific Fixes

- Prevented post-Red Elite Four rematches from lowering the hard cap to 65.
- Made Elm-lab Infinite Candy and Pocket Heal rewards deterministic across reloads.
- Corrected Falkner's reusable-TM dialogue.
- Prevented the Medicine pocket from overflowing while retaining access to legacy
  V2.0 stacks.
- Restored Own Tempo Rockruff as a 1% Route 33 encounter in every time period.
- Corrected 11 modern Pokédex descriptions that exceeded the no-wrap line limit.
- Audited all 47 Mega Stones and restored acquisition paths for the five legendary
  stones that lacked a valid wild-basic-form source.

## QoL

- Retained and regression-locked the current EV/IV summary viewer.
- Retained and regression-locked reusable Repels with Max → Super → normal priority.
- Retained Critical Capture and applied its final generation-specific animation
  guard without changing capture rates.
- Retained Capture EXP and verified its shared hard-cap path.
- Retained modern vitamin caps of 252 per stat and 510 total.
- Retained the modern friendship-evolution threshold of 160.
- Enabled evolution triggers at the hard cap without allowing candies above it.

## Compatibility

- Clean builds use the inherited ARM GCC 10.3 toolchain and no 60 FPS hacks.
- V2.0 `SaveData`, bag, pocket, PC, and Pokémon record sizes remain unchanged.
- Generated ARM9/overlay AP bytes are verified after builds.
- Wild doubles, Force Set, restore-items-at-battle-end, Z-Moves, Dynamax, Terastal,
  and global/battle-only 60 FPS remain disabled.

## Known Issues

- Save A/B/C/D playthrough checks are not run because no V2.0 save fixtures were
  supplied. Structural compatibility passes; runtime compatibility still needs
  those files.
- Extended D-pad/Mega, Ariana double-KO, Hall of Fame, move/ability, QoL, and full
  campaign matrices need prepared playable fixtures. Automated source contracts,
  clean builds, generated-byte checks, and available melonDS JIT boot smokes pass.
- DeSmuME and physical DS/3DS/TWiLight/R4/DSpico runs were not available in this
  environment and are not reported as passes.
- Ability Patch is not obtainable in the campaign. Its inherited nominal 250,000
  price remains serialized through the legacy 16-bit field as 53,392; the invasive
  upstream wide-price subsystem was deliberately excluded.
- The inherited modern-engine TODO backlog is recorded in
  `docs/FINAL_CODE_AUDIT.md`; excluded or unreachable mechanics were not imported
  solely to remove comments.

## Upstream revisions represented

Direct or semantic backports/audits include:

`e45e1ab475b23e4aafda472d6a13d8248d17e5a9`,
`3919379e838bf07f39659769b19ecedc70262eda`,
`245aa5e38e99b2b4668985277cf23d4d85d501d9`,
`f4fd450447c458bad4230649e6a19a8552f65678`, `ddabadb780`,
`42496dbd9`, `7d26f57fe`, `207f93c92`, `531222a5e`, `22686956f`,
`12cf75b8b`, `8242d462b`, `87d34f105`, `a18db2ce6`, `f5b5488e0`,
`c67ac01faafc2d5d00763ca444d239024156ff8c`,
`031c579a4698f43832f75cb3cf11ba043fd6e229`, `5418b65cf`,
`3265d051c`, `22df8b40f3fe374675589e81d5e55390e51d1451`,
`b9b9cab7363b492ebb13ce010a70a45d767079dd`,
`8d780780b7881a426417162c8d783ee09d248a91`, `8b448a7e`,
`153045c54`, `07fe8db4b`,
`637603374c1aa14b961f024ea0546e505d30f57d`,
`75ef1e1b39add295ea9b986cd91ecc5fc94f25ba`,
`cb721681e62012d864b01620a6d08034f08b948c`,
`784e888295ce5cbac932771ce7524c28ad26fc10`, and
`b15b01c9fa1add4ce196186ab1125f49b0ddc4fb`.

Some are already ancestors of the Generations base or intermediate revisions whose
final semantics were reconstructed; `docs/UPSTREAM_AUDIT.md` is the authoritative
per-revision decision ledger. Deliberate exclusions and reasons are also recorded
there, including 60 FPS, unsolicited battle gimmicks, restore-items, and wide prices.

## Local V2.1 history

The branch contains focused commits from the V2.0 base through the final release
manifest. Use `git log --reverse c28e104a8..v2.1` for the complete immutable list; the
release manifest records the final source revision and artifact hashes.
