# Mega Stone acquisition audit

## Result

Generations V2.1 has one engine mapping for each of its 47 item-based Mega
Evolutions. Every stone now has an acquisition path without changing encounters,
trainer teams, progression flags, or the V2.0 save layout.

The original Generations rule is retained: wild basic forms carry their line's
stone. When both personal-data item slots are equal, HeartGold's held-item routine
guarantees the item. Different slots use the original 50%/5% odds (60%/20% with a
Compound Eyes lead). `RESTORE_ITEMS_AT_BATTLE_END` transfers a caught Pokémon's new
held item to the bag and clears the temporary held slot.

The five stones without a valid wild-basic-form path are the deliberate exception:
Mewtwonite X/Y, Latiasite, Latiosite, and Diancite are sold by the Celadon Department
Store 3F clerk. Celadon is post-League, so this repairs availability without moving
the Mega Ring gate or changing Johto progression. Five duplicate evolution items
were replaced there; all five remain available from existing Goldenrod, Celadon,
Mahogany, or Safari Zone inventories.

## Inventory

| Stone | Mega target | Acquisition source | Effective chance |
| --- | --- | --- | --- |
| `ITEM_VENUSAURITE` | Venusaur | wild Bulbasaur | guaranteed |
| `ITEM_CHARIZARDITE_X` | Charizard X | wild Charmander, slot 1 | 50%; 60% with Compound Eyes |
| `ITEM_CHARIZARDITE_Y` | Charizard Y | wild Charmander, slot 2 | 5%; 20% with Compound Eyes |
| `ITEM_BLASTOISINITE` | Blastoise | wild Squirtle | guaranteed |
| `ITEM_BEEDRILLITE` | Beedrill | wild Weedle | guaranteed |
| `ITEM_PIDGEOTITE` | Pidgeot | wild Pidgey | guaranteed |
| `ITEM_ALAKAZITE` | Alakazam | wild Abra | guaranteed |
| `ITEM_SLOWBRONITE` | Slowbro | wild Slowpoke | guaranteed |
| `ITEM_GENGARITE` | Gengar | wild Gastly | guaranteed |
| `ITEM_KANGASKHANITE` | Kangaskhan | wild Kangaskhan | guaranteed |
| `ITEM_PINSIRITE` | Pinsir | wild Pinsir | guaranteed |
| `ITEM_GYARADOSITE` | Gyarados | wild Magikarp | guaranteed |
| `ITEM_AERODACTYLITE` | Aerodactyl | wild Aerodactyl | guaranteed |
| `ITEM_MEWTWONITE_X` | Mewtwo X | Celadon Department Store 3F | purchasable post-League |
| `ITEM_MEWTWONITE_Y` | Mewtwo Y | Celadon Department Store 3F | purchasable post-League |
| `ITEM_AMPHAROSITE` | Ampharos | wild Mareep | guaranteed |
| `ITEM_STEELIXITE` | Steelix | wild Onix | guaranteed |
| `ITEM_SCIZORITE` | Scizor | wild Scyther | guaranteed |
| `ITEM_HERACRONITE` | Heracross | wild Heracross | guaranteed |
| `ITEM_HOUNDOOMINITE` | Houndoom | wild Houndour | guaranteed |
| `ITEM_TYRANITARITE` | Tyranitar | wild Larvitar | guaranteed |
| `ITEM_SCEPTILITE` | Sceptile | wild Treecko | guaranteed |
| `ITEM_BLAZIKENITE` | Blaziken | wild Torchic | guaranteed |
| `ITEM_SWAMPERTITE` | Swampert | wild Mudkip | guaranteed |
| `ITEM_GARDEVOIRITE` | Gardevoir | wild Ralts, slot 2 | 5%; 20% with Compound Eyes |
| `ITEM_SABLENITE` | Sableye | wild Sableye | guaranteed |
| `ITEM_MAWILITE` | Mawile | wild Mawile | guaranteed |
| `ITEM_AGGRONITE` | Aggron | wild Aron | guaranteed |
| `ITEM_MEDICHAMITE` | Medicham | wild Meditite | guaranteed |
| `ITEM_MANECTITE` | Manectric | wild Electrike | guaranteed |
| `ITEM_SHARPEDONITE` | Sharpedo | wild Carvanha | guaranteed |
| `ITEM_CAMERUPTITE` | Camerupt | wild Numel | guaranteed |
| `ITEM_ALTARIANITE` | Altaria | wild Swablu | guaranteed |
| `ITEM_BANETTITE` | Banette | wild Shuppet | guaranteed |
| `ITEM_ABSOLITE` | Absol | wild Absol | guaranteed |
| `ITEM_GLALITITE` | Glalie | wild Snorunt | guaranteed |
| `ITEM_SALAMENCITE` | Salamence | wild Bagon | guaranteed |
| `ITEM_METAGROSSITE` | Metagross | wild Beldum | guaranteed |
| `ITEM_LATIASITE` | Latias | Celadon Department Store 3F | purchasable post-League |
| `ITEM_LATIOSITE` | Latios | Celadon Department Store 3F | purchasable post-League |
| `ITEM_LOPUNNITE` | Lopunny | wild Buneary | guaranteed |
| `ITEM_GARCHOMPITE` | Garchomp | wild Gible | guaranteed |
| `ITEM_LUCARIONITE` | Lucario | wild Riolu | guaranteed |
| `ITEM_ABOMASITE` | Abomasnow | wild Snover | guaranteed |
| `ITEM_GALLADITE` | Gallade | wild Ralts, slot 1 | 50%; 60% with Compound Eyes |
| `ITEM_AUDINITE` | Audino | wild Audino | guaranteed |
| `ITEM_DIANCITE` | Diancie | Celadon Department Store 3F | purchasable post-League |

Rayquaza remains the deliberate non-item exception: its Mega mapping is activated
by Dragon Ascent and is not part of the 47-stone inventory.

## Evidence and validation boundary

- `src/battle/mega.c` maps all 47 constants to the correct species and form.
- `armips/data/mondata.s` provides all wild-held stones and
  `armips/asm/custom/mart_items.s` provides the five legendary exceptions.
- The original HeartGold `WildMonSetRandomHeldItem` implementation documents the
  guaranteed and split-slot probabilities; the primary reference is
  [pret/pokeheartgold](https://github.com/pret/pokeheartgold).
- `src/battle/battle_input.c` retains the JIT-safe Mega D-pad table
  `{1, 2, 3, 4, 0, 5}` and the touch path remains present.
- `scripts/test_mega_stone_audit.py` locks the 47 constants, mappings, acquisition
  paths, five-item Celadon inventory, and input table.

Source contracts, generated data, build, and emulator boot can be validated here.
Obtaining every stone in a campaign, activating every Mega form, repeated-battle
D-pad/touch behavior, and save/reload remain **NOT RUN** until deterministic save
fixtures or hardware are available; they must not be reported as gameplay passes.
