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
cal = -60
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
#tc = 0  # Count transients
#tcs = []  # Store transients per trials
#kud_list = []  # Store durations of key pressed
#cdt = []  # Store sum(kud), cumulative reaction time on a trial.
#mdt = []
#dtstd = []
latencies = []
exit = True
n = 0

# Load resources
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal: AbstractImage = pyglet.image.load('materials/pedestal.png')
fixr = pyglet.sprite.Sprite(pedestal, x=cntx + iso * deg1 + cal - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)
fixl = pyglet.sprite.Sprite(pedestal, x=cntx - iso * deg1 - cal - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)

# disparities
variation = display_info.variation*5
variation2 = display_info.inner_size[1] #variation2 = display_info.inner_size
variation3 = list(range(1, 6))*2

# measure only crossed disparity
# Replicate for repetition
#var = list(np.repeat(variation, rept))
#var2 = list(np.repeat(variation2, len(var) / 2))
#var3 = list(np.repeat(variation3, len(var) / 2))

# added zero disparity condition
# variation2.extend([0]*rept*len(test_eye))
# test_eye2.extend(test_eye*rept)

# Randomize
r = random.randint(0, math.factorial(len(variation)))
random.seed(r)
sequence = random.sample(variation, len(variation))
random.seed(r)
sequence2 = [variation2]*len(variation) #sequence2 = random.sample(var2, len(var))
random.seed(r)
sequence3 = random.sample(variation3, len(variation))

print(sequence)
print(sequence2)
print(sequence3)
print(len(sequence))


# ----------- Core program following ----------------------------

# A getting key response function
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc, exit, trial_start, kd
        if exit is False and symbol == key.DOWN:
            kd = time.time()
#            kd.append(time.time())
#            tc = tc + 1
            pyglet.clock.unschedule(delete)
            pyglet.clock.schedule_once(delete, 0.001)
        if exit is True and symbol == key.UP:
            p_sound.play()
            exit = False
            pyglet.clock.schedule_once(delete, 30.0)
            pyglet.clock.schedule_once(replace, 0.2)
            trial_start = time.time()
        if symbol == key.ESCAPE:
            win.close()
            pyglet.app.exit()
#    def on_key_release(self, symbol, modifiers):
#        global tc
#        if exit is False and symbol == key.DOWN:
#            ku.append(time.time())
#            tc = tc + 1

resp_handler = key_resp()


# Store objects into draw_objects
def fixer():
    draw_objects.append(fixl)
    draw_objects.append(fixr)


def replace(dt):
    del draw_objects[:]
    draw_objects.append(R)
    draw_objects.append(L)


# A end routine function
def exit_routine(dt):
    global exit
    exit = True
    beep_sound.play()
    prepare_routine()
    fixer()
    pyglet.app.exit()


@win.event
def on_draw():
    # Refresh window
    win.clear()
    # 描画対象のオブジェクトを描画する
    for draw_object in draw_objects:
        draw_object.draw()


# Remove stimulus
def delete(dt):
    global n, trial_end
    del draw_objects[:]
    p_sound.play()
    n += 1
    pyglet.clock.schedule_once(get_results, 1.0)
    trial_end = time.time()


def get_results(dt):
    global ku, kud, kd, kud_list, mdt, dtstd, n, tc, tcs, sequence
#    ku.append(trial_start + 30.0)
#    while len(kd) > 0:
#        kud.append(ku.popleft() - kd.popleft() + 0)  # list up key_press_duration
#    kud_list.append(str(kud))
#    c = sum(kud)
#    cdt.append(c)
#    tcs.append(tc)
#    if kud:
#        m = np.mean(kud)
#        d = np.std(kud)
#    else:
#        m, d = 0, 0
#    mdt.append(m)
#    dtstd.append(d)
    if kd is None:
        latency = 30.0
    else:
        latency = kd - trial_start
    latencies.append(latency)
    print("--------------------------------------------------\n"
          "trial: " + str(n) + "/" + str(len(variation)) + '\n'
          "start: " + str(trial_start) + '\n'
          "end: " + str(trial_end) + '\n'
          "latency: " + str(latency) + '\n'
          "condition: " + str(sequence[n - 1]) + ', ' + str(sequence3[n - 1]) + '\n'
          "--------------------------------------------------")
    # Check the experiment continue or break
    if n != len(variation):
        pyglet.clock.schedule_once(exit_routine, 5.0)
    else:
        pyglet.app.exit()


def set_polygon(seq, seq2, seq3):
    global L, R, n
    # Set up polygon for stimulus
    R = pyglet.resource.image('stereograms/' + str(seq3) + 'rds' + str(seq) + str(seq2) + 'R.png')
    R = pyglet.sprite.Sprite(R)
    R.x = cntx + deg1 * iso + cal - R.width / 2.0
    R.y = cnty - R.height / 2.0
    L = pyglet.resource.image('stereograms/' + str(seq3) + 'rds' + str(seq) + str(seq2) + 'L.png')
    L = pyglet.sprite.Sprite(L)
    L.x = cntx - deg1 * iso - cal - L.width / 2.0
    L.y = cnty - L.height / 2.0


def prepare_routine():
    if n < len(variation):
        fixer()
        set_polygon(sequence[n], sequence2[n], sequence3[n])
    else:
        pass


# Store the start time
start = time.time()
win.push_handlers(resp_handler)

fixer()
set_polygon(sequence[0], sequence2[0], sequence3[0])

for i in sequence:
#    tc = 0  # Count transients
#    ku = deque([])  # Store unix time when key up
#    kd = deque([])  # Store unix time when key down
#    kud = []  # Differences between kd and ku
    kd = None

    pyglet.app.run()

# -------------- End loop -------------------------------

win.close()

# Store the end time
end_time = time.time()
daten = datetime.datetime.now()

# Write results onto csv
results = pd.DataFrame({'cnd': sequence,  # Store variance_A conditions
                        'inner_size': sequence2,
                        'test_eye': sequence3,
                        'latencies': latencies})
#                        'transient_counts': tcs,  # Store transient_counts
# Store cdt(target values) and input number of trials
#                        'mdt': mdt,
#                        'dtstd': dtstd,
#                        'key_press_list': kud_list})  # Store the key_press_duration list

os.makedirs('data', exist_ok=True)

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf='./data/DATE' + name + '.csv', index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u'開始日時: ' + str(start))
print(u'終了日時: ' + str(end_time))
print(u'経過時間: ' + str(end_time - start))
