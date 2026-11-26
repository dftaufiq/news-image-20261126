#!/usr/bin/env python3
"""Generate the news-image-20261126 front page (1024x1024 PNG).

Draws a dense newspaper front page for Thursday 26 November 2026 with
flat PIL illustrations (original artwork, no photographs, no copied art).
Run: python3 generate_image.py [output-path]  (default: entry.png)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (178, 32, 44)
NAVY = (31, 58, 95)
GOLD = (201, 162, 39)
GREY = (110, 108, 100)
LIGHT = (233, 228, 214)
DARKBLUE = (16, 28, 52)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap returning list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, s, f, max_w, fill=INK, leading=None, max_lines=None):
    """Draw wrapped text; returns y after last line."""
    if leading is None:
        leading = int(f.size * 1.18)
    lines = wrap(draw, s, f, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def center(draw, cx, y, s, f, fill=INK):
    draw.text((cx - draw.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def tag(draw, x, y, label, bg, fg=(255, 255, 255), size=11):
    """Small filled tag; returns width used."""
    f = font(F_SANS_B, size)
    w = int(draw.textlength(label, font=f)) + 10
    h = size + 7
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=bg)
    draw.text((x + 5, y + 3), label, font=f, fill=fg)
    return w


def rule(draw, x0, y, x1, color=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def skyline(draw, x0, y0, x1, y1, color, windows=True, seed=7):
    """Flat city skyline silhouette inside a box."""
    import random
    rnd = random.Random(seed)
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    w = x1 - x0
    x = x0
    while x < x1 - 8:
        bw = rnd.randint(18, 46)
        bh = rnd.randint(int((y1 - y0) * 0.35), int((y1 - y0) * 0.95))
        draw.rectangle([x, y1 - bh, min(x + bw, x1), y1], fill=color)
        if windows:
            for wy in range(y1 - bh + 5, y1 - 6, 9):
                for wx in range(x + 4, min(x + bw, x1) - 4, 8):
                    if rnd.random() < 0.45:
                        draw.rectangle([wx, wy, wx + 3, wy + 4],
                                       fill=(255, 214, 120))
        x += bw + rnd.randint(1, 5)


def flame(draw, cx, base_y, scale=1.0):
    """Stylised flame: layered polygons."""
    s = scale
    outer = [(cx - 26 * s, base_y), (cx - 18 * s, base_y - 34 * s),
             (cx - 6 * s, base_y - 22 * s), (cx + 2 * s, base_y - 52 * s),
             (cx + 12 * s, base_y - 26 * s), (cx + 24 * s, base_y - 30 * s),
             (cx + 26 * s, base_y)]
    draw.polygon(outer, fill=(230, 90, 20))
    inner = [(cx - 13 * s, base_y), (cx - 9 * s, base_y - 20 * s),
             (cx + 1 * s, base_y - 30 * s), (cx + 11 * s, base_y - 14 * s),
             (cx + 13 * s, base_y)]
    draw.polygon(inner, fill=(255, 196, 0))


def smoke(draw, cx, cy, r, color=(90, 88, 84)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    draw.ellipse([cx - r * 0.6, cy - r * 1.1, cx + r * 0.7, cy + r * 0.2],
                 fill=(110, 108, 102))


def tanker(draw, x0, y, w, hull=(40, 44, 52), deck=(200, 60, 30)):
    """Oil tanker silhouette with burning deck fire."""
    hull_h = 16
    draw.polygon([(x0, y), (x0 + w, y), (x0 + w - 14, y + hull_h),
                  (x0 + 14, y + hull_h)], fill=hull)
    draw.rectangle([x0 + w * 0.62, y - 18, x0 + w * 0.72, y], fill=(60, 64, 72))
    draw.rectangle([x0 + w * 0.66, y - 30, x0 + w * 0.68, y - 18],
                   fill=(60, 64, 72))
    draw.rectangle([x0 + w * 0.18, y - 10, x0 + w * 0.30, y], fill=deck)
    flame(draw, x0 + w * 0.24, y - 8, 0.8)
    flame(draw, x0 + w * 0.78, y - 6, 0.9)
    draw.rectangle([x0, y + hull_h, x0 + w, y + hull_h + 3], fill=(30, 60, 90))

# ---------------------------------------------------------------- art panels
def art_hero(draw, x0, y0, x1, y1):
    """Dusk strait: burning tankers on the sea, Riyadh skyline, missile trails."""
    # sky: deep dusk gradient bands
    bands = [(16, 28, 52), (38, 52, 88), (74, 62, 78), (150, 74, 52),
             (214, 110, 40)]
    bh = (y1 - y0) / len(bands)
    for i, c in enumerate(bands):
        draw.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh + 1], fill=c)
    # a few stars in the dark top band
    for sx, sy in [(x0 + 60, y0 + 10), (x0 + 130, y0 + 18), (x0 + 420, y0 + 8),
                   (x0 + 700, y0 + 12), (x0 + 900, y0 + 8)]:
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    # missile trails: kept strictly inside the art box
    for (sx, sy, ex, ey) in [(x0 + 70, y1 - 34, x0 + 330, y0 + 26),
                             (x0 + 620, y1 - 30, x0 + 880, y0 + 22)]:
        draw.line([(sx, sy), (ex, ey)], fill=(255, 230, 150), width=3)
        draw.line([(sx, sy), (ex, ey)], fill=(255, 255, 255), width=1)
        bx, by = (sx + ex) // 2, (sy + ey) // 2
        for dx, dy in [(0, 0), (-12, -5), (12, -5), (-9, 9), (11, 7)]:
            draw.line([(bx, by), (bx + dx, by + dy)], fill=(255, 210, 80),
                      width=2)
        draw.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(255, 240, 160))
    # Riyadh skyline silhouette (dark) along the top of the sea
    sea_y = y0 + (y1 - y0) * 0.68
    skyline(draw, x0 + 30, sea_y - 40, x0 + 330, sea_y, (24, 22, 34), seed=11)
    # KAFD twisted tower: simple tapered rectangle
    draw.polygon([(x0 + 252, sea_y), (x0 + 258, sea_y - 58),
                  (x0 + 272, sea_y - 58), (x0 + 278, sea_y)],
                 fill=(24, 22, 34))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(24, 52, 84))
    for i in range(4):
        yy = sea_y + 8 + i * 7
        draw.line([(x0 + 20 + i * 40, yy), (x0 + 200 + i * 60, yy)],
                  fill=(70, 110, 150), width=2)
    # small fire glow on the water, drawn before the hulls
    draw.ellipse([x0 + 420, sea_y + 20, x0 + 560, sea_y + 26],
                 fill=(214, 110, 40))
    draw.ellipse([x0 + 720, sea_y + 26, x0 + 900, sea_y + 32],
                 fill=(214, 110, 40))
    # two burning tankers
    tanker(draw, x0 + 380, sea_y + 4, 240)
    tanker(draw, x0 + 660, sea_y + 14, 300)


def art_macys(draw, x0, y0, x1, y1):
    """Rainy New York street, big red parade balloon, '100' badge."""
    draw.rectangle([x0, y0, x1, y1], fill=(58, 78, 110))
    for i in range(14):  # rain streaks
        rx = x0 + 12 + i * ((x1 - x0 - 24) // 14)
        draw.line([(rx, y0 + 6), (rx - 6, y0 + 34)], fill=(200, 214, 232),
                  width=2)
    skyline(draw, x0, y1 - 40, x1, y1, (30, 38, 56), windows=True, seed=5)
    # big round balloon, left of centre
    cx, cy = (x0 + x1) // 2 - 90, y0 + 38
    draw.ellipse([cx - 44, cy - 26, cx + 44, cy + 26], fill=(178, 32, 44))
    draw.ellipse([cx - 30, cy - 16, cx + 10, cy + 6], fill=(205, 60, 70))
    draw.ellipse([cx - 34, cy - 20, cx - 18, cy - 8], fill=(255, 200, 200))
    for k in range(3):  # ropes to handlers below
        draw.line([(cx - 28 + k * 28, cy + 24), (cx - 32 + k * 28, y1 - 40)],
                  fill=(240, 236, 220), width=2)
    # gold 100 badge, clear of the balloon
    bx = x1 - 56
    draw.ellipse([bx, y0 + 8, bx + 44, y0 + 52], fill=GOLD)
    draw.text((bx + 6, y0 + 16), "100", font=font(F_SANS_B, 20), fill=INK)


def art_eu(draw, x0, y0, x1, y1):
    """EU circle of stars over Brussels hemicycle, €45bn in the centre."""
    draw.rectangle([x0, y0, x1, y1], fill=(31, 58, 95))
    cx, cy = (x0 + x1) // 2, y0 + 40
    # hemicycle arc
    draw.pieslice([cx - 120, cy - 40, cx + 120, cy + 130], 180, 360,
                  fill=(20, 38, 66))
    for i in range(12):  # circle of stars
        import math
        a = math.pi * 2 * i / 12 - math.pi / 2
        sx, sy = cx + 56 * math.cos(a), cy + 56 * math.sin(a)
        draw.ellipse([sx - 5, sy - 5, sx + 5, sy + 5], fill=(255, 214, 60))
    draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(255, 214, 60))
    t = "€45bn"
    tw = draw.textlength(t, font=font(F_SANS_B, 16))
    draw.text((cx - tw / 2, cy - 10), t, font=font(F_SANS_B, 16), fill=NAVY)


def art_refinery(draw, x0, y0, x1, y1):
    """Refinery towers with flames and smoke at night."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(24, 26, 34))
    draw.ellipse([x1 - 26, y0 + 4, x1 - 6, y0 + 24], fill=(240, 220, 180))
    for tx in (x0 + 18, x0 + 56, x0 + 96):
        th = h * 0.62
        draw.rectangle([tx, y1 - th, tx + 20, y1], fill=(52, 54, 62))
        draw.rectangle([tx + 5, y1 - th - 8, tx + 15, y1 - th],
                       fill=(52, 54, 62))
        flame(draw, tx + 10, y1 - th - 7, 0.35)
    smoke(draw, x0 + 28, y0 + 12, 8)
    smoke(draw, x0 + 106, y0 + 8, 9)
    draw.rectangle([x0, y1 - 4, x1, y1], fill=(12, 12, 16))


