#include "../include/random_starters.h"

#include "../include/battle.h"
#include "../include/config.h"
#include "../include/msgdata.h"
#include "../include/pokemon.h"
#include "../include/save.h"
#include "../include/task.h"
#include "../include/window.h"
#include "../include/constants/moves.h"
#include "../include/constants/species.h"
#include "../include/constants/file.h"

#define JOHTO_STARTER_SALT 0x4A6F6874
#define KANTO_STARTER_SALT 0x4B616E74
#define RIVAL_STARTER_SALT 0x53696C76
#define HEAP_ID_FIELD2 11
#define DYNAMIC_STARTER_TABLE ((volatile u32 *)0x02108514)
#define STARTER_MESSAGE_BANK 190
#define STRING_EOS 0xFFFF

typedef struct StarterPoolEntry {
    u16 species;
    u16 safeMove;
} StarterPoolEntry;

typedef struct ChooseStarterTaskData {
    int state;
    void *args;
} ChooseStarterTaskData;

static const StarterPoolEntry sStarterPool[] = {
#include "../include/random_starter_pool.inc"
};

static u32 Mix32(u32 value)
{
    value ^= value >> 16;
    value *= 0x7FEB352D;
    value ^= value >> 15;
    value *= 0x846CA68B;
    value ^= value >> 16;
    return value;
}

static const StarterPoolEntry *FindStarterEntry(u16 species)
{
    u32 i;
    for (i = 0; i < NELEMS(sStarterPool); i++) {
        if (sStarterPool[i].species == species) {
            return &sStarterPool[i];
        }
    }
    return NULL;
}

static BOOL ChoicesContain(const StarterChoices *choices, u16 species)
{
    u32 i;
    if (choices == NULL) {
        return FALSE;
    }
    for (i = 0; i < NELEMS(choices->species); i++) {
        if (choices->species[i] == species) {
            return TRUE;
        }
    }
    return FALSE;
}

static BOOL TryAppendStarterChoice(const StarterPoolEntry *entry, const StarterChoices *excluded, StarterChoices *out, u32 count)
{
    u32 i;
    if (ChoicesContain(excluded, entry->species) || ChoicesContain(out, entry->species)) {
        return FALSE;
    }
    for (i = 0; i < count; i++) {
        const StarterPoolEntry *chosen = FindStarterEntry(out->species[i]);
        if (chosen != NULL
         && PokePersonalParaGet(chosen->species, PERSONAL_TYPE_1)
            == PokePersonalParaGet(entry->species, PERSONAL_TYPE_1)) {
            return FALSE;
        }
    }
    out->species[count] = entry->species;
    return TRUE;
}

void GenerateStarterChoices(u32 trainerId, StarterRegion region, const StarterChoices *excluded, StarterChoices *out)
{
    u32 salt = region == STARTER_REGION_JOHTO ? JOHTO_STARTER_SALT : KANTO_STARTER_SALT;
    u32 state = Mix32(trainerId ^ salt);
    u32 draw;
    u32 count = 0;

    out->species[0] = SPECIES_NONE;
    out->species[1] = SPECIES_NONE;
    out->species[2] = SPECIES_NONE;

    for (draw = 0; draw < NELEMS(sStarterPool) * 4 && count < 3; draw++) {
        const StarterPoolEntry *entry;

        state = Mix32(state + 0x9E3779B9 + draw);
        entry = &sStarterPool[state % NELEMS(sStarterPool)];
        if (TryAppendStarterChoice(entry, excluded, out, count)) {
            count++;
        }
    }

    if (count < 3) {
        u32 start = state % NELEMS(sStarterPool);
        for (draw = 0; draw < NELEMS(sStarterPool) && count < 3; draw++) {
            const StarterPoolEntry *entry = &sStarterPool[(start + draw) % NELEMS(sStarterPool)];
            if (TryAppendStarterChoice(entry, excluded, out, count)) {
                count++;
            }
        }
    }
}

u16 GetStarterChoice(const StarterChoices *choices, u8 position)
{
    return position < 3 ? choices->species[position] : SPECIES_NONE;
}

