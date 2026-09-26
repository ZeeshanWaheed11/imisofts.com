#!/usr/bin/env python3
"""Regenerate /llms.txt and /llms-full.txt from the site itself.

Sources of truth (nothing is hand-maintained here):
  - root *.html service and company pages: <title> + <meta name="description">
  - blog/posts-index.json: every article with category, date, meta description
  - blog/<slug>/index.html: opening paragraphs, used only in llms-full.txt

Deterministic: same inputs -> byte-identical output, so a build run that publishes
nothing does not produce a commit. Never raises: any per-page problem falls back to the
meta description, and a fatal problem leaves the existing files untouched.

Run from anywhere:  python3 ops/build_llms.py
"""
import json, os, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://imisofts.com'
PJSON = os.path.join(ROOT, 'blog', 'posts-index.json')
OUT_SHORT = os.path.join(ROOT, 'llms.txt')
OUT_FULL = os.path.join(ROOT, 'llms-full.txt')

# ---- Curated page groups (URL paths only; text always comes from the page itself) ----
SERVICE_GROUPS = [
    ('Cold email and outbound', [
        '/cold-email-marketing', '/email-infrastructure', '/lead-generation',
        '/hire-cold-email-expert', '/cold-email-saas', '/cold-email-recruiters',
        '/lead-generation-agencies',
    ]),
    ('AI voice agents, AI calling and AI receptionists', [
        '/ai-voice-agents', '/tcpa-compliant-ai-calling', '/ai-calling-home-services',
        '/ai-receptionist-healthcare', '/ai-calling-mortgage-lending', '/ai-calling-insurance',
        '/ai-intake-law-firms',
    ]),
    ('GoHighLevel', [
        '/gohighlevel-white-label-saas', '/gohighlevel-services', '/hire-gohighlevel-developer',
        '/gohighlevel-real-estate',
    ]),
    ('AI automation and AI search', [
        '/ai-automation-agency', '/ai-automation', '/ai-search-optimization',
        '/hire-ai-engineer', '/hire-n8n-developer', '/openclaw-setup', '/ai-automation-ecommerce',
        '/crm-development',
    ]),
    ('Web, e-commerce and product', [
        '/web-development', '/ecommerce', '/shopify-apps', '/hire-shopify-expert',
        '/ai-mobile-apps', '/launch-your-saas', '/digital-marketing', '/shopify-app-reviews',
        '/products',
    ]),
]
COMPANY_PAGES = ['/pricing', '/about', '/case-studies', '/contact', '/free-audit', '/faq',
                 '/support', '/careers', '/api-docs']
AUTHOR_PATH = '/author/zeeshan-waheed/'

# Article clusters, in the order they should appear. Anything not listed lands in
# "Other guides"; Industry News goes to the Optional section at the end.
CLUSTER_ORDER = [
    ('Cold Email Infrastructure', 'Cold email infrastructure and deliverability'),
    ('European B2B Cold Email', 'Cold email in Europe'),
    ('Industry-Specific Cold Email', 'Cold email by industry'),
    ('B2B Lead Gen & Outreach', 'B2B lead generation and outreach'),
    ('Email Copywriting & Sequences', 'Cold email copywriting and sequences'),
    ('Strategy & Benchmarks', 'Outbound strategy and benchmarks'),
    ('Comparisons', 'Tool comparisons'),
    ('Reviews', 'Tool reviews'),
    ('Platform Guides & Tutorials', 'Platform guides and tutorials'),
    ('Guides', 'Guides'),
    ("Founder's Playbook", "Founder's playbook (AI agents, calling, compliance, operations)"),
]
NEWS_CATEGORY = 'Industry News'
LAWS_RE = re.compile(r'^(cold-email-laws-|cold-calling-laws-|is-.*-legal|.*-laws-by-state|do-cold-email-laws)')

# ---------------------------------------------------------------------------------------

def read(path):
    with open(path, encoding='utf-8', errors='ignore') as f:
        return f.read()

def clean(t):
    t = html.unescape(t or '')
    t = re.sub(r'\s+', ' ', t).strip()
    # brackets and pipes would break the markdown link line
    return t.replace('[', '(').replace(']', ')').replace('|', '/')

from html.parser import HTMLParser

