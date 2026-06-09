#!/usr/bin/env python3
"""Idempotent affiliate-link normalizer for imisofts.com blog posts.

1. Swap the old/non-earning Instantly link to the correct referral link.
2. Ensure every Apollo/Instantly affiliate anchor has target=_blank +
   rel="noopener noreferrer sponsored" (also collapses malformed duplicated tags).
3. Insert a visible affiliate disclosure once per post that carries an affiliate link.

Safe to re-run. Usage: python3 ops/fix_affiliate_links.py [repo_root]
"""
import os, re, sys, glob

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OLD_INSTANTLY = "https://instantly.ai/?via=coldemailmarketing"
NEW_INSTANTLY = "https://refer.instantly.ai/oovph6ghwnaa"
APOLLO = "https://get.apollo.io/u5ocuv7me9t2"
AFF_URLS = [APOLLO, NEW_INSTANTLY]

DISCLOSURE = ('<p class="affiliate-disclosure" style="font-size:14px;line-height:1.6;'
              'color:#475569;background:#f8fafc;border-left:3px solid #F45407;'
              'padding:11px 15px;border-radius:6px;margin:0 0 22px;">'
              '<strong>Affiliate disclosure:</strong> some links in this article are partner links. '
              'If you start a paid plan through them, imisofts may earn a commission at no extra cost to you. '
              'We only recommend tools we actually use to run client campaigns.</p>')

anchor_re = re.compile(r'<a\b[^>]*?href="(' + '|'.join(re.escape(u) for u in AFF_URLS) + r')"[^>]*>')
style_re = re.compile(r'style="[^"]*"')
DISCL_PRESENT = re.compile(r'affiliate[ -]disclosure|earn a commission|may earn', re.I)

def normalize_anchor(m):
    tag, url = m.group(0), m.group(1)
    sm = style_re.search(tag)
    style = (' ' + sm.group(0)) if sm else ''
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer sponsored"{style}>'

def process(html):
    changed = False
    if OLD_INSTANTLY in html:
        html = html.replace(OLD_INSTANTLY, NEW_INSTANTLY); changed = True
    new = anchor_re.sub(normalize_anchor, html)
    if new != html:
        html = new; changed = True
    has_aff = any(u in html for u in AFF_URLS)
    if has_aff and not DISCL_PRESENT.search(html) and '<article class="article-content">' in html:
        html = html.replace('<article class="article-content">',
                             '<article class="article-content">\n' + DISCLOSURE, 1)
        changed = True
    return html, changed

def main():
    files = glob.glob(os.path.join(ROOT, "blog", "*", "index.html"))
    n_changed = swaps = discl = 0
    for f in sorted(files):
        with open(f, encoding="utf-8") as fh: html = fh.read()
        had_old = OLD_INSTANTLY in html
        had_discl = bool(DISCL_PRESENT.search(html))
        new, changed = process(html)
        if changed:
            with open(f, "w", encoding="utf-8") as fh: fh.write(new)
            n_changed += 1
            if had_old: swaps += 1
            if not had_discl and 'affiliate-disclosure' in new: discl += 1
    print(f"files changed: {n_changed}; instantly-link swaps: {swaps}; disclosures added: {discl}")

if __name__ == "__main__":
    main()
