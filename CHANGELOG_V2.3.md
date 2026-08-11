# HeartGold Generations v2.3

## Battle menu

- Pressing Up while `RUN` is focused now selects `FIGHT` without confirming it.
- The patch is isolated to the main command menu in overlay 12.
- The shared move-submenu literal at `0x02269F4C`, Mega input tables, and JIT
  behavior are unchanged.

## Automatic HMs

- Cut, Fly, Surf, Strength, Whirlpool, Rock Smash, Waterfall, and Rock Climb
  can be used in the field without being taught.
- Automatic use still requires the corresponding HM, badge, and a non-Egg
  party member. The first non-Egg Pokemon is the visual actor, even if fainted
  or incompatible with the move.
- The seven contextual HMs retain their original obstacle, map, story, and
  state checks.
- HM02 in the Bag now offers `FLY / TEACH / CANCEL`. Fly delegates restrictions
  and destination handling to the original engine; Teach retains the original
  teaching flow.
- HMs remain teachable for battle. Non-HM field moves are unchanged.

## Compatibility

- No new save fields, flags, or migration.
- Save layouts remain compatible with v2.0 through v2.2.1.
- The 60 FPS and uncapped-frame-rate hacks remain disabled.
- v2.2.1 encounters, availability, forms, abilities, sprites, and balance are
  unchanged.
