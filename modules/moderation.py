import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from discord.ext.commands import has_permissions, CheckFailure
from typing import Literal
from typing import Optional

import guild_settings as gs
import re

class moderation(commands.GroupCog, name="moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @commands.Cog.listener("on_message")
    async def on_message(self,message:discord.Message):
        if message.author.id == self.bot.user.id:
            return
        try:
            blacklist = str(gs.read(message.guild.id,"blocked_words","")).split(",")
        except AttributeError:
            return
        for word in blacklist:
            if any([":regex" in word]):
                word = re.sub(re.escape(":regex"),"",word)
                if re.search(word.lower(),message.content.lower()):
                    await message.delete()
                    try:
                        return await message.author.send(f"""The word **"{word.title()}"** isn't allowed in the guild **"{message.guild.name}"**!""")
                    except:
                        return
            else:
                if any([word.lower() in message.content.lower()]):
                    await message.delete()
                    try:
                        return await message.author.send(f"""The word **"{word.title()}"** isn't allowed in the guild **"{message.guild.name}"**!""")
                    except:
                        return

    #/confessions_reset
    @app_commands.command(name="confessions_reset",description="| Moderation (Admin) | Resets the confessions counter of this guild!")
    @has_permissions(manage_messages=True)
    async def confessions_reset(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_messages:
            gs.set(interaction.guild_id,"confessions",0)
            interaction.response.send_message("The confessions counter has been reset to **0!**")
        else:
            await interaction.response.send_message(f"You don't have permission to do that!")

    #/blacklist
    @app_commands.command(name="blacklist",description="| Moderation (Manage Messages) | Blacklists a specified word on all messages")
    @app_commands.describe(word="Which word do you want to add to the blacklist?",regex="Do you want to block any letter patterns containing this word?")
    @has_permissions(manage_messages=True)
    async def blacklist_add(self, interaction:discord.Interaction, word:str, action:Literal["Add","Remove","Clear"] ,regex:Optional[Literal["Yes","No"]]):
        if action == "Add":      
            if regex == "Yes":
                try:
                    blocked_words = gs.read(interaction.guild_id,"blocked_words")
                    gs.set(interaction.guild_id,"blocked_words",blocked_words + "," + word.lower() + ":regex")
                except:
                    gs.set(interaction.guild_id,"blocked_words",word.lower()+":regex")
            else:    
                try:
                    blocked_words = gs.read(interaction.guild_id,"blocked_words")
                    gs.set(interaction.guild_id,"blocked_words",blocked_words + "," + word.lower())
                except:
                    gs.set(interaction.guild_id,"blocked_words",word.lower())
            return await interaction.response.send_message(f"""Added "{word}" to the blacklist""",ephemeral=True)
        elif action == "Remove":
            try:
                blocked_words = str(gs.read(interaction.guild_id,"blocked_words")).split(",")
            except:
                return await interaction.response.send_message("The blacklist is empty!",ephemeral=True)
            for w in blocked_words:
                if any([word.lower() in w.lower()]):
                    try:
                        blocked_words = blocked_words.remove(word.lower())
                    except ValueError:
                        blocked_words = blocked_words.remove(word.lower()+":regex")
                    gs.set(interaction.guild_id,"blocked_words",blocked_words)
                    return await interaction.response.send_message(f"""The word "{word.title()}" has been removed from the blacklist!""",ephemeral=True)
            else:
                return await interaction.response.send_message(f"""There's no words matching "{word.title()}" in the blacklist!""",ephemeral=True)
        elif action == "Clear":
            gs.set(interaction.guild_id,"blocked_words",None)
            return await interaction.response.send_message("The blacklist has been wiped!",ephemeral=True)

    #/purge
    @app_commands.command(name="purge",description="| Moderation (Manage Messages) | Bulk deletes a specified ammount of messsages!",)
    @has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, ammount:app_commands.Range[int,1,100]):
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
    await bot.add_cog(moderation(bot))
