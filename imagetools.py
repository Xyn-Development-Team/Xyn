from PIL import ImageDraw, Image, ImageFont, ImageFilter, ImageEnhance
from PIL import __version__ as pil_ver
PILLOW_VERSION = tuple([int(_) for _ in pil_ver.split(".")[:3]])

import requests
from io import BytesIO
import re

import time
import random

class effects:
    def invert(img,force=1):
        invert = ImageEnhance.Contrast().enhance(int(f"-{force}"))

def draw_center_text(
    image,
    xy,
    # args shared by ImageDraw.textsize() and .text()
    text,
    font=None,
    spacing=4,
    direction=None,
    features=None,
    language=None,
    stroke_width=0,
    # ImageDraw.text() exclusive args
    **kwargs,
):
    """
    Draw center middle-aligned text. Basically a backport of 
    ImageDraw.text(..., anchor="mm"). 

    :param PIL.Image.Image image:
    :param tuple xy: center of text
    :param unicode text:
    ...
    """
    draw = ImageDraw.Draw(image)
    # Text anchor is firstly implemented in Pillow 8.0.0.
    if PILLOW_VERSION >= (8, 0, 0):
        kwargs.update(anchor="mm")
    else:
        kwargs.pop("anchor", None)  # let it defaults to "la"
        if font is None:
            font = draw.getfont()
        # anchor="mm" middle-middle coord xy -> "left-ascender" coord x'y'
        # offset_y = ascender - top, https://stackoverflow.com/a/46220683/5101148
        # WARN: ImageDraw.textsize() return text size with offset considered.
        w, h = draw.textsize(
            text,
            font=font,
            spacing=spacing,
            direction=direction,
            features=features,
            language=language,
            stroke_width=stroke_width,
        )
        offset = font.getoffset(text)
        w, h = w - offset[0], h - offset[1]
        xy = (xy[0] - w / 2 - offset[0], xy[1] - h / 2 - offset[1])
    draw.text(
        xy,
        text,
        font=font,
        spacing=spacing,
        direction=direction,
        features=features,
        language=language,
        stroke_width=stroke_width,
        **kwargs,
    )

def get_image(image,resize=False,size=(300,300)):
    """Checks if the pfp is a url and if so, loads it locally, else it tries to load from a path
    ## pfp
    Can be either a url or a string containing the path to such file
    ## resize
    Defines if you want to resize the image to the size contained in the next argument `size`
    ## size
    If `resize` is True, it will simply resite to this size, it's type is a `tuple!`"""
    if image:
        if any(["https://" in image]):
            response = requests.get(image)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image)
        image = image.convert("RGBA")
        if resize:
            return image.resize(size)
        else:
            return image

def rip(id,username:str,description:str,pfp):
    """Generates the image of a tombstone with a pfp, name and description "engraved" in it!
    ## id
    Discord's user id, but if you're not operating with ID's, treat this as the filename!
    ## username
    This is the "name" of the person who's supposed to be, y'know... dead, it's the text on top, with a bigger size, such as a title
    ## description
    This should also be kinda self-explanatory, that's the bottom text, maybe with a funny quote?? The sky is the limit, or rather 72 characters... -_-
    If you put more than 72, expect some very weird text
    """
    #Load the pfp
    pfp = get_image(pfp,resize=True)

    #Load the background
    tombstone = Image.open("./assets/tombstone.png")

    #Creates a layer for the text
    text_layer = Image.new('RGBA', tombstone.size)

    #Define the fonts
    name_font = ImageFont.truetype(r'./assets/fonts/Roboto-Regular.ttf', 50)
    description_font = ImageFont.truetype(r'./assets/fonts/Roboto-Regular.ttf', 35)

    #Draw the name and description
    draw_center_text(text_layer,xy=[600,140],text=username,font=name_font,fill="white",stroke_fill="black",stroke_width=3,align="center")
    draw_center_text(text_layer,xy=[600,540],text=re.sub("(.{35})", "\\1-\n", description, 0, re.DOTALL),font=description_font,fill="white",stroke_fill="black",stroke_width=3,align="center")

    #Applies the embossed effect to the layers and paste them into the background
    
    text_layer = text_layer.filter(ImageFilter.EMBOSS)
    pfp = pfp.filter(ImageFilter.EMBOSS)

    tombstone.paste(pfp,[455,200],pfp)
    tombstone.paste(text_layer,text_layer)

    #Fixes the lack of color in the image after pasting the embossed text
    tombstone = ImageEnhance.Contrast(tombstone).enhance(2)
    
    tombstone.save(f"./temp/{id} {time.strftime('%H %M %S rip')}.png") 
    return f"./temp/{id} {time.strftime('%H %M %S rip')}.png"

