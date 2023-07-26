class module:
    name = "Analytics"
    description = "Logs command usage anonymously"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord.ext import commands
from typing import Optional
import os
import shutil
from objdict import ObjDict
from typing import Union

class Analytics(commands.Cog, name="analytics"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not os.path.isdir("./analytics"):
            os.makedirs("./analytics")
        if not os.path.isfile("./analytics/commands.json"):
            with open(f"./analytics/commands.json", "w") as command_analytics:
                command_analytics.write("{}")

    @commands.Cog.listener()
    async def on_app_command_completion(self,interaction,command):
        command = interaction.command.name
        module = interaction.command.module

        with open(f"./analytics/commands.json", "r+") as command_analytics:
            try:
                data = ObjDict.loads(command_analytics.read())
            except ObjDict.JsonDecodeError:
                print("Your analytics file seems to be corrupted! Backing up and creating a new one...")
                shutil.copy2("./analytics/commands.json", "./analytics/commands(backup).json")
                command_analytics.write("{}")
                data = ObjDict.loads(command_analytics.read())
            
            data[f"{module}/{command}"] = data.get(f"{module}/{command}", 0) + 1
            command_analytics.seek(0)
            command_analytics.write(ObjDict.dumps(data))
            command_analytics.truncate()


async def setup(bot: commands.Bot):
    await bot.add_cog(Analytics(bot))
    print("Analytics was loaded!")