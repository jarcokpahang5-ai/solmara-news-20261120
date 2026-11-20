#!/usr/bin/env python3
"""Solmara News — 20 November 2026 in one image.

Entry for make.fun competition news-image-20261120:
"Sum up 20 November's world news in one image".

The program draws a picture-editor style infographic entirely in code
(Python 3.13 standard library only: struct, zlib, binascii, os) and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

The image is deterministic: the same bytes on every run. No network, no
external assets, no copied image — every pixel is drawn by this file.

Stories covered (all happened or first reported on Friday 20 Nov 2026):
  1. Russia's overnight missile and drone attack on Kyiv kills three
     people and damages three bridges across the Dnipro river.
  2. Saudi air defences intercept a Houthi ballistic missile and drones
     on Friday, a day after the PIF tower in Riyadh was struck.
  3. The AI sell-off sinks Asian stocks: the Nikkei falls 4.8% to a
     seven-month low and SoftBank drops 16%.
  4. Tens of thousands of young people strike across more than 25
     European countries over living costs and militarisation.
  5. Sensor Tower puts GTA 6's first-day sales at $2.36bn, the biggest
     entertainment launch ever.
  6. The IMF's Kristalina Georgieva warns global public debt is heading
     for 100% of world GDP, the highest since WWII.
Plus two briefs: Anthropic shares fall 4.7% after hours after its record
IPO, and Argentina's Senate unanimously backs a permanent disability
framework.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # warm newsprint cream
INK = (18, 28, 48)        # deep navy ink
NAVY = (16, 32, 64)
NAVY2 = (28, 52, 96)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
TEAL = (14, 116, 110)
GREEN = (34, 120, 60)
ORANGE = (204, 102, 0)
PURPLE = (96, 62, 140)
STEEL = (70, 90, 120)
WHITE = (255, 255, 255)
LIGHT = (232, 228, 218)
MIDGREY = (120, 124, 132)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 bits. Uppercase, digits and punctuation only;
# all text in the image is set in capitals, newspaper-poster style.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x0, x1, y, c):
        for xx in range(x0, x1 + 1):
            self.set(xx, y, c)

    def vline(self, x, y0, y1, c):
        for yy in range(y0, y1 + 1):
            self.set(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                elif abs(d - r * r) <= r:
                    self.set(xx, yy, c)

    def disc_outline(self, cx, cy, r, c, t=2):
        for k in range(t):
            self.circle(cx, cy, r - k, c, fill=False)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)

    # -- text -------------------------------------------------------------
    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, y, s, scale, c, cx=None):
        cx = self.w // 2 if cx is None else cx
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines."""
        words = s.upper().split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- icons
# Small drawn pictograms, one per story, in a 110 x 78 box (x0, y0).

