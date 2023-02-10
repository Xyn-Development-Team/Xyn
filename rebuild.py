## Modules #################################################################################################################

#Main
import settings
import hikari
import lightbulb
from lightbulb.ext import tasks
import time
import os
import guild_settings as gs
from dotenv import load_dotenv
from datetime import date
from dateutil.relativedelta import relativedelta
from datetime import timedelta

#Music
import miru

#Automatic Translations
import translators as ts

#Initialize the bot

load_dotenv()

if settings.mode == "Retail":
    bot = lightbulb.BotApp(token=os.getenv('token'),prefix=lightbulb.when_mentioned_or(None))
elif settings.mode == "Development":
    bot = lightbulb.BotApp(token=os.getenv('development_token'),prefix=lightbulb.when_mentioned_or(None))
else:
    raise Exception("You must set the mode to 'Retail' or 'Development'")
miru.install(bot)

@bot.listen(hikari.StartedEvent)
async def startup_routine(event):
    #Set activity
    activity = hikari.Activity(name=settings.status,type=hikari.ActivityType.WATCHING) ; await bot.update_presence(activity=activity)
    
    #Load modules
    if settings.modules.music:
        bot.load_extensions("modules.music")
    if settings.modules.cli:
        bot.load_extensions("modules.cli")
    if settings.modules.scraping:
        bot.load_extensions("modules.scraping")
    if settings.modules.moderation:
        bot.load_extensions("modules.moderation")
    if settings.modules.fun:
        bot.load_extensions("modules.fun")

tasks.load(bot)

#Error managing
@bot.listen(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    guild_id = event.context.guild_id
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(gs.text("command_error",gs.guild_language(guild_id),gs.get_uwu(guild_id)).format(event.context.command.name),flags=hikari.MessageFlag.EPHEMERAL)
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond(gs.text("no_dev",gs.guild_language(guild_id),gs.get_uwu(guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(gs.text("cooldown",gs.guild_language(guild_id),gs.get_uwu(guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
    elif isinstance(exception, lightbulb.errors.MissingRequiredRole):
        await event.context.respond(gs.text("no_permission",gs.guild_language(guild_id),gs.get_uwu(guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
    elif isinstance(exception, lightbulb.errors.MissingRequiredPermission):
        await event.context.respond(gs.text("no_permission",gs.guild_language(guild_id),gs.get_uwu(guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
    elif isinstance(exception, lightbulb.errors.BotMissingRequiredPermission):
        await event.context.respond(gs.text("xyn_no_permission",gs.guild_language(guild_id),gs.get_uwu(guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
    else:
        raise exception

#/say
@bot.command
@lightbulb.option("message","What Should I say?")
@lightbulb.option("greetings","Type here any greetings of your preferece or leave it empty",required=False)
@lightbulb.command("say","Makes the bot say things")
@lightbulb.implements(lightbulb.SlashCommand)
async def say(ctx: lightbulb.Context):
    Message = ctx.options.message
    if ctx.options.greetings:
        await ctx.respond(f"{Message}\n- {ctx.options.greetings} <@{ctx.user.id}>")
    else:
        await ctx.respond(f"{Message}\n- <@{ctx.user.id}>")

#/translate
@bot.command 
@lightbulb.option("input",description="What do you want to translate?")
@lightbulb.option("to",description="The target language to translate to. Ex: pt, en, es, ja")
@lightbulb.option("silently",description="Makes the message only appear for you",choices=["Yes","No"],required=False)
@lightbulb.command("translate","Translate your input to another language of your choice",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def translate_command(ctx:lightbulb.SlashContext):
    if ctx.options.silently == "Yes":
        await ctx.respond(str(ts.translate_text(query_text=str(ctx.options.input),translator="google",from_language="auto",to_language=str(ctx.options.to).lower())),flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(str(ts.translate_text(query_text=str(ctx.options.input),translator="google",from_language="auto",to_language=str(ctx.options.to).lower())))
        
#/check_age
@bot.command()
@lightbulb.option("user","Whose account do you want to check?.",type=hikari.User)
@lightbulb.command("check_age","Check's the age of an account")
@lightbulb.implements(lightbulb.SlashCommand)
async def check_age(ctx: lightbulb.SlashContext):
    account = ctx.options.user
    raw_date = f"{account.created_at}"
    year = int(raw_date[0:4]) ; month = int(raw_date[5:7]) ; day = int(raw_date[8:10])
    hour = raw_date[11:13]
    minute = raw_date[14:16]
    age = relativedelta(date.today(), date(year,month,day))
    await ctx.respond(f"Created at: {day}/{month}/{year} | {hour}:{minute} | Age : {age.years} year(s), {age.months} month(s), {age.days} day(s) ",flags=hikari.MessageFlag.EPHEMERAL)

#Check age
@bot.command
@lightbulb.command("Account's Age","See when this account was created.")
@lightbulb.implements(lightbulb.UserCommand)
async def check_age_menu(ctx: lightbulb.UserContext):
    account = ctx.options.target
    raw_date = f"{account.created_at}"
    year = int(raw_date[0:4]) ; month = int(raw_date[5:7]) ; day = int(raw_date[8:10])
    hour = raw_date[11:13]
    minute = raw_date[14:16]
    age = relativedelta(date.today(), date(year,month,day))
    await ctx.respond(f"Created at: {day}/{month}/{year} | {hour}:{minute} | Age : {age.years} year(s), {age.months} month(s), {age.days} day(s) ",flags=hikari.MessageFlag.EPHEMERAL)

#Get Pfp
@bot.command
@lightbulb.command("Get Pfp","Get the user's pfp in high quality (or at least the quality they've uploaded it).")
@lightbulb.implements(lightbulb.UserCommand)
async def get_pfp_menu(ctx: lightbulb.SlashContext):
    account = ctx.options.target
    if account.avatar_url:
        await ctx.respond(f"{account.avatar_url}",flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(gs.text("no_pfp",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

#Get Banner
@bot.command
@lightbulb.command("Get Banner","Get the user's banner in high quality (or at least the quality they've uploaded it).")
@lightbulb.implements(lightbulb.UserCommand)
async def get_banner(ctx: lightbulb.UserContext):
    account = ctx.options.target
    rest_account = await ctx.app.rest.fetch_user(account.id)
    banner = rest_account.banner_url
    if banner:
        await ctx.respond(f"{banner}",flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(gs.text("no_banner",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

#/get_pfp
@bot.command
@lightbulb.option("user","Who's pfp do you want to get?.",type=hikari.User)
@lightbulb.command("get_pfp","Get the url to the user's pfp")
@lightbulb.implements(lightbulb.SlashCommand)
async def get_pfp(ctx: lightbulb.SlashContext):
    account = ctx.options.user
    if account.avatar_url:
        await ctx.respond(f"{account.avatar_url}",flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(gs.text("no_pfp",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

#/get_banner
@bot.command
@lightbulb.option("user","Who's banner do you want to get?.",type=hikari.User)
@lightbulb.command("get_banner","Get the url to the user's banner")
@lightbulb.implements(lightbulb.SlashCommand)
async def get_banner(ctx: lightbulb.SlashContext):
    rest_account = await ctx.app.rest.fetch_user(ctx.options.user.id)
    banner = rest_account.banner_url
    if banner:
        await ctx.respond(f"{banner}",flags=hikari.MessageFlag.EPHEMERAL)
    else:
        await ctx.respond(gs.text("no_banner",gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()
    bot.run()
