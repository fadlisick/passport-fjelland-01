#!/usr/bin/env python3
"""Draw the Republic of Fjelland passport spread (1024x720 PNG).

Pure Pillow drawing, no network, no external images. Deterministic:
fixed seed, no timestamps. Rendered at 2x and downscaled for smooth edges.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 2048, 1440          # 2x working size; final 1024x720
PAPER = (244, 238, 225)
PAPER_DARK = (232, 224, 203)
INK = (34, 38, 31)
PINE = (30, 70, 54)
PINE_DK = (22, 52, 40)
GOLD = (168, 132, 44)
GREY = (107, 106, 94)
BLUE = (43, 76, 126)
GREEN = (46, 94, 78)
RED = (142, 59, 52)
PURPLE = (110, 59, 110)
SKIN = (233, 196, 156)
SKIN_SH = (214, 172, 128)
HAIR = (70, 48, 31)
HAIR_LT = (96, 68, 44)
JACKET = (158, 74, 47)
CREAM = (248, 244, 232)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def spaced(d, x, y, text, font, fill, tracking=0):
    """Draw text with extra tracking between characters."""
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill)
        cx += d.textlength(ch, font=font) + tracking
    return cx


def text_w(d, text, font, tracking=0):
    w = d.textlength(text, font=font)
    return w + tracking * max(0, len(text) - 1)


def centre(d, cx, y, text, font, fill, tracking=0):
    spaced(d, cx - text_w(d, text, font, tracking) / 2, y, text, font, fill, tracking)


def wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- ICAO MRZ
def _mrz_val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord("A") + 10


def check_digit(s):
    total = 0
    for i, ch in enumerate(s):
        total += _mrz_val(ch) * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_lines():
    line1 = "P<FJLHAUG<<ELIN<SOFIE"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "FJ482917"
    doc_cd = check_digit(doc)
    dob = "900614"
    dob_cd = check_digit(dob)
    sex = "F"
    exp = "340311"
    exp_cd = check_digit(exp)
    body = doc + doc_cd + "FJL" + dob + dob_cd + sex + exp + exp_cd
    personal = "<" * (44 - len(body) - 1)
    line2 = body + personal
    line2 += check_digit(line2[:43])
    return line1, line2


# ---------------------------------------------------------------- guilloche
def guilloche(base):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for cx, cy in ((420, 1560), (1750, -260), (1024, 720)):
        r = 60
        while r < 1500:
            d.ellipse((cx - r, cy - r, cx + r, cy + r),
                      outline=(30, 70, 54, 9), width=2)
            r += 34
    # fine horizontal security lines removed: they read as ruled paper
    out = Image.alpha_composite(base.convert("RGBA"), ov)
    rnd = random.Random(20261121)
    d2 = ImageDraw.Draw(out)
    for _ in range(2600):
        x = rnd.randrange(W)
        y = rnd.randrange(H)
        d2.point((x, y), fill=(90, 80, 60, 14))
    return out


# ---------------------------------------------------------------- portrait
def draw_portrait(d, x0, y0, w, h):
    """Flat vector portrait of Elin Sofie Haug, mountain rescue guide."""
    # background panel: pale sky, sun, ridge lines
    d.rectangle((x0, y0, x0 + w, y0 + h), fill=(216, 224, 220))
    d.ellipse((x0 + w - 78, y0 + 26, x0 + w - 18, y0 + 86), fill=(238, 226, 190))
    ridge = [(x0, y0 + h * 0.42), (x0 + w * 0.28, y0 + h * 0.30),
             (x0 + w * 0.52, y0 + h * 0.44), (x0 + w * 0.74, y0 + h * 0.32),
             (x0 + w, y0 + h * 0.46), (x0 + w, y0 + h * 0.42),
             (x0, y0 + h * 0.42)]
    d.polygon(ridge, fill=(188, 200, 194))
    d.line([(x0, y0 + h * 0.42), (x0 + w * 0.28, y0 + h * 0.30),
            (x0 + w * 0.52, y0 + h * 0.44), (x0 + w * 0.74, y0 + h * 0.32),
            (x0 + w, y0 + h * 0.46)], fill=(150, 166, 158), width=3)

    cx = x0 + w // 2
    # back hair mass
    d.ellipse((cx - 78, y0 + 62, cx + 78, y0 + 300), fill=HAIR)
    # shoulders / rescue jacket
    d.polygon([(cx - 132, y0 + h), (cx - 118, y0 + 268),
               (cx - 62, y0 + 238), (cx + 62, y0 + 238),
               (cx + 118, y0 + 268), (cx + 132, y0 + h)], fill=JACKET)
    # jacket collar + zip
    d.polygon([(cx - 62, y0 + 238), (cx, y0 + 262), (cx + 62, y0 + 238),
               (cx + 46, y0 + 222), (cx - 46, y0 + 222)], fill=CREAM)
    d.line((cx, y0 + 262, cx, y0 + h), fill=(90, 40, 28), width=4)
    d.line((cx - 96, y0 + 300, cx - 128, y0 + h), fill=(120, 52, 36), width=3)
    d.line((cx + 96, y0 + 300, cx + 128, y0 + h), fill=(120, 52, 36), width=3)
    # small pine badge on the jacket
    d.ellipse((cx + 62, y0 + 292, cx + 96, y0 + 326), fill=PINE)
    d.polygon([(cx + 79, y0 + 296), (cx + 73, y0 + 312), (cx + 85, y0 + 312)],
              fill=GOLD)
    # neck
    d.rectangle((cx - 20, y0 + 196, cx + 20, y0 + 252), fill=SKIN)
    d.rectangle((cx - 20, y0 + 196, cx + 20, y0 + 214), fill=SKIN_SH)
    # ears
    d.ellipse((cx - 76, y0 + 128, cx - 58, y0 + 162), fill=SKIN)
    d.ellipse((cx + 58, y0 + 128, cx + 76, y0 + 162), fill=SKIN)
    # head
    d.ellipse((cx - 62, y0 + 66, cx + 62, y0 + 222), fill=SKIN)
    # cheek shading
    d.ellipse((cx - 56, y0 + 158, cx - 22, y0 + 184), fill=(228, 178, 140))
    d.ellipse((cx + 22, y0 + 158, cx + 56, y0 + 184), fill=(228, 178, 140))
    # hair cap + centre part
    d.pieslice((cx - 66, y0 + 52, cx + 66, y0 + 170), 180, 360, fill=HAIR)
    d.polygon([(cx - 66, y0 + 120), (cx - 58, y0 + 66), (cx - 30, y0 + 58),
               (cx - 44, y0 + 118)], fill=HAIR)
    d.polygon([(cx + 66, y0 + 120), (cx + 58, y0 + 66), (cx + 30, y0 + 58),
               (cx + 44, y0 + 118)], fill=HAIR)
    # braids over the shoulders
    for sgn in (-1, 1):
        bx = cx + sgn * 84
        d.rounded_rectangle((bx - 15, y0 + 150, bx + 15, y0 + 330),
                            radius=15, fill=HAIR)
        for i, yy in enumerate(range(y0 + 168, y0 + 320, 26)):
            d.line((bx - 12, yy, bx + 12, yy + 12), fill=HAIR_LT, width=4)
        d.rectangle((bx - 16, y0 + 322, bx + 16, y0 + 336), fill=PINE)
    # brows
    d.arc((cx - 44, y0 + 124, cx - 12, y0 + 142), 200, 340, fill=HAIR, width=4)
    d.arc((cx + 12, y0 + 124, cx + 44, y0 + 142), 200, 340, fill=HAIR, width=4)
    # eyes: grey-green, looking at the viewer
    for sgn in (-1, 1):
        ex = cx + sgn * 28
        d.ellipse((ex - 12, y0 + 142, ex + 12, y0 + 156), fill=(248, 246, 240))
        d.ellipse((ex - 5, y0 + 143, ex + 5, y0 + 155), fill=(107, 127, 110))
        d.ellipse((ex - 3, y0 + 145, ex + 3, y0 + 153), fill=(30, 30, 28))
        d.arc((ex - 13, y0 + 140, ex + 13, y0 + 156), 180, 360, fill=HAIR, width=3)
    # nose
    d.line((cx + 1, y0 + 152, cx - 2, y0 + 182), fill=SKIN_SH, width=3)
    d.arc((cx - 7, y0 + 178, cx + 8, y0 + 190), 0, 180, fill=SKIN_SH, width=3)
    # lips, muted rose
    d.polygon([(cx - 14, y0 + 198), (cx, y0 + 194), (cx + 14, y0 + 198),
               (cx, y0 + 204)], fill=(176, 112, 95))
    d.arc((cx - 14, y0 + 198, cx + 14, y0 + 208), 0, 180, fill=(140, 84, 70),
          width=2)
    # frame
    d.rectangle((x0, y0, x0 + w, y0 + h), outline=PINE_DK, width=4)
    d.rectangle((x0 + 8, y0 + 8, x0 + w - 8, y0 + h - 8), outline=(30, 70, 54),
                width=1)


# ---------------------------------------------------------------- stamps
def stamp_rect(d, x, y, w, h, colour, lines, angle=0):
    """A rectangular border stamp; lines = [(text, font, bold?)]."""
    layer = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ox, oy = 40, 40
    ld.rounded_rectangle((ox, oy, ox + w, oy + h), radius=14,
                         outline=colour + (235,), width=5)
    ld.rounded_rectangle((ox + 10, oy + 10, ox + w - 10, oy + h - 10),
                         radius=10, outline=colour + (235,), width=2)
    cy = oy + 18
    for text, font, big in lines:
        f = F(SANS_B if big else SANS, font)
        centre(ld, ox + w // 2, cy, text, f, colour + (235,))
        cy += font + 12
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    return layer, (x - 40, y - 40)


def ring_text(img, cx, cy, r, text, size, colour, alpha=225):
    """Draw text along the top arc, each glyph rotated tangentially."""
    import math as _m
    step = _m.degrees(0.62 * size / r) * 1.15
    start = -90 - step * (len(text) - 1) / 2
    for i, ch in enumerate(text):
        ang = _m.radians(start + i * step)
        tile = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        f = F(SANS_B, size)
        td.text((24 - td.textlength(ch, font=f) / 2, 24 - size / 2), ch,
                font=f, fill=colour + (alpha,))
        tile = tile.rotate(-(start + i * step) - 90, resample=Image.BICUBIC,
                           expand=False)
        px = cx + int(r * _m.cos(ang)) - 24
        py = cy + int(r * _m.sin(ang)) - 24
        img.alpha_composite(tile, (px, py))


def round_seal(d, cx, cy, r, colour, ring_text_s, centre_lines, alpha=225):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=colour + (alpha,),
              width=6)
    d.ellipse((cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16),
              outline=colour + (alpha,), width=2)
    yy = cy - 34
    for text, size in centre_lines:
        f = F(SERIF_B if size > 30 else SANS_B, size)
        centre(d, cx, yy, text, f, colour + (alpha,))
        yy += size + 10


def shield(d, x, y, s):
    """Coat of arms: shield, three peaks, pine, star, waves."""
    pts = [(x, y), (x + s, y), (x + s, y + s * 0.62),
           (x + s * 0.5, y + s), (x, y + s * 0.62)]
    d.polygon(pts, fill=PINE, outline=GOLD, width=4)
    d.polygon([(x + s * 0.14, y + s * 0.58), (x + s * 0.38, y + s * 0.26),
               (x + s * 0.5, y + s * 0.44), (x + s * 0.64, y + s * 0.22),
               (x + s * 0.86, y + s * 0.58)], fill=CREAM)
    # star above the peaks
    sx, sy, r = x + s * 0.5, y + s * 0.16, s * 0.07
    star = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(star, fill=GOLD)
    for i, yy in enumerate((y + s * 0.68, y + s * 0.76, y + s * 0.84)):
        d.arc((x + s * 0.2, yy - 14, x + s * 0.8, yy + 14), 0, 180,
              fill=CREAM, width=3)


def field(d, x, y, w, label, value, vfont=None, vsize=30):
    d.text((x, y), label, font=F(SANS, 17), fill=GREY)
    d.text((x, y + 22), value, font=vfont or F(SERIF_B, vsize), fill=INK)
    d.line((x, y + 60, x + w, y + 60), fill=(190, 182, 160), width=2)
    return y + 74


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # page tint + spine
    d.rectangle((24, 24, 1000, H - 24), fill=(247, 242, 231))
    d.rectangle((1048, 24, 2024, H - 24), fill=(247, 242, 231))
    d.rectangle((1000, 24, 1048, H - 24), fill=(214, 204, 184))
    d.line((1024, 24, 1024, H - 24), fill=(170, 158, 134), width=3)
    d.rectangle((24, 24, 2024, H - 24), outline=(150, 138, 112), width=3)

    # ---------------- data page (left) ----------------
    shield(d, 56, 62, 116)
    spaced(d, 196, 74, "REPUBLIC OF FJELLAND", F(SERIF_B, 46), PINE, 2)
    spaced(d, 198, 132, "FJELLANDS REPUBLIKK  ·  PASSPORT", F(SANS_B, 21),
           GOLD, 3)
    d.line((56, 176, 968, 176), fill=PINE, width=4)
    d.line((56, 184, 968, 184), fill=PINE, width=1)

    # portrait + signature
    draw_portrait(d, 56, 216, 288, 368)
    d.text((56, 596), "PHOTO 35 × 45 mm", font=F(SANS, 15), fill=GREY)
    d.text((60, 640), "Elin Haug", font=F(SERIF_I, 46), fill=(44, 62, 110))
    d.line((56, 700, 344, 700), fill=INK, width=2)
    d.text((56, 710), "HOLDER'S SIGNATURE", font=F(SANS, 15), fill=GREY)

    # round office seal under the signature
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    round_seal(od, 200, 830, 96, PINE, "",
               [("12 MAR", 30), ("2024", 30)], alpha=200)
    ring_text(ov, 200, 830, 66, "FJELLSTAD", 20, PINE, 200)
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov), (0, 0))

    # data fields
    fx, fy = 380, 216
    d.text((fx, fy), "TYPE", font=F(SANS, 17), fill=GREY)
    d.text((fx, fy + 22), "P", font=F(SERIF_B, 30), fill=INK)
    d.text((fx + 110, fy), "CODE", font=F(SANS, 17), fill=GREY)
    d.text((fx + 110, fy + 22), "FJL", font=F(SERIF_B, 30), fill=INK)
    d.text((fx + 250, fy), "PASSPORT No.", font=F(SANS, 17), fill=GREY)
    d.text((fx + 250, fy + 22), "FJ 482 917", font=F(SERIF_B, 30), fill=INK)
    d.line((fx, fy + 60, 968, fy + 60), fill=(190, 182, 160), width=2)
    fy += 74
    fy = field(d, fx, fy, 588, "SURNAME · ETTERNAVN", "HAUG")
    fy = field(d, fx, fy, 588, "GIVEN NAMES · FORNAVN", "ELIN SOFIE")
    fy = field(d, fx, fy, 588, "NATIONALITY · NASJONALITET", "FJELLANDER")
    y0 = fy
    fy = field(d, fx, fy, 280, "DATE OF BIRTH · FØDT", "14 JUN 1990")
    field(d, fx + 310, y0, 278, "SEX · KJØNN", "F")
    fy = field(d, fx, fy, 588, "PLACE OF BIRTH · FØDESTED", "FJELLSTAD")
    y0 = fy
    fy = field(d, fx, fy, 280, "HEIGHT · HØYDE", "171 cm")
    field(d, fx + 310, y0, 278, "EYES · ØYNE", "GREY")
    fy = field(d, fx, fy, 588, "OCCUPATION · YRKE", "MOUNTAIN RESCUE GUIDE")
    y0 = fy
    fy = field(d, fx, fy, 280, "DATE OF ISSUE · UTSTEDT", "12 MAR 2024")
    field(d, fx + 310, y0, 278, "PLACE OF ISSUE", "FJELLSTAD")
    y0 = fy
    fy = field(d, fx, fy, 280, "DATE OF EXPIRY · GYLDIG TIL", "11 MAR 2034")
    field(d, fx + 310, y0, 278, "AUTHORITY · MYNDIGHET", "PASSPORT OFFICE")

    # observation
    oy = 1000
    d.rectangle((56, oy, 968, oy + 148), outline=PINE, width=2)
    d.text((72, oy + 12), "OBSERVATION · MERKNAD", font=F(SANS_B, 19),
           fill=PINE)
    obs = ("The holder, being a certified Mountain Rescue Guide, may cross "
           "the high passes of Fjelland without visa when on duty, and may "
           "land at any mountain station without formality.")
    yy = oy + 42
    for ln in wrap(d, obs, F(SERIF_I, 25), 880):
        d.text((72, yy), ln, font=F(SERIF_I, 25), fill=INK)
        yy += 32

    # MRZ
    l1, l2 = mrz_lines()
    d.rectangle((56, 1188, 968, 1300), fill=(232, 228, 214))
    d.text((72, 1204), l1, font=F(MONO, 29), fill=INK)
    d.text((72, 1244), l2, font=F(MONO, 29), fill=INK)
    d.text((56, 1320), "P<FJL HAUG<<ELIN<SOFIE — FJ 482 917 — 14 JUN 1990 — 11 MAR 2034",
           font=F(SANS, 16), fill=GREY)
    d.text((56, 1372), "This passport remains the property of the Republic of Fjelland.",
           font=F(SERIF_I, 19), fill=GREY)
    d.text((940, 1372), "7", font=F(SERIF, 20), fill=GREY)

    # ---------------- visas page (right) ----------------
    vx = 1088
    spaced(d, vx, 74, "VISAS", F(SERIF_B, 46), PINE, 2)
    spaced(d, vx + 210, 88, "ENDORSEMENTS · STAMPS", F(SANS_B, 21), GOLD, 3)
    d.line((vx, 176, 2008, 176), fill=PINE, width=4)
    d.line((vx, 184, 2008, 184), fill=PINE, width=1)

    stamps = [
        (vx, 216, BLUE, "KINGDOM OF VESTLAND", "ARRIVAL", "Brenna Pass",
         "02 APR 2024", -1.5),
        (vx + 480, 216, BLUE, "KINGDOM OF VESTLAND", "DEPARTURE",
         "Brenna Pass", "18 APR 2024", 1.2),
        (vx, 448, GREEN, "REPUBLIC OF OSTARA", "ARRIVAL",
         "Lake Ostara Ferry", "09 SEP 2025", 1.4),
        (vx + 480, 448, GREEN, "REPUBLIC OF OSTARA", "DEPARTURE",
         "Lake Ostara Ferry", "23 SEP 2025", -1.0),
    ]
    base = img.convert("RGBA")
    for x, y, col, country, kind, place, date, ang in stamps:
        layer, pos = stamp_rect(d, x, y, 440, 190, col, [
            (country, 26, True), (kind, 24, True), (place, 22, False),
            (date, 30, True)], angle=ang)
        base = Image.alpha_composite(base, Image.new("RGBA", (W, H)))
        tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        tmp.paste(layer, pos)
        base = Image.alpha_composite(base, tmp)
    img = base.convert("RGB")
    d = ImageDraw.Draw(img)

    # condition of issue
    cy = 690
    d.rectangle((vx, cy, 2008, cy + 190), outline=PINE, width=2)
    d.text((vx + 16, cy + 12), "CONDITION OF ISSUE — FJELLAND MOUNTAIN ACT §7",
           font=F(SANS_B, 20), fill=PINE)
    cond = ("The holder must register with the Mountain Warden within 48 "
            "hours of any arrival by high pass, and must carry a stamped "
            "route card when travelling beyond the Northern Ridges.")
    yy = cy + 46
    for ln in wrap(d, cond, F(SERIF, 25), 888):
        d.text((vx + 16, yy), ln, font=F(SERIF, 25), fill=INK)
        yy += 32

    # departure seal + fee stamp
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    round_seal(od, 1300, 1060, 118, PINE, "",
               [("14 FEB", 34), ("2026", 34)], alpha=225)
    ring_text(ov, 1300, 1060, 84, "FJELLAND DEPARTURE", 22, PINE, 225)
    d2 = ImageDraw.Draw(ov)
    layer, pos = stamp_rect(d2, 1560, 990, 420, 130, PURPLE, [
        ("MOUNTAIN PASS FEE PAID", 26, True), ("40 KRONER", 30, True)],
        angle=-8)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.paste(layer, pos)
    ov = Image.alpha_composite(ov, tmp)
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    d = ImageDraw.Draw(img)

    d.text((vx, 1240), "HOLDER IS A CERTIFIED MOUNTAIN RESCUE GUIDE. RE-ENTRY TO THE",
           font=F(SANS, 17), fill=GREY)
    d.text((vx, 1264), "OUTER RIDGES REQUIRES A WARDEN STAMP.",
           font=F(SANS, 17), fill=GREY)
    d.text((vx, 1300), "FJELLSTAD · 12 MAR 2024 · PASSPORT OFFICE",
           font=F(SANS, 16), fill=GREY)
    d.text((1980, 1372), "8", font=F(SERIF, 20), fill=GREY)

    img = guilloche(img)
    img = img.resize((1024, 720), Image.LANCZOS).convert("RGB")
    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes", img.size)


if __name__ == "__main__":
    build()
