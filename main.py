#!/usr/bin/env python

import os
import datetime
import pytz
import argparse

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true", help="Test mode which uses xv to display the generated image locally")
args = parser.parse_args()
test_mode=args.test

font30 = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf", 30)
font15 = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf", 15)

# NB: mode P means 8 bit indexed; i might later just make two grayscale images one for each color instead of doing an indexed color version and splitting it out.
black = Image.new(mode='1', size=(152, 296), color=(255))
red = Image.new(mode='1', size=(152, 296), color=(255))

draw_black = ImageDraw.Draw(black)
draw_red = ImageDraw.Draw(red)

draw_black.line((0, 0) + black.size, fill=0)
draw_black.line((0, black.size[1], black.size[0], 0), fill=0)
draw_red.line((0, 0) + red.size, fill=0)
draw_red.line((0, red.size[1] - 10, red.size[0] - 10, 10), fill=0)

utc_now_datetime = pytz.utc.localize(datetime.datetime.now())
now_chicago = utc_now_datetime.astimezone(pytz.timezone("America/Chicago")).strftime("%H:%M")
now_utc = utc_now_datetime.strftime("%H:%M")
draw_black.text((20, 20), "UTC", fill=0, font=font15)
draw_red.text((30, 50), now_utc, fill=0, font=font30)
draw_black.text((20, 90), "Chicago", fill=0, font=font15)
draw_red.text((30, 110), now_chicago, fill=0, font=font30)
del draw_red
del draw_black


if test_mode:
    black.show()
    red.show()
else:
    black.save("black.bmp")
    red.save("red.bmp")
    os.system("cp black.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb1.bmp")
    os.system("cp red.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb2.bmp")
    os.system("cd buydisplay-epaper26-example-adaptation/wiringpi/ && ./epd")
