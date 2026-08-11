# HeartGold Generations v2.2.1

v2.2.1 is a focused corrective release for v2.2. It does not change wild
encounters, evolution methods, save structures, the level curve, or the
disabled 60 FPS policy.

## Gen 9 sprite corrections

- Replaced every canonical Gen 9 battle sprite or icon that still used the
  Bulbasaur/blank placeholder. The regression audit now passes for all
  **120/120** canonical Gen 9 species.
- Corrected primary assets for 27 species: Oinkologne, Dolliv, Squawkabilly,
  Naclstack, Bellibolt, Bramblin, Brambleghast, Flittle, Orthworm, Dondozo,
  Brute Bonnet, Sandy Shocks, Iron Treads, Iron Bundle, Iron Hands, Iron
  Jugulis, Iron Moth, Wo-Chien, Iron Leaves, Poltchageist, Sinistcha, Okidogi,
  Munkidori, Ogerpon, Iron Boulder, Iron Crown, and Terapagos.
- Imported 17 available corrections from the hg-engine upstream sprite set.
- Adapted the remaining ten from the pinned PokeAPI/Smogon-style source set,
  including front, back, normal, and shiny artwork. These use a duplicated
  static frame rather than fabricated animation.
- Locked battle sheets to the HGSS-compatible 160x80, indexed 4 bpp format and
  verified their generated NCGR/NCLR files inside `pokegra.narc`.

## Operational ability substitutions

The following assigned abilities had no complete operational effect in this
engine and now use mechanics that are already implemented:

| Pokemon | Non-operational assignment | v2.2.1 assignment |
| --- | --- | --- |
| Arboliva | Seed Sower | Grassy Surge |
| Gholdengo | Good as Gold | Magic Bounce |
| Koraidon | Orichalcum Pulse | Drought |
| Miraidon | Hadron Engine | Electric Surge |
| Pecharunt | Poison Puppeteer | Poison Touch |
| Flamigo (Hidden Ability) | Costar | Download |
| Paldean Tauros - Combat Breed (Hidden Ability) | Cud Chew | Sheer Force |
| Paldean Tauros - Blaze Breed (Hidden Ability) | Cud Chew | Sheer Force |
| Paldean Tauros - Aqua Breed (Hidden Ability) | Cud Chew | Sheer Force |

The availability manifest and `Ability Changes.pdf` were regenerated from the
same substitution list.

## Verification

- 41/41 repository regression scripts: PASS.
- ARM GCC 10.3.1 clean-origin build: PASS.
- All ten newly converted battle assets produce 6,448-byte 4 bpp NCGR files;
  generated `pokegra.narc` matches the copy inserted into the ROM.
- Visual review of normal/shiny front/back palettes: PASS.
- melonDS 15-second boot/responsiveness smoke: PASS.
- xdelta encode/decode round trip: PASS, byte-identical to the final ROM.

Full in-game inspection of every corrected species and every replacement
ability remains a manual/playable test boundary; automated source, generated
asset, build, and boot contracts are complete.
