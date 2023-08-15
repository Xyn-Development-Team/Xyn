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

import httpx
from bs4 import BeautifulSoup

import modules.scraping.steam as steam

#Define gelbooru with its credentials
gelbooru = Gelbooru(os.getenv("gelbooru_api_key"), os.getenv("gelbooru_user_id"))

#Gets reddit posts with the defined boundaries
async def random_reddit(subreddit, safe_mode=True, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
            }
            async with httpx.AsyncClient() as client:
                url = f"https://www.reddit.com/r/{subreddit}/random.json?count=1&t=all"
                response = await client.get(url, headers=headers)

                if response.status_code == 302:
                    redirect_url = response.headers.get("location")
                    if redirect_url:
                        response = await client.get(redirect_url, headers=headers)

                response.raise_for_status()

                # Continue with parsing the response
                data = response.json()
                if data and isinstance(data, list):
                    post_data = data[0]['data']['children'][0]['data']
                    title = post_data['title']
                    url = post_data['url']
                    nsfw = post_data['over_18']
                    
                    if safe_mode and nsfw:
                        retries += 1
                        continue
                    
                    return {
                        'title': title,
                        'url': url,
                        'nsfw': nsfw
                    }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 302:
                print("Redirecting...")
            else:
                print(f"HTTP Error: {e}")
            retries += 1
        except Exception as e:
            print(f"Error: {e}")
            retries += 1

    return None

class steam_cog(commands.GroupCog,name="steam"):
    def __init__(self, bot: commands.Bot) -> None:
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
    async def reddit(self, interaction: discord.Interaction, subreddit: str, safe_mode:Literal["Yes","No"]) -> None:
        await interaction.response.defer(thinking=True)
        
        if safe_mode == "No":
            if interaction.guild and not interaction.channel.is_nsfw():
                return await interaction.followup.send("The Safe Mode can only be turned off in a NSFW channel!")
        
        subreddit = re.sub(r"r/", "", subreddit)
        try:
            random_post = await random_reddit(subreddit,{"Yes":True,"No":False}.get(safe_mode,True))
            if random_post:
                title = random_post['title']
                url = random_post['url']
                await interaction.followup.send(f'{title}\n{url}')
            else:
                await interaction.followup.send("No suitable posts found (NSFW filtered)")
        except KeyError:
            await interaction.followup.send("The specified subreddit wasn't found, are you sure you spelled it correctly?")

    #/gelbooru
    @app_commands.command(name="gelbooru",description="| Scraping | Gets a random image from the specified tags on Gelbooru")
    @app_commands.describe(tags="What you want to search for, split the tags by using spaces!",ignore_tags="These are the tags you don't want! Split them by using spaces!",safe_mode="Avoids any NSFW images. (Disabling it is only available on NSFW channels)")
    async def gelbooru(self, interaction: discord.Interaction, tags: str, ignore_tags: Optional[str], safe_mode:Literal["Yes","No"]) -> None:
        await interaction.response.defer(ephemeral=False,thinking=True)
        tags = tags.split(" ")
        if ignore_tags:
            exclude_tags = ignore_tags.split(" ")
        if safe_mode == "Yes":
            tags.append("rating:general")
        else:
            if interaction.guild and not interaction.channel.is_nsfw():
                return await interaction.followup.send("The Safe Mode can only be turned off in a NSFW channel!")
        result = await gelbooru.search_posts(tags=tags,exclude_tags=exclude_tags if ignore_tags else None)
        result = random.choice(result)
        await interaction.followup.send(result)

async def setup(bot: commands.Bot) -> None:
    print("Scraping was loaded!")
    await bot.add_cog(scr(bot))
    await bot.add_cog(steam_cog(bot))
