class module:
    name = "osu!"
    cog_name = "osu"
    description = "rhythm is just a *command* away"
    author = "Moonlight Dorkreamer 🌓"
    xyn_version = "V3"
    version = "04042024"

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
    from typing import Literal
    from typing import Optional
    from os import getenv
    from dotenv import load_dotenv ; load_dotenv()
    from ossapi import Ossapi
    import random
    import storage
    import time
    import requests
    import localization
    import imagetools
    import pycountry
    import re
    import aiordr
    import settings

#Sets the credential to the API
api = Ossapi(getenv('osu_client_id'), getenv('osu_secret'))

#Starts the client
ordr = aiordr.ordrClient(verification_key=getenv("ordr_api_key"))

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
    flag = re.sub("ko","kr",flag)
    return flag


class osu_wiki_urls():
    gamemodes = {
        "osu":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21",
        "taiko":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21taiko",
        "catch":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21catch",
        "mania":"https://osu.ppy.sh/wiki/en/Game_mode/osu%21mania"
    }

class osu(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    #/replay
    @app_commands.command(name="replay",description="Renders a replay in mp4 using o!rdr! | This command has a 5 minute cooldown! |")
    @discord.app_commands.checks.cooldown(1, 300)
    @app_commands.describe(file="The .osr file for your replay!",url="A url containing your replay!",username="Your osu! username!")
    async def replay(self, interaction: discord.Interaction, file:Optional[discord.Attachment],url:Optional[str],username:str):
        if interaction.guild:
            language = storage.guild.read(interaction.guild_id,"language")
        else:
            language = str(interaction.locale).lower()

        if file:
            url = file.url
        
        if not url:
            return await interaction.response.send_message(localization.external.read("replay.no_file", language))

        await interaction.response.send_message(localization.external.read("replay.uploading",language))
        
        render = await ordr.create_render(
            username=username,
            skin="FreedomDiveBTMC",
            replay_url=url,
            resolution="1280x720"
        )
        
        @ordr.on_render_added
        async def on_render_added(event: aiordr.models.RenderAddEvent) -> None:
            if event.render_id == render.render_id:
                await interaction.edit_original_response(content=localization.external.read("replay.rendering",language))
        
        @ordr.on_render_fail
        async def on_render_fail(event: aiordr.models.RenderFailEvent) -> None:
            if event.render_id == render.render_id:
                return await interaction.edit_original_response(content=str(localization.external.read(replay.error, language)).format(event))
            
        @ordr.on_render_finish
        async def on_render_finish(event: aiordr.models.RenderFinishEvent) -> None:
            if event.render_id == render.render_id:
                return await interaction.edit_original_response(content=event.video_url)

    #/profile
    @app_commands.command(name="profile",description="Shows the specified user's osu!profile page!")
    @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    async def profile(self,interaction: discord.Interaction, user:str):
        if interaction.guild:
            language = storage.guild.read(interaction.guild_id, "language")
        else:
            language = str(interaction.locale).lower()
        await interaction.response.defer(thinking=True)
        
        user = api.search(user, mode="user") ; user = user.users.data[0].expand()

        if not user:
            user = api.user(user)
        
        if not user:
            return await interaction.followup.send(localization.external.read("no_user", language))

        if not user.profile_colour:
            accent_color = imagetools.get_average_color(image=user.avatar_url)
        else:
            accent_color = user.profile_colour

        beatmap = None
        if user.discord:
            discord_user = interaction.guild.get_member_named(user.discord)
            if discord_user.activity:
                if discord_user and discord_user.activity.name == "osu!":
                    if discord_user.activity.state == "Clicking circles":
                        mode = "osu"
                    elif discord_user.activity.state == "Smashing keys":
                        mode = "mania"
                    elif discord_user.activity.state == "Bashing drums":
                        mode = "taiko"
                    elif discord_user.activity.state == "Catching fruit":
                        mode = "catch"
                    else:
                        mode = None

                    if mode:
                        beatmap_query = discord_user.activity.details
                        beatmap = api.search_beatmapsets(query=beatmap_query, explicit_content="show").beatmapsets[0]

        if not user.profile_colour:
            average_color = imagetools.get_average_color(image=user.avatar_url)
        else:
            average_color = user.profile_colour
        
        embed = discord.Embed(title=f"{get_flag(code=user.country_code)}{':robot:' if user.is_bot else ''} {':x:' if user.is_deleted else ''} {user.username} {':green_circle:' if user.is_online else ':red_circle:'}",color=discord.Color.from_str(average_color)).set_thumbnail(url=user.avatar_url).set_image(url=user.cover_url)
        
        if beatmap:
            embed.set_author(name=str(localization.external.read(f"playing.{mode}", language)).format(beatmap=beatmap.title) if mode else None, url=f"https://osu.ppy.sh/beatmapsets/{beatmap.id}")

        fields = {
            f"{localization.external.read('profile.followers', language)}": '{:,}'.format(user.follower_count),
            f"{localization.external.read('profile.rank', language)}": f"#{'{:,}'.format(user.rank_history.data[-1])}",
            f"{localization.external.read('profile.playmode', language)}": f"[{user.playmode}]({osu_wiki_urls.gamemodes[user.playmode]})" if user.playmode else None,
            f"{localization.external.read('profile.playstyle', language)}": re.sub("\|", ", ", str(user.playstyle.name).title()) if user.playstyle else None,
            f"{localization.external.read('profile.location', language)}": user.location,
            f"{localization.external.read('profile.occupation', language)}": user.occupation,
            f"{localization.external.read('profile.interests', language)}": user.interests,
            f"{localization.external.read('profile.Twitter', language)}": f"[@{user.twitter}](https://twitter.com/{user.twitter})" if user.twitter else None,
            f"{localization.external.read('profile.Discord', language)}": f"[{user.discord}](https://discord.com/users/{user.discord})" if user.discord else None
        }

        for name, value in fields.items():
            if value:
                if value != "None":
                    embed.add_field(name=name, value=value)

        await interaction.followup.send(embed=embed)

    # API is broken :c
   #/recent
    # @app_commands.command(name="recent",description="Shows the most recent plays of an user!")
    # @app_commands.describe(user="Who do you want to check? You can use either usernames or ID's!")
    # async def recent(self, interaction: discord.Interaction, user:str,mode:Optional[Literal["osu!","osu!taiko","osu!catch","osu!mania"]]):        
    #     await interaction.response.defer(thinking=True)
    #     if interaction.guild:
    #         language = storage.guild.read(interaction.guild.id, "language")
    #     else:
    #         language = str(interaction.locale).lower()
    #     user = api.search(user,mode="user") ; user = user.users.data[0].expand()

    #     if not user.profile_colour:
    #         accent_color = imagetools.get_average_color(image=user.avatar_url)
    #     else:
    #         accent_color = user.profile_colour

    #     if not mode:
    #         mode = user.playmode
    #         scores = api.user_scores(user,"recent",include_fails=False,limit=5)
    #     else:
    #         if mode != "osu!":
    #             search_mode = re.sub("osu!","",mode)
    #         else:
    #             search_mode = re.sub("!","",mode)
    #         scores = api.user_scores(user,"recent",mode=search_mode,include_fails=False,limit=5)

    #     embed = discord.Embed(title=f"{get_flag(code=user.country_code)}: {user.username}",color=discord.Color.from_str(accent_color)).set_author(name=localization.external.read("recent_plays",language).format(mode=mode)).set_thumbnail(url=user.avatar_url)

    #     for s in range(len(scores)):
    #         language = scores[s].beatmap.beatmapset().language["name"]
    #         flag = get_flag(language=language)
    #         embed.add_field(name=f"{flag} {scores[s].beatmap.beatmapset().title} ({scores[s].beatmap.version}) * [{scores[s].beatmap.difficulty_rating}⭐]",value=f"{'{:,.0f}'.format(scores[s].score)} / {0 if not scores[s].pp else scores[s].pp}pp / {round(scores[s].accuracy * 100, 2) / 1}% {'' if  str(scores[s].mods) == 'NM' else scores[s].mods}",inline=False)

    #     #message = await interaction.followup.send(f"{interaction.user.name} used /osu recent",silent=True)
    #     await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot) -> None:
    print(localization.external.read("setup.loaded",settings.language))
    await bot.add_cog(osu(bot))