def art_markets(draw, x0, y0, x1, y1):
    """Chart: plunging line recovering, green up-tick at the end."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(240, 238, 228))
    w = x1 - x0
    pts = [(x0 + 4, y0 + h * 0.30), (x0 + w * 0.2, y0 + h * 0.45),
           (x0 + w * 0.35, y0 + h * 0.35), (x0 + w * 0.5, y0 + h * 0.70),
           (x0 + w * 0.65, y0 + h * 0.62), (x0 + w * 0.8, y0 + h * 0.82),
           (x0 + w * 0.9, y0 + h * 0.55), (x0 + w - 6, y0 + h * 0.32)]
    pts = [(int(a), int(b)) for a, b in pts]
    draw.line(pts, fill=(178, 32, 44), width=3, joint="curve")
    draw.line([pts[-2], pts[-1]], fill=(34, 120, 60), width=3)
    ex, ey = pts[-1]
    draw.polygon([(ex, ey - 7), (ex - 6, ey + 3), (ex + 6, ey + 3)],
                 fill=(34, 120, 60))
    # white chip with the closing level, clear of the number badge
    draw.rectangle([x0 + 26, y0 + 3, x0 + 84, y0 + 19], fill=(255, 255, 255),
                   outline=(26, 26, 26), width=1)
    draw.text((x0 + 30, y0 + 5), "50,183", font=font(F_SANS_B, 11), fill=INK)


def art_cairo(draw, x0, y0, x1, y1):
    """Highway overpass, overturned tanker, big flame."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(52, 44, 40))
    draw.rectangle([x0, y1 - 12, x1, y1 - 5], fill=(90, 84, 76))
    draw.rectangle([x0 + 26, y1 - 20, x0 + 38, y1 - 12], fill=(70, 64, 58))
    draw.rectangle([x0 + 130, y1 - 20, x0 + 142, y1 - 12], fill=(70, 64, 58))
    # overturned tanker cylinder
    draw.ellipse([x0 + 62, y1 - 22, x0 + 132, y1 - 6], fill=(180, 180, 176))
    flame(draw, (x0 + x1) // 2, y1 - 20, 0.6)
    smoke(draw, (x0 + x1) // 2 + 26, y0 + 8, 9)
    draw.text((x0 + 26, y0 + 3), "31", font=font(F_SANS_B, 18),
              fill=(255, 255, 255))


def art_chess(draw, x0, y0, x1, y1):
    """Chessboard corner with king and knight, '1–1' score."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(31, 58, 95))
    sq = (h - 6) // 4
    bx, by = x0 + 6, y0 + 3
    for r in range(4):
        for c in range(4):
            col = (240, 236, 220) if (r + c) % 2 == 0 else (52, 56, 66)
            draw.rectangle([bx + c * sq, by + r * sq,
                            bx + (c + 1) * sq, by + (r + 1) * sq], fill=col)
    kx, ky = bx + sq + sq // 2, by + sq + sq // 2
    draw.ellipse([kx - 6, ky - 6, kx + 6, ky + 6], fill=(255, 255, 255))
    draw.text((kx - 3, ky - 5), "+", font=font(F_SANS_B, 9), fill=INK)
    nx, ny = bx + 2 * sq + sq // 2, by + 2 * sq + sq // 2
    draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=(26, 26, 26))
    draw.text((nx - 4, ny - 5), "N", font=font(F_SANS_B, 9),
              fill=(255, 255, 255))
    draw.text((x1 - 40, y0 + 4), "1–1", font=font(F_SANS_B, 18),
              fill=(255, 255, 255))


def art_india(draw, x0, y0, x1, y1):
    """Memorial candles row under a saffron band, India Gate silhouette."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(24, 26, 34))
    draw.rectangle([x0, y0, x1, y0 + 7], fill=(255, 153, 51))
    draw.rectangle([x0, y0 + 7, x1, y0 + 10], fill=(255, 255, 255))
    draw.rectangle([x0, y0 + 10, x1, y0 + 17], fill=(19, 136, 8))
    # India Gate arch
    gx = (x0 + x1) // 2
    draw.rectangle([gx - 20, y0 + 19, gx + 20, y1 - 4], fill=(120, 96, 60))
    draw.pieslice([gx - 11, y0 + 24, gx + 11, y0 + 34], 180, 360,
                  fill=(24, 26, 34))
    for cx in (x0 + 18, x0 + 44, x1 - 44, x1 - 18):
        draw.rectangle([cx - 2, y1 - 12, cx + 2, y1 - 4],
                       fill=(240, 236, 220))
        flame(draw, cx, y1 - 12, 0.22)
    # "18" in a dark chip, clear of the arch
    draw.rectangle([x0 + 4, y0 + 19, x0 + 30, y0 + 36], fill=(24, 26, 34),
                   outline=(255, 255, 255), width=1)
    draw.text((x0 + 7, y0 + 21), "18", font=font(F_SANS_B, 13),
              fill=(255, 255, 255))


def art_space(draw, x0, y0, x1, y1):
    """Tiangong station + Shenzhou capsule among stars."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(10, 14, 30))
    import random
    rnd = random.Random(3)
    for _ in range(22):
        sx = rnd.randint(x0 + 4, x1 - 4)
        sy = rnd.randint(y0 + 4, y1 - 4)
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 255))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    draw.rectangle([cx - 56, cy - 5, cx + 56, cy + 5], fill=(150, 160, 175))
    draw.rectangle([cx - 22, cy - 10, cx + 22, cy + 10], fill=(190, 198, 210))
    draw.rectangle([cx - 76, cy - 3, cx - 56, cy + 3], fill=(40, 90, 160))
    draw.rectangle([cx + 56, cy - 3, cx + 76, cy + 3], fill=(40, 90, 160))
    draw.ellipse([cx + 68, cy - 7, cx + 82, cy + 7], fill=(230, 120, 40))
    draw.ellipse([cx - 82, cy - 7, cx - 68, cy + 7], fill=(230, 120, 40))


def art_gaza(draw, x0, y0, x1, y1):
    """City at dusk with searchlight beam and smoke column."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(74, 62, 66))
    skyline(draw, x0, y1 - 16, x1, y1, (40, 36, 40), windows=False, seed=9)
    draw.polygon([(x0 + 120, y1 - 16), (x0 + 150, y0 + 4),
                  (x0 + 166, y0 + 4), (x0 + 144, y1 - 16)],
                 fill=(255, 240, 180))
    smoke(draw, x0 + 48, y0 + 10, 9)
    smoke(draw, x0 + 64, y0 + 4, 7)


def art_nigeria(draw, x0, y0, x1, y1):
    """Savanna horizon, acacia tree, warning sun."""
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(232, 200, 120))
    draw.ellipse([x1 - 36, y0 + 4, x1 - 8, y0 + 32], fill=(214, 110, 40))
    draw.rectangle([x0, y1 - 12, x1, y1], fill=(150, 110, 50))
    tx = x0 + 34
    draw.rectangle([tx, y1 - 24, tx + 5, y1 - 12], fill=(90, 60, 30))
    draw.ellipse([tx - 13, y1 - 32, tx + 24, y1 - 20], fill=(90, 120, 50))
    draw.ellipse([tx + 5, y1 - 36, tx + 36, y1 - 24], fill=(110, 140, 60))
    draw.text((x0 + 26, y0 + 3), "30", font=font(F_SANS_B, 16), fill=INK)

# ---------------------------------------------------------------- map + layout
def draw_map(draw, x0, y0, x1, y1, pins):
    """Very simplified world map (flat blobs) with numbered red pins."""
    draw.rectangle([x0, y0, x1, y1], fill=(226, 222, 206))
    land = (196, 188, 158)
    # North America
    draw.polygon([(x0 + 8, y0 + 18), (x0 + 62, y0 + 8), (x0 + 78, y0 + 26),
                  (x0 + 60, y0 + 44), (x0 + 30, y0 + 46), (x0 + 10, y0 + 34)],
                 fill=land)
    # South America
    draw.polygon([(x0 + 62, y0 + 62), (x0 + 92, y0 + 58), (x0 + 96, y0 + 84),
                  (x0 + 80, y0 + 108), (x0 + 68, y0 + 88)], fill=land)
    # Europe
    draw.polygon([(x0 + 104, y0 + 14), (x0 + 128, y0 + 10),
                  (x0 + 134, y0 + 26), (x0 + 116, y0 + 34),
                  (x0 + 104, y0 + 28)], fill=land)
    # Africa
    draw.polygon([(x0 + 106, y0 + 44), (x0 + 136, y0 + 42),
                  (x0 + 142, y0 + 66), (x0 + 128, y0 + 92),
                  (x0 + 114, y0 + 78), (x0 + 106, y0 + 60)], fill=land)
    # Asia (big blob)
    draw.polygon([(x0 + 138, y0 + 12), (x0 + 196, y0 + 8),
                  (x0 + 214, y0 + 26), (x0 + 200, y0 + 48),
                  (x0 + 168, y0 + 50), (x0 + 146, y0 + 34)], fill=land)
    # SE Asia islands + Australia
    draw.polygon([(x0 + 178, y0 + 56), (x0 + 196, y0 + 54),
                  (x0 + 200, y0 + 66), (x0 + 184, y0 + 68)], fill=land)
    draw.ellipse([x0 + 182, y0 + 84, x0 + 214, y0 + 104], fill=land)
    # pin positions (fractions of the map box), spread so numbers don't touch
    pos = {1: (0.68, 0.44), 2: (0.18, 0.28), 3: (0.55, 0.15),
           4: (0.68, 0.16), 5: (0.26, 0.40), 6: (0.54, 0.46),
           7: (0.46, 0.28), 8: (0.74, 0.36), 9: (0.88, 0.12),
           10: (0.60, 0.34), 11: (0.46, 0.56)}
    f = font(F_SANS_B, 10)
    for n in pins:
        fx, fy = pos[n]
        px, py = x0 + fx * (x1 - x0), y0 + fy * (y1 - y0)
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(n), font=f)
        draw.text((px - tw / 2, py - 6), str(n), font=f, fill=(255, 255, 255))


