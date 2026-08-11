#ifndef AUTOMATIC_HM_H
#define AUTOMATIC_HM_H

#include "types.h"

typedef struct SCRIPTCONTEXT SCRIPTCONTEXT;
struct Party;

enum AutomaticHmBadge {
    BADGE_ZEPHYR = 0,
    BADGE_HIVE = 1,
    BADGE_PLAIN = 2,
    BADGE_FOG = 3,
    BADGE_STORM = 4,
    BADGE_GLACIER = 6,
    BADGE_RISING = 7,
    BADGE_EARTH = 15,
};

struct AutomaticHmRule {
    u16 move;
    u16 item;
    u8 badge;
};

const struct AutomaticHmRule *IsAutomaticHm(u16 move);
BOOL HasAutomaticHmAccess(void *saveData, u16 move);
u16 SelectAutomaticHmActor(struct Party *party);
BOOL ScrCmd_CheckMoveInParty_AutomaticHm(SCRIPTCONTEXT *ctx);

#endif // AUTOMATIC_HM_H
