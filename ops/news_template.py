#!/usr/bin/env python3
"""News template 2 for NEW news articles. Added 2026-11-14 (SEO audit, items A2 and B1 to B5).

Applies only to an article whose page does not exist yet, or whose page already carries the marker
data-news-template="2". Every older page keeps the old template, byte for byte.

What a template 2 article gets:
  - markup: author and editor, publisher tied to the company entity (@id) with the real logo,
    isAccessibleForFree, inLanguage, optional "about" from the spec;
  - a byline block (see BYLINE) whose name links to the newsdesk section, /newsdesk/;
  - after the body: Related coverage (three stories, linked by their exact titles) and one small
    "About this article" box (who wrote it, who edits it, that imisofts sells services, how to
    report an error), in place of the sales banner;
  - the sidebar without the packages card.
The article text itself is not changed. Phone layout (tables, long words) is handled for every
article by the phone rules at the end of /blog/blog.css.
Related coverage is chosen once, on the first build, and read back from the page on a rebuild.

Added later on 2026-11-14 (audit items B2, A3, the rest of A2 and B4, and the link rule C5):
  - a real lead picture in place of the text card, when the article has one: a file next to the
    spec (content/news/<slug>.lead.png) or its own data chart. Three shapes for the markup, and the
    share tags point to it (ops/lead_image.py);
  - "Updated" and "Correction" notes: the spec lists what changed ("updates"), the builder stamps
    each note once from its own clock, shows it at the top of the article and beside the publish
    time, and moves dateModified and the sitemap lastmod. A rebuild never moves a stamp;
  - the beat: breadcrumb Home / Newsdesk / beat, the category tag links the beat page, and the
    markup names the beat as the section;
  - related coverage for a brand-new article prefers related older stories that no other article
    links to yet.
"""
import glob, hashlib, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = 'https://imisofts.com'
MARK = 'data-news-template="2"'
BYLINE = 'newsdesk'          # 'newsdesk' = "imisofts Newsdesk, Editor: Zeeshan Waheed"; 'founder' = "Zeeshan Waheed"
AUTHOR_URL = SITE + '/author/zeeshan-waheed/'
ORG_ID = SITE + '/#organization'
PERSON_ID = AUTHOR_URL + '#person'
NEWSDESK_URL = SITE + '/newsdesk/'          # the newsdesk section (ops/build_newsdesk.py)
NEWSDESK_ID = NEWSDESK_URL + '#newsdesk'
LOGO = {"@type": "ImageObject", "url": SITE + "/favicon-512.png", "width": 512, "height": 512}
_LABEL = 'font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#98A2B3'
ABOUT = ('<aside class="about-this-article" ' + MARK + ' style="margin:24px 0 8px;padding:16px 18px;border:1px solid #EAECF0;'
         'border-radius:12px;background:#FCFCFD;font-size:14px;line-height:1.65;color:#475467">'
         '<div style="' + _LABEL + ';margin-bottom:6px">About this article</div>'
         'Written by imisofts Newsdesk from the primary sources linked above. Editor: Zeeshan Waheed. '
         'imisofts is an agency and sells services related to the topics it covers, including any service linked here. '
         '<a href="/newsdesk/corrections/" style="color:#475467;text-decoration:underline">Report an error</a>.</aside>')
_REL_RX = re.compile(r'<section class="related-coverage".*?</section>', re.S)


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def attr(t):
    return esc(t).replace('"', '&quot;')


def beat(meta):
    """(slug, name) of the article's beat, or (None, None). The spec names it ("beat"); without it the
    newsdesk's own guess is used, so the breadcrumb and the newsdesk lists always agree."""
    try:
        import build_newsdesk as ND
        b = ND.beat_for(meta)
        return (b, ND.bname[b]) if b else (None, None)
    except Exception:
        return (None, None)


def wants(out_path):
    """True for a page that does not exist yet or already uses template 2."""
    if not os.path.exists(out_path):
        return True
    try:
        return MARK in open(out_path, encoding='utf-8').read()
    except OSError:
        return False


_STOP = set('with from that this what when your have will they their about into over under than then them more most make made does news guide best 2025 2026 2027 price pricing cost costs'.split())


def _words(o):
    """Topic words of a spec: title and keywords, lower case, four letters or more, minus filler."""
    text = (str(o.get('title', '')) + ' ' + str(o.get('keywords', ''))).lower()
    return set(w for w in re.findall(r'[a-z0-9]{4,}', text) if w not in _STOP)


_INBOUND = {}


