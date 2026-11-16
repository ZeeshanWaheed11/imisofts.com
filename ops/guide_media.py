#!/usr/bin/env python3
"""Real lead picture and in-body figures for NEW guides (content/affiliate). Added 2026-11-17 for the GTA 6 desk.

Opt-in only, so every guide published before this builds byte for byte the same:
  * lead picture: the spec has "lead": {"alt", "caption", "credit", "fit"} AND a file
    content/affiliate/<slug>.lead.png (or .jpg, .jpeg, .webp). It replaces the text card at the top, and
    og:image, twitter:image and the Article schema point to it in three shapes (ops/lead_image.py).
  * figures: the body holds <figure class="post-figure"><img data-file="NAME" alt="..."><figcaption>...</figcaption></figure>
    and the file content/affiliate/<slug>.NAME.png (or .jpg, .jpeg, .webp) sits next to the spec. The build writes
    assets/blog/<slug>/NAME-<hash>.webp (at most 1200 px wide) and fills in src, width and height.
    A figure whose file is missing is removed, so a page never shows a broken image.
The hash comes from the picture and the settings, so a rebuild writes nothing new.
"""
import hashlib, os, re

VERSION = '2026-11-17.1'
SITE = 'https://imisofts.com'
EXTS = ('.png', '.jpg', '.jpeg', '.webp')
MAXW = 1200
_FIG_RX = re.compile(r'<figure\b[^>]*>(?:(?!</figure>).)*?<img\b[^>]*\bdata-file="([a-z0-9-]{1,40})"[^>]*>(?:(?!</figure>).)*?</figure>', re.S)
_IMG_RX = re.compile(r'<img\b[^>]*\bdata-file="([a-z0-9-]{1,40})"[^>]*>')


def _attr(t):
    return (t or '').replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')


def _esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _file(root, slug, name):
    base = os.path.join(root, 'content', 'affiliate', '%s.%s' % (slug, name))
    for e in EXTS:
        if os.path.exists(base + e):
            return base + e
    return None


def _lead(html, meta, root):
    if not isinstance(meta.get('lead'), dict):
        return html
    import lead_image as LI
    if not LI.source_file(meta['slug'], root, 'affiliate'):
        print('lead image skipped for %s: no content/affiliate/%s.lead file' % (meta['slug'], meta['slug']))
        return html
    lead = LI.ensure(meta, root, html, 'affiliate')
    if not lead:
        return html
    cap = ' '.join(x for x in (lead['caption'].strip(), ('Credit: ' + lead['credit'].strip()) if lead['credit'].strip() else '') if x)
    fig = ('<figure class="post-hero post-lead" style="margin:0 0 8px">'
           '<img src="%s" width="%d" height="%d" alt="%s" loading="eager" fetchpriority="high" decoding="async">%s</figure>'
           % (lead['webp16'], lead['w'], lead['h'], _attr(lead['alt']),
              ('<figcaption style="font-size:13px;line-height:1.5;color:#64748b;margin:8px 0 16px">%s</figcaption>' % _esc(cap)) if cap else ''))
    html, n = re.subn(r'<figure class="post-hero"[^>]*>.*?</figure>', lambda m: fig, html, count=1, flags=re.S)
    if not n:
        a = html.find('<article class="article-content">'); p = html.find('</p>', a)
        if a < 0 or p < 0:
            return html
        html = html[:p + 4] + '\n' + fig + '\n' + html[p + 4:]
    url = SITE + lead['jpg16']
    for rx in (r'(<meta property="og:image" content=")[^"]*(")', r'(<meta name="twitter:image" content=")[^"]*(")'):
        html = re.sub(rx, lambda m: m.group(1) + url + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")', lambda m: m.group(1) + _attr(lead['alt']) + m.group(2), html, count=1)
    shapes = [SITE + lead['jpg16'], SITE + lead['jpg43'], SITE + lead['jpg11']]

    def _ld(m):
        import json
        try:
            o = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if not isinstance(o, dict) or o.get('@type') not in ('Article', 'NewsArticle', 'BlogPosting'):
            return m.group(0)
        old = o.get('image') if isinstance(o.get('image'), list) else []
        o['image'] = shapes + [u for u in old if '/chart-' in str(u)]
        return '<script type="application/ld+json">\n' + json.dumps(o, indent=1, ensure_ascii=False) + '\n</script>'
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', _ld, html, flags=re.S)
    print('lead image: %s' % lead['jpg16'])
    return html


def _figures(html, meta, root):
    if 'data-file="' not in html:
        return html
    slug = meta['slug']
    out_dir = os.path.join(root, 'assets', 'blog', slug)

    def one_img(m):
        name = m.group(1)
        src = _file(root, slug, name)
        if not src:
            return None
        data = open(src, 'rb').read()
        hh = hashlib.sha1((VERSION + '|').encode() + data).hexdigest()[:10]
        rel = '/assets/blog/%s/%s-%s.webp' % (slug, name, hh)
        path = os.path.join(root, rel.lstrip('/'))
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(data))
        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGBA'); flat = Image.new('RGB', im.size, (255, 255, 255)); flat.paste(im, mask=im.split()[-1]); im = flat
        else:
            im = im.convert('RGB')
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        if not os.path.exists(path):
            os.makedirs(out_dir, exist_ok=True)
            im.save(path, 'WEBP', quality=84, method=6)
        alt = re.search(r'\balt="([^"]*)"', m.group(0))
        return ('<img src="%s" width="%d" height="%d" alt="%s" loading="lazy" decoding="async" '
                'style="width:100%%;height:auto;border-radius:14px;display:block">' % (rel, im.width, im.height, alt.group(1) if alt else ''))

    def one_fig(m):
        img = _IMG_RX.search(m.group(0))
        new_img = one_img(img)
        if not new_img:
            print('figure skipped for %s: no content/affiliate/%s.%s file' % (slug, slug, img.group(1)))
            return ''
        fig = m.group(0).replace(img.group(0), new_img, 1)
        fig = re.sub(r'<figure\b[^>]*>', '<figure class="post-figure" style="margin:28px 0">', fig, count=1)
        fig = re.sub(r'<figcaption\b[^>]*>', '<figcaption style="font-size:13px;line-height:1.5;color:#64748b;margin:8px 0 0">', fig)
        print('figure: %s' % img.group(1))
        return fig
    a = html.find('<article class="article-content">'); b = html.find('</article>', a)
    if a < 0 or b < 0:
        return html
    body = _FIG_RX.sub(one_fig, html[a:b])
    return html[:a] + body + html[b:]


def apply(html, meta, root):
    """Lead picture and figures for a guide. Returns the page unchanged when the spec uses neither."""
    html = _lead(html, meta, root)
    return _figures(html, meta, root)
