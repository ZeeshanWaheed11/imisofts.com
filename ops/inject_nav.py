#!/usr/bin/env python3
"""Add new service pages to the site-wide navigation: desktop mega-menu, mobile menu, footer.

Additive and idempotent. Clones the existing /ai-automation entry in each of the three
places so the markup and indentation match the surrounding nav exactly, then rewrites
href / title / description / icon. Skips any file that already links the new page, and
any file that has no nav.

Since 2026-11-14 it also adds top-level pages that are not services (see TOP): one plain
link in the desktop menu, one in the mobile menu and one in the footer, each placed right
after the link it follows. Same rules: additive, idempotent, nothing else is touched.

It also adds footer-only links (see FOOT): one link in the site footer and no menu entry.
Used for the newsdesk, because the desktop menu is full at nine links.

Run from the repo root:  python3 ops/inject_nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Service pages for the Services mega-menu ONLY.
# The AI-calling INDUSTRY pages are deliberately NOT here: they belong in the
# Industries dropdown and are owned by ops/restructure_nav.py. Listing them in both
# made the scripts fight, with inject re-adding them to the mega-menu every run.
# new service pages to wire in: (slug, nav title, mega-menu description, footer label, svg path d)
NEW = [
    ("/ai-voice-agents", "AI Voice Agents",
     "Compliant AI calling that books meetings",
     "AI Voice Agents",
     "M12 15a3 3 0 003-3V6a3 3 0 00-6 0v6a3 3 0 003 3zM19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"),
    ("/gohighlevel-white-label-saas", "White-Label SaaS",
     "Resell GoHighLevel as your own software",
     "White-Label SaaS",
     "M4 7h16M4 12h16M4 17h10M18 15l3 3-3 3"),
    ("/tcpa-compliant-ai-calling", "TCPA-Compliant Calling",
     "Consent, DNC and opt-out infrastructure",
     "TCPA-Compliant Calling",
     "M12 3l7.5 3v5.5c0 4.6-3.2 8.4-7.5 9.5-4.3-1.1-7.5-4.9-7.5-9.5V6L12 3zM9 12l2 2 4-4"),
    ("/ai-search-optimization", "AI Search Optimization",
     "Get named by ChatGPT and AI Overviews",
     "AI Search Optimization",
     "M11 4.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM15.8 15.8L21 21"),
    ("/email-infrastructure", "Email Infrastructure",
     "Domains, authentication and warm-up",
     "Email Infrastructure",
     "M3 7l9 6 9-6M4 5h16a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V6a1 1 0 011-1z"),
    ("/ui-ux-design", "UI/UX Design",
     "Research, Figma and design systems",
     "UI/UX Design",
     "M4 20h4L19 9a2.8 2.8 0 00-4-4L4 16zM13.5 6.5l4 4"),
    ("/blockchain-development", "Blockchain Development",
     "Smart contracts and Web3 apps",
     "Blockchain Development",
     "M12 3l8 4.5v9L12 21l-8-4.5v-9zM4 7.5l8 4.5 8-4.5M12 12v9"),
    ("/aws-cloud-migration", "AWS Cloud Migration",
     "Move to AWS with a tested cutover",
     "AWS Cloud Migration",
     "M7 18.5h10.5a4 4 0 00.6-7.95A5.5 5.5 0 007.4 9.1 4.75 4.75 0 007 18.5z"),
    ("/cybersecurity-services", "Cybersecurity Services",
     "Assessments, hardening, monitoring",
     "Cybersecurity Services",
     "M12 3l7.5 3v5.5c0 4.6-3.2 8.4-7.5 9.5-4.3-1.1-7.5-4.9-7.5-9.5V6L12 3zM9 12l2 2 4-4"),
    ("/salesforce-implementation", "Salesforce Implementation",
     "Sales Cloud setup, data and Flow",
     "Salesforce Implementation",
     "M4 5h16l-6 7.5V19l-4 1.5v-8z"),
    ("/hubspot-implementation", "HubSpot Implementation",
     "Onboarding, migration, workflows",
     "HubSpot Implementation",
     "M6 3.5a2.5 2.5 0 110 5 2.5 2.5 0 010-5zM18 3.5a2.5 2.5 0 110 5 2.5 2.5 0 010-5zM12 15.5a2.5 2.5 0 110 5 2.5 2.5 0 010-5zM8.5 6h7M7.3 8.2l3.5 7.6M16.7 8.2l-3.5 7.6"),
]

ANCHOR = "/ai-automation"   # clone the entry for this page, insert directly after it

# Entries that do not belong after /ai-automation name the link they follow (added 2026-11-16 for the six
# Development services; each one follows the previous one, so the menu keeps this order). Entries that are not
# listed here keep the default ANCHOR, exactly as before.
AFTER = {
    "/ui-ux-design": "/launch-your-saas",
    "/blockchain-development": "/ui-ux-design",
    "/aws-cloud-migration": "/blockchain-development",
    "/cybersecurity-services": "/aws-cloud-migration",
    "/salesforce-implementation": "/cybersecurity-services",
    "/hubspot-implementation": "/salesforce-implementation",
}

# Top-level pages that are not services: (slug, menu label, footer label, slug of the link it follows)
TOP = [
    ("/clients", "Clients", "Our Clients", "/case-studies"),
]

# Spacing of the desktop menu, so nine links stay on one line at every desktop width.
# Before "Clients" was added (2026-11-14) the tighter 20px spacing applied up to 1180px only.
# Now: 20px up to 1260px, and 12px up to 1100px (the desktop menu starts at 1025px).
NAV_FIT_OLD = "@media (max-width:1180px){.nav-menu{gap:20px}}"
NAV_FIT_NEW = "@media (max-width:1260px){.nav-menu{gap:20px}}@media (max-width:1100px){.nav-menu{gap:12px}}"

# Footer-only links: (href, footer label, the footer items it may follow, first one found wins).
# The whole item is compared (href and label), and only inside <footer>, so a breadcrumb or a
# list in the page body that links to the same address is never mistaken for it or changed.
FOOT = [
    ("/newsdesk/", "News", ('<li><a href="/blog">Blog</a></li>', '<li><a href="/blog/">Blog</a></li>')),
]

# The Industries hub (proposed 2026-11-16): one "All Industries" link at the top of the Industries
# dropdown, the Industries group of the mobile menu and the Industries column of the footer.
# (href, label, dropdown description, svg path d)
HUB = ("/industries", "All Industries", "Every industry we build for",
       "M4 4h6.5v6.5H4zM13.5 4H20v6.5h-6.5zM4 13.5h6.5V20H4zM13.5 13.5H20V20h-6.5z")

SKIP_DIRS = {".git", ".github", "node_modules", "ops", "content", "assets", "data"}


def mega_block(html, slug, title, desc, dpath, anchor=ANCHOR):
    """Clone the anchor's mega-item block and retarget it."""
    i = html.find('<a href="%s" class="mega-item">' % anchor)
    if i == -1:
        return None, None
    j = html.find("</a>", i)
    if j == -1:
        return None, None
    j += 4
    block = html[i:j]
    new = block.replace('href="%s"' % anchor, 'href="%s"' % slug, 1)
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
        anchor = AFTER.get(slug, ANCHOR)

        # 1. desktop mega-menu
        pos, blk = (None, None) if in_mega else mega_block(html, slug, title, desc, dpath, anchor)
        if pos:
            sep = "\n" + " " * 22
            html = html[:pos] + sep + blk + html[pos:]
            report["mega"] += 1

        # 2. mobile menu
        mob = '<a href="%s" class="mobile-service-link">' % anchor
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
        foot_anchor = '<li><a href="%s">' % anchor
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

    for slug, label, foot, after in TOP:
        # desktop menu, mobile menu: a plain link right after the link it follows, same indentation
        for cls in ("nav-link", "mobile-nav-link"):
            if '<a href="%s" class="%s">' % (slug, cls) in html:
                continue
            k = html.find('<a href="%s" class="%s">' % (after, cls))
            if k == -1:
                continue
            end = html.find("</a>", k) + 4
            ls = html.rfind("\n", 0, k)
            indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:k]).group(0)
            html = html[:end] + indent + '<a href="%s" class="%s">%s</a>' % (slug, cls, label) + html[end:]
            report["top"] += 1
        # footer
        if '<li><a href="%s">' % slug not in html:
            f = html.find('<li><a href="%s">' % after)
            if f != -1:
                fend = html.find("</li>", f) + 5
                ls = html.rfind("\n", 0, f)
                indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:f]).group(0)
                html = html[:fend] + indent + '<li><a href="%s">%s</a></li>' % (slug, foot) + html[fend:]
                report["top"] += 1
        # keep the longer desktop menu on one line
        if '<a href="%s" class="nav-link">' % slug in html and NAV_FIT_OLD in html:
            html = html.replace(NAV_FIT_OLD, NAV_FIT_NEW)

    for href, label, afters in FOOT:
        item = '<li><a href="%s">%s</a></li>' % (href, label)
        done = False
        for m in re.finditer(r"<footer\b", html):
            fi = m.start()
            fe = html.find("</footer>", fi)
            if fe == -1:
                fe = len(html)
            if item in html[fi:fe]:
                done = True          # already there
                break
        if done:
            continue
        for m in re.finditer(r"<footer\b", html):
            fi = m.start()
            fe = html.find("</footer>", fi)
            if fe == -1:
                fe = len(html)
            for after in afters:
                f = html.find(after, fi, fe)
                if f == -1:
                    continue
                fend = f + len(after)
                ls = html.rfind("\n", 0, f)
                indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:f]).group(0)
                html = html[:fend] + indent + item + html[fend:]
                report["foot"] += 1
                done = True
                break
            if done:
                break

    # ---- Industries hub link (desktop dropdown, mobile group, footer column) ----
    href, label, desc, dpath = HUB
    # 1. desktop: clone the first item of the Industries dropdown and put the copy in front of it
    if '<a href="%s" class="dropdown-link">' % href not in html:
        d = html.find('<div class="nav-dropdown" id="industriesDropdown">')
        s = html.find('<div class="dropdown-simple">', d) if d != -1 else -1
        k = html.find('<a href="', s) if s != -1 else -1
        if k != -1 and html[k:html.find('>', k)].endswith('class="dropdown-link"'):
            end = html.find("</a>", k) + 4
            blk = html[k:end]
            blk = re.sub(r'<a href="[^"]*"', '<a href="%s"' % href, blk, count=1)
            blk = re.sub(r'(<div class="dropdown-link-title">)[^<]*(</div>)', lambda m: m.group(1) + label + m.group(2), blk, count=1)
            blk = re.sub(r'(<div class="dropdown-link-desc">)[^<]*(</div>)', lambda m: m.group(1) + desc + m.group(2), blk, count=1)
            blk = re.sub(r'(<path stroke-linecap="round" stroke-linejoin="round" stroke-width="[^"]*" d=")[^"]*(")',
                         lambda m: m.group(1) + dpath + m.group(2), blk, count=1)
            ls = html.rfind("\n", 0, k)
            indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:k]).group(0)
            html = html[:k] + blk + indent + html[k:]
            report["hub"] += 1
    # 2. mobile: first link of the Industries group
    if '<a href="%s" class="mobile-service-link">' % href not in html:
        m = re.search(r'<div class="mobile-services-title"[^>]*>\s*Industries\s*<svg', html)
        c = html.find('<div class="mobile-section-content">', m.end()) if m else -1
        k = html.find('<a href="', c) if c != -1 else -1
        if k != -1 and html[k:html.find('>', k)].endswith('class="mobile-service-link"'):
            ls = html.rfind("\n", 0, k)
            indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:k]).group(0)
            html = html[:k] + '<a href="%s" class="mobile-service-link">%s</a>' % (href, label) + indent + html[k:]
            report["hub"] += 1
    # 3. footer: first item of the Industries column (only inside <footer>)
    fi = html.find("<footer")
    if fi != -1 and '<li><a href="%s">' % href not in html[fi:]:
        h = html.find('<span class="footer-heading">Industries</span>', fi)
        u = html.find('<ul class="footer-links">', h) if h != -1 else -1
        k = html.find('<li>', u) if u != -1 else -1
        if k != -1 and k < html.find('</ul>', u):
            ls = html.rfind("\n", 0, k)
            indent = "" if ls == -1 else "\n" + re.match(r"[ \t]*", html[ls + 1:k]).group(0)
            html = html[:k] + '<li><a href="%s">%s</a></li>' % (href, label) + indent + html[k:]
            report["hub"] += 1

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return True
    return False


def main():
    report = {"mega": 0, "mobile": 0, "footer": 0, "top": 0, "foot": 0, "hub": 0}
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
    print("top-level links added -> %d" % report["top"])
    print("footer-only links added -> %d" % report["foot"])
    print("industries hub links added -> %d" % report["hub"])
    if changed == 0:
        print("nothing to do (already wired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
