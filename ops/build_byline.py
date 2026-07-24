#!/usr/bin/env python3
"""Founder Byline -> site index wiring (additive, idempotent).

Reads content/byline/*.json metadata specs, one per already-built Founder Byline page
(the page HTML lives at blog/<slug>/index.html and is committed separately), and
ADDITIVELY wires each into:
  - blog/posts-index.json  (category "Founder's Playbook")
  - sitemap.xml            (evergreen <url>, not news-sitemap)
  - blog/index.html        via ops/sync_blog_index.py (cards) + ensures the "Founder's Playbook" cat-tab

It never rebuilds article HTML and never touches news / affiliate / NL-DE content.
Idempotent: re-running adds nothing once everything is wired.

Trigger: .github/workflows/publish-byline.yml on push to content/byline/** or manual dispatch.
"""
import json, os, re, sys, subprocess, html as _html

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(ROOT, 'content', 'byline')
PJSON    = os.path.join(ROOT, 'blog', 'posts-index.json')
IDX      = os.path.join(ROOT, 'blog', 'index.html')
SITEMAP  = os.path.join(ROOT, 'sitemap.xml')
SYNC     = os.path.join(ROOT, 'ops', 'sync_blog_index.py')

CATEGORY = "Founder's Playbook"
CAT_ATTR = _html.escape(CATEGORY, quote=True)   # -> Founder&#x27;s Playbook (matches sync_blog_index card() esc)


def load_specs():
    out = []
    if not os.path.isdir(SPEC_DIR):
        return out
    for fn in sorted(os.listdir(SPEC_DIR)):
        if fn.endswith('.json'):
            with open(os.path.join(SPEC_DIR, fn), encoding='utf-8') as f:
                sp = json.load(f)
                if sp.get('slug'):
                    out.append(sp)
    return out


def wire_posts_index(specs):
    posts = json.load(open(PJSON, encoding='utf-8'))
    wrapped = isinstance(posts, dict)
    lst = posts.get('posts', []) if wrapped else posts
    have = {p.get('slug') for p in lst}
    added = []
    for sp in specs:
        slug = sp['slug']
        if slug in have:
            continue
        lst.append({
            "number": len(lst) + 1,
            "filename": "%s/index.html" % slug,
            "title": sp['title'],
            "meta_description": sp['meta_description'],
            "url_slug": "/blog/%s" % slug,
            "primary_keyword": sp.get('primary_keyword', ''),
            "secondary_keywords": sp.get('secondary_keywords', ''),
            "category": CATEGORY,
            "word_count_target": str(sp.get('word_count', 1000)),
            "schema_type": "BlogPosting",
            "author": "Zeeshan Waheed",
            "date": sp['date'],
            "slug": slug,
            "word_count": sp.get('word_count', 1000),
            "read_time": sp.get('read_time', 5),
            "has_faq": True,
            "category_normalized": CATEGORY,
        })
        have.add(slug)
        added.append(slug)
    if added:
        with open(PJSON, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
            f.write('\n')
    return added


def wire_sitemap(specs):
    if not os.path.exists(SITEMAP):
        return []
    s = open(SITEMAP, encoding='utf-8').read()
    added = []
    for sp in specs:
        loc = "https://imisofts.com/blog/%s/" % sp['slug']
        if loc in s:
            continue
        block = ("<url>\n<loc>%s</loc>\n<lastmod>%s</lastmod>\n"
                 "<changefreq>monthly</changefreq>\n<priority>0.7</priority>\n</url>\n") % (loc, sp['date'])
        s = s.replace('</urlset>', block + '</urlset>', 1)
        added.append(sp['slug'])
    if added:
        open(SITEMAP, 'w', encoding='utf-8').write(s)
    return added


def ensure_tab():
    """Add the 'Founder's Playbook' filter tab once (sync_blog_index only auto-adds Industry News)."""
    s = open(IDX, encoding='utf-8').read()
    tab_btn = '<button class="cat-tab" data-category="%s">%s</button>' % (CAT_ATTR, CAT_ATTR)
    if tab_btn in s:
        return False
    all_btn = '<button class="cat-tab active" data-category="All">All</button>'
    if all_btn not in s:
        print('WARN: All-tab anchor not found; tab not inserted')
        return False
    s = s.replace(all_btn, all_btn + '\n' + tab_btn, 1)
    open(IDX, 'w', encoding='utf-8').write(s)
    return True


def main():
    specs = load_specs()
    if not specs:
        print('no byline specs found; nothing to do')
        return 0
    before = open(IDX, encoding='utf-8').read().count('class="post-card"')
    pi = wire_posts_index(specs)
    sm = wire_sitemap(specs)
    # Card them on /blog using the SAME sync the news engine uses (additive + idempotent).
    subprocess.run([sys.executable, SYNC], check=True, cwd=ROOT)
    tab = ensure_tab()
    after = open(IDX, encoding='utf-8').read().count('class="post-card"')
    # SAFETY: the grid must never shrink, and our new cards must have landed.
    assert after >= before + len(pi), 'card count sanity failed: %d -> %d (added %d)' % (before, after, len(pi))
    print('posts-index +%d %s | sitemap +%d %s | tab_added=%s | cards %d -> %d'
          % (len(pi), pi, len(sm), sm, tab, before, after))
    return 0


if __name__ == '__main__':
    sys.exit(main())
