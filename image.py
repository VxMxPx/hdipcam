"""
Cam image manipulation.
"""

import io, math, operator, time
from PIL import Image, ImageChops, ImageDraw
from functools import reduce

def frombytes(imagebytes):
    """
    Return an image object from imagebytes.
    """
    return Image.open(io.BytesIO(imagebytes))

def diff(image1, image2):
    """
    Calculate difference between two images.
    """
    hst = ImageChops.difference(image1, image2).histogram()
    return math.sqrt(
        reduce(
            operator.add,
            map(lambda hst, i: hst*(i**2), hst, range(256))) / (float(image1.size[0]) * image1.size[1]))

def mask(image, regions):
    """
    Add black square mask to image.
    Regions format: (top, left, width, height) or,
    for multiple: ((top, left, width, height))
    """
    if type(regions[0]) != tuple:
        regions = (regions,)
    canvas = ImageDraw.Draw(image)
    for reg in regions:
        params = (int(reg[0]), int(reg[1]), int(reg[0]) + int(reg[2]), int(reg[1]) + int(reg[3]))
        canvas.rectangle(params, fill="#000000")
    del canvas

def watermark(image, caption):
    """
    Add watermark text to the image.
    """
    canvas = ImageDraw.Draw(image)
    canvas.text((10, image.size[1] - 20), caption)
    del canvas

def combine(image1, image2, caption=None):
    """
    Put two images side by side.
    """
    canvas = Image.new('RGB', (image1.size[0] * 2, image1.size[1]))
    canvas.paste(image1, (0, 0))
    canvas.paste(image2, (image1.size[0], 0))
    if caption:
        watermark(canvas, caption)
    return canvas

def save(image, path, filename=None):
    """
    Save image to file.
    """
    if not filename:
        filename = time.strftime("%Y-%m-%d-%H-%M-%S")
    image_file = open(path + str(filename) + ".jpg", "wb")
    if type(image) is bytes:
        image_file.write(image)
    else:
        image.save(image_file, 'jpeg')
    image_file.close()
