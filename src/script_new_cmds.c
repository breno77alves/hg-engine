#include "../include/types.h"
#include "../include/script.h"
#include "../include/repel.h"
#include "../include/automatic_hm_fly.h"
#include "../include/random_starters.h"
#include "../include/config.h"
#include "../include/pokemon.h"
#include "../include/save.h"
#include "../include/constants/species.h"
#include "../include/constants/file.h"

#define SCRIPT_NEW_CMD_REPEL_USE    0
#define KANTO_PARTY_COUNT_VAR       0x8007

BOOL Script_RunNewCmd(SCRIPTCONTEXT *ctx) {
    u8 sw = ScriptReadByte(ctx);
    u16 arg0 = ScriptReadHalfword(ctx);

    switch (sw) {
        case SCRIPT_NEW_CMD_REPEL_USE:;
#ifdef IMPLEMENT_REUSABLE_REPELS
            u16 most_recent_repel = Repel_GetMostRecent();
            SetScriptVar(arg0, most_recent_repel);
            Repel_Use(most_recent_repel, HEAPID_MAIN_HEAP);
#endif
            break;

        case SCRIPT_NEW_CMD_AUTOMATIC_HM_CHECK_FLY:
            SetScriptVar(arg0, AutomaticHmFly_Check());
            break;

        case SCRIPT_NEW_CMD_AUTOMATIC_HM_FLY:
            AutomaticHmFly_SetChoice(2);
            break;

        case SCRIPT_NEW_CMD_AUTOMATIC_HM_TEACH:
            AutomaticHmFly_SetChoice(3);
            break;

        case SCRIPT_NEW_CMD_AUTOMATIC_HM_CANCEL:
            AutomaticHmFly_SetChoice(4);
            break;

        case SCRIPT_NEW_CMD_GET_KANTO_STARTER: {
            u16 *slotAndSpecies = GetVarPointer(ctx->fsys, arg0);
            StarterChoices excluded;
            StarterChoices kanto;
            struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(ctx->fsys->savedata);

            if (CheckScriptFlagPassSave(SavArray_Flags_get(ctx->fsys->savedata), RANDOMIZED_STARTERS_FLAG)) {
                GenerateStarterChoices(profile->id, STARTER_REGION_JOHTO, NULL, &excluded);
            } else {
                excluded.species[0] = SPECIES_BULBASAUR;
                excluded.species[1] = SPECIES_CHARMANDER;
                excluded.species[2] = SPECIES_SQUIRTLE;
            }
            GenerateStarterChoices(profile->id, STARTER_REGION_KANTO, &excluded, &kanto);
            *slotAndSpecies = GetStarterChoice(&kanto, (u8)*slotAndSpecies);
            break;
        }

        case SCRIPT_NEW_CMD_FINALIZE_KANTO_STARTER: {
            u16 species = *GetVarPointer(ctx->fsys, arg0);
            u16 previousPartyCount = *GetVarPointer(ctx->fsys, KANTO_PARTY_COUNT_VAR);
            struct Party *party = SaveData_GetPlayerPartyPtr(ctx->fsys->savedata);
            if (party->count != previousPartyCount + 1) {
                break;
            }
            if (party->count != 0) {
                struct PartyPokemon *mon = Party_GetMonByIndex(party, party->count - 1);
                if (GetMonData(mon, MON_DATA_SPECIES, NULL) == species) {
                    EnsureStarterHasOffensiveMove(mon);
                    if (CheckScriptFlagPassSave(SavArray_Flags_get(ctx->fsys->savedata), HIDDEN_ABILITIES_STARTERS_FLAG)) {
                        SET_MON_HIDDEN_ABILITY_BIT(mon)
                        ResetPartyPokemonAbility(mon);
                    }
                }
            }
            break;
        }

        default: break;
    }

    return FALSE;
}