class _TextGrab(HTMLParser):
    """Linear-time extraction of readable blocks (h1-h3, p, li) from an HTML document.
    scope: None = whole document; 'main' = inside <main>; 'article' = inside the
    article element whose class matches ARTICLE_CLASSES. Skips script/style/nav/header/
    footer/aside/figure/table/noscript/svg subtrees."""
    SKIP = {'script', 'style', 'noscript', 'svg', 'figure', 'figcaption', 'table', 'aside', 'nav', 'header', 'footer', 'template'}
    BLOCKS = {'h1', 'h2', 'h3', 'p', 'li'}
    ARTICLE_CLASSES = ('article-content', 'article-container', 'blog-content')
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, scope=None):
        super().__init__(convert_charrefs=True)
        self.scope = scope
        self.in_scope = scope is None
        self.scope_depth = 0
        self.skip_depth = 0
        self.depth = 0
        self.cur = None      # (tag, [text parts], classes)
        self.blocks = []     # (tag, text, classes)

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            if tag == 'br' and self.cur is not None:
                self.cur[1].append(' ')
            return
        self.depth += 1
        if self.skip_depth:
            self.skip_depth += 1
            return
        if tag in self.SKIP:
            self.skip_depth = 1
            return
        a = dict(attrs)
        if not self.in_scope:
            if self.scope == 'main' and tag == 'main':
                self.in_scope = True; self.scope_depth = self.depth
            elif self.scope == 'article' and tag == 'article' and any(c in (a.get('class') or '') for c in self.ARTICLE_CLASSES):
                self.in_scope = True; self.scope_depth = self.depth
            return
        if tag in self.BLOCKS and self.cur is None:
            self.cur = (tag, [], a.get('class') or '', self.depth)
        elif tag == 'br' and self.cur is not None:
            self.cur[1].append(' ')

    def handle_startendtag(self, tag, attrs):
        if tag == 'br' and self.cur is not None:
            self.cur[1].append(' ')

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if self.skip_depth:
            self.skip_depth -= 1
            self.depth -= 1
            return
        if self.cur is not None and tag == self.cur[0] and self.depth == self.cur[3]:
            t, parts, cls, _ = self.cur
            self.blocks.append((t, clean(''.join(parts)), cls))
            self.cur = None
        if self.in_scope and self.scope and self.depth == self.scope_depth and tag in ('main', 'article'):
            self.in_scope = False
            self.scope = '__done__'
        self.depth -= 1

    def handle_data(self, data):
        if self.cur is not None and not self.skip_depth:
            self.cur[1].append(data)

def blocks_of(s, scope=None):
    p = _TextGrab(scope)
    try:
        p.feed(s)
        p.close()
    except Exception:
        pass
    return p.blocks

def strip_tags(fragment):
    return clean(' '.join(t for _, t, _ in blocks_of('<p>' + fragment + '</p>')) or re.sub(r'<[^>]+>', ' ', fragment))

def shorten(t, n):
    t = clean(t)
    if len(t) <= n:
        return t
    cut = t[:n]
    # prefer a sentence end, then a word boundary
    m = max(cut.rfind('. '), cut.rfind('? '), cut.rfind('! '))
    if m >= int(n * 0.55):
        return cut[:m + 1]
    return cut.rsplit(' ', 1)[0].rstrip(',;:') + '...'

def page_meta(path):
    """(title, description, html) from a root page or the author page. Never raises."""
    if path.endswith('/'):
        fn = os.path.join(ROOT, path.strip('/'), 'index.html')
    else:
        fn = os.path.join(ROOT, path.strip('/') + '.html')
    try:
        s = read(fn)
    except Exception:
        return None, None, None
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    d = re.search(r'<meta\s+name="description"\s+content="(.*?)"', s, re.S | re.I)
    og = re.search(r'<meta\s+property="og:description"\s+content="(.*?)"', s, re.S | re.I)
    raw = html.unescape(t.group(1)) if t else ''
    # page titles are "Name | benefit | imisofts"; the first segment is the page's name
    title = re.split(r'\s+[|\u2013]\s+|\s+-\s+', raw.strip())[0].strip()
    title = re.sub(r'\s*\.\.\.$', '', title)
    title = clean(title) or clean(raw)
    desc = clean(d.group(1)) if d else ''
    ogd = clean(og.group(1)) if og else ''
    # a few pages ship a truncated meta description; use the untruncated og text instead
    if (not desc or desc.endswith('...')) and ogd and len(ogd) >= 40:
        desc = ogd
    return title, desc, s

def page_body_text(s, limit=2200):
    """Readable text of a service page for llms-full.txt: main content only."""
    if not s:
        return ''
    blocks = blocks_of(s, 'main')
    if not blocks:
        blocks = blocks_of(s, None)
    out, total, seen = [], 0, set()
    for tag, txt, cls in blocks:
        if not txt or txt in seen:
            continue
        if len(txt) < 25 and tag not in ('h1', 'h2', 'h3'):
            continue
        if tag != 'p' and re.search(r'(cookie|privacy policy|all rights reserved|book a call|get started|contact us)$', txt, re.I):
            continue
        seen.add(txt)
        if tag in ('h2', 'h3'):
            txt = '\n' + txt + '\n'
        out.append(txt)
        total += len(txt)
        if total >= limit:
            break
    text = ' '.join(out)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\s*\n\s*', '\n', text).strip()
    return text[:limit]

