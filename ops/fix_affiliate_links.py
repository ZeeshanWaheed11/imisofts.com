#!/usr/bin/env python3
"""Idempotent blog-post normalizer for imisofts.com.

1. Swap the old/non-earning Instantly link to the correct referral link.
2. Ensure every Apollo/Instantly affiliate anchor has target=_blank +
   rel="noopener noreferrer sponsored" (also collapses malformed duplicated tags).
3. Insert a visible affiliate disclosure once per post that carries an affiliate link.
4. Remove published AI-scaffolding sections (FAQ Schema / Internal Links /
   External Links / Image Alt Suggestions / Quick Answer) AND their table-of-contents
   entries, which should never have shipped.

Safe to re-run. Usage: python3 ops/fix_affiliate_links.py [repo_root]
"""
import os, re, sys, glob

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
OLD_INSTANTLY = "https://instantly.ai/?via=coldemailmarketing"
NEW_INSTANTLY = "https://refer.instantly.ai/oovph6ghwnaa"
APOLLO = "https://get.apollo.io/u5ocuv7me9t2"
AFF_URLS = [APOLLO, NEW_INSTANTLY]
JUNK_IDS = r"faq-schema|internal-links|external-links|image-alt-suggestions|quick-answer"

DISCLOSURE = ('<p class="affiliate-disclosure" style="font-size:14px;line-height:1.6;'
              'color:#475569;background:#f8fafc;border-left:3px solid #F45407;'
              'padding:11px 15px;border-radius:6px;margin:0 0 22px;">'
              '<strong>Affiliate disclosure:</strong> some links in this article are partner links. '
              'If you start a paid plan through them, imisofts may earn a commission at no extra cost to you. '
              'We only recommend tools we actually use to run client campaigns.</p>')

anchor_re = re.compile(r'<a\b[^>]*?href="(' + '|'.join(re.escape(u) for u in AFF_URLS) + r')"[^>]*>')
style_re = re.compile(r'style="[^"]*"')
DISCL_PRESENT = re.compile(r'affiliate[ -]disclosure|earn a commission|may earn', re.I)
JUNK_RE = re.compile(r'<h2 id="(?:' + JUNK_IDS + r')"[^>]*>.*?(?=<h2|<section|</article|</main|<footer)', re.DOTALL)
TOC_JUNK_RE = re.compile(r'\s*<li>\s*<a href="#(?:' + JUNK_IDS + r')"[^>]*>.*?</a>\s*</li>', re.DOTALL)

def normalize_anchor(m):
    tag, url = m.group(0), m.group(1)
    sm = style_re.search(tag)
    style = (' ' + sm.group(0)) if sm else ''
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer sponsored"{style}>'

def process(html):
    changed = False
    if OLD_INSTANTLY in html:
        html = html.replace(OLD_INSTANTLY, NEW_INSTANTLY); changed = True
    for rx, rep in ((anchor_re, normalize_anchor), (JUNK_RE, ''), (TOC_JUNK_RE, '')):
        new = rx.sub(rep, html)
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
    n=swaps=discl=junk=0
    for f in sorted(files):
        html = open(f, encoding="utf-8").read()
        had_old = OLD_INSTANTLY in html
        had_discl = bool(DISCL_PRESENT.search(html))
        had_junk = bool(JUNK_RE.search(html)) or bool(TOC_JUNK_RE.search(html))
        new, changed = process(html)
        if changed:
            open(f,"w",encoding="utf-8").write(new); n+=1
            if had_old: swaps+=1
            if not had_discl and 'affiliate-disclosure' in new: discl+=1
            if had_junk: junk+=1
    print(f"files changed: {n}; instantly swaps: {swaps}; disclosures added: {discl}; junk-cleaned: {junk}")

if __name__ == "__main__":
    main()
