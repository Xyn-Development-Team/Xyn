class module:
    name = "Scraping"
    cog_name = "scraping"
    description = "Commmands to scrape images from other user profiles or some famous websites"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Literal
from typing import Optional

import requests
import re

from pygelbooru import Gelbooru
import os
from dotenv import load_dotenv
load_dotenv()
import time
import json
import random
import imagetools
import settings

#Define gelbooru with its credentials
gelbooru = Gelbooru(os.getenv("gelbooru_api_key"), os.getenv("gelbooru_user_id"))

#Gets reddit posts with the defined boundaries
def get_reddit(subreddit,count,listing,timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?count={count}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'Xyn'})
    except:
        print('An Error Occured')
        raise Exception("Error getting the sub")
    return request.json()

class steam_cog(commands.GroupCog,name="steam"):
    def __init__(self, bot: commands.Bot) -> None:
        import modules.scraping.steam as steam
        self.bot = bot
        print("scraping.steam was loaded!")
        super().__init__()
        
    @app_commands.command(name="game",description="Shows info about a Steam game and it's price on a selected currency")
    async def game(self, interaction: discord.Interaction, name:Optional[str], app_id:Optional[int], currency:Optional[str]):
        if not name and not app_id:
            return await interaction.response.send_message("Please specify a game!",ephemeral=True)

        if currency != None and not currency in steam.currency_language_mapping:
            return await interaction.response.send_message("Invalid currency! Please refer to the ISO-4217 currency codes\nhttps://en.wikipedia.org/wiki/ISO_4217",ephemeral=True)
  
        await interaction.response.defer(thinking=True)
        
        game = steam.game(app_id,currency,name)
        
        if not game:
            return await interaction.followup.send("Please specify a valid game!",ephemeral=True)
        
        embed = discord.Embed(color=discord.Color.from_str(imagetools.get_accent_color(game["banner"])),title=game["title"],url=game["game_url"],description=f"{game['description']}").set_image(url=game["banner"])
        
        fields = {"Price":game["price"],
                  "Developer":f"[{game['developer']}]({game['developer_url']})",
                  "Publisher":f"[{game['publisher']}]({game['publisher_url']})" if game["publisher"] != game["developer"] else None,
                  "Genre":f"[{game['genre']}]({game['genre_url']})",
                  "Release date":game["release_date"]
        }
        
        for name, value in fields.items():
            if value:
                if value != "None":
                    embed.add_field(name=name, value=value)
        
        await interaction.followup.send(embed=embed)

    #Unfinished
    # @app_commands.command(name="profile",description="Shows info on a specified user")
    # async def profile(self, interaction: discord.Interaction, id:str):
    #     await interaction.response.defer(thinking=True)
        
    #     profile = steam.profile(id)
        
    #     embed = discord.Embed(color=discord.Color.from_str(imagetools.get_accent_color(profile["pfp"])),title=profile["username"],description=profile["summary"]).set_thumbnail(url=profile["pfp"]).set_author(name=id,url=f"https://steamcommunity.com/id/{id}/")
        
    #     await interaction.followup.send(embed=embed)