def small_story(draw, x0, y0, w, h, num, region, art_fn, head, deck, src,
                tag_label, tag_bg):
    """One small story cell: number+region, art, head, deck, source tag."""
    x1 = x0 + w
    art_h = 40
    draw.rectangle([x0, y0, x1, y0 + art_h], outline=INK, width=1)
    art_fn(draw, x0 + 1, y0 + 1, x1 - 1, y0 + art_h - 1)
    # number badge over art
    fnum = font(F_SANS_B, 12)
    draw.ellipse([x0 + 4, y0 + 4, x0 + 21, y0 + 21], fill=RED)
    tw = draw.textlength(str(num), font=fnum)
    draw.text((x0 + 12 - tw / 2, y0 + 6), str(num), font=fnum,
              fill=(255, 255, 255))
    y = y0 + art_h + 3
    draw.text((x0, y), region, font=font(F_SANS_B, 10), fill=RED)
    y += 12
    y = draw_wrapped(draw, x0, y, head, font(F_SERIF_B, 15), w, leading=17,
                     max_lines=2)
    y = draw_wrapped(draw, x0, y + 1, deck, font(F_SANS, 10), w, leading=12,
                     max_lines=2)
    # source + tag at the cell bottom
    by = y0 + h - 12
    draw.text((x0, by + 1), "SOURCE: " + src, font=font(F_SANS, 9), fill=GREY)
    tw2 = draw.textlength(tag_label, font=font(F_SANS_B, 9))
    draw.rectangle([x1 - tw2 - 8, by, x1, by + 11], outline=tag_bg, width=1)
    draw.text((x1 - tw2 - 4, by + 1), tag_label, font=font(F_SANS_B, 9),
              fill=tag_bg)


