#!/usr/bin/env python3
"""Build the newsdesk section. Added 2026-11-14 (SEO audit, item D1 and D2).

Writes /newsdesk/ (latest news with publish times), two beat pages, three editorial pages and a
news-only feed, and keeps their sitemap entries. Every file it writes lives under newsdesk/ (plus
its own lines in sitemap.xml). No other page is touched.

Called by ops/build_news.py at the end of every news build, inside try/except, so a problem here
can never block an article from publishing. Output depends only on the repo, so a rebuild with no
new article changes nothing.

Chrome (head, menu, footer) is copied from clients.html so the pages match the rest of the site.
A news spec may name its beat: "beat": "outbound-compliance" or "outbound-tools". Without it the
beat is guessed from the title, keywords and slug.
"""
import glob, html, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://imisofts.com'
esc = lambda t: html.escape(t or '', quote=True)

BEATS = [
    {'slug': 'outbound-compliance', 'name': 'Outbound compliance',
     'line': 'The rules for calling, texting and emailing people you want to sell to: TCPA, A2P 10DLC, do not call lists, cold email laws and the regulators behind them.'},
    {'slug': 'outbound-tools', 'name': 'Tools outbound teams run on',
     'line': 'Changes to the platforms sales teams depend on: Twilio, HighLevel, Google, Microsoft, the AI models and what they cost.'},
]
_CORE = r'tcpa|can-spam|can spam|10dlc|a2p|robocall|stir.?shaken|do not call|do-not-call|\bdnc\b|telemarketing|toll.?free verification|caller id|opt.?out|consent|unsubscribe|sender (requirements|guidelines)|cold (email|calling) laws?|\bspam'
_CHANNEL = r'\bcall|dial|voice|\bsms\b|\btext|email|outreach|outbound|messag|whatsapp|linkedin|lead gen'
_RULE = r'\blaws?\b|legal|complian|gdpr|\bfcc\b|\bftc\b|regulat|ruling|lawsuit|settlement|penalt|\bfines?\b|\bban|\brules?\b|privacy|disclosure|registry|solicitation'
_TOOLS = r'pricing|\bprices?\b|\bapi\b|releas|launch|update|model|\bgpt|claude|gemini|twilio|highlevel|workspace|microsoft|outlook|gmail|hubspot|apollo|instantly|zoominfo|\bclay\b|n8n|openai|anthropic|deprecat|shutdown|\blimits?\b|outage|copilot|chatgpt|search console|whatsapp|linkedin'

def guess_beat(text):
    if re.search(_CORE, text) or (re.search(_CHANNEL, text) and re.search(_RULE, text)): return 'outbound-compliance'
    if re.search(_TOOLS, text): return 'outbound-tools'
    return None

def load_news():
    out = []
    for f in glob.glob(os.path.join(ROOT, 'content', 'news', '*.json')):
        try: o = json.load(open(f, encoding='utf-8'))
        except Exception: continue
        slug = o.get('slug'); page = os.path.join(ROOT, 'blog', str(slug), 'index.html')
        if not slug or not o.get('title') or not os.path.exists(page): continue
        h = open(page, encoding='utf-8').read()
        m = re.search(r'<meta property="article:published_time" content="(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d[+-]\d\d:\d\d)"', h)
        stamp = m.group(1) if m else None                      # only articles the builder time-stamped carry an hour
        date = (stamp or str(o.get('date', '')))[:10]
        if not re.match(r'\d{4}-\d\d-\d\d$', date): continue
        text = (o['title'] + ' ' + str(o.get('keywords', '')) + ' ' + slug).lower()
        beat = o.get('beat') if o.get('beat') in [b['slug'] for b in BEATS] else guess_beat(text)
        out.append({'slug': slug, 'title': o['title'], 'desc': o.get('desc', ''), 'date': date, 'stamp': stamp, 'beat': beat,
                    'sort': stamp or (date + 'T00:00:00+04:00')})
    out.sort(key=lambda a: (a['sort'], a['slug']), reverse=True)
    return out

