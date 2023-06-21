#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2001-2014 Micronaet SRL (<http://www.micronaet.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import pdb
import sys
import math
import pickle
from PIL import Image
import ConfigParser


# -----------------------------------------------------------------------------
# Read configuration parameter:
# -----------------------------------------------------------------------------
cfg_file = os.path.expanduser('./setup.cfg')

config = ConfigParser.ConfigParser()
config.read([cfg_file])

# Parameters
origin_path = os.path.expanduser(config.get('SETUP', 'origin'))
destination_path = os.path.expanduser(config.get('SETUP', 'destination'))
max_width = eval(config.get('SETUP', 'max_width'))
max_height = eval(config.get('SETUP', 'max_height'))
max_px = eval(config.get('SETUP', 'max_px'))
square_image = eval(config.get('SETUP', 'square_image'))

pickle_file = './loaded.pickle'

try:
    files_resized = pickle.load(open(pickle_file, 'rb'))
except:
    files_resized = {}


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

try:
    for root, folders, files in os.walk(origin_path):
        for filename in files:
            file_in = os.path.join(root, filename)
            file_out = os.path.join(destination_path, filename)

            if file_in not in files_resized:
                files_resized[file_in] = os.path.getmtime(file_in)

            if files_resized[file_in] == os.path.getmtime(file_in):
                print('[WARNING] Nessuna modifica: %s (saltato)' % file_in)
                continue

            try:
                try:
                    img = Image.open(file_in)
                except:
                    print('[ERROR] Apertura file: %s (saltato)' % file_in)
                    continue

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
                    print('[INFO]Resize: %s [max: %s]' % (filename, max_px))
                else:
                    print('[INFO]Resize (square): %s [max: %s]' % (
                        filename, max_px))
            except:
                print('[ERROR] Error resizing: %s\n%s' % (filename, sys.exit()))
        break
finally:
    pickle.dump(files_resized, open(pickle_file, 'wb'))
    print('[INFO] Ridimensionamento terminato')