static u8 SingleTypeScore(u8 attack, u8 defense)
{
    switch (attack) {
    case TYPE_NORMAL:
        if (defense == TYPE_GHOST) return 0;
        if (defense == TYPE_ROCK || defense == TYPE_STEEL) return 1;
        break;
    case TYPE_FIGHTING:
        if (defense == TYPE_GHOST) return 0;
        if (defense == TYPE_NORMAL || defense == TYPE_ROCK || defense == TYPE_STEEL || defense == TYPE_ICE || defense == TYPE_DARK) return 4;
        if (defense == TYPE_FLYING || defense == TYPE_POISON || defense == TYPE_BUG || defense == TYPE_PSYCHIC || defense == TYPE_FAIRY) return 1;
        break;
    case TYPE_FLYING:
        if (defense == TYPE_FIGHTING || defense == TYPE_BUG || defense == TYPE_GRASS) return 4;
        if (defense == TYPE_ROCK || defense == TYPE_STEEL || defense == TYPE_ELECTRIC) return 1;
        break;
    case TYPE_POISON:
        if (defense == TYPE_STEEL) return 0;
        if (defense == TYPE_GRASS || defense == TYPE_FAIRY) return 4;
        if (defense == TYPE_POISON || defense == TYPE_GROUND || defense == TYPE_ROCK || defense == TYPE_GHOST) return 1;
        break;
    case TYPE_GROUND:
        if (defense == TYPE_FLYING) return 0;
        if (defense == TYPE_POISON || defense == TYPE_ROCK || defense == TYPE_STEEL || defense == TYPE_FIRE || defense == TYPE_ELECTRIC) return 4;
        if (defense == TYPE_BUG || defense == TYPE_GRASS) return 1;
        break;
    case TYPE_ROCK:
        if (defense == TYPE_FLYING || defense == TYPE_BUG || defense == TYPE_FIRE || defense == TYPE_ICE) return 4;
        if (defense == TYPE_FIGHTING || defense == TYPE_GROUND || defense == TYPE_STEEL) return 1;
        break;
    case TYPE_BUG:
        if (defense == TYPE_GRASS || defense == TYPE_PSYCHIC || defense == TYPE_DARK) return 4;
        if (defense == TYPE_FIGHTING || defense == TYPE_FLYING || defense == TYPE_POISON || defense == TYPE_GHOST || defense == TYPE_STEEL || defense == TYPE_FIRE || defense == TYPE_FAIRY) return 1;
        break;
    case TYPE_GHOST:
        if (defense == TYPE_NORMAL) return 0;
        if (defense == TYPE_GHOST || defense == TYPE_PSYCHIC) return 4;
        if (defense == TYPE_DARK) return 1;
        break;
    case TYPE_STEEL:
        if (defense == TYPE_ROCK || defense == TYPE_ICE || defense == TYPE_FAIRY) return 4;
        if (defense == TYPE_STEEL || defense == TYPE_FIRE || defense == TYPE_WATER || defense == TYPE_ELECTRIC) return 1;
        break;
    case TYPE_FIRE:
        if (defense == TYPE_BUG || defense == TYPE_STEEL || defense == TYPE_GRASS || defense == TYPE_ICE) return 4;
        if (defense == TYPE_ROCK || defense == TYPE_FIRE || defense == TYPE_WATER || defense == TYPE_DRAGON) return 1;
        break;
    case TYPE_WATER:
        if (defense == TYPE_GROUND || defense == TYPE_ROCK || defense == TYPE_FIRE) return 4;
        if (defense == TYPE_WATER || defense == TYPE_GRASS || defense == TYPE_DRAGON) return 1;
        break;
    case TYPE_GRASS:
        if (defense == TYPE_GROUND || defense == TYPE_ROCK || defense == TYPE_WATER) return 4;
        if (defense == TYPE_FLYING || defense == TYPE_POISON || defense == TYPE_BUG || defense == TYPE_STEEL || defense == TYPE_FIRE || defense == TYPE_GRASS || defense == TYPE_DRAGON) return 1;
        break;
    case TYPE_ELECTRIC:
        if (defense == TYPE_GROUND) return 0;
        if (defense == TYPE_FLYING || defense == TYPE_WATER) return 4;
        if (defense == TYPE_GRASS || defense == TYPE_ELECTRIC || defense == TYPE_DRAGON) return 1;
        break;
    case TYPE_PSYCHIC:
        if (defense == TYPE_DARK) return 0;
        if (defense == TYPE_FIGHTING || defense == TYPE_POISON) return 4;
        if (defense == TYPE_STEEL || defense == TYPE_PSYCHIC) return 1;
        break;
    case TYPE_ICE:
        if (defense == TYPE_FLYING || defense == TYPE_GROUND || defense == TYPE_GRASS || defense == TYPE_DRAGON) return 4;
        if (defense == TYPE_STEEL || defense == TYPE_FIRE || defense == TYPE_WATER || defense == TYPE_ICE) return 1;
        break;
    case TYPE_DRAGON:
        if (defense == TYPE_FAIRY) return 0;
        if (defense == TYPE_DRAGON) return 4;
        if (defense == TYPE_STEEL) return 1;
        break;
    case TYPE_DARK:
        if (defense == TYPE_GHOST || defense == TYPE_PSYCHIC) return 4;
        if (defense == TYPE_FIGHTING || defense == TYPE_DARK || defense == TYPE_FAIRY) return 1;
        break;
    case TYPE_FAIRY:
        if (defense == TYPE_FIGHTING || defense == TYPE_DRAGON || defense == TYPE_DARK) return 4;
        if (defense == TYPE_POISON || defense == TYPE_STEEL || defense == TYPE_FIRE) return 1;
        break;
    }
    return 2;
}

