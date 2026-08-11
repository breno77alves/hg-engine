# HeartGold Generations V2.1.1 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.1.1` |
| Tag | `v2.1.1` |
| Parent release | annotated tag `v2.1` |
| Fix commit | `3caed7162` |
| Final source | annotated tag `v2.1.1` (tag target is the authoritative release SHA) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `HeartGold-Generations-v2.1.1.nds` | `181307872` | `59767B118498373004FBB21FF2D353DFD7E89D1EC4314AAB1464BA8236536F42` | `CD83FF98EA5D54D31CB023B389886175` |
| `HeartGold-Generations-v2.1.1.xdelta` | `26372528` | `87C4D8E534F8D9F06286E94A431A7E1AE6BF3B587BD52A3C17DF43FC20FCAA0B` | `80DECD80B54E24E8FB3141CE2D6E24B0` |

The commercial base and complete patched ROM are local-only and are not committed
or uploaded. Distribute only the patch, source, changelog, and documentation.

## Corrected behavior

Overlay 41's Dress Pokémon view requests the shared `pbr/pokegra.narc` archive.
Generations builds that archive from HGSS `a/0/0/4`, but V2.1 omitted the global
include for the existing ARM9 patch and consequently selected the incompatible DP
unscan routine for NARC `0xC2`. V2.1.1 includes `armips/asm/sprites.s`, replacing
the conditional DP branch at ARM9 `0x02009D2A` with two Thumb NOPs so execution
continues through the HGSS unscan path.

## Build and validation

- Clean build with inherited ARM GCC 10.3 toolchain: **PASS**.
- Automated regression scripts: **29/29 PASS**.
- Dress Pokémon source/include regression contract: **PASS**.
- Generated ARM9 bytes at `0x02009D2A`: **PASS** (`C0 46 C0 46`).
- Generated HGSS source/archive equality (`a/0/0/4` and `pbr/pokegra.narc`):
  **PASS**.
- Existing non-runtime AP and hardware-compatibility contract: **PASS**.
- melonDS boot/responsiveness smoke (15 seconds): **PASS**.
- xdelta decode round trip over the required clean base: **PASS**, reproducing
  the final ROM SHA-256 byte-for-byte.
- Exact Dress Pokémon scene with the reporter's save/state or physical hardware:
  **NOT RUN — fixture unavailable**.

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.1.1.xdelta HeartGold-Generations-v2.1.1.nds
```

The source file must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify the final ROM SHA-256. Do not force the patch onto a
different ROM revision.
