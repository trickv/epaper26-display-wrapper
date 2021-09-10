#!/usr/bin/env python

import os
import datetime
import dateutil.parser
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

font30bold = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/VeraBd.ttf", 30)
font30 = ImageFont.truetype("/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf", 30)
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
import json
conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/now-ac-power.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
solar_now_value = "{0:.2f} kW".format(float(now['data']['result'][0]['value'][1]) / 1000)

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/solaredge-today.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
solaredge_today_value = "{0:.1f} kWh".format(float(now['state']) / 1000)

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/hass-ecobee-br-sensor.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
br_temperature = "{0:.0f}°".format(float(now['state']))

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/hass-ecobee-cj-sensor.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
cj_room_temperature = "{0:.0f}°".format(float(now['state']))

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/my-current-net-metering.cgi")
response = conn.getresponse().read()
conn.close()
j = json.loads(response)
my_current_net_metering_value = "{0:.0f} kWh".format(float(j['state']))
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
last_update = dateutil.parser.parse(j['last_updated'])
threshold = datetime.timedelta(hours=1)


draw_red.text((2, 2), "Solar:", fill=0, font=font30bold)
draw_red.text((5, 45), "Now:", fill=0, font=font15)
draw_black.text((0, 55), solar_now_value, fill=0, font=font30)
draw_red.text((5, 85), "Today:", fill=0, font=font15)
draw_black.text((0, 95), solaredge_today_value, fill=0, font=font30)
if (now - last_update) < threshold:
    draw_red.text((5, 165), "Net:", fill=0, font=font15)
    draw_black.text((0, 175), my_current_net_metering_value, fill=0, font=font30)
draw_red.text((5, 165), "Net:", fill=0, font=font15)
draw_black.text((0, 175), my_current_net_metering_value, fill=0, font=font30)
draw_red.text((5, 220), "BR:", fill=0, font=font15)
draw_black.text((0, 230), br_temperature, fill=0, font=font30)
draw_red.text((75, 220), "CJ:", fill=0, font=font15)
draw_black.text((75, 230), cj_room_temperature, fill=0, font=font30)
draw_red.text((100, 275), now_chicago, fill=0, font=font15)
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
