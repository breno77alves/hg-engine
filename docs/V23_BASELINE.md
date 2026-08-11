# HeartGold Generations v2.3 baseline

## Source

- branch point: `v2.2.1` / `fcf138a31ebd1aa2f5405d97892914f2f3ce9c63`
- clean US HeartGold input ROM SHA-256:
  `2767E2CB80ACC206074232C10A3B74A479E45A472F2EF9F84BBFC55E36AD962D`
- reviewed v2.2.1 build SHA-256:
  `47273F5A085F8692ADBE26FBC77E54ADD0CFBECF7A6D3409D461576568D336A4`

No `.sav` or `.dsv` fixtures were present in the workspace at branch creation.
Playable cases that require campaign state remain explicitly tracked in the v2.3
test plan; automated source and binary contracts must not claim those cases ran.

## Preserved invariants

- save layout remains byte-compatible with v2.0 through v2.2.1;
- the 60 FPS patches remain disabled;
- overlay 12's D-pad literal at `0x02269F4C` is never modified at runtime;
- non-HM field moves retain their learned-move requirement.
