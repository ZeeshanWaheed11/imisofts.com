#!/usr/bin/env python3
"""Article images, style 2: the dark data cover and the clean chart (added 18 Nov 2026, opt-in through image.style == "v2").

Cover (1200x675): dark ink background with a soft accent glow, faint grid and grain; a short headline
(the title before its colon or question mark), one hero number from the spec's key numbers, and a glass
"Key numbers" card with the next three rows. The accent colour follows the spec's qtype, so covers vary.
No full title on the picture (the H1 sits right above it), no "imisofts.com/blog" footer.

Chart (1200x675): white card, rounded bars, slate bars with one accent bar, lighter grid, clear values.

Rendered at 2x and scaled down for clean edges. Pillow only.
"""
import os, re, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get('IMISOFTS_FONTS', os.path.join(HERE, 'fonts'))
W, H, S = 1200, 675, 2
WS, HS = W * S, H * S

ORANGE = (244, 84, 7)
ACCENTS = {   # qtype -> (accent, second glow)
    'cost':   ((249, 115, 22), (236, 72, 153)),
    'legal':  ((59, 130, 246), (20, 184, 166)),
    'change': ((168, 85, 247), (249, 115, 22)),
    'limit':  ((20, 184, 166), (59, 130, 246)),
    'howto':  ((34, 197, 94), (59, 130, 246)),
}
INK0, INK1 = (8, 13, 28), (17, 26, 51)
WHITE = (255, 255, 255); SLATE3 = (203, 213, 225); SLATE4 = (148, 163, 184); SLATE5 = (100, 116, 139)

_F = {}
def F(weight, size):
    k = (weight, size)
    if k not in _F:
        _F[k] = ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-%d.ttf' % weight), size * S)
    return _F[k]

_KEEP = re.compile(u'[^\x20-\x7e\xa0-\xff\u2018\u2019\u201c\u201d\u2026\u20ac\u2122]')
def clean(t):
    t = re.sub(u'\\s*[\u2012\u2013\u2014]\\s*', ', ', (t or ''))
    t = _KEEP.sub('', t)
    return re.sub(r'\s+', ' ', t).strip()

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw * S:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit(d, text, font, maxw):
    if d.textlength(text, font=font) <= maxw * S:
        return text
    while text and d.textlength(text + '\u2026', font=font) > maxw * S:
        text = text[:-1]
    return text.rstrip(' ,;:') + '\u2026'

def P(x, y):
    return (x * S, y * S)

def logo(d, x, top, s, word=WHITE):
    Q = lambda px, py: (x * S + s * S * px, top * S + s * S * py)
    cx, cy = Q(48, 170); r = 18 * s * S
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
    d.polygon([Q(84, 84), Q(136, 84), Q(118, 188), Q(66, 188)], fill=ORANGE)
    d.polygon([Q(146, 84), Q(198, 84), Q(180, 188), Q(128, 188)], fill=ORANGE)
    d.text(Q(200, 188), 'imisofts', font=ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-700.ttf'), int(96 * s * S)), fill=word, anchor='ls')

def short_headline(title, override=None):
    if override:
        return clean(override)
    t = clean(title)
    m = re.match(r'^(.{8,60}?[?:])\s', t)
    if m:
        h = m.group(1).rstrip(':')
        return h
    return t if len(t) <= 48 else t[:48].rsplit(' ', 1)[0]

_NUM = re.compile(r'^((?:[$\u20ac\u00a3]|EUR\s|USD\s)?\s?[\d][\d.,]*\s?(?:%|x|K|M|B|k|bn|million|billion)?)(.*)$')
def split_stat(value):
    v = clean(value)
    m = _NUM.match(v)
    if m and len(m.group(1).strip()) <= 12:
        return m.group(1).strip(), m.group(2).strip()
    return v, ''

_MONTHS = re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d|\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*', re.I)
_NUMERIC = re.compile(r'^(?:[$\u20ac\u00a3]|EUR\s|USD\s|GBP\s)?\s?\d')

def pick_stat(rows):
    """The hero number: the first key-numbers row whose value is a number (not a date); else the first row."""
    for r in rows:
        v = clean(r.get('value', ''))
        if _NUMERIC.match(v) and not _MONTHS.search(v):
            return r
    return rows[0] if rows else None

def stat_parts(value):
    big, rest = split_stat(value)
    if rest.lower().startswith(('to ', 'and ', 'or ', '/', 'x ')) or not rest and len(big) > 14:
        return clean(value), ''
    return big, rest

def _gradient(w, h, c0, c1):
    g = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        g.putpixel((0, y), tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    return g.resize((w, h))

def _glow(base, center, radius, color, alpha):
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = center
    ld.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.55))
    return Image.alpha_composite(base, layer)

