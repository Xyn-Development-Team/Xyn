from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import requests
import urllib
import time
from io import BytesIO
import re
from typing import Union

def get_image(image, resize=False, size=(300, 300)):
    """Checks if the image is a URL and if so, loads it locally, else it tries to load from a path.
    If `resize` is True, it will resize the image to the specified `size`."""
    
    if "https://" in image:
        req = urllib.request.Request(image, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            image = Image.open(response)
    else:
        image = Image.open(image)
    
    if resize:
        image = image.resize(size)
    
    return image


def quote(id:Union[int, str], username=None, display_name="Anonymous", pfp=None, quote="") -> str:
    """Generates an image with a user's quote.

    Args:
        id (Union[int, str]): The user's Discord ID, used solely for easily distinguishing requests.
        username (str, optional): The user's Discord @. Defaults to None.
        display_name (str, optional): The user's display name. Defaults to "Anonymous".
        pfp (str optional): A URL to the user's pfp. Defaults to None.
        quote (str, optional): The content you want to quote. Defaults to "".

    Returns:
        str: Path for the image file.
    """
    
    quote = "\"" + quote + "\""
    background = Image.new("RGBA",(1280,720))
    gradient = Image.open("./modules/fun/assets/quote_gradient.png").resize((1280,720)).convert(mode="RGBA")
    font = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",28) #28
    font2 = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",20)
    font3 = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",20)

    draw = ImageDraw.Draw(background)

    if pfp:
        pfp = get_image(pfp, True, (810, 810)).convert("RGBA")
        background.paste(pfp)

    background.paste(gradient,(0,0),gradient)

    #Quote
    draw.text((980,140),textwrap.fill(quote,35),None,font,align="left",anchor="ms")

    #Display name
    draw.text((980,600),textwrap.fill("- " + display_name,45),None,font,align="left",anchor="ms")

    if username:
        #Username
        draw.text((980,630),textwrap.fill("@" + username if "@" not in username else username ,45), None, font3, align="left", anchor="ms")

    if __name__ == "__main__":
        background.show()
    else:
        filename = f"{id}_{time.strftime('%d_%m_%Y_%H_%M_%S')}.png"
        background.save(f"./modules/fun/temp/{filename}")
        return "./modules/fun/temp/" + filename

def dice(id:Union[int, str], number:int) -> str:
    """Generates the image of a dice with a random number based on the number of sides

    Args:
        id (Union[int, str]): The user's Discord ID, used solely for easily distinguishing requests.
        number (int): The number of sides the dice has from 1 - 999.

    Returns:
        str: Path for the image file.
    """

    dice = Image.open("./modules/fun/assets/dice.png").convert(mode="RGBA")
    draw = ImageDraw.Draw(dice)
    font = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",175)

    draw.text((515,500),str(number),align="center",anchor="mm",font=font)

    if __name__ == "__main__":
        dice.show()
    else:
        filename = f"{id}_{time.strftime('%d_%m_%Y_%H_%M_%S')}.png"
        dice.save(f"./modules/fun/temp/{filename}")
        return f"./modules/fun/temp/{filename}"

def rip(id:Union[int, str], display_name=str, description=None, pfp=None) -> str:
    """Generates the image of a tombstone with the user's display name, pfp and a description.

    Args:
        id (Union[int, str]): The user's Discord ID, used solely for easily distinguishing requests.
        display_name (str): The user's Discord display name. Defaults to str.
        description (str, optional): The text what will go under the user's name and pfp on the gravestone. Defaults to None.
        pfp (str, optional): A URL to the user's pfp. Defaults to None.

    Returns:
        str: A Path for the image file.
    """

    tombstone = Image.open("./modules/fun/assets/tombstone.png")

    text_layer = Image.new("RGBA", tombstone.size)

    font = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",35)

    if pfp:
        pfp = get_image(pfp, (300, 300)).convert("RGBA")
        pfp = ImageEnhance.Contrast(pfp).enhance(2)
        pfp = pfp.filter(ImageFilter.EMBOSS)
        pfp = ImageEnhance.Color(pfp).degenerate
        tombstone.paste(pfp, ((450, 170)), pfp)

    text_draw = ImageDraw.Draw(text_layer)
    text_draw.text((600,125),textwrap.fill(display_name if display_name else "Anonymous",30),fill="white",stroke_fill="black",stroke_width=4,font=font,align="center",anchor="ms")
    
    if description:
        text_draw.text((600,505),textwrap.fill(description,30),fill="white",stroke_fill="black",stroke_width=4,font=font,align="center",anchor="ms")
    
    text_layer = text_layer.filter(ImageFilter.EMBOSS)
    tombstone.paste(text_layer, text_layer)

    tombstone = ImageEnhance.Contrast(tombstone).enhance(2)

    if __name__ == "__main__":
        tombstone.show()
    else:
        filename = f"{id}_{time.strftime('%d_%m_%Y_%H_%M_%S')}.png"
        tombstone.save(f"./modules/fun/temp/{filename}")
        return f"./modules/fun/temp/{filename}"

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def get_average_color(image):
    image = get_image(image)
    
    # Convert the image to RGBA if it's not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Convert the image to a numpy array for faster processing
    pixels = np.array(image)

    # Calculate the average RGB values
    avg_color = tuple(np.average(pixels, axis=(0,1)).astype(int))

    return rgb_to_hex(avg_color)

if __name__ == "__main__":
    id = 69
    #rip(id, "Moonlight Dorkreamer 🌓", "Was too much of a dork to be left alive! here's some more text to feasten your eyes!", "./modules/fun/temp/pfp.jpg")
    #dice(id,999)
    #quote(id, "@dorkreamer", "Moonlight Dorkreamer 🌓",f"./modules/fun/temp/pfp.jpg","I friggin love pudding, anyways here's a long thing OwO, how about we make this even longer and much more lovely, I think we just done it, it's properly wrapping rn")