def draw_text_with_soft_shadow(image, position=(0,0,0), text="", font=ImageFont, text_color=(0,0,0), shadow_color=(0,0,0,128), shadow_offset=(0,10)):
    # Create images for shadow and text
    shadow_image = Image.new('RGBA', image.size)
    text_image = Image.new('RGBA', image.size)

    # Draw shadow
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.text((position[0] + shadow_offset[0], position[1] + shadow_offset[1]), text, font=font, fill=shadow_color)
    shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(3))

    # Draw text
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text(position, text, font=font, fill=text_color)

    # Composite the shadow and text images
    result_image = Image.alpha_composite(image, shadow_image)
    result_image = Image.alpha_composite(result_image, text_image)

    return result_image

def achievement(id,name:str,description:str,platform:str,image):
    def xbox360(name,**kwargs):
        bg = Image.open("./assets/x360achievement.png")
        font = ImageFont.truetype(r"./assets/fonts/NotoSans-Medium.ttf",79)

        draw = ImageDraw.Draw(bg)
        draw.text([425,200],f"{random.randint(0,999)}G - {name}",font=font)

        bg.save(f"./temp/{id} {time.strftime('%H %M %S Xbox360 Achievement')}.png")
        return f"./temp/{id} {time.strftime('%H %M %S Xbox360 Achievement')}.png"

    def steam(image,name,description):
        image = get_image(image,True,[400,400])

        if not image:
            image = Image.open("./assets/SteamLogo.png").resize([400,400])

        bg = Image.open("./assets/SteamAchievement.png")
        final_image = Image.new("RGBA",[bg.width,bg.height])
        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-SemiBold.ttf",95)
        description_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Medium.ttf",103)

        draw = ImageDraw.Draw(bg)

        draw.text([480,150],name,font=name_font)
        
        if description:
            draw.text([480,280],description,font=description_font)

        final_image.paste(image,[40,70])
        final_image.paste(bg,mask=bg)

        final_image.save(f"./temp/{id} {time.strftime('%H %M %S Steam Achievement')}.png")
        return f"./temp/{id} {time.strftime('%H %M %S Steam Achievement')}.png"

    def playstation5(image,name,*args,**kwargs):
        trophy = Image.open(f"./assets/{random.choice(random.sample(['Bronze','Silver','Gold','Platinum'],3))}Trophy.png").resize([150,180])

        image = get_image(image,True,[550,550])
        
        if not image:
            image = Image.open("./assets/PlaystationLogo.png").resize([550,550])

        bg = Image.open("./assets/PS5Achievement.png")
        bg.paste(image,[150,150])
        bg.paste(trophy,[840,220],trophy)
        draw = ImageDraw.Draw(bg)

        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Regular.ttf",160)

        draw.text([1000,200],name,font=name_font)
        
        bg.save(f"./temp/{id} {time.strftime(f'%h %M %S PS5Trophy')}.png")
        return f"./temp/{id} {time.strftime(f'%h %M %S PS5Trophy')}.png"

    def playstation4(image,name,*args,**kwargs):
        trophy = Image.open(f"./assets/{random.choice(random.sample(['Bronze','Silver','Gold','Platinum'],3))}Trophy.png").resize([70,80])

        image = get_image(image,True,[250,250])

        if not image:
            image = Image.open("./assets/PlaystationLogo.png").resize([250,250])

        bg = Image.open("./assets/PS4Achievement.png")
        bg.paste(image,[240,120])
        bg.paste(trophy,[550,270],trophy)
        draw = ImageDraw.Draw(bg)

        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Light.ttf",78)

        draw.text([640,250],name,font=name_font,fill="black")
        
        bg.save(f"./temp/{id} {time.strftime(f'%h %M %S PS4Trophy')}.png")
        return f"./temp/{id} {time.strftime(f'%h %M %S PS4Trophy')}.png"

    def playstation3(image,name,*args,**kwargs):
        trophy = Image.open(f"./assets/{random.choice(random.sample(['Bronze','Silver','Gold','Platinum'],3))}Trophy.png").resize([70,80])

        image = get_image(image,True,[280,280])

        if not image:
            image = Image.open("./assets/PlaystationLogo.png").resize([280,280])

        bg = Image.open("./assets/PS3Achievement.png")
        bg.paste(image,[100,350])
        bg.paste(trophy,[400,470],trophy)
        draw = ImageDraw.Draw(bg)

        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Medium.ttf",71)
        draw_text_with_soft_shadow(bg,(470,460),name,name_font,text_color=(255,255,255),shadow_color=(0,0,0,128),shadow_offset=(0,8)).show()
        
        bg.save(f"./temp/{id} {time.strftime(f'%h %M %S PS3Trophy')}.png")
        return f"./temp/{id} {time.strftime(f'%h %M %S PS3Trophy')}.png"

    def osu(image,name,description):
        image = get_image(image,True,[200,200])
        if not image:
            image = Image.open("./assets/osu!background.png").resize([200,200])

        final_image = Image.new("RGBA",[1600,900])

        badge_bg = Image.open("./assets/osu!medal.png")
        
        name_font = ImageFont.truetype(r"./assets/fonts/Inter-Bold.ttf",32)
        description_font = ImageFont.truetype(r"./assets/fonts/Inter-Medium.ttf",25)

        #Draw all the text
        draw_center_text(badge_bg,[830,560],name,name_font)
        if description:
            draw_center_text(badge_bg,[830,600],description,description_font,fill="cyan")

        #Paste everything together
        final_image.paste(image,[730,250])
        final_image.paste(badge_bg,[0,0],mask=badge_bg)

        final_image.save(f"./temp/{id} {time.strftime('%H %M %S osu!medal')}.png")
        return f"./temp/{id} {time.strftime('%H %M %S osu!medal')}.png"

    platforms = {
        "Xbox360":xbox360,
        "xbox":None,
        "Playstation 5":playstation5,
        "Playstation 4":playstation4,
        "Playstation 3":playstation3,
        "Steam":steam,
        "osu!":osu
    }
    
    platform_callback = platforms.get(platform)
    if platform_callback:
        return platform_callback(image=image, name=name, description=description)
    else:
        raise Exception("Unsupported platform!")


