#include "../include/automatic_hm_fly.h"

#include "../include/automatic_hm.h"
#include "../include/pokemon.h"
#include "../include/script.h"
#include "../include/constants/item.h"
#include "../include/constants/moves.h"

#define AUTOMATIC_HM_FLY_SCRIPT 2073
#define PARTY_SLOT_NONE 6

enum AutomaticHmFlyChoice {
    AUTOMATIC_HM_FLY_CHOICE_INIT = 0,
    AUTOMATIC_HM_FLY_CHOICE_WAITING,
    AUTOMATIC_HM_FLY_CHOICE_FLY,
    AUTOMATIC_HM_FLY_CHOICE_TEACH,
    AUTOMATIC_HM_FLY_CHOICE_CANCEL,
};

struct AutomaticHmFlyPending {
    TaskManager *taskManager;
    struct ItemMenuUseData itemUseData;
    struct ItemCheckUseData itemCheckData;
    FieldMoveCheckData *fieldMoveCheckData;
    u8 choice;
};

static struct AutomaticHmFlyPending sAutomaticHmFlyPending;

static void AutomaticHmFly_ClearPending(void)
{
    sAutomaticHmFlyPending.taskManager = NULL;
    sAutomaticHmFlyPending.fieldMoveCheckData = NULL;
    sAutomaticHmFlyPending.choice = AUTOMATIC_HM_FLY_CHOICE_INIT;
}

u16 AutomaticHmFly_Check(void)
{
    FieldMoveCheckFunc check;
    u32 response;
    FieldSystem *fieldSystem;
    struct Party *party;

    if (sAutomaticHmFlyPending.taskManager == NULL ||
        sAutomaticHmFlyPending.fieldMoveCheckData == NULL) {
        return FIELD_MOVE_RESPONSE_NOT_HERE;
    }

    fieldSystem = sAutomaticHmFlyPending.taskManager->fieldSystem;
    check = (FieldMoveCheckFunc)FieldMove_GetMoveFunc(FIELD_MOVE_FUNC_CHECK, FIELD_MOVE_FLY);
    if (check == NULL) {
        return FIELD_MOVE_RESPONSE_NOT_HERE;
    }

    response = check(sAutomaticHmFlyPending.fieldMoveCheckData);
    if (response != FIELD_MOVE_RESPONSE_OK) {
        return (u16)response;
    }

    if (!HasAutomaticHmAccess(fieldSystem->savedata, MOVE_FLY)) {
        return FIELD_MOVE_RESPONSE_NEED_BADGE;
    }

    party = SaveData_GetPlayerPartyPtr(fieldSystem->savedata);
    if (SelectAutomaticHmActor(party) == PARTY_SLOT_NONE) {
        return FIELD_MOVE_RESPONSE_NO_ACTOR;
    }

    return FIELD_MOVE_RESPONSE_OK;
}

void AutomaticHmFly_SetChoice(u8 choice)
{
    if (sAutomaticHmFlyPending.taskManager == NULL) {
        return;
    }

    if (choice >= AUTOMATIC_HM_FLY_CHOICE_FLY &&
        choice <= AUTOMATIC_HM_FLY_CHOICE_CANCEL) {
        sAutomaticHmFlyPending.choice = choice;
    }
}

static BOOL Task_AutomaticHmFlyPrompt(TaskManager *taskManager)
{
    struct BagViewAppWork *startMenu = taskManager->env;
    struct ItemMenuUseData itemUseData;
    struct ItemCheckUseData itemCheckData;
    FieldMoveCheckData *fieldMoveCheckData;
    FieldMoveUseData useData;
    FieldMoveUseFunc use;
    struct Party *party;
    u16 actor;
    u8 choice;

    if (taskManager != sAutomaticHmFlyPending.taskManager) {
        return FALSE;
    }

    choice = sAutomaticHmFlyPending.choice;
    if (choice == AUTOMATIC_HM_FLY_CHOICE_INIT) {
        sAutomaticHmFlyPending.choice = AUTOMATIC_HM_FLY_CHOICE_WAITING;
        QueueScript(taskManager, AUTOMATIC_HM_FLY_SCRIPT, NULL, NULL);
        return FALSE;
    }

    if (choice == AUTOMATIC_HM_FLY_CHOICE_WAITING) {
        return FALSE;
    }

    itemUseData = sAutomaticHmFlyPending.itemUseData;
    itemCheckData = sAutomaticHmFlyPending.itemCheckData;
    fieldMoveCheckData = sAutomaticHmFlyPending.fieldMoveCheckData;

    if (choice == AUTOMATIC_HM_FLY_CHOICE_TEACH) {
        AutomaticHmFly_ClearPending();
        ItemMenuUseFunc_TMHM(&itemUseData, &itemCheckData);
        return FALSE;
    }

    if (choice == AUTOMATIC_HM_FLY_CHOICE_FLY &&
        AutomaticHmFly_Check() == FIELD_MOVE_RESPONSE_OK) {
        party = SaveData_GetPlayerPartyPtr(taskManager->fieldSystem->savedata);
        actor = SelectAutomaticHmActor(party);
        use = (FieldMoveUseFunc)FieldMove_GetMoveFunc(FIELD_MOVE_FUNC_USE, FIELD_MOVE_FLY);
        if (actor != PARTY_SLOT_NONE && use != NULL) {
            useData.taskManager = taskManager;
            useData.partySlot = actor;
            useData.fieldMoveIdx = FIELD_MOVE_FLY;
            AutomaticHmFly_ClearPending();
            use(&useData, fieldMoveCheckData);
            return FALSE;
        }
    }

    AutomaticHmFly_ClearPending();
    sub_0203C8F0(startMenu, (u32)Task_StartMenu_ReopenBag);
    return FALSE;
}

void ItemMenuUseFunc_AutomaticHmTmHm(struct ItemMenuUseData *data, const struct ItemCheckUseData *checkData)
{
    struct BagViewAppWork *startMenu;

    if (data->itemId != ITEM_HM02) {
        ItemMenuUseFunc_TMHM(data, checkData);
        return;
    }

    startMenu = data->taskManager->env;
    sAutomaticHmFlyPending.taskManager = data->taskManager;
    sAutomaticHmFlyPending.itemUseData = *data;
    sAutomaticHmFlyPending.itemCheckData = *checkData;
    sAutomaticHmFlyPending.fieldMoveCheckData = (FieldMoveCheckData *)startMenu->unk_0370;
    sAutomaticHmFlyPending.choice = AUTOMATIC_HM_FLY_CHOICE_INIT;
    sub_0203C8F0(startMenu, (u32)Task_AutomaticHmFlyPrompt);
}
