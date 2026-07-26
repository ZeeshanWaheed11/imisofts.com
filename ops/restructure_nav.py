#!/usr/bin/env python3
"""Navigation structure and styling.

Services mega-menu, 4 categories, none larger than 6:
  Growth             cold email, lead gen, digital marketing, email infra, GHL services, white-label SaaS
  AI & Automation    ai automation, voice agents, TCPA calling, AI search, OpenClaw
  Development        unchanged
  Hire a Specialist  unchanged

Also:
  - a distinct icon per category (they previously shared the code glyph)
  - breathing room between the category list and the Contact Us card
  - the Industries dropdown restyled to match the Services mega-menu

Moves existing markup rather than regenerating it, so item icons and copy are preserved.
Idempotent. Run from repo root: python3 ops/restructure_nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".github", "node_modules", "ops", "content", "assets", "data"}
MARKER = "nav-cat-fix-3"

PANELS = [
    ("growth", "Growth", ["/cold-email-marketing", "/lead-generation", "/digital-marketing",
                          "/email-infrastructure", "/gohighlevel-services", "/gohighlevel-white-label-saas"]),
    ("ai", "AI &amp; Automation", ["/ai-automation", "/ai-voice-agents", "/tcpa-compliant-ai-calling",
                                   "/ai-search-optimization", "/openclaw-setup"]),
    ("development", "Development", ["/web-development", "/ecommerce", "/crm-development",
                                    "/shopify-apps", "/ai-mobile-apps", "/launch-your-saas"]),
    ("specialist", "Hire a Specialist", ["/hire-cold-email-expert", "/hire-gohighlevel-developer",
                                         "/hire-n8n-developer", "/hire-ai-engineer", "/hire-shopify-expert"]),
]

# distinct category icon per tab (first svg path inside the tab)
TAB_ICONS = {
    "growth":      "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
    "ai":          "M9 3v2m6-2v2M9 19v2m6-2v2M3 9h2M3 15h2m14-6h2m-2 6h2M7 7h10v10H7zM10.5 10.5h3v3h-3z",
    "development": "M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4",
    "specialist":  "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
}

TO_INDUSTRIES = [
    ("/ai-calling-home-services", "AI Calling for Home Services", "Answer every call, book every job",
     "M3 11l9-8 9 8M5 10v10h14V10"),
    ("/ai-receptionist-healthcare", "AI Receptionist for Clinics", "Fewer no-shows, filled cancellations",
     "M12 7v10M7 12h10M4.5 4.5h15v15h-15z"),
    ("/ai-calling-mortgage-lending", "AI Calling for Mortgage", "Contact every lead in under a minute",
     "M3 10l9-6 9 6v10H3V10zM9 20v-6h6v6"),
    ("/ai-calling-insurance", "AI Calling for Insurance", "Reach the leads you paid for",
     "M12 3l7.5 3v5.5c0 4.6-3.2 8.4-7.5 9.5-4.3-1.1-7.5-4.9-7.5-9.5V6L12 3z"),
    ("/ai-intake-law-firms", "AI Intake for Law Firms", "Screen and book every case enquiry",
     "M12 3v18M5 7h14M7 7l-3 7h6l-3-7zM17 7l-3 7h6l-3-7z"),
]

NAV_CSS = """<style id="%s">
/* space between the category list and the Contact Us card */
.mega-sidebar .mega-cta-card{margin-top:28px}
.mega-sidebar{display:flex;flex-direction:column}
.mega-panel,.mega-sidebar{max-height:min(72vh,580px);overflow-y:auto}

