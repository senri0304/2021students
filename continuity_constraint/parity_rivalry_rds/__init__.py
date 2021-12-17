#!/usr/bin/env python
# coding: utf-8

import os, wave, struct, copy
import numpy as np
from PIL import Image, ImageDraw
from display_info import *


to_dir = 'materials'
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
eccentricity = round(1 / np.sqrt(2.0) * ecc / d_height * resolution)


def fixation(d):
    d.rectangle((int(sz) + eccentricity - f, int(sz) + eccentricity + f * 3,
                 int(sz) + eccentricity + f, int(sz) + eccentricity - f * 3),
                fill=(0, 0, 255), outline=None)
    d.rectangle((int(sz) + eccentricity - f * 3, int(sz) + eccentricity + f,
                 int(sz) + eccentricity + f * 3, int(sz) + eccentricity - f),
                fill=(0, 0, 255), outline=None)

# generate random pattern
def pattern(n, p, size):
    shape = (size, size)
    rands = np.random.binomial(2, p, shape)

    img = Image.new("RGBA", (int(shape[0]), int(shape[1])), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    y = 0
    for x in range(0, shape[0]):
        for y in range(0, shape[0]):
            if rands[x, y] != 0:
                draw.point((rands[x, y]*x, y), fill=lm)

    img.save(os.path.join('materials/rds' + str(n) + '.png'), quality=100)


# stereogram without stimuli
img = Image.new("RGBA", (sz*2, sz*2), (lb, lb, lb, 255))
draw = ImageDraw.Draw(img)

basename = os.path.basename('gbg.png')
img.save(os.path.join(to_dir, basename), quality=100)


to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)


# rds, requires line size in proportion, background image path and target image path
def stereogramize(disparity, size, n, outer='materials/rdsnoise.png'):
    # Two images prepare
    bg = Image.open(outer)
    gbg = Image.open('materials/gbg.png')

    img_resize = bg.resize((int(bg.width*2), int(bg.height*2)))
    img = Image.new('RGBA', (sz*2, sz*2), (lb, lb, lb, 0))
    img.paste(img_resize, (int(gbg.width/2 - img_resize.width/2) + disparity, int(gbg.height/2 - img_resize.height/2)))
    gbg = Image.alpha_composite(gbg, img)
    draw = ImageDraw.Draw(gbg)
    if size == 0:
        draw.rectangle((int(gbg.width / 2) - int(f / 2), int(gbg.height / 2) - int(ll / 2),
                        int(gbg.width / 2) + int(f / 2), int(gbg.height / 2) + int(ll / 2)),
                       fill=(int(lb*1.5), 0, 0), outline=None)
    else:
        draw.rectangle((int(gbg.width / 2) - int((ll / 2)*size), int(gbg.height / 2) - int(f / 2),
                        int(gbg.width / 2) + int((ll / 2)*size), int(gbg.height / 2) + int(f / 2)),
                       fill=(int(lb*1.5), 0, 0), outline=None)

    fixation(draw)

    # Write images
    basename = os.path.basename('rds' + str(disparity) + str(size) + str(n) + '.png')
    gbg.save(os.path.join(to_dir, basename), quality=100)


loop = 0
for i in variation:
    for loop in range(1, 4):
        pattern('noise', 0.3, int(sz/2))
        stereogramize(0, 0, loop)
        pattern('noise', 0.3, int(sz/2))
        stereogramize(0, i, loop)

# stereogram without stimuli
img = Image.new("RGB", (sz*2, sz*2), (lb, lb, lb))
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
