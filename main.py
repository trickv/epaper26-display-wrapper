#!/usr/bin/env python

import os
import datetime
import pytz
import argparse
from filelock import Timeout, FileLock

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true", help="Test mode which uses xv to display the generated image locally")
args = parser.parse_args()
test_mode=args.test

lockfile_path = ".run-lock"
lock = FileLock(lockfile_path, timeout=0.01)
lock.acquire()

font30 = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf", 30)
font15 = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf", 15)

# NB: mode P means 8 bit indexed; i might later just make two grayscale images one for each color instead of doing an indexed color version and splitting it out.
size=(152, 296)
black = Image.new(mode='1', size=size, color=(255))
red = Image.new(mode='1', size=size, color=(255))

draw_black = ImageDraw.Draw(black)
draw_red = ImageDraw.Draw(red)

draw_black.line((0, 0, size[0], 0), fill=0)
draw_black.line((0, size[1] - 1, size[0] - 1, size[1] - 1), fill=0)
draw_red.line((0, 0, 0, size[1]), fill=0)
draw_red.line((size[0] - 1, 0, size[0] - 1, size[1] - 1), fill=0)

utc_now_datetime = pytz.utc.localize(datetime.datetime.now())
now_chicago = utc_now_datetime.astimezone(pytz.timezone("America/Chicago")).strftime("%H:%M")
now_utc = utc_now_datetime.strftime("%H:%M")
#draw_black.text((20, 30), "UTC", fill=0, font=font15)
#draw_red.text((30, 50), now_utc, fill=0, font=font30)
#draw_black.text((20, 90), "Chicago", fill=0, font=font15)
import http.client
conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/now.cgi")
response = conn.getresponse().read()
conn.close

import json
now = json.loads(response)
solar_now_value = "{0}".format(int(now['data']['result'][0]['value'][1]) / 100)

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/now-dc-volts.cgi")
response = conn.getresponse().read()
conn.close

now = json.loads(response)
dc_volts = "{0}".format(int(now['data']['result'][0]['value'][1]) / 10)

solar_today_value = solar_yesterday_value = "-1"
draw_red.text((2, 2), "Solar:", fill=0, font=font30)
draw_red.text((10, 35), "Now:", fill=0, font=font15)
draw_black.text((80, 35), solar_now_value, fill=0, font=font15)
draw_red.text((10, 55), "DC Volts:", fill=0, font=font15)
draw_black.text((80, 55), dc_volts, fill=0, font=font15)
draw_red.text((10, 75), "Today:", fill=0, font=font15)
draw_black.text((80, 75), solar_today_value, fill=0, font=font15)
draw_red.text((10, 95), "Yesterday:", fill=0, font=font15)
draw_black.text((80, 95), solar_yesterday_value, fill=0, font=font15)
draw_red.text((50, 190), now_chicago, fill=0, font=font15)
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
