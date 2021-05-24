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
iso = 7.0
draw_objects = []  # 描画対象リスト
end_routine = False  # Routine status to be exitable or not
latencies = []  # Store sum(kud), cumulative reaction time on a trial.
trial_times = []
exit = True
oneshot = True
n = 0

# Load resources
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal1: AbstractImage = pyglet.image.load('materials/pedestal1.png')
pedestal2: AbstractImage = pyglet.image.load('materials/pedestal2.png')
fixr1 = pyglet.sprite.Sprite(pedestal1, x=cntx + iso * deg1 - pedestal1.width / 2.0, y=cnty - pedestal1.height / 2.0)
fixl1 = pyglet.sprite.Sprite(pedestal1, x=cntx - iso * deg1 - pedestal1.width / 2.0, y=cnty - pedestal1.height / 2.0)
fixr2 = pyglet.sprite.Sprite(pedestal2, x=cntx + iso * deg1 - pedestal2.width / 2.0, y=cnty - pedestal2.height / 2.0)
fixl2 = pyglet.sprite.Sprite(pedestal2, x=cntx - iso * deg1 - pedestal2.width / 2.0, y=cnty - pedestal2.height / 2.0)


# disparities
eccentricity = [1, 2]
#test_eye = [-1, 1]

# measure only crossed disparity
# Replicate for repetition
variation2 = list(np.repeat(display_info.variation, rept*2))
#test_eye2 = list(np.repeat(test_eye, len(variation2)/2))
eccentricity2 = eccentricity*int((len(variation2)/2))

# Randomize
r = random.randint(0, math.factorial(len(variation2)))
random.seed(r)
sequence = random.sample(variation2, len(variation2))
random.seed(r)
sequence2 = random.sample(eccentricity2, len(variation2))
#random.seed(r)
#sequence3 = random.sample(test_eye2, len(variation2))

print(sequence)
print(sequence2)
#print(sequence3)
print(len(sequence))


# ----------- Core program following ----------------------------

# A getting key response function
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc, exit, trial_start, oneshot, kd
        if exit is False and oneshot is True and symbol == key.DOWN:
            kd = time.time()
            oneshot = False
            delete()
        if exit is True and oneshot is True and symbol == key.UP:
            p_sound.play()
            exit = False
            pyglet.clock.schedule_once(replace, 0.5)
            oneshot = False
            trial_start = time.time()
        if symbol == key.ESCAPE:
            win.close()
            pyglet.app.exit()


resp_handler = key_resp()


# Store objects into draw_objects
def fixer(seq2):
    if seq2 != 1:
        draw_objects.append(fixl2)
        draw_objects.append(fixr2)
    else:
        draw_objects.append(fixl1)
        draw_objects.append(fixr1)


def replace(dt):
    global oneshot
    del draw_objects[:]
    draw_objects.append(R)
    draw_objects.append(L)
    oneshot = True

# A end routine function
def exit_routine(dt):
    global exit, oneshot
    exit = True
    oneshot = True
    beep_sound.play()
    prepare_routine()
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
    n += 1
    trial_end = time.time()
    get_results()


def get_results():
    global kd, n, trial_end, trial_start, sequence, file_names, latencies
    trial_time = trial_end - trial_start
    trial_times.append(trial_time)
    latency = kd - trial_start - 0.5
    latencies.append(latency)
    print('--------------------------------------------------')
    print('trial: ' + str(n) + '/' + str(len(sequence)))
    print('response: ' + str(latency))
    print('condition: ' + str(sequence[n - 1]) + ', ' + str(sequence2[n - 1]))
    # Check the experiment continue or break
    if n != len(variation2):
        pyglet.clock.schedule_once(exit_routine, 1.0)
    else:
        pyglet.app.exit()


def set_polygon(seq, seq2, seq3=1):
    global L, R, n
    # Set up polygon for stimulus
    R = pyglet.resource.image('stereograms/' + str(seq) + 'lsn' + str(seq2) + '.png')
    R = pyglet.sprite.Sprite(R)
    R.x = cntx + deg1 * iso * seq3 - R.width / 2.0
    R.y = cnty - R.height / 2.0
    L = pyglet.resource.image('stereograms/' + str(seq) + 'lsp' + str(seq2) + '.png')
    L = pyglet.sprite.Sprite(L)
    L.x = cntx - deg1 * iso * seq3 - L.width / 2.0
    L.y = cnty - L.height / 2.0


def prepare_routine():
    if n < len(variation2):
        fixer(sequence2[n])
        set_polygon(sequence[n], sequence2[n])
    else:
        pass


# Store the start time
start = time.time()
win.push_handlers(resp_handler)

fixer(sequence2[0])
set_polygon(sequence[0], sequence2[0])

for i in sequence:
    tc = 0  # Count transients
    ku = deque([])  # Store unix time when key up
    kd = deque([])  # Store unix time when key down
    kud = []  # Differences between kd and ku

    pyglet.app.run()

# -------------- End loop -------------------------------

win.close()

# Store the end time
end_time = time.time()
daten = datetime.datetime.now()

# Write results onto csv
results = pd.DataFrame({'cnd': sequence,  # Store variance_A conditions
                        'eccentricity': sequence2,
                        'latency': latencies})  # Store cdt(target values) and input number of trials
os.makedirs('data', exist_ok=True)

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf='./data/DATE' + name + '.csv', index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u'開始日時: ' + str(start))
print(u'終了日時: ' + str(end_time))
print(u'経過時間: ' + str(end_time - start))
