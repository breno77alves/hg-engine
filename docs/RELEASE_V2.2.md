# HeartGold Generations v2.2 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.2` |
| Tag | `v2.2` |
| Parent release | annotated tag `v2.1.1` |
| Availability commit | `add3ada30` |
| Abilities/forms commit | `46f21b2a1` |
| Documentation commit | `4c711971d` |
| Final source | annotated tag `v2.2` (tag target is authoritative) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `HeartGold-Generations-v2.2.nds` | `181320160` | `8EC4AAA00DD4764F6A63F2442BE4A49CA9BBA0E9CC88D2450D735C2E08EB6559` | `32B0FA7E7F7A186BF02487FCECD6639C` |
| `HeartGold-Generations-v2.2.xdelta` | `26384430` | `56040F09BA57BB5747174DD03199F00BE624DC8FE67B3A305982F89D78C67E11` | `52D97231A681EBFEFA1230F5260A088E` |

The commercial base and complete patched ROM are local-only and are not
committed or uploaded. Distribute only the patch, source, changelog, and
documentation.

## Release acceptance

- Complete single-save graph: **PASS — 1,025/1,025 species**.
- Supported functional-form matrix: **PASS — 61 targets**.
- v2.1.1 encounter regression: **PASS — all 441 baseline wild species retained**.
- Real-trade-only evolutions: **PASS — zero**.
- Required evolution/form items: **PASS — repeatable sources**.
- Yamper on Route 29: **PASS — 10% morning/day, 5% night**.
- Legendary/mythical allocation: **PASS — exactly 1% in all periods**.
- Repository regression scripts: **PASS — 39/39**.
- Clean GCC 10.3 build: **PASS**.
- melonDS boot/responsiveness smoke (15 seconds): **PASS**.
- xdelta decode round trip: **PASS**, reproducing the final ROM SHA-256
  byte-for-byte.
- 60 FPS global/battle hacks: **disabled and regression-locked**.
- Persistent save layouts inherited from v2.0/v2.1/v2.1.1: **unchanged**.

## Runtime validation boundary

The source contracts, clean build, generated files, emulator boot, and patch
round trip are verified. Full playable Route 29/evolution, special-form battle,
post-game legendary, and representative old-save scenarios require prepared
save fixtures or manual play and are not reported as passes. See
`docs/V22_TEST_PLAN.md` for the exact fixture matrix.

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.2.xdelta HeartGold-Generations-v2.2.nds
```

The source must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify the final ROM SHA-256. Do not force the patch onto a
different ROM revision.
