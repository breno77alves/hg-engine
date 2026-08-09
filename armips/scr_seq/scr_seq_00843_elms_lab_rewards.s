.nds

.include "armips/include/scriptmacros.s"
.include "armips/include/vars.s"
.include "asm/include/items.inc"

// Elm's aide originally gives five Potions here. Replace that inherited ROM
// block with the two Generations QoL key items unconditionally, so save/reload
// order cannot select the inherited Potion reward.
.open "build/a012/2_843", 0

.org 0x6DD
giveitem_no_check ITEM_INFINITE_CANDY, 1
giveitem_no_check ITEM_INFINITE_REJUVINATOR, 1
goto 0x70E

.close
