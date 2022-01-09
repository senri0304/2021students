#!/usr/bin/env python
# coding: utf-8

import pyglet.canvas, random, math
import numpy as np

# Input display information
inch = 23.0
aspect_width = 16.0
aspect_height = 9.0

exclude_mousePointer = False

# Get display information
display = pyglet.canvas.get_display()
screens = display.get_screens()
win = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
win.set_fullscreen(fullscreen=True, screen=screens[len(screens) - 1])  # Present secondary display
win.set_exclusive_mouse(exclude_mousePointer)  # Exclude mouse pointer
key = pyglet.window.key

# Load variable conditions
cntx = screens[len(screens) - 1].width / 2  # Store center of screen about x position
cnty = screens[len(screens) - 1].height / 3  # Store center of screen about y position

resolution = screens[len(screens) - 1].height

c = (aspect_width ** 2 + aspect_height ** 2) ** 0.5
d_height = 2.54 * (aspect_height / c) * inch

deg1 = round(resolution * (1 / d_height))

# independent variables
variation = ['0', '0.15', '0.3', '0.6']

# repetition
rept = 3
repetition = list(range(1, rept + 1))

# Replicate for repetition
variation2 = list(np.repeat(variation, rept))
repetition = repetition*len(variation)


# Randomize
r = random.randint(0, math.factorial(len(variation2)))
random.seed(r)
sequence = random.sample(variation2, len(variation2))
random.seed(r)
sequence2 = random.sample(repetition, len(variation2))

print(sequence)
print(sequence2)
print(len(sequence))
