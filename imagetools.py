from PIL import ImageDraw, Image, ImageFont, ImageFilter, ImageEnhance
from PIL import __version__ as pil_ver
PILLOW_VERSION = tuple([int(_) for _ in pil_ver.split(".")[:3]])

import requests
from io import BytesIO
import re

import time

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

def get_pfp(pfp,resize=False,size=(300,300)):
    """Checks if the pfp is a url and if so, loads it locally, else it tries to load from a path
    ## pfp
    Can be either a url or a string containing the path to such file
    ## resize
    Defines if you want to resize the image to the size contained in the next argument `size`
    ## size
    If `resize` is True, it will simply resite to this size, it's type is a `tuple!`"""
    if any(["https://" in pfp]):
        response = requests.get(pfp)
        pfp = Image.open(BytesIO(response.content))
    else:
        pfp = Image.open(pfp)
    pfp = pfp.convert("RGBA")
    if resize:
        return pfp.resize(size)
    else:
        return pfp

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
    pfp = get_pfp(pfp,resize=True)

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

def quote(id,username:str,quote:str,pfp):
    pfp = get_pfp(pfp)
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


    