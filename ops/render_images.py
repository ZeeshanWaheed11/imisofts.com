#!/usr/bin/env python3
"""
imisofts article images: branded hero card + optional data chart, rendered at build time.

Shared by ops/build_news.py, ops/build_affiliate.py and ops/build_byline.py.

A spec opts in by carrying an "image" object. Specs without it are untouched, so
articles published before 2026-09-26 never change (Zeeshan's decision: new articles only).

    "image": {
      "cluster":  "Cold email laws",                 # pill, top right (<= 28 chars)
      "takeaway": "One plain sentence under the title (<= 120 chars).",
      "alt":      "optional alt text; defaults to the title",
      "stamp":    "optional bottom-right line; defaults to 'Published <Month YYYY>'",
      "chart": {                                      # optional, only when the article has a real table
        "title":    "What a team really pays for monday.com Pro",
        "subtitle": "Annual cost by team size ...",
        "type":     "hbar",                           # v1 supports horizontal bars
        "rows":     [["3 people", 684], ["5 people", 1140]],
        "highlight": 2,                               # optional row index drawn in orange
        "note":     ["The sixth seat adds $1,140 a year,", "five times the $19 seat price."],
        "prefix":   "$", "suffix": "/yr",             # value formatting
        "source":   "Pro plan, annual billing. Source: monday.com pricing page, September 2026.",
        "alt":      "Bar chart of annual monday.com Pro cost by team size",
        "after_heading": "optional heading text; the chart goes right before it"
      }
    }

Outputs (content-hashed so the immutable /assets cache never serves a stale render):
    assets/blog/<slug>/hero-<hash>.webp   in-page image, 1200x675
    assets/blog/<slug>/hero-<hash>.jpg    og:image / twitter:image / schema image (JPEG for social crawlers)
    assets/blog/<slug>/chart-<hash>.webp  optional
    assets/blog/<slug>/chart-<hash>.jpg   optional

Public API used by the builders:
    ensure_images(meta, root) -> dict | None
    apply_images_to_html(html, meta, imgs) -> html
"""
import hashlib, json, os, re, sys, subprocess, datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # GitHub's setup-python image has no Pillow; install once, quietly.
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet', 'pillow'], check=False)
    from PIL import Image, ImageDraw, ImageFont

RENDER_VERSION = '2026-09-26.1'
SITE = 'https://imisofts.com'
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, 'fonts')

W, H = 1200, 675
INK = (15, 23, 42); BODY = (51, 65, 85); MUTED = (100, 116, 139); LINE = (226, 232, 240)
BG = (252, 252, 250); ORANGE = (244, 84, 7); ORANGE_TINT = (255, 243, 236); ORANGE_DEEP = (154, 52, 18)

_FONTS = {}
def F(weight, size):
    key = (weight, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(os.path.join(FONT_DIR, 'Inter-%d.ttf' % weight), size)
    return _FONTS[key]

# Inter's latin subset: keep printable Latin-1, curly quotes, ellipsis, euro, trademark. Dashes become commas
# (the site linter bans them anyway). Anything else is dropped rather than drawn as a box.
_KEEP = re.compile(u'[^\x20-\x7e -ÿ‘’“”…€™]')
def clean(t):
    t = re.sub(u'\\s*[\u2012\u2013\u2014]\\s*', ', ', (t or ''))
    t = _KEEP.sub('', t)
    return re.sub(r'\s+', ' ', t).strip()

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def logo(d, x, top, s):
    """Exact nav-logo geometry from index.html (viewBox 0 0 900 256), scaled by s."""
    P = lambda px, py: (x + s * px, top + s * py)
    cx, cy = P(48, 170); r = 18 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ORANGE)
    d.polygon([P(84, 84), P(136, 84), P(118, 188), P(66, 188)], fill=ORANGE)
    d.polygon([P(146, 84), P(198, 84), P(180, 188), P(128, 188)], fill=ORANGE)
    d.text(P(200, 188), 'imisofts', font=F(700, int(96 * s)), fill=INK, anchor='ls')

def pill(d, right_x, y, text, font, fill, color, padx=18, pady=10):
    tw = d.textlength(text, font=font); h = font.size + pady * 2; w = tw + padx * 2
    x = right_x - w
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=fill)
    d.text((x + padx, y + pady - 1), text, font=font, fill=color)

def _save(img, base):
    """Write WebP (page) and JPEG (social/schema). Returns (webp_path, jpg_path)."""
    webp, jpg = base + '.webp', base + '.jpg'
    img.save(webp, 'WEBP', quality=82, method=6)
    img.save(jpg, 'JPEG', quality=86, optimize=True, progressive=True)
    return webp, jpg

