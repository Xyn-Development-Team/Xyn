from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
from io import BytesIO
import time

def get_pfp(pfp:str,resize=(800,800)):
    if str(pfp).startswith("https://") or pfp.startswith("http://"):
        try:
            response = requests.get(pfp)
            image = Image.open(BytesIO(response.content))
        except:
            return False
    else:
        try:
            image = Image.open(pfp)
        except:
            return False
    image = image.convert(mode="RGBA")
    if resize:
        image = image.resize(resize)
    return image

def quote(id,username="Anonymous", pfp=None, quote=""):
    quote = "\"" + quote + "\""
    background = Image.new("RGBA",(1280,720))
    gradient = Image.open("./modules/fun/assets/quote_gradient.png").resize((1280,720)).convert(mode="RGBA")
    font = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",28) #28
    font2 = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",20)

    draw = ImageDraw.Draw(background)

    if pfp:
        pfp = get_pfp(pfp)
        background.paste(pfp)

    background.paste(gradient,(0,0),gradient)

    #Quote
    draw.text((710,140),textwrap.fill(quote,30),None,font,align="left")

    #Username
    draw.text((710,600),textwrap.fill("- " + username,45),None,font,align="left")

    if __name__ == "__main__":
        background.show()
    else:
        filename = f"{id}_{time.strftime("%d_%m_%Y_%H_%M_%S")}.png"
        background.save(f"./modules/fun/temp/{filename}")
        return "./modules/fun/temp/" + filename

def dice(id,number):
    dice = Image.open("./modules/fun/assets/dice.png").convert(mode="RGBA")
    draw = ImageDraw.Draw(dice)
    font = ImageFont.truetype("./modules/fun/assets/fonts/DejaVuSans.ttf",175)

    draw.text((515,500),str(number),align="center",anchor="mm",font=font)

    if __name__ == "__main__":
        dice.show()
    else:
        filename = f"{id}_{time.strftime("%d_%m_%Y_%H_%M_%S")}.png"
        dice.save(f"./modules/fun/temp/{filename}")
        return f"./modules/fun/temp/{filename}"

if __name__ == "__main__":
    id = 69
    dice(id,999)
    #quote(id,"Moonlight Dorkreamer 🌓",f"./temp/{id}_pfp.jpg","I friggin love pudding, anyways here's a long thing OwO, how about we make this even longer and much more lovely, I think we just done it, it's properly wrapping rn")