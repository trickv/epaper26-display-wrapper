#!/usr/bin/env python

import os
import argparse

from PIL import Image
from PIL import ImageDraw


parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true", help="Test mode which uses xv to display the generated image locally")
args = parser.parse_args()
test_mode=args.test

# NB: mode P means 8 bit indexed; i might later just make two grayscale images one for each color instead of doing an indexed color version and splitting it out.
black = Image.new(mode='1', size=(296, 152), color=(255))

draw = ImageDraw.Draw(black)
draw.line((0, 0) + black.size, fill=128)
draw.line((0, black.size[1], black.size[0], 0), fill=128)
del draw

red = Image.new(mode='1', size=(296, 152), color=(255))

draw = ImageDraw.Draw(black)
draw.line((0, 0) + red.size, fill=128)
draw.line((0, red.size[1], red.size[0], 0), fill=128)
del draw


if test_mode:
    black.show()
    red.show()
else:
    black.save("black.bmp")
    red.save("red.bmp")
    os.system("cp black.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb1.bmp")
    os.system("cp red.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb2.bmp")
    os.system("cd buydisplay-epaper26-example-adaptation/wiringpi/ && ./epd")
