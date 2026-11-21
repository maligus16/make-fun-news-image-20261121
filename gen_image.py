#!/usr/bin/env python3
"""Render the 21 November 2026 front page (1024x1024) from stories.json.

Written from scratch in this session. All counts (story total, region
totals, brief numbers) are derived from stories.json at runtime, so the
masthead, the region bar and the numbered list can never disagree.
"""
import json
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "stories.json"), encoding="utf-8"))

W, H = 1024, 1024
PAPER = (246, 240, 224)
INK = (26, 26, 26)
RED = (163, 31, 31)
NAVY = (22, 35, 63)
GRAY = (96, 89, 76)
LIGHT = (232, 224, 206)
SKY = (38, 68, 110)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_IT = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, int(round(size)))


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns list of lines that fit width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start, width, max_lines):
    """Largest font size (<= start) whose wrap fits max_lines."""
    size = start
    while size > 7:
        fnt = font(path, size)
        if len(wrap(draw, text, fnt, width)) <= max_lines:
            return fnt
        size -= 0.5
    return font(path, 7)


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def chip(draw, x, y, text, fnt, fg=(255, 255, 255), bg=RED, pad=4):
    w = draw.textlength(text, font=fnt) + pad * 2
    h = fnt.size + pad
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    draw.text((x + pad, y + pad // 2 - 1), text, font=fnt, fill=fg)
    return w


# ---------------------------------------------------------------- world map
# Simplified continent outlines as (lon, lat) polygons.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-85, 80), (-80, 73),
     (-75, 72), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 24),
     (-115, 30), (-120, 34), (-125, 40), (-125, 49), (-130, 55),
     (-145, 60), (-155, 58), (-162, 55)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-25, 70), (-40, 76), (-58, 74)],
    # South America
    [(-80, 10), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-55, -35), (-65, -40), (-70, -50),
     (-70, -55), (-74, -40), (-72, -20), (-80, -5)],
    # Asia (drawn before Europe so Europe sits on top)
    [(30, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (160, 69), (170, 67), (178, 65), (170, 60), (162, 56), (158, 52),
     (150, 59), (142, 55), (140, 50), (135, 45), (130, 42), (127, 40),
     (122, 38), (120, 32), (122, 28), (115, 22), (108, 18), (105, 10),
     (100, 8), (98, 12), (95, 16), (92, 20), (88, 22), (85, 19), (80, 15),
     (77, 8), (75, 12), (72, 20), (66, 25), (60, 25), (57, 26), (52, 28),
     (50, 30), (48, 30), (44, 29), (40, 28), (38, 25), (35, 28), (34, 28),
     (36, 36), (33, 36), (30, 36), (27, 37), (26, 40), (28, 45), (30, 46),
     (32, 48), (35, 52), (40, 55), (45, 58), (50, 60), (45, 62), (40, 65),
     (35, 68)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 59), (30, 60), (28, 62), (24, 65),
     (18, 69), (12, 71), (18, 70), (25, 71), (30, 70), (40, 68), (44, 68),
     (40, 60), (35, 55), (30, 50), (28, 46), (23, 40), (19, 42), (12, 44),
     (8, 44), (3, 42), (-2, 37)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 20), (-17, 15), (-12, 8),
     (-8, 4), (-4, 5), (6, 4), (9, 4), (13, 0), (12, -6), (13, -12),
     (12, -18), (16, -28), (20, -35), (28, -33), (32, -26), (35, -20),
     (40, -15), (40, -10), (46, -1), (51, 2), (51, 11), (44, 11), (40, 15),
     (38, 18), (35, 22), (32, 28), (25, 32), (19, 32), (11, 34), (10, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (136, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    # Indonesia
    [(95, 5), (100, 2), (106, -2), (112, -6), (118, -8), (124, -9),
     (130, -3), (135, -1), (138, -4), (132, -8), (120, -10), (110, -7),
     (102, -4), (96, 2)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (144, 44),
     (141, 45), (139, 40), (136, 36), (132, 33)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 58), (-2, 58), (0, 53), (1, 51), (-3, 50)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (175, -41),
     (172, -43), (168, -46)],
    # Madagascar
    [(44, -16), (47, -15), (50, -17), (49, -22), (45, -25), (43, -20)],
]


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (90.0 - lat) / 180.0 * h)