def _month(date_iso):
    try:
        return datetime.date.fromisoformat(date_iso[:10]).strftime('%B %Y')
    except Exception:
        return datetime.date.today().strftime('%B %Y')

# --------------------------------------------------------------------------- hero
def render_hero(path_base, title, cluster, takeaway, stamp):
    img = Image.new('RGB', (W, H), BG)
    # brand motif: the two slanted bars, faint, right side
    motif = Image.new('RGBA', (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(motif)
    s, ox, oy = 2.9, 760, 150
    for pts in ([(84, 84), (136, 84), (118, 188), (66, 188)], [(146, 84), (198, 84), (180, 188), (128, 188)]):
        md.polygon([(ox + s * px, oy + s * py) for px, py in pts], fill=(244, 84, 7, 26))
    img = Image.alpha_composite(img.convert('RGBA'), motif).convert('RGB')
    d = ImageDraw.Draw(img)
    logo(d, 64, 56, 0.34)
    if cluster:
        pill(d, W - 64, 60, clean(cluster).upper()[:28], F(700, 17), ORANGE_TINT, ORANGE_DEEP)
    title = clean(title)
    tf = F(800, 64); lines = wrap(d, title, tf, 760)
    if len(lines) > 3:
        tf = F(800, 56); lines = wrap(d, title, tf, 760)
    if len(lines) > 3:
        tf = F(800, 48); lines = wrap(d, title, tf, 780)
    lines = lines[:4]
    block_h = len(lines) * int(tf.size * 1.15)
    sub_lines = []
    sf = F(400, 26)
    if takeaway:
        sub_lines = wrap(d, clean(takeaway), sf, 760)[:2]
    total = block_h + (18 + len(sub_lines) * int(sf.size * 1.45) if sub_lines else 0)
    y = max(150, int((H - 92 - 150 - total) / 2) + 150)   # vertically centred between header and footer rule
    for ln in lines:
        d.text((64, y), ln, font=tf, fill=INK); y += int(tf.size * 1.15)
    if sub_lines:
        y += 18
        for ln in sub_lines:
            d.text((64, y), ln, font=sf, fill=MUTED); y += int(sf.size * 1.45)
    d.line([64, H - 92, W - 64, H - 92], fill=LINE, width=2)
    bf = F(500, 20)
    d.text((64, H - 66), 'imisofts.com/blog', font=bf, fill=BODY)
    stamp = clean(stamp)
    d.text((W - 64 - d.textlength(stamp, font=bf), H - 66), stamp, font=bf, fill=MUTED)
    return _save(img, path_base)

# --------------------------------------------------------------------------- chart
def _fmt(v, prefix, suffix):
    if isinstance(v, (int, float)) and float(v).is_integer():
        s = '{:,}'.format(int(v))
    else:
        try: s = '{:,.2f}'.format(float(v))
        except Exception: s = str(v)
    return '%s%s%s' % (prefix, s, suffix)

def render_chart(path_base, ch):
    rows = [(clean(str(r[0])), float(r[1])) for r in ch.get('rows', []) if len(r) >= 2]
    if not rows:
        return None
    rows = rows[:9]
    prefix, suffix = ch.get('prefix', ''), ch.get('suffix', '')
    hi = ch.get('highlight', None)
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    d.text((64, 52), clean(ch.get('title', ''))[:70], font=F(800, 40), fill=INK)
    y = 104
    sf = F(400, 22)
    for ln in wrap(d, clean(ch.get('subtitle', '')), sf, 1072)[:2]:
        d.text((64, y), ln, font=sf, fill=MUTED); y += 30
    top = y + 18
    avail = (H - 92 - 24) - top
    n = len(rows)
    gap = 22 if n <= 6 else 14
    bh = min(44, int((avail - gap * (n - 1)) / n))
    lf = F(500, 22); vf = F(700, 22)
    label_w = max(d.textlength(r[0], font=lf) for r in rows)
    x0 = int(64 + label_w + 24)
    vmax = max(r[1] for r in rows) or 1.0
    value_w = max(d.textlength(_fmt(r[1], prefix, suffix), font=vf) for r in rows)
    note = [clean(t) for t in (ch.get('note') or [])][:2]
    af = F(600, 20)
    note_w = max([d.textlength(t, font=af) for t in note] + [0])
    bar_max = (W - 64) - x0 - 14 - value_w - (28 + note_w if note else 0)
    bar_max = max(240, bar_max)
    for i, (lab, val) in enumerate(rows):
        yy = top + i * (bh + gap)
        d.text((x0 - 24 - d.textlength(lab, font=lf), yy + bh / 2 - lf.size / 2 - 2), lab, font=lf, fill=BODY)
        w = bar_max * val / vmax
        hot = (hi is not None and i == hi)
        d.rounded_rectangle([x0, yy, x0 + max(w, 6), yy + bh], radius=6, fill=ORANGE if hot else INK)
        d.text((x0 + w + 14, yy + bh / 2 - vf.size / 2 - 2), _fmt(val, prefix, suffix), font=vf, fill=ORANGE_DEEP if hot else INK)
        if hot and note:
            ax = x0 + w + 14 + d.textlength(_fmt(val, prefix, suffix), font=vf) + 28
            d.line([ax - 16, yy + bh / 2, ax - 4, yy + bh / 2], fill=ORANGE, width=3)
            if len(note) == 2:
                d.text((ax, yy + bh / 2 - af.size - 3), note[0], font=af, fill=ORANGE_DEEP)
                d.text((ax, yy + bh / 2 + 3), note[1], font=af, fill=ORANGE_DEEP)
            else:
                d.text((ax, yy + bh / 2 - af.size / 2 - 2), note[0], font=af, fill=ORANGE_DEEP)
    d.line([x0, top - 12, x0, top + n * (bh + gap) - gap + 12], fill=LINE, width=2)
    d.line([64, H - 92, W - 64, H - 92], fill=LINE, width=2)
    src = clean(ch.get('source', ''))
    ff = F(400, 18)
    logo_w = int(900 * 0.24)
    for k, ln in enumerate(wrap(d, src, ff, W - 64 - 64 - logo_w - 30)[:2]):
        d.text((64, H - 72 + k * 24), ln, font=ff, fill=MUTED)
    logo(d, W - 64 - logo_w, H - 84, 0.24)
    return _save(img, path_base)

# --------------------------------------------------------------------------- orchestration
def _hash(obj):
    return hashlib.sha1(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()[:8]

def ensure_images(meta, root):
    """Render the images a spec asks for (if missing) and return their paths. None when the spec has no image block."""
    im = meta.get('image')
    if not isinstance(im, dict):
        return None
    slug = meta['slug']
    title = meta.get('title', '')
    out_dir = os.path.join(root, 'assets', 'blog', slug)
    os.makedirs(out_dir, exist_ok=True)
    stamp = im.get('stamp') or ('Published ' + _month(meta.get('date', '')))
    hero_inputs = {'v': RENDER_VERSION, 't': title, 'c': im.get('cluster', ''), 'k': im.get('takeaway', ''), 's': stamp}
    hh = _hash(hero_inputs)
    hero_base = os.path.join(out_dir, 'hero-' + hh)
    if not (os.path.exists(hero_base + '.webp') and os.path.exists(hero_base + '.jpg')):
        render_hero(hero_base, title, im.get('cluster', ''), im.get('takeaway', ''), stamp)
    res = {
        'slug': slug,
        'hero_webp': '/assets/blog/%s/hero-%s.webp' % (slug, hh),
        'hero_jpg': '/assets/blog/%s/hero-%s.jpg' % (slug, hh),
        'hero_alt': clean(im.get('alt') or title),
        'hero_w': W, 'hero_h': H,
    }
    ch = im.get('chart')
    if isinstance(ch, dict) and ch.get('rows'):
        chh = _hash({'v': RENDER_VERSION, 'c': {k: v for k, v in ch.items() if k not in ('after_heading', 'alt')}})
        chart_base = os.path.join(out_dir, 'chart-' + chh)
        if not (os.path.exists(chart_base + '.webp') and os.path.exists(chart_base + '.jpg')):
            if render_chart(chart_base, ch) is None:
                ch = None
        if ch:
            res.update({
                'chart_webp': '/assets/blog/%s/chart-%s.webp' % (slug, chh),
                'chart_jpg': '/assets/blog/%s/chart-%s.jpg' % (slug, chh),
                'chart_alt': clean(ch.get('alt') or ch.get('title') or 'Chart'),
                'chart_caption': clean(ch.get('source', '')),
                'chart_after': clean(ch.get('after_heading', '')),
            })
    return res

def _attr(t):
    return (t or '').replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')

def hero_figure(imgs):
    return ('<figure class="post-hero" style="margin:0 0 8px">'
            '<img src="%s" width="%d" height="%d" alt="%s" loading="eager" fetchpriority="high" decoding="async">'
            '</figure>') % (imgs['hero_webp'], imgs['hero_w'], imgs['hero_h'], _attr(imgs['hero_alt']))

def chart_figure(imgs):
    cap = ('<figcaption style="font-size:13px;line-height:1.5;color:#64748b;margin:-12px 0 24px">%s</figcaption>' % _attr(imgs['chart_caption'])) if imgs.get('chart_caption') else ''
    return ('<figure class="post-chart" style="margin:0">'
            '<img src="%s" width="%d" height="%d" alt="%s" loading="lazy" decoding="async">%s'
            '</figure>') % (imgs['chart_webp'], W, H, _attr(imgs['chart_alt']), cap)

_HEADING_RX = re.compile(r'(<p><strong>[^<]{3,70}</strong></p>|<h2\b[^>]*>)')

def apply_images_to_html(html, meta, imgs):
    """Insert the figures and point og:image, twitter:image and the Article schema at the hero. Idempotent."""
    if not imgs or 'class="post-hero"' in html:
        return html
    hero_abs = SITE + imgs['hero_jpg']
    # 1) social tags
    html = re.sub(r'(<meta property="og:image" content=")[^"]*(")', lambda m: m.group(1) + hero_abs + m.group(2), html, count=1)
    html = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")', lambda m: m.group(1) + hero_abs + m.group(2), html, count=1)
    if 'property="og:image:width"' not in html:
        extra = ('<meta property="og:image:width" content="%d">\n<meta property="og:image:height" content="%d">\n'
                 '<meta property="og:image:alt" content="%s">\n') % (imgs['hero_w'], imgs['hero_h'], _attr(imgs['hero_alt']))
        html = re.sub(r'(<meta property="og:image" content="[^"]*">\n?)', lambda m: m.group(1) + extra, html, count=1)
    # 2) schema image on the article object
    def _ld(m):
        try:
            o = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        objs = o if isinstance(o, list) else ([o] if '@graph' not in o else o['@graph'])
        touched = False
        for node in objs:
            if isinstance(node, dict) and node.get('@type') in ('NewsArticle', 'Article', 'BlogPosting'):
                imgs_list = [hero_abs]
                if imgs.get('chart_jpg'): imgs_list.append(SITE + imgs['chart_jpg'])
                node['image'] = imgs_list
                touched = True
        if not touched:
            return m.group(0)
        return '<script type="application/ld+json">\n' + json.dumps(o, indent=1, ensure_ascii=False) + '\n</script>'
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', _ld, html, flags=re.S)
    # 3) hero after the first real paragraph of the article (skip the affiliate disclosure)
    a = html.find('<article class="article-content">')
    if a < 0:
        return html
    end = html.find('</article>', a)
    pos = a
    while True:
        p_open = html.find('<p', pos)
        if p_open < 0 or p_open > end:
            return html
        p_close = html.find('</p>', p_open)
        if p_close < 0 or p_close > end:
            return html
        if 'affiliate-disclosure' not in html[p_open:p_close]:
            break
        pos = p_close + 4
    ins = p_close + 4
    html = html[:ins] + '\n' + hero_figure(imgs) + '\n' + html[ins:]
    # 4) optional chart: before the named heading, else before the second heading, else before the CTA banner
    if imgs.get('chart_webp'):
        a = html.find('<article class="article-content">'); end = html.find('</article>', a)
        body = html[a:end]
        target = -1
        if imgs.get('chart_after'):
            want = imgs['chart_after'].lower()
            for m in _HEADING_RX.finditer(body):
                seg = body[m.start(): body.find('</', m.start()) + 40]
                if want in re.sub(r'<[^>]+>', '', seg).lower():
                    target = m.start(); break
        if target < 0:
            heads = [m.start() for m in _HEADING_RX.finditer(body)]
            if len(heads) >= 2: target = heads[1]
        if target < 0:
            c = body.find('<div class="blog-cta-banner">')
            target = c if c >= 0 else -1
        if target >= 0:
            html = html[:a + target] + chart_figure(imgs) + '\n' + html[a + target:]
    return html

if __name__ == '__main__':
    # Manual check:  python3 ops/render_images.py content/news/<slug>.json
    root = os.path.dirname(HERE)
    for spec in sys.argv[1:]:
        meta = json.load(open(spec, encoding='utf-8'))
        print(json.dumps(ensure_images(meta, root), indent=1))
