class module:
    name = "Fun"
    cog_name = "fun"
    description = "Lot's of fun commands!"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"

import os

if __name__ == "__main__":
    # This is supposed to be imported by Xyn! You dummy!!!
    # We can't really localize this, since loading localization with this being directly executed would crash :c
    print("This is supposed to be imported by Xyn! You dummy!!!")
    os._exit(1)
else:
    import discord
    from discord import app_commands
    from discord.ext import commands
    import random
    import requests
    import storage
    from typing import Optional, Union
    import modules.fun.imagetools as imagetools
    import localization
    import re

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

    #TODO add color based on the color most present in the user's pfp
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent):
        emoji = payload.emoji
        guild = self.bot.get_guild(payload.guild_id)
        channel = guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        for reaction in message.reactions:
            if reaction.emoji == storage.guild.read(guild.id, "starboard_emoji") and reaction.count >= int(storage.guild.read(guild.id, "starboard_threshold")):
                starboard_channel = guild.get_channel(storage.guild.read(guild.id, "starboard_channel"))
                
                embed = discord.Embed(title=message.author.display_name,description=f"\"{message.content}\"").set_thumbnail(url=message.author.display_avatar.url)

                attachment_counter = 0
                attachments = []
                
                for attachment in message.attachments:
                    attachment_counter =+ 1
                    attachments.append(attachment.url)
                
                if attachment_counter == 1:
                    embed.set_image(url=attachments[0])

                await starboard_channel.send(embed=embed)

                if attachment_counter > 1:
                    for attachment in attachments:
                        await starboard_channel.send(attachment)

    #/diceroll
    @app_commands.command(name="diceroll",description="Allows you to roll a dice")
    async def diceroll(self, interaction: discord.Interaction,sides:app_commands.Range[int,1,999]):
        dice = random.randint(1,int(sides))
        image = imagetools.dice(interaction.user.id,dice)

        thumbnail = discord.File(image,filename=f"dice_{dice}_xyn.png")

        # Title = **{user}**
        # Description = has rolled a **{dice}!**
        embed = discord.Embed(title=f"**{interaction.user.display_name}**",description=str(localization.external.read("diceroll_embed_description",storage.guild.read(interaction.guild.id,"language"))).format(dice=dice),color=discord.Color.from_str("#e8439c"))
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
            result = localization.external.read("heads",storage.guild.read(interaction.guild.id,"language"))
        else:
            result = localization.external.read("tails",storage.guild.read(interaction.guild.id,"language"))
        # **{user}** has flipped **{result}!**
        embed = discord.Embed(title=localization.external.read("coinflip_embed_title",storage.guild.read(interaction.guild.id,"language")))
        await interaction.response.send_message(embed=embed)
    
    #/uselessfacts
    # TODO Implement Google Translate into the response in case the guild language isn't en-us
    @app_commands.command(name="uselessfacts",description="Gives you a random useless fact about za warudo")
    async def uselessfacts(self, interaction: discord.Interaction):
        fact = requests.get("https://useless-facts.sameerkumar.website/api").json()["data"]
        await interaction.response.send_message(fact)

    #/persona
    @app_commands.command(name="persona",description="Allows u to send a message as \"another user\"")
    async def persona(self, interaction: discord.Interaction, message:str, username:Optional[str], pfp:Optional[discord.Attachment]):
        #DM's
        if not interaction.guild:
            # This command can only be used within a guild!
            return await interaction.response.send_message(localization.internal.read("guild_only",storage.guild.read(interaction.guild.id,"language")))
        
        if not username:
            username = storage.user.read(interaction.user.id,"persona_username")
            if not username:
                #You need to provide an username at least once to use this command!
                return await interaction.response.send_message(localization.external.read("persona_no_username"))
        else:
            storage.user.set(interaction.user.id,"persona_username",username)

        # {bot} is thinking...
        await interaction.response.send_message(localization.internal.read("thinking",storage.guild.read(interaction.guild.id,"language")),ephemeral=True)

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

    #/quote
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
            # An error has occurred generating this quote image :c
            await interaction.followup.send(localization.external.read("quote_error",storage.guild.read(interaction.guild.id,"language")))

    #/confess
    @app_commands.command(name="confess",description="Allows you to confess anonymously")
    async def confess(self, interaction: discord.Interaction):
        if interaction.guild:
            await interaction.response.send_modal(Confession())
        else:
            # This command can only be used within a guild!
            await interaction.response.send_message(localization.internal.read("guild_only",storage.guild.read(interaction.guild.id,"language")))

    #/starboard_setups
    @app_commands.command(name="starboard_setup",description="Setup how starboards behave")
    @app_commands.default_permissions(manage_messages=True)
    async def starboard_setup(self, interaction:discord.Interaction, channel:discord.TextChannel, emoji:str, threshold:int):
        await interaction.response.defer(thinking=True,ephemeral=True)

        emoji_pattern = re.compile(r'<:\w+:\d+>|[^\w\s,]')
        emojis = emoji_pattern.findall(emoji)

        storage.guild.set(interaction.guild_id, "starboard_channel", channel.id)
        storage.guild.set(interaction.guild_id, "starboard_emoji", emojis[0])
        storage.guild.set(interaction.guild_id, "starboard_threshold", threshold)

        await interaction.followup.send(localization.external.read("starboard_setup", storage.guild.read(interaction.guild.id, "language")),ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    if not os.path.isdir("./modules/fun/temp"):
        os.makedirs("./modules/fun/temp")
    print("fun.py was loaded!")
    await bot.add_cog(fun(bot))
