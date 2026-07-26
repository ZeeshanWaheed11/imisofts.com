#!/usr/bin/env python3
"""Reorganise the navigation so no panel overflows the screen.

Before: Services > Growth held 16 items and ran off the bottom of the viewport.

After:
  Services mega-menu, 5 categories, none larger than 6
    Growth            cold email, lead gen, digital marketing, email infrastructure
    AI & Automation   ai automation, voice agents, TCPA calling, AI search, OpenClaw
    GoHighLevel       GHL services, white-label SaaS
    Development       unchanged
    Hire a Specialist unchanged
  Industries dropdown gains the 5 AI-calling industry pages and becomes 2 columns.

Moves existing markup rather than regenerating it, so styling and icons are preserved.
Idempotent. Run from repo root: python3 ops/restructure_nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".github", "node_modules", "ops", "content", "assets", "data"}

PANELS = [
    ("growth", "Growth", ["/cold-email-marketing", "/lead-generation", "/digital-marketing", "/email-infrastructure"]),
    ("ai", "AI &amp; Automation", ["/ai-automation", "/ai-voice-agents", "/tcpa-compliant-ai-calling",
                                   "/ai-search-optimization", "/openclaw-setup"]),
    ("gohighlevel", "GoHighLevel", ["/gohighlevel-services", "/gohighlevel-white-label-saas"]),
    ("development", "Development", ["/web-development", "/ecommerce", "/crm-development",
                                    "/shopify-apps", "/ai-mobile-apps", "/launch-your-saas"]),
    ("specialist", "Hire a Specialist", ["/hire-cold-email-expert", "/hire-gohighlevel-developer",
                                         "/hire-n8n-developer", "/hire-ai-engineer", "/hire-shopify-expert"]),
]

# industry pages that move OUT of Services and INTO the Industries dropdown
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

NAV_CSS = """<style id="nav-cat-fix">
/* Industries dropdown: two columns so a longer list still fits on screen */
.nav-dropdown-menu--narrow{width:auto}
.dropdown-simple{display:grid;grid-template-columns:1fr 1fr;gap:2px;min-width:640px}
.mega-panel{max-height:min(70vh,560px);overflow-y:auto}
.mega-sidebar{max-height:min(70vh,560px);overflow-y:auto}
@media(max-width:900px){.dropdown-simple{grid-template-columns:1fr;min-width:0}}
</style>
"""


def mega_blocks(html):
    """href -> full <a class="mega-item"> block."""
    out = {}
    for m in re.finditer(r'<a href="(/[a-z0-9\-]+)" class="mega-item">[\s\S]*?</a>', html):
        out.setdefault(m.group(1), m.group(0))
    return out


def build_dropdown_link(template, href, title, desc, dpath):
    blk = template
    blk = re.sub(r'<a href="[^"]*"', '<a href="%s"' % href, blk, count=1)
    blk = re.sub(r'(<div class="dropdown-link-title">)[^<]*(</div>)',
                 lambda m: m.group(1) + title + m.group(2), blk, count=1)
    blk = re.sub(r'(<div class="dropdown-link-desc">)[^<]*(</div>)',
                 lambda m: m.group(1) + desc + m.group(2), blk, count=1)
    blk = re.sub(r'(<path stroke-linecap="round" stroke-linejoin="round" stroke-width="[^"]*" d=")[^"]*(")',
                 lambda m: m.group(1) + dpath + m.group(2), blk, count=1)
    return blk


def process(path, rep):
    try:
        html = open(path, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        return False
    if 'class="mega-tab' not in html or 'id="panel-growth"' not in html:
        return False
    if 'id="nav-cat-fix"' in html:
        return False  # already restructured

    orig = html
    blocks = mega_blocks(html)

    # ---------- 1. Industries dropdown ----------
    dl = re.search(r'<a href="/cold-email-saas" class="dropdown-link">[\s\S]*?</a>', html)
    if dl:
        tmpl = dl.group(0)
        add = ""
        for href, title, desc, dpath in TO_INDUSTRIES:
            if 'href="%s" class="dropdown-link"' % href in html:
                continue
            add += "\n                " + build_dropdown_link(tmpl, href, title, desc, dpath)
        if add:
            end = dl.end()
            # append after the LAST existing dropdown-link in that container
            last = None
            for m in re.finditer(r'<a href="/[a-z0-9\-]+" class="dropdown-link">[\s\S]*?</a>', html):
                last = m
            html = html[:last.end()] + add + html[last.end():]
            rep["industries"] += len(TO_INDUSTRIES)

    # ---------- 2. rebuild the Services panels ----------
    # Regex cannot delimit a panel because mega-item blocks contain nested <div>s, so
    # find the mega-content container by matching div depth and regenerate it wholesale.
    def match_div(s, start):
        """start = index of a '<div'. Return index just past its matching '</div>'."""
        i, depth = start, 0
        while i < len(s):
            o = s.find("<div", i + 1)
            c = s.find("</div>", i + 1)
            if c == -1:
                return -1
            if o != -1 and o < c:
                depth += 1
                i = o
            else:
                if depth == 0:
                    return c + len("</div>")
                depth -= 1
                i = c
        return -1

    mc = html.find('<div class="mega-content">')
    if mc != -1:
        mc_end = match_div(html, mc)
        if mc_end != -1:
            panels_html = []
            for idx, (pid, label, hrefs) in enumerate(PANELS):
                wanted = [blocks[h] for h in hrefs if h in blocks]
                if not wanted:
                    continue
                grid = "\n                      ".join(wanted)
                cls = "mega-panel active" if idx == 0 else "mega-panel"
                panels_html.append(
                    '<div class="%s" id="panel-%s">\n                    <div class="mega-grid">\n                      %s\n                    </div>\n                  </div>'
                    % (cls, pid, grid))
                rep["panels"] += 1
            if panels_html:
                new_mc = ('<div class="mega-content">\n                  '
                          + "\n                  ".join(panels_html)
                          + '\n                </div>')
                html = html[:mc] + new_mc + html[mc_end:]

    # ---------- 3. sidebar tabs ----------
    tabm = re.search(r'<div class="mega-tab" data-tab="development">[\s\S]*?</div>\s*(?=<div class="mega-tab|<div class="mega-cta-card)', html)
    if tabm:
        tab_tmpl = tabm.group(0)
        for pid, label, _ in PANELS:
            if 'data-tab="%s"' % pid in html:
                continue
            newtab = tab_tmpl.replace('data-tab="development"', 'data-tab="%s"' % pid, 1)
            newtab = re.sub(r'<span>[^<]*</span>', '<span>%s</span>' % label, newtab, count=1)
            html = html.replace('<div class="mega-tab" data-tab="development">',
                                newtab + '<div class="mega-tab" data-tab="development">', 1)
            rep["tabs"] += 1

    # ---------- 4. mobile menu groups ----------
    mob = {}
    for m in re.finditer(r'<a href="(/[a-z0-9\-]+)" class="mobile-service-link">([^<]*)</a>', html):
        mob.setdefault(m.group(1), m.group(0))
    gm = re.search(r'(<div class="mobile-section-group">Growth</div>)((?:\s*<a href="[^"]*" class="mobile-service-link">[^<]*</a>)+)', html)
    if gm:
        parts = []
        for pid, label, hrefs in PANELS:
            if pid in ("development", "specialist"):
                continue
            links = [mob[h] for h in hrefs if h in mob]
            if not links:
                continue
            plain = label.replace("&amp;", "and")
            parts.append('<div class="mobile-section-group">%s</div>\n              ' % plain +
                         "\n              ".join(links))
        if parts:
            html = html[:gm.start()] + "\n              ".join(parts) + html[gm.end():]
            rep["mobile"] += 1

    # ---------- 5. css ----------
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
    print("tabs added %d | panels added %d | industries links %d | mobile regrouped %d"
          % (rep["tabs"], rep["panels"], rep["industries"], rep["mobile"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
