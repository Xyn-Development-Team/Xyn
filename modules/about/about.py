class module:
    name = "About"
    cog_name = "about"
    description = "Adds commands to show information about this instance"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Literal
from typing import Optional
import settings
import importlib
import imagetools
from os import path

class about(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/permissions
    @app_commands.command(name="permissions",description="Here you can learn why Xyn needs it's permissions!")
    async def permissions_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Permissions and reasoning:**",color=discord.Color.from_str(imagetools.get_accent_color(self.bot.user.display_avatar.url))).set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.deploy.permissions_usage.items():
            embed.add_field(name=key,value=value,inline=False)

        await interaction.response.send_message(embed=embed)

    #/deployment
    @app_commands.command(name="deployment",description="Here you can see information about this Xyn's deployment")
    async def deployment_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Maintained by:** {settings.deploy.maintainers}\n\n**Modules loaded:**",color=discord.Color.from_str(imagetools.get_accent_color(self.bot.user.display_avatar.url))).set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.modules.items():
            if value:               
                if path.isfile(f"modules/{key}.py"):
                    module = importlib.import_module(f"modules.{key}")
                elif path.isdir(f"modules/{key}"):
                    module = importlib.import_module(f"modules.{key}.{key}")
            embed.add_field(name=module.module.name,value="Enabled" if value else "Disabled")
        await interaction.response.send_message(embed=embed)

    #/credits
    @app_commands.command(name="credits",description="Check who are the amazing people behind this deployment")
    async def credits(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Maintained by:** {settings.deploy.maintainers}",color=discord.Color.from_str(imagetools.get_accent_color(self.bot.user.display_avatar.url))).set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.deploy.credits.items():
            embed.add_field(name=key,value=value,inline=False)
            
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    print("About was loaded")
    await bot.add_cog(about(bot))