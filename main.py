#!/usr/bin/env python

import argparse

from PIL import Image
from PIL import ImageDraw


parser = argparse.ArgumentParser()
parser.add_argument("--test", action="store_true", help="Test mode which uses xv to display the generated image locally")
args = parser.parse_args()
test_mode=args.test

# NB: mode P means 8 bit indexed; i might later just make two grayscale images one for each color instead of doing an indexed color version and splitting it out.
p = Image.new(mode='P', size=(296, 152), color=(255,255,255))

draw = ImageDraw.Draw(p)
draw.line((0, 0) + p.size, fill=128)
draw.line((0, p.size[1], p.size[0], 0), fill=128)
del draw


if test_mode:
    p.show()
else:
    p.save("foo.bmp")