MONTHS = 'January February March April May June July August September October November December'.split()
def when(a):
    y, m, d = a['date'].split('-'); day = '%s %d, %s' % (MONTHS[int(m) - 1], int(d), y)
    if not a['stamp']: return '<time datetime="%s">%s</time>' % (a['date'], day)
    hh, mm = int(a['stamp'][11:13]), a['stamp'][14:16]
    return '<time datetime="%s">%s, %d:%s %s GMT+4</time>' % (a['stamp'], day, (hh % 12) or 12, mm, 'AM' if hh < 12 else 'PM')

CSS = '''
.nd-page{--orange:#F45407;--orange-text:#C43F04;--ink:#0F172A;--text:#1A1A1A;--muted:#5B6270;--soft:#6B7280;--line:#ECEEF2;--grey-2:#F9FAFB;color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased;overflow-wrap:break-word}
.nd-page a{color:inherit;text-decoration:none}
.nd-page :focus-visible{outline:2px solid var(--orange);outline-offset:3px;border-radius:8px}
.nd-wrap{max-width:1040px;margin:0 auto}
.nd-hero{position:relative;padding:136px 0 64px;text-align:center;overflow:hidden;isolation:isolate}
.nd-hero::before{content:"";position:absolute;inset:0;z-index:-2;background:radial-gradient(60% 55% at 50% 0%,rgba(244,84,7,.10),rgba(244,84,7,0) 70%),linear-gradient(180deg,#fff 0%,var(--grey-2) 100%)}
.nd-hero::after{content:"";position:absolute;inset:0;z-index:-1;opacity:.55;background-image:radial-gradient(rgba(15,23,42,.10) 1px,transparent 1px);background-size:22px 22px;-webkit-mask-image:radial-gradient(70% 60% at 50% 35%,#000 30%,transparent 75%);mask-image:radial-gradient(70% 60% at 50% 35%,#000 30%,transparent 75%)}
.nd-hero--slim{padding:128px 0 48px}
.nd-crumbs ol{list-style:none;display:flex;justify-content:center;flex-wrap:wrap;gap:8px;font-size:14px;color:var(--soft);margin:0 0 22px;padding:0}
.nd-crumbs li+li::before{content:"/";margin-right:8px;color:#C5C9D0}
.nd-crumbs a:hover{color:var(--orange-text)}
.nd-crumbs [aria-current]{color:var(--ink);font-weight:500}
.nd-eyebrow{display:inline-flex;align-items:center;gap:10px;font-size:15px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:#666;margin:0}
.nd-eyebrow::before{content:"";width:8px;height:8px;border-radius:50%;background:var(--orange);box-shadow:0 0 0 4px rgba(244,84,7,.15)}
.nd-hero h1{font-size:48px!important;font-weight:800;line-height:1.15!important;letter-spacing:-.02em;color:var(--ink);max-width:860px;margin:18px auto 0}
.nd-hero h1 em{font-style:normal;color:var(--orange)}
.nd-lead{font-size:18px;color:var(--muted);max-width:680px;margin:20px auto 0}
.nd-actions{display:flex;justify-content:center;flex-wrap:wrap;gap:12px;margin-top:30px}
.nd-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;border-radius:8px;padding:12px 24px;font-size:15px;font-weight:500;line-height:1.2;transition:transform .2s,box-shadow .2s,border-color .2s}
.nd-btn:hover{transform:translateY(-1px)}
.nd-btn-primary{background:var(--orange);color:#fff!important;box-shadow:0 8px 20px -8px rgba(244,84,7,.55)}
.nd-btn-secondary{background:#fff;color:#333!important;border:1px solid #E3E6EA}
.nd-section{padding:72px 0}
.nd-section--grey{background:var(--grey-2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.nd-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px 32px;flex-wrap:wrap;margin-bottom:28px}
.nd-head h2{font-size:30px;font-weight:800;letter-spacing:-.02em;color:var(--ink);margin:0;line-height:1.2}
.nd-head p{font-size:14px;color:var(--soft);margin:0}
.nd-lede{display:block;background:#fff;border:1px solid var(--line);border-radius:16px;padding:28px 30px;box-shadow:0 20px 50px -34px rgba(15,23,42,.28);transition:transform .25s,box-shadow .25s,border-color .25s}
.nd-lede:hover{transform:translateY(-2px);border-color:rgba(244,84,7,.35);box-shadow:0 26px 60px -34px rgba(15,23,42,.38)}
.nd-lede h3{font-size:28px;font-weight:800;letter-spacing:-.02em;line-height:1.2;color:var(--ink);margin:10px 0 10px}
.nd-lede p{font-size:16px;color:var(--muted);margin:0;max-width:760px}
.nd-meta{display:flex;align-items:center;flex-wrap:wrap;gap:8px 12px;font-size:13px;color:var(--soft)}
.nd-chip{display:inline-flex;align-items:center;height:24px;padding:0 10px;border-radius:999px;background:#FFF3EE;color:var(--orange-text);font-size:12px;font-weight:600;letter-spacing:.02em}
.nd-list{list-style:none;margin:18px 0 0;padding:0;background:#fff;border:1px solid var(--line);border-radius:16px;overflow:hidden}
.nd-list li+li{border-top:1px solid var(--line)}
.nd-story{display:grid;grid-template-columns:230px 1fr auto;align-items:baseline;gap:6px 24px;padding:18px 24px;transition:background .2s}
.nd-story:hover{background:#FCFCFD}
.nd-story time{font-size:13px;color:var(--soft);font-variant-numeric:tabular-nums}
.nd-story strong{font-size:17px;font-weight:600;color:var(--ink);line-height:1.4}
.nd-story:hover strong{color:var(--orange-text)}
.nd-more{display:inline-flex;align-items:center;gap:6px;margin-top:22px;font-size:15px;font-weight:500;color:var(--orange-text)!important}
.nd-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:20px}
.nd-cards--3{grid-template-columns:repeat(3,minmax(0,1fr))}
.nd-card{display:flex;flex-direction:column;gap:10px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:26px 26px 24px;box-shadow:0 1px 2px rgba(15,23,42,.04);transition:transform .25s,box-shadow .25s,border-color .25s}
.nd-card:hover{transform:translateY(-2px);border-color:rgba(244,84,7,.35);box-shadow:0 22px 50px -34px rgba(15,23,42,.35)}
.nd-card h3{font-size:20px;font-weight:700;letter-spacing:-.01em;color:var(--ink);margin:0;line-height:1.3}
.nd-card p{font-size:15px;color:var(--muted);margin:0}
.nd-card span{margin-top:auto;padding-top:8px;font-size:14px;font-weight:500;color:var(--orange-text)}
.nd-prose{max-width:760px;margin:0 auto;padding:56px 0 88px}
.nd-prose h2{font-size:24px;font-weight:800;letter-spacing:-.01em;color:var(--ink);margin:40px 0 12px;line-height:1.3}
.nd-prose p,.nd-prose li{font-size:17px;line-height:1.75;color:#333}
.nd-prose p{margin:0 0 16px}
.nd-prose ul{margin:0 0 18px;padding-left:22px}
.nd-prose li{margin-bottom:8px}
.nd-prose a{color:var(--orange-text);text-decoration:underline;text-underline-offset:3px}
.nd-note{margin-top:36px;padding:18px 20px;border:1px solid var(--line);border-radius:12px;background:var(--grey-2);font-size:14.5px;color:var(--muted)}
@media (max-width:900px){.nd-story{grid-template-columns:1fr auto}.nd-story time{grid-column:1/-1}.nd-cards--3{grid-template-columns:1fr}}
@media (max-width:767px){.nd-hero{padding:112px 0 48px}.nd-hero h1{font-size:34px!important}.nd-lead{font-size:16.5px}.nd-section{padding:52px 0}.nd-head h2{font-size:25px}.nd-lede{padding:22px 20px}.nd-lede h3{font-size:22px}.nd-cards{grid-template-columns:1fr}.nd-story{grid-template-columns:1fr;padding:16px 18px}.nd-story .nd-chip{justify-self:start}.nd-prose{padding:40px 0 64px}.nd-prose h2{font-size:21px}}
'''

