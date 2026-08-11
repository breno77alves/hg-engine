# HeartGold Generations v2.3 test plan

## Automated contracts

- battle-menu 3x2 grid, including `RUN + Up -> FIGHT`;
- no write or repoint at `0x02269F4C` and no Mega-table change;
- exact eight-entry HM/item/badge table;
- HM and badge ownership plus first non-Egg actor selection;
- vanilla fallback for all non-HM moves;
- all seven contextual field scripts still call command 141 and retain their
  original field setup/effect paths;
- HM02-only bag interception and `FLY / TEACH / CANCEL` routing;
- Fly restriction and execution delegated to the original field-move table;
- no persistent structure or save-layout change.

## Build gates

- incremental build with GCC 10.3;
- clean build with GCC 10.3;
- zero compiler warnings or assembler errors;
- hook bytes and protected Mega/JIT bytes checked in the final ROM;
- xdelta encode/decode round trip with identical SHA-256.

## Playable matrix

- boot and title-screen smoke in melonDS;
- ten consecutive battles, full command navigation, and Mega by touch/D-pad;
- positive and negative cases for all eight HMs;
- Fly destination, Teach, Cancel, follower, disguise, Safari/Pal Park, and
  unvisited-destination cases;
- loading saves from v2.0, v2.1, v2.1.1, v2.2, and v2.2.1;
- JIT and interpreter runs.

The repository contains no `.sav` or `.dsv` campaign fixtures. Cases requiring
specific badges, obstacles, destinations, Mega-ready parties, or historical
saves must therefore be marked fixture-dependent until exercised manually;
source/build contracts do not substitute for those playable results.

## Release results

- Repository regression scripts: **PASS - 45/45**.
- Incremental GCC 10.3 build: **PASS**.
- Clean-origin GCC 10.3 build: **PASS**. The long asset generation was resumed
  after runner timeouts; every retained artifact was created after the same
  `make clean`.
- v2.3 C/ASM compiler warnings: **zero**. The build retains the catalogued
  legacy newline and PNG-metadata warnings covered by the inherited-warning
  contract.
- Final overlay 12 bytes: `RUN + Up` branch `23 D1 -> C0 46`; protected
  `0x02269F4C` bytes remain `D4 02 3D 02`, identical to v2.2.1.
- Features/QoL PDF render: **PASS - one A4 page, visually inspected**.
- melonDS boot/responsiveness smoke: **PASS** - hg-engine splash and overworld,
  emulator reporting 60/60.
- xdelta encode/decode round trip: **PASS**, byte-identical SHA-256.
- Fixture-dependent playable matrix: **NOT CLAIMED**. No disposable campaign or
  historical-save fixtures were available, and the detected personal save was
  not modified.
