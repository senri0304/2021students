#!/usr/bin/env python
# coding: utf-8

import pyglet.canvas
import numpy as np

# Input display information
inch = 23.0
aspect_width = 16.0
aspect_height = 9.0

# Input stereogram relative_size in cm unit
size = 5

# Input luminance of background
lb = 85  # 215, 84%

# Input fixation point position in cm unit
ecc = 1

# Get display information
display = pyglet.canvas.get_display()
screens = display.get_screens()

resolution = screens[len(screens) - 1].height

c = (aspect_width ** 2 + aspect_height ** 2) ** 0.5
d_height = 2.54 * (aspect_height / c) * inch

deg1 = round(resolution * (1 / d_height))

# あとでresizeするためにサイズを1/2倍する
sz = round(resolution * ((size/2) / d_height))
f = round(sz * 0.023 / 2)  # 3.6 min of arc in 5 deg presentation area, actually 0.6 mm

eccentricity = round(1 / np.sqrt(2.0) * ecc / d_height * resolution)

# Input target relative_size in cm unit
inner_size = [int(sz/4), int(sz/2)]

# disparity; 3.6 min of arc * given parameter
# note that this parameter proceed x2 under creating rds
variation = [int(f*3), int(f*6)]
