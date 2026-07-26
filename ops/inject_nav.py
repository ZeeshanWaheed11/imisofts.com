#!/usr/bin/env python3
"""Add new service pages to the site-wide navigation: desktop mega-menu, mobile menu, footer.

Additive and idempotent. Clones the existing /ai-automation entry in each of the three
places so the markup and indentation match the surrounding nav exactly, then rewrites
href / title / description / icon. Skips any file that already links the new page, and
any file that has no nav.

Run from the repo root:  python3 ops/inject_nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# new service pages to wire in: (slug, nav title, mega-menu description, footer label, svg path d)
NEW = [
    ("/ai-voice-agents", "AI Voice Agents",
     "Compliant AI calling that books meetings",
     "AI Voice Agents",
     "M12 15a3 3 0 003-3V6a3 3 0 00-6 0v6a3 3 0 003 3zM19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"),
]

ANCHOR = "/ai-automation"   # clone the entry for this page, insert directly after it

SKIP_DIRS = {".git", ".github", "node_modules", "ops", "content", "assets", "data"}


def mega_block(html, slug, title, desc, dpath):
    """Clone the anchor's mega-item block and retarget it."""
    i = html.find('<a href="%s" class="mega-item">' % ANCHOR)
    if i == -1:
        return None, None
    j = html.find("</a>", i)
    if j == -1:
        return None, None
    j += 4
    block = html[i:j]
    new = block.replace('href="%s"' % ANCHOR, 'href="%s"' % slug, 1)
    new = re.sub(r'(<div class="mega-item-title">)[^<]*(</div>)',
                 lambda m: m.group(1) + title + m.group(2), new, count=1)
    new = re.sub(r'(<div class="mega-item-desc">)[^<]*(</div>)',
                 lambda m: m.group(1) + desc + m.group(2), new, count=1)
    new = re.sub(r'(<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d=")[^"]*(")',
                 lambda m: m.group(1) + dpath + m.group(2), new, count=1)
    return j, new


def process(path, report):
    try:
        html = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return False
    if 'class="mega-item"' not in html and 'class="mobile-service-link"' not in html \
       and '<li><a href="%s">' % ANCHOR not in html:
        return False

    orig = html
    for slug, title, desc, foot, dpath in NEW:
        # Check the NAV markup specifically, not just the slug. A service page contains
        # its own URL in canonical/og tags, so a plain "slug in html" test made the page
        # skip itself and end up as the only page missing its own nav entry.
        in_mega   = '<a href="%s" class="mega-item">' % slug in html
        in_mobile = '<a href="%s" class="mobile-service-link">' % slug in html
        in_footer = '<li><a href="%s">' % slug in html
        if in_mega and in_mobile and in_footer:
            continue  # fully wired

        # 1. desktop mega-menu
        pos, blk = (None, None) if in_mega else mega_block(html, slug, title, desc, dpath)
        if pos:
            sep = "\n" + " " * 22
            html = html[:pos] + sep + blk + html[pos:]
            report["mega"] += 1

        # 2. mobile menu
        mob = '<a href="%s" class="mobile-service-link">' % ANCHOR
        k = -1 if in_mobile else html.find(mob)
        if k != -1:
            end = html.find("</a>", k) + 4
            indent = ""
            ls = html.rfind("\n", 0, k)
            if ls != -1:
                indent = "\n" + re.match(r"[ \t]*", html[ls + 1:k]).group(0)
            html = html[:end] + indent + \
                '<a href="%s" class="mobile-service-link">%s</a>' % (slug, title) + html[end:]
            report["mobile"] += 1

        # 3. footer
        foot_anchor = '<li><a href="%s">' % ANCHOR
        f = -1 if in_footer else html.find(foot_anchor)
        if f != -1:
            fend = html.find("</li>", f) + 5
            indent = ""
            ls = html.rfind("\n", 0, f)
            if ls != -1:
                indent = "\n" + re.match(r"[ \t]*", html[ls + 1:f]).group(0)
            html = html[:fend] + indent + \
                '<li><a href="%s">%s</a></li>' % (slug, foot) + html[fend:]
            report["footer"] += 1

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return True
    return False


def main():
    report = {"mega": 0, "mobile": 0, "footer": 0}
    changed = scanned = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            scanned += 1
            if process(os.path.join(dirpath, fn), report):
                changed += 1
    print("scanned %d html files | updated %d" % (scanned, changed))
    print("insertions -> mega-menu %d | mobile %d | footer %d"
          % (report["mega"], report["mobile"], report["footer"]))
    if changed == 0:
        print("nothing to do (already wired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
