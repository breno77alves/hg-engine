# HeartGold Generations v2.3 release manifest

## Source identity

| Item | Value |
| --- | --- |
| Fork | `https://github.com/breno77alves/hg-engine` |
| Branch | `HeartGold-Generations-v2.3` |
| Tag | `v2.3` |
| Parent release | annotated tag `v2.2.1` / `fcf138a31` |
| Baseline/tests | `953ee8132` |
| Battle D-pad | `eb8efe9e2` |
| Automatic HM core | `a935258d0` |
| Contextual HM architecture | `88eccadb9` |
| Automatic Fly bag flow | `c2a79e169` |
| Final source | annotated tag `v2.3` (tag target is authoritative) |

## Build identity

| Artifact | Size | SHA-256 | MD5 |
| --- | ---: | --- | --- |
| Required clean base `rom.nds` | `134217728` | `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D` | `AE2A483D0A5E8130D39F44F41A86DF57` |
| Local final ROM `HeartGold-Generations-v2.3.nds` | `181333472` | `FFE183818DCD5995CFF7EA4DF2383F9763071228CBF9DE627998FB9AE7B1C6F8` | `1A7A0D7FB4D496A151B89F492D887C6C` |
| `HeartGold-Generations-v2.3.xdelta` | `26632787` | `E4648AA628CF2398AD96BA33F6AC9B4E1B458331A57A35DEA26A53D4588AD3EA` | `D742FC867F85B26F9FAEE1B3E0B7809A` |

The commercial base and complete patched ROM are local-only and are not
committed or uploaded. Distribute only the patch, source, changelog, and
documentation.

## Release acceptance

- Repository regression scripts: **PASS - 45/45**.
- Incremental and clean-origin GCC 10.3 builds: **PASS**.
- v2.3 compiler warnings: **zero**; catalogued legacy asset warnings remain.
- `RUN + Up` final bytes: **PASS - `23 D1 -> C0 46`**.
- Mega/JIT literal at `0x02269F4C`: **PASS - `D4 02 3D 02`, byte-identical to v2.2.1**.
- Eight-entry HM/item/badge contract and non-HM vanilla fallback: **PASS**.
- Seven contextual HMs preserve original scripts and field paths: **PASS**.
- HM02 `FLY / TEACH / CANCEL` source/build integration: **PASS**.
- Save ABI/persistent-layout contracts: **PASS - no new persistent state**.
- Features/QoL PDF render: **PASS**.
- melonDS boot/responsiveness smoke: **PASS - hg-engine splash and overworld**.
- xdelta decode round trip: **PASS**, reproducing the final ROM SHA-256 exactly.
- 60 FPS/uncapped-frame-rate hacks: **remain disabled**.

## Runtime validation boundary

No disposable `.sav` or `.dsv` fixtures were present. The detected personal
save was used only to observe boot to the overworld and was not modified. Ten
consecutive battles, Mega touch/D-pad input, the eight positive/negative HM
flows, Fly destination restrictions, and historical-save loading are therefore
fixture-dependent and are not reported as completed playable tests.

## Patch application

Use xdelta 3.2.0 or another compatible xdelta3 implementation:

```text
xdelta3 -d -s clean-base.nds HeartGold-Generations-v2.3.xdelta HeartGold-Generations-v2.3.nds
```

The source must be exactly 134,217,728 bytes and match the base SHA-256 above.
After patching, verify the final ROM SHA-256. Do not force the patch onto a
different ROM revision.