def draw_map(draw, x0, y0, w, h, stories):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(196, 214, 226),
                   outline=(120, 110, 95), width=1)
    land = (222, 205, 170)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x0, y0, w, h) for lon, lat in poly]
        draw.polygon(pts, fill=land, outline=(150, 138, 112))
    # pins for the drawn stories that have coordinates (nudge Europe apart)
    nudge = {2: (4, -5), 3: (6, 6), 4: (10, 6), 5: (8, -6), 6: (-5, 6),
             9: (-16, 10), 10: (-6, -8), 11: (8, 8), 12: (-12, 0)}
    f_pin = font(F_SANS_B, 8)
    for s in stories:
        if not s.get("map"):
            continue
        lon, lat = s["map"]
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        dx, dy = nudge.get(s["n"], (0, 0))
        px, py = px + dx, py + dy
        r = 7
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        t = str(s["n"])
        tw = draw.textlength(t, font=f_pin)
        draw.text((px - tw / 2, py - 5.5), t, font=f_pin, fill=(255, 255, 255))
    # space inset for the Mercury story
    f_sp = font(F_SANS_B, 8)
    label = "7 · MERCURY (SPACE)"
    tw = draw.textlength(label, font=f_sp)
    bx, by = x0 + 4, y0 + h - 18
    draw.rectangle([bx, by, bx + tw + 10, by + 14], fill=NAVY)
    draw.text((bx + 5, by + 2.5), label, font=f_sp, fill=(255, 255, 255))


# ---------------------------------------------------------------- illustrations
def art_bg(draw, x, y, w, h, top, bottom):
    """Vertical gradient background."""
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)


def art_label(draw, x, y, text, fnt):
    return chip(draw, x, y, text, fnt, bg=RED)


def art_quake(d, x, y, w, h):
    art_bg(d, x, y, w, h, (214, 164, 110), (122, 84, 52))
    # Andes ridge
    d.polygon([(x, y + h), (x + w * 0.18, y + h * 0.35), (x + w * 0.38, y + h),
               (x + w * 0.55, y + h * 0.28), (x + w * 0.78, y + h),
               (x + w * 0.92, y + h * 0.45), (x + w, y + h)], fill=(94, 66, 44))
    d.polygon([(x + w * 0.18, y + h * 0.35), (x + w * 0.13, y + h * 0.48),
               (x + w * 0.24, y + h * 0.48)], fill=(245, 240, 230))
    d.polygon([(x + w * 0.55, y + h * 0.28), (x + w * 0.50, y + h * 0.42),
               (x + w * 0.61, y + h * 0.42)], fill=(245, 240, 230))
    # crack
    pts = [(x + w * 0.08, y + h), (x + w * 0.16, y + h * 0.82),
           (x + w * 0.10, y + h * 0.66), (x + w * 0.20, y + h * 0.52)]
    d.line(pts, fill=(30, 20, 14), width=3)
    # seismograph trace
    pts = []
    for i in range(41):
        px = x + w * 0.30 + i * (w * 0.65 / 40)
        amp = (6 if i % 7 == 0 else 2) * (1 if 12 < i < 30 else 0.3)
        py = y + h * 0.78 + (amp if i % 2 else -amp)
        pts.append((px, py))
    d.line(pts, fill=(163, 31, 31), width=2)
    art_label(d, x + 6, y + 6, "M6.7", font(F_SANS_B, 13))


