# v2.3 automatic HM architecture

## Rules

Automatic field use requires all three conditions:

1. the matching HM is present in the Bag;
2. the matching badge is owned;
3. the party contains at least one non-Egg Pokemon.

The first non-Egg party member is used only as the visual actor. It may be
fainted and does not need to be compatible with, or know, the move.

| HM | Move | Badge |
|---|---|---|
| HM01 | Cut | Hive |
| HM02 | Fly | Storm |
| HM03 | Surf | Fog |
| HM04 | Strength | Plain |
| HM05 | Whirlpool | Glacier |
| HM06 | Rock Smash | Zephyr |
| HM07 | Waterfall | Rising |
| HM08 | Rock Climb | Earth |

## Contextual integration

The seven contextual HMs continue through the original field scripts. The
v2.3 hook changes only command 141 (`CheckMoveInParty`): for an HM, it applies
the central automatic-access gate and returns the visual actor. For every
other move it reproduces the original learned-move search and Egg exclusion.

This preserves the original obstacle interaction, map and story restrictions,
Surf/Strength state transitions, animation setup, and field-move execution.
Flash, Dig, Teleport, Headbutt, Sweet Scent, and other non-HM field moves are
not intercepted.

Fly is handled separately from HM02 in the Bag and delegates both restriction
checks and execution to the original Fly field-move functions.

## Save and battle compatibility

The implementation stores no persistent state and adds no save fields or
flags. HMs remain teachable for battle use. The battle D-pad patch is isolated
in overlay 12 and does not change the Mega/JIT literal at `0x02269F4C`.
