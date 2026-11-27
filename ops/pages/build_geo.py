import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import page, esc, ROOT
from geo_css import GEO_CSS
from countries import PAGES, ICONS, STATS, PROOF

SITE = 'https://imisofts.com'
FORM_SRC = 'https://forms.clickup.com/90182475304/p/f/2kzmpqh8-778/LRSQ2Q9CSVZE21JQM2/contact-us-form-all-pages'


def strip_tags(t):
    return re.sub(r'<[^>]+>', '', t)


def icon(name):
    return ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % ICONS[name])


def build(p):
    url = '%s/%s' % (SITE, p['slug'])
    m = []
    # ---- hero
    m.append('''
  <section class="gl-hero">
    <div class="container">
      <div class="gl-hero-grid">
        <div>
          <nav class="gl-crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/lead-generation">Lead generation</a><span>/</span>%(crumb)s</nav>
          <div class="gl-badge">%(badge)s</div>
          <h1>%(h1)s</h1>
          <p class="gl-lead">%(lead)s</p>
          <div class="gl-ctas">
            <a href="#contact" class="gl-btn gl-btn-primary">Get a free audit &rarr;</a>
            <a href="/cold-email-marketing#packages" class="gl-btn gl-btn-secondary">See packages</a>
          </div>
          <div class="gl-stats">''' % dict(crumb=esc(p['crumb']), badge=esc(p['badge']), h1=p['h1'], lead=esc(p['lead'])))
    for n, l in STATS:
        m.append('''
            <div><div class="gl-stat-num">%s</div><div class="gl-stat-label">%s</div></div>''' % (esc(n), esc(l)))
    m.append('''
          </div>
        </div>
        <div class="gl-card">
          <div class="gl-card-title">%s</div>
          <ul class="gl-check">''' % esc(p['card_title']))
    for it in p['card_items']:
        m.append('\n            <li>%s</li>' % esc(it))
    m.append('''
          </ul>
          <div class="gl-card-foot">%s</div>
        </div>
      </div>
    </div>
  </section>
''' % esc(p['card_foot']))
    # ---- services
    m.append('''
  <section class="gl-section">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">Services</span>
        <h2>%s</h2>
        <p>%s</p>
      </div>
      <div class="gl-grid3">''' % (esc(p['services_title']), esc(p['services_intro'])))
    for ic, h, d, href, label in p['services']:
        m.append('''
        <div class="gl-tile">
          <div class="gl-icon">%s</div>
          <h3>%s</h3>
          <p>%s</p>
          <a class="gl-more" href="%s">%s &rarr;</a>
        </div>''' % (icon(ic), esc(h), esc(d), href, esc(label)))
    m.append('''
      </div>
    </div>
  </section>
''')
    # ---- rules
    m.append('''
  <section class="gl-section gl-alt">
    <div class="container">
      <div class="gl-split">
        <div class="gl-prose">
          <span class="gl-eyebrow">Compliance</span>
          <h2>%s</h2>''' % esc(p['rules_title']))
    for para in p['rules_prose']:
        m.append('\n          <p>%s</p>' % esc(para))
    m.append('\n          <p style="margin-bottom:10px;">Read our full guides:</p>\n          <div class="gl-pills">')
    for href, label in p['guides']:
        m.append('<a href="%s">%s</a>' % (href, esc(label)))
    m.append('''</div>
          <p class="gl-note">This page is practical guidance, not legal advice.</p>
        </div>
        <div class="gl-rules">''')
    for h, d in p['rules']:
        m.append('''
          <div class="gl-rule"><strong>%s</strong><p>%s</p></div>''' % (esc(h), esc(d)))
    m.append('''
        </div>
      </div>
    </div>
  </section>
''')
    # ---- steps
    m.append('''
  <section class="gl-section">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">How it works</span>
        <h2>How a campaign starts</h2>
        <p>Four steps from first call to booked meetings. You approve the list, the copy and the launch.</p>
      </div>
      <div class="gl-steps">''')
    for h, d in p['steps']:
        m.append('''
        <div class="gl-step"><h3>%s</h3><p>%s</p></div>''' % (esc(h), esc(d)))
    m.append('''
      </div>
    </div>
  </section>
''')
    # ---- proof
    m.append('''
  <section class="gl-section gl-alt">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">Why imisofts</span>
        <h2>Why B2B teams choose imisofts</h2>
        <p>An outbound and AI automation agency founded in 2019 and headquartered in Dubai. Pricing is published and plans are month-to-month.</p>
      </div>
      <div class="gl-proof">''')
    for n, l in PROOF:
        m.append('''
        <div class="gl-proof-item"><div class="gl-proof-num">%s</div><div class="gl-proof-label">%s</div></div>''' % (esc(n), esc(l)))
    m.append('''
      </div>
      <div class="gl-band">
        <p>%s</p>
        <a href="#contact" class="gl-btn gl-btn-primary">Get a free audit &rarr;</a>
      </div>
    </div>
  </section>
''' % p['timezone'])
    # ---- faq
    m.append('''
  <section class="gl-section">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">FAQ</span>
        <h2>Questions we hear from %s companies</h2>
      </div>
      <div class="gl-faq">''' % esc('UK' if p['slug'].endswith('-uk') else ('Australian' if 'australia' in p['slug'] else 'UAE')))
    for q, a in p['faq']:
        m.append('''
        <details>
          <summary>%s</summary>
          <p>%s</p>
        </details>''' % (esc(q), a))
    m.append('''
      </div>
    </div>
  </section>
''')
    # ---- contact
    m.append('''
  <section class="gl-contact" id="contact">
    <div class="container">
      <div class="gl-contact-grid">
        <div>
          <span class="gl-eyebrow">Free audit</span>
          <h2>Get a free outbound audit for your %s market</h2>
          <p class="gl-sub">Tell us who you sell to and we will send back a written audit within 24 hours: who to target, how many inboxes you need, what to say, and which plan fits.</p>
          <ul class="gl-check">
            <li>Your ideal customer profile and list size</li>
            <li>A sending setup that protects your main domain</li>
            <li>Compliance points for your target country</li>
            <li>A clear recommendation, with no obligation</li>
          </ul>
          <div class="gl-contact-meta">Prefer to talk? <a href="https://cal.com/zeeshanwaheed/30min" target="_blank" rel="noopener">Book a 30 minute call</a> or email <a href="mailto:growth@imisofts.com">growth@imisofts.com</a>.<br>imisofts, The Prism Tower, 19th Floor, Business Bay, Dubai, United Arab Emirates.</div>
        </div>
        <div class="gl-formcard">
          <h3>Get your free audit</h3>
          <p class="gl-formsub">Takes 30 seconds. Audit delivered within 24 hours.</p>
          <div class="gl-formwrap">
            <iframe class="clickup-embed" title="Free audit contact form" src="%s" onwheel="" loading="lazy" scrolling="no"></iframe>
          </div>
          <script async src="https://app-cdn.clickup.com/assets/js/forms-embed/v1.js"></script>
          <div class="gl-formalt">Prefer to chat? <a href="https://wa.me/971524320369" target="_blank" rel="noopener noreferrer">WhatsApp us</a></div>
        </div>
      </div>
    </div>
  </section>
''' % (esc({'uk': 'UK', 'au': 'Australian', 'ae': 'UAE'}[p['key']]), FORM_SRC))
    # ---- related
    m.append('''
  <section class="gl-section">
    <div class="container">
      <div class="gl-head" style="margin-bottom:32px;">
        <h2>More on outbound by country</h2>
      </div>
      <div class="gl-related">''')
    for href, t, sub in p['related']:
        m.append('\n        <a href="%s">%s<small>%s</small></a>' % (href, esc(t), esc(sub)))
    m.append('''
      </div>
    </div>
  </section>
''')
    main_html = ''.join(m)

    org = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'imisofts', 'url': SITE,
           'logo': SITE + '/logo.svg',
           'address': {'@type': 'PostalAddress', 'streetAddress': 'The Prism Tower, 19th Floor, Business Bay',
                       'addressLocality': 'Dubai', 'addressCountry': 'AE'},
           'telephone': '+971524320369', 'email': 'growth@imisofts.com'}
    service = {'@context': 'https://schema.org', '@type': 'Service', '@id': url + '#service',
               'name': p['service_name'], 'serviceType': 'B2B lead generation', 'url': url,
               'description': p['description'], 'areaServed': p['area'], 'provider': org,
               'offers': {'@type': 'Offer', 'url': SITE + '/pricing', 'availability': 'https://schema.org/InStock'}}
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE},
        {'@type': 'ListItem', 'position': 2, 'name': 'Lead generation', 'item': SITE + '/lead-generation'},
        {'@type': 'ListItem', 'position': 3, 'name': p['crumb'], 'item': url}]}
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}} for q, a in p['faq']]}

    return page(title=p['title'], description=p['description'], canonical=url,
                robots='index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1',
                og_url=url, og_image=SITE + '/og-image-lead-gen.jpg', schema=[service, crumbs, faq],
                extra_css=GEO_CSS, main_html=main_html)


if __name__ == '__main__':
    for key, p in PAGES.items():
        p['key'] = key
        out = build(p)
        path = os.path.join(ROOT, p['slug'] + '.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
        print('wrote', path, len(out))
