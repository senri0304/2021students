# -*- coding: utf-8 -*-
import datetime
import math
import os
import pyglet
import random
import time
from collections import deque

import numpy as np
import pandas as pd
from pyglet.gl import *
from pyglet.image import AbstractImage

import display_info

# Prefernce
# ------------------------------------------------------------------------
rept = 1
exclude_mousePointer = False
# ------------------------------------------------------------------------

# Get display informations
display = pyglet.canvas.get_display()
screens = display.get_screens()
win = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
win.set_fullscreen(fullscreen=True, screen=screens[len(screens) - 1])  # Present secondary display
win.set_exclusive_mouse(exclude_mousePointer)  # Exclude mouse pointer
key = pyglet.window.key

# Load variable conditions
deg1 = display_info.deg1
cntx = screens[len(screens) - 1].width / 2  # Store center of screen about x position
cnty = screens[len(screens) - 1].height / 3  # Store center of screen about y position
dat = pd.DataFrame()
iso = 8.0
draw_objects = []  # 描画対象リスト
end_routine = False  # Routine status to be exitable or not
xs = []
exit = True
n = 0

# Load resources
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal: AbstractImage = pyglet.image.load('materials/pedestal.png')
fixr = pyglet.sprite.Sprite(pedestal, x=cntx + iso * deg1 - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)
fixl = pyglet.sprite.Sprite(pedestal, x=cntx - iso * deg1 - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)

# vernier orientation
p = [1, -1]
# disparity direction
q = [1, -1]
# up series, down series
v = [100, -100]


# measure only crossed disparity
# Replicate for repetition
variation2 = list(np.repeat(p, rept*len(v)))
variation3 = list(v*(int(len(variation2)/2)))

# Randomize
r = random.randint(0, math.factorial(len(variation2)))
random.seed(r)
sequence = random.sample(variation2, len(variation2))
random.seed(r)
sequence2 = random.sample(variation3, len(variation2))
random.seed(r)
sequence3 = sequence #[-1*i for i in sequence]

print(sequence)
print(sequence2)
print(sequence3)
print(len(sequence))


# A getting key response function
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc, exit, trial_start, seq3, n
        if exit is False and symbol == key.UP:
            R.x += 5
            L.x -= 5
            delete()
        if exit is False and symbol == key.DOWN:
            R.x -= 5
            L.x += 5
            delete()
        if exit is True and symbol == key.UP:
            p_sound.play()
            pyglet.clock.schedule_once(replace, 0.1)
            trial_start = time.time()
        if exit is False and symbol == key.RETURN:
            exit = True
            get_results()
            n += 1
        if symbol == key.ESCAPE:
            win.close()
            pyglet.app.exit()


resp_handler = key_resp()


# Store objects into draw_objects
def fixer(dt):
    draw_objects.append(fixl)
    draw_objects.append(fixr)


def replace(dt):
    global exit
    del draw_objects[:]
    draw_objects.append(R)
    draw_objects.append(L)
    exit = False


# A end routine function
def exit_routine(dt):
    global exit
    exit = True
    beep_sound.play()
    if n < len(variation2):
        set_polygon(sequence[n], sequence2[n], sequence3[n])
    else:
        pass
#    fixer()
    pyglet.app.exit()


@win.event
def on_draw():
    # Refresh window
    win.clear()
    # 描画対象のオブジェクトを描画する
    for draw_object in draw_objects:
        draw_object.draw()


# Remove stimulus
def delete():
    global n, trial_end
    del draw_objects[:]
    p_sound.play()
    pyglet.clock.schedule_once(replace, 0.5)


def get_results():
    global n, sequence
    del draw_objects[:]
    # 右目の座標 - 右目が全額並行面と直角の座標、プラスならば輻輳より、マイナスならば開散
    x = R.x - (cntx + deg1 * iso - R.width / 2.0)
    xs.append(x)
    print("--------------------------------------------------\n"
          "x: " + str(x) + "\n"
          "--------------------------------------------------")
    # Check the experiment continue or break
    if n != len(variation2):
        pyglet.clock.schedule_once(exit_routine, 5)
    else:
        pyglet.app.exit()


def set_polygon(seq, seq2, seq3):
    global L, R, n
    # Set up polygon for stimulus
    R = pyglet.resource.image('stereograms/' +str(seq3) + str(seq) + 'lsh.png')
    R = pyglet.sprite.Sprite(R)
    R.x = cntx + deg1 * iso + seq2 - R.width / 2.0
    R.y = cnty - R.height / 2.0
    L = pyglet.resource.image('stereograms/' + str(seq3) + str(seq) + 'lsv.png')
    L = pyglet.sprite.Sprite(L)
    L.x = cntx - deg1 * iso - seq2 - L.width / 2.0
    L.y = cnty - L.height / 2.0


# Store the start time
start = time.time()
win.push_handlers(resp_handler)

#fixer()
set_polygon(sequence[0], sequence2[0], sequence3[0])

for i in sequence:
    pyglet.app.run()

# -------------- End loop -------------------------------

win.close()

# Store the end time
end_time = time.time()
daten = datetime.datetime.now()

# Write results onto csv
results = pd.DataFrame({'cnd': sequence2,  # Store variance_A conditions
                        'test_eye': sequence3,
                        'x': xs})

os.makedirs('data', exist_ok=True)

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf='./data/DATE' + name + '.csv', index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u'開始日時: ' + str(start))
print(u'終了日時: ' + str(end_time))
print(u'経過時間: ' + str(end_time - start))