def _grain(base, amount=10, seed=7):
    rnd = random.Random(seed)
    small = Image.new('L', (base.width // 4, base.height // 4))
    small.putdata([rnd.randint(0, 255) for _ in range(small.width * small.height)])
    noise = small.resize(base.size).point(lambda p: int(p * amount / 255))
    layer = Image.new('RGBA', base.size, (255, 255, 255, 0))
    layer.putalpha(noise)
    return Image.alpha_composite(base, layer)

def render_cover(path_base, meta):
    im = meta.get('image') or {}
    qtype = meta.get('qtype') or 'howto'
    acc, acc2 = ACCENTS.get(qtype, ACCENTS['howto'])
    rows = [r for r in (meta.get('key_numbers') or {}).get('rows', []) if r.get('label') and r.get('value')]
    stat = im.get('stat') or pick_stat(rows)
    card_rows = [r for r in rows if r is not stat][:3]

    img = _gradient(WS, HS, INK0, INK1).convert('RGBA')
    img = _glow(img, (int(WS * 0.86), int(HS * 0.05)), int(WS * 0.36), acc, 120)
    img = _glow(img, (int(WS * 0.08), int(HS * 1.02)), int(WS * 0.30), acc2, 55)
    # faint grid, stronger near the top right
    grid = Image.new('RGBA', img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(grid)
    step = 56 * S
    for x in range(0, WS, step): gd.line([x, 0, x, HS], fill=(255, 255, 255, 14), width=S)
    for y in range(0, HS, step): gd.line([0, y, WS, y], fill=(255, 255, 255, 14), width=S)
    mask = Image.new('L', img.size, 0); md = ImageDraw.Draw(mask)
    md.ellipse([int(WS * 0.35), int(-HS * 0.6), int(WS * 1.4), int(HS * 1.0)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(120 * S))
    img = Image.composite(Image.alpha_composite(img, grid), img, mask)
    img = _grain(img, 9)

    d = ImageDraw.Draw(img)
    X = 72
    logo(d, X, 52, 0.30)

    # category chip
    cluster = clean(im.get('cluster', '')).upper()[:30]
    cf = F(700, 15)
    y = 150
    if cluster:
        tw = d.textlength(cluster, font=cf); pw, ph = tw + 30 * S + 16 * S, 34 * S
        x0, y0 = X * S, y * S
        ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], radius=ph // 2, fill=acc + (40,), outline=acc + (170,), width=S)
        img = Image.alpha_composite(img, ov); d = ImageDraw.Draw(img)
        d.ellipse([x0 + 15 * S, y0 + ph // 2 - 4 * S, x0 + 23 * S, y0 + ph // 2 + 4 * S], fill=acc)
        d.text((x0 + 31 * S, y0 + ph // 2), cluster, font=cf, fill=WHITE, anchor='lm')
        y += 58

    # short headline
    head = short_headline(meta.get('title', ''), im.get('headline'))
    hf = F(800, 58)
    lines = wrap(d, head, hf, 560)
    if len(lines) > 3:
        hf = F(800, 48); lines = wrap(d, head, hf, 560)
    for ln in lines[:3]:
        d.text((X * S, y * S), ln, font=hf, fill=WHITE)
        y += int(hf.size / S * 1.12)

    # hero number
    if stat:
        big, rest = stat_parts(stat['value'])
        label = clean(stat.get('label', ''))
        if rest:
            label = (rest + ', ' + label) if label else rest
        y += 22
        bf = F(800, 84)
        for size in (84, 72, 60, 52, 44):
            bf = F(800, size)
            if d.textlength(big, font=bf) <= 560 * S:
                break
        # accent gradient text
        tw = int(d.textlength(big, font=bf)) + 4 * S
        th = int(bf.size * 1.25)
        tmask = Image.new('L', (tw, th), 0)
        ImageDraw.Draw(tmask).text((0, 0), big, font=bf, fill=255)
        grad = Image.new('RGBA', (tw, th))
        for xx in range(tw):
            t = xx / max(1, tw - 1)
            c = tuple(int(acc[i] + (255 - acc[i]) * 0.35 * t) for i in range(3))
            ImageDraw.Draw(grad).line([xx, 0, xx, th], fill=c + (255,))
        img.paste(grad, (X * S, y * S), tmask)
        y += int(bf.size / S * 1.08) + 10
        lf = F(500, 19)
        for ln in wrap(d, label, lf, 540)[:2]:
            d.text((X * S, y * S), ln, font=lf, fill=SLATE3)
            y += 27

    # glass card with the next key numbers
    if card_rows:
        cx0, cy0, cw = 700, 132, 432
        rowh = 92
        ch = 64 + rowh * len(card_rows) + 20
        cy0 = max(110, int((H - ch) / 2) + 10)
        # shadow
        sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([cx0 * S, (cy0 + 24) * S, (cx0 + cw) * S, (cy0 + ch + 24) * S], radius=26 * S, fill=(0, 0, 0, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(28 * S))
        img = Image.alpha_composite(img, sh)
        # frosted panel
        box = (cx0 * S, cy0 * S, (cx0 + cw) * S, (cy0 + ch) * S)
        region = img.crop(box).filter(ImageFilter.GaussianBlur(18 * S))
        rmask = Image.new('L', region.size, 0)
        ImageDraw.Draw(rmask).rounded_rectangle([0, 0, region.width - 1, region.height - 1], radius=26 * S, fill=255)
        img.paste(region, box[:2], rmask)
        ov = Image.new('RGBA', img.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle(box, radius=26 * S, fill=(255, 255, 255, 20), outline=(255, 255, 255, 46), width=S)
        for k in range(3):
            od.ellipse([(cx0 + 26 + k * 16) * S, (cy0 + 27) * S, (cx0 + 34 + k * 16) * S, (cy0 + 35) * S], fill=(255, 255, 255, 70))
        od.line([(cx0 + 1) * S, (cy0 + 60) * S, (cx0 + cw - 1) * S, (cy0 + 60) * S], fill=(255, 255, 255, 34), width=S)
        for i in range(len(card_rows) - 1):
            ly = cy0 + 60 + 18 + i * 92 + 92 - 10
            od.line([(cx0 + 26) * S, ly * S, (cx0 + cw - 26) * S, ly * S], fill=(255, 255, 255, 26), width=S)
        img = Image.alpha_composite(img, ov)
        d = ImageDraw.Draw(img)
        kf = F(700, 13)
        d.text(((cx0 + cw - 26) * S, (cy0 + 31) * S), 'KEY NUMBERS', font=kf, fill=SLATE4, anchor='rm')
        ry = cy0 + 60
        lf = F(500, 16); vf = F(700, 24)
        for i, r in enumerate(card_rows):
            top = ry + 18 + i * rowh
            d.rounded_rectangle([(cx0 + 26) * S, (top + 4) * S, (cx0 + 30) * S, (top + 58) * S], radius=2 * S, fill=acc)
            d.text(((cx0 + 44) * S, top * S), fit(d, clean(r['label']), lf, cw - 70), font=lf, fill=SLATE4)
            d.text(((cx0 + 44) * S, (top + 26) * S), fit(d, clean(r['value']), vf, cw - 70), font=vf, fill=WHITE)

    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=86, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
    return path_base + '.webp', path_base + '.jpg'


def _fmt(v, prefix, suffix):
    if isinstance(v, (int, float)) and float(v).is_integer():
        s = '{:,}'.format(int(v))
    else:
        try: s = '{:,.2f}'.format(float(v))
        except Exception: s = str(v)
    return '%s%s%s' % (prefix, s, suffix)

def render_chart(path_base, ch, qtype='howto'):
    acc = ACCENTS.get(qtype, ACCENTS['howto'])[0]
    rows = [(clean(str(r[0])), float(r[1])) for r in ch.get('rows', []) if len(r) >= 2][:9]
    if not rows:
        return None
    prefix, suffix = ch.get('prefix', ''), ch.get('suffix', '')
    hi = ch.get('highlight', 0 if ch.get('highlight') is None else ch.get('highlight'))
    img = Image.new('RGB', (WS, HS), WHITE).convert('RGBA')   # full bleed: the page's figure box is the frame
    d = ImageDraw.Draw(img)
    X = 72
    kf = F(700, 13)
    d.text((X * S, 64 * S), 'DATA', font=kf, fill=acc)
    d.text((X * S, 84 * S), fit(d, clean(ch.get('title', '')), F(800, 34), W - 2 * X), font=F(800, 34), fill=(15, 23, 42))
    y = 132
    sf = F(400, 18)
    for ln in wrap(d, clean(ch.get('subtitle', '')), sf, W - 2 * X)[:2]:
        d.text((X * S, y * S), ln, font=sf, fill=SLATE5); y += 26
    top = y + 22
    bottom = H - 104
    n = len(rows); gap = 16 if n <= 6 else 10
    bh = min(46, int((bottom - top - gap * (n - 1)) / n))
    used = n * bh + (n - 1) * gap
    top = top + max(0, int((bottom - top - used) / 2) - 10)
    lf = F(500, 18); vf = F(700, 19)
    label_w = max(d.textlength(r[0], font=lf) for r in rows) / S
    x0 = int(X + min(label_w, 330) + 22)
    vmax = max(r[1] for r in rows) or 1.0
    value_w = max(d.textlength(_fmt(r[1], prefix, suffix), font=vf) for r in rows) / S
    bar_max = (W - X) - x0 - 16 - value_w
    # light vertical guides
    for k in range(1, 5):
        gx = x0 + bar_max * k / 4
        d.line([gx * S, (top - 8) * S, gx * S, (top + n * (bh + gap) - gap + 8) * S], fill=(241, 245, 249), width=S)
    for i, (lab, val) in enumerate(rows):
        yy = top + i * (bh + gap)
        hot = (i == hi)
        lab_t = fit(d, lab, lf, 330)
        d.text(((x0 - 22) * S, (yy + bh / 2) * S), lab_t, font=lf, fill=(51, 65, 85), anchor='rm')
        w = max(bar_max * val / vmax, 8)
        d.rounded_rectangle([x0 * S, yy * S, (x0 + w) * S, (yy + bh) * S], radius=int(bh / 2) * S, fill=acc if hot else (203, 213, 225))
        d.text(((x0 + w + 14) * S, (yy + bh / 2) * S), _fmt(val, prefix, suffix), font=vf, fill=acc if hot else (15, 23, 42), anchor='lm')
    d.line([X * S, (H - 88) * S, (W - X) * S, (H - 88) * S], fill=(241, 245, 249), width=S)
    src = clean(ch.get('source', ''))
    ff = F(400, 15)
    for k, ln in enumerate(wrap(d, src, ff, W - 2 * X - 200)[:2]):
        d.text((X * S, (H - 74 + k * 20) * S), ln, font=ff, fill=SLATE5)
    logo(d, W - X - 190, H - 80, 0.21, word=(15, 23, 42))
    out = img.convert('RGB').resize((W, H), Image.LANCZOS)
    out.save(path_base + '.webp', 'WEBP', quality=86, method=6)
    out.save(path_base + '.jpg', 'JPEG', quality=88, optimize=True, progressive=True)
    return path_base + '.webp', path_base + '.jpg'


