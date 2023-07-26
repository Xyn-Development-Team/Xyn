from PIL import ImageDraw, Image, ImageFont, ImageFilter, ImageEnhance
from PIL import __version__ as pil_ver
PILLOW_VERSION = tuple([int(_) for _ in pil_ver.split(".")[:3]])

import requests
from io import BytesIO
import re

import time
import random

import textwrap

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
    draw_center_text(text_layer,xy=[600,540],text=textwrap.fill(description,35) if description else "",font=description_font,fill="white",stroke_fill="black",stroke_width=3,align="center")

    #Applies the embossed effect to the layers and paste them into the background
    
    text_layer = text_layer.filter(ImageFilter.EMBOSS)
    pfp = pfp.filter(ImageFilter.EMBOSS)

    tombstone.paste(pfp,[455,200],pfp)
    tombstone.paste(text_layer,text_layer)

    #Fixes the lack of color in the image after pasting the embossed text
    tombstone = ImageEnhance.Contrast(tombstone).enhance(2)
    
    filename = f"./temp/{id} {time.strftime('%H %M %S rip')}.png"
    tombstone.save(filename) 
    return filename

def get_accent_color(image):
    # Load the image
    image = get_image(image)

    # Resize the image to a smaller size for faster processing
    image = image.resize((100, 100))

    # Get the RGB values of all pixels in the resized image
    rgb_values = list(image.getdata())

    # Count the occurrence of each RGB value
    color_counts = {}
    for rgb in rgb_values:
        if rgb in color_counts:
            color_counts[rgb] += 1
        else:
            color_counts[rgb] = 1

    # Sort the RGB values based on their occurrence (descending order)
    sorted_colors = sorted(color_counts, key=color_counts.get, reverse=True)

    # Get the RGB values of the most dominant color
    dominant_color = sorted_colors[0]

    # Convert the RGB values to hexadecimal color code
    hex_color = '#{:02x}{:02x}{:02x}'.format(*dominant_color)

    return hex_color

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

        filename = f"./temp/{id} {time.strftime('%H %M %S Xbox360 Achievement')}.png"
        bg.save(filename)
        return filename

    def steam(image,name,description):
        image = get_image(image,True,[400,400])

        if not image:
            image = Image.open("./assets/SteamLogo.png").resize([400,400])

        bg = Image.open("./assets/SteamAchievement.png")
        final_image = Image.new("RGBA",[bg.width,bg.height])
        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-SemiBold.ttf",95)
        description_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Medium.ttf",72)

        draw = ImageDraw.Draw(bg)

        draw.text([480,150],name,font=name_font)
        
        if description:
            draw.text([480,280],description,font=description_font,fill="#d3d3d3")

        final_image.paste(image,[40,70])
        final_image.paste(bg,mask=bg)

        filename = f"./temp/{id} {time.strftime('%H %M %S Steam Achievement')}.png"
        final_image.save(filename)
        return filename

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
        
        filename = f"./temp/{id} {time.strftime(f'%h %M %S PS5Trophy')}.png"
        bg.save(filename)
        return filename

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
        
        filename = f"./temp/{id} {time.strftime(f'%h %M %S PS4Trophy')}.png"
        bg.save(filename)
        return filename

    def playstation3(image,name,*args,**kwargs):
        trophy = Image.open(f"./assets/{random.choice(random.sample(['Bronze','Silver','Gold','Platinum'],3))}Trophy.png").resize([70,80])

        image = get_image(image,True,[280,280])

        if not image:
            image = Image.open("./assets/PlaystationLogo.png").resize([280,280])

        bg = Image.open("./assets/PS3Achievement.png")
        bg.paste(image,[100,350])
        bg.paste(trophy,[400,470],trophy)

        name_font = ImageFont.truetype(r"./assets/fonts/NotoSans-Medium.ttf",71)
        bg = draw_text_with_soft_shadow(bg,(470,460),name,name_font,text_color=(255,255,255),shadow_color=(0,0,0,128),shadow_offset=(0,8))
        
        filename = f"./temp/{id} {time.strftime(f'%h %M PS3Trophy')}.png"
        bg.save(filename)
        return filename

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

        filename = f"./temp/{id} {time.strftime('%H %M %S osu!medal')}.png"
        final_image.save(filename)
        return filename

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
    draw_center_text(bg,[1550,350],f""" "{textwrap.fill(quote,35)}" """,font)
    
    font2 = ImageFont.truetype(r'./assets/fonts/Roboto-Regular.ttf', 30)
    draw_center_text(bg,[1550,800],f"- {username}, {time.strftime('%Y')}",font2)

    filename = f"./temp/{id} {time.strftime('%H %M %S quote')}.png"
    bg.save(filename)
    return filename


if __name__ == "__main__":
    achievement(id=69,name="Missed the fucking point, UwU",description="You fucking did it, didn't you?",platform="Steam",image="https://cdn.discordapp.com/avatars/1052773724501323788/4197174342e2ec66fdb47ccc2503fc1a.png?size=1024")