#!/usr/bin/env python3
"""Sync blog/index.html card grid from blog/posts-index.json.
Inserts any post (newest-first) whose slug isn't already a card. Idempotent.
Run after publishing a new article. Preserves all existing cards untouched."""
import json, re, html, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDX  = os.path.join(ROOT, 'blog', 'index.html')
PJSON= os.path.join(ROOT, 'blog', 'posts-index.json')

GRAD = {  # category -> thumbnail gradient (matches site palette)
 'Industry News':            'linear-gradient(135deg, #F45407, #B45309)',
 'Cold Email Infrastructure':'linear-gradient(135deg, #374151, #1F2937)',
 'default':                  'linear-gradient(135deg, #1E293B, #0F172A)',
}
# posts-index category -> blog-index tab category (data-category)
TABMAP = {
 'Industry News':'Industry News', 'AI Automation':'Industry News',
}

def esc(t): return html.escape(t or '', quote=True)

def card(p):
    slug = p['slug']; title = p['title']
    cat  = p.get('category','Industry News')
    tab  = TABMAP.get(cat, cat)
    grad = GRAD.get(tab, GRAD['default'])
    desc = (p.get('meta_description') or '').strip()
    if len(desc) > 120: desc = desc[:117].rsplit(' ',1)[0] + '...'
    kw = p.get('primary_keyword','')
    sk = p.get('secondary_keywords','')
    if isinstance(sk, list): sk = ', '.join(sk)
    keywords = (kw + (', '+sk if sk else '')).strip(', ')
    date = p.get('date','')
    rt   = p.get('read_time') or p.get('readingTime') or 5
    thumb = p.get('thumb')   # 2026-11-18: image system 2 posts carry their preview cover; every other card is unchanged
    if thumb:
        th = (f'<div class="card-thumbnail" style="background:#f3efe7;padding:0;overflow:hidden">'
              f'<img src="{esc(thumb)}" alt="{esc(title)}" width="1200" height="675" loading="lazy" decoding="async" '
              f'style="width:100%;height:100%;object-fit:cover;object-position:center;display:block"></div>\n')
    else:
        th = (f'<div class="card-thumbnail" style="background: {grad};">'
              f'<span class="card-thumb-cat">{esc(tab)}</span>'
              f'<span class="card-thumb-title">{esc(title)}</span>'
              f'<span class="card-thumb-brand">imisofts.com</span></div>\n')
    return (
f'<a href="/blog/{slug}/" class="post-card" data-category="{esc(tab)}" '
f'data-title="{esc(title)}" data-keywords="{esc(keywords)}">\n'
+ th +
f'<div class="card-category">{esc(tab)}</div>\n'
f'<h2>{esc(title)}</h2>\n'
f'<p class="card-excerpt">{esc(desc)}</p>\n'
f'<div class="card-footer">\n<span>{esc(date)}</span>\n<span>{rt} min read</span>\n</div>\n</a>')

def main():
    s = open(IDX, encoding='utf-8').read()
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import fix_blog_grid
        _heal,_n = fix_blog_grid.fix(s)
        if _heal != s:
            s=_heal; open(IDX,'w',encoding='utf-8').write(s)
            print('grid self-heal: moved %d cards into posts-grid'%_n)
    except Exception as _e:
        print('grid self-heal skipped:', _e)
    posts = json.load(open(PJSON, encoding='utf-8'))
    if isinstance(posts, dict): posts = posts.get('posts', [])
    # REFRESH PASS (evergreen refreshes only). The insert pass below never touches an
    # existing card, so a refreshed post used to keep its original card: stale date, stale
    # title, stranded deep in the grid. Scope: ONLY cards whose date has actually moved,
    # i.e. a real refresh. Those are re-rendered and re-sorted to the front of the grid.
    # Everything else is left byte-for-byte alone. Idempotent: no date drift, no rewrite.
    anchor0 = '<div class="posts-grid" id="postsGrid">\n'
    refreshed = []
    for p in posts:
        slug = p.get('slug'); pdate = str(p.get('date','')).strip()
        if not slug or not pdate: continue
        m = re.search(r'<a href="/blog/%s/" class="post-card".*?</a>' % re.escape(slug), s, re.S)
        if not m: continue
        cd = re.search(r'<div class="card-footer">\s*<span>([^<]*)</span>', m.group(0))
        if not cd or cd.group(1).strip() == pdate: continue   # no refresh -> hands off
        fresh = card(p)
        s = s[:m.start()] + s[m.end():]
        if anchor0 not in s: continue
        s = s.replace(anchor0, anchor0 + fresh + '\n', 1)
        refreshed.append('%s -> %s' % (slug, pdate))
    if refreshed:
        open(IDX,'w',encoding='utf-8').write(s)
        print('refreshed + re-sorted %d card(s): %s' % (len(refreshed), ', '.join(refreshed)))
    # PICTURE PASS (2026-11-27). A post that has a "thumb" in posts-index.json but whose card still shows
    # the plain gradient (the GTA 6 desk guides published 19 to 27 Nov) gets its picture. Only the
    # card-thumbnail div of that one card changes; cards that already show a picture are left alone.
    pictured = []
    for p in posts:
        slug = p.get('slug'); thumb = p.get('thumb')
        if not slug or not thumb: continue
        m = re.search(r'(<a href="/blog/%s/" class="post-card".*?)(<div class="card-thumbnail" style="background: [^"]*;">.*?</div>\n?)' % re.escape(slug), s, re.S)
        if not m or '</a>' in m.group(1): continue
        title = p.get('title', '')
        pic = (f'<div class="card-thumbnail" style="background:#f3efe7;padding:0;overflow:hidden">'
               f'<img src="{esc(thumb)}" alt="{esc(title)}" width="1200" height="675" loading="lazy" decoding="async" '
               f'style="width:100%;height:100%;object-fit:cover;object-position:center;display:block"></div>\n')
        s = s[:m.start(2)] + pic + s[m.end(2):]
        pictured.append(slug)
    if pictured:
        open(IDX,'w',encoding='utf-8').write(s)
        print('card picture added for %d card(s): %s' % (len(pictured), ', '.join(pictured)))
    existing = set(re.findall(r'href="/blog/([a-z0-9-]+)/"', s))
    # newest first by date then by list order
    def keyf(p): return (p.get('date',''), )
    new = [p for p in posts if p.get('slug') and p['slug'] not in existing]
    new.sort(key=lambda p: p.get('date',''), reverse=True)
    if not new:
        print('blog index already in sync; no cards added'); return 0
    # ensure Industry News tab exists
    if 'data-category="Industry News"' not in s:
        s = s.replace(
          '<button class="cat-tab active" data-category="All">All</button>',
          '<button class="cat-tab active" data-category="All">All</button>\n'
          '<button class="cat-tab" data-category="Industry News">Industry News</button>', 1)
    cards = '\n'.join(card(p) for p in new)
    anchor = '<div class="posts-grid" id="postsGrid">\n'
    assert anchor in s, 'posts-grid anchor not found'
    s = s.replace(anchor, anchor + cards + '\n', 1)
    open(IDX,'w',encoding='utf-8').write(s)
    print(f'inserted {len(new)} card(s):', ', '.join(p['slug'] for p in new))
    return 0

if __name__ == '__main__':
    sys.exit(main())
