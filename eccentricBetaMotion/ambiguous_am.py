#!/usr/bin/env python
# coding: utf-8

import os, pyglet, time, datetime, random, copy, math
from pyglet.gl import *
from pyglet.image import AbstractImage
from collections import deque
import pandas as pd
import numpy as np
import display_info

# Prefernce
# ------------------------------------------------------------------------
rept = 3
exclude_mousePointer = False
# ------------------------------------------------------------------------

# Get display information
display = pyglet.canvas.get_display()
screens = display.get_screens()
win = pyglet.window.Window(style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
win.set_fullscreen(fullscreen=True, screen=screens[len(screens) - 1])  # Present secondary display
key = pyglet.window.key
fixer = pyglet.graphics.Batch()
batch = pyglet.graphics.Batch()

# Load variable conditions
deg1 = display_info.deg1
iso = 8
cntx = screens[len(screens) - 1].width / 2  # Store center of screen about x positon
cnty = screens[len(screens) - 1].height / 3  # Store center of screen about y position
draw_objects = []  # 描画対象リスト
end_routine = False  # Routine status to be exitable or not
tc = 0  # Count transients
tcs = []  # Store transients per trials
trial_starts = []  # Store time when trial starts
kud_list = []  # Store durations of key pressed
cdt = []  # Store sum(kud), cumulative reaction time on a trial.
mdt = []
dtstd = []
exit = True
n = 0
oneshot = True

# Load sound resource
## Sounds
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal: AbstractImage = pyglet.image.load('materials/pedestal.png')
fixr = pyglet.sprite.Sprite(pedestal, x=cntx + iso * deg1 - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)
fixl = pyglet.sprite.Sprite(pedestal, x=cntx - iso * deg1 - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)

# Images
left_half1 = pyglet.resource.image('stereograms/left_half.png')
left_half1 = pyglet.sprite.Sprite(left_half1)
left_half1.x = cntx + deg1 * iso - left_half1.width / 2.0
left_half1.y = cnty - left_half1.height / 2.0
right_half1 = pyglet.resource.image('stereograms/right_half.png')
right_half1 = pyglet.sprite.Sprite(right_half1)
right_half1.x = cntx - deg1 * iso - right_half1.width / 2.0
right_half1.y = cnty - right_half1.height / 2.0

right_half2 = pyglet.resource.image('stereograms/right_half.png')
right_half2 = pyglet.sprite.Sprite(right_half2)
right_half2.x = cntx + deg1 * iso - left_half1.width / 2.0
right_half2.y = cnty - left_half1.height / 2.0
left_half2 = pyglet.resource.image('stereograms/left_half.png')
left_half2 = pyglet.sprite.Sprite(left_half2)
left_half2.x = cntx - deg1 * iso - right_half2.width / 2.0
left_half2.y = cnty - right_half2.height / 2.0

variation = [1]
file_names = list(np.repeat(variation, rept))
r = random.randint(0, math.factorial(len(file_names)))
random.seed(r)
sequence = random.sample(file_names, len(file_names))

print(sequence)

# A getting key response function
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc, exit, trial_start
        if exit == False and symbol == key.DOWN:
            kd.append(time.time())
            tc = tc + 1
        if exit == True and symbol == key.UP:
            exit = False
            p_sound.play()
            del draw_objects[:]
            draw_objects.extend([left_half1, left_half2, right_half1, right_half2])
            pyglet.clock.schedule_interval(on_move, 0.25)
            pyglet.clock.schedule_once(delete, 30.0)
            trial_start = time.time()
        if symbol == key.ESCAPE:
            win.close()
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        global tc
        if exit == False and symbol == key.DOWN:
            ku.append(time.time())
            tc = tc + 1


resp_handler = key_resp()


def fixer():
    draw_objects.append(fixl)
    draw_objects.append(fixr)


# Remove stimulus
def delete(dt):
    global n, dl, trial_end, exit
    exit = False
    pyglet.clock.unschedule(on_move)
    del draw_objects[:]
    p_sound.play()
    pyglet.clock.schedule_once(exit_routine, 30.0)
    trial_end = time.time()
    n += 1
    Get_results()


def exit_routine(dt):
    global exit
    exit = True
    beep_sound.play()
    fixer()
    pyglet.app.exit()


def Get_results():
    global ku, kud, kd, kud_list, mdt, dtstd, n, tc, tcs, trial_end, trial_start, sequence, file_names
    ku.append(trial_start + 30.0)
    while len(kd) > 0:
        kud.append(ku.popleft() - kd.popleft() + 0)  # list up key_press_duration
    kud_list.append(str(kud))
    c = sum(kud)
    cdt.append(c)
    tcs.append(tc)
    if kud == []:
        kud.append(0)
    m = np.mean(kud)
    d = np.std(kud)
    mdt.append(m)
    dtstd.append(d)
    print("--------------------------------------------------")
    print("trial: " + str(n) + "/" + str(len(file_names)))
    print("start: " + str(trial_start))
    print("end: " + str(trial_end))
    print("key_pressed: " + str(kud))
    print("transient counts: " + str(tc))
    print("cdt: " + str(c))
    print("mdt: " + str(m))
    print("dtstd: " + str(d))
    print("condition: " + str(sequence[n - 1]))
    print("--------------------------------------------------")
    # Check the experiment continue or break
    if n != len(file_names):
        n += 1
        pass
    else:
        pyglet.app.exit()


def set_polygon(seq):
    pass


@win.event
def on_draw():
    # Refresh window
    win.clear()
    # 描画対象のオブジェクトを描画する
    for draw_object in draw_objects:
        draw_object.draw()


@win.event
def on_move(dt):
    draw_objects.reverse()
    draw_objects[0].draw()
    draw_objects[1].draw()


# Store the start time
start = time.time()
win.push_handlers(resp_handler)

fixer()

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
results = pd.DataFrame({'distance': sequence,  # Store variance_A conditions
                        "transient_counts": tcs,  # Store transient_counts
                        "cdt": cdt,  # Store cdt(target values) and input number of trials
                        "mdt": mdt,
                        "dtstd": dtstd,
                        "key_press_list": kud_list})  # Store the key_press_duration list

if os.path.exists("data") == False:
    os.mkdir("data")

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf="./data/DATA" + name + ".csv", index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u"開始日時: " + str(start))
print(u"終了日時: " + str(end_time))
print(u"経過時間: " + str(end_time - start))