def art_stocks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 52))
    # grid
    for i in range(1, 4):
        yy = y + h * i / 4
        d.line([(x, yy), (x + w, yy)], fill=(40, 56, 88), width=1)
    # candlesticks
    import random
    rnd = random.Random(7)
    n = 9
    cw = w / (n + 1)
    price = h * 0.30
    for i in range(n):
        cx = x + cw * (i + 0.7)
        o = price + rnd.uniform(-6, 6)
        c = o + rnd.uniform(4, 14)
        price = c
        col = (198, 52, 52) if c > o else (72, 160, 90)
        d.line([(cx, y + o - 6), (cx, y + c + 6)], fill=col, width=2)
        d.rectangle([cx - 4, y + o, cx + 4, y + c], fill=col)
    # falling line
    pts = [(x + w * 0.05, y + h * 0.28), (x + w * 0.30, y + h * 0.38),
           (x + w * 0.52, y + h * 0.34), (x + w * 0.72, y + h * 0.58),
           (x + w * 0.95, y + h * 0.82)]
    d.line(pts, fill=(232, 80, 80), width=3)
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
              fill=(232, 80, 80))
    art_label(d, x + 6, y + 6, "−5.3%", font(F_SANS_B, 13))


def art_cop31(d, x, y, w, h):
    art_bg(d, x, y, w, h, (126, 178, 205), (196, 214, 226))
    cx, cy, r = x + w * 0.30, y + h * 0.52, min(w, h) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(44, 110, 170),
              outline=(22, 35, 63), width=2)
    d.polygon([(cx - r * 0.7, cy - r * 0.3), (cx - r * 0.2, cy - r * 0.6),
               (cx + r * 0.3, cy - r * 0.4), (cx + r * 0.1, cy + r * 0.1),
               (cx - r * 0.4, cy + r * 0.2)], fill=(96, 160, 90))
    d.polygon([(cx + r * 0.2, cy + r * 0.45), (cx + r * 0.6, cy + r * 0.3),
               (cx + r * 0.75, cy + r * 0.6), (cx + r * 0.3, cy + r * 0.8)],
              fill=(96, 160, 90))
    # thermometer
    tx = x + w * 0.72
    d.rounded_rectangle([tx - 7, y + h * 0.18, tx + 7, y + h * 0.78],
                        radius=7, fill=(255, 255, 255), outline=RED, width=2)
    d.ellipse([tx - 12, y + h * 0.72, tx + 12, y + h * 0.94], fill=RED)
    d.rectangle([tx - 4, y + h * 0.30, tx + 4, y + h * 0.78], fill=RED)
    art_label(d, x + 6, y + 6, "NO DEAL", font(F_SANS_B, 13))


def art_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 26, 48))
    # buildings
    for bx, bw, bh in [(0.05, 0.16, 0.55), (0.24, 0.14, 0.72), (0.42, 0.18, 0.48),
                       (0.63, 0.15, 0.66), (0.81, 0.14, 0.52)]:
        d.rectangle([x + w * bx, y + h - h * bh, x + w * (bx + bw), y + h],
                    fill=(40, 52, 80))
        for wy in range(3):
            d.rectangle([x + w * (bx + 0.03), y + h - h * bh + 8 + wy * 12,
                         x + w * (bx + 0.07), y + h - h * bh + 16 + wy * 12],
                        fill=(240, 200, 90))
    # explosion star
    ex, ey = x + w * 0.72, y + h * 0.30
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(ex, ey), (ex + 16 * math.cos(a), ey + 16 * math.sin(a))],
               fill=(245, 180, 60), width=3)
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(250, 220, 120))
    # ambulance
    ax, ay = x + w * 0.08, y + h * 0.74
    d.rectangle([ax, ay, ax + w * 0.30, ay + h * 0.16], fill=(245, 245, 240))
    d.rectangle([ax + w * 0.05, ay + h * 0.03, ax + w * 0.09, ay + h * 0.13],
                fill=RED)
    d.rectangle([ax + w * 0.03, ay + h * 0.06, ax + w * 0.11, ay + h * 0.10],
                fill=RED)
    d.ellipse([ax + 4, ay + h * 0.16 - 4, ax + 12, ay + h * 0.16 + 4], fill=INK)
    d.ellipse([ax + w * 0.30 - 12, ay + h * 0.16 - 4, ax + w * 0.30 - 4,
               ay + h * 0.16 + 4], fill=INK)
    art_label(d, x + 6, y + 6, "DOUBLE-TAP", font(F_SANS_B, 12))


