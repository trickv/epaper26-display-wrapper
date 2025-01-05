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
try:
    #solar_now_value = "{0:.2f} kW".format(float(now['data']['result'][0]['value'][1]) / 1000) # prometheus data source
    if now['state'] == "unavailable":
        solar_now_value = now['state']
    else:
        solar_now_value = "{0:.2f} kW".format(float(now['state']) / 1000) # hass data source
except IndexError:
    solar_now_value = "err"

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/solaredge-today.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
solaredge_today_value = "{0:.1f} kWh".format(float(now['state']) / 1000)

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/hass-tde-projection.cgi")
response = conn.getresponse().read()
conn.close()
now = json.loads(response)
tde_projection = "{0:.1f} kWh".format(float(now['state']))

def get_simple_hass_state(cgi_name, unit):
    conn = http.client.HTTPSConnection("vanstaveren.us")
    conn.request("GET", "/~trick/epaper/{}.cgi".format(cgi_name))
    response = conn.getresponse().read()
    conn.close()
    now = json.loads(response)
    hass_sensor_state = "{0:.0f}{1}".format(float(now['state']), unit)
    return hass_sensor_state

br_temperature = get_simple_hass_state("hass-ecobee-br-sensor", "°")
cj_room_temperature = get_simple_hass_state("hass-ecobee-cj-sensor", "°")

heat_load_east = get_simple_hass_state("hass-heat-load-east", "%")
heat_load_west = get_simple_hass_state("hass-heat-load-west", "%")
heat_load_forced_air = get_simple_hass_state("hass-heat-load-forced-air", "%")
boiler_set_point = get_simple_hass_state("hass-boiler-set-point", "°")

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/my-current-net-metering.cgi")
response = conn.getresponse().read()
conn.close()
j = json.loads(response)
my_current_net_metering_value = "{0:.0f} kWh".format(float(j['state']))
now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
last_update = dateutil.parser.parse(j['last_updated'])
threshold = datetime.timedelta(hours=1)

conn = http.client.HTTPSConnection("vanstaveren.us")
conn.request("GET", "/~trick/epaper/hass-net-last-update.cgi")
response = conn.getresponse().read()
conn.close()
json_object = json.loads(response)
comed_data_age = "{0:.1f}".format(float(json_object['state']))


# Draw Solar numbers:
y_position = 0
draw_black.text((0, y_position), solar_now_value, fill=0, font=font30)
y_position += 30
draw_black.text((0, y_position), solaredge_today_value, fill=0, font=font30)
y_position += 30
draw_black.text((0, y_position), tde_projection, fill=0, font=font30)
y_position += 30
draw_black.text((0, y_position), my_current_net_metering_value, fill=0, font=font30)
y_position += 30
draw_red.line((0, y_position, size[0], y_position), fill=0)
y_position += 5

# Now heating & cooling info:
draw_red.text((5, y_position), "Office:", fill=0, font=font15)
draw_red.text((75, y_position), "Guest:", fill=0, font=font15)
y_position += 10
draw_black.text((0, y_position), br_temperature, fill=0, font=font30)
draw_black.text((75, y_position), cj_room_temperature, fill=0, font=font30)
y_position += 30
draw_red.text((5, y_position), "Heat Load:", fill=0, font=font15)
y_position += 15
draw_red.text((5, y_position), "East:", fill=0, font=font15)
draw_red.text((80, y_position), "West:", fill=0, font=font15)
y_position += 15
draw_black.text((0, y_position), heat_load_east, fill=0, font=font30)
draw_black.text((80, y_position), heat_load_west, fill=0, font=font30)
y_position += 30
draw_red.text((5, y_position), "HVAC:", fill=0, font=font15)
draw_red.text((75, y_position), "Boiler Set:", fill=0, font=font15)
y_position += 15
draw_black.text((0, y_position), heat_load_forced_air, fill=0, font=font30)
draw_black.text((75, y_position), boiler_set_point, fill=0, font=font30)


# metadata at bottom of screen
draw_red.text((2, 275), comed_data_age, fill=0, font=font15)
draw_red.text((100, 275), now_chicago, fill=0, font=font15)

# cleanup
del draw_red
del draw_black


red.save("red.bmp")
black.save("black.bmp")
if test_mode:
    os.system("convert black.bmp red.bmp -combine combined-testmode.bmp")
    os.system("eog combined-testmode.bmp")
else:
    os.system("cp black.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb1.bmp")
    os.system("cp red.bmp buydisplay-epaper26-example-adaptation/wiringpi/pic/cw-1rb2.bmp")
    os.system("cd buydisplay-epaper26-example-adaptation/wiringpi/ && ./epd")
