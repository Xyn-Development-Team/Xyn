from PIL import Image
from io import BytesIO
import numpy as np
import urllib

def get_image(image, resize=False, size=(300, 300)):
    """Checks if the image is a URL and if so, loads it locally, else it tries to load from a path.
    If `resize` is True, it will resize the image to the specified `size`."""
    
    if "https://" in image:
        with urllib.request.urlopen(image) as response:
            image = Image.open(response)
    else:
        image = Image.open(image)
    
    if resize:
        image = image.resize(size)
    
    return image

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