def art_nato(d, x, y, w, h):
    art_bg(d, x, y, w, h, (58, 92, 150), (22, 35, 63))
    cx, cy, r = x + w * 0.50, y + h * 0.46, min(w, h) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=2)
    pts = []
    for i in range(8):
        ang = math.radians(i * 45)
        rr = r * 0.92 if i % 2 == 0 else r * 0.28
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 255, 255))
    # Polish flag
    fx, fy = x + w * 0.06, y + h * 0.72
    d.rectangle([fx, fy, fx + 34, fy + 8], fill=(255, 255, 255))
    d.rectangle([fx, fy + 8, fx + 34, fy + 16], fill=(200, 40, 40))
    art_label(d, x + 6, y + 6, "GRAVE VIOLATION", font(F_SANS_B, 11))


def art_iran(d, x, y, w, h):
    art_bg(d, x, y, w, h, (140, 170, 205), (210, 222, 232))
    for cx, cy, cw in [(0.2, 0.25, 60), (0.55, 0.15, 80), (0.8, 0.35, 50)]:
        d.ellipse([x + w * cx - cw / 2, y + h * cy, x + w * cx + cw / 2,
                   y + h * cy + 16], fill=(255, 255, 255))
    # plane silhouette
    px, py = x + w * 0.50, y + h * 0.55
    d.ellipse([px - 52, py - 8, px + 52, py + 8], fill=(30, 42, 66))
    d.polygon([(px + 30, py - 4), (px + 62, py - 22), (px + 66, py - 18),
               (px + 44, py + 2)], fill=(30, 42, 66))
    d.polygon([(px - 8, py + 4), (px + 6, py + 22), (px + 14, py + 20),
               (px + 8, py + 4)], fill=(30, 42, 66))
    d.polygon([(px - 44, py - 2), (px - 62, py - 20), (px - 56, py - 22),
               (px - 34, py - 4)], fill=(30, 42, 66))
    art_label(d, x + 6, y + 6, "2027", font(F_SANS_B, 13))


def art_bepi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 24))
    import random
    rnd = random.Random(11)
    for _ in range(26):
        sx = x + rnd.uniform(0, w)
        sy = y + rnd.uniform(0, h * 0.7)
        d.ellipse([sx, sy, sx + 1.6, sy + 1.6], fill=(255, 255, 255))
    # Mercury
    mx, my, mr = x + w * 0.68, y + h * 0.55, min(w, h) * 0.26
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(198, 142, 92),
              outline=(150, 100, 62), width=2)
    for cx, cy, cr in [(-0.4, -0.3, 0.22), (0.3, 0.2, 0.28), (-0.1, 0.45, 0.18),
                       (0.45, -0.35, 0.15)]:
        d.ellipse([mx + mr * cx - mr * cr, my + mr * cy - mr * cr,
                   mx + mr * cx + mr * cr, my + mr * cy + mr * cr],
                  fill=(168, 112, 70))
    # spacecraft + trajectory
    d.arc([x + w * 0.05, y + h * 0.05, x + w * 0.75, y + h * 0.95],
          start=200, end=330, fill=(120, 160, 220), width=2)
    sx, sy = x + w * 0.22, y + h * 0.30
    d.rectangle([sx - 12, sy - 6, sx + 12, sy + 6], fill=(200, 205, 215),
                outline=(255, 255, 255))
    d.rectangle([sx - 26, sy - 3, sx - 12, sy + 3], fill=(60, 90, 160))
    d.rectangle([sx + 12, sy - 3, sx + 26, sy + 3], fill=(60, 90, 160))
    art_label(d, x + 6, y + 6, "19:24 CET", font(F_SANS_B, 12))


