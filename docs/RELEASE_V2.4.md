# HeartGold Generations v2.4 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.4` |
| Tag | `v2.4` |
| Parent release | annotated tag `v2.3` |
| Baseline/tests | `270623b1f` |
| Starter generator | `08a18f1c4` |
| Elm and Silver integration | `544a95bbb` |
| Oak integration | `fcdfc9623` |
| Documentation | `0913660ea` |
| Final source | annotated tag `v2.4` (tag target is authoritative) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `HeartGold-Generations-v2.4.nds` | `181339616` | `80262F66D2DBDA5DB8A48B1590029866A5C43FBAE115681DFC086F4093D8884A` | `6A76A4BA2707B07F7BB75589C9166E88` |
| `HeartGold-Generations-v2.4.xdelta` | `26637339` | `6BCAD8654AB96CCB69199137B75B1CC923157518F79B00032E422AB5A9AB48BB` | `A0BE84228E4127C71AE019B873817968` |

The commercial base and complete patched ROM are local-only and are not
committed or uploaded. Distribute only the patch, source, changelog, and
documentation.

## Release acceptance

- Repository regression scripts plus final-ROM verification: **PASS - 48/48**.
- Starter pool audit: **PASS - 325 eligible canonical first-stage families**.
- Determinism/property run: **PASS - 100,000 full Trainer IDs**, with distinct
  primary types, six distinct Johto/Kanto offers, stable reload results and no
  forbidden species.
- Fixed Trainer-ID vectors: **PASS**, protecting the generator contract.
- Elm, Oak and all 21 Silver trainer variants: **PASS - source and built-byte
  integration verified**.
- Final ARM9/overlay hooks, Oak script/message payloads and every generated
  starter cry index in the final SDAT: **PASS**.
- Route 34 classic starter availability: **PASS - all six original starters
  remain in their documented periods**.
- Save ABI/persistent-layout contracts: **PASS - no save expansion or migration**.
- Mega Evolution, v2.3 D-pad and automatic-HM contracts: **PASS - unchanged**.
- Random-starter object code budget: **PASS - 3,438 bytes of `.text`**.
- GCC 10.3.1 incremental build: **PASS**.
- GCC 10.3.1 clean-origin build: **PASS**. The build was resumed from the same
  clean-origin artifact tree after execution-window timeouts; two transient
  high-parallelism `nitrogfx` exits were reproduced individually with the same
  inputs, completed successfully, and the remainder was built at `-j2`.
- Clean-origin and subsequent incremental ROM hashes: **identical**.
- Updated documentation PDFs rendered and visually inspected: **PASS**.
- melonDS 1.1 boot/title responsiveness smoke: **PASS - 60/60 emulator display
  rate; no uncapped-frame-rate patch enabled**.
- xdelta decode round trip: **PASS**, reproducing the final ROM SHA-256 exactly.
- 60 FPS/uncapped-frame-rate hacks: **remain disabled**, matching the v2.3
  configuration.

## Runtime validation boundary

No disposable `.sav` or `.dsv` fixture was available. The final ROM was opened
to the title screen in melonDS without loading or modifying a personal save.
Interactive confirmation of the Elm and Oak selection scenes, all seven Silver
battles, and historical-save edge cases therefore remains fixture-dependent and
is not reported as completed playable validation. Their data paths, scripts,
compiled bytes and deterministic contracts are covered by the automated suite.

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.4.xdelta HeartGold-Generations-v2.4.nds
```

The source must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify the final ROM SHA-256. Do not force the patch onto a
different ROM revision.