def chrome():
    s = open(os.path.join(ROOT, 'clients.html'), encoding='utf-8').read()
    a, b = s.find('<main'), s.find('</main>') + 7
    head_body, tail = s[:a], s[b:]
    tail = re.sub(r'<script>\s*\(function\(\)\{\s*var items=\[\]\.slice\.call\(document\.querySelectorAll\(\'\.cl-item.*?</script>\s*', '', tail, flags=re.S)
    assert 'cl-item' not in tail
    return head_body, tail

def render(path, title, desc, main, ld):
    head_body, tail = chrome(); url = SITE + path; s = head_body
    def sub(rx, new, n=1):
        nonlocal s
        s2, k = re.subn(rx, lambda m: new, s, count=n, flags=re.S); assert k >= 1, rx; s = s2
    sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title))
    sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % esc(desc))
    sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url)
    sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % url)
    for p in ('og:title', 'twitter:title'): sub(r'<meta (property|name)="%s" content="[^"]*">' % p, '<meta %s="%s" content="%s">' % ('property' if p.startswith('og') else 'name', p, esc(title)))
    for p in ('og:description', 'twitter:description'): sub(r'<meta (property|name)="%s" content="[^"]*">' % p, '<meta %s="%s" content="%s">' % ('property' if p.startswith('og') else 'name', p, esc(desc)))
    for p in ('og:image', 'twitter:image'): sub(r'<meta (property|name)="%s" content="[^"]*">' % p, '<meta %s="%s" content="%s/og-image.jpg">' % ('property' if p.startswith('og') else 'name', p, SITE))
    for p in ('og:image:alt', 'twitter:image:alt'): sub(r'<meta (property|name)="%s" content="[^"]*">' % p, '<meta %s="%s" content="imisofts">' % ('property' if p.startswith('og') else 'name', p))
    sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">\n' + json.dumps(ld, indent=1, ensure_ascii=False) + '\n</script>')
    sub(r'<style id="clients-page">.*?</style>', '<style id="newsdesk-page">' + CSS + '</style>')
    sub(r'</head>', '<link rel="alternate" type="application/rss+xml" title="imisofts Newsdesk" href="/newsdesk/feed.xml">\n</head>')
    return put(os.path.join(ROOT, path.strip('/'), 'index.html'), s + main + tail)

