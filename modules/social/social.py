class module:
    name = "Social"
    cog_name = "social"
    description = "Commands to make interacting with fellow users a bit easier."
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
    import storage
    import localization
    from typing import Literal, Optional
    import objdict
    import imagetools
    import datetime

class social(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.channel.guild:
            return

        if not os.path.isdir("./modules/social/users/afk"):
            os.makedirs("./modules/social/users/afk")
        
        if not os.path.isdir("./modules/social/guilds/"):
            os.makedirs("./modules/social/guilds/")

        guild_id = message.channel.guild.id
        language = storage.guild.read(guild_id,"language")

        try:
            guild_afk = os.listdir(f"./modules/social/guilds/{guild_id}/afk/")
        except FileNotFoundError:
            os.makedirs(f"./modules/social/guilds/{guild_id}/afk/")
            guild_afk = []

        global_afk = os.listdir(f"./modules/social/users/afk/")

        for user in guild_afk:
            if f"<@{user.rstrip('.json')}>" in message.content:
                data = objdict.loads(str(open(f"./modules/social/guilds/{guild_id}/afk/{user}","r").read()))
                try:
                    afk_message = "\"" + data["afk_message"] + "\""
                except KeyError:
                    afk_message = None
                
                guild = await self.bot.fetch_guild(guild_id)
                user = await guild.fetch_member(user.rstrip('.json'))
                timestamp = data["timestamp"]

                embed = discord.Embed(title=str(localization.external.read("afk_embed_title", language)).format(user=user.display_name), description=afk_message, color=discord.Color.from_str(imagetools.get_average_color(user.display_avatar.url)), timestamp=datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).set_thumbnail(url=user.display_avatar.url)
                return await message.reply(embed=embed)

        for user in global_afk:
            if f"<@{user.rstrip('.json')}>" in message.content:
                data = objdict.loads(str(open(f"./modules/social/users/afk/{user}","r").read()))
                try:
                    afk_message = "\"" + data["afk_message"] + "\""
                except KeyError:
                    afk_message = None
                
                guild = await self.bot.fetch_guild(guild_id)
                user = await guild.fetch_member(user.rstrip('.json'))
                timestamp = data["timestamp"]

                embed = discord.Embed(title=str(localization.external.read("afk_embed_title", language)).format(user=user.display_name), description=afk_message, color=discord.Color.from_str(imagetools.get_average_color(user.display_avatar.url)), timestamp=datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')).set_thumbnail(url=user.display_avatar.url)
                return await message.reply(embed=embed)

    #/unafk
    @app_commands.command(name="unafk", description="Disables AFK")
    async def unafk(self, interaction:discord.Interaction, globally:Optional[Literal["Yes", "No"]]):
        if not os.path.isdir(f"./modules/social/guilds/{interaction.guild.id}/"):
            os.makedirs(f"./modules/social/guilds/{interaction.guild.id}/afk")
        
        if interaction.guild:
            language = storage.guild.read(interaction.guild.id,"language")
        else:
            if not str(globally.lower()) == "yes":
                return await interaction.response.send_message(localization.external.read("no_guild_afk", language), ephemeral=True)
        
        if globally:
            try:
                os.remove(f"./modules/social/users/afk/{interaction.user.id}.json")
            except OSError as e:
                pass
            return await interaction.response.send_message(localization.external.read("disable_afk", language))
        elif interaction.guild:
            try:
                os.remove(f"./modules/social/guilds/{interaction.guild.id}/afk/{interaction.user.id}.json")
            except OSError as e:
                pass
            return await interaction.response.send_message(localization.external.read("disable_afk_guild", language), ephemeral=True)

    #/afk
    @app_commands.command(name="afk", description="Show an AFK message whenever someone pings you!")
    @app_commands.describe(message="(Optional) A Message that will be shown when someone pings you while AFK", globally="Do you want to be AFK for every server Xyn is on?")
    async def afk(self, interaction: discord.Interaction, message:Optional[str], globally:Optional[Literal["Yes", "No"]]):     
        if not os.path.isdir(f"./modules/social/guilds/{interaction.guild.id}/"):
            os.makedirs(f"./modules/social/guilds/{interaction.guild.id}/afk")
        
        if interaction.guild:
            language = storage.guild.read(interaction.guild.id,"language")
        else:
            language = str(interaction.locale).lower()
            if not str(globally.lower()) == "yes":
                return await interaction.response.send_message(localization.external.read("no_guild_afk", language))
        
        if str(globally).lower() == "yes":
            with open(f"./modules/social/users/afk/{interaction.user.id}.json", "w") as file:
                data = objdict.ObjDict()
                if message:
                    data["afk_message"] = message
                data["timestamp"] = datetime.datetime.now()
                file.write(data.dumps())
            storage.user.set(interaction.user.id, "afk", True)
            return await interaction.response.send_message(localization.external.read("enable_afk", storage.guild.read(interaction.guild.id, "language")), ephemeral=True)
        else:
            with open(f"./modules/social/guilds/{interaction.guild.id}/afk/{interaction.user.id}.json", "w") as file:
                data = objdict.ObjDict()
                if message:
                    data["afk_message"] = message
                data["timestamp"] = datetime.datetime.now()
                file.write(data.dumps())
            return await interaction.response.send_message(localization.external.read("enable_afk_guild", storage.guild.read(interaction.guild.id, "language")), ephemeral=True)

    #/poll
    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(choices="Separate each choice with a semicolon (;)", title="A nice eye-catching title for your poll")
    async def poll(self, interaction: discord.Interaction, title:str, choices:str, thumbnail:Optional[discord.Attachment], votes:Optional[int]):
        choices = choices.split(";")

        emojis = ["⚫","🟤", "🟣", "🔵", 
        "🟢", "🟡", "🟠", "🔴", "⚪"]

        embed = discord.Embed(title=title)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail.url)
        
        counter = 0
        reactions = []
        for choice in choices:
            reactions.append(emojis[counter])
            embed.add_field(name=emojis[counter], value=choice, inline=True)
            counter += 1
        
        await interaction.response.send_message("Poll created!", ephemeral=True)
        message = await interaction.channel.send(embed=embed)
        
        for reaction in reactions:
            await message.add_reaction(reaction)


async def setup(bot: commands.Bot) -> None:
    print("social.py was loaded!")

    if not os.path.isdir("./modules/social/users"):
        os.makedirs("./modules/social/users/")

    if not os.path.isdir("./modules/social/guilds"):
        os.makedirs("./modules/social/guilds/")

    await bot.add_cog(social(bot))