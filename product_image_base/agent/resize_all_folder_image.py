import os
import base64
import sys

from PIL import Image
import math
import ConfigParser

# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('./setup.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])

# Parameters
origin_path = config.get('SETUP', 'origin')
destination_path = config.get('SETUP', 'destination')
max_width = config.get('SETUP', 'max_width')
max_height = config.get('SETUP', 'max_height')
max_px = config.get('SETUP', 'max_px')
square_image = config.get('SETUP', 'square_image')


# -----------------------------------------------------------------------------
# Utility function:
# -----------------------------------------------------------------------------
def change_image_in_square(fullname):
    """ Change image in square with adding 2 band
    """
    # Center the image:
    image = Image.open(fullname)
    old_width, old_height = image.size
    if old_width > old_height:
        new_width = new_height = old_width
    else:
        new_width = new_height = old_height
    x1 = int(math.floor((new_width - old_width) / 2))
    y1 = int(math.floor((new_height - old_height) / 2))

    # Get fill in colour:
    mode = image.mode
    if len(mode) == 4:  # RGBA, CMYK
        new_background = (255, 255, 255, 255)
    elif len(mode) == 3:  # RGB
        new_background = (255, 255, 255)
    else:  # len(mode) == 1:  # L, 1
        new_background = (255,)

    new_image = Image.new(mode, (new_width, new_height), new_background)
    new_image.paste(image, (x1, y1, x1 + old_width, y1 + old_height))
    del image
    new_image.save(fullname)


for root, folders, files in os.walk(origin_path):
    for filename in files:
        file_in = os.path.join(root, filename)
        file_out = os.path.join(destination_path, filename)

        try:
            img = Image.open(file_in)
            width, height = img.size

            if width > height:
                new_width = max_px
                new_height = max_px * height / width
            else:
                new_height = max_px
                new_width = max_px * width / height

            new_img = img.resize(
                (new_width, new_height),
                Image.ANTIALIAS)

            # Filters: NEAREST BILINEAR BICUBIC ANTIALIAS
            new_img.save(file_out, 'JPEG')  # todo change output!!!!

            if square_image:
                change_image_in_square(file_out)
                print('Resize: %s [max: %s]' % (filename, max_px))
            else:
                print('Resize (square): %s [max: %s]' % (filename, max_px))
        except:
            print('Error resizing: %s\n%s' % (filename, sys.exit()))