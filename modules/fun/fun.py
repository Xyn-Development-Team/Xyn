class module:
    name = "Fun"
    cog_name = "fun"
    description = "Lot's of fun commands!"
    author = "XDT (Xyn Development Team)"
    xyn_version = "latest"

import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional, Union

import random
import requests
import roleplay
import time
from icrawler.builtin import GoogleImageCrawler
import shutil
import guild_settings as gs
import user_settings as us
import os

import imagetools
from PIL import Image, ImageFilter, ImageFont, ImageDraw, ImageEnhance

#Confession modal
class Confession(discord.ui.Modal,title="Confession"):
    user_title = discord.ui.TextInput(
        label="Title",
        placeholder="Insert a nice title to your confession",
        max_length=40
    )

    confession = discord.ui.TextInput(
        label="Confession",
        placeholder="Type your confession here...",
        style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            description=self.confession.value,
            color=discord.Color.random(),
        )
        confessions = gs.read(interaction.guild_id,option="confessions",default=0)
        gs.set(interaction.guild_id,option="confessions",value=confessions+1)
        embed.title = f"Confession #{confessions+1} {self.user_title.value}"
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Your confession has been posted successfully!",ephemeral=True)

class fun(commands.GroupCog, name=module.cog_name):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

        pfp_context_menu = app_commands.ContextMenu(
            name="Quote this!",
            callback=self.quote_menu,
        )
        self.bot.tree.add_command(pfp_context_menu)
    
    #Context Menu
    async def quote_menu(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(thinking=True)
        image = imagetools.quote(message.author.id,message.author.display_name,message.content,message.author.display_avatar.url)
        await interaction.followup.send(file=discord.File(image))
        os.remove(image)

    #/uselessfacts
    @app_commands.command(name="uselessfacts",description="| Fun | Sends a random useless fact")
    async def uselessfacts(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"\"{requests.get('https://useless-facts.sameerkumar.website/api').json()['data']}\"")

    #This API was suspended, temporarily disabling this until new solution is implemented
    # #/animequote
    # @app_commands.command(name="animequote",description="| Fun | Gets a random quote from a random anime")
    # async def animequote(self, ctx:discord.Interaction):
    #     r = requests.get("https://animechan.vercel.app/api/random")
    #     content = r.json()
    #     anime = content["anime"]
    #     character = content["character"]
    #     quote = content["quote"]

    #     emb = discord.Embed(title=f"{anime}",description=f"From: {character}")
    #     emb.add_field(name="Says:",value=f"\"{quote}\"")

    #     foldername = str(time.strftime('%H')) + str(time.strftisername:Optional[str], pfp:Optional[discord.Attachment],message:str,last_pfp:Optional[Literal["Yes","No"]]
    #             photo = discord.File(f"./{foldername}/000001.png",filename="000001.png")
    #             emb.set_thumbnail(url=f"attachment://000001.png")
    #         except:
    #             photo = discord.File(f"./{foldername}/000001.jpg",filename="000001.jpg")
    #             emb.set_thumbnail(url=f"attachment://000001.jpg")
    #     except IndexError:
    #         photo = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fcdn.onlinewebfonts.com%2Fsvg%2Fimg_355542.png&f=1&nofb=1"
    #     await ctx.followup.send(file=photo,embed=emb)
    #     shutil.rmtree(f"./{foldername}")

    #/local_persona
    @app_commands.command(name="local_persona",description="""Allows you to send a message as "another user" """)
    @app_commands.describe(user="Who do you want to impersonate?",message="""What do you want "them" to say?""")
    async def local_persona(self, interaction: discord.Interaction, user:discord.User, message:str):
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")
        
        await interaction.response.send_message(f"{interaction.client.user.name} is thinking...",ephemeral=True)

        time.sleep(0.2)
        webhook = await interaction.channel.create_webhook(name=user.display_name,avatar=requests.get(user.display_avatar.url).content)

        await webhook.send(message)
        await interaction.delete_original_response()
        await webhook.delete()

    #/persona
    @app_commands.command(name="persona",description="Allows you to send a message as someone completely different, with a BOT tag at the username :3")
    @app_commands.describe(username="Which username do you want to use?",pfp="Keep the file size less than 8MB, it'll use this as a profile picture",message="What do you want to say?",last_pfp="Do you want to reuse the last pfp?")
    async def persona(self, interaction: discord.Interaction, username:Optional[str], pfp:Optional[discord.Attachment],message:str,last_pfp:Optional[Literal["Yes","No"]]):
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")

        await interaction.response.send_message(f"{interaction.client.user.name} is thinking...",ephemeral=True)
        
        if username:
            us.set(interaction.user.id,"persona_last_username",username)
        else:
            username = us.read(interaction.user.id,"persona_last_username")
        if not username:
            await interaction.delete_original_response()
            return await interaction.channel.send("Your previous username is either invalid or doesn't exist anymore @_@\nPlease insert a username!",ephemeral=True)
        
        if pfp:
            us.set(interaction.user.id,"persona_last_pfp",pfp.url)
            time.sleep(0.2)
            webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(pfp.url).content)
        else:
            if last_pfp == "No":
                webhook = await interaction.channel.create_webhook(name=username)
            else:
                try:
                    webhook = await interaction.channel.create_webhook(name=username,avatar=requests.get(str(us.read(interaction.user.id,option="persona_last_pfp"))).content)
                except:
                    await interaction.delete_original_response()
                    return await interaction.followup.send("Your previous pfp is either invalid or doesn't exist anymore @_@",ephemeral=True)

        await interaction.delete_original_response()

        await webhook.send(message)
        await webhook.delete()

    #/arrest
    @app_commands.command(name="arrest",description="Put someone in jail")
    async def arrest(self, interaction: discord.Interaction, user:discord.User, reason:Optional[str]):
        await user.display_avatar.save(f"./temp/{user.id}.png")
        pfp = Image.open(f"./temp/{user.id}.png")

        jail = Image.open("./assets/jail_bars.png")

        jail.resize(pfp.size)
        pfp.paste(jail,mask=jail)

        filename = f"./temp/{user.id} {time.strftime('%H %M %S arrest')}.png"
        pfp.save(filename)
        jail.close()
        pfp.close()

        if reason:
            await interaction.response.send_message(f"<@{interaction.user.id}> arrested <@{user.id}> for {reason}!",file=discord.File(f"./temp/{user.id} {time.strftime('%H %M %S arrest')}.png"))
        else:
            await interaction.response.send_message(f"<@{interaction.user.id}> arrested <@{user.id}>!",file=discord.File(filename))
        os.remove(filename)

    #/rip
    @app_commands.command(name="rip",description="| Fun | It's dead Jim")
    @app_commands.describe(user="Who?",description="Ex: His last words were, I like ass, [Limited to 71 characters!]")
    async def rip(self,interaction: discord.Interaction, user:discord.User,description:Optional[app_commands.Range[str,1,71]]):
        await interaction.response.defer(thinking=True)
        image = imagetools.rip(user.id,user.display_name,description,user.display_avatar.url)
        await interaction.followup.send(file=discord.File(image))
        os.remove(image)

    #/quote
    @app_commands.command(name="quote",description="| Fun | Someone said something quite poetic, huh?")
    @app_commands.describe(user="Who's the poetic menace?",quote="What was it?")
    async def quote(self,interaction: discord.Interaction, user:discord.User, quote:str):
        await interaction.response.defer(thinking=True)
        image = imagetools.quote(user.id,user.display_name,quote,user.display_avatar.url)
        await interaction.followup.send(file=discord.File(image))
        os.remove(image)

    #/achievement
    @app_commands.command(name="achievement",description="| Fun | Someone has got an achievement, cool!")
    @app_commands.describe(image="(Optional) What's the picture for this achievement?",pfp="(Optional) Use someone's pfp as a picture for this achievement",name="What's the name of this achievement? [Limited to 24 characters!]",description="What is this achievement about? (Only works on supported images) [Limited to 32 characters!]")
    async def achievements(self, interaction:discord.Interaction,image:Optional[discord.Attachment], pfp:Optional[discord.User], name:app_commands.Range[str,1,24], description:Optional[app_commands.Range[str,1,32]],platform:Literal["Xbox360","Playstation 5","Playstation 4", "Playstation 3", "Steam", "osu!"]):
        await interaction.response.defer(thinking=True)
        if image and not pfp:
            image = image.url
        if pfp:
            image = pfp.display_avatar.url
        image = imagetools.achievement(interaction.user.id,name,description,platform,image)
        await interaction.followup.send(file=discord.File(image))
        os.remove(image)

    #/diceroll
    @app_commands.command(name="diceroll", description="| Fun | Rolls a dice for you")
    @app_commands.describe(dice="What type of dice do you want to roll?")
    async def diceroll(self, ctx: discord.Interaction, dice: Literal["D6","D20"]):
        if dice == "D6":
            result = random.randint(0, 5)
            sides = ["https://cdn.discordapp.com/emojis/1018347458897645629.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347460982218792.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347463259738142.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347465352687707.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347467621806090.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018347470251626576.webp?quality=lossless"]
        elif dice == "D20":
            sides = ["https://cdn.discordapp.com/emojis/1018361716490379284.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361718197465128.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361719808065586.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361721087348797.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361723163512862.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361724899950604.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361726623821824.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361728305745980.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361729920532511.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361731686354986.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361733636698203.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361735540920390.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361737218621471.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361738791493693.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361740540522506.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361742314709033.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361744223121478.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361746190237716.webp?&quality=lossless","https://cdn.discordapp.com/emojis/1018361748165767238.webp?quality=lossless","https://cdn.discordapp.com/emojis/1018361750023839784.webp?&quality=lossless"]
            result = random.randint(0, 19)
        roll = sides[result]
        dice_number = result+1
        emb = discord.Embed(title=f"{ctx.user.display_name}",description=f"Rolled a **{dice_number}!**")
        emb.set_thumbnail(url=str(roll))
        await ctx.response.send_message(embed=emb)

    #/coinflip
    @app_commands.command(name="coinflip",description="| Fun | Flips a coin")
    async def coinflip(self, ctx: discord.Interaction):    
        result = random.randint(0,1)
        if result == 0:
            coin = "Heads"
        elif result == 1:
            coin = "Tails"
        coins = ["https://cdn.discordapp.com/emojis/1085660740800757902.webp","https://cdn.discordapp.com/emojis/1085660744592396400.webp"]
        emb = discord.Embed(title=f"{ctx.user.display_name}",description=f"It landed on **{coin}!**")
        emb.set_thumbnail(url=str(coins[result]))
        await ctx.response.send_message(embed=emb)

    #/roleplay
    @app_commands.command(name="roleplay",description="| Fun | Let's you roleplay using anime gifs")
    @app_commands.describe(action="What do you want to do?",together="With/To who do you want to do this?")
    async def roleplay(self, interaction: discord.Interaction, action:Literal["Slap","Kiss","Hug","Sleep","Punch","Cuddle","Blush","Pat","Smug","Poke","Run","Stare"], together:discord.User=None):
        try:
            image_request = requests.get(f"https://api.otakugifs.xyz/gif?reaction={action.lower()}")
            response = image_request.json()
            image = response["url"]
        except:
            image = "https://pbs.twimg.com/media/DKs2G92X0AEjh3Z.jpg"
        if together:
            emb = discord.Embed(description=roleplay.better_roleplay(action.lower(),interaction,target=f"<@{together.id}>"))
        else:
            emb = discord.Embed(description=roleplay.better_roleplay(action.lower(),interaction))
        emb.set_image(url=str(image))
        await interaction.response.send_message(embed=emb)

    #/confess
    @app_commands.command(name = "confess", description = "| Fun | Let's you make a completely anonymous confession")
    async def confess(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message("This command doesn't work outside of a guild!")
        await interaction.response.send_modal(Confession())

async def setup(bot: commands.Bot) -> None:
    print("fun was loaded!")
    await bot.add_cog(fun(bot))