def _inbound(root):
    """slug -> how many other articles link to it inside their text. Read once per run, and only when a
    brand-new article needs it."""
    if _INBOUND.get('//done'):
        return _INBOUND
    rx = re.compile(r'href="(?:https://imisofts\.com)?/blog/([a-z0-9-]+)/?"')
    for f in glob.glob(os.path.join(root, 'blog', '*', 'index.html')):
        me = os.path.basename(os.path.dirname(f))
        try:
            h = open(f, encoding='utf-8').read()
        except OSError:
            continue
        a = h.find('<article class="article-content">'); b = h.find('</article>', a)
        if a < 0 or b < 0:
            continue
        for s in set(rx.findall(h[a:b])):
            if s != me:
                _INBOUND[s] = _INBOUND.get(s, 0) + 1
    _INBOUND['//done'] = True
    return _INBOUND


def related_block(meta, root):
    out = os.path.join(root, 'blog', meta['slug'], 'index.html')
    if os.path.exists(out):                                      # rebuild: keep the block chosen on the first build
        m = _REL_RX.search(open(out, encoding='utf-8').read())
        if m:
            return m.group(0)
    mine = str((meta.get('image') or {}).get('cluster', '')).strip().lower()
    my_words = _words(meta)
    cands = []
    for f in glob.glob(os.path.join(root, 'content', 'news', '*.json')):
        try:
            o = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        if o.get('slug') and o.get('slug') != meta['slug'] and o.get('title'):
            cl = str((o.get('image') or {}).get('cluster', '')).strip().lower()
            score = (3 if (mine and cl == mine) else 0) + len(my_words & _words(o))
            cands.append((score, str(o.get('date', '')), str(o.get('time', '')), o['slug'], o['title']))
    cands.sort(key=lambda c: (c[0], c[1], c[2], c[3]), reverse=True)
    if not cands:
        return ''
    rel = [c for c in cands if c[0] > 0]
    related = len(rel[:3]) >= 2                                  # an honest label: "related" only when it is
    head = 'Related coverage' if related else 'Latest from the newsdesk'
    if related:
        # the closest story first, then up to two clearly related older stories (two shared topic words or the
        # same cluster) that no other article links to yet
        inbound = _inbound(root)
        picks = rel[:1] + [c for c in rel[1:] if c[0] >= 2 and not inbound.get(c[3])][:2]
        for c in rel[1:] + cands:
            if len(picks) >= 3:
                break
            if c not in picks:
                picks.append(c)
    else:
        picks = sorted(cands, key=lambda c: (c[1], c[2], c[3]), reverse=True)[:3]
    link = 'color:#101828;font-weight:500;text-decoration:none;line-height:1.45;display:block'
    lis = '\n'.join('<li style="margin:0;padding:12px 0;border-bottom:1px solid #F2F4F7"><a href="/blog/%s/" style="%s">%s</a></li>'
                    % (s, link, esc(t)) for _, _, _, s, t in picks)
    return ('<section class="related-coverage" style="margin:36px 0 0;padding-top:22px;border-top:1px solid #EAECF0">\n'
            '<div style="%s;margin-bottom:4px">%s</div>\n<ul style="list-style:none;margin:0;padding:0">\n%s\n</ul>\n</section>') % (_LABEL, head, lis)


def after_body(meta, root):
    """Everything that follows the article text and precedes the FAQ."""
    return '\n'.join(p for p in (related_block(meta, root), ABOUT) if p)


def _markup(html, meta, lead=None):
    bslug, bname = beat(meta)
    dump = lambda o: '<script type="application/ld+json">\n' + json.dumps(o, indent=1, ensure_ascii=False) + '\n</script>'

    def repl(m):
        try:
            o = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if isinstance(o, dict) and o.get('@type') == 'BreadcrumbList':
            trail = [('Home', SITE + '/'), ('Newsdesk', NEWSDESK_URL)] + ([(bname, NEWSDESK_URL + bslug + '/')] if bslug else [])
            trail.append((meta['title'], '%s/blog/%s/' % (SITE, meta['slug'])))
            o['itemListElement'] = [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(trail)]
            return dump(o)
        if not (isinstance(o, dict) and o.get('@type') == 'NewsArticle'):
            return m.group(0)
        o['articleSection'] = bname or 'News'
        if lead:
            old = o.get('image') if isinstance(o.get('image'), list) else []
            keep_chart = [u for u in old if '/chart-' in str(u)] if lead['kind'] == 'file' else []
            o['image'] = [SITE + lead['jpg16'], SITE + lead['jpg43'], SITE + lead['jpg11']] + keep_chart
        if meta.get('_upd'):
            o['dateModified'] = max(t for t, _, _ in meta['_upd'])
        person = {"@type": "Person", "@id": PERSON_ID, "name": "Zeeshan Waheed", "url": AUTHOR_URL}
        if BYLINE == 'newsdesk':
            o['author'] = {"@type": "Organization", "@id": NEWSDESK_ID, "name": "imisofts Newsdesk", "url": NEWSDESK_URL,
                           "parentOrganization": {"@id": ORG_ID}}
            o['editor'] = person
        else:
            o['author'] = person
        o['publisher'] = {"@type": "Organization", "@id": ORG_ID, "name": "imisofts", "url": SITE + "/", "logo": LOGO}
        o['publishingPrinciples'] = NEWSDESK_URL + 'editorial-standards/'
        o['isAccessibleForFree'] = True
        o['inLanguage'] = 'en'
        ab = meta.get('about')
        if isinstance(ab, list) and ab:                           # optional spec field: [{"name": ..., "sameAs": ...}, ...]
            o['about'] = [dict({"@type": "Thing"}, **{k: v for k, v in a.items() if k in ('name', 'sameAs', '@type')})
                          for a in ab if isinstance(a, dict) and a.get('name')]
        return dump(o)
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, html, flags=re.S)