static u16 StabScore(const StarterPoolEntry *attacker, const StarterPoolEntry *defender)
{
    u8 attackPrimary = (u8)PokePersonalParaGet(attacker->species, PERSONAL_TYPE_1);
    u8 attackSecondary = (u8)PokePersonalParaGet(attacker->species, PERSONAL_TYPE_2);
    u8 defensePrimary = (u8)PokePersonalParaGet(defender->species, PERSONAL_TYPE_1);
    u8 defenseSecondary = (u8)PokePersonalParaGet(defender->species, PERSONAL_TYPE_2);
    u16 primary = SingleTypeScore(attackPrimary, defensePrimary);
    u16 secondary = SingleTypeScore(attackSecondary, defensePrimary);
    if (defenseSecondary != defensePrimary) {
        primary *= SingleTypeScore(attackPrimary, defenseSecondary);
        secondary *= SingleTypeScore(attackSecondary, defenseSecondary);
    }
    return primary > secondary ? primary : secondary;
}

u16 DetermineRivalStarter(const StarterChoices *choices, u16 playerSpecies)
{
    const StarterPoolEntry *player = FindStarterEntry(playerSpecies);
    u32 playerPosition;
    u32 offset;
    u16 bestSpecies = SPECIES_NONE;
    u16 bestScore = 0;

    if (player == NULL) {
        return choices->species[1];
    }
    for (playerPosition = 0; playerPosition < 3; playerPosition++) {
        if (choices->species[playerPosition] == playerSpecies) break;
    }
    if (playerPosition == 3) {
        return choices->species[1];
    }
    for (offset = 1; offset <= 2; offset++) {
        const StarterPoolEntry *candidate = FindStarterEntry(choices->species[(playerPosition + offset) % 3]);
        u16 score = candidate == NULL ? 0 : StabScore(candidate, player);
        if (bestSpecies == SPECIES_NONE || score > bestScore) {
            bestSpecies = choices->species[(playerPosition + offset) % 3];
            bestScore = score;
        }
    }
    return bestSpecies;
}

u16 GetStarterEvolutionForLevel(u16 baseSpecies, u8 level, u32 trainerId)
{
    u16 current = baseSpecies;
    u32 depth;
    if (FindStarterEntry(baseSpecies) == NULL || level < 16) {
        return baseSpecies;
    }
    for (depth = 0; depth < 8; depth++) {
        struct Evolution evolutions[MAX_EVOS_PER_POKE];
        u16 targets[MAX_EVOS_PER_POKE];
        u32 count = 0;
        u32 i;
        ArchiveDataLoad(evolutions, ARC_EVOLUTIONS, current);
        for (i = 0; i < MAX_EVOS_PER_POKE; i++) {
            u16 target = evolutions[i].target & 0x07FF;
            if (evolutions[i].method != EVO_NONE && target != SPECIES_NONE) {
                targets[count++] = target;
            }
        }
        if (count == 0) {
            break;
        }
        current = targets[Mix32(trainerId ^ RIVAL_STARTER_SALT ^ baseSpecies ^ (depth * 0x9E37)) % count];
        if (level < 36) {
            break;
        }
    }
    return current;
}

BOOL EnsureStarterHasOffensiveMoveFromBase(struct PartyPokemon *mon, u16 baseSpecies)
{
    const StarterPoolEntry *entry;
    u32 i;

    for (i = 0; i < 4; i++) {
        u16 move = (u16)GetMonData(mon, MON_DATA_MOVE1 + i, NULL);
        if (move != MOVE_NONE && GetMoveData(move, MOVE_DATA_BASE_POWER) > 0) {
            return TRUE;
        }
    }
    entry = FindStarterEntry(baseSpecies);
    if (entry == NULL || entry->safeMove == MOVE_NONE) {
        return FALSE;
    }
    SetPartyPokemonMoveAtPos(mon, entry->safeMove, 0);
    return TRUE;
}

BOOL EnsureStarterHasOffensiveMove(struct PartyPokemon *mon)
{
    u16 species = (u16)GetMonData(mon, MON_DATA_SPECIES, NULL);
    return EnsureStarterHasOffensiveMoveFromBase(mon, species);
}

