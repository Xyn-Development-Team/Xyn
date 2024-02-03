import requests
from PIL import Image
from io import BytesIO

def get_image(image,resize=False,size=(300,300)):
    """Checks if the image is a url and if so, loads it locally, else it tries to load from a path
    ## image
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


def get_accent_color(image):
    # Load the image
    if image:
        image = get_image(image)
    else:
        return None

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