class scr(commands.GroupCog, name="scraping"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

        pfp_context_menu = app_commands.ContextMenu(
            name="Get user's pfp",
            callback=self.menu_get_pfp,
        )
        self.bot.tree.add_command(pfp_context_menu)

        banner_context_menu = app_commands.ContextMenu(
            name="Get user's banner",
            callback=self.menu_get_banner,
        )
        self.bot.tree.add_command(banner_context_menu)

    #Context Menu
    async def menu_get_pfp(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.send_message(user.display_avatar.url,ephemeral=True)

    #Context Menu
    async def menu_get_banner(self,interaction: discord.Interaction, user: discord.Member):
        user = await self.bot.fetch_user(user.id)
        try:
            await interaction.response.send_message(user.banner.url,ephemeral=True)
        except:
            await interaction.response.send_message(f"The user: <@{user.id}> Doesn't have a banner!",ephemeral=True)


    #/pfp
    @app_commands.command(name="pfp",description="Gets a user's server pfp")
    async def get_pfp(self, interaction: discord.Interaction, user: discord.User, silent:Optional[Literal["Yes","No"]]):
        await interaction.response.send_message(user.display_avatar.url,ephemeral=True) if silent and silent.lower() == "yes" else await interaction.response.send_message(user.display_avatar.url)

    #/banner
    @app_commands.command(name="banner",description="Gets a user's server banner")
    async def get_banner(self, interaction: discord.Interaction, user: discord.User, silent:Optional[Literal["Yes","No"]]):
        user = await self.bot.fetch_user(user.id)
        await interaction.response.send_message(user.banner.url,ephemeral=True) if silent and silent.lower() == "yes" else await interaction.response.send_message(user.banner.url)

    #/reddit
    @app_commands.command(name="reddit",description="| Scraping | Gets a random post from a subreddit")
    async def reddit(self, interaction: discord.Interaction, subreddit: str,) -> None:
        subreddit = subreddit = re.sub("r/","",subreddit)
        try:
            top_post = get_reddit(subreddit,count=1,listing="random",timeframe="all")
        except Exception("Error getting the sub"):
            await interaction.response.send_message("There was an error fetching from this subreddit, check your spelling and/or try again later")
            return
        try:
            title = top_post[0]['data']['children'][0]['data']['title']
            url = top_post[0]['data']['children'][0]['data']['url']
        except KeyError:
            await interaction.response.send_message("This subreddit wasn't found, are you sure you spelled it correctly?")
            return
        
        await interaction.response.send_message(f'{title}\n{url}')

    #/gelbooru
    @app_commands.command(name="gelbooru",description="| Scraping | Gets a random image from the specified tags on Gelbooru")
    async def gelbooru(self, interaction: discord.Interaction, tags: str, ignore_tags: Optional[str], safe_mode:Literal["Yes","No"]) -> None:
        await interaction.response.defer(ephemeral=False,thinking=True)
        channel = interaction.channel
        tags = tags.split(",")
        if ignore_tags != None:
            exclude_tags = ignore_tags.split(",")
            exclude_tags_string = exclude_tags[0]
            if exclude_tags_string == "" or None:
                exclude_tags_string = None
        else:
            exclude_tags = None
            exclude_tags_string = ""
        if safe_mode == "No":
            if interaction.guild and not channel.is_nsfw():
                await interaction.followup.send("The Safe Mode can only be turned off in a NSFW channel!")
            else:
                result = await gelbooru.search_posts(tags=tags,exclude_tags=exclude_tags_string)
                result = random.choice(result)
                await interaction.followup.send(result)
        elif safe_mode == "Yes":
            async def safe_gelbooru():
                result = await gelbooru.search_posts(tags=tags,exclude_tags=exclude_tags_string)
                result = random.choice(result)
                
                filename = str(time.strftime('%H')) + str(time.strftime('%M')) + str(time.strftime('%S')) + ".png"
                img_data = requests.get(result).content
                with open(filename, 'wb') as handler:
                    handler.write(img_data)
                f = open(filename,"rb")

                headers = {"Authorization": f"Authorization: Bearer {os.getenv('edenai_token')}"}

                url=" https://api.edenai.run/v2/image/explicit_content"
                data={"providers": "api4ai"}
                files = {'file': f}

                response = requests.post(url, data=data, files=files, headers=headers)

                response = json.loads(response.text)
                try:
                    lewd = int(response["api4ai"]["items"][0]["likelihood"])
                except:
                    await safe_gelbooru()
                    return
                if lewd > 3:
                    f.close()
                    try:
                        os.remove(filename)
                    except PermissionError:
                        time.sleep(5)
                        os.remove(filename)
                    await safe_gelbooru()
                    return
                else:
                    await interaction.followup.send(result)
                time.sleep(5)
                f.close()
                try:
                    f.close()
                    os.remove(filename)
                except PermissionError:
                    try:
                        time.sleep(5)
                        f.close()
                    except PermissionError:
                        try:
                            os.remove(filename)
                        except PermissionError:
                            pass
                return

            await safe_gelbooru()
            return

async def setup(bot: commands.Bot) -> None:
    print("Scraping was loaded!")
    await bot.add_cog(scr(bot))
    try:
        if settings.modules["scraping.steam"]:
            await bot.add_cog(steam_cog(bot))
    except KeyError:
        print("[modules.scraping WARNING]scraping.steam wasn't added to your module settings, so it'll remain disabled!")