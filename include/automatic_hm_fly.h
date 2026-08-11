#ifndef AUTOMATIC_HM_FLY_H
#define AUTOMATIC_HM_FLY_H

#include "item.h"

enum AutomaticHmFlyScriptCommand {
    SCRIPT_NEW_CMD_AUTOMATIC_HM_CHECK_FLY = 1,
    SCRIPT_NEW_CMD_AUTOMATIC_HM_FLY = 2,
    SCRIPT_NEW_CMD_AUTOMATIC_HM_TEACH = 3,
    SCRIPT_NEW_CMD_AUTOMATIC_HM_CANCEL = 4,
};

enum FieldMoveFunctionType {
    FIELD_MOVE_FUNC_USE = 0,
    FIELD_MOVE_FUNC_CHECK = 1,
};

enum FieldMoveIndex {
    FIELD_MOVE_CUT = 0,
    FIELD_MOVE_FLY = 1,
};

enum FieldMoveResponse {
    FIELD_MOVE_RESPONSE_OK = 0,
    FIELD_MOVE_RESPONSE_NOT_HERE = 1,
    FIELD_MOVE_RESPONSE_NEED_BADGE = 2,
    FIELD_MOVE_RESPONSE_HAVE_FOLLOWER = 3,
    FIELD_MOVE_RESPONSE_ALREADY_SURFING = 4,
    FIELD_MOVE_RESPONSE_NOT_NOW = 5,
    FIELD_MOVE_RESPONSE_NO_ACTOR = 6,
};

typedef struct FieldMoveUseData {
    TaskManager *taskManager;
    u16 partySlot;
    u16 fieldMoveIdx;
} FieldMoveUseData;

typedef struct FieldMoveCheckData {
    u32 mapId;
    FieldSystem *fieldSystem;
    void *facingObject;
    u16 flag;
} FieldMoveCheckData;

typedef void (*FieldMoveUseFunc)(FieldMoveUseData *useData, const FieldMoveCheckData *checkData);
typedef u32 (*FieldMoveCheckFunc)(const FieldMoveCheckData *checkData);

void ItemMenuUseFunc_AutomaticHmTmHm(struct ItemMenuUseData *data, const struct ItemCheckUseData *checkData);
u16 AutomaticHmFly_Check(void);
void AutomaticHmFly_SetChoice(u8 choice);

void *LONG_CALL FieldMove_GetMoveFunc(u32 funcType, u16 fieldMoveIndex);
BOOL LONG_CALL Task_StartMenu_ReopenBag(TaskManager *taskManager);
void LONG_CALL QueueScript(TaskManager *taskManager, u16 script, void *lastInteracted, void *environment);

#endif // AUTOMATIC_HM_FLY_H
