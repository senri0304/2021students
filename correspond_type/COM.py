# -*- coding: utf-8 -*-
import os, pyglet, time, datetime, random, copy, math
from typing import List, Any

from pyglet.gl import *
from pyglet.image import AbstractImage
from collections import deque
import pandas as pd
import numpy as np
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
win.set_fullscreen(fullscreen=True, screen=screens[len(screens)-1])  # Present secondary display
win.set_exclusive_mouse(exclude_mousePointer)  # Exclude mouse pointer
key = pyglet.window.key

# Load variable conditions
deg1 = display_info.deg1
cntx = screens[len(screens)-1].width / 2  # Store center of screen about x position
cnty = screens[len(screens)-1].height / 3  # Store center of screen about y position
dat = pd.DataFrame()
iso = 7.5
draw_objects = []  # 描画対象リスト
end_routine = False  # Routine status to be exitable or not
tcs_test = []  # Store transients per trials
tcs_sup = []
press_timing_test = []  # Store durations of key pressed
press_timing_sup = []
release_timing_test = []
release_timing_sup = []
cdt_test = []  # Store sum(kud), cumulative reaction time on a trial.
cdt_sup = []
mdt_test = []
mdt_sup = []
dtstd_test = []
dtstd_sup = []
exit = True
n = 0

# Load resources
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal: AbstractImage = pyglet.image.load('materials/pedestal.png')
fixr = pyglet.sprite.Sprite(pedestal, x=cntx+iso*deg1-pedestal.width/2.0, y=cnty-pedestal.height/2.0)
fixl = pyglet.sprite.Sprite(pedestal, x=cntx-iso*deg1-pedestal.width/2.0, y=cnty-pedestal.height/2.0)


variation = [0.5, 1, 2, 4]
test_eye = [1, -1]

# Replicate for repetition
variation2 = variation*len(test_eye)*rept
test_eye2 = list(np.repeat(test_eye, len(variation2)/len(test_eye)))

# Randomize
r = random.randint(0, math.factorial(len(variation2)))
random.seed(r)
sequence = random.sample(variation2, len(variation2))
random.seed(r)
sequence3 = random.sample(test_eye2, len(variation2))

print(sequence)
print(sequence3)


# ----------- Core program following ----------------------------

# A getting key response function
# Press left during the red bar disappears
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc_test, tc_sup, exit, trial_start
        if exit is False and symbol == key.LEFT:
            if test_eye != 1:
                kd_test.append(time.time())
                tc_test = tc_test + 1
            else:
                kd_sup.append(time.time())
                tc_sup = tc_sup + 1
        if exit is False and symbol == key.RIGHT:
            if test_eye != 1:
                kd_sup.append(time.time())
                tc_sup = tc_sup + 1
            else:
                kd_test.append(time.time())
                tc_test = tc_test + 1
        if exit is True and symbol == key.UP:
            p_sound.play()
            exit = False
            pyglet.clock.schedule_once(delete, 30.0)
            replace()
            trial_start = time.time()
        if symbol == key.ESCAPE:
            win.close()
            pyglet.app.exit()

    def on_key_release(self, symbol, modifiers):
        global tc_test, tc_sup
        if exit is False and symbol == key.LEFT:
            if test_eye != 1:
                ku_test.append(time.time())
                tc_test = tc_test + 1
            else:
                ku_sup.append(time.time())
                tc_sup = tc_sup + 1
        if exit is False and symbol == key.RIGHT:
            if test_eye != 1:
                ku_sup.append(time.time())
                tc_sup = tc_sup + 1
            else:
                ku_test.append(time.time())
                tc_test = tc_test + 1


# Store objects into draw_objects
def fixer():
    draw_objects.append(fixl)
    draw_objects.append(fixr)