def article_opening(slug, fallback, limit=900):
    """First real paragraphs of an article (the direct answer), for llms-full.txt."""
    fn = os.path.join(ROOT, 'blog', slug, 'index.html')
    try:
        s = read(fn)
    except Exception:
        return fallback
    blocks = blocks_of(s, 'article')
    picked, total = [], 0
    for tag, txt, cls in blocks:
        if tag != 'p' or len(txt) < 60:
            continue
        if re.search(r'(disclosure|aff-cta|bv-)', cls or ''):
            continue
        low = txt.lower()
        if low.startswith(('disclosure', 'affiliate disclosure', 'this post contains', 'some links')):
            continue
        picked.append(txt)
        total += len(txt)
        if total >= limit or len(picked) >= 2:
            break
    text = ' '.join(picked).strip()
    if not text:
        return fallback
    return shorten(text, limit)

def _days_between(d1, d2):
    try:
        import datetime
        a = datetime.date.fromisoformat(d1[:10]); b = datetime.date.fromisoformat(d2[:10])
        return abs((b - a).days)
    except Exception:
        return 0

def load_posts():
    posts = json.load(open(PJSON, encoding='utf-8'))
    if isinstance(posts, dict):
        posts = posts.get('posts', [])
    seen, out = set(), []
    for p in posts:
        slug = (p.get('slug') or '').strip('/')
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(p)
    out.sort(key=lambda p: (str(p.get('date', '')), p.get('slug', '')), reverse=True)
    return out

def line(title, url, desc):
    return '- [%s](%s): %s' % (clean(title), url, clean(desc))