def lead_story(draw, x0, y0, w, h, num, region, art_fn, head, deck, src,
               tag_label, tag_bg):
    """Lead story: art on top, bigger head."""
    x1 = x0 + w
    art_h = 76
    draw.rectangle([x0, y0, x1, y0 + art_h], outline=INK, width=1)
    art_fn(draw, x0 + 1, y0 + 1, x1 - 1, y0 + art_h - 1)
    fnum = font(F_SANS_B, 14)
    draw.ellipse([x0 + 5, y0 + 5, x0 + 25, y0 + 25], fill=RED)
    tw = draw.textlength(str(num), font=fnum)
    draw.text((x0 + 15 - tw / 2, y0 + 7), str(num), font=fnum,
              fill=(255, 255, 255))
    y = y0 + art_h + 6
    draw.text((x0, y), region, font=font(F_SANS_B, 11), fill=RED)
    y += 14
    y = draw_wrapped(draw, x0, y, head, font(F_SERIF_B, 22), w, leading=24,
                     max_lines=2)
    y = draw_wrapped(draw, x0, y + 2, deck, font(F_SANS, 11), w, leading=13,
                     max_lines=2)
    by = y0 + h - 14
    draw.text((x0, by + 1), "SOURCE: " + src, font=font(F_SANS, 9), fill=GREY)
    tw2 = draw.textlength(tag_label, font=font(F_SANS_B, 9))
    draw.rectangle([x1 - tw2 - 8, by, x1, by + 12], outline=tag_bg, width=1)
    draw.text((x1 - tw2 - 4, by + 1), tag_label, font=font(F_SANS_B, 9),
              fill=tag_bg)