def art_f1(d, x, y, w, h):
    art_bg(d, x, y, w, h, (70, 76, 88), (30, 32, 40))
    # track
    d.ellipse([x + w * 0.06, y + h * 0.18, x + w * 0.94, y + h * 0.86],
              outline=(220, 220, 220), width=10)
    d.ellipse([x + w * 0.06, y + h * 0.18, x + w * 0.94, y + h * 0.86],
              outline=(200, 40, 40), width=2)
    # car (side silhouette)
    cx, cy = x + w * 0.50, y + h * 0.52
    d.polygon([(cx - 52, cy + 8), (cx - 40, cy - 6), (cx - 8, cy - 10),
               (cx + 26, cy - 6), (cx + 52, cy + 2), (cx + 52, cy + 8)],
              fill=(30, 170, 135), outline=(255, 255, 255))
    d.rectangle([cx + 40, cy - 16, cx + 52, cy + 0], fill=(30, 170, 135),
                outline=(255, 255, 255))
    d.ellipse([cx - 34, cy + 2, cx - 18, cy + 14], fill=INK)
    d.ellipse([cx + 18, cy + 2, cx + 34, cy + 14], fill=INK)
    # checkered flag
    fx, fy = x + w * 0.78, y + h * 0.10
    for i in range(4):
        for j in range(3):
            if (i + j) % 2 == 0:
                d.rectangle([fx + i * 6, fy + j * 6, fx + i * 6 + 6,
                             fy + j * 6 + 6], fill=INK)
    art_label(d, x + 6, y + 6, "1:34.041", font(F_SANS_B, 12))


def art_atp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 110, 84))
    d.rectangle([x + w * 0.10, y + h * 0.12, x + w * 0.90, y + h * 0.88],
                fill=(66, 132, 100), outline=(255, 255, 255), width=2)
    d.line([(x + w * 0.50, y + h * 0.12), (x + w * 0.50, y + h * 0.88)],
           fill=(255, 255, 255), width=2)
    # net
    d.line([(x + w * 0.10, y + h * 0.50), (x + w * 0.90, y + h * 0.50)],
           fill=(255, 255, 255), width=3)
    # ball
    bx, by = x + w * 0.68, y + h * 0.30
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=(205, 220, 60),
              outline=(255, 255, 255), width=1)
    d.arc([bx - 11, by - 11, bx + 11, by + 11], start=300, end=60,
          fill=(255, 255, 255), width=2)
    art_label(d, x + 6, y + 6, "SEMI-FINALS", font(F_SANS_B, 12))


def art_denmark(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 40, 52))
    # white cross (Danish flag)
    d.rectangle([x + w * 0.32, y, x + w * 0.32 + 12, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.42 + 12], fill=(255, 255, 255))
    art_label(d, x + 6, y + 6, "7 DAYS", font(F_SANS_B, 12))


def art_houthi(d, x, y, w, h):
    art_bg(d, x, y, w, h, (232, 190, 130), (150, 110, 70))
    # port cranes
    for cx in (0.15, 0.45, 0.72):
        bx = x + w * cx
        d.line([(bx, y + h * 0.85), (bx, y + h * 0.35)], fill=(60, 50, 40), width=4)
        d.line([(bx, y + h * 0.35), (bx + w * 0.18, y + h * 0.45)],
               fill=(60, 50, 40), width=3)
        d.line([(bx, y + h * 0.35), (bx - w * 0.08, y + h * 0.42)],
               fill=(60, 50, 40), width=3)
    d.rectangle([x, y + h * 0.85, x + w, y + h], fill=(52, 92, 128))
    # missile trail + burst
    pts = [(x + w * 0.85, y + h * 0.12), (x + w * 0.62, y + h * 0.30),
           (x + w * 0.45, y + h * 0.44)]
    d.line(pts, fill=(255, 255, 255), width=2)
    ex, ey = pts[-1]
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        d.line([(ex, ey), (ex + 12 * math.cos(a), ey + 12 * math.sin(a))],
               fill=(245, 180, 60), width=3)
    d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=(250, 220, 120))
    art_label(d, x + 6, y + 6, "41 KILLED", font(F_SANS_B, 12))


