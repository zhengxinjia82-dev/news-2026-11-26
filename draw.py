#!/usr/bin/env python3
"""News front page, Thursday 26 November 2026. Fresh build, v2.
1024x1024, light paper, serif masthead, 3 headlines + 10 features + 21 briefs.
Deterministic: no time, no randomness, data only from stories.json."""
import json, math, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
    D = json.load(f)

W, H = 1024, 1024
MX = 24
PAPER = (247, 243, 232)
CARD = (255, 253, 246)
INK = (17, 17, 17)
GREY = (85, 85, 85)
RED = (185, 28, 28)
LINE = (201, 194, 174)
DOT = (148, 138, 116)
NAVY = (22, 35, 61)
BADGE = {"CONFIRMED": (21, 128, 61), "REPORTED": (29, 78, 216),
         "CLAIM": (180, 83, 9), "OFFICIAL": (14, 116, 144)}

FD = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    return ImageFont.truetype(FD + name, size)
F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)

def wrap(text, ft, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if ft.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(text, ft, width, max_lines, what):
    lines = wrap(text, ft, width)
    if len(lines) > max_lines:
        raise ValueError(f"{what}: {len(lines)} lines > {max_lines}: {text!r}")
    return lines

def text(d, x, y, s, ft, fill=INK, anchor="la"):
    d.text((x, y), s, font=ft, fill=fill, anchor=anchor)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

ALL = D["headlines"] + D["secondary"] + D["briefs"]
TOTAL = len(ALL)
REGIONS = sorted({s["geo"] for s in ALL})
FIELDS = sorted({s["field"] for s in ALL if "field" in s})
NG, NF = len(REGIONS), len(FIELDS)

# ---------- top bar ----------
kick_r = f"{TOTAL} STORIES \u00b7 {NG} REGIONS \u00b7 {NF} FIELDS \u00b7 ALL FROM THIS THURSDAY"
text(d, MX, 10, "THE WORLD'S NEWS IN ONE DAY", F_SANS_B(13), RED)
text(d, W - MX, 10, kick_r, F_SANS_B(13), RED, anchor="ra")
d.line([(MX, 32), (W - MX, 32)], fill=INK, width=2)

# ---------- masthead ----------
size = 58
while F_SERIF_B(size).getlength(D["date_label"]) > 940 and size > 40:
    size -= 1
text(d, MX, 36, D["date_label"], F_SERIF_B(size), INK)
d.line([(MX, 104), (W - MX, 104)], fill=INK, width=2)
d.line([(MX, 107), (W - MX, 107)], fill=INK, width=1)
text(d, MX, 112, D["subtitle"], F_SERIF(15), GREY)

# ---------- UTC timeline ----------
text(d, MX, 132, D["timeline_label"], F_SANS_B(11), INK)
LX0, LX1, LY = 150, 1000, 168
d.line([(LX0, LY), (LX1, LY)], fill=NAVY, width=3)
text(d, MX, 158, "00:00", F_SANS_B(10), GREY)
text(d, W - MX, 158, "13:30", F_SANS_B(10), GREY, anchor="ra")
SPAN = 13 * 60 + 30  # 00:00-13:30 UTC in minutes
for i, ev in enumerate(D["timeline"]):
    hh, mm = ev["time"].split(":")
    mins = int(hh) * 60 + int(mm)
    x = LX0 + (mins / SPAN) * (LX1 - LX0)
    d.ellipse([x - 5, LY - 5, x + 5, LY + 5], fill=RED, outline="white", width=1)
    lab = f"{ev['time']} {ev['label']}"
    ft = F_SANS(10)
    lw = ft.getlength(lab)
    cx = min(max(x, MX + lw / 2), W - MX - lw / 2)
    if i % 2 == 0:  # above
        text(d, cx, 146, lab, ft, INK, anchor="ma")
        d.line([(x, LY - 5), (x, 158)], fill=GREY, width=1)
    else:  # below
        text(d, cx, 176, lab, ft, INK, anchor="ma")
        d.line([(x, LY + 5), (x, 176)], fill=GREY, width=1)
d.line([(MX, 190), (W - MX, 190)], fill=LINE, width=1)

# ---------- illustration helpers ----------
def banner(d, x, y, w, h, s, size=15):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    ft = F_SANS_B(size)
    while ft.getlength(s) > w - 8 and size > 8:
        size -= 1
        ft = F_SANS_B(size)
    text(d, x + w / 2, y + (h - size) / 2 - 1, s, ft, (255, 255, 255), anchor="ma")

def art_nuke(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(27, 42, 74))
    for sx, sy in [(20, 14), (60, 8), (110, 20), (180, 10), (250, 18), (290, 8), (150, 26)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill="white")
    d.line([(x, y + h - 30), (x + w, y + h - 30)], fill=(60, 80, 110), width=2)
    d.arc([x + 40, y + 10, x + 280, y + h - 10], 200, 340, fill=(255, 200, 80), width=3)
    # rocket at the top of the arc, white body, red flame
    d.polygon([(x + 246, y + 14), (x + 258, y + 14), (x + 264, y + 34), (x + 252, y + 30)], fill=(240, 240, 240), outline=INK)
    d.polygon([(x + 246, y + 14), (x + 252, y + 30), (x + 246, y + 26)], fill=(255, 140, 40))
    d.polygon([(x + 258, y + 14), (x + 252, y + 30), (x + 258, y + 26)], fill=(255, 140, 40))
    # launch tower on the ground
    d.rectangle([x + 56, y + h - 58, x + 92, y + h - 30], fill=(90, 100, 120), outline=INK)
    d.line([(x + 56, y + h - 58), (x + 92, y + h - 58)], fill=(200, 200, 200), width=2)

def art_grain(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(188, 216, 232))
    d.ellipse([x + w - 50, y + 8, x + w - 20, y + 38], fill=(255, 220, 120))
    d.rectangle([x, y + h - 34, x + w, y + h], fill=(46, 111, 142))
    for wy in (h - 26, h - 16):
        d.arc([x + 10, y + wy - 6, x + 70, y + wy + 6], 0, 180, fill="white", width=2)
        d.arc([x + 150, y + wy - 6, x + 210, y + wy + 6], 0, 180, fill="white", width=2)
    d.polygon([(x + 70, y + h - 52), (x + 240, y + h - 52), (x + 225, y + h - 34), (x + 85, y + h - 34)], fill=(40, 40, 40))
    for i, c in enumerate([(185, 28, 28), (30, 90, 160), (220, 160, 40), (40, 120, 70)]):
        d.rectangle([x + 90 + i * 36, y + h - 78, x + 122 + i * 36, y + h - 52], fill=c, outline="white")
    d.rectangle([x + 238, y + h - 72, x + 252, y + h - 52], fill=(240, 240, 240))

def art_tariff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 220, 192))
    for cx, cy, c in [(40, 30, (170, 120, 60)), (100, 30, (120, 90, 50)),
                      (70, 60, (150, 100, 55)), (220, 26, (185, 28, 28))]:
        d.rectangle([x + cx, y + cy, x + cx + 52, y + cy + 26], fill=c, outline=INK)
    text(d, x + 246, y + 22, "%", F_SERIF_B(34), RED, anchor="ma")
    d.line([(x + 20, y + h - 32), (x + w - 20, y + h - 32)], fill=INK, width=2)
    d.polygon([(x + w - 40, y + h - 40), (x + w - 20, y + h - 32), (x + w - 40, y + h - 24)], fill=RED)

