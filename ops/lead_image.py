#!/usr/bin/env python3
"""Real lead image for NEW news articles (template 2). Added 2026-11-14 (SEO audit, item B2).

Where the picture comes from, in this order:
  1. a file next to the spec: content/news/<slug>.lead.png (or .jpg, .jpeg, .webp), with its words in
     the spec: "lead": {"alt": "...", "caption": "...", "credit": "...", "fit": "contain" or "cover"};
  2. the article's own data chart, when the spec has one (image.chart);
  3. nothing: the article keeps the text card, exactly as before.

What is written: assets/blog/<slug>/lead-<hash>-16x9.jpg (1200x675), -4x3.jpg (1200x900),
-1x1.jpg (1200x1200) and lead-<hash>-16x9.webp for the page. The hash comes from the picture and the
settings, so a rebuild writes nothing new and the page stays byte for byte the same.
Pillow is the only dependency (the publish workflow installs it).
"""
import hashlib, os, re

VERSION = '2026-11-14.1'
SITE = 'https://imisofts.com'
SHAPES = (('16x9', 1200, 675), ('4x3', 1200, 900), ('1x1', 1200, 1200))
EXTS = ('.png', '.jpg', '.jpeg', '.webp')
_CHART_RX = re.compile(r'<figure class="post-chart"[^>]*><img src="(/assets/blog/[^"]+/chart-[0-9a-f]+)\.webp"[^>]*>(?:<figcaption[^>]*>(.*?)</figcaption>)?</figure>\n?', re.S)


def source_file(slug, root):
    base = os.path.join(root, 'content', 'news', slug + '.lead')
    for e in EXTS:
        if os.path.exists(base + e):
            return base + e
    return None


def _fit(im, w, h, fit):
    from PIL import Image, ImageFilter
    sw, sh = im.size
    k = max(w / sw, h / sh)
    big = im.resize((max(w, round(sw * k)), max(h, round(sh * k))), Image.LANCZOS)
    x, y = (big.width - w) // 2, (big.height - h) // 2
    cover = big.crop((x, y, x + w, y + h))
    if fit == 'cover':
        return cover
    # contain: the whole picture, on a soft backdrop made from the picture itself
    back = Image.blend(cover.filter(ImageFilter.GaussianBlur(30)), Image.new('RGB', (w, h), (248, 249, 251)), 0.6)
    k = min(w / sw, h / sh)
    fore = im.resize((max(1, round(sw * k)), max(1, round(sh * k))), Image.LANCZOS)
    back.paste(fore, ((w - fore.width) // 2, (h - fore.height) // 2))
    return back


def ensure(meta, root, html=''):
    """Returns the lead picture for this article as a dict, or None when it has none."""
    slug = meta['slug']
    spec = meta.get('lead') if isinstance(meta.get('lead'), dict) else {}
    src = source_file(slug, root)
    kind, alt, caption, credit, fit = 'file', spec.get('alt') or meta.get('title', ''), spec.get('caption', ''), spec.get('credit', ''), spec.get('fit', 'contain')
    if not src:
        m = _CHART_RX.search(html or '')
        if not m:
            return None
        src = os.path.join(root, m.group(1).lstrip('/') + '.jpg')
        if not os.path.exists(src):
            return None
        ch = (meta.get('image') or {}).get('chart') or {}
        kind, alt, caption, credit, fit = 'chart', ch.get('alt') or ch.get('title') or meta.get('title', ''), ch.get('source', ''), '', 'contain'
    fit = 'cover' if fit == 'cover' else 'contain'
    data = open(src, 'rb').read()
    hh = hashlib.sha1((VERSION + '|' + fit + '|').encode() + data).hexdigest()[:10]
    out_dir = os.path.join(root, 'assets', 'blog', slug)
    web = '/assets/blog/%s/lead-%s' % (slug, hh)
    todo = [s for s in SHAPES if not os.path.exists(os.path.join(out_dir, 'lead-%s-%s.jpg' % (hh, s[0])))]
    if todo or not os.path.exists(os.path.join(out_dir, 'lead-%s-16x9.webp' % hh)):
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(data))
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA'); flat = Image.new('RGB', im.size, (255, 255, 255)); flat.paste(im, mask=im.split()[-1]); im = flat
        else:
            im = im.convert('RGB')
        os.makedirs(out_dir, exist_ok=True)
        for name, w, h in SHAPES:
            pic = _fit(im, w, h, fit)
            pic.save(os.path.join(out_dir, 'lead-%s-%s.jpg' % (hh, name)), 'JPEG', quality=86, optimize=True)
            if name == '16x9':
                pic.save(os.path.join(out_dir, 'lead-%s-16x9.webp' % hh), 'WEBP', quality=82, method=6)
    return {'kind': kind, 'alt': alt, 'caption': caption, 'credit': credit, 'w': 1200, 'h': 675,
            'webp16': web + '-16x9.webp', 'jpg16': web + '-16x9.jpg', 'jpg43': web + '-4x3.jpg', 'jpg11': web + '-1x1.jpg'}


def strip_chart(html):
    """Remove the mid-article chart figure (used when the chart has become the lead picture)."""
    return _CHART_RX.sub('', html, count=1)
