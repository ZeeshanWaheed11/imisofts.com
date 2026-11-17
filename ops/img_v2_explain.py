#!/usr/bin/env python3
"""imisofts explainer illustrations and preview covers (added 18 Nov 2026, opt-in through image.style == "v2").

Four layouts, each filled from a small block in the spec, so the picture explains the article:
  flow      steps with icons and arrows        ("How a company data license works")
  compare   2 to 4 options with their numbers  ("Whisper vs gpt-transcribe, per minute")
  timeline  3 to 5 dated events                ("Whisper: announced, last day")
  rules     a subject icon and 2 to 4 rule rows with a tick, cross or warning mark

Spec block (example):
  "image": {"style": "explain", "explain": {
      "layout": "flow", "kicker": "How it works", "headline": "How a company data license works",
      "items": [{"icon": "database", "label": "Your records", "note": "SOPs, CRM, tickets"}, ...]}}

Warm paper, soft colour discs behind hand-drawn icons, Inter labels, paper grain. Pillow only.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('IMISOFTS_FONTS', os.path.join(HERE, 'fonts'))
W, H, S = 1200, 675, 2
WS, HS = W * S, H * S

PALETTES = {
    'ember': {'bg': (245, 241, 233), 'ink': (28, 32, 44), 'muted': (98, 104, 118), 'accent': (232, 92, 38),
              'discs': [(246, 199, 172), (224, 210, 182), (204, 214, 196), (238, 214, 200)], 'paper': (253, 251, 246)},
    'sage':  {'bg': (240, 241, 233), 'ink': (30, 36, 34), 'muted': (96, 104, 100), 'accent': (229, 98, 47),
              'discs': [(201, 213, 189), (230, 214, 186), (246, 205, 180), (214, 222, 214)], 'paper': (252, 252, 247)},
    'tide':  {'bg': (236, 240, 243), 'ink': (25, 33, 46), 'muted': (92, 102, 116), 'accent': (229, 98, 47),
              'discs': [(196, 212, 226), (232, 216, 196), (246, 204, 182), (214, 224, 230)], 'paper': (251, 252, 253)},
}

_F = {}
def F(weight, size):
    k = (weight, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-%d.ttf' % weight), int(size * S))
    return _F[k]


# ------------------------------------------------------------------ hand-drawn primitives
def _smooth(pts, n=16):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


class Pen:
    def __init__(self, d, rnd, color, width=3.0):
        self.d, self.rnd, self.color, self.w = d, rnd, color, width

    def _wob(self, pts, amp):
        r = self.rnd
        p1, p2, p3, p4 = (r.uniform(0, 6.28) for _ in range(4))
        out, L, prev = [], 0.0, None
        for (x, y) in pts:
            if prev is not None:
                L += math.hypot(x - prev[0], y - prev[1])
            prev = (x, y)
            out.append((x + amp * (0.65 * math.sin(L / (80 * S) + p1) + 0.35 * math.sin(L / (27 * S) + p2)),
                        y + amp * (0.65 * math.sin(L / (74 * S) + p3) + 0.35 * math.sin(L / (25 * S) + p4))))
        return out

    def line(self, pts, closed=False, width=None, color=None, smooth=True):
        if closed:
            pts = list(pts) + [pts[0]]
        P = [(x * S, y * S) for x, y in pts]
        if smooth and len(P) > 2:
            P = _smooth(P)
        w = int((width or self.w) * S)
        self.d.line(self._wob(P, 1.1 * S), fill=color or self.color, width=w, joint='curve')

    def ring(self, cx, cy, rx, ry=None, n=36, **kw):
        ry = ry or rx
        self.line([(cx + rx * math.cos(2 * math.pi * t / n), cy + ry * math.sin(2 * math.pi * t / n)) for t in range(n)], closed=True, **kw)

    def arc(self, cx, cy, r, a0, a1, n=24, **kw):
        self.line([(cx + r * math.cos(math.radians(a0 + (a1 - a0) * t / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * t / n))) for t in range(n + 1)], **kw)

    def rect(self, x0, y0, x1, y1, r=8, **kw):
        pts = []
        for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for t in range(7):
                a = math.radians(a0 + 90 * t / 6)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        kw.setdefault('smooth', False)
        self.line(pts, closed=True, **kw)


def fill_rect(d, x0, y0, x1, y1, r, color):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=int(r * S), fill=color)


def disc(d, cx, cy, r, color, rnd):
    ph = [rnd.uniform(0, 6.28) for _ in range(3)]
    pts = []
    for i in range(120):
        a = 2 * math.pi * i / 120
        rr = r * (1 + 0.035 * math.sin(2 * a + ph[0]) + 0.025 * math.sin(3 * a + ph[1]) + 0.02 * math.sin(5 * a + ph[2]))
        pts.append(((cx + rr * math.cos(a)) * S, (cy + rr * math.sin(a)) * S))
    d.polygon(pts, fill=color)


# ------------------------------------------------------------------ icons (drawn in a box of about 100 px around cx, cy)
def ic_database(p, d, cx, cy, A):
    for k in range(3):
        y = cy - 30 + k * 26
        fill_rect(d, cx - 36, y, cx + 36, y + 26, 0, p.paper) if False else None
    d.rectangle([(cx - 36) * S, (cy - 34) * S, (cx + 36) * S, (cy + 34) * S], fill=P_CUR['paper'])
    d.ellipse([(cx - 36) * S, (cy + 22) * S, (cx + 36) * S, (cy + 46) * S], fill=P_CUR['paper'])
    d.ellipse([(cx - 36) * S, (cy - 46) * S, (cx + 36) * S, (cy - 22) * S], fill=A)
    p.ring(cx, cy - 34, 36, 12)
    for k in (0, 1):
        y = cy - 8 + k * 26
        p.line([(cx - 36, y), (cx - 18, y + 10), (cx, y + 12), (cx + 18, y + 10), (cx + 36, y)])
    p.line([(cx - 36, cy - 34), (cx - 36, cy + 34)], smooth=False)
    p.line([(cx + 36, cy - 34), (cx + 36, cy + 34)], smooth=False)
    p.line([(cx - 36, cy + 34), (cx - 18, cy + 44), (cx, cy + 46), (cx + 18, cy + 44), (cx + 36, cy + 34)])


def ic_document(p, d, cx, cy, A):
    fill_rect(d, cx - 32, cy - 42, cx + 32, cy + 42, 6, P_CUR['paper'])
    p.line([(cx - 32, cy - 42), (cx + 14, cy - 42), (cx + 32, cy - 24), (cx + 32, cy + 42), (cx - 32, cy + 42)], closed=True, smooth=False)
    p.line([(cx + 14, cy - 42), (cx + 14, cy - 24), (cx + 32, cy - 24)], smooth=False)
    for k in range(4):
        y = cy - 16 + k * 14
        p.line([(cx - 20, y), (cx + (18 if k % 2 else 8), y)], width=2.4, smooth=False)
    fill_rect(d, cx - 20, cy + 26, cx + 2, cy + 32, 3, A)


def ic_shield(p, d, cx, cy, A):
    pts = [(cx, cy - 44), (cx + 36, cy - 30), (cx + 34, cy + 6), (cx + 18, cy + 30), (cx, cy + 44), (cx - 18, cy + 30), (cx - 34, cy + 6), (cx - 36, cy - 30)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=P_CUR['paper'])
    p.line(pts, closed=True)
    p.line([(cx - 14, cy), (cx - 3, cy + 12), (cx + 16, cy - 12)], width=4, color=A, smooth=False)


def ic_lock(p, d, cx, cy, A):
    fill_rect(d, cx - 30, cy - 8, cx + 30, cy + 40, 8, A)
    p.rect(cx - 30, cy - 8, cx + 30, cy + 40, r=8)
    p.arc(cx, cy - 10, 20, 180, 360)
    p.line([(cx - 20, cy - 10), (cx - 20, cy - 8)], smooth=False)
    d.ellipse([(cx - 5) * S, (cy + 8) * S, (cx + 5) * S, (cy + 18) * S], fill=P_CUR['ink'])


def ic_chip(p, d, cx, cy, A):
    fill_rect(d, cx - 30, cy - 30, cx + 30, cy + 30, 8, P_CUR['paper'])
    p.rect(cx - 30, cy - 30, cx + 30, cy + 30, r=8)
    for k in (-16, 0, 16):
        for (x0, y0, x1, y1) in ((cx + k, cy - 30, cx + k, cy - 44), (cx + k, cy + 30, cx + k, cy + 44), (cx - 30, cy + k, cx - 44, cy + k), (cx + 30, cy + k, cx + 44, cy + k)):
            p.line([(x0, y0), (x1, y1)], width=2.6, smooth=False)
    d.text((cx * S, (cy + 1) * S), 'AI', font=F(800, 22), fill=A, anchor='mm')


def ic_building(p, d, cx, cy, A):
    d.polygon([((cx - 44) * S, (cy - 16) * S), (cx * S, (cy - 44) * S), ((cx + 44) * S, (cy - 16) * S)], fill=A)
    p.line([(cx - 44, cy - 16), (cx, cy - 44), (cx + 44, cy - 16)], closed=True, smooth=False)
    for k in (-26, -9, 9, 26):
        fill_rect(d, cx + k - 5, cy - 10, cx + k + 5, cy + 30, 2, P_CUR['paper'])
        p.line([(cx + k - 5, cy - 10), (cx + k - 5, cy + 30)], width=2.4, smooth=False)
        p.line([(cx + k + 5, cy - 10), (cx + k + 5, cy + 30)], width=2.4, smooth=False)
    p.line([(cx - 46, cy + 32), (cx + 46, cy + 32)], smooth=False)
    p.line([(cx - 40, cy + 40), (cx + 40, cy + 40)], smooth=False)


def ic_coin(p, d, cx, cy, A, sym='$'):
    d.ellipse([(cx - 38) * S, (cy - 38) * S, (cx + 38) * S, (cy + 38) * S], fill=A)
    p.ring(cx, cy, 38)
    p.ring(cx, cy, 28, width=2)
    d.text((cx * S, (cy + 1) * S), sym, font=F(800, 30), fill=P_CUR['paper'], anchor='mm')


def ic_envelope(p, d, cx, cy, A):
    fill_rect(d, cx - 44, cy - 30, cx + 44, cy + 30, 6, P_CUR['paper'])
    p.rect(cx - 44, cy - 30, cx + 44, cy + 30, r=6)
    p.line([(cx - 42, cy - 26), (cx, cy + 4), (cx + 42, cy - 26)], smooth=False)
    d.ellipse([(cx + 26) * S, (cy - 46) * S, (cx + 50) * S, (cy - 22) * S], fill=A)


def ic_calendar(p, d, cx, cy, A, text=None):
    fill_rect(d, cx - 40, cy - 34, cx + 40, cy + 40, 8, P_CUR['paper'])
    fill_rect(d, cx - 40, cy - 34, cx + 40, cy - 12, 8, A)
    p.rect(cx - 40, cy - 34, cx + 40, cy + 40, r=8)
    for x in (cx - 20, cx + 20):
        p.line([(x, cy - 44), (x, cy - 26)], width=4, smooth=False)
    if text:
        d.text((cx * S, (cy + 14) * S), text, font=F(800, 20), fill=P_CUR['ink'], anchor='mm')
    else:
        for i in range(3):
            for j in range(2):
                d.ellipse([(cx - 22 + i * 22 - 3) * S, (cy + 2 + j * 18 - 3) * S, (cx - 22 + i * 22 + 3) * S, (cy + 2 + j * 18 + 3) * S], fill=P_CUR['ink'])


def ic_wave(p, d, cx, cy, A):
    d.ellipse([(cx - 44) * S, (cy - 44) * S, (cx + 44) * S, (cy + 44) * S], fill=P_CUR['paper'])
    p.ring(cx, cy, 44)
    hs = [10, 22, 34, 18, 28, 12, 20]
    for i, h in enumerate(hs):
        x = cx - 27 + i * 9
        p.line([(x, cy - h / 2), (x, cy + h / 2)], width=4, color=A if i in (2, 4) else None, smooth=False)


def ic_card(p, d, cx, cy, A):
    fill_rect(d, cx - 46, cy - 30, cx + 46, cy + 30, 8, A)
    p.rect(cx - 46, cy - 30, cx + 46, cy + 30, r=8)
    d.rectangle([(cx - 46) * S, (cy - 16) * S, (cx + 46) * S, (cy - 6) * S], fill=P_CUR['ink'])
    fill_rect(d, cx - 34, cy + 8, cx - 8, cy + 18, 3, P_CUR['paper'])


def ic_key(p, d, cx, cy, A):
    d.ellipse([(cx - 44) * S, (cy - 16) * S, (cx - 12) * S, (cy + 16) * S], fill=A)
    p.ring(cx - 28, cy, 16)
    p.line([(cx - 12, cy), (cx + 44, cy)], width=4, smooth=False)
    p.line([(cx + 30, cy), (cx + 30, cy + 14)], width=4, smooth=False)
    p.line([(cx + 42, cy), (cx + 42, cy + 10)], width=4, smooth=False)


def ic_person(p, d, cx, cy, A):
    d.ellipse([(cx - 16) * S, (cy - 40) * S, (cx + 16) * S, (cy - 8) * S], fill=A)
    p.ring(cx, cy - 24, 16)
    d.pieslice([(cx - 36) * S, (cy) * S, (cx + 36) * S, (cy + 72) * S], 180, 360, fill=P_CUR['paper'])
    p.arc(cx, cy + 36, 36, 180, 360)
    p.line([(cx - 36, cy + 36), (cx + 36, cy + 36)], smooth=False)


def ic_scale(p, d, cx, cy, A):
    p.line([(cx, cy - 40), (cx, cy + 34)], smooth=False)
    p.line([(cx - 40, cy - 26), (cx + 40, cy - 26)], smooth=False)
    p.line([(cx - 24, cy + 38), (cx + 24, cy + 38)], width=4, smooth=False)
    for sx in (-40, 40):
        d.chord([(cx + sx - 20) * S, (cy - 8) * S, (cx + sx + 20) * S, (cy + 22) * S], 0, 180, fill=A if sx < 0 else P_CUR['paper'])
        p.line([(cx + sx, cy - 26), (cx + sx - 20, cy + 6)], width=2.2, smooth=False)
        p.line([(cx + sx, cy - 26), (cx + sx + 20, cy + 6)], width=2.2, smooth=False)
        p.arc(cx + sx, cy + 6, 20, 0, 180, width=2.6)
    d.ellipse([(cx - 6) * S, (cy - 46) * S, (cx + 6) * S, (cy - 34) * S], fill=A)


def ic_chart(p, d, cx, cy, A):
    for i, h in enumerate([24, 40, 58]):
        x = cx - 34 + i * 26
        fill_rect(d, x, cy + 36 - h, x + 18, cy + 36, 3, A if i == 2 else P_CUR['paper'])
        p.rect(x, cy + 36 - h, x + 18, cy + 36, r=3, width=2.4)
    p.line([(cx - 44, cy + 40), (cx + 44, cy + 40)], smooth=False)


def ic_globe(p, d, cx, cy, A):
    d.ellipse([(cx - 40) * S, (cy - 40) * S, (cx + 40) * S, (cy + 40) * S], fill=P_CUR['paper'])
    p.ring(cx, cy, 40)
    p.ring(cx, cy, 16, 40, width=2.4)
    p.line([(cx - 40, cy), (cx + 40, cy)], width=2.4, smooth=False)
    p.line([(cx - 34, cy - 20), (cx + 34, cy - 20)], width=2.2, smooth=False)
    p.line([(cx - 34, cy + 20), (cx + 34, cy + 20)], width=2.2, smooth=False)
    d.ellipse([(cx + 18) * S, (cy - 38) * S, (cx + 38) * S, (cy - 18) * S], fill=A)


def ic_warning(p, d, cx, cy, A):
    pts = [(cx, cy - 40), (cx + 44, cy + 34), (cx - 44, cy + 34)]
    d.polygon([(x * S, y * S) for x, y in pts], fill=A)
    p.line(pts, closed=True, smooth=False)
    d.text((cx * S, (cy + 10) * S), '!', font=F(800, 34), fill=P_CUR['paper'], anchor='mm')


ICONS = {'database': ic_database, 'document': ic_document, 'shield': ic_shield, 'lock': ic_lock, 'chip': ic_chip, 'ai': ic_chip,
         'building': ic_building, 'lab': ic_building, 'coin': ic_coin, 'money': ic_coin, 'envelope': ic_envelope, 'email': ic_envelope,
         'calendar': ic_calendar, 'wave': ic_wave, 'audio': ic_wave, 'card': ic_card, 'key': ic_key, 'person': ic_person,
         'scale': ic_scale, 'law': ic_scale, 'chart': ic_chart, 'globe': ic_globe, 'warning': ic_warning}

P_CUR = {}


def mark(d, p, kind, cx, cy, A):
    """tick, cross or warning mark in a small disc"""
    col = {'yes': (64, 145, 96), 'no': (210, 72, 54), 'warn': A}.get(kind, A)
    d.ellipse([(cx - 18) * S, (cy - 18) * S, (cx + 18) * S, (cy + 18) * S], fill=col)
    pen = Pen(d, p.rnd, P_CUR['paper'], 3.6)
    if kind == 'yes':
        pen.line([(cx - 8, cy), (cx - 2, cy + 7), (cx + 9, cy - 7)], smooth=False)
    elif kind == 'no':
        pen.line([(cx - 7, cy - 7), (cx + 7, cy + 7)], smooth=False); pen.line([(cx + 7, cy - 7), (cx - 7, cy + 7)], smooth=False)
    else:
        d.text((cx * S, (cy + 1) * S), '!', font=F(800, 22), fill=P_CUR['paper'], anchor='mm')


def arrow(p, x0, y0, x1, y1, bend=-22):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + bend
    p.line([(x0, y0), (mx, my), (x1, y1)], width=3.2)
    ang = math.atan2(y1 - my, x1 - mx)
    for da in (2.55, -2.55):
        p.line([(x1, y1), (x1 + 16 * math.cos(ang + da), y1 + 16 * math.sin(ang + da))], width=3.2, smooth=False)


def text_center(d, x, y, t, font, fill, maxw):
    words, lines, cur = t.split(), [], ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=font) <= maxw * S:
            cur = c
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    for i, ln in enumerate(lines[:2]):
        d.text((x * S, (y + i * font.size / S * 1.25) * S), ln, font=font, fill=fill, anchor='ma')
    return len(lines[:2])


def logo(d, x, top, s, word):
    Q = lambda px, py: ((x + s * px) * S, (top + s * py) * S)
    cx, cy = Q(48, 170); r = 18 * s * S
    O = (244, 84, 7)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=O)
    d.polygon([Q(84, 84), Q(136, 84), Q(118, 188), Q(66, 188)], fill=O)
    d.polygon([Q(146, 84), Q(198, 84), Q(180, 188), Q(128, 188)], fill=O)
    d.text(Q(200, 188), 'imisofts', font=ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-700.ttf'), int(96 * s * S)), fill=word, anchor='ls')


# ------------------------------------------------------------------ layouts
def header(d, P, ex):
    k = (ex.get('kicker') or '').upper()
    if k:
        f = F(700, 15)
        d.text((72 * S, 64 * S), k, font=f, fill=P['accent'])
    d.text((72 * S, 88 * S), ex.get('headline', ''), font=F(800, 38), fill=P['ink'])


def lay_flow(d, P, rnd, ex):
    items = ex['items'][:5]
    n = len(items)
    span = 1056
    gap = span / n
    cy = 330
    pen = Pen(d, rnd, P['ink'], 3.2)
    for i, it in enumerate(items):
        cx = 72 + gap * (i + 0.5)
        disc(d, cx, cy, 70, P['discs'][i % len(P['discs'])], rnd)
        A = P['accent'] if i == n - 1 or it.get('hot') else P['ink']
        A = P['accent']
        ICONS.get(it.get('icon', 'document'), ic_document)(pen, d, cx, cy, A)
        if it.get('badge'):
            bf = F(800, 17)
            tw = d.textlength(it['badge'], font=bf) / S + 22
            fill_rect(d, cx + 26, cy - 92, cx + 26 + tw, cy - 62, 15, P['ink'])
            d.text(((cx + 26 + tw / 2) * S, (cy - 77) * S), it['badge'], font=bf, fill=P['paper'], anchor='mm')
        nl = text_center(d, cx, cy + 104, it.get('label', ''), F(700, 22), P['ink'], gap - 24)
        if it.get('note'):
            text_center(d, cx, cy + 104 + nl * 28 + 6, it['note'], F(500, 17), P['muted'], gap - 30)
        if i < n - 1:
            arrow(pen, cx + 80, cy, cx + gap - 80, cy, bend=-10)


def lay_compare(d, P, rnd, ex):
    items = ex['items'][:4]
    n = len(items)
    cw = min(300, (1056 - (n - 1) * 28) / n)
    total = n * cw + (n - 1) * 28
    x0 = (W - total) / 2
    top, bottom = 170, 590
    pen = Pen(d, rnd, P['ink'], 3.0)
    vmax = max((it.get('num') or 0) for it in items) or 1
    for i, it in enumerate(items):
        x = x0 + i * (cw + 28)
        hot = it.get('hot')
        fill_rect(d, x, top, x + cw, bottom, 22, P['paper'])
        pen.rect(x, top, x + cw, bottom, r=22, width=2.6, color=P['accent'] if hot else P['ink'])
        cx = x + cw / 2
        disc(d, cx, top + 86, 56, P['discs'][i % len(P['discs'])], rnd)
        ICONS.get(it.get('icon', 'coin'), ic_coin)(pen, d, cx, top + 86, P['accent'])
        d.text((cx * S, (top + 166) * S), it.get('label', ''), font=F(700, 21), fill=P['ink'], anchor='ma')
        vf = F(800, 44 if len(it.get('value', '')) <= 8 else 34)
        d.text((cx * S, (top + 204) * S), it.get('value', ''), font=vf, fill=P['accent'] if hot else P['ink'], anchor='ma')
        if it.get('unit'):
            d.text((cx * S, (top + 262) * S), it['unit'], font=F(500, 17), fill=P['muted'], anchor='ma')
        if it.get('num') is not None:
            bw = (cw - 60) * it['num'] / vmax
            fill_rect(d, x + 30, bottom - 70, x + 30 + cw - 60, bottom - 52, 9, (232, 228, 220))
            fill_rect(d, x + 30, bottom - 70, x + 30 + max(bw, 18), bottom - 52, 9, P['accent'] if hot else P['ink'])
        if it.get('note'):
            d.text((cx * S, (bottom - 40) * S), it['note'], font=F(600, 16), fill=P['accent'] if hot else P['muted'], anchor='ma')


def lay_timeline(d, P, rnd, ex):
    items = ex['items'][:5]
    n = len(items)
    pen = Pen(d, rnd, P['ink'], 3.2)
    y = 380
    x0, x1 = 190, 1010
    pen.line([(x0 - 30, y), ((x0 + x1) / 2, y - 6), (x1 + 30, y)], width=3.6)
    for i, it in enumerate(items):
        x = x0 + (x1 - x0) * (i / max(1, n - 1))
        hot = it.get('hot')
        disc(d, x, y - 120, 62, P['discs'][i % len(P['discs'])], rnd)
        ICONS.get(it.get('icon', 'calendar'), ic_calendar)(pen, d, x, y - 120, P['accent'])
        d.ellipse([(x - 13) * S, (y - 13) * S, (x + 13) * S, (y + 13) * S], fill=P['accent'] if hot else P['ink'])
        d.text((x * S, (y + 30) * S), it.get('date', ''), font=F(800, 22), fill=P['accent'] if hot else P['ink'], anchor='ma')
        text_center(d, x, y + 64, it.get('label', ''), F(500, 18), P['muted'], (x1 - x0) / max(1, n - 1) - 20)


def lay_rules(d, P, rnd, ex):
    pen = Pen(d, rnd, P['ink'], 3.4)
    cx, cy = 250, 375
    disc(d, cx, cy, 128, P['discs'][0], rnd)
    ic = ICONS.get(ex.get('subject_icon', 'envelope'), ic_envelope)
    # draw the subject icon at twice the size on its own layer
    lay = Image.new('RGBA', (240 * S, 240 * S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ic(Pen(ld, rnd, P['ink'], 2.0), ld, 120, 120, P['accent'])
    lay = lay.resize((int(240 * S * 1.9), int(240 * S * 1.9)), Image.LANCZOS)
    IMG_CUR[0].alpha_composite(lay, (int((cx - 228) * S), int((cy - 228) * S)))
    if ex.get('subject'):
        fill_rect(d, cx - 70, cy + 104, cx + 70, cy + 140, 18, P['ink'])
        d.text((cx * S, (cy + 122) * S), ex['subject'], font=F(700, 18), fill=P['paper'], anchor='mm')
    rows = ex['items'][:4]
    top = 190
    rh = 98
    for i, r in enumerate(rows):
        y = top + i * rh
        fill_rect(d, 470, y, 1128, y + rh - 18, 18, P['paper'])
        mark(d, pen, r.get('mark', 'yes'), 512, y + (rh - 18) / 2, P['accent'])
        d.text((548 * S, (y + 18) * S), r.get('label', ''), font=F(700, 22), fill=P['ink'])
        if r.get('note'):
            d.text((548 * S, (y + 48) * S), r['note'], font=F(500, 17), fill=P['muted'])


LAYOUTS = {'flow': lay_flow, 'compare': lay_compare, 'timeline': lay_timeline, 'rules': lay_rules}
IMG_CUR = [None]


def grain(img, rnd, strength=12):
    small = Image.new('L', (img.width // 3, img.height // 3))
    small.putdata([rnd.randint(128 - strength, 128 + strength) for _ in range(small.width * small.height)])
    return ImageChops.overlay(img, small.resize(img.size, Image.BILINEAR).convert('RGB'))


def render_explain(path_base, slug, ex, palette=None):
    rnd = random.Random(slug)
    pal = palette or ex.get('palette') or rnd.choice(list(PALETTES))
    P = PALETTES[pal]
    P_CUR.clear(); P_CUR.update(P)
    img = Image.new('RGBA', (WS, HS), P['bg'] + (255,))
    IMG_CUR[0] = img
    d = ImageDraw.Draw(img)
    header(d, P, ex)
    LAYOUTS[ex.get('layout', 'flow')](d, P, rnd, ex)
    d = ImageDraw.Draw(img)
    logo(d, W - 72 - 160, 50, 0.18, P['ink'])
    if ex.get('footnote'):
        d.text((72 * S, (H - 40) * S), ex['footnote'], font=F(500, 15), fill=P['muted'])
    out = grain(img.convert('RGB'), rnd).resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=88, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=90, optimize=True, progressive=True)
    return pal


# ------------------------------------------------------------------ preview cover (blog card, social share, Google)
def render_cover(path_base, slug, ex, headline, palette=None):
    """The picture people see before they click: big headline that reads at card size, and the article's
    icons in large colour discs. Same style as the explainer inside the article."""
    global S
    rnd = random.Random(slug + ':cover')
    pal = palette or ex.get('palette') or rnd.choice(list(PALETTES))
    P = PALETTES[pal]
    P_CUR.clear(); P_CUR.update(P)
    img = Image.new('RGBA', (WS, HS), P['bg'] + (255,))
    IMG_CUR[0] = img
    d = ImageDraw.Draw(img)
    # kicker and headline, left
    k = (ex.get('kicker') or '').upper()
    y = 150
    if k:
        f = F(700, 18)
        tw = d.textlength(k, font=f) / S
        fill_rect(d, 72, y, 72 + tw + 36, y + 40, 20, P['ink'])
        d.text(((72 + 18) * S, (y + 20) * S), k, font=f, fill=P['paper'], anchor='lm')
        y += 70
    hf = F(800, 60)
    words, lines, cur = headline.split(), [], ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=hf) <= 560 * S:
            cur = c
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    if len(lines) > 4:
        hf = F(800, 50)
    for ln in lines[:4]:
        d.text((72 * S, y * S), ln, font=hf, fill=P['ink'])
        y += int(hf.size / S * 1.12)
    # icons, right: one big disc and two small ones
    items = ex.get('items', [])
    if ex.get('layout') == 'rules':
        icons = ['scale', ex.get('subject_icon', 'envelope'), 'warning']
    else:
        icons = [it.get('icon', 'document') for it in items] or ['document']
    pick = [icons[-1], icons[0], icons[len(icons) // 2]] if len(icons) >= 3 else (icons + icons + icons)[:3]
    spots = [(905, 340, 168, 2.3), (735, 175, 78, 1.05), (1075, 545, 70, 0.95)]
    for i, ((cx, cy, r, sc), name) in enumerate(zip(spots, pick)):
        disc(d, cx, cy, r, P['discs'][i % len(P['discs'])], rnd)
        S0 = S
        S = S0 * sc          # draw the icon natively at the larger scale (no upscaling, clean edges)
        _F.clear()
        lay = Image.new('RGBA', (int(240 * S), int(240 * S)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        ICONS.get(name, ic_document)(Pen(ld, rnd, P['ink'], 3.0 / max(sc, 1.0) + (0.6 if sc > 1.5 else 0)), ld, 120, 120, P['accent'])
        S = S0
        _F.clear()
        img.alpha_composite(lay, (int((cx - 120 * sc) * S), int((cy - 120 * sc) * S)))
    d = ImageDraw.Draw(img)
    big = ex.get('cover_number')
    if big:
        f = F(800, 30)
        tw = d.textlength(big, font=f) / S
        fill_rect(d, 905 - tw / 2 - 22, 470, 905 + tw / 2 + 22, 524, 27, P['accent'])
        d.text((905 * S, 497 * S), big, font=f, fill=P['paper'], anchor='mm')
    logo(d, 72, 560, 0.24, P['ink'])
    out = grain(img.convert('RGB'), rnd).resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=88, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=90, optimize=True, progressive=True)
    return pal