def art_chart(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(253, 246, 227))
    base = y + h - (30 if not small else 13)
    d.line([(x + 8, base), (x + w - 8, base)], fill=INK, width=2)
    bars = [(15, 9), (45, 7), (75, 12), (105, 5)] if small else [(30, 55), (80, 40), (130, 55), (180, 28), (230, 18)]
    cols = [(21, 128, 61), (185, 28, 28), (21, 128, 61), (185, 28, 28), (21, 128, 61)]
    bw = 12 if small else 30
    for i, (bx, bh) in enumerate(bars):
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=cols[i % len(cols)])
    if not small:
        pts = [(x + 30, base - 55), (x + 80, base - 40), (x + 130, base - 55), (x + 180, base - 28), (x + 230, base - 18)]
        d.line(pts, fill=RED, width=3)

def art_scales(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(236, 229, 211))
    cx = x + w // 2
    if small:
        d.line([(cx, y + 1), (cx, y + 17)], fill=INK, width=2)
        d.line([(cx - 30, y + 5), (cx + 30, y + 5)], fill=INK, width=2)
        for sgn in (-1, 1):
            px = cx + sgn * 30
            d.line([(px, y + 5), (px, y + 9)], fill=INK, width=1)
            d.polygon([(px - 9, y + 9), (px + 9, y + 9), (px, y + 16)], fill=(185, 28, 28), outline=INK)
        d.line([(cx - 14, y + 17), (cx + 14, y + 17)], fill=INK, width=2)
        return
    top = y + 6
    bot = y + h - 16
    d.line([(cx, top), (cx, bot)], fill=INK, width=3)
    d.line([(cx - 8, top), (cx + 8, top)], fill=INK, width=3)
    d.line([(cx - 46, top + 6), (cx + 46, top + 6)], fill=INK, width=3)
    for sgn in (-1, 1):
        px = cx + sgn * 46
        d.line([(px, top + 6), (px, top + 16)], fill=INK, width=2)
        d.polygon([(px - 14, top + 16), (px + 14, top + 16), (px, bot)], fill=(185, 28, 28), outline=INK)
    d.line([(cx - 22, bot), (cx + 22, bot)], fill=INK, width=3)

