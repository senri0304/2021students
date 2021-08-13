#!/usr/bin/env python
# coding: utf-8

import os, wave, struct
from PIL import Image, ImageDraw
from display_info import *

to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)


# fixation point
def fixation(d):
    d.rectangle((int(sz / 2) - f, int(sz / 2) + deg1*0.8 + f * 3,
                 int(sz / 2) + f, int(sz / 2) + deg1*0.8 - f * 3),
                fill=(0, 0, 255), outline=None)
    d.rectangle((int(sz / 2) - f * 3, int(sz / 2) + deg1*0.8 + f,
                 int(sz / 2) + f * 3, int(sz / 2) + deg1*0.8 - f),
                fill=(0, 0, 255), outline=None)


# Generate RDSs
def stereogramize(disparity, inner, num):
    # Two images prepare
    img = Image.new("RGB", (int(sz), int(sz)), (lb, lb, lb))
    draw = ImageDraw.Draw(img)

    img2 = Image.new("RGB", (int(sz), int(sz)), (lb, lb, lb))
    draw2 = ImageDraw.Draw(img2)

    # Draw the planes of RDSs
    for i in range(0, int(sz)):
        for j in range(1, int(sz) + 1):
            x = np.round(np.random.binomial(1, 0.5, 1)) * j
            draw.point((x - 1, i), fill=(0, 0, 0))
            draw2.point((x - 1, i), fill=(0, 0, 0))

    # Fill the targets area
    draw.rectangle((int(sz / 2) - int(inner / 2) - disparity / 2, int(sz / 2) + int(inner / 2),
                    int(sz / 2) + int(inner / 2) - disparity / 2, int(sz / 2) - int(inner / 2)), fill=(lb, lb, lb),
                   outline=None)
    draw2.rectangle((int(sz / 2) - int(inner / 2) + disparity / 2, int(sz / 2) + int(inner / 2),
                     int(sz / 2) + int(inner / 2) + disparity / 2, int(sz / 2) - int(inner / 2)), fill=(lb, lb, lb),
                    outline=None)

    # Drawing the targets
    for i in range(0, int(inner) + 1):
        for j in range(0, int(inner) + 1):
            x = np.round(np.random.binomial(1, 0.5, 1)) * (1 + j)
            if x != 0:
                draw.point((x + ((sz / 2) - (inner / 2)) - 1 - disparity / 2, i + (sz / 2) - (inner / 2)), fill=(0, 0, 0))
                draw2.point((x + (sz / 2) - (inner / 2) - 1 + disparity / 2, i + (sz / 2) - (inner / 2)), fill=(0, 0, 0))

    fixation(draw)
    fixation(draw2)

    img_resize = img.resize((int(img.width*2), int(img.height*2)))
    img2_resize = img2.resize((int(img2.width*2), int(img2.height*2)))

    # Write images
    basenameR = os.path.basename(str(num) + 'rds' + str(disparity) + str(inner) + 'R.png')
    basenameL = os.path.basename(str(num) + 'rds' + str(disparity) + str(inner) + 'L.png')
    img_resize.save(os.path.join(to_dir, basenameR), quality=100)
    img2_resize.save(os.path.join(to_dir, basenameL), quality=100)


for i in range(1, 6):
    stereogramize(variation[0], inner_size[0], i)
    stereogramize(variation[1], inner_size[0], i)
    stereogramize(variation[0], inner_size[1], i)
    stereogramize(variation[1], inner_size[1], i)


# stereogram without stimuli
img = Image.new("RGB", (sz, sz), (lb, lb, lb))
draw = ImageDraw.Draw(img)

fixation(draw)

img_resize = img.resize((int(img.width * 2), int(img.height * 2)))

to_dir = 'materials'
os.makedirs(to_dir, exist_ok=True)
basename = os.path.basename('pedestal.png')
img_resize.save(os.path.join(to_dir, basename), quality=100)

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
