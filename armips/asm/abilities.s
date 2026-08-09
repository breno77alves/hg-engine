.nds
.thumb

// Store 9-bit ability IDs in personal data, BoxPokemon, BattlePokemon, and UI.

.open "base/arm9.bin", 0x2000000

// Personal NARC ability fields are now u16 at 0x16 and 0x1A.
.org 0x0206FB80
ldrh r5, [r4, #0x16]

.org 0x0206FB84
ldrh r5, [r4, #0x1A]

// SummaryPokemonData reuses the old u16 form field for ability and the old
// u8 ability field for form.
.org 0x02089A2A
add r1, #0x4e
strh r0, [r1]

.org 0x02089B30
add r1, #0x32
strb r0, [r1]

.org 0x0208D376
ldrh r2, [r4, r2]

.org 0x0208D3C4
ldrh r1, [r4, r1]

.org 0x0208D464
.word 0x27E

// GiveMon's script parameter must retain all 16 bits.
.org 0x0204D132
lsl r0, #0x10
lsr r0, #0x10

.org 0x02054248
ldrh r0, [r0, #0x14]

.close


.open "base/overlay/overlay_0012.bin", 0x022378C0

// Move BattlePokemon.ability from the old u8 at 0x27 to the unused u16 at
// 0x7A, retaining the total structure size and surrounding BattleStruct ABI.
.equ BASE_BATTLEMON_OFFSET, 0x2D40
.equ NEW_ABILITY_OFFSET, 0x7a
.equ ABILITY_OFFSET_WITHIN_BATTLESTRUCT, (BASE_BATTLEMON_OFFSET + NEW_ABILITY_OFFSET)

// WS_ABICNT_CALC / statbuffchange.
.org 0x0223F0E8
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

.org 0x0223F374
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// btl_scr_cmd_87_tryknockoff.
.org 0x02242FC8
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// btl_scr_cmd_d1_trynaturalcure.
.org 0x02245148
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// MessageParamTokuseiGet and AI ability storage.
.org 0x022481BC
ldrh r4, [r2, r0]

.org 0x022481CC
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

.org 0x02248648
add r1, r1
add r1, r0, r1
mov r0, #0x3e
lsl r0, #4
strh r2, [r1, r0]
bx lr

// ST_PokemonParamGet / BattleSystem_GetBattleMon.
.org 0x0224E780
strh r0, [r3, r2]
sub r2, #(ABILITY_OFFSET_WITHIN_BATTLESTRUCT-0x2DB8)
sub r1, #(ABILITY_OFFSET_WITHIN_BATTLESTRUCT-0x2DAC)

.org 0x0224E7A0
strh r0, [r2, r1]

.org 0x0224E914
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// GetBattlerVar must load the expanded u16 field rather than the old byte.
.org 0x0224EF36
add r4, #NEW_ABILITY_OFFSET
ldrh r0, [r4]

// SetBattlerVar.
.org 0x0224F320
ldrh r0, [r3]
add r2, #NEW_ABILITY_OFFSET
strh r0, [r2]

// ST_ServerTokuseiGet / GetBattlerAbility.
.org 0x02252830
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// BattleFormChangeCheck.
.org 0x02256F24
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// Forecast/Trace/Multitype checks.
.org 0x022585CC
ldrh r3, [r6, r2]

.org 0x022585DA
sub r2, #(ABILITY_OFFSET_WITHIN_BATTLESTRUCT-0x2D8C)

.org 0x022585EA
sub r2, #(ABILITY_OFFSET_WITHIN_BATTLESTRUCT-0x2D8C)

.org 0x022585F4
ldrh r2, [r6, r2]

.org 0x02258636
ldrh r1, [r2, r0]

.org 0x02258640
sub r0, #(ABILITY_OFFSET_WITHIN_BATTLESTRUCT-0x2D8C)

.org 0x02258654
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

// BattleControl_EmitPartyStatusHeal.
.org 0x02263CFC
ldrh r1, [r3, r1]

.org 0x02263D10
.word ABILITY_OFFSET_WITHIN_BATTLESTRUCT

.close
