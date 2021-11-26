#!/usr/bin/env python
# coding: utf-8

import os, wave, struct, copy
import numpy as np
from PIL import Image, ImageDraw
from display_info import *


to_dir = 'materials'
os.makedirs(to_dir, exist_ok=True)
to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)

# Input stereogram relative_size in cm unit
size = 2.0

# Input line relative_size in cm unit
line_length = 0.7  # 30pix is 42 min of arc on 57cm distance

# Input luminance of background
lb = 85  # 215, 84%
lm = (30, 30, 30)

# Input fixation point position in cm unit
ecc = 1

sz = round(resolution * (size / d_height))
ll = round(resolution * line_length / d_height)
f = 2 #round(sz * 0.023 / 2)  # 3.6 min of arc in 5 deg presentation area, actually 0.6 mm

# Input the disparity at pixel units.
disparity = 4 # 3.0pix, approximately 3*1.5 = 4.5'

eccentricity = round(1 / np.sqrt(2.0) * ecc / d_height * resolution)


def fixation(d):
    d.rectangle((int(sz) + eccentricity - f, int(sz) + eccentricity + f * 3,
                 int(sz) + eccentricity + f, int(sz) + eccentricity - f * 3),
                fill=(0, 0, 255), outline=None)
    d.rectangle((int(sz) + eccentricity - f * 3, int(sz) + eccentricity + f,
                 int(sz) + eccentricity + f * 3, int(sz) + eccentricity - f),
                fill=(0, 0, 255), outline=None)

# generate random pattern
def pattern(n, p, shape=(sz, sz)):
    rands = np.random.binomial(2, p, shape)

    img = Image.new("RGB", (int(shape[0]), int(shape[1])), (lb, lb, lb))
    draw = ImageDraw.Draw(img)

    y = 0
    for x in range(0, shape[0]):
        for y in range(0, shape[0]):
            if rands[x, y] != 0:
                draw.point((rands[x, y]*x, y), fill=lm)

    img.save(os.path.join('materials/rds' + str(n) + '.png'), quality=100)


pattern('outer0.1', 0.05)
pattern('inner0.1', 0.05, (int(sz/4), int(sz/4)))


# rds, requires disparity in pix, background image path and target image path
def stereogramize(disparity, outer, inner):
    # Two images prepare
    bg = Image.open(outer)
    tar = Image.open(inner)

    bg.paste(tar, (int(bg.width/2 - tar.width/2 + disparity/2), int(bg.height/2 - tar.height/2)))

    img_resize = bg.resize((int(bg.width*2), int(bg.height*2)))

    draw = ImageDraw.Draw(img_resize)
    draw.rectangle((img_resize.width / 2 - int(f / 2) - disparity, img_resize.height / 2 - ll / 2,
                    img_resize.width / 2 + int(f / 2) - disparity, img_resize.height / 2 + ll / 2),
                   fill=(int(lb*1.5), 0, 0), outline=None)

    fixation(draw)

    # Write images
    basename = os.path.basename('rds' + str(disparity) + '.png')
    img_resize.save(os.path.join(to_dir, basename), quality=100)


stereogramize(4, 'materials/rdsouter.png', 'materials/rdsinner.png')
stereogramize(-4, 'materials/rdsouter.png', 'materials/rdsinner.png')
stereogramize(4, 'materials/rdsouter0.1.png', 'materials/rdsinner0.1.png')
stereogramize(-4, 'materials/rdsouter0.1.png', 'materials/rdsinner0.1.png')


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