def art_chip(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(31, 41, 55))
    cx, cy = x + w // 2, y + (h - 14) // 2
    s = 12 if small else 34
    d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=(60, 130, 200), outline=(255, 255, 255), width=2)
    d.rectangle([cx - s // 4, cy - s // 4, cx + s // 4, cy + s // 4], fill=(255, 255, 255))
    for k in range(3):
        d.line([(cx - s // 2 - 8, cy - s // 4 + k * s // 4), (cx - s // 2, cy - s // 4 + k * s // 4)], fill=(255, 255, 255), width=2)
        d.line([(cx + s // 2, cy - s // 4 + k * s // 4), (cx + s // 2 + 8, cy - s // 4 + k * s // 4)], fill=(255, 255, 255), width=2)

def art_virus(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(243, 232, 232))
    cx, cy = x + w // 2, y + (h - 14) // 2
    if small:
        cy = y + 9
    r = 5 if small else 20
    spike = 4 if small else 6
    for a in range(0, 360, 30):
        ex = cx + (r + spike) * math.cos(math.radians(a))
        ey = cy + (r + spike) * math.sin(math.radians(a))
        d.line([(cx, cy), (ex, ey)], fill=(185, 28, 28), width=2)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(185, 28, 28))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(185, 28, 28), outline=(120, 10, 10), width=2)
    d.ellipse([cx - r // 2, cy - r // 2, cx - r // 4, cy - r // 4], fill=(255, 255, 255))

def art_treaty(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(230, 236, 245))
    if small:
        d.rectangle([x + 20, y + 2, x + 60, y + 13], fill=(0, 40, 120))
        d.rectangle([x + 20, y + 2, x + 60, y + 13], outline="white")
        d.ellipse([x + 30, y + 5, x + 34, y + 9], fill="white")
        d.ellipse([x + 44, y + 6, x + 48, y + 10], fill="white")
        d.rectangle([x + 90, y + 2, x + 130, y + 13], fill=(0, 120, 80))
        d.rectangle([x + 90, y + 2, x + 130, y + 13], outline="white")
        d.ellipse([x + 100, y + 5, x + 104, y + 9], fill=(255, 220, 0))
        d.ellipse([x + 114, y + 6, x + 118, y + 10], fill=(255, 220, 0))
        d.line([(x + 20, y + 2), (x + 20, y + 17)], fill=INK, width=1)
        d.line([(x + 130, y + 2), (x + 130, y + 17)], fill=INK, width=1)
    else:
        d.rectangle([x + 30, y + 12, x + 130, y + 62], fill=(0, 40, 120), outline=INK)
        d.polygon([(x + 30, y + 12), (x + 80, y + 12), (x + 80, y + 37), (x + 30, y + 37)], fill=(0, 20, 80))
        for sx, sy in [(110, 25), (120, 45), (95, 50), (115, 55)]:
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill="white")
        d.rectangle([x + 180, y + 12, x + 280, y + 62], fill=(0, 120, 80), outline=INK)
        d.polygon([(x + 180, y + 12), (x + 280, y + 12), (x + 180, y + 62)], fill=(0, 60, 160))
        for sx, sy in [(200, 22), (215, 30), (230, 20), (245, 32), (260, 24)]:
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2], fill=(255, 220, 0))
        d.line([(x + 30, y + 12), (x + 30, y + 78)], fill=INK, width=2)
        d.line([(x + 280, y + 12), (x + 280, y + 78)], fill=INK, width=2)

def art_candles(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(253, 246, 227))
    mid = y + (h - 14) // 2
    data = [(18, -4, 4, 1), (48, 3, -3, 1), (78, -5, 5, 1)] if small else \
           [(30, -14, 10, 1), (80, 8, -8, -1), (130, -10, 8, 1), (180, 12, -10, -1), (230, -6, 6, 1)]
    bw = 8 if small else 18
    for cx, o, c, _ in data:
        col = (21, 128, 61) if c > 0 else (185, 28, 28)
        wick = 4 if small else 8
        d.line([(x + cx + bw // 2, mid + o - wick), (x + cx + bw // 2, mid + o + wick)], fill=INK, width=1)
        d.rectangle([x + cx, mid + o - abs(c), x + cx + bw, mid + o + abs(c)], fill=col, outline=INK)

def art_hoop(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(245, 230, 208))
    cx, cy = x + w // 2, y + (h - 14) // 2
    r = 8 if small else 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 120, 40), outline=INK, width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=INK, width=1)
    d.line([(cx, cy - r), (cx, cy + r)], fill=INK, width=1)
    d.arc([cx - r, cy - r, cx + r, cy + r], 300, 60, fill=INK, width=1)
    if not small:
        d.line([(x + w - 70, y + 12), (x + w - 20, y + 12)], fill=(185, 28, 28), width=4)
        for k in range(3):
            d.line([(x + w - 66 + k * 16, y + 12), (x + w - 58 + k * 16, y + 30)], fill=INK, width=1)

def art_flags(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(238, 242, 247))
    if small:
        d.rectangle([x + 25, y + 2, x + 70, y + 13], fill=(200, 20, 20))
        d.rectangle([x + 25, y + 2, x + 45, y + 8], fill=(0, 40, 120))
        d.rectangle([x + 100, y + 2, x + 145, y + 13], fill=(220, 30, 30))
        d.ellipse([x + 118, y + 5, x + 126, y + 11], fill=(255, 220, 0))
        d.line([(x + 25, y + 2), (x + 25, y + 17)], fill=INK, width=1)
        d.line([(x + 145, y + 2), (x + 145, y + 17)], fill=INK, width=1)
    else:
        d.rectangle([x + 40, y + 12, x + 140, y + 62], fill=(200, 20, 20), outline=INK)
        d.rectangle([x + 40, y + 12, x + 90, y + 37], fill=(0, 40, 120))
        d.ellipse([x + 58, y + 18, x + 72, y + 31], fill="white")
        d.rectangle([x + 170, y + 12, x + 270, y + 62], fill=(220, 30, 30), outline=INK)
        d.polygon([(x + 220, y + 20), (x + 223, y + 30), (x + 234, y + 30), (x + 225, y + 37),
                   (x + 228, y + 48), (x + 220, y + 41), (x + 212, y + 48), (x + 215, y + 37),
                   (x + 206, y + 30), (x + 217, y + 30)], fill=(255, 220, 0))
        d.line([(x + 40, y + 12), (x + 40, y + 78)], fill=INK, width=2)
        d.line([(x + 270, y + 12), (x + 270, y + 78)], fill=INK, width=2)

def art_bolt(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(254, 243, 199))
    cx = x + w // 2
    if small:
        d.polygon([(cx + 4, y + 1), (cx - 5, y + 9), (cx - 1, y + 9), (cx - 4, y + 17), (cx + 5, y + 8), (cx + 1, y + 8)], fill=(230, 170, 0), outline=INK)
    else:
        d.polygon([(cx + 12, y + 6), (cx - 18, y + 42), (cx - 2, y + 42), (cx - 12, y + 76), (cx + 18, y + 34), (cx + 2, y + 34)], fill=(230, 170, 0), outline=INK)
        d.rectangle([x + w - 90, y + 14, x + w - 30, y + 40], fill=(185, 28, 28))
        text(d, x + w - 60, y + 18, "£", F_SANS_B(18), (255, 255, 255), anchor="ma")

def art_plane(d, x, y, w, h, small=False):
    d.rectangle([x, y, x + w, y + h], fill=(219, 234, 254))
    for cx, cy, r in [(30, 8, 8), (90, 4, 6), (160, 10, 7), (250, 6, 8)]:
        d.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r], fill="white")
    cx, cy = x + w // 2, y + (h - 14) // 2
    if small:
        cy = y + 9
    d.ellipse([cx - 34, cy - 6, cx + 34, cy + 6], fill=(40, 60, 90))
    d.polygon([(cx - 6, cy - 6), (cx + 10, cy - (16 if not small else 10)), (cx + 16, cy - 6)], fill=(40, 60, 90))
    d.polygon([(cx - 30, cy + 4), (cx - 18, cy + (14 if not small else 8)), (cx - 10, cy + 4)], fill=(40, 60, 90))
    d.polygon([(cx + 30, cy - 2), (cx + 44, cy), (cx + 30, cy + 2)], fill=(185, 28, 28))
    d.line([(x + 12, cy + 12), (cx - 40, cy + 12)], fill=GREY, width=1)

BIG_ART = {"nuke": art_nuke, "grain": art_grain, "tariff": art_tariff,
           "chart": art_chart, "scales": art_scales, "chip": art_chip,
           "virus": art_virus, "treaty": art_treaty, "candles": art_candles,
           "hoop": art_hoop, "flags": art_flags, "bolt": art_bolt, "plane": art_plane}

def draw_art(d, key, x, y, w, h, small=False):
    fn = BIG_ART[key]
    if key in ("chart", "scales", "chip", "virus", "treaty", "candles", "hoop", "flags", "bolt", "plane"):
        fn(d, x, y, w, h, small)
    else:
        fn(d, x, y, w, h)

# ---------- 3 headlines ----------
HX, HY, HW, HGAP = MX, 196, 312, 20
for i, s in enumerate(D["headlines"]):
    x = HX + i * (HW + HGAP)
    d.rectangle([x, HY, x + HW, HY + 108], outline=LINE, width=1)
    draw_art(d, s["art"], x, HY, HW, 108)
    banner(d, x, HY + 108 - 26, HW, 26, s["banner"], 15)
    cy = HY + 118
    d.ellipse([x, cy, x + 18, cy + 18], fill=RED)
    text(d, x + 9, cy + 2, str(s["n"]), F_SANS_B(11), (255, 255, 255), anchor="ma")
    text(d, x + 24, cy + 2, f"{s['region']} \u00b7 {s['field']}", F_SANS_B(11), RED)
    ty = HY + 144
    tlines = fit_lines(s["title"], F_SERIF_B(21), HW, 3, f"headline {s['n']} title")
    for ln in tlines:
        text(d, x, ty, ln, F_SERIF_B(21), INK)
        ty += 25
    by = ty + 4
    blines = fit_lines(s["body"], F_SANS(12), HW, 2, f"headline {s['n']} body")
    for ln in blines:
        text(d, x, by, ln, F_SANS(12), GREY)
        by += 16
    badge_y = HY + 244
    text(d, x, badge_y, s["badge"], F_SANS_B(10), BADGE[s["badge"]])
    text(d, x + F_SANS_B(10).getlength(s["badge"]) + 6, badge_y,
         f"\u00b7 {s['source']} \u00b7 {s['place']}", F_SANS(10), GREY)

# ---------- numbers bar ----------
NY = 458
text(d, MX, NY, "THE DAY IN NUMBERS", F_SANS_B(12), INK)
cols = 6
cw = (W - 2 * MX) // cols
for i, nb in enumerate(D["numbers"]):
    cx = MX + i * cw
    text(d, cx, NY + 16, nb["num"], F_SERIF_B(24), RED)
    text(d, cx, NY + 44, nb["cap"], F_SANS(10), GREY)
d.line([(MX, 508), (W - MX, 508)], fill=LINE, width=1)

# ---------- 10 features ----------
FX, FY, FW, FH, FGAP, FRGAP = MX, 516, 187, 100, 10, 8
for i, s in enumerate(D["secondary"]):
    row, col = divmod(i, 5)
    x = FX + col * (FW + FGAP)
    y = FY + row * (FH + FRGAP)
    d.rectangle([x, y, x + FW, y + 30], outline=LINE, width=1)
    draw_art(d, s["art"], x, y, FW, 30, small=True)
    banner(d, x, y + 30 - 12, FW, 12, s["banner"], 10)
    text(d, x, y + 34, f"{s['n']}", F_SANS_B(10), RED)
    text(d, x + 16, y + 34, s["region"], F_SANS_B(9), RED)
    ty = y + 46
    tlines = fit_lines(s["title"], F_SANS_B(12), FW, 2, f"secondary {s['n']} title")
    for ln in tlines:
        text(d, x, ty, ln, F_SANS_B(12), INK)
        ty += 13
    body = fit_lines(s["body"], F_SANS(11), FW, 1, f"secondary {s['n']} body")
    text(d, x, y + 73, body[0], F_SANS(11), GREY)
    text(d, x, y + 87, s["badge"], F_SANS_B(9), BADGE[s["badge"]])
    text(d, x + F_SANS_B(9).getlength(s["badge"]) + 5, y + 87,
         f"\u00b7 {s['source']}", F_SANS(9), GREY)
d.line([(MX, 728), (W - MX, 728)], fill=LINE, width=1)

# ---------- world map ----------
NA = [(-168, 66), (-155, 71), (-140, 70), (-128, 71), (-115, 73), (-105, 72), (-95, 80),
      (-88, 82), (-80, 76), (-76, 73), (-70, 68), (-65, 62), (-60, 55), (-55, 52),
      (-60, 47), (-66, 45), (-70, 42), (-74, 39), (-76, 35), (-80, 32), (-81, 26),
      (-84, 30), (-88, 29), (-91, 19), (-95, 17), (-100, 16), (-105, 20), (-110, 23),
      (-114, 28), (-118, 33), (-122, 38), (-124, 44), (-125, 49), (-130, 55), (-140, 60),
      (-152, 58), (-162, 55), (-166, 60)]
SA = [(-79, 9), (-77, 4), (-75, 0), (-72, -4), (-70, -10), (-70, -18), (-70, -23),
      (-70, -30), (-72, -37), (-73, -44), (-70, -52), (-66, -55), (-68, -50), (-65, -45),
      (-62, -41), (-58, -34), (-52, -32), (-48, -28), (-41, -23), (-39, -17), (-35, -9),
      (-35, -6), (-40, -3), (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
      (-72, 12), (-76, 10)]
AF = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 12), (-12, 8), (-8, 5),
      (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0), (12, -3), (12, -10), (13, -16),
      (12, -22), (14, -28), (17, -32), (19, -34), (25, -34), (28, -32), (32, -28),
      (35, -24), (36, -20), (40, -15), (40, -10), (42, -5), (46, -1), (51, 2),
      (51, 11), (48, 11), (44, 13), (41, 18), (39, 22), (37, 27), (35, 28), (33, 31),
      (30, 32), (25, 32), (20, 32), (15, 32), (11, 34), (10, 37), (5, 37), (0, 36), (-2, 35)]
EA = [(-10, 36), (-9, 38), (-9, 43), (-5, 44), (-2, 44), (0, 44), (3, 43), (7, 44),
      (10, 44), (12, 44), (14, 45), (18, 40), (19, 42), (22, 40), (23, 36), (26, 36),
      (28, 37), (30, 36), (33, 36), (36, 36), (36, 39), (33, 41), (30, 41), (28, 41),
      (27, 41), (28, 44), (29, 45), (31, 47), (33, 46), (35, 47), (38, 47), (40, 47),
      (42, 46), (44, 47), (46, 46), (48, 46), (50, 46), (52, 48), (54, 50), (56, 52),
      (58, 54), (60, 55), (62, 58), (64, 60), (66, 64), (68, 68), (70, 71), (72, 72),
      (75, 73), (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 77),
      (110, 76), (115, 74), (120, 73), (125, 72), (130, 71), (135, 71), (140, 72),
      (145, 72), (150, 70), (155, 69), (160, 69), (165, 67), (170, 67), (175, 65),
      (178, 65), (178, 62), (175, 60), (170, 60), (165, 60), (162, 58), (160, 55),
      (158, 52), (156, 51), (152, 50), (150, 47), (147, 45), (143, 43), (141, 40),
      (140, 38), (138, 35), (136, 34), (134, 34), (132, 33), (130, 33), (129, 35),
      (127, 36), (126, 38), (124, 40), (122, 39), (120, 38), (120, 34), (120, 30),
      (118, 26), (116, 23), (114, 22), (110, 20), (108, 18), (108, 12), (106, 10),
      (105, 9), (103, 7), (101, 6), (100, 8), (98, 10), (97, 15), (95, 16), (94, 18),
      (92, 21), (91, 22), (89, 22), (88, 22), (86, 20), (84, 19), (82, 17), (80, 15),
      (80, 13), (79, 10), (77, 8), (76, 10), (74, 15), (73, 19), (72, 20), (70, 21),
      (68, 23), (66, 25), (64, 25), (62, 25), (60, 25), (58, 26), (56, 27), (54, 27),
      (52, 28), (50, 29), (49, 30), (48, 30), (46, 29), (44, 29), (42, 28), (40, 28),
      (39, 27), (38, 25), (37, 22), (36, 20), (35, 18), (34, 16), (33, 15), (32, 15),
      (30, 14), (28, 14), (26, 14), (24, 14), (22, 13), (20, 13), (18, 13), (16, 14),
      (15, 15), (14, 16), (13, 17), (12, 18), (11, 20), (10, 22), (9, 24), (8, 26),
      (7, 28), (6, 30), (5, 32), (4, 34), (3, 35), (2, 36), (0, 36), (-2, 35),
      (-4, 35), (-6, 34), (-8, 34), (-10, 34)]
AU = [(113, -22), (114, -25), (114, -30), (115, -33), (116, -35), (119, -34), (122, -34),
      (124, -33), (127, -32), (129, -32), (131, -32), (132, -32), (134, -33), (136, -35),
      (137, -35), (139, -37), (140, -38), (142, -38), (144, -38), (146, -39), (148, -38),
      (150, -37), (151, -36), (153, -32), (153, -27), (152, -24), (150, -22), (148, -20),
      (146, -19), (144, -15), (142, -11), (141, -13), (140, -17), (139, -17), (137, -16),
      (136, -15), (135, -12), (134, -12), (132, -12), (130, -13), (128, -14), (126, -14),
      (124, -15), (122, -17), (120, -20), (118, -20), (116, -21), (114, -22)]
ISLANDS = [(-1, 53, 2, 3), (139, 37, 2.5, 4), (118, -2, 5, 2), (172, -41, 2, 3),
           (47, -19, 1.5, 3), (81, 7.5, 1, 1.5), (121, 23.5, 1, 1.5),
           (122, 12, 2, 3), (114, 0, 3, 2.5), (102, 0, 2, 3), (141, -5, 4, 2),
           (-18, 65, 2, 1.5), (-79, 21, 2.5, 1)]
POLYS = [NA, SA, AF, EA, AU]

def in_poly(lon, lat, poly):
    inside, n = False, len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def is_land(lon, lat):
    for p in POLYS:
        if in_poly(lon, lat, p):
            return True
    for cx, cy, rx, ry in ISLANDS:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1:
            return True
    return False

MAPX, MAPY, MAPW, MAPH = MX, 756, 292, 100
text(d, MX, 736, "WHERE IT HAPPENED — 13 PINS", F_SANS_B(12), INK)
COLS, ROWS = 64, 25
for r in range(ROWS):
    for c in range(COLS):
        lon = -170 + (c + 0.5) * 360 / COLS
        lat = 85 - (r + 0.5) * 145 / ROWS
        if is_land(lon, lat):
            px = MAPX + (c + 0.5) * MAPW / COLS
            py = MAPY + (r + 0.5) * MAPH / ROWS
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=DOT)

def pin_xy(lat, lon):
    return (MAPX + (lon + 170) / 360 * MAPW, MAPY + (85 - lat) / 145 * MAPH)

OFFSETS = {1: (-16, -10), 2: (-12, -8), 3: (-20, 10), 4: (12, 8),
           6: (0, -14), 10: (16, 10), 13: (12, -8)}
for s in D["headlines"] + D["secondary"]:
    px, py = pin_xy(s["lat"], s["lon"])
    dx, dy = OFFSETS.get(s["n"], (0, 0))
    qx, qy = px + dx, py + dy
    d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    if (dx, dy) != (0, 0):
        d.line([(px, py), (qx, qy)], fill=RED, width=1)
    d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline="white", width=1)
    text(d, qx, qy - 5, str(s["n"]), F_SANS_B(8), (255, 255, 255), anchor="ma")
text(d, MX, 864, "1–3 headlines \u00b7 4–13 features", F_SANS(10), GREY)

# ---------- DATE CHECK ----------
DCX, DCY, DCW, DCH = MX, 880, 292, 112
d.rectangle([DCX, DCY, DCX + DCW, DCY + DCH], outline=RED, width=2)
text(d, DCX + 8, DCY + 6, "DATE CHECK — LEFT OUT AS OLDER NEWS", F_SANS_B(11), RED)
yy = DCY + 24
for item, when in D["date_check"]:
    line = f"\u2715 {item}"
    if F_SANS(10).getlength(line) + F_SANS_B(10).getlength(when) + 16 > DCW:
        raise ValueError(f"date check too long: {line}")
    text(d, DCX + 8, yy, line, F_SANS(10), INK)
    text(d, DCX + DCW - 8, yy, when, F_SANS_B(10), RED, anchor="ra")
    yy += 12
text(d, DCX + 8, yy + 2, D["not_yet"], F_SANS_B(10), RED)

# ---------- briefs ----------
BX, BY = 332, 736
text(d, BX, BY, "ALSO ON THURSDAY 26 NOVEMBER", F_SANS_B(12), INK)
BW, BGAP = 330, 8
for i, b in enumerate(D["briefs"]):
    col, row = divmod(i, 11)
    x = BX + col * (BW + BGAP)
    y = BY + 22 + row * 15
    s = f"{b['n']}. {b['text']}"
    if len(s) > 55:
        raise ValueError(f"brief too long ({len(s)}): {s}")
    if F_SANS(11).getlength(s) > BW:
        raise ValueError(f"brief too wide: {s}")
    text(d, x, y, s, F_SANS(11), INK)

# ---------- HOW SURE + regions ----------
HY2 = BY + 22 + 11 * 15 + 8
text(d, BX, HY2, "HOW SURE:", F_SANS_B(10), INK)
text(d, BX + 68, HY2, "CONFIRMED = 2+ outlets \u00b7 OFFICIAL = on record", F_SANS(10), INK)
text(d, BX + 68, HY2 + 13, "REPORTED = one outlet \u00b7 CLAIM = one side's word", F_SANS(10), INK)
counts = {}
for s in ALL:
    counts[s["geo"]] = counts.get(s["geo"], 0) + 1
ORDER = ["E. Asia", "S. Asia", "SE Asia", "Middle East", "Europe",
         "Africa", "N. America", "S. America", "Oceania"]
reg_line = " \u00b7 ".join(f"{g.upper()} {counts[g]}" for g in ORDER if g in counts)
text(d, BX, HY2 + 28, reg_line, F_SANS_B(10), GREY)

# ---------- footer ----------
d.line([(MX, 994), (W - MX, 994)], fill=LINE, width=1)
text(d, MX, 1000, D["pledge"], F_SANS(10), GREY)
text(d, MX, 1012, D["sources"], F_SANS(10), GREY)

img.save(os.path.join(HERE, "entry.png"))
print(f"saved entry.png  {TOTAL} stories, {NG} regions, {NF} fields")
