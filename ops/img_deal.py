#!/usr/bin/env python3
"""Deal Room pictures for the acquire desk's buyer guides (added 27 Nov 2026, colours reworked the same day).

Zeeshan, 27 Nov 2026, about the buyer guides that send readers to /acquire: "We need different kind of
graphics and images for these articles which look professional", then on the first draft: "The graphics
and colors look cheap tbh. The color should be blue or something like acquire uses."

So this follows the look of the Acquire.com marketplace: deep indigo, electric blue, a pale blue page,
white cards with soft shadows, heavy geometric sans headlines (Inter 800). Opt-in with "theme": "deal"
inside an image system 2 block; every other article keeps the warm explainer style of img_v2_explain.py.

Same spec block and the same five layouts as image system 2 (flow, cards, compare, timeline, rules).
The preview cover (blog card, og:image) is indigo with a white "listing card" that carries the key figure.
"palette" is accepted and ignored (one blue look for the whole desk).

Pillow only. Font: Inter (SIL OFL).
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('IMISOFTS_FONTS', os.path.join(HERE, 'fonts'))
W, H, S = 1200, 675, 2

INDIGO = (37, 34, 74)          # Acquire.com heading and hero colour
INDIGO_2 = (52, 46, 112)
BLUE = (62, 80, 247)           # Acquire.com button blue
BLUE_DEEP = (44, 58, 214)
BLUE_SOFT = (232, 235, 255)    # rgba(78, 95, 255, 0.1) on white
PAGE = (238, 242, 254)         # Acquire.com section background
TRACK = (214, 223, 252)
CARD = (255, 255, 255)
SLATE = (84, 88, 122)
MUTED = (112, 117, 150)
LINE = (220, 226, 246)
GREEN, GREEN_BG = (21, 128, 61), (220, 245, 230)
RED, RED_BG = (200, 40, 50), (253, 228, 230)
AMBER, AMBER_BG = (176, 100, 10), (254, 240, 214)
BRAND = (244, 84, 7)

_F = {}
def F(weight, size):
    k = (weight, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-%s.ttf' % weight), int(size * S))
    return _F[k]


def X(v):
    return int(round(v * S))


def rrect(d, x0, y0, x1, y1, r, fill=None, outline=None, width=1.0):
    d.rounded_rectangle([X(x0), X(y0), X(x1), X(y1)], radius=X(r), fill=fill, outline=outline,
                        width=max(1, X(width)) if outline else 0)


def shadow(img, x0, y0, x1, y1, r, strength=34, dy=10, blur=22):
    """Soft drop shadow under a card (drawn on the image before the card)."""
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([X(x0), X(y0 + dy), X(x1), X(y1 + dy)], radius=X(r), fill=INDIGO + (strength,))
    lay = lay.filter(ImageFilter.GaussianBlur(X(blur)))
    img.alpha_composite(lay)


def card(img, x0, y0, x1, y1, r=18, fill=CARD, strength=30):
    shadow(img, x0, y0, x1, y1, r, strength)
    d = ImageDraw.Draw(img)
    rrect(d, x0, y0, x1, y1, r, fill=fill)
    return d


def wrap(d, text, font, maxw):
    words, lines, cur = (text or '').split(), [], ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=font) <= maxw * S:
            cur = c
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def spaced(d, xy, text, font, fill, track=1.6, anchor='l'):
    x, y = xy
    total = sum(d.textlength(ch, font=font) for ch in text) / S + track * max(0, len(text) - 1)
    if anchor == 'm':
        x -= total / 2
    elif anchor == 'r':
        x -= total
    for ch in text:
        d.text((X(x), X(y)), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) / S + track
    return total


def pill(d, x, y, text, fg, bg, size=13, padx=14, h=30, track=1.4, anchor='l'):
    f = F(700, size)
    tw = sum(d.textlength(ch, font=f) for ch in text) / S + track * max(0, len(text) - 1)
    w = tw + 2 * padx
    if anchor == 'm':
        x -= w / 2
    rrect(d, x, y, x + w, y + h, h / 2, fill=bg)
    spaced(d, (x + padx, y + (h - size) / 2 - 2), text, f, fg, track)
    return w


# ------------------------------------------------------------------ clean line icons (drawn on a 64 unit grid)
class Ic:
    def __init__(self, d, cx, cy, size, color, width=2.4):
        self.d, self.cx, self.cy, self.k, self.c, self.w = d, cx, cy, size / 64.0, color, width

    def p(self, x, y):
        return (X(self.cx + (x - 32) * self.k), X(self.cy + (y - 32) * self.k))

    def line(self, *pts):
        self.d.line([self.p(*q) for q in pts], fill=self.c, width=X(self.w), joint='curve')

    def rect(self, x0, y0, x1, y1, r=3, fill=None):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.rounded_rectangle([a, b], radius=X(r * self.k), outline=self.c, width=X(self.w), fill=fill)

    def ell(self, x0, y0, x1, y1, fill=None):
        self.d.ellipse([self.p(x0, y0), self.p(x1, y1)], outline=self.c, width=X(self.w), fill=fill)

    def arc(self, x0, y0, x1, y1, a0, a1):
        self.d.arc([self.p(x0, y0), self.p(x1, y1)], a0, a1, fill=self.c, width=X(self.w))

    def text(self, x, y, t, size, weight=700):
        self.d.text(self.p(x, y), t, font=F(weight, size * self.k), fill=self.c, anchor='mm')


def i_database(i):
    i.ell(14, 8, 50, 20); i.line((14, 14), (14, 50)); i.line((50, 14), (50, 50))
    i.arc(14, 26, 50, 38, 0, 180); i.arc(14, 44, 50, 56, 0, 180)

def i_document(i):
    i.line((16, 8), (40, 8), (50, 18), (50, 56), (16, 56), (16, 8)); i.line((40, 8), (40, 18), (50, 18))
    for y in (28, 36, 44):
        i.line((23, y), (43, y))

def i_shield(i):
    i.line((32, 7), (52, 15), (52, 31), (32, 57), (12, 31), (12, 15), (32, 7)); i.line((23, 31), (30, 38), (42, 25))

def i_lock(i):
    i.rect(14, 28, 50, 56, 4); i.arc(20, 10, 44, 38, 180, 360); i.line((32, 38), (32, 46))

def i_chip(i):
    i.rect(18, 18, 46, 46, 4); i.rect(26, 26, 38, 38, 2)
    for v in (24, 32, 40):
        i.line((v, 10), (v, 18)); i.line((v, 46), (v, 54)); i.line((10, v), (18, v)); i.line((46, v), (54, v))

def i_building(i):
    i.line((12, 56), (52, 56)); i.rect(18, 12, 46, 56, 1)
    for y in (20, 30, 40):
        i.line((25, y), (29, y)); i.line((35, y), (39, y))
    i.line((29, 56), (29, 47), (35, 47), (35, 56))

def i_coin(i):
    i.ell(10, 10, 54, 54); i.text(32, 33, '$', 26, 700)

def i_envelope(i):
    i.rect(10, 16, 54, 48, 3); i.line((12, 19), (32, 34), (52, 19))

def i_calendar(i):
    i.rect(10, 14, 54, 54, 4); i.line((10, 26), (54, 26)); i.line((22, 8), (22, 18)); i.line((42, 8), (42, 18))
    for x in (22, 32, 42):
        for y in (36, 46):
            i.d.ellipse([i.p(x - 1.6, y - 1.6), i.p(x + 1.6, y + 1.6)], fill=i.c)

def i_wave(i):
    for x, h in ((14, 8), (22, 18), (30, 28), (38, 16), (46, 24), (54, 10)):
        i.line((x - 2, 32 - h / 2), (x - 2, 32 + h / 2))

def i_card(i):
    i.rect(8, 16, 56, 48, 4); i.line((8, 25), (56, 25)); i.line((16, 39), (30, 39))

def i_key(i):
    i.ell(8, 22, 28, 42); i.line((28, 32), (56, 32)); i.line((48, 32), (48, 40)); i.line((40, 32), (40, 38))

def i_person(i):
    i.ell(22, 8, 42, 28); i.arc(12, 34, 52, 74, 180, 360)

def i_scale(i):
    i.line((32, 10), (32, 52)); i.line((20, 52), (44, 52)); i.line((12, 18), (52, 18))
    i.line((12, 18), (6, 34)); i.line((12, 18), (18, 34)); i.arc(6, 28, 18, 40, 0, 180)
    i.line((52, 18), (46, 34)); i.line((52, 18), (58, 34)); i.arc(46, 28, 58, 40, 0, 180)

def i_chart(i):
    i.line((10, 8), (10, 54), (56, 54)); i.line((16, 44), (28, 32), (36, 38), (52, 18)); i.line((44, 18), (52, 18), (52, 26))

def i_globe(i):
    i.ell(8, 8, 56, 56); i.ell(22, 8, 42, 56); i.line((8, 32), (56, 32)); i.arc(10, 6, 54, 28, 30, 150); i.arc(10, 36, 54, 58, 210, 330)

def i_warning(i):
    i.line((32, 8), (58, 54), (6, 54), (32, 8)); i.line((32, 24), (32, 38))
    i.d.ellipse([i.p(30, 44), i.p(34, 48)], fill=i.c)

def i_briefcase(i):
    i.rect(8, 20, 56, 52, 4); i.line((24, 20), (24, 13), (40, 13), (40, 20)); i.line((8, 33), (56, 33)); i.rect(28, 29, 36, 37, 1)

def i_bank(i):
    i.line((6, 22), (32, 8), (58, 22), (6, 22)); i.line((8, 54), (56, 54)); i.line((10, 48), (54, 48))
    for x in (16, 27, 37, 48):
        i.line((x, 26), (x, 44))

def i_percent(i):
    i.ell(10, 10, 26, 26); i.ell(38, 38, 54, 54); i.line((48, 12), (16, 52))

def i_search(i):
    i.ell(8, 8, 40, 40); i.line((36, 36), (54, 54))

def i_clock(i):
    i.ell(8, 8, 56, 56); i.line((32, 18), (32, 32), (42, 38))

def i_flag(i):
    i.line((14, 56), (14, 8)); i.line((14, 10), (50, 10), (42, 21), (50, 32), (14, 32))

def i_handshake(i):
    i.rect(4, 20, 13, 42, 2); i.rect(51, 20, 60, 42, 2)          # cuffs
    i.line((13, 23), (24, 19), (33, 22))                         # left hand, top
    i.line((51, 23), (42, 20), (28, 30), (31, 34), (40, 28))     # right hand pulling in
    i.line((13, 38), (22, 46), (29, 50), (36, 49), (44, 44), (51, 39))   # hands, bottom
    i.line((25, 41), (29, 45)); i.line((30, 38), (35, 43)); i.line((36, 35), (41, 40))  # fingers

ICONS = {'database': i_database, 'document': i_document, 'shield': i_shield, 'lock': i_lock, 'chip': i_chip, 'ai': i_chip,
         'building': i_building, 'lab': i_building, 'coin': i_coin, 'money': i_coin, 'envelope': i_envelope, 'email': i_envelope,
         'calendar': i_calendar, 'wave': i_wave, 'audio': i_wave, 'card': i_card, 'key': i_key, 'person': i_person,
         'scale': i_scale, 'law': i_scale, 'chart': i_chart, 'globe': i_globe, 'warning': i_warning,
         'briefcase': i_briefcase, 'bank': i_bank, 'percent': i_percent, 'search': i_search, 'clock': i_clock,
         'flag': i_flag, 'handshake': i_handshake}


def icon(d, name, cx, cy, size, color, width=2.6):
    ICONS.get(name, i_document)(Ic(d, cx, cy, size, color, width))


def icon_chip(d, name, cx, cy, box, hot=False, on_blue=False):
    """Blue line icon in a pale blue rounded square (white on blue when the card is highlighted)."""
    if on_blue:
        rrect(d, cx - box / 2, cy - box / 2, cx + box / 2, cy + box / 2, box * 0.28, fill=(92, 108, 250))
        icon(d, name, cx, cy, box * 0.56, CARD, 2.6)
    else:
        rrect(d, cx - box / 2, cy - box / 2, cx + box / 2, cy + box / 2, box * 0.28, fill=BLUE if hot else BLUE_SOFT)
        icon(d, name, cx, cy, box * 0.56, CARD if hot else BLUE, 2.6)


def num_badge(d, cx, cy, n, hot=False, on_blue=False, r=17):
    fill = CARD if on_blue else (BLUE if hot else INDIGO)
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=fill)
    d.text((X(cx), X(cy + 0.5)), str(n), font=F(800, 16), fill=BLUE if on_blue else CARD, anchor='mm')


def logo(d, x, top, s, word):
    Q = lambda px, py: (X(x + s * px), X(top + s * py))
    cx, cy = Q(48, 170); r = 18 * s * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRAND)
    d.polygon([Q(84, 84), Q(136, 84), Q(118, 188), Q(66, 188)], fill=BRAND)
    d.polygon([Q(146, 84), Q(198, 84), Q(180, 188), Q(128, 188)], fill=BRAND)
    d.text(Q(200, 188), 'imisofts', font=ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-700.ttf'), int(96 * s * S)), fill=word, anchor='ls')


# ------------------------------------------------------------------ in-body pictures (pale blue page, white cards)
def frame(d, ex):
    k = (ex.get('kicker') or '').upper()
    if k:
        pill(d, 72, 50, k, BLUE, CARD, size=12, padx=13, h=28, track=1.5)
    hl = ex.get('headline', '')
    hf = F(800, 38)
    if d.textlength(hl, font=hf) > 880 * S:
        hf = F(800, 32)
    d.text((X(72), X(92)), hl, font=hf, fill=INDIGO)
    logo(d, W - 72 - 150, 54, 0.17, INDIGO)
    if ex.get('footnote'):
        d.text((X(72), X(H - 42)), ex['footnote'], font=F(500, 14), fill=MUTED)
    spaced(d, (W - 72, H - 41), 'BUYER GUIDE', F(700, 11), MUTED, 1.6, anchor='r')


def lay_flow(img, d, ex):
    items = ex['items'][:5]
    n = len(items)
    gap = 18
    cw = (1056 - gap * (n - 1)) / n
    top, bot = 176, 596
    hot_any = any(x.get('hot') for x in items)
    for i, it in enumerate(items):
        x = 72 + i * (cw + gap)
        hot = it.get('hot') or (i == n - 1 and not hot_any)
        d = card(img, x, top, x + cw, bot, 18, fill=BLUE if hot else CARD)
        num_badge(d, x + 32, top + 34, i + 1, hot, on_blue=hot)
        if i < n - 1:                                   # small connector between cards
            cy = top + 34
            d.line([X(x + cw + 3), X(cy), X(x + cw + gap - 3), X(cy)], fill=TRACK, width=X(2))
        icon_chip(d, it.get('icon', 'document'), x + cw / 2, top + 140, 84, on_blue=hot)
        if it.get('badge'):
            pill(d, x + cw / 2, top + 196, it['badge'], CARD if not hot else BLUE, BLUE if not hot else CARD, size=12, padx=10, h=24, anchor='m')
        y = top + 236
        for ln in wrap(d, it.get('label', ''), F(800, 22), cw - 30)[:2]:
            d.text((X(x + cw / 2), X(y)), ln, font=F(800, 22), fill=CARD if hot else INDIGO, anchor='ma'); y += 28
        y += 8
        for ln in wrap(d, it.get('note', ''), F(500, 16), cw - 34)[:4]:
            d.text((X(x + cw / 2), X(y)), ln, font=F(500, 16), fill=(222, 226, 255) if hot else SLATE, anchor='ma'); y += 22


def lay_cards(img, d, ex):
    items = ex['items'][:6]
    n = len(items)
    per = n if n <= 3 else (2 if n == 4 else 3)
    rows = math.ceil(n / per)
    gap = 22
    cw = (1056 - gap * (per - 1)) / per
    top = 170
    ch = (426 - gap * (rows - 1)) / rows
    for i, it in enumerate(items):
        r, c = divmod(i, per)
        in_row = min(per, n - r * per)                 # centre a short last row
        x, y = 72 + (per - in_row) * (cw + gap) / 2 + c * (cw + gap), top + r * (ch + gap)
        hot = it.get('hot')
        d = card(img, x, y, x + cw, y + ch, 18, fill=BLUE if hot else CARD)
        icon_chip(d, it.get('icon', 'document'), x + 52, y + 52, 60, on_blue=hot)
        if ex.get('numbered'):
            pill(d, x + cw - 24 - 70, y + 38, 'STEP %d' % (i + 1), CARD if hot else BLUE, (92, 108, 250) if hot else BLUE_SOFT, size=11, padx=10, h=26)
        ty = y + 100 if rows > 1 else y + 132
        for ln in wrap(d, it.get('label', ''), F(800, 22), cw - 52)[:2]:
            d.text((X(x + 26), X(ty)), ln, font=F(800, 22), fill=CARD if hot else INDIGO); ty += 28
        ty += 6
        for ln in wrap(d, it.get('note', ''), F(500, 16), cw - 52)[:3]:
            d.text((X(x + 26), X(ty)), ln, font=F(500, 16), fill=(222, 226, 255) if hot else SLATE); ty += 22


def lay_compare(img, d, ex):
    items = ex['items'][:4]
    n = len(items)
    top, bot = 170, 598
    d = card(img, 72, top, W - 72, bot, 20)
    rh = (bot - top - 24) / n
    bx0, bx1 = 430, 880
    vmax = max([it.get('num') or 0 for it in items] + [0]) or 1
    for i, it in enumerate(items):
        y = top + 12 + i * rh
        cy = y + rh / 2
        hot = it.get('hot')
        icon_chip(d, it.get('icon', 'coin'), 132, cy, 56, hot)
        lf = F(800, 22)
        if d.textlength(it.get('label', ''), font=lf) > 250 * S:
            lf = F(800, 18)
        ly = cy - (24 if it.get('note') else 13)
        d.text((X(176), X(ly)), it.get('label', ''), font=lf, fill=INDIGO)
        if it.get('note'):
            d.text((X(176), X(ly + 30)), it['note'], font=F(500, 15), fill=SLATE)
        if it.get('num') is not None:
            bw = max(14, (bx1 - bx0) * float(it['num']) / vmax)
            rrect(d, bx0, cy - 13, bx1, cy + 13, 13, fill=PAGE)
            rrect(d, bx0, cy - 13, bx0 + bw, cy + 13, 13, fill=BLUE if hot else INDIGO)
        val = it.get('value', '')
        d.text((X(908), X(cy - 4)), val, font=F(800, 32 if len(val) <= 8 else 26), fill=BLUE if hot else INDIGO, anchor='ls')
        if it.get('unit'):
            d.text((X(908), X(cy + 20)), it['unit'], font=F(500, 15), fill=SLATE, anchor='ls')
        if i < n - 1:
            d.line([X(104), X(y + rh), X(W - 104), X(y + rh)], fill=LINE, width=X(1))


def lay_timeline(img, d, ex):
    items = ex['items'][:5]
    n = len(items)
    x0, x1 = 170, 1030
    ay = 420
    d = card(img, 72, 170, W - 72, 598, 20)
    step = (x1 - x0) / max(1, n - 1)
    xs = [x0 + step * i if n > 1 else (x0 + x1) / 2 for i in range(n)]
    h = next((i for i, it in enumerate(items) if it.get('hot')), n - 1)
    rrect(d, 120, ay - 3, W - 120, ay + 3, 3, fill=TRACK)
    rrect(d, 120, ay - 3, xs[h], ay + 3, 3, fill=BLUE)          # progress up to the highlighted step
    for i, it in enumerate(items):
        x = xs[i]
        hot = i == h
        icon_chip(d, it.get('icon', 'calendar'), x, 268, 68, hot)
        d.text((X(x), X(334)), it.get('date', ''), font=F(800, 22), fill=BLUE if hot else INDIGO, anchor='ma')
        r = 12 if hot else 8
        d.ellipse([X(x - r), X(ay - r), X(x + r), X(ay + r)], fill=BLUE if i <= h else CARD, outline=BLUE, width=X(3))
        if hot:
            d.ellipse([X(x - 4), X(ay - 4), X(x + 4), X(ay + 4)], fill=CARD)
        y = ay + 34
        for ln in wrap(d, it.get('label', ''), F(600, 17), step - 24)[:3]:
            d.text((X(x), X(y)), ln, font=F(600, 17), fill=SLATE, anchor='ma'); y += 23


MARKS = {'yes': ('YES', GREEN, GREEN_BG), 'no': ('NO', RED, RED_BG), 'warn': ('CHECK', AMBER, AMBER_BG)}

def lay_rules(img, d, ex):
    d = card(img, 72, 170, 380, 598, 20, fill=INDIGO, strength=40)
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([X(170), X(190), X(380), X(400)], fill=BLUE + (120,))
    glow = glow.filter(ImageFilter.GaussianBlur(X(50)))
    mask = Image.new('L', img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([X(72), X(170), X(380), X(598)], radius=X(20), fill=255)
    img.paste(Image.alpha_composite(img.copy(), glow), (0, 0), mask)
    d = ImageDraw.Draw(img)
    rrect(d, 166, 238, 286, 358, 30, fill=BLUE)
    icon(d, ex.get('subject_icon', 'document'), 226, 298, 70, CARD, 3.0)
    y = 396
    for ln in wrap(d, ex.get('subject') or '', F(800, 26), 260)[:2]:
        d.text((X(226), X(y)), ln, font=F(800, 26), fill=CARD, anchor='ma'); y += 33
    spaced(d, (226, 556), 'AT A GLANCE', F(700, 11), (170, 176, 230), 1.8, anchor='m')
    rows = ex['items'][:4]
    n = len(rows)
    top, bot = 170, 598
    d = card(img, 404, top, W - 72, bot, 20)
    rh = (bot - top - 20) / n
    for i, r in enumerate(rows):
        y = top + 10 + i * rh
        cy = y + rh / 2
        label, col, bg = MARKS.get(r.get('mark', 'yes'), MARKS['yes'])
        rrect(d, 434, cy - 14, 434 + 82, cy + 14, 14, fill=bg)
        spaced(d, (434 + 41, cy - 8), label, F(800, 12), col, 1.2, anchor='m')
        ty = cy - (24 if r.get('note') else 13)
        d.text((X(540), X(ty)), r.get('label', ''), font=F(800, 22), fill=INDIGO)
        if r.get('note'):
            d.text((X(540), X(ty + 30)), r['note'], font=F(500, 16), fill=SLATE)
        if i < n - 1:
            d.line([X(434), X(y + rh), X(W - 102), X(y + rh)], fill=LINE, width=X(1))


LAYOUTS = {'flow': lay_flow, 'cards': lay_cards, 'compare': lay_compare, 'timeline': lay_timeline, 'rules': lay_rules}


def _save(img, path_base):
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=90, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=91, optimize=True, progressive=True)


def render_explain(path_base, slug, ex, palette=None):
    img = Image.new('RGBA', (W * S, H * S), PAGE + (255,))
    d = ImageDraw.Draw(img)
    frame(d, ex)
    LAYOUTS.get(ex.get('layout', 'flow'), lay_flow)(img, d, ex)
    _save(img, path_base)
    return 'deal'


# ------------------------------------------------------------------ preview cover (blog card, og:image, schema)
def render_cover(path_base, slug, ex, headline, palette=None):
    img = Image.new('RGBA', (W * S, H * S), INDIGO + (255,))
    glow = Image.new('RGBA', img.size, (0, 0, 0, 0))     # soft blue light, top right and bottom left
    g = ImageDraw.Draw(glow)
    g.ellipse([X(720), X(-260), X(1380), X(380)], fill=BLUE + (150,))
    g.ellipse([X(-260), X(470), X(260), X(900)], fill=(110, 90, 255, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(X(90)))
    img = Image.alpha_composite(img, glow)
    dots = Image.new('RGBA', img.size, (0, 0, 0, 0))     # dot grid, like a deal-room dashboard
    dd = ImageDraw.Draw(dots)
    for gx in range(36, W, 28):
        for gy in range(30, H, 28):
            dd.ellipse([X(gx - 1), X(gy - 1), X(gx + 1), X(gy + 1)], fill=(255, 255, 255, 16))
    img = Image.alpha_composite(img, dots)
    d = ImageDraw.Draw(img)
    k = (ex.get('kicker') or 'Buyer guide').upper()
    pill(d, 72, 118, k, (190, 198, 255), (70, 70, 150), size=13, padx=15, h=32, track=1.8)
    hf = F(800, 60)
    lines = wrap(d, headline, hf, 640)
    if len(lines) > 3:
        hf = F(800, 50); lines = wrap(d, headline, hf, 640)
    y = 176
    for ln in lines[:4]:
        d.text((X(72), X(y)), ln, font=hf, fill=CARD)
        y += int(hf.size / S * 1.16)
    # the white "listing card" on the right
    cx0, cy0, cx1, cy1 = 742, 150, 1128, 500
    shadow(img, cx0, cy0, cx1, cy1, 22, strength=110, dy=18, blur=30)
    d = ImageDraw.Draw(img)
    rrect(d, cx0, cy0, cx1, cy1, 22, fill=CARD)
    spaced(d, (cx0 + 30, cy0 + 30), 'KEY FIGURE', F(700, 12), MUTED, 2.0)
    big = ex.get('cover_number') or ''
    size = 64
    while size > 34 and d.textlength(big, font=F(800, size)) > (cx1 - cx0 - 60) * S:
        size -= 4
    d.text((X(cx0 + 30), X(cy0 + 58)), big, font=F(800, size), fill=BLUE)
    cap = ex.get('cover_caption') or ex.get('headline') or ''
    yy = cy0 + 74 + size
    for ln in wrap(d, cap, F(600, 17), cx1 - cx0 - 60)[:2]:
        d.text((X(cx0 + 30), X(yy)), ln, font=F(600, 17), fill=SLATE); yy += 23
    d.line([X(cx0 + 30), X(cy1 - 110), X(cx1 - 30), X(cy1 - 110)], fill=LINE, width=X(1))
    # mini bar chart inside the card (decorative rising bars)
    bx, by = cx0 + 30, cy1 - 30
    rnd = random.Random(slug + ':bars')
    hts = sorted(rnd.uniform(18, 70) for _ in range(7))
    for j, hgt in enumerate(hts):
        rrect(d, bx + j * 22, by - hgt, bx + j * 22 + 14, by, 4, fill=BLUE if j == len(hts) - 1 else TRACK)
    names = ([ex.get('subject_icon')] if ex.get('layout') == 'rules' else []) + [it.get('icon') for it in (ex.get('items') or []) if it.get('icon')]
    seen = []
    for nme in names:
        if nme and nme not in seen:
            seen.append(nme)
    seen = (seen or ['briefcase', 'chart', 'document'])[:3]
    gx = cx1 - 30 - 46 * len(seen) - 8 * (len(seen) - 1)
    for nme in seen:
        rrect(d, gx, by - 46, gx + 46, by, 12, fill=BLUE_SOFT)
        icon(d, nme, gx + 23, by - 23, 26, BLUE, 2.2)
        gx += 54
    logo(d, 72, 562, 0.24, CARD)
    spaced(d, (W - 72, 592), 'IMISOFTS.COM/BLOG', F(600, 12), (170, 176, 230), 2.0, anchor='r')
    _save(img, path_base)
    return 'deal'
