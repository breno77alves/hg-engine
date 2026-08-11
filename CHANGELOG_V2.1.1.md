# Pokémon HeartGold Generations V2.1.1

V2.1.1 is a focused compatibility update for V2.1. It keeps the same content,
progression, save layout, and battle-engine behavior while correcting Pokémon
rendering in the Dress Pokémon accessory screen.

## Fixed

- Included the existing HGSS pokepic unscan patch in the final ARM9 build.
- Fixed the corrupted striped/block display shown in place of every Pokémon on
  the Dress Pokémon screen.
- Added a regression contract that requires both the patch implementation and
  its inclusion in the global armips assembly.

## Compatibility and validation

- Existing V2.0 and V2.1 saves remain structurally compatible; no save fields,
  species data, progression flags, or content tables changed.
- A clean GCC 10.3 build completed successfully.
- All 29 automated regression scripts passed.
- The generated ARM9 contains `C0 46 C0 46` at `0x02009D2A`, selecting the HGSS
  unscan path used by the copied HGSS `pokegra` archive.
- The generated `a/0/0/4` archive is byte-identical to `pbr/pokegra.narc`.
- The final ROM passed a 15-second melonDS boot/responsiveness smoke test.
- The v2.1.1 xdelta round trip reproduced the final ROM byte-for-byte.

An in-game Dress Pokémon check on the reporter's exact save and physical setup
remains the final fixture-dependent confirmation; it cannot be automated without
that save/state. The compiled binary condition that caused the corruption is
corrected and regression-locked.
