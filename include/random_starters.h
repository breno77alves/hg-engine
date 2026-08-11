#ifndef RANDOM_STARTERS_H
#define RANDOM_STARTERS_H

#include "types.h"

struct PartyPokemon;
struct FieldSystem;

typedef enum StarterRegion {
    STARTER_REGION_JOHTO,
    STARTER_REGION_KANTO,
} StarterRegion;

typedef struct StarterChoices {
    u16 species[3];
} StarterChoices;

enum {
    SCRIPT_NEW_CMD_GET_KANTO_STARTER = 5,
    SCRIPT_NEW_CMD_FINALIZE_KANTO_STARTER = 6,
};

void GenerateStarterChoices(u32 trainerId, StarterRegion region, const StarterChoices *excluded, StarterChoices *out);
u16 GetStarterChoice(const StarterChoices *choices, u8 position);
u16 DetermineRivalStarter(const StarterChoices *choices, u16 playerSpecies);
u16 GetStarterEvolutionForLevel(u16 baseSpecies, u8 level, u32 trainerId);
BOOL EnsureStarterHasOffensiveMove(struct PartyPokemon *mon);
BOOL EnsureStarterHasOffensiveMoveFromBase(struct PartyPokemon *mon, u16 baseSpecies);
void LaunchStarterChoiceScene_Randomized(struct FieldSystem *fieldSystem);
u8 ChooseStarter_PrintMsgOnWinEx(void *window, u32 heapId, BOOL makeFrame, s32 msgBank, int msgNo, u32 color, u32 speed, void **out);

#endif
