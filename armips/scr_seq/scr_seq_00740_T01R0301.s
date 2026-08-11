.nds

.include "armips/include/scriptmacros.s"
.include "armips/include/vars.s"

.open "build/a012/2_740", 0

// Replace only the fixed Bulbasaur/Squirtle/Charmander display tails. Each
// six-byte goto occupies the original scrcmd_452 command exactly.
.org 0x066D
goto v24_oak_ball_0

.org 0x071B
goto v24_oak_ball_1

.org 0x07C9
goto v24_oak_ball_2

// The vanilla common routine used the species itself as a ball-position key.
// Keep the generated species in x8004 and the physical ball in x8006.
.org 0x0816
.halfword VAR_SPECIAL_x8006
.org 0x0831
.halfword VAR_SPECIAL_x8006
.org 0x08BA
.halfword VAR_SPECIAL_x8006
.org 0x08D5
.halfword VAR_SPECIAL_x8006

.org 0x1158

v24_oak_ball_0:
    setvar VAR_SPECIAL_x8004, 0
    RunNewCommand NEW_COMMAND_GET_KANTO_STARTER, VAR_SPECIAL_x8004
    scrcmd_452 VAR_SPECIAL_x8004, 0
    PlayCry VAR_SPECIAL_x8004, 0
    buffer_species_name 0, VAR_SPECIAL_x8004, 0, 0
    npc_msg 45
    WaitCry
    touchscreen_menu_hide
    getmenuchoice VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq 0x096C
    setvar VAR_SPECIAL_x8006, 3
    GetPartyCount VAR_SPECIAL_x8007
    call 0x0801
    RunNewCommand NEW_COMMAND_FINALIZE_KANTO_STARTER, VAR_SPECIAL_x8004
    end

v24_oak_ball_1:
    setvar VAR_SPECIAL_x8004, 1
    RunNewCommand NEW_COMMAND_GET_KANTO_STARTER, VAR_SPECIAL_x8004
    scrcmd_452 VAR_SPECIAL_x8004, 0
    PlayCry VAR_SPECIAL_x8004, 0
    buffer_species_name 0, VAR_SPECIAL_x8004, 0, 0
    npc_msg 44
    WaitCry
    touchscreen_menu_hide
    getmenuchoice VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq 0x096C
    setvar VAR_SPECIAL_x8006, 4
    GetPartyCount VAR_SPECIAL_x8007
    call 0x0801
    RunNewCommand NEW_COMMAND_FINALIZE_KANTO_STARTER, VAR_SPECIAL_x8004
    end

v24_oak_ball_2:
    setvar VAR_SPECIAL_x8004, 2
    RunNewCommand NEW_COMMAND_GET_KANTO_STARTER, VAR_SPECIAL_x8004
    scrcmd_452 VAR_SPECIAL_x8004, 0
    PlayCry VAR_SPECIAL_x8004, 0
    buffer_species_name 0, VAR_SPECIAL_x8004, 0, 0
    npc_msg 43
    WaitCry
    touchscreen_menu_hide
    getmenuchoice VAR_SPECIAL_RESULT
    compare VAR_SPECIAL_RESULT, 1
    goto_if_eq 0x096C
    setvar VAR_SPECIAL_x8006, 5
    GetPartyCount VAR_SPECIAL_x8007
    call 0x0801
    RunNewCommand NEW_COMMAND_FINALIZE_KANTO_STARTER, VAR_SPECIAL_x8004
    end

.close
