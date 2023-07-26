class module:
    name = "osu!"
    cog_name = "osu"
    description = "osu! Related commands"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
from typing import Optional
from os import getenv
from dotenv import load_dotenv ; load_dotenv()
from ossapi import Ossapi
import random
import guild_settings as gs
import time

import requests

import pycountry
import re
import imagetools

#Sets the credential to the API
api = Ossapi(getenv('osu_client_id'), getenv('osu_client_secret'))

async def loading_emoji(interaction:discord.Interaction):
    for emoji in interaction.guild.emojis:
        if emoji.name == "osuxyn":
            return f"<a:{emoji.name}:{emoji.id}>"
    emoji = await interaction.guild.create_custom_emoji(name="osuxyn",image=open("./assets/osu!xyn.gif","rb").read(),reason="This animated emoji is used when loading osu! commands")
    return f"<a:{emoji.name}:{emoji.id}>"
    
def get_flag(name:str=None,language:str=None,code:str=None):
    """## Transforms any of the given arguments into Discord flag emojis!
    `name`: A Country's name Ex: Japan, United States, Brazil
    `language`: A Country's language Ex: Japanese, English, Portuguese
    `code`: A osu! player's country code Ex: ja, us, br"""
    if language:
        try:
            flag = f":flag_{(pycountry.languages.get(name=language).alpha_3)[:-1]}:"
        except AttributeError:
            flag = ":flags:"
    elif name:
        try:
            flag = f":flag_{(pycountry.countries.get(name=name).alpha_3)[:-1]}:"
        except AttributeError:
            flag = ":flags:"
    elif code:
        flag = f":flag_{code.lower()}:"
    else:
        return f":flags:"
    
    #Here's any other necessary modifications to adapt to Discord's emoji naming scheme!
    flag = re.sub("en","us",flag)
    flag = re.sub("uk","gb",flag)
    flag = re.sub("zh","cn",flag)
    return flag


class osu_wiki_urls():
    gamemodes = {
        "osu":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21",
        "taiko":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21taiko",
        "catch":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21catch",
        "mania":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21mania"
    }

async def osu_webhook(interaction:discord.Interaction):
    for w in await interaction.channel.webhooks():
        if w.name == f"osu!{interaction.client.user.name.lower()}" or w.name == f"osu!{interaction.client.user.display_name.lower()}":
            if w.name != f"osu!{interaction.client.user.display_name.lower()}":
                await w.edit(name=interaction.client.user.display_name.lower())
            return w
    
    time.sleep(0.2)
    return await interaction.channel.create_webhook(name=f"osu!{interaction.client.user.display_name.lower()}",avatar=requests.get("https://media.discordapp.net/attachments/1094384364533600256/1103812782689886278/osuxyn.png").content)


class osu(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/recent
    @app_commands.command(name="recent",description="Shows the most recent plays of an user!")
    @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    async def recent(self, interaction: discord.Interaction, user:str,mode:Optional[Literal["osu!","osu!taiko","osu!catch","osu!mania"]]):        
        if interaction.guild:
            await interaction.response.send_message(f"{await loading_emoji(interaction)} osu!{self.bot.user.display_name} is thinking...",silent=True)
            webhook = await osu_webhook(interaction)
        else:
            await interaction.response.defer(thinking=True)

        user = api.user(user)
        if not mode:
            mode = user.playmode
            scores = api.user_scores(user,"recent",include_fails=False,limit=5)
        else:
            if mode != "osu!":
                search_mode = re.sub("osu!","",mode)
            else:
                search_mode = re.sub("!","",mode)
            scores = api.user_scores(user,"recent",mode=search_mode,include_fails=False,limit=5)

        embed = discord.Embed(title=f"{get_flag(code=user.country_code)}: {user.username}").set_author(name=f"Recent {mode} plays from:").set_thumbnail(url=user.avatar_url)

        for s in range(len(scores)):
            language = scores[s].beatmap.beatmapset().language["name"]
            flag = get_flag(language=language)
            embed.add_field(name=f"{flag} {scores[s].beatmap.beatmapset().title} ({scores[s].beatmap.version}) * [{scores[s].beatmap.difficulty_rating}⭐]",value=f"{'{:,.0f}'.format(scores[s].score)} / {0 if not scores[s].pp else scores[s].pp}pp / {round(scores[s].accuracy * 100, 2) / 1}% {'' if  str(scores[s].mods) == 'NM' else scores[s].mods}",inline=False)

        #message = await interaction.followup.send(f"{interaction.user.name} used /osu recent",silent=True)
        if interaction.guild:
            await interaction.delete_original_response()
            await webhook.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)

    #/background
    @app_commands.command(name="background",description="Shows a random seasonal background from osu!")
    async def seasonal_background(self, interaction: discord.Interaction):
        if interaction.guild:
            webhook = await osu_webhook(interaction)
            await interaction.response.send_message(f"{await loading_emoji(interaction)} osu!{self.bot.user.display_name} is thinking...",silent=True)
            #await interaction.response.send_message(f"<a:https://cdn.discordapp.com/emojis/1103271887158640651.gif?v=1>  {webhook.name} is thinking...",silent=True)
        else:
            await interaction.response.defer(thinking=True)
        
        backgrounds = api.seasonal_backgrounds()
        
        if interaction.guild:
            await interaction.delete_original_response()
            await webhook.send(random.choice(backgrounds.backgrounds).url)
        else:
            await interaction.followup.send(random.choice(backgrounds.backgrounds).url)

    #/profile
    @app_commands.command(name="profile",description="Shows the specified user's osu!profile page!")
    @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    async def profile(self,interaction: discord.Interaction, user:str):
        if interaction.guild:
            webhook = await osu_webhook(interaction)
            await interaction.response.send_message(f"{await loading_emoji(interaction)} osu!{self.bot.user.display_name} is thinking...",silent=True)
        else:
            await interaction.response.defer(thinking=True)
        
        user = api.user(user)

        if not user.profile_colour:
            accent_color = imagetools.get_accent_color(image=user.avatar_url)
        else:
            accent_color = user.profile_colour
        
        embed = discord.Embed(title=f"{get_flag(code=user.country_code)}{':robot:' if user.is_bot else ''} {':crown:' if user.is_admin else ''} {':x:' if user.is_deleted else ''} {user.username} {':green_circle:' if user.is_online else ':red_circle:'}",color=discord.Color.from_str(accent_color)).set_thumbnail(url=user.avatar_url).set_image(url=user.cover_url)

        fields = {
            "Followers:": '{:,}'.format(user.follower_count),
            "Rank:": f"# {'{:,}'.format(user.rank_history.data[-1])}" if user.rank_history else None,
            "Playmode:": f"[{user.playmode}]({osu_wiki_urls.gamemodes[user.playmode]})" if user.playmode else None,
            "Playstyle:": re.sub("\|", ", ", str(user.playstyle.name).title()) if user.playstyle else None,
            "Location": user.location,
            "Occupation": user.occupation,
            "Interests": user.interests,
            "Twitter": f"[@{user.twitter}](https://twitter.com/{user.twitter})" if user.twitter else None,
            "Discord": f"[{user.discord}](https://discord.com/users/{user.discord})" if user.discord else None
        }

        for name, value in fields.items():
            if value:
                if value != "None":
                    embed.add_field(name=name, value=value)


        if interaction.guild:
            await interaction.delete_original_response()
            await webhook.send(embed=embed)
        else:
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    print("osu! was loaded!")
    await bot.add_cog(osu(bot))