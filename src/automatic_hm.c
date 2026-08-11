#include "../include/automatic_hm.h"

#include "../include/bag.h"
#include "../include/pokemon.h"
#include "../include/save.h"
#include "../include/script.h"
#include "../include/constants/item.h"
#include "../include/constants/moves.h"

#define AUTOMATIC_HM_RULE_COUNT 8
#define PARTY_SLOT_NONE 6
#define HEAP_ID_FIELD 11

static const struct AutomaticHmRule sAutomaticHmRules[AUTOMATIC_HM_RULE_COUNT] = {
    { MOVE_CUT, ITEM_HM01, BADGE_HIVE },
    { MOVE_FLY, ITEM_HM02, BADGE_STORM },
    { MOVE_SURF, ITEM_HM03, BADGE_FOG },
    { MOVE_STRENGTH, ITEM_HM04, BADGE_PLAIN },
    { MOVE_WHIRLPOOL, ITEM_HM05, BADGE_GLACIER },
    { MOVE_ROCK_SMASH, ITEM_HM06, BADGE_ZEPHYR },
    { MOVE_WATERFALL, ITEM_HM07, BADGE_RISING },
    { MOVE_ROCK_CLIMB, ITEM_HM08, BADGE_EARTH },
};

static BOOL PlayerProfile_TestBadgeFlag(const struct PlayerProfile *profile, u8 badge)
{
    if (badge < 8) {
        return (profile->johtoBadges & (1 << badge)) != 0;
    }

    return (profile->kantoBadges & (1 << (badge - 8))) != 0;
}

const struct AutomaticHmRule *IsAutomaticHm(u16 move)
{
    u32 i;

    for (i = 0; i < AUTOMATIC_HM_RULE_COUNT; i++) {
        if (sAutomaticHmRules[i].move == move) {
            return &sAutomaticHmRules[i];
        }
    }

    return NULL;
}

BOOL HasAutomaticHmAccess(void *saveData, u16 move)
{
    const struct AutomaticHmRule *rule = IsAutomaticHm(move);
    struct PlayerProfile *profile;

    if (rule == NULL) {
        return FALSE;
    }

    if (!Bag_HasItem(Sav2_Bag_get(saveData), rule->item, 1, HEAP_ID_FIELD)) {
        return FALSE;
    }

    profile = Sav2_PlayerData_GetProfileAddr(saveData);
    return PlayerProfile_TestBadgeFlag(profile, rule->badge);
}

u16 SelectAutomaticHmActor(struct Party *party)
{
    u16 i;

    for (i = 0; i < party->count; i++) {
        struct PartyPokemon *mon = Party_GetMonByIndex(party, i);

        if (!GetMonData(mon, MON_DATA_IS_EGG, NULL)) {
            return i;
        }
    }

    return PARTY_SLOT_NONE;
}

static u16 SelectVanillaMoveUser(struct Party *party, u16 move)
{
    u16 i;

    for (i = 0; i < party->count; i++) {
        struct PartyPokemon *mon = Party_GetMonByIndex(party, i);

        if (GetMonData(mon, MON_DATA_IS_EGG, NULL)) {
            continue;
        }

        if (MonHasMove(mon, move)) {
            return i;
        }
    }

    return PARTY_SLOT_NONE;
}

BOOL ScrCmd_CheckMoveInParty_AutomaticHm(SCRIPTCONTEXT *ctx)
{
    struct Party *party = SaveData_GetPlayerPartyPtr(ctx->fsys->savedata);
    u16 *slot = ScriptGetVarPointer(ctx);
    u16 move = ScriptGetVar(ctx);

    *slot = PARTY_SLOT_NONE;

    if (IsAutomaticHm(move) != NULL) {
        if (HasAutomaticHmAccess(ctx->fsys->savedata, move)) {
            *slot = SelectAutomaticHmActor(party);
        }
    } else {
        *slot = SelectVanillaMoveUser(party, move);
    }

    return FALSE;
}