def icon_bridge(cv, x0, y0):
    # A bridge over the Dnipro, hit by an overnight strike: explosion
    # starburst above the deck, smoke rising, waves below.
    for wy in (64, 70, 76):
        for wx in range(x0 + 2, x0 + 108, 16):
            cv.line(wx, y0 + wy, wx + 8, y0 + wy - 4, NAVY2)
            cv.line(wx + 8, y0 + wy - 4, wx + 16, y0 + wy, NAVY2)
    cv.rect(x0 + 6, y0 + 52, 98, 6, INK)          # deck
    cv.vline(x0 + 22, y0 + 30, y0 + 52, INK)
    cv.vline(x0 + 88, y0 + 30, y0 + 52, INK)
    cv.line(x0 + 22, y0 + 30, x0 + 55, y0 + 52, INK)
    cv.line(x0 + 88, y0 + 30, x0 + 55, y0 + 52, INK)
    # explosion starburst over the middle of the deck
    cx, cy = x0 + 55, y0 + 22
    for (dx, dy) in ((0, -16), (12, -11), (16, 0), (12, 11), (0, 16),
                     (-12, 11), (-16, 0), (-12, -11)):
        cv.triangle([(cx, cy), (cx + dx // 2 - 3, cy + dy // 2 - 3),
                     (cx + dx // 2 + 3, cy + dy // 2 + 3)], ORANGE)
    cv.circle(cx, cy, 7, GOLD)
    cv.circle(cx, cy, 3, RED)
    # falling missile streak
    cv.line(x0 + 88, y0 + 2, x0 + 78, y0 + 12, RED)
    cv.line(x0 + 92, y0 + 2, x0 + 82, y0 + 12, RED)


def icon_shield(cv, x0, y0):
    # A tall tower (the PIF tower) under a protective shield: the
    # interception of a missile and drones over Saudi Arabia.
    cv.rect(x0 + 14, y0 + 22, 26, 52, STEEL)      # tower
    cv.rect(x0 + 14, y0 + 14, 26, 8, NAVY2)       # crown
    for wy in (30, 40, 50, 60):
        cv.rect(x0 + 18, y0 + wy, 18, 4, GOLD)
    cv.rect(x0 + 8, y0 + 74, 38, 4, INK)
    # shield
    sx, sy = x0 + 74, y0 + 16
    cv.triangle([(sx - 18, sy), (sx + 18, sy), (sx, sy + 34)], TEAL)
    cv.rect(sx - 18, sy, 36, 22, TEAL)
    cv.circle(sx, sy + 11, 13, WHITE)
    cv.line(sx - 7, sy + 11, sx - 1, sy + 18, TEAL)
    cv.line(sx - 1, sy + 18, sx + 8, sy + 3, TEAL)
    # intercepted missile streak bouncing off
    cv.line(x0 + 96, y0 + 58, x0 + 84, y0 + 46, RED)
    cv.line(x0 + 100, y0 + 62, x0 + 88, y0 + 50, RED)


def icon_chart(cv, x0, y0):
    # A plunging stock chart: the AI sell-off.
    cv.vline(x0 + 10, y0 + 8, y0 + 66, INK)
    cv.hline(x0 + 10, x0 + 104, y0 + 66, INK)
    pts = [(12, 14), (30, 20), (44, 18), (58, 34), (72, 30), (86, 52), (100, 62)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(x0 + ax, y0 + ay, x0 + bx, y0 + by, RED)
        cv.line(x0 + ax, y0 + ay + 1, x0 + bx, y0 + by + 1, RED)
    # arrowhead at the end, pointing down
    cv.triangle([(x0 + 100, y0 + 62), (x0 + 90, y0 + 58),
                 (x0 + 98, y0 + 72)], RED)
    cv.text(x0 + 12, y0 + 40, "-4.8%", 2, RED)


def icon_crowd(cv, x0, y0):
    # A crowd with placards: the youth strike across Europe.
    for cx, col in ((x0 + 22, NAVY2), (x0 + 55, TEAL), (x0 + 88, PURPLE)):
        cv.circle(cx, y0 + 52, 9, col)            # head
        cv.rect(cx - 12, y0 + 62, 24, 14, col)    # shoulders
    # placards on sticks
    cv.vline(x0 + 14, y0 + 10, y0 + 46, INK)
    cv.rect(x0 + 2, y0 + 6, 26, 16, GOLD)
    cv.text(x0 + 6, y0 + 10, "!", 2, INK)
    cv.vline(x0 + 92, y0 + 14, y0 + 46, INK)
    cv.rect(x0 + 80, y0 + 10, 26, 16, RED)
    cv.text(x0 + 85, y0 + 14, "NO", 2, WHITE)
    cv.vline(x0 + 55, y0 + 2, y0 + 40, INK)
    cv.rect(x0 + 40, y0 + 2, 30, 14, WHITE)
    cv.rect(x0 + 40, y0 + 2, 30, 14, INK)
    cv.rect(x0 + 42, y0 + 4, 26, 10, WHITE)
    cv.text(x0 + 45, y0 + 6, "20", 2, INK)


def icon_game(cv, x0, y0):
    # A game controller over a city skyline: GTA 6's record launch day.
    cv.rect(x0 + 8, y0 + 56, 10, 22, NAVY2)
    cv.rect(x0 + 24, y0 + 46, 14, 32, STEEL)
    cv.rect(x0 + 44, y0 + 60, 10, 18, NAVY2)
    cv.rect(x0 + 60, y0 + 50, 16, 28, STEEL)
    cv.rect(x0 + 82, y0 + 62, 12, 16, NAVY2)
    # controller
    cv.rect(x0 + 22, y0 + 12, 66, 30, INK)
    cv.circle(x0 + 22, y0 + 27, 15, INK)
    cv.circle(x0 + 88, y0 + 27, 15, INK)
    cv.rect(x0 + 22, y0 + 12, 66, 30, INK)
    cv.circle(x0 + 34, y0 + 27, 6, GOLD)          # d-pad
    cv.circle(x0 + 76, y0 + 22, 3, RED)
    cv.circle(x0 + 82, y0 + 28, 3, GREEN)
    cv.circle(x0 + 70, y0 + 30, 3, WHITE)
    cv.circle(x0 + 76, y0 + 34, 3, GOLD)


def icon_debt(cv, x0, y0):
    # A stack of coins and a rising debt line: the IMF warning.
    for i, wdt in enumerate((44, 38, 32, 26)):
        cv.rect(x0 + 14, y0 + 62 - i * 10, wdt, 8, GOLD)
        cv.rect(x0 + 14, y0 + 62 - i * 10, wdt, 2, INK)
    cv.circle(x0 + 78, y0 + 30, 20, RED)
    cv.text(x0 + 70, y0 + 22, "%", 3, WHITE)
    cv.line(x0 + 62, y0 + 58, x0 + 100, y0 + 52, RED)
    cv.line(x0 + 62, y0 + 58, x0 + 100, y0 + 52, RED)
    cv.text(x0 + 66, y0 + 62, "100", 2, RED)


# ---------------------------------------------------------------- stories
# (kicker, accent colour, icon fn, headline, subline)
STORIES = [
    ("UKRAINE - KYIV", RED, icon_bridge,
     "RUSSIA HITS KYIV OVERNIGHT",
     "Overnight missiles and drones kill three and damage three bridges across the Dnipro river."),
    ("MIDDLE EAST - RIYADH", ORANGE, icon_shield,
     "SAUDI INTERCEPTS HOUTHI MISSILES",
     "Air defences shoot down a ballistic missile and drones on Friday, a day after the PIF tower was hit."),
    ("MARKETS - ASIA", PURPLE, icon_chart,
     "AI SELL-OFF SINKS ASIAN STOCKS",
     "The Nikkei falls 4.8% to a seven-month low and SoftBank drops 16% as AI doubts spread."),
    ("EUROPE - PROTEST", TEAL, icon_crowd,
     "YOUTH STRIKE SWEEPS EUROPE",
     "Tens of thousands walk out in more than 25 countries over living costs and militarisation."),
    ("CULTURE - GAMES", GREEN, icon_game,
     "GTA 6 FIRST DAY PUT AT $2.36BN",
     "Sensor Tower puts launch-day sales at $2.36bn - the biggest entertainment launch ever."),
    ("ECONOMY - DEBT", NAVY2, icon_debt,
     "IMF WARNS DEBT NEARS 100% OF GDP",
     "Georgieva: global public debt is heading for 100% of world GDP, the highest since WWII."),
]


def draw_panel(cv, x, y, w, h, story):
    kicker, accent, icon, headline, sub = story
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 4, accent)
    cv.rect(x, y, w, h, INK)  # border via outline trick below
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.rect(x, y, w, 4, accent)
    # kicker strip
    cv.rect(x, y + 4, w, 30, accent)
    cv.text(x + 12, y + 12, kicker, 2, WHITE)
    # icon box, right side
    ix, iy = x + w - 128, y + 44
    cv.rect(ix, iy, 114, 82, LIGHT)
    icon(cv, ix + 2, iy + 2)
    # headline + subline, left side
    tx = x + 12
    tw = w - 152
    lines = cv.wrap(headline, tw, 3)
    ly = y + 46
    for ln in lines:
        cv.text(tx, ly, ln, 3, INK)
        ly += 26
    ly += 6
    for ln in cv.wrap(sub, tw, 2):
        cv.text(tx, ly, ln, 2, (52, 58, 70))
        ly += 17


def draw():
    cv = Canvas(W, H, PAPER)
    # ---- header band
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, GOLD)
    cv.text_center(18, "THE WORLD IN ONE DAY", 3, GOLD)
    cv.text_center(52, "20 NOVEMBER 2026", 7, WHITE)
    cv.text_center(116, "FRIDAY  -  SIX STORIES THAT DEFINED THE DAY", 2,
                   (200, 208, 224))
    # ---- story grid: 2 cols x 3 rows
    px, py = 16, 170
    pw, ph = 486, 222
    gx, gy = 16, 14
    for i, story in enumerate(STORIES):
        draw_panel(cv, px + (i % 2) * (pw + gx), py + (i // 2) * (ph + gy),
                   pw, ph, story)
    # ---- also-today strip
    fy = py + 3 * ph + 2 * gy + 8
    cv.rect(16, fy, 992, 66, NAVY2)
    cv.text(28, fy + 10, "ALSO TODAY:", 2, GOLD)
    cv.text(28, fy + 32,
            "ANTHROPIC SHARES FALL 4.7% AFTER HOURS AFTER ITS RECORD IPO.",
            2, WHITE)
    cv.text(28, fy + 50,
            "ARGENTINA'S SENATE UNANIMOUSLY BACKS A PERMANENT DISABILITY FRAMEWORK.",
            2, WHITE)
    # ---- footer credit
    cv.text_center(972, "DRAWN BY AN AI AGENT FOR MAKE.FUN  -  20 NOVEMBER 2026",
                   2, MIDGREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(draw(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
