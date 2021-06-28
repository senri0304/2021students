#!/usr/bin/env python
# coding: utf-8

import os, wave, struct
from PIL import Image, ImageDraw
from display_info import *

to_dir = 'stereograms'
os.makedirs(to_dir, exist_ok=True)

disparity = f*2

# fixation point
def fixation(d):
    d.rectangle((int(sz / 2) - f, int(sz / 2) + deg1 + f * 3,
                 int(sz / 2) + f, int(sz / 2) + deg1 - f * 3),
                fill=(0, 0, 255), outline=None)
    d.rectangle((int(sz / 2) - f * 3, int(sz / 2) + deg1 + f,
                 int(sz / 2) + f * 3, int(sz / 2) + deg1 - f),
                fill=(0, 0, 255), outline=None)


# ls
def stereogramize(p=1, q=1, r=1):
    img = Image.new("RGB", (sz, sz), (lb, lb, lb))
    draw = ImageDraw.Draw(img)
    img2 = Image.new("RGB", (sz, sz), (lb, lb, lb))
    draw2 = ImageDraw.Draw(img2)

    draw.rectangle((int(sz / 2) - int(ll / 2), int(sz / 2) + int(f / 2),
                    int(sz / 2) + int(ll / 2), int(sz / 2) - int(f / 2)),
                   fill=(0, 0, 0), outline=None)

    draw.rectangle((int(sz / 2) - int(f / 2), int(sz / 2) + int(ll / 2)*p,
                    int(sz / 2) + int(f / 2), int(sz / 2)),
                   fill=(0, 0, 0), outline=None)

    draw2.rectangle((int(sz / 2) - int(ll / 2), int(sz / 2) + int(f / 2),
                     int(sz / 2) + int(ll / 2), int(sz / 2) - int(f / 2)),
                    fill=(0, 0, 0), outline=None)

    draw2.rectangle((int(sz / 2) - int(f / 2), int(sz / 2) + int(ll / 2)*-p,
                     int(sz / 2) + int(f / 2), int(sz / 2)),
                    fill=(0, 0, 0), outline=None)

    draw.rectangle((int(sz / 2) - int(ll / 2) + disparity*q, int(sz / 2) + int(f / 2) + int(eccentricity)*2,
                    int(sz / 2) + int(ll / 2) + disparity*q, int(sz / 2) - int(f / 2) + int(eccentricity)*2),
                   fill=(0, 0, 0), outline=None)

    draw.rectangle((int(sz / 2) - int(ll / 2), int(sz / 2) + int(f / 2) - int(eccentricity)*2,
                    int(sz / 2) + int(ll / 2), int(sz / 2) - int(f / 2) - int(eccentricity)*2),
                   fill=(0, 0, 0), outline=None)

    draw2.rectangle((int(sz / 2) - int(ll / 2) + disparity * -q, int(sz / 2) + int(f / 2) + int(eccentricity)*2,
                     int(sz / 2) + int(ll / 2) + disparity * -q, int(sz / 2) - int(f / 2) + int(eccentricity)*2),
                    fill=(0, 0, 0), outline=None)

    draw2.rectangle((int(sz / 2) - int(f / 2), int(sz / 2) + int(ll / 2) - int(eccentricity)*2,
                     int(sz / 2) + int(f / 2), int(sz / 2) - int(ll / 2) - int(eccentricity)*2),
                    fill=(0, 0, 0), outline=None)


#    fixation(draw)

    basename = os.path.basename(str(p) + str(q) + 'lsh.png')
    img.save(os.path.join(to_dir, basename), quality=100)
    basename = os.path.basename(str(p) + str(q) + 'lsv.png')
    img2.save(os.path.join(to_dir, basename), quality=100)


stereogramize()
stereogramize(-1)
stereogramize(1, -1)
stereogramize(-1, -1)

# stereogram without stimuli
img = Image.new("RGB", (sz, sz), (lb, lb, lb))
draw = ImageDraw.Draw(img)

#fixation(draw)

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
