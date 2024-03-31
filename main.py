import asyncio
import inspect
import platform
import time
from os import getcwd, getenv, makedirs, path

import discord
from discord import app_commands
from colorama import Back, Fore, Style
from discord.ext import commands
from discord.ext.commands import has_permissions
from typing import Literal

from dotenv import load_dotenv ; load_dotenv()

import settings
import platform
import cpuinfo
import localization
import storage

from typing import Literal

class Bot(commands.Bot):
    """Initializes the bot and it's modules, as well as the error handler"""
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('>.<'), intents=discord.Intents().all())

        @self.tree.command(name="reload", description="Reloads all bot modules!")
        @app_commands.describe(resync="Sync all commands")
        @commands.is_owner()
        async def reload(interaction: discord.Interaction, resync:Literal["Yes","No"]):
            await interaction.response.defer(thinking=True)
            for key, value in settings.modules.items():
                if value:
                    if path.isfile(f"modules/{key}.py"):
                        await self.reload_extension(f"modules.{key}")
                    elif path.isdir(f"modules/{key}"):
                        await self.reload_extension(f"modules.{key}.{key}")
                    else:
                        # The module {module}'s files are missing!!
                        print(str(localization.internal.read("module_missing",settings.language)))
            
            if resync == "Yes":
                await self.tree.sync()
            
            await interaction.followup.send("All modules were reloaded successfully!",ephemeral=True)

        @self.tree.command(name="language", description="Sets what language Xyn should use in it's responses!")
        @has_permissions(administrator=True)
        async def language(interaction: discord.Interaction, language:Literal[tuple(localization.languages.keys())]):
            if not interaction.guild:
                return await interaction.response.send_message(localization.internal.read("guild_only", str(interaction.locale).lower()))
                
            storage.guild.set(interaction.guild.id, "language", localization.languages[language])
            await interaction.response.send_message(str(localization.internal.read("language_set", localization.languages[language])).format(language=language))

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error:discord.app_commands.CommandInvokeError):
            # Get the frame where the exception occurred
            frame = inspect.currentframe().f_back

            # Get information about the occurence
            line_number = frame.f_lineno
            file_path = inspect.getframeinfo(frame).filename
            filename = path.basename(inspect.getframeinfo(frame).filename)
            log = f"{time.strftime('%d/%m/%Y %H:%M:%S UTC')}\nException: {interaction.command.module}.{interaction.command.name}:\nFile: {filename} {'(External)' if file_path != getcwd() else ''}, line {line_number}\n{error.original}"
            
            if isinstance(error.original, discord.errors.InteractionResponded):
                # Interaction already acknowledged, {interaction.command.module}.{interaction.command.name}
                print(str(localization.internal.read("interaction_acknowledged",settings.language)).format(module=interaction.command.module,command=interaction.command.name))

            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                # You don't have permission to use this command!
                await interaction.channel.send(localization.internal.read("user_no_permission",settings.language),ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.BotMissingPermissions):
                # I don't have permission to do this!
                await interaction.channel.send(localization.internal.read("bot_no_permission"),ephemeral=True)
            else:
                await interaction.channel.send(str(localization.internal.read("uncaught_exception",settings.language)).format(log=log))
                # "An uncaught exception has occurred, this occurrence has been automatically reported to your maintainer!:\nHere's the log:\n```{log}```
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H:%M:%S UTC')}.txt","w",encoding="utf-8")
                logger.write(log)
                logger.close()

    async def setup_hook(self):
        for key, value in settings.modules.items():
            if value:
                if path.isfile(f"modules/{key}.py"):
                    await self.load_extension(f"modules.{key}")
                elif path.isdir(f"modules/{key}"):
                    await self.load_extension(f"modules.{key}.{key}")
                else:
                    # The module {module}'s files are missing!!
                    print(str(localization.internal.read("module_missing",settings.language)))
        #await self.tree.sync() # Only uncomment this when implementing new commands, or you'll be rate limited pretty quickly!!

    # Let's make sure we'll always have a language set for any new guilds
    async def on_guild_join(self, guild):
        if not storage.guild.read(guild.id, "language"):
            storage.guild.set(guild.id,"language",settings.language)

    # And also to ones we're already in
    async def on_interaction(self, interaction:discord.Interaction):
        if interaction.guild:
            if not storage.guild.read(interaction.guild.id, "language"):
                storage.guild.set(interaction.guild.id,"language", settings.language)

    async def on_ready(self):
        if not path.isdir("./logs"):
            makedirs("./logs")
        #Status task, updates the bot's presence every minute
        async def status_task(self):
            while True:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name="past you nerds!",url="https://www.youtube.com/watch?v=HZCKddHYgPM"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="with you nerds!"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="hide and seek with Fae!"))
                await asyncio.sleep(60)

        bot.loop.create_task(status_task(self))
        prfx = (Back.BLACK + Fore.MAGENTA + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT + " ")
        # prfx + f" Logged in as {Fore.MAGENTA}{self.user.name}{Fore.RESET}"
        print(prfx + str(localization.internal.read("logged_as",settings.language)).format(color=Fore.MAGENTA,user=self.user.name,reset=Fore.RESET))
        # prfx + f" Running on {Fore.GREEN}{settings.mode.lower()}{Fore.RESET} mode"
        print(prfx + str(localization.internal.read("running_on",settings.language)).format(color=Fore.GREEN,mode=str(localization.internal.read(settings.mode.lower(),settings.language)).lower(),reset=Fore.RESET))
        # prfx + f" OS: {Fore.CYAN}{platform.platform()} / {platform.release()}{Fore.RESET}"
        print(prfx + str(localization.internal.read("os",settings.language)).format(color=Fore.CYAN,os=platform.platform(),release=platform.release(),reset=Fore.RESET))
        # prfx + f" CPU: {Fore.CYAN}{cpuinfo.get_cpu_info()['brand_raw']}{Fore.RESET}"
        print(prfx + str(localization.internal.read("cpu",settings.language)).format(color=Fore.CYAN,cpu=cpuinfo.get_cpu_info()['brand_raw'],reset=Fore.RESET))
        # prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + Fore.WHITE"
        print(prfx + str(localization.internal.read("python_version",settings.language)).format(color=Fore.YELLOW,version=str(platform.python_version()),reset=Fore.RESET))
        # prfx + " Discord.py Version " + Fore.YELLOW + discord.__version__ + Fore.RESET"
        print(prfx + str(localization.internal.read("discord.py_version")).format(color=Fore.YELLOW,version=discord.__version__,reset=Fore.RESET))

bot = Bot()
if settings.mode.lower() == "retail":
    bot.run(getenv("token")) 
elif settings.mode.lower() == "development":
    bot.run(getenv("development_token"))
else:
    print(localization.internal.read("no_runtime",settings.language))