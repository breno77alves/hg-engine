#include "../include/types.h"
#include "../include/script.h"
#include "../include/repel.h"
#include "../include/automatic_hm_fly.h"
#include "../include/constants/file.h"

#define SCRIPT_NEW_CMD_REPEL_USE    0

BOOL Script_RunNewCmd(SCRIPTCONTEXT *ctx) {
    u8 sw = ScriptReadByte(ctx);
    u16 UNUSED arg0 = ScriptReadHalfword(ctx);

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

        default: break;
    }

    return FALSE;
}
