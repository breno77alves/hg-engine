# HeartGold Generations v2.4

## Random starters per save

- Elm and Oak now offer deterministic random trios derived from the full
  32-bit Trainer ID. Reloading a save does not reroll either trio.
- Each trio contains three different species with three different primary
  types. Oak excludes all three Johto choices, so the six offers are unique.
- The audited pool contains only canonical first-stage Pokemon that evolve and
  have valid battle sprite, icon, cry and follower resources.
- Legendary, mythical, sublegendary, Ultra Beast, Paradox, regional and other
  alternative forms are excluded.
- Every pool member has a deterministic safe damaging move fallback for level
  5 gifts that would otherwise have no usable attack.

## Silver and Oak

- Silver selects the unchosen candidate with the best STAB effectiveness
  against the player's starter, with deterministic circular tie-breaking.
- His starter family advances at levels 16 and 36; branched evolutions use a
  stable Trainer-ID-derived path. Only the 21 variants of the seven original
  Silver battles are changed, and pre-v2.4 saves retain their old teams.
- Oak's three balls now use dynamic species, sprite, cry, name and confirmation
  while preserving ball removal, nickname and party-space behavior.
- Older saves that have not taken Oak's gift receive a random Kanto trio without
  changing their original Johto starter or Silver teams.

## Availability and compatibility

- Bulbasaur and Chikorita remain on Route 34 in the morning; Squirtle and
  Totodile during the day; Charmander and Cyndaquil at night.
- No save structure or size changed. One existing flag records that the new
  Elm flow was reached.
- Mega Evolution, v2.3 battle D-pad behavior, automatic HMs and the disabled
  60 FPS/uncapped-frame-rate configuration are unchanged.
