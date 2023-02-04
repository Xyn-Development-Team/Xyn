import lightbulb
import hikari
import uwuify
import guild_settings as gs
import requests
import random

fun = lightbulb.Plugin("fun")

#/roll_dice
@fun.command
@lightbulb.option("type","What type of dice do you want to roll?",choices=["D6","D20"])
@lightbulb.command("roll_dice","Rolls the dice")
@lightbulb.implements(lightbulb.SlashCommand)
async def roll_dice(ctx: lightbulb.Context):
    rest_account = await ctx.app.rest.fetch_user(ctx.author.id)
    accent = rest_account.accent_color
    if ctx.options.type == "D6":
        dice_emoji = ["<:Dice1:1018347458897645629>","<:Dice2:1018347460982218792>","<:Dice3:1018347463259738142>","<:Dice4:1018347465352687707>","<:Dice5:1018347467621806090>","<:Dice6:1018347470251626576>"]
        dices = ["https://cdn.discordapp.com/emojis/1018347458897645629.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347460982218792.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347463259738142.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347465352687707.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347467621806090.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347470251626576.webp?quality=lossless"]
        dice = random.randint(0, 5)
    elif ctx.options.type == "D20":
        dices = ["https://cdn.discordapp.com/emojis/1018361716490379284.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361718197465128.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361719808065586.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361721087348797.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361723163512862.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361724899950604.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361726623821824.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361728305745980.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361729920532511.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361731686354986.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361733636698203.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361735540920390.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361737218621471.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361738791493693.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361740540522506.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361742314709033.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361744223121478.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361746190237716.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361748165767238.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361750023839784.webp?&quality=lossless"]
        dice = random.randint(0, 19)
    dn = dice + 1
    dice = dices[dice]
    emb = hikari.Embed(title=f"{ctx.author}",description=f"Rolled a {dn} !",color=accent)
    emb.set_thumbnail(f"{dice}")
    await ctx.respond(emb)

@fun.command
@lightbulb.option("text","What do you w-want t-to say?!! UwU")
@lightbulb.command("uwuify","Makes evewything that you type wess bowing ^w^")
@lightbulb.implements(lightbulb.SlashCommand)
async def uwu(ctx: lightbulb.Context):
    await ctx.respond(uwuify.uwu(ctx.options.text,flags=uwuify.STUTTER | uwuify.YU))

@fun.command
@lightbulb.option("uwuify","Do you w-want t-to enhance youw sewvew commands!?",choices=["Yes","No"])
@lightbulb.command("uwuify_server","Enhances youw sewvew commands?!!")
@lightbulb.implements(lightbulb.SlashCommand)
async def uwu_server(ctx: lightbulb.Context):
    if ctx.options.uwuify == "Yes":
        if gs.set_uwu(ctx.guild_id,True) == "English Only":
            await ctx.respond(gs.text("uwu_no_lang", gs.guild_language(ctx.guild_id)))
        else:
            await ctx.respond(gs.text("uwu_enabled",gs.guild_language(ctx.guild_id)))
    elif ctx.options.uwuify == "No":
        if gs.set_uwu(ctx.guild_id,False) == "English Only":
            await ctx.respond(gs.text("uwu_no_lang", gs.guild_language(ctx.guild_id)))
        else:
            await ctx.respond(gs.text("uwu_disabled",gs.guild_language(ctx.guild_id)))
    else:
        await ctx.respond(gs.text("generic_error",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))

#/roleplay
@fun.command
@lightbulb.option("action",description="What are you going to do?",choices=["slap","kiss","hug","sleep","punch","cuddle","blush","pat","smug","poke","run","stare"])
@lightbulb.option("together",description="With who or To who? (Optional)",type=hikari.User,required=False)
@lightbulb.command("roleplay","Do something from a list of actions!",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def roleplay(ctx: lightbulb.SlashContext):
    import roleplay
    action = ctx.options.action
    try:
        target = f"<@{ctx.options.together.id}>"
    except:
        target = None
    try:
        image_request = requests.get(f"https://api.otakugifs.xyz/gif?reaction={ctx.options.action}")
        response = image_request.json()
        image = response["url"]
    except:
        image = "https://pbs.twimg.com/media/DKs2G92X0AEjh3Z.jpg"
    emb = hikari.Embed(description=roleplay.better_roleplay(action,ctx,target))
    emb.set_image(image)
    await ctx.respond(emb)

def load(bot: lightbulb.BotApp):
    bot.add_plugin(fun)

def unload(bot):
    bot.remove_plugin(fun)