def art_gold(d, x, y, w, h):
    art_bg(d, x, y, w, h, (36, 40, 52), (18, 20, 28))
    # falling arrow
    d.line([(x + w * 0.15, y + h * 0.25), (x + w * 0.85, y + h * 0.70)],
           fill=(232, 80, 80), width=4)
    d.polygon([(x + w * 0.85, y + h * 0.70), (x + w * 0.85, y + h * 0.52),
               (x + w * 0.68, y + h * 0.70)], fill=(232, 80, 80))
    # gold bars
    bx, by = x + w * 0.14, y + h * 0.66
    for i, (ox, oy) in enumerate([(0, 0), (30, 0), (15, -14)]):
        d.polygon([(bx + ox, by + oy), (bx + ox + 6, by + oy - 8),
                   (bx + ox + 26, by + oy - 8), (bx + ox + 32, by + oy),
                   (bx + ox + 28, by + oy + 8), (bx + ox + 4, by + oy + 8)],
                  fill=(212, 175, 55), outline=(150, 115, 30))
    art_label(d, x + 6, y + 6, "−4%", font(F_SANS_B, 13))


def art_akvan(d, x, y, w, h):
    art_bg(d, x, y, w, h, (90, 140, 180), (170, 200, 220))
    # coastline
    d.polygon([(x, y + h), (x, y + h * 0.62), (x + w * 0.30, y + h * 0.55),
               (x + w * 0.55, y + h * 0.68), (x + w * 0.80, y + h * 0.60),
               (x + w, y + h * 0.66), (x + w, y + h)], fill=(214, 196, 150))
    # cyclone spiral
    cx, cy = x + w * 0.42, y + h * 0.34
    for r, a0 in [(26, 0), (20, 120), (14, 240), (8, 60)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], start=a0, end=a0 + 220,
              fill=(255, 255, 255), width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    # rain
    for i in range(8):
        rx = x + w * (0.08 + i * 0.11)
        d.line([(rx, y + h * 0.72), (rx - 4, y + h * 0.82)],
               fill=(240, 244, 250), width=2)
    art_label(d, x + 6, y + 6, "209 MM", font(F_SANS_B, 12))


ART = {"quake": art_quake, "stocks": art_stocks, "cop31": art_cop31,
       "kryvyi": art_kryvyi, "nato": art_nato, "iran": art_iran,
       "bepi": art_bepi, "f1": art_f1, "atp": art_atp, "denmark": art_denmark,
       "houthi": art_houthi, "gold": art_gold, "akvan": art_akvan}


