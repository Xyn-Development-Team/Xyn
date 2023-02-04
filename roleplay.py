actions = {"kiss":"<@{userId}> kissed {target}! <3",
    "slap":"<@{userId}> slapped {target}!",
    "punch":"<@{userId}> punched {target}!",
    "hug":"<@{userID}> hugged {target}!",
    "sleep":"<@{userID}> is sleeping with {target}! <3",
    "poke":"<@{userID}> is poking {target}!",
    "cuddle":"<@{userID}> is cuddling {target}! <3",
    "blush":"<@{userID}> is blushing with {target}! <3",
    "pat":"<@{userID}> is petting {target}! <3",
    "smug":"<@{userID}> is being smug with {target}!",
    "run":"<@{userID}> is running with {target}!",
    "stare":"<@{userID}> is staring {target} 0_0 !",
    }
actions_solo = {"kiss":"<@{userID}> kissed themselves? 0_0",
        "slap":"<@{userID}> slapped themselves!",
        "punch":"<@{userID}> punched themselves!",
        "hug":"<@{userID}> hugged themselves? 0_0",
        "sleep":"<@{userID}> is sleeping",
        "poke":"<@{userID}> is poking themselves? 0_0",
        "cuddle":"<@{userID}> is cuddling with themselves? 0_0",
        "blush":"<@{userID}> is blushing! <3",
        "pat":"<@{userID}> is petting themselves? 0_0",
        "smug":"<@{userID}> is being smug!",
        "run":"<@{userID}> is running!",
        "stare":"<@{userID}> is staring themselves! 0_0",
    }

def better_roleplay(action,ctx,target=None):
    try:
        rpString = actions[action] if target != None else actions_solo[action]
        return rpString.format(userID = ctx.user.id, target=target)
    except:
        return f"<@{ctx.user.id}> came on catgirl. OWO?"