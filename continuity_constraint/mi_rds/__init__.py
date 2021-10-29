#!/usr/bin/env python
# coding: utf-8

import os, wave, struct, copy
import numpy as np
from PIL import Image, ImageDraw
from display_info import *

to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)

# Input stereogram relative_size in cm unit
size = 2.0

# Input line relative_size in cm unit
line_length = 0.5  # 30pix is 42 min of arc on 57cm distance

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

sz = round(resolution * (size / d_height))
ll = round(resolution * line_length / d_height)
f = round(sz * 0.023 / 2)  # 3.6 min of arc in 5 deg presentation area, actually 0.6 mm

# Input the disparity at pixel units.
disparity = 4 # 3.0pix, approximately 3*1.5 = 4.5'

eccentricity = round(1 / np.sqrt(2.0) * ecc / d_height * resolution)


def pattern(shape=(sz, sz)):
    rands = np.random.randint(0, 2, shape)
    offset = np.random.randint(0, 2, shape)
    for i in range(0, rands.shape[1]):
        randrow = list(rands[i, ])
        del randrow[0:i]
        randrow.extend(list(offset[i:shape[1]]))
        print(randrow)
        rands[i, ] = randrow
    return rands


pat = pattern()

# rds
def stereogramize(disparity, inner, pat):
    # Two images prepare
    img = Image.new("RGB", (int(sz), int(sz)), (lb, lb, lb))
    draw = ImageDraw.Draw(img)

    img2 = Image.new("RGB", (int(sz), int(sz)), (lb, lb, lb))
    draw2 = ImageDraw.Draw(img2)

    # Fill the targets area
#    draw.rectangle((int(sz / 2) - int(inner / 2) - disparity / 2, 0,
#                    int(sz / 2) + int(inner / 2) - disparity / 2, sz), fill=(lb, lb, lb),
#                   outline=None)
#    draw2.rectangle((int(sz / 2) - int(inner / 2) + disparity / 2, 0,
#                     int(sz / 2) + int(inner / 2) + disparity / 2, sz), fill=(lb, lb, lb),
#                    outline=None)

    # Drawing the targets
    for i in range(0, int(sz)):
        for j in range(0, int(sz) + 1):
            if pat != 0:
                draw.point((pat + ((sz / 2) - (inner / 2)) - 1 - disparity / 2, i), fill=(0, 0, 0))
                draw2.point((pat + (sz / 2) - (inner / 2) - 1 + disparity / 2, i), fill=(0, 0, 0))

    img_resize = img.resize((int(img.width*2), int(img.height*2)))
    img2_resize = img2.resize((int(img2.width*2), int(img2.height*2)))

    # Write images
    basenameR = os.path.basename('rds' + str(disparity) + str(inner) + 'R.png')
    basenameL = os.path.basename('rds' + str(disparity) + str(inner) + 'L.png')
    img_resize.save(os.path.join(to_dir, basenameR), quality=100)
    img2_resize.save(os.path.join(to_dir, basenameL), quality=100)


stereogramize(6, sz/2, sz)


# stereogram without stimuli
img = Image.new("RGB", (sz, sz), (lb, lb, lb))
draw = ImageDraw.Draw(img)

to_dir = 'materials'
os.makedirs(to_dir, exist_ok=True)
basename = os.path.basename('pedestal.png')
img.save(os.path.join(to_dir, basename), quality=100)

# sound files
# special thank: @kinaonao  https://qiita.com/kinaonao/items/c3f2ef224878fbd232f5

# sin波
# --------------------------------------------------------------------------------------------------------------------
def create_wave(A, f0, fs, t, name):  # A:振幅,f0:基本周波数,fs:サンプリング周波数,再生時間[s],n:名前
    # nポイント
    # --------------------------------------------------------------------------------------------------------------------
    point = np.arange(0, fs * t)
    sin_wave = A * np.sin(2 * np.pi * f0 * point / fs)

    sin_wave = [int(x * 32767.0) for x in sin_wave]  # 16bit符号付き整数に変換

    # バイナリ化
    binwave = struct.pack("h" * len(sin_wave), *sin_wave)

    # サイン波をwavファイルとして書き出し
    w = wave.Wave_write(os.path.join(to_dir, str(name) + ".wav"))
    p = (1, 2, fs, len(binwave), 'NONE',
         'not compressed')  # (チャンネル数(1:モノラル,2:ステレオ)、サンプルサイズ(バイト)、サンプリング周波数、フレーム数、圧縮形式(今のところNONEのみ)、圧縮形式を人に判読可能な形にしたもの？通常、 'NONE' に対して 'not compressed' が返されます。)
    w.setparams(p)
    w.writeframes(binwave)
    w.close()


create_wave(1, 460, 44100, 1.0, '460Hz')
create_wave(1, 840, 44100, 0.1, '840Hz')
