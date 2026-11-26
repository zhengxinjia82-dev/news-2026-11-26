#!/usr/bin/env python3
"""news-image-20261126: draw the Thursday 26 November 2026 front page.

Fresh code written for this day only, from the news-image style guide:
light paper front page, serif masthead, UTC timeline, 3 illustrated leads,
10 illustrated features, briefs, dotted world map with 13 pins, DATE CHECK,
per-story verification badges and sources, stat banner inside every picture.
All 18 stories were verified as happening, or first reported, on 26 Nov 2026.
Note: PIL text coordinates are top-y, not baselines; all layout math below
uses top-y.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))

W = H = 1024
MX = 24
CW = W - 2 * MX
PAPER = "#f7f3e8"
INK = "#111111"
GRAY = "#555555"
RED = "#b91c1c"
RULE = "#c9c2ae"
NAVY = "#1e3a5f"
MAPDOT = "#948a74"
BADGE = {"CONFIRMED": "#15803d", "REPORTED": "#1d4ed8",
         "CLAIM": "#b45309", "OFFICIAL": "#6d28d9"}

FDIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(f"{FDIR}/{name}.ttf", size)


def tw(draw, text, fnt):
    return draw.textbbox((0, 0), text, font=fnt)[2]


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if tw(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(draw, text, fname, start, max_w):
    size = start
    while size > 20 and tw(draw, text, font(fname, size)) > max_w:
        size -= 1
    return font(fname, size)


def center(draw, cx, y, text, fnt, fill):
    draw.text((cx - tw(draw, text, fnt) / 2, y), text, font=fnt, fill=fill)


def fail(msg):
    print(f"LAYOUT FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- kicker
fk = font("DejaVuSans-Bold", 13)
d.text((MX, 10), DATA["kicker_left"], font=fk, fill=RED)
r = DATA["kicker_right"]
d.text((W - MX - tw(d, r, fk), 10), r, font=fk, fill=RED)
d.line([(MX, 32), (W - MX, 32)], fill=RED, width=2)

# ------------------------------------------------------------- masthead
fm = fit(d, DATA["date_label"].upper(), "DejaVuSerif-Bold", 58, 936)
label = DATA["date_label"].upper()
d.text(((W - tw(d, label, fm)) / 2, 40), label, font=fm, fill=INK)
d.line([(MX, 104), (W - MX, 104)], fill=INK, width=2)
d.line([(MX, 107), (W - MX, 107)], fill=INK, width=1)
d.text((MX, 112), DATA["subtitle"], font=font("DejaVuSerif", 15), fill=GRAY)

# ------------------------------------------------------------- timeline
# The day is only ~3h old in UTC at build time, so the axis honestly covers
# 00:00-06:00 UTC ("so far"); callout labels sit on spread slots with
# leader lines to their dots.
d.text((MX, 134), DATA["timeline_label"], font=font("DejaVuSans-Bold", 11),
       fill=INK)
TL_X0, TL_X1, TL_Y = 150, 1000, 168
d.line([(TL_X0, TL_Y), (TL_X1, TL_Y)], fill=NAVY, width=3)
for h in range(7):
    x = TL_X0 + h * (TL_X1 - TL_X0) / 6
    d.line([(x, TL_Y - 4), (x, TL_Y + 4)], fill=NAVY, width=2)
d.text((TL_X0 - 8, TL_Y + 8), "00:00 UTC", font=font("DejaVuSans", 9),
       fill=GRAY)
end = "06:00 UTC"
d.text((TL_X1 - tw(d, end, font("DejaVuSans", 9)), TL_Y + 8), end,
       font=font("DejaVuSans", 9), fill=GRAY)


def tl_x(hhmm):
    h, m = (int(v) for v in hhmm.split(":"))
    return TL_X0 + ((h * 60 + m) / 360.0) * (TL_X1 - TL_X0)


slots = [(280, "above"), (440, "below"), (600, "above"), (760, "below"),
         (920, "above")]
fb = font("DejaVuSans-Bold", 11)
for ev, (sx, side) in zip(DATA["timeline"], slots):
    x = tl_x(ev["time"])
    d.ellipse([x - 5, TL_Y - 5, x + 5, TL_Y + 5], fill=RED)
    lab = f'{ev["time"]}  {ev["label"]}'
    lw = tw(d, lab, fb)
    lx = min(max(sx - lw / 2, MX), W - MX - lw)
    if side == "above":
        ly = 146
        d.line([(x, TL_Y - 6), (lx + lw / 2, ly + 12)], fill=GRAY, width=1)
        d.text((lx, ly), lab, font=fb, fill=INK)
    else:
        ly = 186
        d.line([(x, TL_Y + 6), (lx + lw / 2, ly - 2)], fill=GRAY, width=1)
        d.text((lx, ly), lab, font=fb, fill=INK)
d.line([(MX, 202), (W - MX, 202)], fill=RULE, width=1)

# ------------------------------------------------------- illustration art
# All geometry is proportional to (w, h) so the same motif works at
# headline size (312x100) and feature size (187x32).
TINTS = {"nuke": "#cfe0f0", "chart": "#e8f0e4", "tariff": "#f3e8d8",
         "plane": "#dde8f5", "building": "#e9e4d8", "river": "#d8ecf3",
         "ballot": "#efe6f0", "hoop": "#f5e3d3", "shield": "#e2e8f0",
         "jet": "#dbe7f3", "bridge": "#e8e2d5", "closed": "#e5e5e5"}


def art(draw, key, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=TINTS[key], outline=RULE)
    cx, cy = x + w / 2, y + h / 2
    if key == "nuke":
        draw.polygon([(cx, y + h * 0.10), (cx - w * 0.05, y + h * 0.78),
                      (cx + w * 0.05, y + h * 0.78)], fill="#b91c1c")
        draw.rectangle([cx - w * 0.07, y + h * 0.78, cx + w * 0.07,
                        y + h * 0.88], fill=INK)
        draw.line([(x + w * 0.05, cy), (cx - w * 0.08, cy)], fill=NAVY,
                  width=2)
        draw.line([(cx + w * 0.08, cy), (x + w * 0.95, cy - h * 0.12)],
                  fill=NAVY, width=2)
        for fx, fy in [(0.06, 0.14), (0.92, 0.18), (0.62, 0.38)]:
            ox, oy = x + w * fx, y + h * fy
            draw.ellipse([ox - 3, oy - 3, ox + 3, oy + 3], fill=NAVY)
    elif key == "chart":
        draw.line([(x + w * 0.05, y + h * 0.88), (x + w * 0.95, y + h * 0.88)],
                  fill=INK, width=2)
        draw.line([(x + w * 0.05, y + h * 0.88), (x + w * 0.05, y + h * 0.12)],
                  fill=INK, width=2)
        pts = [(x + w * 0.08, y + h * 0.78), (x + w * 0.35, y + h * 0.55),
               (x + w * 0.60, y + h * 0.62), (x + w * 0.92, y + h * 0.16)]
        draw.line(pts, fill=RED, width=3)
        for px, py in pts[1:]:
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
    elif key == "tariff":
        for i, c in enumerate(["#b91c1c", "#1d4ed8", "#15803d"]):
            bh = h * (0.34 + 0.20 * i)
            bx = x + w * 0.05 + i * (w * 0.30)
            draw.rectangle([bx, y + h * 0.88 - bh, bx + w * 0.26,
                            y + h * 0.88], fill=c)
        pct = font("DejaVuSerif-Bold", 30 if h > 60 else 16)
        draw.text((x + w * 0.78, y + h * 0.06), "%", font=pct, fill=NAVY)
    elif key == "plane":
        draw.ellipse([x + w * 0.15, cy - h * 0.22, x + w * 0.85,
                      cy + h * 0.22], fill=NAVY)
        draw.polygon([(cx, cy - h * 0.22), (cx + w * 0.06, cy - h * 0.45),
                      (cx + w * 0.12, cy - h * 0.22)], fill=NAVY)
        draw.polygon([(cx - w * 0.04, cy + h * 0.22),
                      (cx - w * 0.11, cy + h * 0.45),
                      (cx - w * 0.02, cy + h * 0.22)], fill=NAVY)
        draw.line([(x + w * 0.03, cy + h * 0.10), (x + w * 0.15, cy + h * 0.10)],
                  fill=GRAY, width=2)
    elif key == "building":
        for i, bh in enumerate([0.55, 0.85, 0.65]):
            bx = x + w * 0.06 + i * (w * 0.30)
            draw.rectangle([bx, y + h * 0.90 - h * bh, bx + w * 0.24,
                            y + h * 0.90], fill=NAVY if i == 1 else "#5b6b7f")
            for wy in range(3):
                wy0 = y + h * 0.90 - h * (0.18 + 0.22 * wy)
                draw.rectangle([bx + 3, wy0, bx + 9, wy0 + h * 0.10],
                               fill="#f7f3e8")
    elif key == "river":
        for k in range(3):
            yy = y + h * (0.22 + 0.28 * k)
            pts = [(x + w * 0.05 + j * (w * 0.90) / 6,
                    yy + (h * 0.10 if j % 2 else -h * 0.10))
                   for j in range(7)]
            draw.line(pts, fill="#1d4ed8", width=2)
    elif key == "ballot":
        draw.rectangle([cx - w * 0.12, y + h * 0.14, cx + w * 0.12,
                        y + h * 0.86], outline=NAVY, width=2)
        draw.line([(cx - w * 0.08, y + h * 0.26), (cx + w * 0.08, y + h * 0.26)],
                  fill=NAVY, width=3)
        draw.line([(cx - w * 0.05, cy + h * 0.05), (cx - w * 0.01, cy + h * 0.18),
                   (cx + w * 0.07, cy - h * 0.18)], fill="#15803d", width=3)
    elif key == "hoop":
        draw.rectangle([x + w * 0.82, y + h * 0.12, x + w * 0.88,
                        y + h * 0.88], fill=INK)
        draw.ellipse([x + w * 0.68, cy - h * 0.12, x + w * 0.86,
                      cy + h * 0.12], outline=RED, width=2)
        draw.ellipse([x + w * 0.06, cy - h * 0.32, x + w * 0.20,
                      cy + h * 0.32], fill="#b45309", outline=INK)
    elif key == "shield":
        draw.polygon([(cx, y + h * 0.10), (cx + w * 0.12, y + h * 0.22),
                      (cx + w * 0.10, y + h * 0.82), (cx, y + h * 0.94),
                      (cx - w * 0.10, y + h * 0.82),
                      (cx - w * 0.12, y + h * 0.22)], fill=NAVY)
        draw.line([(cx - w * 0.05, cy), (cx - w * 0.01, cy + h * 0.14),
                   (cx + w * 0.06, cy - h * 0.16)], fill="white", width=3)
    elif key == "jet":
        draw.polygon([(x + w * 0.05, cy + h * 0.22), (x + w * 0.92, cy - h * 0.30),
                      (x + w * 0.84, cy + h * 0.26)], fill=NAVY)
        draw.polygon([(x + w * 0.45, cy - h * 0.06), (x + w * 0.60, cy - h * 0.45),
                      (x + w * 0.70, cy - h * 0.06)], fill=NAVY)
        draw.line([(x + w * 0.03, cy - h * 0.30), (x + w * 0.40, cy - h * 0.30)],
                  fill=GRAY, width=2)
    elif key == "bridge":
        draw.line([(x + w * 0.05, y + h * 0.86), (x + w * 0.95, y + h * 0.86)],
                  fill=INK, width=3)
        draw.arc([x + w * 0.15, y + h * 0.06, x + w * 0.85, y + h * 0.98],
                 180, 360, fill=RED, width=3)
        for fx in (0.3, 0.5, 0.7):
            draw.line([(x + w * fx, y + h * 0.86), (x + w * fx, y + h * 0.30)],
                      fill=GRAY, width=1)
    elif key == "closed":
        for i in range(5):
            draw.rectangle([x + w * 0.05 + i * (w * 0.90) / 5, y + h * 0.10,
                            x + w * 0.05 + (i + 1) * (w * 0.90) / 5,
                            y + h * 0.34],
                           fill=RED if i % 2 == 0 else "#f7f3e8")
        draw.rectangle([cx - w * 0.14, y + h * 0.52, cx + w * 0.14,
                        y + h * 0.90], fill=NAVY)
        sf = font("DejaVuSans-Bold", 9 if h <= 60 else 12)
        word = "SHUT"
        draw.text((cx - tw(d, word, sf) / 2, y + h * 0.62), word, font=sf,
                  fill="white")


def banner(draw, x, y, w, h, text, size):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    f = fit(d, text, "DejaVuSans-Bold", size, w - 8)
    center(d, x + w / 2, y + (h - f.size) / 2 - 1, text, f, "white")


def badge_line(draw, x, y, badge, source, size=10):
    f = font("DejaVuSans-Bold", size)
    draw.text((x, y), f"● {badge} · {source}", font=f, fill=BADGE[badge])


# ------------------------------------------------------------- headlines
HL_Y, HL_H, HL_W, HL_GAP = 208, 100, 312, 20
for i, st in enumerate(DATA["headlines"]):
    x = MX + i * (HL_W + HL_GAP)
    art(d, st["art"], x, HL_Y, HL_W, HL_H)
    banner(d, x, HL_Y + HL_H - 26, HL_W, 26, st["banner"], 16)
    d.ellipse([x, HL_Y + HL_H + 8, x + 18, HL_Y + HL_H + 26], fill=RED)
    num = str(st["n"])
    nf = font("DejaVuSans-Bold", 11)
    d.text((x + 9 - tw(d, num, nf) / 2, HL_Y + HL_H + 11), num, font=nf,
           fill="white")
    d.text((x + 24, HL_Y + HL_H + 10), st["region"],
           font=font("DejaVuSans-Bold", 11), fill=RED)
    d.text((x + HL_W - tw(d, st["place"], font("DejaVuSans-Bold", 11)),
            HL_Y + HL_H + 10), st["place"], font=font("DejaVuSans-Bold", 11),
           fill=GRAY)
    title_lines = wrap(d, st["title"], font("DejaVuSerif-Bold", 21), HL_W)
    if len(title_lines) > 3:
        fail(f"headline {st['n']} title wraps to {len(title_lines)} lines")
    for j, ln in enumerate(title_lines):
        d.text((x, HL_Y + 132 + j * 25), ln,
               font=font("DejaVuSerif-Bold", 21), fill=INK)
    body_lines = wrap(d, st["body"], font("DejaVuSans", 12), HL_W)
    if len(body_lines) > 2:
        fail(f"headline {st['n']} body wraps to {len(body_lines)} lines")
    for j, ln in enumerate(body_lines):
        d.text((x, HL_Y + 210 + j * 16), ln,
               font=font("DejaVuSans", 12), fill=INK)
    badge_line(d, x, HL_Y + 242, st["badge"], st["source"])
d.line([(MX, 468), (W - MX, 468)], fill=RULE, width=1)

# ---------------------------------------------------------- numbers bar
d.text((MX, 476), "THE DAY IN NUMBERS", font=font("DejaVuSans-Bold", 12),
       fill=INK)
NB_W = CW // 5
for i, nb in enumerate(DATA["numbers"]):
    x = MX + i * NB_W
    d.text((x, 492), nb["num"], font=font("DejaVuSerif-Bold", 24), fill=RED)
    cap = wrap(d, nb["cap"], font("DejaVuSans", 11), NB_W - 8)
    if len(cap) > 1:
        fail(f"number {nb['num']} caption wraps to {len(cap)} lines")
    d.text((x, 518), cap[0], font=font("DejaVuSans", 11), fill=GRAY)
d.line([(MX, 536), (W - MX, 536)], fill=RULE, width=1)

# ------------------------------------------------------------- secondary
SEC_W, SEC_GAP = 187, 10
SEC_ROWS = [544, 662]
for row_i, ry0 in enumerate(SEC_ROWS):
    for col in range(5):
        st = DATA["secondary"][row_i * 5 + col]
        x = MX + col * (SEC_W + SEC_GAP)
        art(d, st["art"], x, ry0, SEC_W, 32)
        banner(d, x, ry0 + 17, SEC_W, 15, st["banner"], 11)
        tag_region = st["region"].replace("SOUTH ASIA", "S. ASIA").replace(
            "EAST ASIA", "E. ASIA")
        tag = f'{st["n"]} · {tag_region}'
        tf = font("DejaVuSans-Bold", 10)
        if tw(d, tag, tf) > SEC_W:
            fail(f"secondary {st['n']} tag too wide: {tag}")
        d.text((x, ry0 + 37), tag, font=tf, fill=RED)
        tl = wrap(d, st["title"], font("DejaVuSans-Bold", 12), SEC_W)
        if len(tl) > 2:
            fail(f"secondary {st['n']} title wraps to {len(tl)} lines")
        for j, ln in enumerate(tl):
            d.text((x, ry0 + 50 + j * 13), ln,
                   font=font("DejaVuSans-Bold", 12), fill=INK)
        bl = wrap(d, st["body"], font("DejaVuSans", 11), SEC_W)
        if len(bl) > 2:
            fail(f"secondary {st['n']} body wraps to {len(bl)} lines: {bl}")
        for j, ln in enumerate(bl):
            d.text((x, ry0 + 77 + j * 10), ln,
                   font=font("DejaVuSans", 11), fill=INK)
        badge_line(d, x, ry0 + 100, st["badge"], st["source"], size=9)
d.line([(MX, 780), (W - MX, 780)], fill=RULE, width=1)

# --------------------------------------------------------- bottom band
# ---- world map (own rectangle landmask, dotted)
MAP_X0, MAP_X1, MAP_Y0, MAP_Y1 = MX, 360, 804, 868
d.text((MX, 790), "WHERE IT HAPPENED — 13 PINS",
       font=font("DejaVuSans-Bold", 12), fill=INK)
LAND = [(50, 71, -168, -55), (25, 49, -125, -67), (8, 32, -117, -83),
        (60, 83, -58, -20), (-5, 10, -80, -35), (-55, -5, -73, -40),
        (36, 70, -11, 40), (50, 58, -5, 2), (0, 35, -18, 32),
        (-35, 0, 12, 40), (12, 42, 35, 60), (5, 35, 60, 105),
        (20, 53, 75, 135), (50, 75, 40, 180), (-10, 20, 95, 140),
        (30, 45, 129, 146), (-40, -10, 113, 154), (-47, -34, 166, 178)]
CELL = 4
COLS = (MAP_X1 - MAP_X0) // CELL
ROWS = (MAP_Y1 - MAP_Y0) // CELL


def on_land(lat, lon):
    return any(a <= lat <= b and c <= lon <= e
               for a, b, c, e in LAND)


for r in range(ROWS):
    lat = 85 - (r + 0.5) * 145 / ROWS
    for c in range(COLS):
        lon = -180 + (c + 0.5) * 360 / COLS
        if on_land(lat, lon):
            px, py = MAP_X0 + c * CELL, MAP_Y0 + r * CELL
            d.ellipse([px, py, px + 2, py + 2], fill=MAPDOT)


def pin_xy(lat, lon):
    return (MAP_X0 + (lon + 180) / 360 * (MAP_X1 - MAP_X0),
            MAP_Y0 + (85 - lat) / 145 * (MAP_Y1 - MAP_Y0))


OFFSETS = {1: (-18, -14), 2: (14, -18), 3: (-24, 10), 4: (28, 2),
           5: (24, -14), 6: (-16, 18), 7: (18, 8), 8: (-14, -14),
           9: (-16, 8), 10: (-30, -10), 11: (2, 18), 12: (-16, 12),
           13: (16, -12)}
pins = DATA["headlines"] + DATA["secondary"]
for st in pins:
    px, py = pin_xy(st["lat"], st["lon"])
    ox, oy = OFFSETS.get(st["n"], (0, 0))
    qx, qy = px + ox, py + oy
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    if (ox, oy) != (0, 0):
        d.line([(px, py), (qx, qy)], fill=RED, width=1)
    d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline="white")
    num = str(st["n"])
    nf = font("DejaVuSans-Bold", 9)
    d.text((qx - tw(d, num, nf) / 2, qy - 5), num, font=nf, fill="white")
d.text((MX, 874), "Pins 1–13: the three leads and ten features.",
       font=font("DejaVuSans", 10), fill=GRAY)

# ---- DATE CHECK
BX0, BX1, BY0, BY1 = MX, 360, 890, 992
d.rectangle([BX0, BY0, BX1, BY1], outline=RED, width=2)
d.text((BX0 + 8, BY0 + 4), "DATE CHECK — LEFT OUT AS OLDER NEWS",
       font=font("DejaVuSans-Bold", 11), fill=RED)
df = font("DejaVuSans", 10)
for i, (txt, when) in enumerate(DATA["date_check"]):
    y = BY0 + 18 + i * 11
    item = f"✕ {txt}"
    if tw(d, item, df) > (BX1 - BX0 - 8 - tw(d, when, df) - 8):
        fail(f"date-check line too long: {item}")
    d.text((BX0 + 8, y), item, font=df, fill=INK)
    d.text((BX1 - 8 - tw(d, when, df), y), when, font=df, fill=GRAY)
ny = "Not yet: " + " · ".join(DATA["not_yet"])
ny_lines = wrap(d, ny, df, BX1 - BX0 - 16)
for j, ln in enumerate(ny_lines):
    d.text((BX0 + 8, BY0 + 18 + len(DATA["date_check"]) * 11 + j * 11), ln,
           font=df, fill=RED)

# ---- briefs + legend
BR_X = 376
d.text((BR_X, 790), "ALSO ON THURSDAY 26 NOVEMBER",
       font=font("DejaVuSans-Bold", 12), fill=INK)
bf = font("DejaVuSans", 11)
for i, br in enumerate(DATA["briefs"]):
    line = f'{14 + i}. {br["text"]}'
    if tw(d, line, bf) > (W - MX - BR_X):
        fail(f"brief {14 + i} too long: {line}")
    d.text((BR_X, 808 + i * 22), line, font=bf, fill=INK)
d.text((BR_X, 922), "HOW SURE", font=font("DejaVuSans-Bold", 11), fill=INK)
lf = font("DejaVuSans", 10)
d.text((BR_X, 936), "CONFIRMED = 2+ outlets  ·  OFFICIAL = on record",
       font=lf, fill=GRAY)
d.text((BR_X, 948), "REPORTED = one outlet  ·  CLAIM = one side's word",
       font=lf, fill=GRAY)
d.text((BR_X, 966), DATA["regions_line"], font=font("DejaVuSans-Bold", 11),
       fill=INK)
audit = ("DATES AUDITED — Window 00:00–24:00 UTC; filed early in the day, "
         "before Europe and the Americas woke.")
af = font("DejaVuSans", 10)
if tw(d, audit, af) > (W - MX - BR_X):
    fail("audit line too long")
d.text((BR_X, 980), audit, font=af, fill=GRAY)

# ---------------------------------------------------------------- footer
d.text((MX, 1000), DATA["pledge"], font=font("DejaVuSans", 10), fill=GRAY)
d.text((MX, 1012), DATA["sources"], font=font("DejaVuSans", 10), fill=GRAY)

out = HERE / "entry.png"
img.save(out, optimize=True)
print(f"saved {out} {out.stat().st_size} bytes")