/* Industries dropdown styled to match the Services mega-menu */
.nav-dropdown-menu--narrow{width:auto}
.dropdown-simple{display:grid;grid-template-columns:1fr 1fr;gap:2px;min-width:660px;padding:20px}
.dropdown-link{padding:14px 16px;border-radius:10px;gap:14px;align-items:flex-start}
.dropdown-link:hover{background:linear-gradient(135deg,#fff9f6 0%%,#fff4ef 100%%)}
.dropdown-link svg{width:20px;height:20px;padding:8px;background:linear-gradient(135deg,#fff4ef 0%%,#ffe8dd 100%%);
 border-radius:10px;color:#F45407;flex-shrink:0}
.dropdown-link:hover svg{background:#F45407;color:#fff}
.dropdown-link-title{font-size:15px;font-weight:600;color:#1a1a1a;margin-bottom:3px}
.dropdown-link-desc{font-size:13px;color:#6b7280;line-height:1.5}
@media(max-width:900px){.dropdown-simple{grid-template-columns:1fr;min-width:0;padding:14px}}
</style>
""" % MARKER


def match_div(s, start):
    i, depth = start, 0
    while i < len(s):
        o = s.find("<div", i + 1)
        c = s.find("</div>", i + 1)
        if c == -1:
            return -1
        if o != -1 and o < c:
            depth += 1; i = o
        else:
            if depth == 0:
                return c + len("</div>")
            depth -= 1; i = c
    return -1


def process(path, rep):
    try:
        html = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return False
    if 'class="mega-tab' not in html or '<div class="mega-content">' not in html:
        return False
    if 'id="%s"' % MARKER in html:
        return False

    orig = html
    # drop any earlier version of our style block
    html = re.sub(r'<style id="nav-cat-fix[^"]*">[\s\S]*?</style>\s*', '', html)

    blocks = {}
    for m in re.finditer(r'<a href="(/[a-z0-9\-]+)" class="mega-item">[\s\S]*?</a>', html):
        blocks.setdefault(m.group(1), m.group(0))

    # ---------- 1. Industries dropdown gains the industry pages ----------
    links = list(re.finditer(r'<a href="(/[a-z0-9\-]+)" class="dropdown-link">[\s\S]*?</a>', html))
    if links:
        tmpl = links[0].group(0)
        have = {m.group(1) for m in links}
        add = ""
        for href, title, desc, dpath in TO_INDUSTRIES:
            if href in have:
                continue
            blk = re.sub(r'<a href="[^"]*"', '<a href="%s"' % href, tmpl, count=1)
            blk = re.sub(r'(<div class="dropdown-link-title">)[^<]*(</div>)',
                         lambda m: m.group(1) + title + m.group(2), blk, count=1)
            blk = re.sub(r'(<div class="dropdown-link-desc">)[^<]*(</div>)',
                         lambda m: m.group(1) + desc + m.group(2), blk, count=1)
            blk = re.sub(r'(<path stroke-linecap="round" stroke-linejoin="round" stroke-width="[^"]*" d=")[^"]*(")',
                         lambda m: m.group(1) + dpath + m.group(2), blk, count=1)
            add += "\n                " + blk
        if add:
            last = links[-1]
            html = html[:last.end()] + add + html[last.end():]
            rep["industries"] += 1

    # ---------- 2. rebuild the Services panels ----------
    mc = html.find('<div class="mega-content">')
    mc_end = match_div(html, mc) if mc != -1 else -1
    if mc_end != -1:
        out = []
        for idx, (pid, label, hrefs) in enumerate(PANELS):
            wanted = [blocks[h] for h in hrefs if h in blocks]
            if not wanted:
                continue
            grid = "\n                      ".join(wanted)
            cls = "mega-panel active" if idx == 0 else "mega-panel"
            out.append('<div class="%s" id="panel-%s">\n                    <div class="mega-grid">\n                      %s\n                    </div>\n                  </div>'
                       % (cls, pid, grid))
        if out:
            html = (html[:mc] + '<div class="mega-content">\n                  '
                    + "\n                  ".join(out) + '\n                </div>' + html[mc_end:])
            rep["panels"] += 1

    # ---------- 3. tabs: keep only ours, in order, with distinct icons ----------
    tabs = list(re.finditer(r'<div class="mega-tab[^"]*" data-tab="([^"]+)">[\s\S]*?</div>\s*(?=<div class="mega-tab|<div class="mega-cta-card)', html))
    if tabs:
        tmpl = tabs[0].group(0)
        new_tabs = []
        for idx, (pid, label, _) in enumerate(PANELS):
            src = next((t.group(0) for t in tabs if t.group(1) == pid), tmpl)
            blk = re.sub(r'class="mega-tab[^"]*"', 'class="mega-tab active"' if idx == 0 else 'class="mega-tab"', src, count=1)
            blk = re.sub(r'data-tab="[^"]*"', 'data-tab="%s"' % pid, blk, count=1)
            blk = re.sub(r'<span>[^<]*</span>', '<span>%s</span>' % label, blk, count=1)
            if pid in TAB_ICONS:
                blk = re.sub(r'(<path stroke-linecap="round" stroke-linejoin="round" stroke-width="[^"]*" d=")[^"]*(")',
                             lambda m: m.group(1) + TAB_ICONS[pid] + m.group(2), blk, count=1)
            new_tabs.append(blk.rstrip())
        html = html[:tabs[0].start()] + "\n                  ".join(new_tabs) + "\n                  " + html[tabs[-1].end():]
        rep["tabs"] += 1

    # ---------- 4. mobile groups ----------
    mob = {}
    for m in re.finditer(r'<a href="(/[a-z0-9\-]+)" class="mobile-service-link">([^<]*)</a>', html):
        mob.setdefault(m.group(1), m.group(0))
    gm = re.search(r'(<div class="mobile-section-group">[^<]*</div>)((?:\s*(?:<div class="mobile-section-group">[^<]*</div>|<a href="[^"]*" class="mobile-service-link">[^<]*</a>))+)', html)
    if gm:
        parts = []
        for pid, label, hrefs in PANELS:
            ls = [mob[h] for h in hrefs if h in mob]
            if not ls:
                continue
            parts.append('<div class="mobile-section-group">%s</div>\n              ' % label.replace("&amp;", "and")
                         + "\n              ".join(ls))
        if parts:
            html = html[:gm.start()] + "\n              ".join(parts) + html[gm.end():]
            rep["mobile"] += 1

    html = html.replace("</head>", NAV_CSS + "</head>", 1)

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return True
    return False


def main():
    rep = {"tabs": 0, "panels": 0, "industries": 0, "mobile": 0}
    changed = scanned = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            scanned += 1
            if process(os.path.join(dirpath, fn), rep):
                changed += 1
    print("scanned %d | restructured %d" % (scanned, changed))
    print("tabs %d | panels %d | industries %d | mobile %d"
          % (rep["tabs"], rep["panels"], rep["industries"], rep["mobile"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