def quote(id,username:str,quote:str,pfp):
    pfp = get_image(pfp)
    pfp = pfp.resize([1200,1200])

    bg = Image.open("./assets/quote_bg_base.png")
    gradient = Image.open("./assets/quote_bg_gradient.png")

    pfp.putalpha(180)

    bg.paste(pfp,[0,0],pfp)
    bg.paste(gradient,gradient)

    font = ImageFont.truetype(r'./assets/fonts/Roboto-Regular.ttf', 45)
    formatted_text = re.sub("(.{35})", "\\1-\n", quote, 0, re.DOTALL)
    draw_center_text(bg,[1550,350],f""" "{formatted_text}" """,font)

    draw = ImageDraw.Draw(bg)

    #draw.rectangle(((1450, 800), (1650, 830)), fill=accent_color)
    
    font2 = ImageFont.truetype(r'./assets/fonts/Roboto-Regular.ttf', 30)
    draw_center_text(bg,[1550,800],f"- {username}, {time.strftime('%Y')}",font2)

    bg.save(f"./temp/{id} {time.strftime('%H %M %S quote')}.png")
    return f"./temp/{id} {time.strftime('%H %M %S quote')}.png"


if __name__ == "__main__":
    achievement(id=69,name="Missed the fucking point, UwU",description="You finally did it! Great job!",platform="playstation3",image="https://cdn.discordapp.com/avatars/1052773724501323788/4197174342e2ec66fdb47ccc2503fc1a.png?size=1024")
