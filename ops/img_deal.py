#!/usr/bin/env python3
"""Deal Room pictures for the acquire desk's buyer guides (added 27 Nov 2026).

Zeeshan, 27 Nov 2026, about the buyer guides that send readers to /acquire: "We need different kind of
graphics and images for these articles which look professional." Opt-in with "theme": "deal" inside an
image system 2 block; every other article keeps the warm explainer style of img_v2_explain.py.

Same spec block and the same five layouts as image system 2 (flow, cards, compare, timeline, rules), drawn
like an investment research note instead of a sketch:
  - in-body pictures: warm white paper, navy ink, a serif headline, hairline rules, clean line icons,
    numbered steps, horizontal bar charts, a term-sheet table for rules;
  - the preview cover (blog card, og:image): deep navy, serif headline, the key figure in a stat panel.
Palettes keep their names so the engines can rotate them: ember = gold accent, sage = teal, tide = blue.

Pillow only. Fonts: Inter (labels) and Source Serif 4 Display (headlines and figures), both SIL OFL.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('IMISOFTS_FONTS', os.path.join(HERE, 'fonts'))
W, H, S = 1200, 675, 2

NAVY = (12, 27, 51)
NAVY_2 = (21, 42, 74)
INK = (15, 23, 42)
SLATE = (71, 85, 105)
MUTED = (100, 116, 139)
LINE = (222, 226, 232)
TRACK = (236, 239, 243)
PAPER = (250, 249, 246)
CARD = (255, 255, 255)
GREEN = (15, 118, 110)
RED = (190, 40, 40)
AMBER = (180, 110, 20)
BRAND = (244, 84, 7)

ACCENTS = {            # accent on light paper, accent on navy
    'ember': ((168, 124, 38), (214, 172, 88)),
    'sage': ((15, 118, 110), (94, 196, 178)),
    'tide': ((30, 78, 160), (126, 168, 236)),
}

_F = {}
def F(kind, size):
    """kind: 400 to 800 for Inter, 'serif' or 'serif-b' for Source Serif 4 Display."""
    k = (kind, size)
    if k not in _F:
        name = {'serif': 'SourceSerif4Display-SemiBold.ttf', 'serif-b': 'SourceSerif4Display-Bold.ttf'}.get(kind, 'Inter-%s.ttf' % kind)
        _F[k] = ImageFont.truetype(os.path.join(FONT_DIR, name), int(size * S))
    return _F[k]


def X(v):
    return int(round(v * S))


def rrect(d, x0, y0, x1, y1, r, fill=None, outline=None, width=1.0):
    d.rounded_rectangle([X(x0), X(y0), X(x1), X(y1)], radius=X(r), fill=fill, outline=outline,
                        width=max(1, X(width)) if outline else 0)


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
    """Letter-spaced small caps line (eyebrows and labels)."""
    x, y = xy
    total = sum(d.textlength(ch, font=font) for ch in text) / S + track * max(0, len(text) - 1)
    if anchor == 'm':
        x -= total / 2
    for ch in text:
        d.text((X(x), X(y)), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) / S + track
    return total


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


def icon(d, name, cx, cy, size, color, width=2.4):
    ICONS.get(name, i_document)(Ic(d, cx, cy, size, color, width))


def icon_tile(d, name, cx, cy, box, color, bg=CARD, border=LINE):
    rrect(d, cx - box / 2, cy - box / 2, cx + box / 2, cy + box / 2, 10, fill=bg, outline=border, width=1.2)
    icon(d, name, cx, cy, box * 0.56, color, 2.3)


def logo(d, x, top, s, word):
    Q = lambda px, py: (X(x + s * px), X(top + s * py))
    cx, cy = Q(48, 170); r = 18 * s * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRAND)
    d.polygon([Q(84, 84), Q(136, 84), Q(118, 188), Q(66, 188)], fill=BRAND)
    d.polygon([Q(146, 84), Q(198, 84), Q(180, 188), Q(128, 188)], fill=BRAND)
    d.text(Q(200, 188), 'imisofts', font=ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-700.ttf'), int(96 * s * S)), fill=word, anchor='ls')


# ------------------------------------------------------------------ in-body pictures (light paper)
def frame(d, A, ex):
    k = (ex.get('kicker') or '').upper()
    if k:
        d.rectangle([X(72), X(66), X(104), X(68.5)], fill=A)
        spaced(d, (114, 59), k, F(700, 13), A, 1.8)
    hl = ex.get('headline', '')
    hf = F('serif', 40)
    if d.textlength(hl, font=hf) > 900 * S:
        hf = F('serif', 34)
    d.text((X(72), X(84)), hl, font=hf, fill=NAVY)
    logo(d, W - 72 - 150, 56, 0.17, NAVY)
    d.line([X(72), X(H - 58), X(W - 72), X(H - 58)], fill=LINE, width=X(1))
    if ex.get('footnote'):
        d.text((X(72), X(H - 44)), ex['footnote'], font=F(500, 14), fill=MUTED)
    tag = 'BUYER GUIDE'
    tw = sum(d.textlength(c, font=F(700, 11)) for c in tag) / S + 1.6 * (len(tag) - 1)
    spaced(d, (W - 72 - tw, H - 42), tag, F(700, 11), MUTED, 1.6)


def lay_flow(d, A, ex):
    items = ex['items'][:5]
    n = len(items)
    gap = 1056 / n
    ty = 262
    d.line([X(72 + gap * 0.5), X(ty), X(72 + gap * (n - 0.5)), X(ty)], fill=LINE, width=X(2))
    for i, it in enumerate(items):
        cx = 72 + gap * (i + 0.5)
        hot = it.get('hot') or (i == n - 1 and not any(x.get('hot') for x in items))
        d.text((X(cx), X(198)), '%02d' % (i + 1), font=F('serif', 32), fill=A if hot else SLATE, anchor='ma')
        r = 9 if hot else 7
        d.ellipse([X(cx - r), X(ty - r), X(cx + r), X(ty + r)], fill=A if hot else NAVY)
        if i < n - 1:
            ax = cx + gap / 2
            d.line([X(ax - 6), X(ty - 6), X(ax), X(ty), X(ax - 6), X(ty + 6)], fill=MUTED, width=X(2), joint='curve')
        icon_tile(d, it.get('icon', 'document'), cx, 354, 88, A if hot else NAVY, border=A if hot else LINE)
        if it.get('badge'):
            bf = F(700, 13)
            bw = d.textlength(it['badge'], font=bf) / S + 18
            rrect(d, cx + 30, 300, cx + 30 + bw, 324, 12, fill=A)
            d.text((X(cx + 30 + bw / 2), X(312)), it['badge'], font=bf, fill=CARD, anchor='mm')
        y = 424
        for ln in wrap(d, it.get('label', ''), F(700, 23), gap - 28)[:2]:
            d.text((X(cx), X(y)), ln, font=F(700, 23), fill=NAVY, anchor='ma'); y += 29
        y += 6
        for ln in wrap(d, it.get('note', ''), F(500, 17), gap - 34)[:3]:
            d.text((X(cx), X(y)), ln, font=F(500, 17), fill=SLATE, anchor='ma'); y += 23


def lay_cards(d, A, ex):
    items = ex['items'][:6]
    n = len(items)
    per = n if n <= 3 else (2 if n == 4 else 3)
    rows = math.ceil(n / per)
    gap = 22
    cw = (1056 - gap * (per - 1)) / per
    top = 162
    ch = (440 - gap * (rows - 1)) / rows
    for i, it in enumerate(items):
        r, c = divmod(i, per)
        x, y = 72 + c * (cw + gap), top + r * (ch + gap)
        hot = it.get('hot')
        rrect(d, x, y, x + cw, y + ch, 12, fill=CARD, outline=A if hot else LINE, width=1.4 if hot else 1.2)
        d.rectangle([X(x), X(y + 14), X(x + 4), X(y + ch - 14)], fill=A if hot else NAVY)
        num = '%02d' % (i + 1)
        d.text((X(x + 26), X(y + 18)), num, font=F('serif', 26), fill=A if (hot or ex.get('numbered')) else SLATE)
        icon_tile(d, it.get('icon', 'document'), x + cw - 50, y + 44, 56, A if hot else NAVY)
        ty = y + (ch * 0.42 if rows > 1 else 132)
        for ln in wrap(d, it.get('label', ''), F(700, 23), cw - 52)[:2]:
            d.text((X(x + 26), X(ty)), ln, font=F(700, 23), fill=NAVY); ty += 29
        ty += 6
        for ln in wrap(d, it.get('note', ''), F(500, 17), cw - 52)[:3]:
            d.text((X(x + 26), X(ty)), ln, font=F(500, 17), fill=SLATE); ty += 23


def lay_compare(d, A, ex):
    items = ex['items'][:4]
    n = len(items)
    top, bottom = 168, 596
    rh = (bottom - top) / n
    bx0, bx1 = 420, 900
    vmax = max([it.get('num') or 0 for it in items] + [0]) or 1
    for q in range(5):                              # light gridlines, like a research chart
        gx = bx0 + (bx1 - bx0) * q / 4
        d.line([X(gx), X(top + 4), X(gx), X(bottom - 8)], fill=TRACK, width=X(1))
    for i, it in enumerate(items):
        y = top + i * rh
        cy = y + rh / 2
        hot = it.get('hot')
        icon_tile(d, it.get('icon', 'coin'), 104, cy, 56, A if hot else NAVY, border=A if hot else LINE)
        ly = cy - (24 if it.get('note') else 13)
        lf = F(700, 23)
        if d.textlength(it.get('label', ''), font=lf) > 256 * S:
            lf = F(700, 19)
        d.text((X(148), X(ly)), it.get('label', ''), font=lf, fill=NAVY)
        if it.get('note'):
            d.text((X(148), X(ly + 30)), it['note'], font=F(500, 15), fill=SLATE)
        if it.get('num') is not None:
            bw = max(8, (bx1 - bx0) * float(it['num']) / vmax)
            d.rectangle([X(bx0), X(cy - 15), X(bx1), X(cy + 15)], fill=TRACK)
            d.rectangle([X(bx0), X(cy - 15), X(bx0 + bw), X(cy + 15)], fill=A if hot else NAVY)
        val = it.get('value', '')
        vf = F('serif-b', 36 if len(val) <= 8 else 30)
        d.text((X(924), X(cy - 6)), val, font=vf, fill=A if hot else NAVY, anchor='ls')
        if it.get('unit'):
            d.text((X(924), X(cy + 20)), it['unit'], font=F(500, 15), fill=SLATE, anchor='ls')
        if i < n - 1:
            d.line([X(72), X(y + rh), X(W - 72), X(y + rh)], fill=LINE, width=X(1))


def lay_timeline(d, A, ex):
    items = ex['items'][:5]
    n = len(items)
    x0, x1 = 150, 1050
    ay = 430
    d.line([X(96), X(ay), X(W - 96), X(ay)], fill=NAVY, width=X(2))
    step = (x1 - x0) / max(1, n - 1)
    for i, it in enumerate(items):
        x = x0 + step * i if n > 1 else (x0 + x1) / 2
        hot = it.get('hot')
        icon_tile(d, it.get('icon', 'calendar'), x, 236, 72, A if hot else NAVY, border=A if hot else LINE)
        d.text((X(x), X(300)), it.get('date', ''), font=F('serif-b', 26), fill=A if hot else NAVY, anchor='ma')
        d.line([X(x), X(346), X(x), X(ay - 12)], fill=LINE, width=X(1.5))
        r = 10 if hot else 7
        d.ellipse([X(x - r), X(ay - r), X(x + r), X(ay + r)], fill=A if hot else CARD, outline=NAVY if not hot else A, width=X(2))
        y = ay + 30
        for ln in wrap(d, it.get('label', ''), F(600, 17), step - 22)[:3]:
            d.text((X(x), X(y)), ln, font=F(600, 18), fill=SLATE, anchor='ma'); y += 23


MARKS = {'yes': ('YES', GREEN), 'no': ('NO', RED), 'warn': ('CHECK', AMBER)}

def lay_rules(d, A, ex, accent_dark=None):
    rrect(d, 72, 162, 396, 596, 14, fill=NAVY)
    icon(d, ex.get('subject_icon', 'document'), 234, 318, 120, accent_dark or A, 3.0)
    sub = ex.get('subject') or ''
    y = 430
    for ln in wrap(d, sub, F('serif', 28), 280)[:2]:
        d.text((X(234), X(y)), ln, font=F('serif', 28), fill=CARD, anchor='ma'); y += 36
    spaced(d, (234, 548), 'AT A GLANCE', F(700, 11), (150, 165, 190), 1.8, anchor='m')
    rows = ex['items'][:4]
    n = len(rows)
    top, bottom = 162, 596
    rh = (bottom - top) / n
    for i, r in enumerate(rows):
        y = top + i * rh
        cy = y + rh / 2
        label, col = MARKS.get(r.get('mark', 'yes'), MARKS['yes'])
        pf = F(800, 12)
        pw = 76
        rrect(d, 428, cy - 14, 428 + pw, cy + 14, 14, fill=col)
        spaced(d, (428 + pw / 2, cy - 8), label, pf, CARD, 1.2, anchor='m')
        ty = cy - (24 if r.get('note') else 13)
        d.text((X(528), X(ty)), r.get('label', ''), font=F(700, 23), fill=NAVY)
        if r.get('note'):
            d.text((X(528), X(ty + 30)), r['note'], font=F(500, 17), fill=SLATE)
        if i < n - 1:
            d.line([X(428), X(y + rh), X(W - 72), X(y + rh)], fill=LINE, width=X(1))


LAYOUTS = {'flow': lay_flow, 'cards': lay_cards, 'compare': lay_compare, 'timeline': lay_timeline, 'rules': lay_rules}


def _save(img, path_base):
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=90, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=91, optimize=True, progressive=True)


def _pal(slug, ex, palette, salt=''):
    rnd = random.Random(slug + salt)
    return palette or ex.get('palette') or rnd.choice(sorted(ACCENTS))


def render_explain(path_base, slug, ex, palette=None):
    pal = _pal(slug, ex, palette)
    if pal not in ACCENTS:
        pal = 'ember'
    A, A_dark = ACCENTS[pal]
    img = Image.new('RGB', (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    frame(d, A, ex)
    lay = ex.get('layout', 'flow')
    if lay == 'rules':
        lay_rules(d, A, ex, accent_dark=A_dark)
    else:
        LAYOUTS.get(lay, lay_flow)(d, A, ex)
    _save(img, path_base)
    return pal


# ------------------------------------------------------------------ preview cover (blog card, og:image, schema)
def render_cover(path_base, slug, ex, headline, palette=None):
    pal = _pal(slug, ex, palette, ':cover')
    if pal not in ACCENTS:
        pal = 'ember'
    A = ACCENTS[pal][1]
    img = Image.new('RGB', (W * S, H * S), NAVY)
    d = ImageDraw.Draw(img)
    for yy in range(H):                                   # gentle vertical gradient
        t = yy / H
        col = tuple(int(NAVY[j] + (NAVY_2[j] - NAVY[j]) * t) for j in range(3))
        d.rectangle([0, X(yy), X(W), X(yy + 1)], fill=col)
    over = Image.new('RGBA', img.size, (0, 0, 0, 0))
    o = ImageDraw.Draw(over)
    for gx in range(0, W + 1, 60):                         # faint grid
        o.line([X(gx), 0, X(gx), X(H)], fill=(255, 255, 255, 9), width=X(1))
    for gy in range(0, H + 1, 60):
        o.line([0, X(gy), X(W), X(gy)], fill=(255, 255, 255, 9), width=X(1))
    rnd = random.Random(slug + ':line')                    # a quiet rising line, bottom right
    pts, y = [], 600
    for k in range(13):
        x = 620 + k * 50
        y = max(300, y - rnd.uniform(-6, 30))
        pts.append((X(x), X(y)))
    o.line(pts, fill=A + (70,), width=X(3), joint='curve')
    img = Image.alpha_composite(img.convert('RGBA'), over)
    d = ImageDraw.Draw(img)
    # left: eyebrow and serif headline
    k = (ex.get('kicker') or 'Buyer guide').upper()
    d.rectangle([X(72), X(122), X(110), X(125)], fill=A)
    spaced(d, (122, 114), k, F(700, 15), A, 2.2)
    hf = F('serif-b', 60)
    lines = wrap(d, headline, hf, 600)
    if len(lines) > 3:
        hf = F('serif-b', 50); lines = wrap(d, headline, hf, 600)
    y = 170
    for ln in lines[:4]:
        d.text((X(72), X(y)), ln, font=hf, fill=CARD)
        y += int(hf.size / S * 1.14)
    # right: stat panel with the key figure and the article's icons
    px0, py0, px1, py1 = 760, 160, 1128, 480
    panel = Image.new('RGBA', img.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([X(px0), X(py0), X(px1), X(py1)], radius=X(18), fill=(255, 255, 255, 14), outline=(255, 255, 255, 46), width=X(1.2))
    img = Image.alpha_composite(img, panel)
    d = ImageDraw.Draw(img)
    big = ex.get('cover_number') or ''
    if big:
        spaced(d, (px0 + 32, py0 + 34), 'KEY FIGURE', F(700, 12), (170, 184, 206), 2.0)
        size = 88
        while size > 40 and d.textlength(big, font=F('serif-b', size)) > (px1 - px0 - 64) * S:
            size -= 4
        d.text((X(px0 + 32), X(py0 + 66)), big, font=F('serif-b', size), fill=A)
        d.line([X(px0 + 32), X(py0 + 92 + size), X(px1 - 32), X(py0 + 92 + size)], fill=(255, 255, 255, 40), width=X(1))
        cap = ex.get('cover_caption') or ex.get('headline') or ''
        cy0 = py0 + 108 + size
        for ln in wrap(d, cap, F(500, 17), px1 - px0 - 64)[:2]:
            d.text((X(px0 + 32), X(cy0)), ln, font=F(500, 17), fill=(196, 206, 222)); cy0 += 23
    items = ex.get('items') or []
    names = ([ex.get('subject_icon')] if ex.get('layout') == 'rules' else []) + [it.get('icon') for it in items if it.get('icon')]
    seen = []
    for nme in names:
        if nme and nme not in seen:
            seen.append(nme)
    seen = (seen or ['briefcase', 'chart', 'document'])[:3]
    gx = px0 + 32
    for nme in seen:
        rrect(d, gx, py1 - 104, gx + 72, py1 - 32, 12, outline=(255, 255, 255), width=1.2)
        icon(d, nme, gx + 36, py1 - 68, 40, CARD, 2.2)
        gx += 90
    logo(d, 72, 560, 0.24, CARD)
    spaced(d, (W - 72 - 186, 590), 'IMISOFTS.COM/BLOG', F(600, 12), (150, 165, 190), 2.0)
    _save(img, path_base)
    return pal


if __name__ == '__main__':      # quick preview: python3 ops/img_deal.py /tmp/out
    import sys, json
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/deal'
    os.makedirs(out, exist_ok=True)
    print('render with render_explain / render_cover from a spec block')
