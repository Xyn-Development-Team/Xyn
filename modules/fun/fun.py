class module:
    name = "Fun"
    cog_name = "fun"
    description = "Lot's of fun commands!"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"

import os

if __name__ == "__main__":
    print("This is supposed to be imported by Xyn! You dummy!!!")
    os._exit(1)
else:
    import discord
    from discord import app_commands
    from discord.ext import commands
    import random
    import requests
    import storage
    from typing import Optional
    import modules.fun.imagetools as imagetools

class Confession(discord.ui.Modal,title="Confession"):
    user_title = discord.ui.TextInput(
        label="Title",
        placeholder="A nice eye-catching title",
        max_length=40
    )

    confession = discord.ui.TextInput(
        label="Confession",
        placeholder="Your confession...",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=self.confession.value,
            color=discord.Color.random(),
        )
        confessions = storage.guild.read(interaction.guild_id,option="confessions")

        if confessions:
            confessions = int(confessions) + 1
        else:
            confessions = 1
        storage.guild.set(interaction.guild_id,"confessions",confessions)

        embed.title = f"Confession #{confessions} {self.user_title.value}"
        await interaction.response.send_message("Confession posted successfully!",ephemeral=True)
        await interaction.channel.send(embed=embed)

class fun(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    #/diceroll
    @app_commands.command(name="diceroll",description="Allows you to roll a dice")
    async def diceroll(self, interaction: discord.Interaction,sides:app_commands.Range[int,1,999]):
        dice = random.randint(1,int(sides))
        image = imagetools.dice(interaction.user.id,dice)

        thumbnail = discord.File(image,filename=f"dice_{dice}_xyn.png")

        embed = discord.Embed(title=f"**{interaction.user.display_name}**",description=f"has rolled a **{dice}!**",color=discord.Color.from_str("#e8439c"))
        embed.set_thumbnail(url=f"attachment://dice_{dice}_xyn.png")
        
        await interaction.response.send_message(file=thumbnail,embed=embed)
        thumbnail.close()
        os.remove(image)

    #TODO: Add a coin thumbnail to the embed
    #/coinflip
    @app_commands.command(name="coinflip",description="Allows you to flip a coin")
    async def coinflip(self, interaction: discord.Interaction):
        coin = random.randint(0,1)
        if coin < 1:
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
            return await interaction.response.send_message("This command can only be used within a guild!")
        
        if not username:
            username = storage.user.read(interaction.user.id,"persona_username")
            if not username:
                return await interaction.response.send_message("You need to provide an username at least once to use this command!")
        else:
            storage.user.set(interaction.user.id,"persona_username",username)

        await interaction.response.send_message(f"{interaction.client.user.name} is thinking...",ephemeral=True)

        if not pfp:
            pfp = storage.user.read(interaction.user.id,"persona_pfp")
            
            if pfp:
                webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(pfp).content)
            else:
                webhook = await interaction.channel.create_webhook(name=username)
        else:
            storage.user.set(interaction.user.id,"persona_pfp",pfp)
            webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(pfp.url).content)

        await webhook.send(message)
        await webhook.delete()

    @app_commands.command(name="quote",description="Someone said something quite poetic, huh?")
    async def quote(self, interaction: discord.Interaction, quote:str, user:Optional[discord.User],name:Optional[str],pfp:Optional[discord.Attachment]):
        await interaction.response.defer(thinking=True)
        if user:
            image = imagetools.quote(user.id,user.display_name,user.display_avatar,quote)
        else:
            image = imagetools.quote(id=interaction.user.id ,username=name if name else "Anonymous",pfp=pfp if pfp else None,quote=quote)
        
        if image:
            await interaction.followup.send(file=discord.File(image))
            os.remove(image)
        else:
            await interaction.followup.send("An error has occurred generating this quote image :c")

    @app_commands.command(name="confess",description="Allows you to confess anonymously")
    async def confess(self, interaction: discord.Interaction):
        if interaction.guild:
            await interaction.response.send_modal(Confession())
        else:
            await interaction.response.send_message("This command can only be used within a guild!")

async def setup(bot: commands.Bot) -> None:
    if not os.path.isdir("./modules/fun/temp"):
        os.makedirs("./modules/fun/temp")
    print("fun.py was loaded!")
    await bot.add_cog(fun(bot))
