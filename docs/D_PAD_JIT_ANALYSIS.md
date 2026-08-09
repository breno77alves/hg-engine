# D-pad / melonDS JIT analysis

## Reproduction target

The reported failure occurs with melonDS JIT after leaving one battle and entering
another: the move menu still accepts touch input, but D-pad navigation stops selecting
moves. The Generations V2.0 implementation changes an overlay 12 literal at runtime
whenever the Mega button layout is selected or restored.

## Overlay facts

The values below were verified against the decompressed US HeartGold overlay extracted
from the configured `rom.nds`:

- overlay: 12;
- load address: `0x022378C0`;
- RAM size: `0x00037380` (226,176 bytes);
- D-pad grid literal: `0x02269F4C`;
- original literal value: `0x0226E218`;
- original six-byte table: `01 02 03 04 00 00`;
- Mega table required by Generations: `01 02 03 04 00 05`.

Thumb disassembly of the function beginning at `0x02269DD4` shows four reads of the
literal, including:

```text
02269E22  ldr r0, [pc, #296]  ; 0x02269F4C
02269E4A  ldr r0, [pc, #256]  ; 0x02269F4C
02269E82  ldr r0, [pc, #200]  ; 0x02269F4C
02269EC4  ldr r2, [pc, #132]  ; 0x02269F4C
```

The address is a literal-pool word consumed by the D-pad/touch-grid callback, not a
normal Generations state variable. Writing a different pointer into it while overlay
12 is executing is therefore self-modifying code from a JIT cache-coherency
perspective, even though the write targets data bytes in the literal pool.

## V2.1 design

V2.1 uses three explicit maps in `src/battle/battle_input.c`:

- `DPadSelectTouchDataIndexVanilla` — `{1, 2, 3, 4, 0, 0}`;
- `DPadSelectTouchDataIndexMega` — `{1, 2, 3, 4, 0, 5}`;
- `DPadSelectTouchDataIndexActive` — mutable and initialized to the vanilla map.

`repoints` changes the literal once while constructing the ROM so it permanently
points to `DPadSelectTouchDataIndexActive`. At runtime both move-menu callbacks only
change byte 5 of the active table. The other five bytes are identical, so a one-byte
write also prevents the input callback from observing a partially copied map.

There are no remaining C runtime writes to `0x02269F4C`.

## Automated regression check

Run after extracting the untouched base overlay:

```sh
python scripts/test_dpad_jit_safety.py --expect-vanilla
```

Run after building V2.1 (with `DEVKITARM` available):

```sh
python scripts/test_dpad_jit_safety.py --expect-built
```

The check validates the source contract, both fixed maps, mutable active map, absence
of runtime writes, build-time repoint, original overlay facts, and final linked symbol
address. For the reviewed build, the active table linked at `0x023D4C10` and overlay
12's literal contained the same value.

## Current test result

- incremental `make clean_code` / build: PASS after correcting the local toolchain
  `PATH`; no D-pad-specific compiler warning remains;
- final reviewed ROM size: 181,388,256 bytes;
- final reviewed ROM SHA-256: `E50D6A3FA3C64D910FC4398969BE5D5E2F864BA8011D1706B73C65AE582D28C2`;
- melonDS 1.1 with `[JIT] Enable = true`: title/opening sequence visual smoke PASS
  at 60/60 FPS;
- binary pointer check: PASS.

The 10+ consecutive-battle matrix, D-pad/touch Mega selection, post-Mega navigation,
switching, and fast-forward cases remain NOT RUN until a deterministic battle/Mega
save fixture is available. The source fix is not promoted to full behavioral PASS
until those cases complete.
