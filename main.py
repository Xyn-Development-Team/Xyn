import discord
from discord.ext import commands
from colorama import Back, Fore, Style
import time
import platform
from dotenv import load_dotenv ; load_dotenv()
from os import getenv, makedirs, path, getcwd
import settings
import asyncio

import discord
from discord.ext import commands
import inspect


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('>.<'), intents=discord.Intents().all())

        @self.tree.error
        async def on_app_command_error(interaction: discord.Interaction, error:discord.app_commands.CommandInvokeError):
            # Get the frame where the exception occurred
            frame = inspect.currentframe().f_back

            # Get information about the occurence
            line_number = frame.f_lineno
            file_path = inspect.getframeinfo(frame).filename
            filename = path.basename(inspect.getframeinfo(frame).filename)
            log = f"{time.strftime('%d/%m/%Y %H:%M:%S UTC')}\nException: {interaction.command.module}.{interaction.command.name}:\nFile: {filename} {'(External)' if file_path != getcwd() else ''}, line {line_number}\n{error.original}"

            if isinstance(error.original, AttributeError):
                if not path.isdir("./logs"):
                    makedirs("./logs")
                try:
                    await interaction.response.send_message(f"An uncaught `AttributeError` has occurred, this occurrence has been automatically reported to your maintainer!\nHere's the log:\n```{log}```")
                except discord.errors.InteractionResponded:
                    await interaction.followup.send(f"An uncaught `AttributeError` has occurred, this occurrence has been automatically reported to your maintainer!\nHere's the log:\n```{log}```")
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H-%M-%S UTC')}.txt","w")
                print(log,file=logger)
                logger.close()
            
            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                await interaction.response.send_message("You don't have permission to run that command!",ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.BotMissingPermissions):
                await interaction.response.send_message("I don't have permission to do that!",ephemeral=True)
            
            elif isinstance(error.original, discord.app_commands.MissingPermissions):
                await interaction.response.send_message("You don't have permission to run that command!",ephemeral=True)

            elif isinstance(error.original, discord.errors.InteractionResponded):
                pass

            else:
                try:
                    await interaction.response.send_message(f"An uncaught exception has occurred, this occurrence has been automatically reported to your maintainer!:\nHere's the log:\n```{log}```")
                except discord.errors.InteractionResponded:
                    await interaction.followup.send(f"An uncaught exception has occurred, this occurrence has been automatically reported to your maintainer!:\nHere's the log:\n```{log}```")
                logger = open(f"./logs/UncaughtException_{time.strftime('%d-%m-%Y %H:%M:%S UTC')}.txt","w")
                print(log,file=logger)
                logger.close()

    async def setup_hook(self):
        for key, value in settings.modules.items():
            if value:
                await self.load_extension(f"modules.{key}")
        await self.tree.sync()        

    async def on_ready(self):
        #Status task, updates the bot's status every minute
        async def status_task(self):
            while True:
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name="past you nerds!",url="https://www.youtube.com/watch?v=HZCKddHYgPM"))
                await asyncio.sleep(60)
                await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="with you nerds!"))
                await asyncio.sleep(60)

        bot.loop.create_task(status_task(self))
        prfx = (Back.BLACK + Fore.MAGENTA + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.MAGENTA + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord.py Version " + Fore.CYAN + discord.__version__)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + Fore.WHITE)



bot = Bot()
if settings.mode.lower() == "retail":
    bot.run(getenv("token")) 
elif settings.mode.lower() == "development":
    bot.run(getenv("development_token"))
else:
    print("You forgot to set the runtime mode, dumbass")
