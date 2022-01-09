# -*- coding: utf-8 -*-
import datetime
import os
import pyglet
import time
from collections import deque
import pandas as pd
from pyglet.image import AbstractImage

from display_info import *

# Prefernce
# ------------------------------------------------------------------------
test_eye = 'r'
cal = -58 # You can calibrate the convergence angle for better viewing.
# ------------------------------------------------------------------------

key = pyglet.window.key
win = win

# Load variable conditions
dat = pd.DataFrame()
iso = 8.0
draw_objects = []  # 描画対象リスト
end_routine = False  # Routine status to be exitable or not
tc = 0  # Count transients
tcs = []  # Store transients per trials
kud_list = []  # Store durations of key pressed
cdt = []  # Store sum(kud), cumulative reaction time on a trial.
mdt = []
dtstd = []
exit = True
n = 0

# Load resources
p_sound = pyglet.resource.media('materials/840Hz.wav', streaming=False)
beep_sound = pyglet.resource.media('materials/460Hz.wav', streaming=False)
pedestal: AbstractImage = pyglet.image.load('materials/pedestal.png')
fixr = pyglet.sprite.Sprite(pedestal, x=cntx + iso * deg1 + cal - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)
fixl = pyglet.sprite.Sprite(pedestal, x=cntx - iso * deg1 - cal - pedestal.width / 2.0, y=cnty - pedestal.height / 2.0)


# ----------- Core program following ----------------------------

# A getting key response function
class key_resp(object):
    def on_key_press(self, symbol, modifiers):
        global tc, exit, trial_start
        if exit is False and symbol == key.DOWN:
            kd.append(time.time())
            tc = tc + 1
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
        global tc
        if exit is False and symbol == key.DOWN:
            ku.append(time.time())
            tc = tc + 1


resp_handler = key_resp()


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
    global ku, kud, kd, kud_list, mdt, dtstd, n, tc, tcs, sequence
    ku.append(trial_start + 30.0)
    while len(kd) > 0:
        kud.append(ku.popleft() - kd.popleft() + 0)  # list up key_press_duration
    kud_list.append(str(kud))
    c = sum(kud)
    cdt.append(c)
    tcs.append(tc)
    if kud:
        m = np.mean(kud)
        d = np.std(kud)
    else:
        m, d = 0, 0
    mdt.append(m)
    dtstd.append(d)
    print("--------------------------------------------------")
    print("trial: " + str(n) + "/" + str(len(variation2)))
    print("start: " + str(trial_start))
    print("end: " + str(trial_end))
    print("key_pressed: " + str(kud))
    print("transient counts: " + str(tc))
    print("cdt: " + str(c))
    print("mdt: " + str(m))
    print("dtstd: " + str(d))
    print("condition: " + str(sequence[n - 1]))# + ', ' + str(sequence2[n - 1]) + ', ' + str(sequence3[n - 1]))
    print("--------------------------------------------------")
    # Check the experiment continue or break
    if n != len(variation2):
        pyglet.clock.schedule_once(exit_routine, 14.0)
    else:
        pyglet.app.exit()


def set_polygon(seq, seq2):
    global L, R, n
    if test_eye == ' l':
        # Set up polygon for stimulus
        R = pyglet.resource.image('stereograms/rds0' + str(seq) + str(int(seq2)) + '.png')
        R = pyglet.sprite.Sprite(R)
        R.x = cntx + deg1 * iso + cal - R.width / 2.0
        R.y = cnty - R.height / 2.0
        L = pyglet.resource.image('stereograms/rds00' + str(int(seq2)) + '.png') # the test bar
        L = pyglet.sprite.Sprite(L)
        L.x = cntx - deg1 * iso - cal - L.width / 2.0
        L.y = cnty - L.height / 2.0
    else:
        R = pyglet.resource.image('stereograms/rds00' + str(int(seq2)) + '.png')
        R = pyglet.sprite.Sprite(R)
        R.x = cntx + deg1 * iso + cal - R.width / 2.0
        R.y = cnty - R.height / 2.0
        L = pyglet.resource.image('stereograms/rds0' + str(seq) + str(int(seq2)) + '.png') # the test bar
        L = pyglet.sprite.Sprite(L)
        L.x = cntx - deg1 * iso - cal - L.width / 2.0
        L.y = cnty - L.height / 2.0

def prepare_routine():
    if n < len(variation2):
        fixer()
        set_polygon(sequence[n], sequence2[n])#, sequence3[n])
    else:
        pass


# Store the start time
start = time.time()
win.push_handlers(resp_handler)

fixer()
set_polygon(sequence[0], sequence2[0])#, sequence3[0])

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
#                        'continuity': sequence2,
#                        'test_eye': sequence3,
                        'transient_counts': tcs,  # Store transient_counts
                        'cdt': cdt,  # Store cdt(target values) and input number of trials
                        'mdt': mdt,
                        'dtstd': dtstd,
                        'key_press_list': kud_list})  # Store the key_press_duration list

os.makedirs('data', exist_ok=True)

name = str(daten)
name = name.replace(":", "'")
results.to_csv(path_or_buf='./data/DATE' + name + '.csv', index=False)  # Output experimental data

# Output following to shell, check this experiment
print(u'開始日時: ' + str(start))
print(u'終了日時: ' + str(end_time))
print(u'経過時間: ' + str(end_time - start))
