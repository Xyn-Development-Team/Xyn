import lightbulb
import hikari
from pygelbooru import Gelbooru
import re
import random
import time
import requests
import json
import os
import guild_settings as gs
from icrawler.builtin import GoogleImageCrawler
import shutil
import translators as ts
import uwuify
from dotenv import load_dotenv

scr = lightbulb.Plugin("scraping")

#Initialize Gelbooru
gelbooru = Gelbooru(os.getenv("gelbooru_api_key"), os.getenv("gelbooru_user_id"))

#Get subreddit content
def get_reddit(subreddit,count,listing,timeframe):
    try:
        base_url = f'https://www.reddit.com/r/{subreddit}/{listing}.json?count={count}&t={timeframe}'
        request = requests.get(base_url, headers = {'User-agent': 'yourbot'})
    except:
        print('An Error Occured')
        raise Exception("Error getting the sub")
    return request.json()

#/reddit
@scr.command
@lightbulb.option("subreddit","Where are we heading to? :D")
@lightbulb.option("listing","controlversial, best, hot, new, random(default), rising, top",required=False)
@lightbulb.command("reddit","Get a random post from a subreddit",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def reddit(ctx:lightbulb.SlashContext):
    subreddit = ctx.options.subreddit ; subreddit = re.sub("r/","",subreddit)
    count = 1
    timeframe = 'day' #hour, day, week, month, year, all
    listing = ctx.options.listing
    if listing == None:
        listing = "random"
    try:
        top_post = get_reddit(subreddit,count,listing,timeframe)
    except Exception("Error getting the sub"):
        await ctx.respond(gs.text('reddit_not_found',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
        return
    if listing != 'random' and listing != None:
        try:
            title = top_post['data']['children'][0]['data']['title']
            url = top_post['data']['children'][0]['data']['url']
        except KeyError:
            await ctx.respond(gs.text('reddit_not_found',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
            return
    elif listing == "random":
        try:
            title = top_post[0]['data']['children'][0]['data']['title']
            url = top_post[0]['data']['children'][0]['data']['url']
        except KeyError:
            await ctx.respond(gs.text('reddit_not_found',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)))
            return
    
    await ctx.respond(f'{title}\n{url}')

#/gelbooru
@scr.command
@lightbulb.option("content","What tags do you want to search? (Split them by using ',')",required=True)
@lightbulb.option("safe_mode","Enable Safe Mode?",choices=["Yes","No"],required=True)
@lightbulb.option("ignore","Choose tags to ignore from your results (Split them by using ',')",required=False)
@lightbulb.command("gelbooru","Search for a random image by tags on Gelbooru's website",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def gelbooru_search(ctx: lightbulb.SlashContext):
    channel = ctx.get_channel()
    tags = ctx.options.content.split(",")
    if ctx.options.ignore != None:
        exclude_tags = ctx.options.ignore.split(",")
        exclude_tags_string = exclude_tags[0]
        if exclude_tags_string == "" or None:
            exclude_tags_string = None
    else:
        exclude_tags = None
        exclude_tags_string = ""
    if ctx.options.safe_mode == "No":
        if channel.is_nsfw == None:
            await ctx.respond(gs.text('no_nsfw',gs.guild_language(ctx.guild_id),gs.get_uwu(ctx.guild_id)),flags=hikari.MessageFlag.EPHEMERAL)
        else:
            result = await gelbooru.search_posts(tags=tags,exclude_tags=exclude_tags_string)
            result = random.choice(result)
            await ctx.respond(result)
    elif ctx.options.safe_mode == "Yes":
        async def safe_gelbooru(ctx):
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
                await safe_gelbooru(ctx)
                return
            if lewd > 3:
                f.close()
                try:
                    os.remove(filename)
                except PermissionError:
                    time.sleep(5)
                    os.remove(filename)
                await safe_gelbooru(ctx)
                return
            else:
                await ctx.respond(result)
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
        await safe_gelbooru(ctx)
        return

#/anime_quote Fixed!
@scr.command
@lightbulb.command("anime_quote","Get a random anime quote!",auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def anime_quote(ctx: lightbulb.SlashContext):
    r = requests.get("https://animechan.vercel.app/api/random")
    content = r.json()
    anime = content["anime"]
    character = content["character"]
    quote = content["quote"]
    foldername = str(time.strftime('%H')) + str(time.strftime('%M')) + str(time.strftime('%S'))
    try:
        google_Crawler = GoogleImageCrawler(storage = {'root_dir': rf'{foldername}'})
        photo = google_Crawler.crawl(keyword = str(character), max_num = 1)
        try:
            photo = open(f"./{foldername}/000001.png","rb").read()
        except:
            photo = open(f"./{foldername}/000001.jpg","rb").read()
    except IndexError:
        photo = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fcdn.onlinewebfonts.com%2Fsvg%2Fimg_355542.png&f=1&nofb=1"
    if gs.guild_language(ctx.guild_id) == "English":
        if gs.get_uwu(ctx.guild_id):
            emb= hikari.Embed(title=f"{anime}",description=f"From: {character}")
            emb.add_field("Says:",f""" "{uwuify.uwu(quote,flags=uwuify.STUTTER | uwuify.YU)}" """)
        else:
            emb= hikari.Embed(title=f"{anime}",description=f"From: {character}")
            emb.add_field("Says:",f""" "{quote}" """)
    elif gs.guild_language(ctx.guild_id) == "Portuguese":
        emb= hikari.Embed(title=f"{anime}",description=f"De: {character}")
        emb.add_field("Diz:",f""" "{ts.translate_text(str(quote),translator="google",to_language="pt")}" """)
    elif gs.guild_language(ctx.guild_id) == "Japanese":
        emb= hikari.Embed(title=f"{anime}",description=f"差出人: {character}")
        emb.add_field("言う:",f""" "{ts.translate_text(str(quote),translator="google",to_language="ja")}" """)
        
    emb.set_thumbnail(photo)
    await ctx.respond(emb)
    #Delete the folder
    try:
        shutil.rmtree(f"./{foldername}")
    except PermissionError:
        time.sleep(5)
        shutil.rmtree(f"./{foldername}")

def load(bot: lightbulb.BotApp):
    load_dotenv()
    bot.add_plugin(scr)

def unload(bot):
    bot.remove_plugin(scr)
