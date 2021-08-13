#!/usr/bin/env python
# coding: utf-8

import os, pyglet, wave, struct
import numpy as np
from PIL import Image, ImageDraw
from display_info import *

to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)

# Input stereogram size in cm unit
size = 5.0

# Input line size in cm unit
line_length = 0.7  # 30pix is 42 min of arc on 57cm distance

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
disparity = f*2

eccentricity = round(1 / np.sqrt(2.0) * ecc / d_height * resolution)*2


# fixation point
def fixation(d):
    d.rectangle((int(sz / 2) + eccentricity - f, int(sz / 2) + eccentricity + f * 3,
                 int(sz / 2) + eccentricity + f, int(sz / 2) + eccentricity - f * 3),
                fill=(0, 0, 255), outline=None)
    d.rectangle((int(sz / 2) + eccentricity - f * 3, int(sz / 2) + eccentricity + f,
                 int(sz / 2) + eccentricity + f * 3, int(sz / 2) + eccentricity - f),
                fill=(0, 0, 255), outline=None)


def draw_dot(d, x_pos, y_pos, t):
    d.rectangle((int(sz / 2) + int(f / 2) + x_pos + disparity * t, int(sz / 2) + y_pos,
                 int(sz / 2) - int(f / 2) + x_pos + disparity * t, int(sz / 2) + y_pos - int(f)),
                fill=(0, 0, 0), outline=None)


# ls
def stereogramize(m, n, t=1, q=True): # 引数nはinner dotsの中央からの遷移量、引数tは視差の種類(交差or非交差)、引数qは遷移するドットを中央1点か3点か
    img = Image.new("RGB", (sz, sz), (lb, lb, lb))
    draw = ImageDraw.Draw(img)

    distance = 2 # 2 dots correspond half of bar's width
    ln = 0.8 # when ln = 0.8, shift scale factor n = 10 locates a dot at centre.
    if q:
        n2, m2 = n, -m
    else:
        n2, m2 = 0, 0
    # outer dots
    draw_dot(draw, 0, int(ll*ln), t)
    draw_dot(draw, 0, -int(ll*ln), t)
    # inner dots
    draw_dot(draw, f*m2, int(ll*ln) - distance*15 + distance*n2, t)
    draw_dot(draw, f*m, int(ll*ln) - distance*10 + distance*n, t)
    draw_dot(draw, f*m2, int(ll*ln) - distance*5 + distance*n2, t)

    fixation(draw)

    basename = os.path.basename(str(m) + str(n) + 'ls' + str(t) + str(q) + '.png')
    img.save(os.path.join(to_dir, basename), quality=100)


# 正の数を渡すとinner dotsが下にずれる
for i in [0, 1, -1]:
    stereogramize(i, 0, 1)
    stereogramize(i, 0, -1)
    stereogramize(i, 0, 1, False)
    stereogramize(i, 0, -1, False)


# stereogram without stimuli
img = Image.new("RGB", (sz, sz), (lb, lb, lb))
draw = ImageDraw.Draw(img)

fixation(draw)

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
