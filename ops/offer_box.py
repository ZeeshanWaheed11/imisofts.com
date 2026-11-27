#!/usr/bin/env python3
"""Service offer box for NEW articles only (added 2026-11-27).

One short box in the middle of a new article that names the imisofts service matching the
topic and links to it, plus the free audit. Articles that existed on 2026-11-27 are listed in
ops/offer_box_existing.txt and are never touched, so pages that already rank do not change.

Used three ways:
  - ops/build_news.py and ops/build_affiliate.py call apply(html, meta) on every build;
  - a byline run adds it to its hand-built page with:  python3 ops/offer_box.py blog/<slug>/index.html
  - a spec can choose the service itself with "offer_box": {"href": "/email-infrastructure"},
    or switch the box off with "offer_box": false.

apply() never raises: on any problem it returns the page unchanged.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
EXISTING_FILE = os.path.join(HERE, 'offer_box_existing.txt')
MARK = 'class="offer-box"'

# Service pages and the copy for each box. No em dashes (the article QA gate rejects them).
OFFERS = {
    '/cold-email-marketing': ('Want cold email that lands in the inbox and books meetings?',
        'imisofts sets up the domains and inboxes, writes the campaigns and books qualified meetings for you. Month-to-month plans.',
        'See cold email packages'),
    '/email-infrastructure': ('Need your cold email infrastructure set up properly?',
        'We buy and configure the domains and inboxes, set SPF, DKIM and DMARC, and warm everything up, so sending starts in about 14 days.',
        'See infrastructure setup'),
    '/lead-generation': ('Want qualified B2B meetings without building an SDR team?',
        'imisofts builds verified prospect lists, runs the outreach and books qualified meetings into your calendar.',
        'See lead generation plans'),
    '/tcpa-compliant-ai-calling': ('Running AI calls in the US?',
        'We build the consent, Do Not Call and opt-out layer under your AI dialer, with an audit-ready record of every call.',
        'See TCPA-compliant AI calling'),
    '/ai-voice-agents': ('Want an AI voice agent that answers and follows up for you?',
        'imisofts builds AI voice agents that call and follow up with your leads in under a minute, with consent capture and DNC checks built in.',
        'See AI voice agents'),
    '/gohighlevel-services': ('Need GoHighLevel set up or automated?',
        'Our GoHighLevel team builds the automations, funnels, A2P registration and white-label SaaS setup for you.',
        'See GoHighLevel services'),
    '/ai-automation': ('Want this workflow automated for your business?',
        'imisofts builds custom AI agents and n8n workflows that take repetitive work off your team, connected to the tools you already use.',
        'See AI automation'),
    '/crm-development': ('Need your CRM set up to match how you sell?',
        'We build and customise HubSpot, Salesforce, Zoho and custom CRMs, with your pipeline, automations and integrations in place.',
        'See CRM development'),
    '/hubspot-implementation': ('Need HubSpot set up properly?',
        'imisofts implements HubSpot with your pipeline, automations, reporting and integrations configured for your team.',
        'See HubSpot implementation'),
    '/salesforce-implementation': ('Need Salesforce set up properly?',
        'imisofts implements Salesforce with your pipeline, automations, reporting and integrations configured for your team.',
        'See Salesforce implementation'),
    '/ai-search-optimization': ('Want your brand named by ChatGPT and Google AI Overviews?',
        'imisofts fixes your entity data, builds citable pages and earns the mentions that lead AI assistants to recommend you.',
        'See AI search optimization'),
    '/shopify-apps': ('Need a Shopify app built?',
        'We build Shopify apps from idea to App Store approval, for your own store or for the public app store.',
        'See Shopify app development'),
    '/seo-services': ('Want more leads from Google search?',
        'imisofts runs technical SEO, content and link building for B2B, SaaS and service businesses.',
        'See SEO services'),
    '/lead-generation-agency-uk': ('Selling to UK businesses?',
        'imisofts runs PECR-aware cold email and appointment setting for UK companies and books qualified meetings into your calendar.',
        'See UK lead generation'),
    '/lead-generation-agency-australia': ('Selling to Australian businesses?',
        'imisofts runs Spam Act compliant cold email and appointment setting for Australian companies and books qualified meetings for you.',
        'See Australian lead generation'),
    '/lead-generation-dubai': ('Selling to businesses in the UAE and the Gulf?',
        'Our Dubai team runs compliant cold email and appointment setting across the UAE and GCC and books qualified meetings for you.',
        'See UAE lead generation'),
}

NO_BOX = re.compile(r'\bgta\b|grand theft auto|rockstar games|playstation|xbox|nintendo|video game|box office|movie|celebrity')
COUNTRY = [
    (re.compile(r'united[- ]kingdom|\buk\b|britain|british|england|scotland|wales|\bico\b|\bpecr\b'), '/lead-generation-agency-uk'),
    (re.compile(r'australia|australian|\bacma\b|spam act'), '/lead-generation-agency-australia'),
    (re.compile(r'\buae\b|dubai|abu dhabi|emirates|saudi|\bgcc\b|qatar|kuwait|bahrain|\boman\b|\btdra\b'), '/lead-generation-dubai'),
]
COUNTRY_TOPICS = re.compile(r'law|legal|gdpr|pecr|compliance|regulat|cold email|cold call|lead gen|b2b|outbound|prospect|telemarketing')
RULES = [
    (re.compile(r'tcpa|robocall|10dlc|do[- ]not[- ]call|\bdnc\b|autodial'), '/tcpa-compliant-ai-calling'),
    (re.compile(r'voice agent|ai voice|voice ai|receptionist|ai call|cold call|calling|dialer|telemarketing|retell|vapi|bland ai'), '/ai-voice-agents'),
    (re.compile(r'gohighlevel|highlevel|\bghl\b'), '/gohighlevel-services'),
    (re.compile(r'deliverab|\bspf\b|dkim|dmarc|warm[- ]?up|inbox placement|sending domain|mailbox|smtp|bounce rate|spam folder|blacklist|google workspace|email infrastructure'), '/email-infrastructure'),
    (re.compile(r'cold email|cold outreach|instantly|smartlead|lemlist|saleshandy|reply\.io|woodpecker|sequence|subject line|follow[- ]up email|can-spam|casl|anti-spam|spam law|email law'), '/cold-email-marketing'),
    (re.compile(r'lead gen|leads|apollo|zoominfo|lusha|clay\b|seamless|prospect|scrap|data enrichment|b2b data|email finder|appointment setting|sdr|outbound'), '/lead-generation'),
    (re.compile(r'hubspot'), '/hubspot-implementation'),
    (re.compile(r'salesforce'), '/salesforce-implementation'),
    (re.compile(r'\bcrm\b|pipedrive|close\.com|zoho|monday\.com'), '/crm-development'),
    (re.compile(r'\baeo\b|answer engine|ai search|ai overview|ai mode|llm seo|generative engine|\bgeo\b|ai citation|chatgpt search|perplexity'), '/ai-search-optimization'),
    (re.compile(r'shopify'), '/shopify-apps'),
    (re.compile(r'n8n|zapier|make\.com|workflow|automation|ai agent|agentic|chatbot'), '/ai-automation'),
    (re.compile(r'\bseo\b|keyword research|backlink|core update|search console|google search|organic traffic'), '/seo-services'),
]
# Section headings as they appear when apply() runs: real <h2> or the news "<p><strong>X</strong></p>" form.
HEADING = re.compile(r'<h2[\s>]|<p><strong>[^<]{3,70}</strong></p>')
END_MARKERS = ('<div class="blog-cta-banner"', '<section class="faq-section"', 'data-news-template="2"', 'class="related-coverage"')


def existing():
    try:
        with open(EXISTING_FILE, encoding='utf-8') as f:
            return {l.strip().strip('/') for l in f if l.strip() and not l.startswith('#')}
    except Exception:
        return None   # file missing: treat every article as existing, never add a box


def topic_text(meta):
    parts = [meta.get('slug', ''), meta.get('title', ''), meta.get('keywords', ''), meta.get('category', '')]
    return ' '.join(str(p) for p in parts).lower().replace('-', ' ')


def pick(meta):
    """Service path for this article, or None when no service fits."""
    t = topic_text(meta)
    if NO_BOX.search(t):
        return None
    if COUNTRY_TOPICS.search(t):
        for rx, href in COUNTRY:
            if rx.search(t):
                return href
    for rx, href in RULES:
        if rx.search(t):
            return href
    return None


def box_html(href):
    head, blurb, label = OFFERS[href]
    return ('<div class="offer-box" data-offer="%s" style="margin:32px 0;padding:24px 26px;border:1px solid #FDE0D3;'
            'border-left:4px solid #F45407;border-radius:14px;background:#FFF8F5;">'
            '<p style="margin:0 0 6px;font-size:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#F45407;">Done for you by imisofts</p>'
            '<p style="margin:0 0 8px;font-size:19px;font-weight:600;line-height:1.4;color:#0F172A;">%s</p>'
            '<p style="margin:0 0 16px;font-size:16px;line-height:1.65;color:#475569;">%s</p>'
            '<p style="margin:0;"><a href="%s" style="display:inline-block;padding:10px 18px;background:#F45407;color:#fff;'
            'border-radius:8px;text-decoration:none;font-weight:500;">%s &rarr;</a>'
            '<a href="/free-audit" style="display:inline-block;margin:10px 0 0 16px;color:#F45407;font-weight:500;">Free audit in 24 hours</a></p>'
            '</div>') % (href, head, blurb, href, label)


def apply(s, meta):
    """Return the page with the offer box inserted, or unchanged. Never raises."""
    try:
        slug = str(meta.get('slug', '')).strip('/')
        if not slug or MARK in s:
            return s
        ex = existing()
        if ex is None or slug in ex:
            return s
        choice = meta.get('offer_box')
        if choice is False:
            return s
        href = choice.get('href') if isinstance(choice, dict) else pick(meta)
        if not href or href not in OFFERS:
            return s
        a = s.find('<article')
        if a < 0:
            return s
        a = s.find('>', a) + 1
        z = s.find('</article>', a)
        if z < 0:
            return s
        end = min([i for i in (s.find(m, a) for m in END_MARKERS) if a <= i < z] or [z])
        # back up to the start of the tag that holds an end marker found inside an attribute
        if end != z and s[end] != '<':
            end = s.rfind('<', a, end)
        heads = [m.start() for m in HEADING.finditer(s, a, end)]
        if len(heads) >= 3:
            at = heads[2]
        elif len(heads) == 2:
            at = heads[1]
        else:
            at = end
        return s[:at] + box_html(href) + '\n' + s[at:]
    except Exception as e:
        print('offer box skipped: %r' % (e,))
        return s


def _meta_from_page(path, s):
    slug = os.path.basename(os.path.dirname(os.path.abspath(path)))
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    k = re.search(r'<meta name="keywords" content="([^"]*)"', s)
    return {'slug': slug, 'title': t.group(1) if t else '', 'keywords': k.group(1) if k else ''}


def main(argv):
    """CLI for hand-built pages: python3 ops/offer_box.py blog/<slug>/index.html [--href /service]"""
    if len(argv) < 2:
        print(__doc__)
        return 0
    path = argv[1]
    s = open(path, encoding='utf-8').read()
    meta = _meta_from_page(path, s)
    if '--href' in argv:
        meta['offer_box'] = {'href': argv[argv.index('--href') + 1]}
    out = apply(s, meta)
    if out == s:
        print('offer box: no change for %s (existing article, already boxed, or no matching service)' % meta['slug'])
        return 0
    with open(path, 'w', encoding='utf-8') as f:
        f.write(out)
    print('offer box: added %s to %s' % (re.search(r'data-offer="([^"]+)"', out).group(1), meta['slug']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
