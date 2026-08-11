# HeartGold Generations v2.2 validation record

## Automated acceptance matrix

| Contract | Result |
| --- | --- |
| National Dex graph | PASS — 1,025/1,025 species reachable in one save |
| Functional forms | PASS — 61 supported targets represented |
| v2.1.1 availability regression | PASS — all 441 baseline wild species retained |
| Real-trade dependency | PASS — zero trade-only evolutions |
| Repeatable required items | PASS |
| Wild-stage policy | PASS — newly allocated families use viable seed stages |
| Grass slot weights | PASS — 20/20/10/10/10/10/5/5/4/4/1/1 |
| Legendary/mythical rarity | PASS — exactly 1%, all three periods |
| Route 29 Yamper | PASS — 10% morning/day, 5% night |
| National Park Galar fossils | PASS |
| Habitat/lore anchors | PASS |
| Pokédex area synchronization | PASS |
| Ability substitutions | PASS |
| Special battle mechanics source contracts | PASS |
| Save ABI/static layout | PASS |
| 60 FPS exclusion | PASS |
| Documentation/source synchronization | PASS |

The repository-wide regression run contains 39 scripts and all 39 pass.

## Build matrix

| Check | Result |
| --- | --- |
| GCC 10.3 incremental build | PASS |
| GCC 10.3 clean single-job build | PASS |
| Generated release hashes | PASS |
| xdelta encode/decode round trip | PASS — byte-identical SHA-256 |
| melonDS boot/responsiveness | PASS — alive/responsive after 15 seconds |

## Playable fixture matrix

The following scenarios require manual play or prepared save states. They are not
promoted to passes by source tests or by a boot smoke:

- new save through Route 29, capture Yamper, and evolve it at level 25;
- Linking Cord, held-item trade replacements, and branched families;
- Nectars, Memories, Masks, Scrolls, and regional-form acquisition;
- Cramorant, Morpeko, Eiscue, Wishiwashi, Minior, and Palafin form transitions;
- special abilities in singles and doubles;
- post-game legendary encounter and capture;
- runtime loading of representative v2.0, v2.1, and v2.1.1 saves.

Static save-layout compatibility is covered automatically. Exact playable save
compatibility remains fixture-dependent until representative save files are
provided. Physical DS/3DS/flashcart testing is outside this build environment.
