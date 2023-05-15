import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Literal
from typing import Optional
import settings

class about(commands.GroupCog, name="about"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/permissions
    @app_commands.command(name="permissions",description="Here you can learn why Xyn needs it's permissions!")
    async def permissions_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Permissions and reasoning:**").set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.deploy.permissions_usage.items():
            embed.add_field(name=key,value=value,inline=False)

        await interaction.response.send_message(embed=embed)

    #/deployment
    @app_commands.command(name="deployment",description="Here you can see information about this Xyn's deployment")
    async def deployment_info(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Maintained by:** {settings.deploy.maintainers}\n\n**Modules loaded:**").set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.modules.items():
            embed.add_field(name=key.title(),value="Enabled" if value else "Disabled")

        await interaction.response.send_message(embed=embed)

    #/credits
    @app_commands.command(name="credits",description="Check who are the amazing people behind this deployment")
    async def credits(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"Xyn ({settings.deploy.codename})",description=f"**Maintained by:** {settings.deploy.maintainers}").set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        for key, value in settings.deploy.credits.items():
            embed.add_field(name=key,value=value,inline=False)
            
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    print("About was loaded")
    await bot.add_cog(about(bot))
