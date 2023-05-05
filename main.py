import discord
from discord.ext import commands
from colorama import Back, Fore, Style
import time
import platform
from dotenv import load_dotenv ; load_dotenv()
from os import getenv
import guild_settings as gs
import settings
import asyncio

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('>.<'), intents=discord.Intents().all())

    async def status_task(self):
        while True:
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name="past you nerds!",url="https://www.youtube.com/watch?v=HZCKddHYgPM"))
            await asyncio.sleep(60)
            await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name="with you nerds!"))
            await asyncio.sleep(60)

    async def setup_hook(self):
        for key, value in settings.modules.items():
            if value:
                await self.load_extension(f"modules.{key}")
        await self.tree.sync()

    async def on_ready(self):
        bot.loop.create_task(self.status_task())
        prfx = (Back.BLACK + Fore.MAGENTA + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.MAGENTA + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord.py Version " + Fore.CYAN + discord.__version__)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + Fore.WHITE)

bot = Bot()

if __name__ == "__main__":
    if settings.mode.lower() == "retail":
        bot.run(getenv("token")) 
    elif settings.mode.lower() == "development":
        bot.run(getenv("development_token"))
    else:
        print("You forgot to set the runtime mode, dumbass")