# HeartGold Generations V2.1 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.1` |
| Tag | `v2.1` |
| Generations V2.0 base | `c28e104a8ed664ce1a5dba6b0d8d83caded89b62` |
| Audited upstream | `c6d63fd8a34f63431214284dc08c3b7942ab0593` |
| Common ancestor | `a6e00404c91e158fb353d3e8e5eaa00eefeabb3e` |
| Final source | annotated tag `v2.1` (tag target is the authoritative release SHA) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `test.nds` | `181307872` | `5211194D31C6C31126AB16AB7407DE4F19398C7C9176CB0802051EB24AD6FA40` | `57F85042A55D56C0693316249CE67467` |
| `HeartGold-Generations-v2.1.xdelta` | `25712791` | `798650F85C92C4BAA48E4524F1211668FC4529770B87A0394B1851C881F965D4` | `692971061BC277F417D7476CBEA99479` |

The commercial base and complete patched ROM are local-only and are not committed
or uploaded. Distribute only the patch, source, changelog, and documentation.

## Build and validation

- Final clean build: **PASS**. `make clean` removed all outputs; an initial asset
  command exposed a missing UCRT64 DLL path, then the same clean tree resumed with
  the corrected environment and reached `Done. See output test.nds.` Every code,
  data, graphic, audio, and archive output was regenerated after the clean.
- Compiler warnings/errors: **0 C warnings, 0 final-pass errors**. The asset tools
  reproduce eight inherited non-fatal warnings: one missing final newline, four
  invalid `bKGD` indices, two invalid `tRNS` chunks, and one armips file-open
  warning in `headbutt.s`. The previous independent clean build has the same set.
- Automated regression scripts: **28/28 PASS**.
- melonDS JIT boot smoke: **PASS after the last code change** (process alive and
  responsive after 15 seconds). The requested repeat on the byte-identical source
  state's final clean artifact was **NOT RUN — app approval/usage limit**, not a ROM
  failure.
- Generated ARM9/overlay AP byte contract: **PASS** at ARM9 `0xA18`, overlay 1
  `0xD2C`, and overlay 123 `0xAC`/`0x164`.
- Patch round trip: **PASS**. Decoding the xdelta over the required base reproduced
  the final ROM SHA-256 byte-for-byte; the temporary decoded ROM was deleted.
- Working tree / origin synchronization: finalized by the release commit and tag;
  build outputs, complete ROMs, local release tooling, and patch staging are ignored.

Fixture-dependent playthrough, DeSmuME, V2.0 Save A–D, and physical hardware
matrices retain the **NOT RUN** statuses documented in `V21_TEST_PLAN.md`. They are
not prerequisites that can be fabricated from source alone.

## Documentation index

- `CHANGELOG_V2.1.md`
- `docs/UPSTREAM_AUDIT.md`
- `docs/GENERATIONS_BUGS.md`
- `docs/MOVE_ABILITY_AUDIT.md`
- `docs/MEGA_STONE_AUDIT.md`
- `docs/SAVE_COMPATIBILITY.md`
- `docs/D_PAD_JIT_ANALYSIS.md`
- `docs/FINAL_CODE_AUDIT.md`
- `docs/V21_TEST_PLAN.md`

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.1.xdelta HeartGold-Generations-v2.1.nds
```

The source file must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify that the output SHA-256 matches the local final ROM row. If
either hash differs, stop and obtain the correct clean base or patch; do not force
application to a different ROM revision.