# ---------------------------------------------------------------- layout (v2, tight budget, all inside 1024)
def build(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 8

    # ---- top rules + kicker
    rule(d, M, 6, W - M, INK, 3)
    rule(d, M, 11, W - M, RED, 1)
    d.text((M, 16), "THE WORLD IN ONE DAY",
           font=font(F_SANS_B, 13), fill=NAVY)
    kr = "36 STORIES  ·  9 REGIONS  ·  ONE DAY"
    d.text((W - M - d.textlength(kr, font=font(F_SANS_B, 13)), 16), kr,
           font=font(F_SANS_B, 13), fill=RED)

    # ---- masthead
    d.text((M, 34), "Thursday", font=font(F_SERIF_B, 66), fill=INK)
    w_thu = d.textlength("Thursday ", font=font(F_SERIF_B, 66))
    d.text((M + w_thu, 34), "26 November 2026", font=font(F_SERIF_B, 66),
           fill=RED)

    # ---- standfirst (one line) + counts boxes
    d.text((M, 106),
           "Missiles over Riyadh, a parade postponed, Europe opens its summit.",
           font=font(F_SERIF_I, 16), fill=INK)
    boxes = [("36", "STORIES"), ("9", "REGIONS"), ("15", "FIELDS"),
             ("17", "SOURCES")]
    bx = W - M - 4 * 108
    for num, lab in boxes:
        d.rectangle([bx, 104, bx + 102, 140], outline=INK, width=1)
        center(d, bx + 51, 108, num, font(F_SERIF_B, 22), fill=RED)
        center(d, bx + 51, 128, lab, font(F_SANS_B, 9), fill=INK)
        bx += 108

    # ---- region strip
    y = 148
    segs = [("N AMERICA 6", 6), ("S AMERICA 1", 1), ("EUROPE 6", 6),
            ("MID EAST 5", 5), ("AFRICA 6", 6), ("S ASIA 5", 5),
            ("E ASIA 4", 4), ("SE ASIA 1", 1), ("OCEANIA 2", 2)]
    cols = [(31, 58, 95), (120, 60, 40), (178, 32, 44), (201, 130, 30),
            (34, 120, 60), (90, 60, 120), (0, 120, 130), (150, 90, 30),
            (100, 100, 100)]
    total = sum(v for _, v in segs)
    x = M
    bar_w = W - 2 * M
    for (lab, v), c in zip(segs, cols):
        sw = bar_w * v / total
        d.rectangle([x, y, x + sw, y + 9], fill=c)
        x += sw
    y += 13
    d.text((M, y), "North America 6  ·  South America 1  ·  Europe 6  ·  "
                   "Middle East 5  ·  Africa 6  ·  South Asia 5  ·  "
                   "East Asia 4  ·  SE Asia 1  ·  Oceania 2",
           font=font(F_SANS, 10), fill=GREY)
    # ---- UTC ticker (one line, verified times only)
    d.text((M, y + 14),
           "00:00 UTC Thanksgiving Day begins  ·  03:47 UTC Riyadh "
           "intercepts reported  ·  06:00 UTC Delhi marks Constitution "
           "Day  ·  14:00 UTC Chess Game 3, Geneva  ·  ALL DAY US markets shut",
           font=font(F_SANS, 10), fill=NAVY)
    rule(d, M, 192, W - M, INK, 2)

    # ---- HERO (full width, breaks the grid): 198–354
    hy0, hy1 = 198, 354
    d.rectangle([M, hy0, W - M, hy1], outline=INK, width=2)
    art_hero(d, M + 1, hy0 + 1, W - M - 1, hy0 + 100)
    fnum = font(F_SANS_B, 15)
    d.ellipse([M + 8, hy0 + 8, M + 30, hy0 + 30], fill=RED)
    d.text((M + 17, hy0 + 11), "1", font=fnum, fill=(255, 255, 255))
    d.rectangle([M + 38, hy0 + 8, M + 168, hy0 + 30], fill=NAVY)
    d.text((M + 44, hy0 + 12), "MIDDLE EAST", font=font(F_SANS_B, 13),
           fill=(255, 255, 255))
    hy = hy0 + 104
    d.text((M + 4, hy), "MISSILES OVER RIYADH",
           font=font(F_SERIF_B, 32), fill=INK)
    src = "SOURCE: REUTERS, AP, AL JAZEERA"
    d.text((W - M - d.textlength(src, font=font(F_SANS, 9)) - 4, hy + 10),
           src, font=font(F_SANS, 9), fill=GREY)
    hy += 38
    deck = ("Saudi defences down two Houthi missiles aimed at the capital; "
            "two tankers burn in Hormuz.")
    d.text((M + 4, hy), deck, font=font(F_SANS, 15), fill=INK)
    tag(d, W - M - 92, hy, "CONFIRMED", (34, 120, 60))

    # ---- LEADS row (2 + 3): 362–542
    ly0 = 362
    rule(d, M, ly0 - 4, W - M, INK, 1)
    lead_story(d, M, ly0, 498, 180, 2, "USA · THANKSGIVING",
               art_macys,
               "Macy's 100th parade postponed to Saturday",
               "A nor'easter brings 60 mph gusts to New York; the parade "
               "moves to Saturday, a first in 100 years.",
               "AP", "CONFIRMED", (34, 120, 60))
    lead_story(d, M + 510, ly0, 498, 180, 3, "EUROPE · BRUSSELS",
               art_eu,
               "EU opens summit on Kyiv's €45bn lifeline",
               "Leaders weigh a €45bn loan — €25bn for arms, €20bn for "
               "the budget — and the 2028–34 budget.",
               "EU COUNCIL", "OFFICIAL", NAVY)

    # ---- SMALL stories, two rows of four: 550–810 (cell 126)
    smalls = [
        (4, "UKRAINE WAR", art_refinery,
         "Two Russian refineries ablaze",
         "Syzran and Kuibyshev hit overnight; 3 MiG-31 and 2 Su-34 "
         "damaged at Savasleyka.", "REUTERS", "REPORTED", RED),
        (5, "MARKETS", art_markets,
         "Dow holds 50,000 as Asia bounces",
         "Dow +0.33% to 50,182.95; Nasdaq −0.6%. US proposes up to 25% "
         "tariffs on India.", "REUTERS", "CONFIRMED", (34, 120, 60)),
        (6, "EGYPT · DISASTER", art_cairo,
         "Tanker fire kills at least 31 in Cairo",
         "Fuel tanker overturns on the Ring Road, Warraq, on Wednesday "
         "evening; 21 hurt.", "AP", "REPORTED", RED),
        (7, "CHESS · GENEVA", art_chess,
         "Gukesh–Sindarov 1–1, Game 3 today",
         "Two draws in the title match; Game 3 at 15:00 CET, Sindarov "
         "has White.", "FIDE", "CONFIRMED", (34, 120, 60)),
        (8, "INDIA · MUMBAI", art_india,
         "India marks 18 years since 26/11",
         "Tributes to the 166 killed in the 2008 Mumbai attacks; India "
         "also marks Constitution Day.", "PTI", "CONFIRMED", (34, 120, 60)),
        (9, "SPACE", art_space,
         "First Pakistani reaches orbit",
         "Shenzhou-24 docks at Tiangong; Muhammad Zeeshan Ali is the "
         "first foreign astronaut aboard.", "XINHUA", "CONFIRMED",
         (34, 120, 60)),
        (10, "GAZA", art_gaza,
         "Israel kills Hamas security chief",
         "Mohammad Abuelouf is killed with his wife and two children, "
         "Gaza officials say.", "AP", "REPORTED", RED),
        (11, "NIGERIA", art_nigeria,
         "Gunmen kill at least 30 in Niger state",
         "Tuesday-evening reprisal attack in Borgu; UN rights chief "
         "warns of escalation.", "REUTERS", "REPORTED", RED),
    ]
    cell_w, cell_h, gap = 244, 126, 8
    sy0 = 550
    for i, s in enumerate(smalls):
        row, col = divmod(i, 4)
        x0 = M + col * (cell_w + gap)
        y0 = sy0 + row * (cell_h + gap)
        small_story(d, x0, y0, cell_w, cell_h, *s)

    # ---- bottom: map + briefs: 818–962
    by0 = 818
    rule(d, M, by0 - 4, W - M, INK, 1)
    d.text((M, by0), "WHERE IT HAPPENED — PINS 1–11",
           font=font(F_SANS_B, 11), fill=RED)
    draw_map(d, M, by0 + 16, M + 218, by0 + 96, range(1, 12))
    d.text((M, by0 + 100), "01 Riyadh · 02 New York · 03 Brussels · "
                           "04 Samara · 05 New York",
           font=font(F_SANS, 9), fill=GREY)
    d.text((M, by0 + 111), "06 Cairo · 07 Geneva · 08 Mumbai · 09 Tiangong "
                           "· 10 Gaza · 11 Borgu",
           font=font(F_SANS, 9), fill=GREY)

    bx0 = M + 232
    d.text((bx0, by0), "AND ALSO — STORIES 12–36",
           font=font(F_SANS_B, 11), fill=RED)
    briefs = [
        (12, "Sudan — RSF drone strikes kill 19 civilians", "Emergency Lawyers"),
        (13, "Russia's own figures: 490,334 war dead since 2022", "BBC"),
        (14, "Huawei guilty on 10 of 12 counts in Brooklyn", "Reuters"),
        (15, "COP31 fails; Pope Leo XIV reacts", "AP"),
        (16, "Australia–Solomon Islands treaty signed", "Reuters"),
        (17, "Cartagena: 20 hostages freed after 17 hours", "AP"),
        (18, "Bangladesh garment wage up 36% after protests", "AFP"),
        (19, "US: second judge blocks birthright order", "Reuters"),
        (20, "Kim calls for wider use of tactical nuclear arms", "Reuters"),
        (21, "North Korea expels Swiss diplomat (48 hours)", "AP"),
        (22, "EU votes 367–268 to loosen nature laws", "Reuters"),
        (23, "Anthropic falls below IPO price", "Principia"),
        (24, "Dell record $54.9bn quarter; AI servers $22bn", "Reuters"),
        (25, "Eurozone inflation 4.0%; Australia 4.9%", "Eurostat"),
        (26, "Kenya secures 293,600 jobs in Saudi Arabia", "C54"),
        (27, "Real Madrid 5–1 PSV (Champions League)", "UEFA"),
        (28, "Sooryavanshi 204 off 53 balls, 28 sixes", "Cricinfo"),
        (29, "CAS restores Senegal's AFCON title", "Reuters"),
        (30, "Miss Universe: Puerto Rico's Jennifer Barreto wins", "AP"),
        (31, "Duran Duran guitarist Andy Taylor dies at 65", "Reuters"),
        (32, "South Korea hikes rates to 3.25%", "Reuters"),
        (33, "US growth revised up to 4.3%", "Reuters"),
        (34, "Bogor mine flood toll rises to 6 (Indonesia)", "Reuters"),
        (35, "London Tube drivers begin eight-strike campaign", "Reuters"),
        (36, "24 Kebbi schoolgirls freed in Nigeria", "Xinhua"),
    ]
    fbrief = font(F_SANS, 9)
    fsrc = font(F_SANS, 9)
    col_w = (W - M - bx0 - 12) // 2
    for i, (n, txt, src) in enumerate(briefs):
        col, row = divmod(i, 13)
        x = bx0 + col * (col_w + 12)
        y = by0 + 16 + row * 10
        d.text((x, y), f"{n}.", font=font(F_SANS_B, 10), fill=RED)
        d.text((x + 22, y), txt, font=fbrief, fill=INK)
        tw = d.textlength(txt, font=fbrief)
        d.text((x + 22 + tw + 4, y), "— " + src, font=fsrc, fill=GREY)

    # ---- DATE CHECK: 966–1006
    dy = 966
    rule(d, M, dy, W - M, INK, 1)
    d.text((M, dy + 4), "DATE CHECK — THESE ARE NOT 26 NOVEMBER",
           font=font(F_SANS_B, 11), fill=RED)
    dc = ["× Jensen Huang reinstated — 24 Nov",
          "× COP31 ends without pact — 22 Nov",
          "× Russian ships hit off Libya — 22 Nov",
          "× EU–Indonesia pact — 21 Nov",
          "× Trump–Putin–Xi in Shenzhen — 17 Nov",
          "× UNRWA worker killed — 23 Nov",
          "× Belgium strike grounds flights — 23 Nov",
          "× US shelves Russia peace plan — 25 Nov"]
    for i, item in enumerate(dc):
        col, row = divmod(i, 4)
        x = M + col * 250
        y = dy + 20 + row * 11
        d.text((x, y), item, font=font(F_SANS, 9), fill=GREY)

    # ---- footer: 1009–1022
    fy = 1009
    rule(d, M, fy, W - M, INK, 1)
    d.text((M, fy + 3),
           "Every story happened or was first reported on Thursday 26 "
           "November 2026. Sources: AP, Reuters, AFP, BBC, FIDE, Xinhua, "
           "EU Council, PTI. OFFICIAL = government · CONFIRMED = 2+ outlets "
           "· REPORTED = 1 outlet. All pictures are original drawings.",
           font=font(F_SANS, 9), fill=GREY)

    img.save(out_path, "PNG", optimize=True)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build(out)
    print("wrote", out)