extern BOOL LONG_CALL CreateStarter_Vanilla(TaskManager *taskManager);
extern void LONG_CALL TaskManager_Call(TaskManager *taskManager, TaskFunc taskFunc, void *env);

void LaunchStarterChoiceScene_Randomized(struct FieldSystem *fieldSystem)
{
    StarterChoices choices;
    ChooseStarterTaskData *env;
    struct PlayerProfile *profile = Sav2_PlayerData_GetProfileAddr(fieldSystem->savedata);
    u32 i;

    GenerateStarterChoices(profile->id, STARTER_REGION_JOHTO, NULL, &choices);
    for (i = 0; i < 3; i++) {
        DYNAMIC_STARTER_TABLE[i] = choices.species[i];
    }
    SetScriptFlagPassSave(SavArray_Flags_get(fieldSystem->savedata), RANDOMIZED_STARTERS_FLAG);

    env = sys_AllocMemoryLo(HEAP_ID_FIELD2, sizeof(*env));
    env->state = 0;
    env->args = NULL;
    TaskManager_Call((TaskManager *)fieldSystem->taskman, CreateStarter_Vanilla, env);
}

static const u16 sStarterConfirmPrefix[] = {
    0x012E, 0x0153, 0x01DE, 0x015D, 0x0153, 0x0159,
    0x01DE, 0x015B, 0x0145, 0x0152, 0x0158, 0x01DE,
}; // "Do you want "
static const u16 sStarterInspectSuffix[] = {
    0x01DE, 0x014D, 0x0157, 0x01DE, 0x0156, 0x0149, 0x0145,
    0x0150, 0x0150, 0x015D, 0x01DE, 0x0149, 0x0152, 0x0149,
    0x0156, 0x014B, 0x0149, 0x0158, 0x014D, 0x0147, 0x01AB,
}; // " is really energetic!"

static void StarterStringAppend(String *string, const u16 *source, u32 count)
{
    u32 i;
    for (i = 0; i < count && string->size + 1 < string->maxsize; i++) {
        string->data[string->size++] = source[i];
    }
    string->data[string->size] = STRING_EOS;
}

static void StarterStringAppendName(String *string, u16 species, u32 heapId)
{
    u16 name[16];
    u32 count = 0;
    GetSpeciesNameIntoArray(species, heapId, name);
    while (count < NELEMS(name) && name[count] != STRING_EOS) {
        count++;
    }
    StarterStringAppend(string, name, count);
}

static String *BuildStarterMessage(u32 heapId, int msgNo)
{
    String *string = String_New(64, heapId);
    u32 position = (msgNo - 1) % 3;
    u16 species = (u16)DYNAMIC_STARTER_TABLE[position];

    if (string == NULL) {
        return NULL;
    }
    string->size = 0;
    string->data[0] = STRING_EOS;
    if (msgNo <= 3) {
        const u16 question = 0x01AC;
        StarterStringAppend(string, sStarterConfirmPrefix, NELEMS(sStarterConfirmPrefix));
        StarterStringAppendName(string, species, heapId);
        StarterStringAppend(string, &question, 1);
    } else {
        StarterStringAppendName(string, species, heapId);
        StarterStringAppend(string, sStarterInspectSuffix, NELEMS(sStarterInspectSuffix));
    }
    return string;
}

extern String *LONG_CALL NewString_ReadMsgData(MsgData *msgData, s32 msgNo);
extern u8 LONG_CALL AddTextPrinterParameterizedWithColor(void *window, u32 fontId, String *string, u32 x, u32 y, u32 speed, u32 color, void *callback);

u8 ChooseStarter_PrintMsgOnWinEx(void *window, u32 heapId, BOOL makeFrame, s32 msgBank, int msgNo, u32 color, u32 speed, void **outRaw)
{
    String **out = (String **)outRaw;
    MsgData *msgData = NewMsgDataFromNarc(MSGDATA_LOAD_DIRECT, 27, msgBank, heapId);
    u8 printerId;

    if (msgBank == STARTER_MESSAGE_BANK && msgNo >= 1 && msgNo <= 6) {
        *out = BuildStarterMessage(heapId, msgNo);
    } else {
        *out = NewString_ReadMsgData(msgData, msgNo);
    }
    FillWindowPixelBuffer(window, (u8)color);
    printerId = AddTextPrinterParameterizedWithColor(window, 1, *out, 0, 0, speed, color, NULL);
    if (makeFrame) {
        DrawFrameAndWindow2(window, FALSE, 0x200, 0);
    } else {
        CopyWindowToVram(window);
    }
    DestroyMsgData(msgData);
    return printerId;
}
