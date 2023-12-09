class module:
    name = "Fun"
    cog_name = "fun"
    description = "Lot's of fun commands!"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"

import settings
import discord
from discord import app_commands
from discord.ext import commands
import random
import requests
import user_storage
from typing import Optional

class fun(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    #TODO: Add a neat little dice emoji to the embed
    #/diceroll
    @app_commands.command(name="diceroll",description="Allows you to roll a dice")
    async def diceroll(self, interaction: discord.Interaction):
        dice = random.randint(1,6)
        embed = discord.Embed(title=f"**{interaction.user.display_name}** has rolled a **{dice}!**")
        await interaction.response.send_message(embed=embed)

    #TODO: Add a coin thumbnail to the embed
    #/coinflip
    @app_commands.command(name="coinflip",description="Allows you to flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        coin = random.randint(1,2)
        if coin < 2:
            result = "Heads"
        else:
            result = "Tails"
        embed = discord.Embed(title=f"**{interaction.user.display_name}** has flipped **{result}!**")
        await interaction.response.send_message(embed=embed)
    
    #/uselessfacts
    @app_commands.command(name="uselessfacts",description="Gives you a random useless fact about za warudo")
    async def uselessfacts(self, interaction: discord.Interaction):
        fact = requests.get("https://useless-facts.sameerkumar.website/api").json()["data"]
        await interaction.response.send_message(fact)

    @app_commands.command(name="persona",description="Allows u to send a message as \"another user\"")
    async def persona(self, interaction: discord.Interaction, message:str, username:Optional[str], pfp:Optional[discord.Attachment]):
        #DM's
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")
        
        if not username:
            username = user_storage.read(interaction.user.id,"persona_username")
            if not username:
                return await interaction.response.send_message("You need to provide an username at least once to use this command!")
        else:
            user_storage.set(interaction.user.id,"persona_username",username)

        await interaction.response.send_message(f"{interaction.client.user.name} is thinking...",ephemeral=True)

        if not pfp:
            pfp = user_storage.read(interaction.user.id,"persona_pfp")
            
            if pfp:
                webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(pfp).content)
            else:
                webhook = await interaction.channel.create_webhook(name=username)
        else:
            user_storage.set(interaction.user.id,"persona_pfp",pfp)
            webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(pfp.url).content)

        await webhook.send(message)
        await webhook.delete()
        
    @app_commands.command(name="test_usr_write",description="Tests if the user_storage module is writting!")
    async def test_write(self, interaction: discord.Interaction):
        user_storage.set(interaction.user.id,"exists","yes")
        await interaction.response.send_message("Check the file u schewpid!")

    @app_commands.command(name="read_test",description="Tests if the user_storage module is reading!")
    async def test_write(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"The value is ``{user_storage.read(interaction.user.id,"exists")}``")

async def setup(bot: commands.Bot) -> None:
    print("fun.py was loaded!")
    await bot.add_cog(fun(bot))
