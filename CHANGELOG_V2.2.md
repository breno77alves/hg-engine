# Pokémon HeartGold Generations v2.2

V2.2 is the complete single-save National Dex release. It builds on v2.1.1,
keeps the established save layout and stability fixes, and makes all 1,025
National Dex species obtainable without a real trade or temporary event.

## Availability and encounters

- Added a generated availability graph and player-facing manifest covering all
  1,025 species plus 61 supported functional forms.
- Preserved every species available in v2.1.1 while adding missing evolutionary
  roots to habitat-appropriate encounter tables.
- Kept ordinary families primarily in Johto and concentrated legendary,
  mythical, paradox, and unusually strong species in Kanto or the post-game.
- Reserved 1% slots in every time period for legendary, mythical, and post-game
  special encounters.
- Added Yamper to Route 29 at 10% in the morning/day and 5% at night. Boltund is
  obtained by evolving Yamper at level 25 and is not a separate wild encounter.
- Added the four Galar fossils to the National Park at 1% (two in the morning,
  two during the day) while preserving Aerodactyl there at night.
- Updated Pokédex area data from the same generated encounter source.

## Evolutions and repeatable items

- Added Linking Cord alternatives for every trade evolution, including item
  trades and every Pumpkaboo size.
- Changed Karrablast and Shelmet to level 30 evolutions.
- Retained level 32 alternatives for walking/multiplayer methods, level 38 for
  Palafin, and Amulet Coin for Gimmighoul.
- Added stable same-save methods for Meltan, Kubfu, Urshifu, and other families
  that depended on unavailable modern systems.
- Made Linking Cord, Nectars, Memories, Scrolls, Masks, Booster Energy, Chipped
  Pot, Amulet Coin, and the supported evolution items repeatably purchasable.

## Abilities and forms

- Completed operational battle handling for Protosynthesis, Quark Drive,
  Hospitality, Opportunist, Stakeout, Cheek Pouch, Cotton Down, Toxic Chain,
  Gulp Missile, Zero to Hero, Shields Down, Hunger Switch, and Schooling.
- Completed battle-form transitions for Cramorant, Morpeko, Minior, Palafin,
  Wishiwashi, and the existing Eiscue path.
- Used stability-first substitutions where the authentic mechanic depends on an
  invasive unsupported system: Yamper/Pickup, Tatsugiri/Storm Drain,
  Oricorio/Own Tempo, Galarian Stunfisk/Magnet Pull, and Terapagos/Filter.
- Added repeatable item paths for Oricorio, Silvally, Ogerpon, and both Urshifu
  styles. Cosmetic, fusion, mount, and automatic battle-only appearances do not
  count as separate captures.

## Documentation and validation

- Replaced `Non-Included Pokemon` with the complete availability matrix.
- Regenerated Wild Encounters, Evolution Changes, Ability Changes, New Item
  Locations, and Features/QoL from the v2.2 sources.
- Reissued the type and Gym Leader references with v2.2 identification.
- Added automated contracts for availability, evolution methods, repeatable
  items, habitat/rarity rules, functional forms, Pokédex areas, abilities, and
  documentation consistency.
- The 60 FPS hacks remain disabled. V2.0, v2.1, and v2.1.1 persistent save
  layouts remain unchanged.

## Distribution

Only source code, documentation, and the xdelta patch are distributable. The
clean commercial base and complete patched ROM remain local-only.
