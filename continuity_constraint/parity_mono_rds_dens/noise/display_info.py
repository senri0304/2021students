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
variation = [0.5, 1.0, 2.0, 4.0]
variation2 = [0.05]#, 0.3]

# repetition
rept = [1]#, 2, 3, 4, 5]

# Replicate for repetition
var1 = list(np.repeat(variation, len(variation2)))#*len(rept)))
var2 = variation2*len(variation)#list(np.repeat(variation2, len(var1)))

print(var1)
print(var2)


# Randomize
r = random.randint(0, math.factorial(len(var1)))
random.seed(r)
sequence = random.sample(var1, len(var1))
random.seed(r)
sequence2 = random.sample(var2, len(var1))

print(sequence)
print(sequence2)
print(len(sequence))
