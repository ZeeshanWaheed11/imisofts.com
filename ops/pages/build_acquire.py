"""/acquire: imisofts is for sale, sold directly (owner request 27 Nov 2026).

Version 2 (same day): Zeeshan said the first version was "not appealing and non branded", so the page was
rebuilt in the homepage design language with brand visuals: real screenshots of the site in browser frames,
the logo mark, the founder's photo and orange stat numbers.

Scope set by Zeeshan: imisofts.com, the cold email infrastructure that generates our own leads, and a few
monthly retainers (details by email). Figures: DR 27 (Ahrefs, checked 27 Nov 2026) and 8K to 10K monthly
visitors (owner's figure). Other numbers come from the site itself (articles, service pages, tools).

Version 2.1 (same day): the figures box under the hero became six tiles with icons, notes and a count-up,
after Zeeshan asked to improve it. On a phone it is a 2 by 3 grid (the old band left one figure alone on a row).

Images live in /assets/acquire/ (screenshots are taken from the site itself; see the vault note).
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import page, esc, ROOT
from geo_css import GEO_CSS

SITE = 'https://imisofts.com'
URL = SITE + '/acquire'
EMAIL = 'growth@imisofts.com'
MAILTO = 'mailto:%s?subject=%s' % (EMAIL, 'Acquisition%20enquiry%3A%20imisofts')

# ---- numbers taken from the site itself --------------------------------------------------------
_posts = json.load(open(os.path.join(ROOT, 'blog', 'posts-index.json'), encoding='utf-8'))
N_POSTS = len(_posts if isinstance(_posts, list) else _posts.get('posts', []))
ARTICLES = '%d+' % (N_POSTS // 10 * 10)          # 941 -> "940+"
SERVICE_PAGES = 49                                 # service links in llms.txt (8 service groups)
FREE_TOOLS = 67                                    # 22 free tools + 45 AI writing tools in llms.txt
LAW_COUNTRIES = len([d for d in os.listdir(os.path.join(ROOT, 'blog'))            # one cold email law guide per country
                     if d.startswith('cold-email-laws-') and d != 'cold-email-laws-by-country'])   # the hub is not a country

ICON = {
    'trend': '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    'book': '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/><path d="M8.5 8h7M8.5 12h5"/>',
    'send': '<path d="M21 3L10 14"/><path d="M21 3l-7 18-4-7-7-4z"/>',
    'repeat': '<path d="M4 11V9.5A3.5 3.5 0 0 1 7.5 6H19"/><path d="M16 3l3 3-3 3"/><path d="M20 13v1.5a3.5 3.5 0 0 1-3.5 3.5H5"/><path d="M8 21l-3-3 3-3"/>',
    'globe': '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.9 5.2 3.9 8.5s-1.3 6.1-3.9 8.5c-2.6-2.4-3.9-5.2-3.9-8.5S9.4 5.9 12 3.5z"/>',
    'mail': '<path d="M3 7l9 6 9-6"/><path d="M4 5h16a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/>',
    'inbox': '<path d="M3 13l2.6-7.2A2 2 0 0 1 7.5 4.5h9a2 2 0 0 1 1.9 1.3L21 13"/><path d="M3 13v4.5a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V13h-5l-1.5 2.5h-5L8 13z"/>',
    'users': '<circle cx="9" cy="8.5" r="3.5"/><path d="M2.5 20c.6-3.4 3.2-5.5 6.5-5.5s5.900 2.100 6.500 5.500"/><path d="M16 5.200a3.500 3.500 0 0 1 0 6.600M18.500 14.900c1.600.8 2.700 2.400 3 5.100"/>',
    'lock': '<rect x="5" y="10.5" width="14" height="9.500" rx="2"/><path d="M8 10.500V8a4 4 0 0 1 8 0v2.500"/>',
    'building': '<path d="M4 21V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v16"/><path d="M16 9h2a2 2 0 0 1 2 2v10"/><path d="M2.500 21h19"/><path d="M8 7.500h4M8 11.500h4M8 15.500h4"/>',
    'code': '<path d="M8.500 7l-5 5 5 5M15.500 7l5 5-5 5M13.500 4.500l-3 15"/>',
    'compass': '<circle cx="12" cy="12" r="8.500"/><path d="M15.500 8.500l-2 5-5 2 2-5z"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    'tool': '<path d="M14.5 6.5a4 4 0 0 0-5.2 5.2L3.5 17.5l3 3 5.8-5.8a4 4 0 0 0 5.2-5.2l-2.6 2.6-2.4-.6-.6-2.4z"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
}


def icon(name, size=22, sw='1.8'):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="%s" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, sw, ICON[name]))


MARK = ("<g fill='%23F45407'><circle cx='48' cy='170' r='18'/><path d='M84,84 L136,84 L118,188 L66,188 Z'/>"
        "<path d='M146,84 L198,84 L180,188 L128,188 Z'/></g>")
MARK_URI = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='26 80 176 112'%3E"
            + MARK.replace('<', '%3C').replace('>', '%3E') + "%3C/svg%3E")

LOGO_DARK = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 256" class="aq-logo" role="img" aria-label="imisofts">'
             '<g fill="#F45407"><circle cx="48" cy="170" r="18"/><path d="M84,84 L136,84 L118,188 L66,188 Z"/>'
             '<path d="M146,84 L198,84 L180,188 L128,188 Z"/></g>'
             '<text x="200" y="188" font-family="Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto" '
             'font-weight="700" font-size="96" letter-spacing="-0.5" fill="#F8FAFC">imisofts</text></svg>')

# The figures box under the hero. (key tile?, icon, number, plus sign?, label, note, count up?)
# Indexed pages: Google Search Console, Page indexing report, 963 indexed on 27 Nov 2026 (shown as 900+).
YEARS = 2026 - 2019
FIGURES = [
    (True, 'ring', '27', '', 'Domain Rating', 'Ahrefs score out of 100', True),
    (True, 'users', '8K-10K', '', 'Monthly visitors', 'Coming to imisofts.com', False),
    (False, 'book', str(N_POSTS // 10 * 10), '+', 'Published articles', 'Guides, comparisons and news', True),
    (False, 'search', '900', '+', 'Pages in Google', 'Indexed in Google Search', True),
    (False, 'tool', str(FREE_TOOLS), '', 'Free tools', 'SEO and AI writing tools', True),
    (False, 'calendar', '2019', '', 'Founded', '%d years in business' % YEARS, False),
]

ASSETS = [
    dict(h='imisofts.com',
         p='The domain, the brand and the complete website. Years of publishing have built search authority that a new site cannot buy.',
         li=['Ahrefs Domain Rating 27',
             '8,000 to 10,000 visitors a month',
             '%s articles, %d service pages and %d free tools' % (ARTICLES, SERVICE_PAGES, FREE_TOOLS),
             'More than 900 pages in Google’s index']),
    dict(h='Cold email infrastructure',
         p='The outbound system we use to win our own clients. It is handed over as a working system, not as a plan.',
         li=['Dedicated sending domains',
             'Warmed inboxes with SPF, DKIM and DMARC',
             'Live campaigns that generate leads for the agency']),
    dict(h='Monthly retainers',
         p='A few active retainer clients come with the business, so it earns from the first month you own it.',
         li=['Active clients who pay every month',
             'Client names, services and monthly amounts are shared by email',
             'How each relationship is handed over is agreed with you first']),
]

SHOTS = [
    ('/blog/', 'blog', 'The imisofts blog, with search and topic filters', ARTICLES + ' articles', 'The blog',
     'Guides, comparisons and news on cold email, AI automation and outbound sales.'),
    ('/blog/cold-email-laws-by-country/', 'law-guides', 'A cold email law guide on imisofts.com',
     '%d country guides' % LAW_COUNTRIES, 'Law and compliance guides',
     'Cold email law explained one country at a time, plus calling and data rules.'),
    ('/free-seo-tools', 'tools', 'The free SEO tools page on imisofts.com', '%d free tools' % FREE_TOOLS, 'Free tools',
     'SEO checkers and AI writing tools that people use without signing up.'),
    ('/newsdesk/', 'newsdesk', 'The imisofts newsdesk', 'Updated every weekday', 'The newsdesk',
     'Dated news for teams that sell by email, phone and text.'),
]

WHY = [
    ('trend', 'Authority that takes years to build',
     'A Domain Rating of 27 and 8,000 to 10,000 monthly visitors come from years of publishing and link earning. A new site starts at zero.'),
    ('book', 'A content library that already ranks',
     'Cold email law guides for %d countries, tool pricing guides and comparisons that show up in Google search and in AI answers.' % LAW_COUNTRIES),
    ('send', 'Lead generation that is already running',
     'The sending domains and inboxes are already warmed and the campaigns are live, so outbound does not have to be built from scratch.'),
    ('repeat', 'Recurring revenue already in place',
     'Active monthly retainers mean the business earns while you grow it.'),
]

SUITS = [
    ('building', 'An agency', 'that wants inbound and outbound lead flow from day one.'),
    ('code', 'A software company', 'in outbound or AI that wants an audience it does not have to build.'),
    ('compass', 'An operator', 'who wants a content site with service revenue attached.'),
]

STEPS = [
    ('Email us', 'Tell us who you are and what interests you: the whole business or a part of it.'),
    ('Get the details', 'We reply with traffic and search reports, the infrastructure setup and a summary of the retainers.'),
    ('Talk to the founder', 'A call with Zeeshan Waheed to go through the numbers and answer your questions.'),
    ('Offer and handover', 'Price and terms are agreed in writing, then the domain, site, infrastructure and client relationships are handed over.'),
]

FAQ = [
    ('What exactly is for sale?',
     'Three things, sold together: imisofts.com (the domain, brand and full website), the cold email infrastructure that '
     'generates leads for the agency, and a few active monthly retainers.'),
    ('What is the asking price?',
     'The price is not published. Email <a href="%s">%s</a> and we will share it with the supporting numbers.' % (MAILTO, EMAIL)),
    ('Can I check the traffic and the Domain Rating myself?',
     'Yes. Domain Rating is public: look up imisofts.com in Ahrefs. Traffic and search reports are shared with serious buyers, '
     'so every number on this page can be checked before you make an offer.'),
    ('How do the retainer clients transfer?',
     'Client names, services, monthly amounts and how each relationship is handed over are covered by email once we have spoken.'),
    ('Is a broker or a marketplace involved?',
     'No. imisofts is sold directly by its founder and is not listed on any marketplace. You deal with the founder from the first email to the handover.'),
    ('Who do I talk to?',
     'Zeeshan Waheed, founder and CEO of imisofts. Start with an email to <a href="%s">%s</a>.' % (MAILTO, EMAIL)),
]

ACQ_CSS = """
<link rel="preload" as="image" href="/assets/acquire/home.webp" type="image/webp" fetchpriority="high">
<style id="acquire-v2">
.aq-hero{position:relative;padding:128px 0 72px;background:linear-gradient(180deg,#ffffff 0%,#fff7f3 46%,#f9fafb 100%);overflow:hidden}
.aq-hero::before{content:'';position:absolute;right:-140px;top:60px;width:760px;height:484px;background:url("MARK") no-repeat center/contain;opacity:.055;pointer-events:none}
.aq-hero .container{position:relative}
.aq-hero-grid{display:grid;grid-template-columns:1fr 1.06fr;gap:64px;align-items:center}
.aq-hero .gl-badge{background:#fff;border:1px solid #ffd9c9;box-shadow:0 4px 14px rgba(244,84,7,.10)}
.aq-hero h1{font-size:60px;font-weight:800;line-height:1.05;letter-spacing:-.025em;color:#1a1a1a;margin-bottom:20px}
.aq-hero h1 span{color:#F45407}
.aq-sub{font-size:22px;line-height:1.45;color:#0F172A;font-weight:500;margin-bottom:16px;max-width:540px}
.aq-lead{font-size:17px;color:#666;line-height:1.7;margin-bottom:30px;max-width:540px}
.aq-hero .gl-ctas{margin-bottom:30px}
.aq-hero .gl-btn-primary{box-shadow:0 10px 22px -8px rgba(244,84,7,.55)}
.aq-by{display:flex;align-items:center;gap:12px;font-size:14px;color:#667085;line-height:1.45}
.aq-by img{width:46px;height:46px;border-radius:50%;object-fit:cover;border:2px solid #fff;box-shadow:0 6px 14px rgba(15,23,42,.16);flex:0 0 46px}
.aq-by strong{display:block;color:#0F172A;font-weight:600;font-size:15px}
.aq-visual{position:relative;padding:22px 0 40px}
.aq-browser{background:#fff;border:1px solid #e7eaee;border-radius:14px;overflow:hidden;box-shadow:0 34px 64px -24px rgba(15,23,42,.30),0 14px 28px -14px rgba(15,23,42,.14)}
.aq-bar{display:flex;align-items:center;gap:6px;padding:10px 14px;background:#f6f7f9;border-bottom:1px solid #eceff3}
.aq-bar i{width:9px;height:9px;border-radius:50%;background:#d9dde3;display:block;flex:0 0 9px}
.aq-url{margin-left:10px;background:#fff;border:1px solid #e7eaee;border-radius:6px;font-size:12px;color:#667085;padding:4px 10px;flex:0 1 240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.aq-tag{margin-left:auto;background:#F45407;color:#fff;font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;border-radius:50px;padding:4px 10px;white-space:nowrap}
.aq-browser img{display:block;width:100%;height:auto}
.aq-chip{position:absolute;background:#fff;border:1px solid #eef0f3;border-radius:14px;padding:13px 18px 13px 14px;box-shadow:0 20px 40px -14px rgba(15,23,42,.28);display:flex;align-items:center;gap:12px}
.aq-chip b{display:block;font-size:22px;font-weight:700;color:#0F172A;line-height:1.1;letter-spacing:-.01em}
.aq-chip small{display:block;font-size:12px;color:#667085;margin-top:3px;white-space:nowrap}
.aq-chip-a{left:-34px;bottom:14px}
.aq-chip-b{right:-26px;top:104px}
.aq-ring{width:46px;height:46px;flex:0 0 46px}
.aq-chip-ic{width:46px;height:46px;flex:0 0 46px;border-radius:12px;background:#fff5f3;color:#F45407;display:flex;align-items:center;justify-content:center}
.aq-fig{margin-top:64px;background:#fff;border:1px solid #eef0f3;border-radius:22px;box-shadow:0 30px 60px -34px rgba(15,23,42,.28);padding:24px}
.aq-fig-head{display:flex;align-items:center;justify-content:space-between;gap:8px 20px;flex-wrap:wrap;margin:2px 4px 18px}
.aq-fig-title{display:inline-flex;align-items:center;gap:10px;font-size:13px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#0F172A}
.aq-fig-title::before{content:'';width:27px;height:17px;background:url("MARK") no-repeat center/contain}
.aq-fig-src{font-size:12.5px;color:#98a2b3;line-height:1.5}
.aq-fig-grid{display:grid;grid-template-columns:1.22fr 1.22fr 1fr 1fr 1fr 1fr;gap:14px}
.aq-ft{border:1px solid #eef0f3;border-radius:16px;background:#fafbfc;padding:20px 18px 18px;min-width:0;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
.aq-ft:hover{transform:translateY(-2px);box-shadow:0 14px 26px -16px rgba(15,23,42,.25);border-color:rgba(244,84,7,.3)}
.aq-ft-key{background:linear-gradient(155deg,#ffeee4 0%,#fff9f6 55%,#ffffff 100%);border-color:#ffd3c0}
.aq-ft-ic{width:42px;height:42px;border-radius:12px;background:#fff;border:1px solid #eceff3;color:#F45407;display:flex;align-items:center;justify-content:center;margin-bottom:16px}
.aq-ft-key .aq-ft-ic{background:#F45407;border-color:#F45407;color:#fff;box-shadow:0 10px 18px -8px rgba(244,84,7,.6)}
.aq-ft-ring{width:42px;height:42px;display:block;margin-bottom:16px}
.aq-ft-num{display:block;font-size:34px;font-weight:800;letter-spacing:-.025em;line-height:1;color:#0F172A;white-space:nowrap}
.aq-ft-num [data-count]{font-variant-numeric:tabular-nums}
.aq-ft-num i{font-style:normal;color:#F45407}
.aq-ft-key .aq-ft-num{font-size:40px;color:#F45407}
.aq-ft-label{display:block;font-size:14.5px;font-weight:600;color:#0F172A;margin-top:10px;line-height:1.3}
.aq-ft-sub{display:block;font-size:12.5px;color:#667085;margin-top:3px;line-height:1.4}
.aq-rows{display:flex;flex-direction:column;gap:96px}
.aq-row{display:grid;grid-template-columns:1fr 1fr;gap:72px;align-items:center}
.aq-row.rev .aq-row-visual{order:-1}
.aq-kicker{display:inline-flex;align-items:center;gap:10px;font-size:13px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#F45407;margin-bottom:14px}
.aq-kicker b{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%;background:#F45407;color:#fff;font-size:13px;font-weight:700;letter-spacing:0}
.aq-row h3{font-size:30px;font-weight:700;color:#0F172A;line-height:1.2;margin-bottom:14px;letter-spacing:-.01em}
.aq-row-text>p{font-size:17px;color:#555;line-height:1.7;margin-bottom:22px}
.aq-row .gl-check li{font-size:16px;color:#333}
.aq-stack{position:relative;padding:0 0 56px 0}
.aq-stack .aq-browser:first-child{width:86%}
.aq-stack .aq-browser+.aq-browser{position:absolute;right:0;bottom:0;width:62%}
.aq-panel{background:#fff;border:1px solid #eef0f3;border-radius:18px;box-shadow:0 30px 56px -28px rgba(15,23,42,.26);padding:26px}
.aq-panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.aq-panel-head span{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#98a2b3;font-weight:600}
.aq-live{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:#067647;background:#ecfdf3;border-radius:50px;padding:5px 11px;font-style:normal}
.aq-live::before{content:'';width:7px;height:7px;border-radius:50%;background:#12b76a}
.aq-flow{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);position:relative}
.aq-flow::before{content:'';position:absolute;left:12.5%;right:12.5%;top:27px;border-top:2px dashed #ffc7b0}
.aq-flow li{position:relative;text-align:center;padding:0 6px}
.aq-node{width:56px;height:56px;border-radius:16px;background:#fff5f3;border:1px solid #ffd9c9;color:#F45407;display:flex;align-items:center;justify-content:center;margin:0 auto 14px;position:relative;box-shadow:0 0 0 6px #fff}
.aq-flow li:last-child .aq-node{background:#F45407;border-color:#F45407;color:#fff;box-shadow:0 0 0 6px #fff,0 12px 22px -8px rgba(244,84,7,.6)}
.aq-flow b{display:block;font-size:14px;font-weight:600;color:#0F172A;line-height:1.35}
.aq-flow small{display:block;font-size:12px;color:#667085;margin-top:4px;line-height:1.4}
.aq-pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:26px;padding-top:20px;border-top:1px solid #f0f2f5}
.aq-pills span{font-size:12px;font-weight:600;color:#475467;background:#f6f7f9;border:1px solid #eceff3;border-radius:50px;padding:5px 12px}
.aq-ledger{display:flex;flex-direction:column;gap:12px;-webkit-mask-image:linear-gradient(180deg,#000 62%,transparent 100%);mask-image:linear-gradient(180deg,#000 62%,transparent 100%)}
.aq-ledger-row{display:flex;align-items:center;gap:14px;border:1px solid #f0f2f5;border-radius:12px;padding:14px 16px;background:#fcfcfd}
.aq-av{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#ffe3d6,#ffc7b0);flex:0 0 38px}
.aq-lines{flex:1;display:flex;flex-direction:column;gap:8px}
.aq-lines span{height:9px;border-radius:50px;background:#e9edf2;display:block}
.aq-lines span+span{background:#f1f4f7}
.aq-amt{display:flex;align-items:center;gap:8px;color:#98a2b3}
.aq-amt span{width:64px;height:11px;border-radius:50px;background:#e9edf2;display:block}
.aq-ledger-foot{display:flex;align-items:center;gap:10px;margin-top:6px;font-size:14px;color:#475467;line-height:1.5}
.aq-ledger-foot svg{color:#F45407;flex:0 0 auto}
.aq-shots{display:grid;grid-template-columns:repeat(2,1fr);gap:28px}
.aq-shot{display:block;background:#fff;border:1px solid #eef0f3;border-radius:18px;overflow:hidden;text-decoration:none;color:inherit;transition:transform .25s ease,box-shadow .25s ease,border-color .25s ease}
.aq-shot:hover{transform:translateY(-4px);box-shadow:0 28px 50px -24px rgba(15,23,42,.26);border-color:rgba(244,84,7,.35)}
.aq-shot-img{display:block;background:#f6f7f9;border-bottom:1px solid #eef0f3;padding:18px 18px 0}
.aq-shot-img img{display:block;width:100%;height:auto;border-radius:10px 10px 0 0;border:1px solid #e7eaee;border-bottom:0;box-shadow:0 -2px 18px rgba(15,23,42,.06)}
.aq-shot-body{display:block;padding:22px 24px 24px}
.aq-shot-tag{display:inline-block;font-size:12px;font-weight:600;color:#F45407;background:#fff5f3;border-radius:50px;padding:4px 11px;margin-bottom:10px}
.aq-shot-body strong{display:block;font-size:19px;font-weight:600;color:#0F172A;margin-bottom:6px}
.aq-shot-body span.aq-shot-desc{display:block;font-size:15px;color:#555;line-height:1.6}
.aq-shot-go{display:inline-block;margin-top:12px;font-size:14px;font-weight:500;color:#F45407}
.aq-why{display:grid;grid-template-columns:repeat(4,1fr);gap:22px}
.aq-why .gl-tile p{margin-bottom:0}
.aq-suits{margin-top:28px;background:#fff;border:1px solid #eef0f3;border-radius:18px;padding:28px 32px;display:grid;grid-template-columns:auto repeat(3,1fr);gap:28px;align-items:center}
.aq-suits-title{font-size:13px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#F45407;max-width:120px;line-height:1.5}
.aq-suit{display:flex;gap:14px;align-items:flex-start;font-size:15px;color:#555;line-height:1.6}
.aq-suit .gl-icon{margin:0;flex:0 0 44px}
.aq-suit strong{color:#0F172A;font-weight:600}
.aq-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:28px;position:relative}
.aq-steps::before{content:'';position:absolute;left:24px;right:calc((100% - 84px)/4 - 24px);top:23px;height:2px;background:linear-gradient(90deg,#F45407,#ffb899)}
.aq-steps li{position:relative}
.aq-num{width:48px;height:48px;border-radius:50%;background:#fff;border:2px solid #F45407;color:#F45407;font-weight:700;font-size:17px;display:flex;align-items:center;justify-content:center;margin-bottom:20px;position:relative;box-shadow:0 0 0 8px #fff}
.aq-steps li:last-child .aq-num{background:#F45407;color:#fff}
.aq-steps h3{font-size:18px;font-weight:600;color:#0F172A;margin-bottom:8px;line-height:1.35}
.aq-steps p{font-size:15px;color:#555;line-height:1.65}
.aq-founder{background:#fff;border:1px solid #eef0f3;border-radius:22px;box-shadow:0 30px 60px -34px rgba(15,23,42,.28);display:grid;grid-template-columns:300px 1fr;gap:48px;align-items:center;padding:28px;max-width:980px;margin:0 auto}
.aq-founder-photo{position:relative}
.aq-founder-photo img{display:block;width:100%;height:auto;border-radius:16px}
.aq-founder-photo::after{content:'';position:absolute;right:-14px;bottom:-14px;width:84px;height:54px;background:url("MARK") no-repeat center/contain}
.aq-founder h2{font-size:30px;margin-bottom:12px}
.aq-founder p{font-size:17px;color:#555;line-height:1.7;margin-bottom:18px}
.aq-founder .aq-pills{margin:0 0 24px;padding:0;border:0}
.aq-founder p.gl-note{font-size:13px;color:#888;line-height:1.6;margin:20px 0 0}
.aq-final{position:relative;padding:96px 0;background:linear-gradient(135deg,#0F172A 0%,#1e293b 100%);color:#fff;overflow:hidden;scroll-margin-top:72px}
.aq-final::before{content:'';position:absolute;left:-120px;bottom:-90px;width:620px;height:395px;background:url("MARK") no-repeat center/contain;opacity:.10;pointer-events:none}
.aq-final::after{content:'';position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,#F45407,#ff8a4c 40%,transparent)}
.aq-final .container{position:relative}
.aq-final-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:64px;align-items:center}
.aq-logo{height:54px;width:auto;display:block;margin:0 0 22px -8px}
.aq-final h2{font-size:40px;font-weight:700;line-height:1.2;color:#fff;margin-bottom:16px;letter-spacing:-.01em}
.aq-final .gl-sub{color:#cbd5e1;font-size:17px;line-height:1.7;margin-bottom:26px;max-width:520px}
.aq-mail{display:inline-block;font-size:24px;font-weight:600;color:#fff;text-decoration:none;border-bottom:2px solid #F45407;padding-bottom:3px;word-break:break-all}
.aq-mail:hover{color:#ffb38f}
.aq-final-meta{margin-top:28px;padding-top:22px;border-top:1px solid rgba(255,255,255,.1);font-size:14px;color:#94a3b8;line-height:1.7;max-width:520px}
.aq-cta-card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:36px;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}
.aq-cta-card h3{font-size:20px;font-weight:600;color:#fff;margin-bottom:16px}
.aq-cta-card .gl-check li{color:rgba(255,255,255,.92)}
.aq-cta-card .gl-check li::before{background-color:rgba(244,84,7,.2)}
.aq-cta-card .gl-btn{margin-top:26px;display:block;text-align:center;box-shadow:0 12px 26px -10px rgba(244,84,7,.7)}
@media (max-width:1340px){.aq-chip-b{right:-6px}}
@media (max-width:1240px){.aq-fig-grid{grid-template-columns:repeat(3,1fr)}}
@media (max-width:1100px){
  .aq-hero h1{font-size:52px}
  .aq-chip-a{left:-12px}
  .aq-why{grid-template-columns:repeat(2,1fr)}
  .aq-suits{grid-template-columns:1fr;gap:20px}.aq-suits-title{max-width:none}
}
@media (max-width:1024px){
  .aq-hero-grid,.aq-row,.aq-final-grid{grid-template-columns:1fr;gap:44px}
  .aq-hero h1{font-size:52px !important;line-height:1.06 !important}
  .aq-row.rev .aq-row-visual{order:0}
  .aq-visual{max-width:640px}
  .aq-chip-a{left:-8px}.aq-chip-b{right:-8px}
  .aq-hero::before{right:-260px;top:40px;opacity:.04}
  .aq-rows{gap:72px}
  .aq-steps{grid-template-columns:repeat(2,1fr);gap:36px 28px}.aq-steps::before{display:none}
  .aq-founder{grid-template-columns:240px 1fr;gap:32px}
}
@media (max-width:640px){
  .aq-hero{padding:104px 0 56px}
  .aq-hero::before{width:380px;height:242px;right:-190px;top:64px;opacity:.045}
  .aq-hero h1{font-size:50px !important;line-height:1.04 !important}
  .aq-hero h1 span{display:block}
  .aq-sub{font-size:19px}
  .aq-visual{padding:6px 0 0}
  .aq-chip{display:none}
  .aq-tag{font-size:10px;padding:3px 8px}
  .aq-fig{margin-top:44px;padding:16px 14px 14px;border-radius:20px}
  .aq-fig-head{margin:2px 2px 14px}
  .aq-fig-grid{grid-template-columns:repeat(2,1fr);gap:10px}
  .aq-ft{padding:16px 14px 14px;border-radius:14px}
  .aq-ft-ic,.aq-ft-ring{width:36px;height:36px;margin-bottom:12px}
  .aq-ft-ic{border-radius:10px}
  .aq-ft-num{font-size:28px}.aq-ft-key .aq-ft-num{font-size:31px}
  .aq-ft-label{font-size:13.5px;margin-top:8px}.aq-ft-sub{font-size:12px}
  .aq-row h3{font-size:25px}
  .aq-rows{gap:60px}
  .aq-panel{padding:20px 16px}
  .aq-flow{grid-template-columns:repeat(2,1fr);gap:24px 8px}.aq-flow::before{display:none}
  .aq-shots{grid-template-columns:1fr;gap:20px}
  .aq-shot-img{padding:14px 14px 0}
  .aq-why{grid-template-columns:1fr}
  .aq-suits{padding:22px}
  .aq-steps{grid-template-columns:1fr;gap:0}
  .aq-steps li{padding:0 0 28px 68px;min-height:76px}
  .aq-steps li:last-child{padding-bottom:0}
  .aq-steps li::before{content:'';position:absolute;left:23px;top:48px;bottom:0;width:2px;background:#ffd9c9}
  .aq-steps li:last-child::before{display:none}
  .aq-num{position:absolute;left:0;top:0;margin:0;box-shadow:none}
  .aq-founder{grid-template-columns:1fr;gap:28px;padding:20px}
  .aq-founder-photo{max-width:260px}
  .aq-founder h2{font-size:26px}
  .aq-final{padding:64px 0}
  .aq-final h2{font-size:30px}
  .aq-mail{font-size:19px}
  .aq-cta-card{padding:24px}
}
@media (prefers-reduced-motion:reduce){.aq-shot,.aq-ft{transition:none}.aq-shot:hover,.aq-ft:hover{transform:none}}
</style>
""".replace('MARK', MARK_URI)


COUNT_JS = """
  <script>
  /* /acquire: the figures count up once when the box scrolls into view. Without JavaScript, or with
     reduced motion, the final numbers are simply shown (they are in the HTML). */
  (function(){
    var box=document.querySelector('.aq-fig');
    if(!box||!('IntersectionObserver' in window)||!window.requestAnimationFrame) return;
    if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var els=box.querySelectorAll('[data-count]'); if(!els.length) return;
    var done=false, dur=1100;
    function set(e){for(var i=0;i<els.length;i++){els[i].textContent=Math.round(Number(els[i].getAttribute('data-count'))*e);}}
    function run(){
      if(done) return; done=true;
      var t0=null;
      function step(ts){if(t0===null)t0=ts;var p=Math.min(1,(ts-t0)/dur);set(1-Math.pow(1-p,3));if(p<1)requestAnimationFrame(step);}
      set(0); requestAnimationFrame(step);
      setTimeout(function(){set(1);},dur+600);
    }
    var io=new IntersectionObserver(function(en){for(var i=0;i<en.length;i++){if(en[i].isIntersecting){run();io.disconnect();break;}}},{threshold:0.3});
    io.observe(box);
  })();
  </script>
"""


def strip_tags(t):
    return re.sub(r'<[^>]+>', '', t)


def checks(items):
    return '<ul class="gl-check">' + ''.join('<li>%s</li>' % esc(i) for i in items) + '</ul>'


def browser(img, w, h, alt, url='imisofts.com', tag=False, eager=False):
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return ('<div class="aq-browser"><div class="aq-bar"><i></i><i></i><i></i><span class="aq-url">%s</span>%s</div>'
            '<img src="/assets/acquire/%s.webp" width="%d" height="%d" alt="%s" %s></div>'
            % (esc(url), '<span class="aq-tag">For sale</span>' if tag else '', img, w, h, esc(alt), load))


RING = ('<svg class="aq-ring" viewBox="0 0 46 46" aria-hidden="true"><circle cx="23" cy="23" r="19" fill="none" stroke="#ffe3d6" stroke-width="6"/>'
        '<circle cx="23" cy="23" r="19" fill="none" stroke="#F45407" stroke-width="6" stroke-linecap="round" '
        'stroke-dasharray="%.1f 119.4" transform="rotate(-90 23 23)"/></svg>' % (119.4 * 27 / 100))


def visual(i):
    if i == 0:
        return ('<div class="aq-stack">'
                + browser('blog', 960, 573, 'The imisofts blog, with search and topic filters', 'imisofts.com/blog')
                + browser('law-guides', 960, 573, 'A cold email law guide on imisofts.com', 'imisofts.com/blog/cold-email-laws-by-country')
                + '</div>')
    if i == 1:
        nodes = [('globe', 'Sending domains', 'Dedicated to outreach'), ('mail', 'Warmed inboxes', 'Authenticated and warm'),
                 ('send', 'Live campaigns', 'Running today'), ('inbox', 'Leads', 'Replies for the agency')]
        return ('<div class="aq-panel"><div class="aq-panel-head"><span>Outbound engine</span><em class="aq-live">Live</em></div>'
                '<ol class="aq-flow">'
                + ''.join('<li><span class="aq-node">%s</span><b>%s</b><small>%s</small></li>' % (icon(ic, 24), esc(b), esc(s)) for ic, b, s in nodes)
                + '</ol><div class="aq-pills"><span>SPF</span><span>DKIM</span><span>DMARC</span><span>Inbox warm-up</span></div></div>')
    row = ('<div class="aq-ledger-row"><span class="aq-av"></span><span class="aq-lines"><span style="width:%d%%"></span>'
           '<span style="width:%d%%"></span></span><span class="aq-amt"><span></span>%s</span></div>')
    return ('<div class="aq-panel"><div class="aq-panel-head"><span>Monthly retainers</span><em class="aq-live">Active</em></div>'
            '<div class="aq-ledger" aria-hidden="true">'
            + row % (58, 36, icon('lock', 16, '2')) + row % (70, 44, icon('lock', 16, '2')) + row % (50, 30, icon('lock', 16, '2'))
            + '</div><div class="aq-ledger-foot">%s<span>Client names and monthly amounts are shared by email with serious buyers.</span></div></div>'
            % icon('lock', 18, '2'))


def build():
    m = []
    m.append('''
  <section class="aq-hero">
    <div class="container">
      <div class="aq-hero-grid">
        <div>
          <nav class="gl-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span>Acquire imisofts</nav>
          <div class="gl-badge">Direct sale from the founder</div>
          <h1>imisofts is <span>for sale</span></h1>
          <p class="aq-sub">A website that ranks, a cold email engine that brings in leads, and clients who pay every month.</p>
          <p class="aq-lead">imisofts is an AI automation and cold email agency founded in 2019. The whole business is offered in one direct deal with its founder, with no broker and no marketplace listing.</p>
          <div class="gl-ctas">
            <a href="%(mailto)s" class="gl-btn gl-btn-primary">Email us about the sale &rarr;</a>
            <a href="#included" class="gl-btn gl-btn-secondary">See what is included</a>
          </div>
          <div class="aq-by">
            <img src="/assets/acquire/founder-avatar.webp" width="96" height="96" alt="Zeeshan Waheed, founder and CEO of imisofts" decoding="async">
            <div><strong>Zeeshan Waheed</strong>Founder and CEO. You deal with him directly.</div>
          </div>
        </div>
        <div class="aq-visual">
          %(hero)s
          <div class="aq-chip aq-chip-a">%(ring)s<div><b>27</b><small>Ahrefs Domain Rating</small></div></div>
          <div class="aq-chip aq-chip-b"><span class="aq-chip-ic">%(users)s</span><div><b>8K-10K</b><small>Monthly visitors</small></div></div>
        </div>
      </div>
      <div class="aq-fig">
        <div class="aq-fig-head">
          <span class="aq-fig-title">imisofts in numbers</span>
          <span class="aq-fig-src">Domain Rating from Ahrefs, indexed pages from Google Search Console, 27 Nov 2026.</span>
        </div>
        <div class="aq-fig-grid">''' % dict(mailto=MAILTO, ring=RING, users=icon('users', 22),
                                       hero=browser('home', 1280, 711, 'The imisofts.com homepage', 'imisofts.com', tag=True, eager=True)))
    for key, ic, num, plus, label, note, count in FIGURES:
        head = RING.replace('class="aq-ring"', 'class="aq-ft-ring"') if ic == 'ring' else '<span class="aq-ft-ic">%s</span>' % icon(ic, 21)
        n = '<span data-count="%s">%s</span>' % (num, num) if count else esc(num)
        m.append('''
          <div class="aq-ft%s">%s<b class="aq-ft-num">%s%s</b><span class="aq-ft-label">%s</span><span class="aq-ft-sub">%s</span></div>'''
                 % (' aq-ft-key' if key else '', head, n, '<i>+</i>' if plus else '', esc(label), esc(note)))
    m.append('''
        </div>
      </div>
    </div>
  </section>

  <section class="gl-section" id="included" style="scroll-margin-top:72px;">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">What is included</span>
        <h2>Three assets, sold as one business</h2>
        <p>A website with authority and traffic, a working system for getting clients, and clients who already pay every month.</p>
      </div>
      <div class="aq-rows">''')
    for i, a in enumerate(ASSETS):
        m.append('''
        <div class="aq-row%s">
          <div class="aq-row-text">
            <div class="aq-kicker"><b>%d</b>Asset %d of 3</div>
            <h3>%s</h3>
            <p>%s</p>
            %s
          </div>
          <div class="aq-row-visual">%s</div>
        </div>''' % (' rev' if i == 1 else '', i + 1, i + 1, esc(a['h']), esc(a['p']), checks(a['li']), visual(i)))
    m.append('''
      </div>
    </div>
  </section>

  <section class="gl-section gl-alt">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">Inside the website</span>
        <h2>What you would own on day one</h2>
        <p>These are real pages from imisofts.com as it stands today. Open any of them to see the live site.</p>
      </div>
      <div class="aq-shots">''')
    for href, img, alt, tag, h, d in SHOTS:
        m.append('''
        <a class="aq-shot" href="%s">
          <span class="aq-shot-img"><img src="/assets/acquire/%s.webp" width="960" height="573" alt="%s" loading="lazy" decoding="async"></span>
          <span class="aq-shot-body"><span class="aq-shot-tag">%s</span><strong>%s</strong><span class="aq-shot-desc">%s</span><span class="aq-shot-go">Open the live page &rarr;</span></span>
        </a>''' % (href, img, esc(alt), esc(tag), esc(h), esc(d)))
    m.append('''
      </div>
    </div>
  </section>

  <section class="gl-section">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">The opportunity</span>
        <h2>Why this is a strong starting point</h2>
        <p>Most agencies and content sites spend their first years building authority, traffic and a way to win clients. imisofts already has all three, plus retainers that pay every month.</p>
      </div>
      <div class="aq-why">''')
    for ic, h, d in WHY:
        m.append('''
        <div class="gl-tile"><div class="gl-icon">%s</div><h3>%s</h3><p>%s</p></div>''' % (icon(ic), esc(h), esc(d)))
    m.append('''
      </div>
      <div class="aq-suits">
        <div class="aq-suits-title">Who it suits</div>''')
    for ic, h, d in SUITS:
        m.append('''
        <div class="aq-suit"><span class="gl-icon">%s</span><span><strong>%s</strong> %s</span></div>''' % (icon(ic), esc(h), esc(d)))
    m.append('''
      </div>
    </div>
  </section>

  <section class="gl-section gl-alt">
    <div class="container">
      <div class="aq-founder">
        <div class="aq-founder-photo"><img src="/assets/acquire/founder.webp" width="480" height="600" alt="Zeeshan Waheed, founder and CEO of imisofts" loading="lazy" decoding="async"></div>
        <div>
          <span class="gl-eyebrow">Who you deal with</span>
          <h2>Sold directly by the founder</h2>
          <p>Zeeshan Waheed founded imisofts in 2019 and runs it today. He handles the sale himself, from your first email to the handover, so every question is answered by the person who built the business.</p>
          <div class="aq-pills"><span>Founder and CEO</span><span>Running imisofts since 2019</span><span>No broker in between</span></div>
          <a href="%(mailto)s" class="gl-btn gl-btn-primary">Email Zeeshan about the sale &rarr;</a>
          <p class="gl-note">Figures on this page: Domain Rating from Ahrefs, checked 27 November 2026. Traffic and search reports are shared with serious buyers.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="gl-section">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">How it works</span>
        <h2>How the sale works</h2>
        <p>Four steps, all handled directly with the founder.</p>
      </div>
      <ol class="aq-steps">''' % dict(mailto=MAILTO))
    for i, (h, d) in enumerate(STEPS):
        m.append('''
        <li><span class="aq-num">%d</span><h3>%s</h3><p>%s</p></li>''' % (i + 1, esc(h), esc(d)))
    m.append('''
      </ol>
    </div>
  </section>

  <section class="gl-section gl-alt">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">FAQ</span>
        <h2>Questions buyers ask first</h2>
      </div>
      <div class="gl-faq">''')
    for q, a in FAQ:
        m.append('''
        <details>
          <summary>%s</summary>
          <p>%s</p>
        </details>''' % (esc(q), a))
    m.append('''
      </div>
    </div>
  </section>

  <section class="aq-final" id="contact">
    <div class="container">
      <div class="aq-final-grid">
        <div>
          %(logo)s
          <h2>Interested in acquiring imisofts?</h2>
          <p class="gl-sub">Everything starts with one email. We reply with the numbers, the infrastructure details and the retainer summary.</p>
          <a class="aq-mail" href="%(mailto)s">%(email)s</a>
          <div class="aq-final-meta">You deal directly with Zeeshan Waheed, founder and CEO.<br>imisofts, The Prism Tower, 19th Floor, Business Bay, Dubai, United Arab Emirates.</div>
        </div>
        <div class="aq-cta-card">
          <h3>What to put in your first email</h3>
          <ul class="gl-check">
            <li>Who you are and the company you represent</li>
            <li>What interests you: the whole business, or a part of it</li>
            <li>Any questions you want answered before a call</li>
          </ul>
          <a href="%(mailto)s" class="gl-btn gl-btn-primary">Email us about the sale &rarr;</a>
        </div>
      </div>
    </div>
  </section>
''' % dict(mailto=MAILTO, email=EMAIL, logo=LOGO_DARK))
    main_html = ''.join(m)

    title = 'Acquire imisofts | Agency Website, Outbound System and Retainers for Sale'
    desc = ('imisofts is for sale, direct from the founder: imisofts.com (Domain Rating 27, 8K to 10K monthly visitors, '
            '%s articles), a working cold email infrastructure and active monthly retainers.' % ARTICLES)
    og = SITE + '/og-image-acquire.jpg'
    webpage = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': URL + '#webpage', 'url': URL, 'name': title,
               'description': desc, 'about': {'@id': SITE + '/#organization'},
               'primaryImageOfPage': {'@type': 'ImageObject', 'url': og, 'width': 1200, 'height': 630},
               'isPartOf': {'@type': 'WebSite', 'url': SITE, 'name': 'imisofts'}}
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE},
        {'@type': 'ListItem', 'position': 2, 'name': 'Acquire imisofts', 'item': URL}]}
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}} for q, a in FAQ]}
    return page(title=title, description=desc, canonical=URL,
                robots='index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1',
                og_url=URL, og_image=og, schema=[webpage, crumbs, faq],
                extra_css=GEO_CSS + ACQ_CSS, main_html=main_html, tail_js=COUNT_JS)


if __name__ == '__main__':
    out = build()
    assert '—' not in out.split('<main>')[1].split('</main>')[0], 'em dash in page copy'
    with open(os.path.join(ROOT, 'acquire.html'), 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote acquire.html', len(out), 'articles', ARTICLES)