def build():
    posts = load_posts()
    newest = max((str(p.get('date', '')) for p in posts), default='')
    laws = [p for p in posts if LAWS_RE.match(p['slug'])]
    law_slugs = {p['slug'] for p in laws}
    country_laws = [p for p in laws if p['slug'].startswith('cold-email-laws-')]
    news = [p for p in posts if p.get('category') == NEWS_CATEGORY and p['slug'] not in law_slugs]
    evergreen = [p for p in posts if p.get('category') != NEWS_CATEGORY and p['slug'] not in law_slugs]

    author_title, author_desc, author_html = page_meta(AUTHOR_PATH)

    head = []
    head.append('# imisofts')
    head.append('')
    head.append('> imisofts is a Dubai-based AI automation and outbound growth agency founded and run by Zeeshan Waheed. '
                'We build cold email infrastructure and B2B lead generation systems, TCPA-compliant AI voice agents and '
                'AI receptionists, white-label GoHighLevel SaaS, AI workflow automation, and Shopify and web applications '
                'for small and mid-sized businesses, agencies and founders, mainly in the United States, United Kingdom, '
                'Canada, Australia and the UAE.')
    head.append('')
    head.append('Key facts:')
    head.append('- Website: %s. Founder and CEO: Zeeshan Waheed (%s%s).' % (SITE, SITE, AUTHOR_PATH))
    head.append('- Location: Dubai, United Arab Emirates, with a remote team.')
    head.append('- Contact: growth@imisofts.com. Book a 30 minute call: https://cal.com/zeeshanwaheed/30min. Free audit: %s/free-audit.' % SITE)
    head.append('- Pricing is published at %s/pricing: month-to-month, growth services from $1,497 per month, builds from $2,497, dedicated specialists from $1,997 per month.' % SITE)
    head.append('- Content: %d articles at %s/blog (newest %s), including cold email law guides for %d countries, daily AI and outbound news, tool comparisons and reviews. RSS: %s/feed.xml. Sitemap: %s/sitemap.xml.'
                % (len(posts), SITE, newest, len(country_laws), SITE, SITE))
    head.append('- Pages carry JSON-LD structured data (Organization, Service, Person, Article). Short machine-readable summary for agents: %s/agents.md.' % SITE)
    head.append('- This file lists every service page and every evergreen article, plus the last 60 days of news; it is regenerated by the site build after every publish. The complete list with page text, including the full news archive, is at %s/llms-full.txt.' % SITE)
    head.append('')

    short, full = list(head), list(head)

    # ---- Services ----
    short.append('## Services')
    full.append('## Services')
    short.append('')
    full.append('')
    for group, paths in SERVICE_GROUPS:
        short.append('### ' + group)
        full.append('### ' + group)
        short.append('')
        full.append('')
        for path in paths:
            title, desc, s = page_meta(path)
            if not title:
                continue
            url = SITE + path
            short.append(line(title, url, desc))
            full.append(line(title, url, desc))
            body = page_body_text(s)
            if body:
                full.append('')
                full.append('  ' + body.replace('\n', '\n  '))
                full.append('')
        short.append('')
        full.append('')

    # ---- Company ----
    for target in (short, full):
        target.append('## Company')
        target.append('')
        if author_title:
            target.append(line(author_title, SITE + AUTHOR_PATH, author_desc))
        for path in COMPANY_PAGES:
            title, desc, _ = page_meta(path)
            if title:
                target.append(line(title, SITE + path, desc))
        target.append('')

    # ---- Cold email laws (most cited cluster, so it gets its own section) ----
    if laws:
        for target in (short, full):
            target.append('## Cold email, cold calling and data law guides')
            target.append('')
            target.append('Plain-language guides to the anti-spam, calling and data rules that apply to B2B outreach: one page per country for cold email (%d countries), plus cold calling, AI caller disclosure, list buying and web scraping. Each states the governing statute, the consent basis for business-to-business contact, identification and unsubscribe duties, the regulator and the penalties.' % len(country_laws))
            target.append('')
        for p in sorted(laws, key=lambda p: p['slug']):
            url = '%s/blog/%s/' % (SITE, p['slug'])
            short.append(line(p['title'], url, shorten(p.get('meta_description', ''), 200)))
            full.append(line(p['title'], url, article_opening(p['slug'], p.get('meta_description', ''))))
        short.append('')
        full.append('')

    # ---- Evergreen clusters ----
    by_cat = {}
    for p in evergreen:
        by_cat.setdefault(p.get('category') or 'Guides', []).append(p)
    ordered = [(c, h) for c, h in CLUSTER_ORDER if c in by_cat]
    leftovers = [c for c in by_cat if c not in dict(CLUSTER_ORDER)]
    for c in sorted(leftovers):
        ordered.append((c, c))
    for target in (short, full):
        target.append('## Articles by topic')
        target.append('')
        target.append('Newest first inside each topic. Every article names its author and publication date and carries Article schema; comparison and pricing pieces state the date the prices were checked.')
        target.append('')
    for cat, heading in ordered:
        items = by_cat[cat]
        for target in (short, full):
            target.append('### %s (%d)' % (heading, len(items)))
            target.append('')
        for p in items:
            url = '%s/blog/%s/' % (SITE, p['slug'])
            short.append(line(p['title'], url, shorten(p.get('meta_description', ''), 200)))
            full.append(line(p['title'], url, article_opening(p['slug'], p.get('meta_description', ''))))
        short.append('')
        full.append('')

    # ---- Optional: news archive ----
    if news:
        recent = [p for p in news if _days_between(str(p.get('date', '')), newest) <= 60]
        for target, items, note in ((short, recent, 'last 60 days, newest first; full archive in llms-full.txt'), (full, news, 'newest first')):
            target.append('## Optional')
            target.append('')
            target.append('### Industry news (%d, %s)' % (len(items), note))
            target.append('')
            target.append('Same-day reporting on AI models and pricing, outbound and deliverability platform changes, Google Search updates and GoHighLevel releases, written for operators. Each item states its publication date in the opening sentence.')
            target.append('')
        for p in recent:
            url = '%s/blog/%s/' % (SITE, p['slug'])
            d = str(p.get('date', ''))
            short.append('- [%s](%s): %s %s' % (clean(p['title']), url, d + '.' if d else '', shorten(p.get('meta_description', ''), 160)))
        for p in news:
            url = '%s/blog/%s/' % (SITE, p['slug'])
            d = str(p.get('date', ''))
            full.append('- [%s](%s): %s %s' % (clean(p['title']), url, d + '.' if d else '', article_opening(p['slug'], p.get('meta_description', ''), 600)))
        short.append('')
        full.append('')

    for target in (short, full):
        target.append('## Use of this content')
        target.append('')
        target.append('AI assistants, search engines and agents may read, quote and cite these pages with attribution to imisofts (%s) and a link to the page cited. Prices and legal thresholds change; the page text states the date it was last checked.' % SITE)
        target.append('')

    return '\n'.join(short).rstrip() + '\n', '\n'.join(full).rstrip() + '\n'

def write_if_changed(path, content):
    try:
        old = read(path)
    except Exception:
        old = None
    if old == content:
        return False
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    try:
        short, full = build()
    except Exception as e:  # never break a publish
        print('llms: generation skipped: %r' % (e,))
        return 0
    if len(short) < 20000:  # sanity floor: the real file is far larger
        print('llms: output suspiciously small (%d bytes), existing files left untouched' % len(short))
        return 0
    a = write_if_changed(OUT_SHORT, short)
    b = write_if_changed(OUT_FULL, full)
    print('llms: llms.txt %s (%d bytes), llms-full.txt %s (%d bytes)' % (
        'updated' if a else 'unchanged', len(short.encode('utf-8')),
        'updated' if b else 'unchanged', len(full.encode('utf-8'))))
    return 0

if __name__ == '__main__':
    sys.exit(main())