# ---------------------------------------------------------------- page build
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(DATA["leads"]) + len(DATA["cards"]) + len(DATA["briefs"])
    regions = DATA["regions"]
    counts = {}
    for s in DATA["leads"] + DATA["cards"] + DATA["briefs"]:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    assert total == 35, total
    assert sum(counts.values()) == total

    MX = 16
    CW = W - 2 * MX  # 992

    # ---- top bar
    y = 8
    f_top = font(F_SANS_B, 12)
    d.text((MX, y), "THE WORLD IN ONE DAY", font=f_top, fill=RED)
    f_note = font(F_SANS, 9)
    note = DATA["masthead_note"]
    d.text((W - MX - d.textlength(note, font=f_note), y + 1), note,
           font=f_note, fill=GRAY)
    d.line([(MX, 26), (W - MX, 26)], fill=INK, width=2)

    # ---- masthead (auto-fit)
    title = DATA["date_label"]
    f_title = fit_font(d, title, F_SERIF, 58, CW, 1)
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 30), title, font=f_title, fill=INK)
    f_sub = font(F_SERIF_IT, 16)
    sub = DATA["subhead"]
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 96), sub, font=f_sub, fill=(60, 56, 48))
    d.line([(MX, 120), (W - MX, 120)], fill=INK, width=2)

    # ---- six big numbers
    y0 = 126
    cell = CW / 6
    f_num = font(F_SERIF, 25)
    f_lab = font(F_SANS, 9)
    for i, bn in enumerate(DATA["big_numbers"]):
        cx = MX + i * cell
        d.text((cx + 8, y0), bn["num"], font=f_num, fill=INK)
        lines = wrap(d, bn["label"], f_lab, cell - 16)
        draw_lines(d, lines[:2], cx + 8, y0 + 30, f_lab, GRAY, 11)
        if i:
            d.line([(cx, y0 + 2), (cx, y0 + 48)], fill=RED, width=2)
    d.line([(MX, 180), (W - MX, 180)], fill=INK, width=1)

    # ---- region bar (widths proportional to counts, but never narrower
    # than the label they carry; the deficit comes off the largest bars)
    y0 = 184
    x = MX
    f_reg = font(F_SANS_B, 10)
    widths = []
    for r in regions:
        n = counts[r["name"]]
        label = "%s %d" % (r["name"], n)
        widths.append(max(CW * n / total,
                          d.textlength(label, font=f_reg) + 10))
    over = sum(widths) - CW
    while over > 0.5:
        excess = [(i, widths[i] - (d.textlength(
            "%s %d" % (regions[i]["name"], counts[regions[i]["name"]]),
            font=f_reg) + 10)) for i in range(len(widths))]
        pool = sum(e for _, e in excess if e > 0)
        if pool <= 0:
            break
        for i, e in excess:
            if e > 0:
                take = min(e, over * e / pool)
                widths[i] -= take
                over -= take
    for r, seg in zip(regions, widths):
        n = counts[r["name"]]
        d.rectangle([x, y0, x + seg - 1, y0 + 19], fill=r["color"])
        label = "%s %d" % (r["name"], n)
        tw = d.textlength(label, font=f_reg)
        tx = x + (seg - tw) / 2
        d.text((tx, y0 + 4), label, font=f_reg, fill=(255, 255, 255))
        x += seg

    # ---- leads (3 columns)
    y0 = 210
    lead_h = 264
    col_w = (CW - 20) / 3
    img_h = 136
    for i, s in enumerate(DATA["leads"]):
        cx = MX + i * (col_w + 10)
        ART[s["art"]](d, cx, y0, col_w, img_h)
        ty = y0 + img_h + 6
        f_kick = font(F_SANS_B, 10)
        badge = " %d " % s["n"]
        bw = d.textlength(badge, font=f_kick)
        d.rectangle([cx, ty, cx + bw, ty + 13], fill=RED)
        d.text((cx, ty), badge, font=f_kick, fill=(255, 255, 255))
        d.text((cx + bw + 5, ty), "%s · %s" % (s["place"], s["field"]),
               font=f_kick, fill=RED)
        ty += 17
        f_head = fit_font(d, s["headline"], F_SERIF, 19, col_w, 2)
        lines = wrap(d, s["headline"], f_head, col_w)
        ty = draw_lines(d, lines, cx, ty, f_head, INK, 22)
        ty += 2
        f_body = font(F_SANS, 11)
        lines = wrap(d, s["body"], f_body, col_w)
        ty = draw_lines(d, lines[:3], cx, ty, f_body, (40, 38, 34), 14)
        f_src = font(F_SANS_IT, 9)
        d.text((cx, ty + 1), "(%s)" % s["source"], font=f_src, fill=GRAY)

    # ---- cards (5 columns x 2 rows)
    y0 = 480
    card_h = 164
    col_w = (CW - 40) / 5
    img_h = 72
    for i, s in enumerate(DATA["cards"]):
        row, col = divmod(i, 5)
        cx = MX + col * (col_w + 10)
        cy = y0 + row * card_h
        ART[s["art"]](d, cx, cy, col_w, img_h)
        ty = cy + img_h + 4
        f_kick = font(F_SANS_B, 8)
        badge = " %d " % s["n"]
        bw = d.textlength(badge, font=f_kick)
        d.rectangle([cx, ty, cx + bw, ty + 11], fill=RED)
        d.text((cx, ty), badge, font=f_kick, fill=(255, 255, 255))
        d.text((cx + bw + 4, ty), "%s · %s" % (s["place"], s["field"]),
               font=f_kick, fill=RED)
        ty += 14
        f_head = fit_font(d, s["headline"], F_SERIF, 13, col_w, 3)
        lines = wrap(d, s["headline"], f_head, col_w)
        ty = draw_lines(d, lines, cx, ty, f_head, INK, 15)
        f_body = font(F_SANS, 9)
        lines = wrap(d, s["body"], f_body, col_w)
        room = int((cy + card_h - 13 - ty) // 11.5)
        draw_lines(d, lines[:max(1, room)], cx, ty, f_body, (40, 38, 34), 11.5)
        f_src = font(F_SANS_IT, 8)
        d.text((cx, cy + card_h - 11), "(%s)" % s["source"], font=f_src,
               fill=GRAY)

    # ---- bottom: map + briefs
    y0 = 814
    map_w = 300
    map_h = 128
    f_sec = font(F_SANS_B, 10)
    d.text((MX, y0), "WHERE IT HAPPENED", font=f_sec, fill=INK)
    d.text((MX + map_w - d.textlength("pins 1–13 mark the drawn stories",
                                      font=font(F_SANS, 8)),
            y0 + 1), "pins 1–13 mark the drawn stories",
           font=font(F_SANS, 8), fill=GRAY)
    draw_map(d, MX, y0 + 15, map_w, map_h,
             DATA["leads"] + DATA["cards"])
    bx = MX + map_w + 12
    bw = W - MX - bx
    n_briefs = len(DATA["briefs"])
    d.text((bx, y0), "ALSO ON SATURDAY 21 NOVEMBER — %d MORE STORIES"
           % n_briefs, font=f_sec, fill=INK)
    d.line([(bx, y0 + 14), (W - MX, y0 + 14)], fill=INK, width=1)
    # two columns of briefs, one line each
    f_br = font(F_SANS, 10)
    f_brb = font(F_SANS_B, 10)
    col_bw = (bw - 10) / 2
    per_col = (n_briefs + 1) // 2
    for i, b in enumerate(DATA["briefs"]):
        col = 0 if i < per_col else 1
        row = i if col == 0 else i - per_col
        tx = bx + col * (col_bw + 10)
        ty = y0 + 19 + row * 11.0
        num = "%d " % b["n"]
        d.text((tx, ty), num, font=f_brb, fill=RED)
        nx = tx + d.textlength(num, font=f_brb)
        place = b["place"] + " "
        d.text((nx, ty), place, font=f_brb, fill=INK)
        px = nx + d.textlength(place, font=f_brb)
        rest = b["text"]
        # shrink to fit one line if needed
        f = f_br
        while d.textlength(rest, font=f) > col_bw - (px - tx) and f.size > 8:
            f = font(F_SANS, f.size - 0.5)
        d.text((px, ty), rest, font=f, fill=(40, 38, 34))

    # ---- UTC timeline
    y0 = 958
    d.line([(MX, y0), (W - MX, y0)], fill=INK, width=1)
    f_tl = font(F_SANS_B, 9)
    f_tlb = font(F_SANS_B, 9)
    d.text((MX, y0 + 4), "AS THE DAY UNFOLDED (UTC)", font=f_tlb, fill=RED)
    tx = MX + 175
    f_ti = font(F_SANS, 9)
    for t in DATA["timeline"]:
        item = "%s  %s" % (t["utc"], t["text"])
        d.text((tx, y0 + 4), t["utc"], font=f_tlb, fill=INK)
        tx += d.textlength(t["utc"] + "  ", font=f_tlb)
        d.text((tx, y0 + 4), t["text"], font=f_ti, fill=(40, 38, 34))
        tx += d.textlength(t["text"] + "   ·   ", font=f_ti)

    # ---- date check
    y0 = 980
    d.rectangle([MX, y0, W - MX, y0 + 28], outline=RED, width=1)
    f_dc = font(F_SANS, 9)
    d.text((MX + 5, y0 + 2), "DATE CHECK", font=font(F_SANS_B, 9), fill=RED)
    lines = wrap(d, DATA["date_check"], f_dc, CW - 92)
    draw_lines(d, lines[:2], MX + 72, y0 + 2, f_dc, (40, 38, 34), 11)

    # ---- footer
    f_ft = font(F_SANS, 8)
    d.text((MX, 1012), DATA["footer"], font=f_ft, fill=GRAY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
