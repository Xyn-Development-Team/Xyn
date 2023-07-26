class module:
    name = "Moderation"
    cog_name = "moderation"
    description = "Some few moderation tools"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions

import guild_settings as gs
import re

class moderation(commands.GroupCog, name="moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/confessions_reset
    @app_commands.command(name="confessions_reset",description="| Moderation (Admin) | Resets the confessions counter of this guild!")
    @has_permissions(manage_messages=True)
    async def confessions_reset(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")
        if interaction.user.guild_permissions.manage_messages:
            gs.set(interaction.guild_id,"confessions",0)
            await interaction.response.send_message("The confessions counter has been reset to **0!**")
        else:
            await interaction.response.send_message(f"You don't have permission to do that!")

    #/purge
    @app_commands.command(name="purge",description="| Moderation (Manage Messages) | Bulk deletes a specified ammount of messsages!",)
    @has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, ammount:app_commands.Range[int,1,100]):
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.defer(thinking=True)
            counter = 0
            async for message in interaction.channel.history(limit=ammount):
                counter += 1
            await interaction.followup.send(f"Purging **{counter}** messages...")
            await interaction.channel.purge(limit=ammount)
            await interaction.channel.send(f"Purged **{counter}** messages!")
        else:
            await interaction.response.send_message(f"You don't have permission to do that!")
        

async def setup(bot: commands.Bot) -> None:
    print("Moderation was loaded!")
    await bot.add_cog(moderation(bot))