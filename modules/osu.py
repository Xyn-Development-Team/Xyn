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

#Sets the credential to the API
api = Ossapi(getenv('osu_client_id'), getenv('osu_client_secret'))

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


class osu(commands.GroupCog, name="osu"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    #/recent
    @app_commands.command(name="recent",description="Shows the most recent plays of an user!")
    @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    async def recent(self, interaction: discord.Interaction, user:str,mode:Optional[Literal["osu!","osu!taiko","osu!catch","osu!mania"]]):        
        webhook = await osu_webhook(interaction)
        await interaction.response.send_message(f"<a:osuxynloading:1103271887158640651>  {webhook.name} is thinking...",silent=True)

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
            embed.add_field(name=f"{flag} {scores[s].beatmap.beatmapset().title} ({scores[s].beatmap.version}) * [{scores[s].beatmap.difficulty_rating}⭐]",value=f"{'{:,.0f}'.format(scores[s].score)} / {0 if not scores[s].pp else scores[s].pp}pp / {round(scores[s].accuracy * 100, 2) / 1}%",inline=False)

        #message = await interaction.followup.send(f"{interaction.user.name} used /osu recent",silent=True)
        await interaction.delete_original_response()
        

        await webhook.send(embed=embed)
        await webhook.delete()

    #/background
    @app_commands.command(name="background",description="Shows a random seasonal background from osu!")
    async def seasonal_background(self, interaction: discord.Interaction):
        webhook = osu_webhook(interaction)
        await interaction.response.send_message(f"<a:osuxynloading:1103271887158640651>  {webhook.name} is thinking...",silent=True)
        
        backgrounds = api.seasonal_backgrounds()
        
        await interaction.delete_original_response()
        await webhook.send(random.choice(backgrounds.backgrounds).url)
    
    #/profile
    @app_commands.command(name="profile",description="Shows the specified user's osu!profile page!")
    @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    async def profile(self,interaction: discord.Interaction, user:str):
        webhook = await osu_webhook(interaction)
        await interaction.response.send_message(f"<a:osuxynloading:1103271887158640651>  {webhook.name} is thinking...",silent=True)
        
        user = api.user(user)
        
        embed = discord.Embed(title=f"{get_flag(code=user.country_code)}{':robot:' if user.is_bot else ''} {':crown:' if user.is_admin else ''} {':x:' if user.is_deleted else ''} {user.username} {':green_circle:' if user.is_online else ':red_circle:'}").set_thumbnail(url=user.avatar_url).set_image(url=user.cover_url)
            
        embed.add_field(name="Followers:",value=user.follower_count)
   
        if user.rank_history:
            embed.add_field(name="Rank:",value=f"{user.rank_history.data[-1]}")

        if user.playmode:
            embed.add_field(name="Playmode:",value=f"[{user.playmode}]({osu_wiki_urls.gamemodes[user.playmode]})")

        if user.playstyle:
            embed.add_field(name="Playstyle:",value=re.sub("\|",", ",str(user.playstyle.name).title()))

        if user.location:
            embed.add_field(name="Location",value=user.location)
        
        if user.occupation:
            embed.add_field(name="Occupation",value=user.occupation)

        if user.interests:
            embed.add_field(name="Interests",value=user.interests)

        if user.twitter:
            embed.add_field(name="Twitter",value=f"[@{user.twitter}](https://twitter.com/{user.twitter})")
        
        if user.discord:
            embed.add_field(name="Discord",value=f"[{user.discord}](https://discord.com/users/{user.discord})")

        await interaction.delete_original_response()
        await webhook.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(osu(bot))