def _byline(html):
    if BYLINE != 'newsdesk':
        return html
    rx = re.compile(r'<a href="/author/zeeshan-waheed/"([^>]*)>Zeeshan Waheed</a>')
    m = rx.search(html)
    if not m:
        return html
    new = ('<a href="/newsdesk/" style="font-weight:500;color:inherit;text-decoration:none">imisofts Newsdesk</a> <span style="color:#98A2B3">&middot;</span> Editor: '
           '<a href="/author/zeeshan-waheed/"%s>Zeeshan Waheed</a>') % m.group(1)
    html = html[:m.start()] + new + html[m.end():]
    return re.sub(r'(<meta property="article:author" content=")[^"]*(")', lambda x: x.group(1) + 'imisofts Newsdesk' + x.group(2), html, count=1)


_CRUMB_RX = re.compile(r'(<nav class="breadcrumbs" aria-label="Breadcrumb">\s*<a href="/">Home</a><span>/</span>)'
                       r'<a href="/blog/">Blog</a><span>/</span><a href="/blog/\?cat=industry-news">Industry News</a>(<span>/</span>)')


def _beat_html(html, meta):
    """Breadcrumb and category tag lead to the newsdesk and the beat page."""
    bslug, bname = beat(meta)
    trail = '<a href="/newsdesk/">Newsdesk</a>' + (('<span>/</span><a href="/newsdesk/%s/">%s</a>' % (bslug, esc(bname))) if bslug else '')
    html = _CRUMB_RX.sub(lambda m: m.group(1) + trail + m.group(2), html, count=1)
    tag = ('<a href="/newsdesk/%s/" class="category-tag">%s</a>' % (bslug, esc(bname))) if bslug else '<a href="/newsdesk/" class="category-tag">News</a>'
    return html.replace('<a href="/blog/?cat=industry-news" class="category-tag">Industry News</a>', tag, 1)


def _lead_html(html, meta):
    """Swap the text card for the article's real lead picture, when it has one. Returns (html, lead or None)."""
    try:
        import lead_image as LI
        lead = LI.ensure(meta, ROOT, html)
    except Exception as e:
        print('lead image skipped for %s: %s' % (meta.get('slug', '?'), e))
        return html, None
    if not lead:
        return html, None
    cap = ' '.join(x for x in (lead['caption'].strip(), ('Credit: ' + lead['credit'].strip()) if lead['credit'].strip() else '') if x)
    fig = ('<figure class="post-hero post-lead" style="margin:0 0 8px">'
           '<img src="%s" width="%d" height="%d" alt="%s" loading="eager" fetchpriority="high" decoding="async">%s</figure>'
           % (lead['webp16'], lead['w'], lead['h'], attr(lead['alt']),
              ('<figcaption style="font-size:13px;line-height:1.5;color:#64748b;margin:8px 0 16px">%s</figcaption>' % esc(cap)) if cap else ''))
    if lead['kind'] == 'chart':
        html = LI.strip_chart(html)                              # the chart is shown once, as the lead
    html, n = re.subn(r'<figure class="post-hero"[^>]*>.*?</figure>', lambda m: fig, html, count=1, flags=re.S)
    if not n:                                                    # no text card on the page: after the first paragraph
        a = html.find('<article class="article-content">'); p = html.find('</p>', a)
        if a < 0 or p < 0:
            return html, None
        html = html[:p + 4] + '\n' + fig + '\n' + html[p + 4:]
    url = SITE + lead['jpg16']
    for rx in (r'(<meta property="og:image" content=")[^"]*(")', r'(<meta name="twitter:image" content=")[^"]*(")'):
        html = re.sub(rx, lambda m: m.group(1) + url + m.group(2), html, count=1)
    html = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")', lambda m: m.group(1) + attr(lead['alt']) + m.group(2), html, count=1)
    print('lead image: %s (%s)' % (lead['jpg16'], lead['kind']))
    return html, lead


_UPD_RX = re.compile(r'<div class="article-updates" data-ledger="([^"]*)"')
_UPD_ICON = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" '
             'd="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>')


