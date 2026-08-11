.nds
.thumb

.open "base/overlay/overlay_0012.bin", 0x022378C0

// BattleInput_CursorMove_MainMenu special-cases RUN + Up by branching over
// BattleCursor_CheckKeyInput. Let the normal 3x2 command grid handle Up so
// the central RUN cell reaches the central FIGHT cell above it.
.org 0x02269B5C
nop

.close
