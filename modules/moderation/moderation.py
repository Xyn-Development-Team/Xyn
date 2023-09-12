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

import pycountry
import xyn_locale
import settings

class moderation(commands.GroupCog, name="moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/confessions_reset
    @app_commands.command(name="confessions_reset",description="| Moderation (Admin) | Resets the confessions counter of this guild!")
    @has_permissions(manage_messages=True)
    async def confessions_reset(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(xyn_locale.internal.locale("only_guild",gs.read(interaction.guild_id,"language")))
        if interaction.user.guild_permissions.manage_messages:
            gs.set(interaction.guild_id,"confessions",0)
            await interaction.response.send_message(xyn_locale.locale("confessions.reset",gs.read(interaction.guild_id,"language","en-us")))
        else:
            await interaction.response.send_message(xyn_locale.internal.locale("no_permission.user",gs.read(interaction.guild_id,"language")))

    #/purge
    @app_commands.command(name="purge",description="| Moderation (Manage Messages) | Bulk deletes a specified ammount of messsages!",)
    @has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, ammount:app_commands.Range[int,1,100]):
        if not interaction.guild:
            return await interaction.response.send_message(xyn_locale.internal.locale("only_guild",gs.read(interaction.guild_id,"language")))
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.defer(thinking=True)
            counter = 0
            async for message in interaction.channel.history(limit=ammount):
                counter += 1
            await interaction.followup.send(xyn_locale.locale("purging",gs.read(interaction.guild_id,"language","en-us")).format(counter))
            await interaction.channel.purge(limit=ammount)
            await interaction.channel.send(xyn_locale.locale("purged",gs.read(interaction.guild_id,"language","en-us")).format(counter))
        else:
            await interaction.response.send_message(xyn_locale.internal.locale("no_permission.user",gs.read(interaction.guild_id,"language")))
        
    #/language
    @app_commands.command(name="language",description="| Moderation (Admin) | Sets the language of Xyn's responses")
    @has_permissions(administrator=True)
    async def language(self, interaction: discord.Interaction, language:str):
        if language in xyn_locale.languages:
            gs.set(interaction.guild_id,"language",xyn_locale.languages[language])
            return await interaction.response.send_message(xyn_locale.locale("language.set",gs.read(interaction.guild_id,"language","en-us")))
        else:
            return await interaction.response.send_message(xyn_locale.locale("invalid_language",gs.read(interaction.guild_id,"language","en-us")).format(language))

async def setup(bot: commands.Bot) -> None:
    print(xyn_locale.locale("setup.loaded",settings.language))
    await bot.add_cog(moderation(bot))