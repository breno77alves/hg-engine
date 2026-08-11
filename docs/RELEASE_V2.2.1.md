# HeartGold Generations v2.2.1 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.2.1` |
| Tag | `v2.2.1` |
| Parent release | annotated tag `v2.2` |
| Sprite correction commit | `657f01c2d` |
| Ability correction commit | `6a9758f57` |
| Final source | annotated tag `v2.2.1` (tag target is authoritative) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `HeartGold-Generations-v2.2.1.nds` | `181331424` | `47273F5A085F8692ADBE26FBC77E54ADD0CFBECF7A6D3409D461576568D336A4` | `F72F4502AB30607CE4A76C4A10A27BAB` |
| `HeartGold-Generations-v2.2.1.xdelta` | `26631704` | `817985577FB5AC8A53D218199F03AF4DFFA7D4201041C05DE649084934954472` | `88EE4782144175E22D555B5D1C3691C6` |

The commercial base and complete patched ROM are local-only and are not
committed or uploaded. Distribute only the patch, source, changelog, and
documentation.

## Release acceptance

- Canonical Gen 9 primary sprite/icon audit: **PASS - 120/120 non-placeholder**.
- Previously affected species corrected: **27**.
- Pinned PokeAPI/Smogon conversions: **10 species, front/back and normal/shiny**.
- Battle sheets and generated NCGR files: **PASS - indexed 4 bpp**.
- Known obtainable non-operational abilities: **zero assignments retained**.
- Repository regression scripts: **PASS - 41/41**.
- Clean-origin GCC 10.3 build: **PASS**.
- Generated `pokegra.narc` insertion hash: **PASS, byte-identical**.
- melonDS boot/responsiveness smoke (15 seconds): **PASS**.
- xdelta decode round trip: **PASS**, reproducing the final ROM SHA-256
  byte-for-byte.
- Wild encounters, evolution rules, persistent save layouts, and 60 FPS
  configuration: **unchanged from v2.2**.

## Runtime validation boundary

All automated source contracts, sprite formats, generated NARCs, clean-origin
build output, visual palette review, emulator boot, and patch round trip are
verified. Full playable inspection of all 27 corrected species and battle
activation of each substituted ability is not reported as complete without
prepared saves/fixtures.

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.2.1.xdelta HeartGold-Generations-v2.2.1.nds
```

The source must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify the final ROM SHA-256. Do not force the patch onto a
different ROM revision.