def _key(note):
    return hashlib.sha1(note.encode('utf-8')).hexdigest()[:10]


def update_stamps(meta, out_path):
    """[(stamp, note, kind)] in the order of the spec's "updates" list. A note is stamped once, from the
    builder's clock, on the build that first sees it. After that the stamp is read back from the page,
    so a rebuild never moves it. Rewording an old note would restamp it: add a new note instead.
    A malformed "updates" value never stops the build: the article is then built without notes."""
    try:
        return _update_stamps(meta, out_path)
    except Exception as e:
        print('update notes skipped for %s: %s' % (meta.get('slug', '?'), e))
        return []


def _update_stamps(meta, out_path):
    notes = []
    for u in (meta.get('updates') if isinstance(meta.get('updates'), list) else []):
        if not isinstance(u, (str, dict)):
            continue
        note, kind = (u, 'update') if isinstance(u, str) else (str(u.get('note', '')), str(u.get('kind', 'update')))
        note = ' '.join(note.split())
        if note:
            notes.append((note, 'correction' if kind == 'correction' else 'update'))
    if not notes:
        return []
    import publish_time as PT
    ledger = {}
    try:
        m = _UPD_RX.search(open(out_path, encoding='utf-8').read())
        if m:
            ledger = dict(x.split('=', 1) for x in m.group(1).split(',') if '=' in x)
    except OSError:
        pass
    now = PT.iso(PT.now())
    return [(ledger.get(_key(n)) or now, n, k) for n, k in notes]


def _updates_html(html, meta):
    """The notes at the top of the article, an "Updated" time beside the publish time, and the modified time in <head>."""
    ups = meta.get('_upd') or []
    if not ups:
        return html
    import publish_time as PT
    human = lambda t: PT.human(PT.parse(t))
    rows = ''.join('<div style="margin:%s"><strong style="color:#101828">%s</strong> <time datetime="%s">%s</time>. %s</div>'
                   % ('0' if i == 0 else '8px 0 0', 'Correction,' if k == 'correction' else 'Updated', t, human(t), esc(n))
                   for i, (t, n, k) in enumerate(sorted(ups, key=lambda u: u[0], reverse=True)))
    box = ('<div class="article-updates" data-ledger="%s" style="margin:0 0 20px;padding:12px 16px;border:1px solid #EAECF0;'
           'border-left:3px solid #F45407;border-radius:10px;background:#FCFCFD;font-size:14.5px;line-height:1.6;color:#475467">%s</div>'
           % (','.join('%s=%s' % (_key(n), t) for t, n, k in ups), rows))
    a = html.find('<article class="article-content">')
    if a < 0:
        return html
    a += len('<article class="article-content">')
    html = html[:a] + '\n' + box + html[a:]
    last = max(t for t, _, _ in ups)
    html = re.sub(r'(<time datetime="[^"]*">[^<]*</time>\s*</div>)',
                  lambda m: m.group(1) + '\n<div class="article-meta-item">\n' + _UPD_ICON + '\nUpdated&nbsp;<time datetime="%s">%s</time>\n</div>' % (last, human(last)), html, count=1)
    return re.sub(r'(<meta property="article:modified_time" content=")[^"]*(")', lambda m: m.group(1) + last + m.group(2), html, count=1)


def sitemap_lastmods(root, metas):
    """A story with update notes carries the time of its newest note as its sitemap lastmod."""
    p = os.path.join(root, 'sitemap.xml')
    try:
        s = open(p, encoding='utf-8').read()
    except OSError:
        return
    orig = s
    for m in metas:
        ups = m.get('_upd') or []
        if not ups:
            continue
        last = max(t for t, _, _ in ups)
        loc = '<loc>%s/blog/%s/</loc>' % (SITE, m['slug'])
        s = re.sub('(' + re.escape(loc) + r'\s*<lastmod>)[^<]*(</lastmod>)', lambda x: x.group(1) + last + x.group(2), s, count=1)
    if s != orig:
        open(p, 'w', encoding='utf-8').write(s)


def finish(html, meta):
    """Head and chrome changes for a template 2 page. Runs once per build, on the freshly built page.
    The three later additions (lead picture, beat, update notes) are each fenced: if one fails, the
    article is built without it and the log says so. An article is never blocked by them."""
    lead = None
    try:
        html, lead = _lead_html(html, meta)
    except Exception as e:
        print('lead image skipped for %s: %s' % (meta.get('slug', '?'), e))
    html = _markup(html, meta, lead)
    html = _byline(html)
    for step in (_beat_html, _updates_html):
        try:
            html = step(html, meta)
        except Exception as e:
            print('%s skipped for %s: %s' % (step.__name__, meta.get('slug', '?'), e))
    return re.sub(r'<div class="sidebar-card">\s*<h3>Our Packages</h3>.*?</div>\s*', '', html, count=1, flags=re.S)