def replace():
    del draw_objects[:]
    fixer()
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
    if len(ku_test) != len(kd_test):
        ku_test.append(trial_start + 30.0)
    if len(ku_sup) != len(kd_sup):
        ku_sup.append(trial_start + 30.0)
    press_timing_test.append(str(np.array(kd_test) - trial_start))
    press_timing_sup.append(str(np.array(kd_sup) - trial_start))
    release_timing_test.append(str(np.array(ku_test) - trial_start))
    release_timing_sup.append(str(np.array(ku_sup) - trial_start))
    while len(kd_test) > 0:
        kud_test.append(ku_test.popleft() - kd_test.popleft() + 0)  # list up key_press_duration
    while len(kd_sup) > 0:
        kud_sup.append(ku_sup.popleft() - kd_sup.popleft() + 0)  # list up key_press_duration
    ct, cs = sum(kud_test), sum(kud_sup)
    cdt_test.append(ct)
    cdt_sup.append(cs)
    tcs_test.append(tc_test)
    tcs_sup.append(tc_sup)
    if kud_test is not None:
        kud_test.append(0)
    if kud_sup is not None:
        kud_sup.append(0)
    ml, mr = np.mean(kud_test), np.mean(kud_sup)
    dl, dr = np.std(kud_test), np.std(kud_sup)
    mdt_test.append(ml)
    mdt_sup.append(mr)
    dtstd_test.append(dl)
    dtstd_sup.append(dr)
    print("--------------------------------------------------\n"
          "trial: " + str(n) + "/" + str(len(sequence)) + '\n'
          "start: " + str(trial_start) + '\n'
          "end: " + str(trial_end) + '\n'
#    "key_pressed: " + str(kud_l) + '\n'
          "transient counts: " + str(tc_test) + ', ' + str(tc_sup) + '\n'
          "cdt: " + str(ct) + ', ' + str(cs) + '\n'
          "mdt: " + str(ml) + ', ' + str(mr) + '\n'
          "dtstd: " + str(dl) + ', ' + str(dr) + '\n'
          "condition: " + str(sequence[n - 1]) + str(sequence3[n - 1]) + '\n'
          "--------------------------------------------------")
    # Check the experiment continue or break
    if n != len(sequence):
        pyglet.clock.schedule_once(exit_routine, 14.0)
    else:
        pyglet.app.exit()


# R and L stores suppressor and test, respectively
def set_polygon(seq, seq3):
    global L, R, n
    # Set up polygon for stimulus
    R = pyglet.resource.image('stereograms/ls.png')
    R = pyglet.sprite.Sprite(R)
    R.x = cntx + deg1 * iso * seq3 - R.width / 2.0
    R.y = cnty - R.height / 2.0
    L = pyglet.resource.image('stereograms/' + str(seq) + 'ls.png')
    L = pyglet.sprite.Sprite(L)
    L.x = cntx - deg1 * iso * seq3 - L.width / 2.0
    L.y = cnty - L.height / 2.0


def prepare_routine():
    if n < len(sequence):
        fixer()
        set_polygon(sequence[n], sequence3[n])
    else:
        pass


# Store the start time
start = time.time()
resp_handler = key_resp()
win.push_handlers(resp_handler)

fixer()
set_polygon(sequence[0], sequence3[0])


for i in sequence:
    tc_test = 0  # Count transients
    tc_sup = 0  # Count transients
    ku_test = deque([])  # Store unix time when key up
    kd_test = deque([])  # Store unix time when key down
    kud_test = []  # Differences between kd and ku
    ku_sup = deque([])  # Store unix time when key up
    kd_sup = deque([])  # Store unix time when key down
    kud_sup = []  # Differences between kd and ku

    pyglet.app.run()

# -------------- End loop -------------------------------

win.close()

# Store the end time
end_time = time.time()
daten = datetime.datetime.now()

# Write results onto csv
results = pd.DataFrame({'cnd': sequence,  # Store variance_A conditions
                        'test_eye': sequence3,
                        'transient_counts_test': tcs_test,  # Store transient_counts
                        'cdt_test': cdt_test,  # Store cdt(target values) and input number of trials
                        'mdt_test': mdt_test,
                        'dtstd_test': dtstd_test,
                        'press_timing_test': press_timing_test,  # Store the key_press_duration list
                        'release_timing_test': release_timing_test,
                        'transient_counts_sup': tcs_sup,  # Store transient_counts
                        'cdt_sup': cdt_sup,  # Store cdt(target values) and input number of trials
                        'mdt_sup': mdt_sup,
                        'dtstd_sup': dtstd_sup,
                        'press_timing_sup': press_timing_sup,
                        'release_timing_sup': release_timing_sup})  # Store the key_press_duration list

os.makedirs('data', exist_ok=True)

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf='./data/DATE' + name + '.csv', index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u'開始日時: ' + str(start))
print(u'終了日時: ' + str(end_time))
print(u'経過時間: ' + str(end_time - start))
