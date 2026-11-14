#!/usr/bin/env python3
"""News template 2 for NEW news articles. Added 2026-11-14 (SEO audit, items A2 and B1 to B5).

Applies only to an article whose page does not exist yet, or whose page already carries the marker
data-news-template="2". Every older page keeps the old template, byte for byte.

What a template 2 article gets:
  - markup: author and editor, publisher tied to the company entity (@id) with the real logo,
    isAccessibleForFree, inLanguage, optional "about" from the spec;
  - a byline block (see BYLINE);
  - after the body: Related coverage (three stories, linked by their exact titles) and one small
    "About this article" box (who wrote it, who edits it, that imisofts sells services, how to
    report an error), in place of the sales banner;
  - the sidebar without the packages card.
The article text itself is not changed. Phone layout (tables, long words) is handled for every
article by the phone rules at the end of /blog/blog.css.
Related coverage is chosen once, on the first build, and read back from the page on a rebuild.
"""
import glob, json, os, re

SITE = 'https://imisofts.com'
MARK = 'data-news-template="2"'
BYLINE = 'newsdesk'          # 'newsdesk' = "imisofts Newsdesk, Editor: Zeeshan Waheed"; 'founder' = "Zeeshan Waheed"
AUTHOR_URL = SITE + '/author/zeeshan-waheed/'
ORG_ID = SITE + '/#organization'
PERSON_ID = AUTHOR_URL + '#person'
LOGO = {"@type": "ImageObject", "url": SITE + "/favicon-512.png", "width": 512, "height": 512}
_LABEL = 'font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#98A2B3'
ABOUT = ('<aside class="about-this-article" ' + MARK + ' style="margin:24px 0 8px;padding:16px 18px;border:1px solid #EAECF0;'
         'border-radius:12px;background:#FCFCFD;font-size:14px;line-height:1.65;color:#475467">'
         '<div style="' + _LABEL + ';margin-bottom:6px">About this article</div>'
         'Written by imisofts Newsdesk from the primary sources linked above. Editor: Zeeshan Waheed. '
         'imisofts is an agency and sells services related to the topics it covers, including any service linked here. '
         '<a href="/contact" style="color:#475467;text-decoration:underline">Report an error</a>.</aside>')
_REL_RX = re.compile(r'<section class="related-coverage".*?</section>', re.S)


def esc(t):
    return (t or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


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
    picks = cands[:3]
    if not picks:
        return ''
    related = sum(1 for c in picks if c[0] > 0) >= 2            # an honest label: "related" only when it is
    head = 'Related coverage' if related else 'Latest from the newsdesk'
    if not related:
        picks = sorted(cands, key=lambda c: (c[1], c[2], c[3]), reverse=True)[:3]
    link = 'color:#101828;font-weight:500;text-decoration:none;line-height:1.45;display:block'
    lis = '\n'.join('<li style="margin:0;padding:12px 0;border-bottom:1px solid #F2F4F7"><a href="/blog/%s/" style="%s">%s</a></li>'
                    % (s, link, esc(t)) for _, _, _, s, t in picks)
    return ('<section class="related-coverage" style="margin:36px 0 0;padding-top:22px;border-top:1px solid #EAECF0">\n'
            '<div style="%s;margin-bottom:4px">%s</div>\n<ul style="list-style:none;margin:0;padding:0">\n%s\n</ul>\n</section>') % (_LABEL, head, lis)


def after_body(meta, root):
    """Everything that follows the article text and precedes the FAQ."""
    return '\n'.join(p for p in (related_block(meta, root), ABOUT) if p)


def _markup(html, meta):
    def repl(m):
        try:
            o = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if not (isinstance(o, dict) and o.get('@type') == 'NewsArticle'):
            return m.group(0)
        person = {"@type": "Person", "@id": PERSON_ID, "name": "Zeeshan Waheed", "url": AUTHOR_URL}
        if BYLINE == 'newsdesk':
            o['author'] = {"@type": "Organization", "name": "imisofts Newsdesk", "url": SITE + "/about",
                           "parentOrganization": {"@id": ORG_ID}}
            o['editor'] = person
        else:
            o['author'] = person
        o['publisher'] = {"@type": "Organization", "@id": ORG_ID, "name": "imisofts", "url": SITE + "/", "logo": LOGO}
        o['isAccessibleForFree'] = True
        o['inLanguage'] = 'en'
        ab = meta.get('about')
        if isinstance(ab, list) and ab:                           # optional spec field: [{"name": ..., "sameAs": ...}, ...]
            o['about'] = [dict({"@type": "Thing"}, **{k: v for k, v in a.items() if k in ('name', 'sameAs', '@type')})
                          for a in ab if isinstance(a, dict) and a.get('name')]
        return '<script type="application/ld+json">\n' + json.dumps(o, indent=1, ensure_ascii=False) + '\n</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', repl, html, flags=re.S)


def _byline(html):
    if BYLINE != 'newsdesk':
        return html
    rx = re.compile(r'<a href="/author/zeeshan-waheed/"([^>]*)>Zeeshan Waheed</a>')
    m = rx.search(html)
    if not m:
        return html
    new = ('<span style="font-weight:500">imisofts Newsdesk</span> <span style="color:#98A2B3">&middot;</span> Editor: '
           '<a href="/author/zeeshan-waheed/"%s>Zeeshan Waheed</a>') % m.group(1)
    html = html[:m.start()] + new + html[m.end():]
    return re.sub(r'(<meta property="article:author" content=")[^"]*(")', lambda x: x.group(1) + 'imisofts Newsdesk' + x.group(2), html, count=1)


def finish(html, meta):
    """Head and chrome changes for a template 2 page. Idempotent."""
    html = _markup(html, meta)
    html = _byline(html)
    return re.sub(r'<div class="sidebar-card">\s*<h3>Our Packages</h3>.*?</div>\s*', '', html, count=1, flags=re.S)
