# HeartGold Generations V2.0 baseline

Baseline registrada antes de qualquer backport ou alteração de código da V2.1.

## Source revisions

- Repository: `https://github.com/spearmintz1/hg-engine`
- Branch: `HeartGold-Generations-(Full-Version-2.0)`
- Base SHA: `c28e104a8ed664ce1a5dba6b0d8d83caded89b62`
- Upstream reference: `https://github.com/BluRosie/hg-engine`
- Upstream `main` SHA fetched on 2026-08-08: `c6d63fd8a34f63431214284dc08c3b7942ab0593`
- Merge base with upstream: `a6e00404c91e158fb353d3e8e5eaa00eefeabb3e`

The original branch and `HeartGold-Generations-v2.1` pointed to the same base SHA before V2.1 work began.

## Build environment

- Host: Windows, MSYS2 UCRT64
- GNU Make: 4.4.1
- CMake: 4.4.2
- Python: 3.12.13
- Host GCC: 16.1.0 (MSYS2 UCRT64)
- ARM GCC: GNU Arm Embedded Toolchain 10.3-2021.10, GCC 10.3.1
- libpng: 1.6.58
- `nitrogfx` submodule: `ac425f63ffbf7cabfaeeb6ff12f4dfbc243214e3`

The current MSYS2 ARM GCC 16 toolchain is not source-compatible with this historical branch because its default C language mode rejects an old-style function declaration in `include/sound.h`. GCC ARM 10.3 was selected to reproduce the intended historical build without modifying V2.0 source code.

## Input ROM

- File: `rom.nds` (kept local and ignored by Git)
- Game code accepted by the build: `IPKE`
- Size: 134,217,728 bytes
- SHA-256: `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D`

## Clean build

Commands:

```sh
export DEVKITARM=/opt/gcc-arm-none-eabi-10.3-2021.10
make clean
make clean_code
make -j"$(nproc)"
```

Result: successful. The build completed with `Done. See output test.nds.` and left no tracked source modifications.

- Output: `test.nds`
- Size: 181,388,256 bytes
- SHA-256: `A9F8D4C76F8E9C127E8BAE2479280D970BCBF4B9235A8C2503A790E405D41979`
- MD5: `A253819DF31608CB3F7E48BA0024D053`
- Approximate first clean-build duration on the Windows-mounted workspace: 21 minutes

## Baseline warnings

The successful build emitted 10 warnings:

1. `src/pokemon.c:2096`: signed/unsigned comparison.
2. `data/itemdata/itemdata.c:39146`: integer `250000` overflows `unsigned short` and becomes `53392`.
3. `data/battle_scripts/subscripts/subscript_0451_HANDLE_GEM_ACTIVATION_MESSAGE.s`: missing final newline.
4. Four libpng `bKGD: invalid index` warnings.
5. Two libpng `tRNS: invalid` warnings.
6. `armips/data/headbutt.s:2762`: file not closed before opening another file.

These are baseline observations, not silently corrected during environment setup. They must be classified in the V2.1 audit before any source change.

## Boot smoke tests

### DeSmuME

- Version: 0.9.13 x64
- Result: pass
- Evidence: emulator internal screenshot reached the Pokémon HeartGold title screen and displayed the Generations build.

### melonDS interpreter

- Version: 1.1
- Configuration: `[JIT] Enable = false`
- Result: pass
- Evidence: emulator ran at 60/60 FPS and reached the Pokémon HeartGold title screen.

### Pending baseline tests

- melonDS JIT boot and the two-battle D-pad reproduction
- New-save campaign smoke test
- Save compatibility fixtures for later progression states
- Physical hardware, TWiLight Menu++, and flashcart tests

No source backport is authorized until the applicable reproduction or test fixture for its subsystem has been prepared.