def put(out, content):
    """Write only when the content differs, so a rebuild with nothing new changes no file."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        if open(out, encoding='utf-8').read() == content: return out
    except OSError: pass
    open(out, 'w', encoding='utf-8').write(content); return out

def crumbs(items):
    lis = ''.join('<li><a href="%s">%s</a></li>' % (u, esc(n)) if u else '<li aria-current="page">%s</li>' % esc(n) for n, u in items)
    return '<nav class="nd-crumbs" aria-label="Breadcrumb"><ol>%s</ol></nav>' % lis
def ld_page(path, name, desc, trail, extra=None):
    g = [{"@type": "CollectionPage" if extra else "WebPage", "@id": SITE + path + "#webpage", "url": SITE + path, "name": name, "description": desc, "inLanguage": "en",
          "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#organization"}, "breadcrumb": {"@id": SITE + path + "#breadcrumb"}},
         {"@type": "BreadcrumbList", "@id": SITE + path + "#breadcrumb", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + (u or path)} for i, (n, u) in enumerate(trail)]}]
    if extra: g[0]["mainEntity"] = {"@id": SITE + path + "#list"}; g.append(extra)
    if path == '/newsdesk/':
        g[0]["about"] = {"@id": SITE + "/newsdesk/#newsdesk"}
        g.append({"@type": "Organization", "@id": SITE + "/newsdesk/#newsdesk", "name": "imisofts Newsdesk", "url": SITE + "/newsdesk/",
                  "parentOrganization": {"@id": SITE + "/#organization"}, "publishingPrinciples": SITE + "/newsdesk/editorial-standards/",
                  "correctionsPolicy": SITE + "/newsdesk/corrections/"})
    return {"@context": "https://schema.org", "@graph": g}
def itemlist(path, arts):
    return {"@type": "ItemList", "@id": SITE + path + "#list", "numberOfItems": len(arts), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": "%s/blog/%s/" % (SITE, a['slug']), "name": a['title']} for i, a in enumerate(arts)]}
bname = {b['slug']: b['name'] for b in BEATS}
def story(a, chip=True):
    c = '<span class="nd-chip">%s</span>' % esc(bname[a['beat']]) if chip and a['beat'] else '<span></span>'
    return '<li><a class="nd-story" href="/blog/%s/">%s<strong>%s</strong>%s</a></li>' % (a['slug'], when(a), esc(a['title']), c)

def main():
    news = load_news(); made = []
    # ---- /newsdesk
    top, rest = news[0], news[1:13]
    beats = ''.join('<a class="nd-card" href="/newsdesk/%s/"><h3>%s</h3><p>%s</p><span>%d stories &rarr;</span></a>' % (b['slug'], esc(b['name']), esc(b['line']), sum(1 for a in news if a['beat'] == b['slug'])) for b in BEATS)
    desk = ''.join('<a class="nd-card" href="/newsdesk/%s/"><h3>%s</h3><p>%s</p><span>Read &rarr;</span></a>' % x for x in (
        ('how-we-report', 'How we report', 'Where a story starts, how we check it, and what we do when we cannot confirm something.'),
        ('editorial-standards', 'Editorial standards', 'The rules every story follows: sources, accuracy, opinion, and what we sell.'),
        ('corrections', 'Corrections', 'How to tell us we got something wrong, and how we fix it in the open.')))
    m = ('<main id="main" class="nd-page">\n<section class="nd-hero" aria-labelledby="nd-title"><div class="container">%s<p class="nd-eyebrow">imisofts Newsdesk</p>'
         '<h1 id="nd-title">News for teams that sell by <em>email, phone and text</em></h1>'
         '<p class="nd-lead">Rule changes, platform changes and price changes that affect outbound sales. Reported from the primary source, with the date and time we published.</p>'
         '<div class="nd-actions"><a class="nd-btn nd-btn-primary" href="#latest">Latest news <span aria-hidden="true">&darr;</span></a><a class="nd-btn nd-btn-secondary" href="/newsdesk/how-we-report/">How we report</a></div></div></section>\n'
         '<section class="nd-section" id="latest" aria-labelledby="nd-latest"><div class="container"><div class="nd-wrap"><div class="nd-head"><h2 id="nd-latest">Latest</h2><p>Times are Dubai time, GMT+4</p></div>'
         '<a class="nd-lede" href="/blog/%s/"><div class="nd-meta">%s%s</div><h3>%s</h3><p>%s</p></a>'
         '<ul class="nd-list">%s</ul><a class="nd-more" href="/blog">All articles <span aria-hidden="true">&rarr;</span></a> <a class="nd-more" href="/newsdesk/feed.xml" style="margin-left:22px">RSS feed</a></div></div></section>\n'
         '<section class="nd-section nd-section--grey" aria-labelledby="nd-beats"><div class="container"><div class="nd-wrap"><div class="nd-head"><h2 id="nd-beats">What we cover</h2><p>The two areas this desk follows</p></div><div class="nd-cards">%s</div></div></div></section>\n'
         '<section class="nd-section" aria-labelledby="nd-desk"><div class="container"><div class="nd-wrap"><div class="nd-head"><h2 id="nd-desk">How this desk works</h2><p>Editor: <a href="/author/zeeshan-waheed/" style="text-decoration:underline">Zeeshan Waheed</a></p></div><div class="nd-cards nd-cards--3">%s</div></div></div></section>\n</main>\n'
         ) % (crumbs([('Home', '/'), ('Newsdesk', None)]), top['slug'], when(top), ('<span class="nd-chip">%s</span>' % esc(bname[top['beat']])) if top['beat'] else '', esc(top['title']), esc(top['desc']), ''.join(story(a) for a in rest), beats, desk)
    d = 'News for outbound sales teams from the imisofts Newsdesk: rule changes, platform changes and price changes, reported from the primary source with real publish times.'
    made.append(render('/newsdesk/', 'imisofts Newsdesk: News for Outbound Sales Teams', d, m, ld_page('/newsdesk/', 'imisofts Newsdesk', d, [('Home', '/'), ('Newsdesk', None)], itemlist('/newsdesk/', news[:13]))))
    # ---- beat pages
    for b in BEATS:
        arts = [a for a in news if a['beat'] == b['slug']]; p = '/newsdesk/' + b['slug'] + '/'
        m = ('<main id="main" class="nd-page">\n<section class="nd-hero nd-hero--slim"><div class="container">%s<p class="nd-eyebrow">Newsdesk beat</p><h1>%s</h1><p class="nd-lead">%s</p></div></section>\n'
             '<section class="nd-section"><div class="container"><div class="nd-wrap"><div class="nd-head"><h2>Latest in this beat</h2><p>%d stories in all. Times are Dubai time, GMT+4</p></div><ul class="nd-list">%s</ul>'
             '<a class="nd-more" href="/blog">Older stories are in the blog <span aria-hidden="true">&rarr;</span></a></div></div></section>\n</main>\n'
             ) % (crumbs([('Home', '/'), ('Newsdesk', '/newsdesk/'), (b['name'], None)]), esc(b['name']), esc(b['line']), len(arts), ''.join(story(a, False) for a in arts[:40]))
        t = '%s News | imisofts Newsdesk' % b['name']
        made.append(render(p, t, b['line'], m, ld_page(p, t, b['line'], [('Home', '/'), ('Newsdesk', '/newsdesk/'), (b['name'], None)], itemlist(p, arts[:40]))))
    # ---- text pages
    for slug, name, desc, body in TEXT_PAGES:
        p = '/newsdesk/' + slug + '/'
        m = ('<main id="main" class="nd-page">\n<section class="nd-hero nd-hero--slim"><div class="container">%s<p class="nd-eyebrow">imisofts Newsdesk</p><h1>%s</h1><p class="nd-lead">%s</p></div></section>\n'
             '<div class="container"><article class="nd-prose">%s</article></div>\n</main>\n') % (crumbs([('Home', '/'), ('Newsdesk', '/newsdesk/'), (name, None)]), esc(name), esc(desc), body)
        made.append(render(p, '%s | imisofts Newsdesk' % name, desc, m, ld_page(p, name, desc, [('Home', '/'), ('Newsdesk', '/newsdesk/'), (name, None)])))
    feed(news); sitemap(news)
    print('newsdesk: built', len(made), 'pages | news articles', len(news), '| with a real publish time', sum(1 for a in news if a['stamp']), '| beats', {b['slug']: sum(1 for a in news if a['beat'] == b['slug']) for b in BEATS}, '| in no beat', sum(1 for a in news if not a['beat']))

def rfc822(stamp):
    y, mo, d = int(stamp[:4]), int(stamp[5:7]), int(stamp[8:10])
    import datetime
    wd = 'Mon Tue Wed Thu Fri Sat Sun'.split()[datetime.date(y, mo, d).weekday()]
    return '%s, %02d %s %d %s %s' % (wd, d, MONTHS[mo - 1][:3], y, stamp[11:19], stamp[19:].replace(':', ''))

def feed(news):
    """News-only feed. Only stories with a stored publish time are listed, so every time in it is real."""
    items = [a for a in news if a['stamp']][:40]
    if not items: return
    x = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
         '<title>imisofts Newsdesk</title>', '<link>%s/newsdesk/</link>' % SITE,
         '<description>News for outbound sales teams: rule changes, platform changes and price changes, reported from the primary source.</description>',
         '<language>en</language>', '<lastBuildDate>%s</lastBuildDate>' % rfc822(items[0]['stamp']),
         '<atom:link href="%s/newsdesk/feed.xml" rel="self" type="application/rss+xml"/>' % SITE]
    for a in items:
        u = '%s/blog/%s/' % (SITE, a['slug'])
        x.append('<item><title>%s</title><link>%s</link><guid isPermaLink="true">%s</guid><pubDate>%s</pubDate><description>%s</description></item>' % (esc(a['title']), u, u, rfc822(a['stamp']), esc(a['desc'])))
    x += ['</channel>', '</rss>', '']
    put(os.path.join(ROOT, 'newsdesk', 'feed.xml'), '\n'.join(x))

def sitemap(news):
    """Keep one sitemap entry per newsdesk page. List pages carry the date of their newest story."""
    p = os.path.join(ROOT, 'sitemap.xml')
    try: s = open(p, encoding='utf-8').read()
    except OSError: return
    newest = lambda arts: arts[0]['date'] if arts else '2026-11-14'
    want = [('/newsdesk/', newest(news), 'daily', '0.8')]
    want += [('/newsdesk/%s/' % b['slug'], newest([a for a in news if a['beat'] == b['slug']]), 'daily', '0.6') for b in BEATS]
    want += [('/newsdesk/%s/' % t[0], '2026-11-14', 'monthly', '0.4') for t in TEXT_PAGES]
    orig = s
    for path, lastmod, freq, prio in want:
        loc = '<loc>%s%s</loc>' % (SITE, path); entry = '<url>\n%s\n<lastmod>%s</lastmod>\n<changefreq>%s</changefreq>\n<priority>%s</priority>\n</url>' % (loc, lastmod, freq, prio)
        if loc in s:
            s = re.sub(r'<url>\s*' + re.escape(loc) + r'.*?</url>', lambda m: entry, s, count=1, flags=re.S)
        else:
            k = s.rfind('</urlset>')
            if k == -1: return
            s = s[:k] + entry + '\n' + s[k:]
    if s != orig: open(p, 'w', encoding='utf-8').write(s)

TEXT_PAGES = [
 ('how-we-report', 'How we report', 'Where a story starts, how it is checked, and what you can hold us to.', '''
<h2>We start from the primary source</h2>
<p>A story begins with the page that owns the fact: the company's own changelog or price page, the regulator's own text, the court filing. We read the page itself, not a summary of it, and we link it in the article.</p>
<h2>We quote exactly</h2>
<p>Numbers and quotes are copied from the source at the time we read it, and the article says which day that was. When a number is our own count or calculation, we say so and show what it is based on.</p>
<h2>We say what we could not confirm</h2>
<p>If a page did not load, a number is not published, or two official pages disagree, the article says that in plain words. We do not fill the gap with a guess.</p>
<h2>Every story is checked before it goes out</h2>
<p>Before publishing, a separate check compares each number, date and quote in the draft with the notes taken from the source. Anything that does not match is fixed or removed.</p>
<h2>We show when we published</h2>
<p>Since November 14, 2026, each news story carries the date and the time it went live, in Dubai time (GMT+4). Older stories show the date only. If we change a story in a way that matters, we add a dated note that says what changed.</p>
<h2>We tell you what we sell</h2>
<p>imisofts is an agency. We sell services related to the topics we cover, and some stories link to one of them. Since November 14, 2026, every new news story ends with an "About this article" box that says so.</p>
<p class="nd-note">The newsdesk is run by imisofts. Editor: <a href="/author/zeeshan-waheed/">Zeeshan Waheed</a>. See also our <a href="/newsdesk/editorial-standards/">editorial standards</a> and <a href="/newsdesk/corrections/">corrections</a>.</p>'''),
 ('editorial-standards', 'Editorial standards', 'The rules every story on the newsdesk follows.', '''
<h2>Accuracy comes first</h2>
<p>We would rather publish later than publish something we have not read at the source. A claim we cannot trace to a source does not go in.</p>
<h2>Sources are named and linked</h2>
<p>Every story links the pages it relies on. We say what a source measured and when, in its own terms, and we do not make a claim stronger than the source does.</p>
<h2>Opinion is labelled</h2>
<p>When we add our own reading of what a change means, it is marked as ours, with words such as "our read" or "we suggest". Headlines describe what happened and match what the story says.</p>
<h2>Legal topics</h2>
<p>Stories about laws and regulations describe the rule from its own text. They are general information, not legal advice.</p>
<h2>What we sell, and what we do not</h2>
<p>imisofts sells services in the areas the newsdesk covers. That is why each new news story carries a note saying so. Coverage is not for sale: a company cannot pay to appear in a news story or to change what it says.</p>
<h2>Mistakes</h2>
<p>When we get something wrong, we fix it and say that we did. The <a href="/newsdesk/corrections/">corrections page</a> explains how.</p>'''),
 ('corrections', 'Corrections', 'How to tell us we got something wrong, and how we fix it.', '''
<h2>Tell us</h2>
<p>If you see an error in a story, write to us through the <a href="/contact">contact page</a>. Tell us which story, what is wrong, and where the correct information can be found. A link to the source helps most.</p>
<h2>What we do</h2>
<ul>
<li>We check the point against the source.</li>
<li>If the story is wrong, we correct it and add a dated note in the story that says what changed.</li>
<li>If the story is right but unclear, we may reword it and say so in the same way.</li>
<li>We do not delete a story to hide an error.</li>
</ul>
<h2>Corrections so far</h2>
<p>This page was created on November 14, 2026. No corrections have been issued since then. When there are some, they will be listed here with the date and the story.</p>'''),
]
if __name__ == '__main__':
    main()
