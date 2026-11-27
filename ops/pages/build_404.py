import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shell import page, esc, ROOT
from geo_css import GEO_CSS
from countries import ICONS

ICONS = dict(ICONS)
ICONS.update({
    'bolt': '<path d="M13 3L5 13.5h6L10 21l8-10.5h-6L13 3z"/>',
    'spark': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6.3 6.3l2.5 2.5M15.2 15.2l2.5 2.5M6.3 17.7l2.5-2.5M15.2 8.8l2.5-2.5"/>',
    'layers': '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    'tool': '<path d="M14.5 6.5a4 4 0 0 0-5.3 5.3L4 17v3h3l5.2-5.2a4 4 0 0 0 5.3-5.3l-2.6 2.6-2.4-.6-.6-2.4 2.6-2.6z"/>',
})


def icon(name, size=22):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % (size, size, ICONS[name]))


POPULAR = [
    ('mail', 'Cold email marketing', 'Done-for-you campaigns that land in the inbox and book meetings.', '/cold-email-marketing'),
    ('server', 'Email infrastructure', 'Domains, inboxes, SPF, DKIM, DMARC and warm-up, set up for you.', '/email-infrastructure'),
    ('users', 'B2B lead generation', 'Verified lists, outreach and appointment setting for your sales team.', '/lead-generation'),
    ('phone', 'AI voice agents', 'AI callers and receptionists that answer, qualify and book around the clock.', '/ai-voice-agents'),
    ('bolt', 'AI automation', 'n8n, Make and custom AI workflows that take busywork off your team.', '/ai-automation'),
    ('layers', 'GoHighLevel services', 'Setup, automations and white-label SaaS on GoHighLevel.', '/gohighlevel-services'),
    ('spark', 'AI search optimization', 'Get your brand cited by ChatGPT, Perplexity and Google AI Overviews.', '/ai-search-optimization'),
    ('tool', 'Free SEO and email tools', 'DNS, SPF, DKIM and DMARC checkers, keyword tools and more.', '/free-seo-tools'),
]

GUIDES = [
    ('/blog/cold-email-laws-by-country/', 'Cold email laws by country'),
    ('/blog/how-many-domains-cold-email-2026/', 'How many domains you need for cold email'),
    ('/blog/cold-email-deliverability/', 'Cold email deliverability'),
    ('/blog/apollo-pricing-plans-2026/', 'Apollo pricing plans'),
    ('/blog/instantly-pricing-plans-2026/', 'Instantly pricing plans'),
    ('/blog/gohighlevel-pricing-2026/', 'GoHighLevel pricing'),
    ('/blog/cold-email-templates-b2b/', 'B2B cold email templates'),
    ('/pricing', 'imisofts pricing'),
]

NF_CSS = """
<style id="not-found-1127">
.nf-hero{padding:136px 0 72px;background:linear-gradient(to bottom,#ffffff,#f9fafb);text-align:center}
.nf-hero [hidden]{display:none !important}
.nf-wrap{max-width:820px}
.nf-code{font-size:150px;font-weight:800;line-height:1;letter-spacing:-4px;color:#0F172A;margin:4px 0 18px;user-select:none}
.nf-code span{color:#F45407}
.nf-hero h1{font-size:44px;font-weight:800;line-height:1.2;margin-bottom:18px;color:#1a1a1a}
.nf-hero h1 span{color:#F45407}
.nf-hero .gl-lead{max-width:640px;margin:0 auto 28px}
.nf-hero code{background:#f2f4f7;color:#344054;padding:2px 8px;border-radius:6px;font-size:15px;word-break:break-all;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.nf-suggest{text-align:left;background:#fff;border:1px solid #eef0f3;border-radius:14px;padding:18px 22px 8px;margin:0 auto 22px;max-width:640px;box-shadow:0 12px 30px rgba(15,23,42,.06)}
.nf-label{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:#999;margin-bottom:6px}
.nf-suggest ul{list-style:none;margin:0;padding:0}
.nf-suggest li a{display:block;padding:12px 0;border-top:1px solid #f2f4f7;color:#0F172A;text-decoration:none;font-weight:500;font-size:16px;line-height:1.4}
.nf-suggest li:first-child a{border-top:none}
.nf-suggest li a:hover{color:#F45407}
.nf-suggest small,.nf-results small{display:block;color:#98a2b3;font-weight:400;font-size:13px;margin-top:2px;word-break:break-all}
.nf-search{position:relative;max-width:640px;margin:0 auto 28px;text-align:left}
.nf-search input{width:100%;padding:16px 18px 16px 50px;border:1px solid #e5e7eb;border-radius:12px;font-size:16px;color:#1a1a1a;background:#fff;outline:none;box-shadow:0 8px 24px rgba(15,23,42,.05);-webkit-appearance:none;appearance:none}
.nf-search input:focus{border-color:#F45407;box-shadow:0 0 0 3px rgba(244,84,7,.15)}
.nf-search > svg{position:absolute;left:17px;top:27px;transform:translateY(-50%);color:#98a2b3;pointer-events:none}
.nf-results{position:absolute;left:0;right:0;top:calc(100% + 6px);background:#fff;border:1px solid #eef0f3;border-radius:12px;box-shadow:0 20px 40px rgba(0,0,0,.12);list-style:none;margin:0;padding:6px 0;max-height:380px;overflow:auto;z-index:20}
.nf-results a{display:block;padding:11px 16px;color:#0F172A;text-decoration:none;font-size:15px;line-height:1.4}
.nf-results a:hover,.nf-results a.nf-active{background:#fff5f3}
.nf-results .nf-empty{padding:12px 16px;color:#667085;font-size:15px}
.nf-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
.nf-ctas{justify-content:center;margin-bottom:0}
.nf-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.nf-grid .gl-tile{display:block;text-decoration:none}
.nf-grid .gl-tile p{margin-bottom:0}
.nf-guides{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;max-width:900px;margin:0 auto}
@media (max-width:1024px){.nf-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:640px){.nf-hero{padding:108px 0 56px}.nf-code{font-size:104px;letter-spacing:-2px}.nf-hero h1{font-size:32px}.nf-grid{grid-template-columns:1fr}}
</style>
"""

NF_JS = r"""
  <script>
  (function () {
    var STOP = ['blog', 'www', 'imisofts', 'com', 'index', 'html', 'htm', 'php', 'amp', 'the', 'and', 'for', 'of', 'to', 'in', 'a', 'an', 'vs', 'on', 'with', 'how', 'what', 'is', 'your', 'page', 'utm'];
    function toks(s) {
      var t = String(s || '').toLowerCase();
      try { t = decodeURIComponent(t); } catch (e) {}
      return (t.match(/[a-z0-9]+/g) || []).filter(function (w) { return w.length > 1 && STOP.indexOf(w) < 0; });
    }
    function norm(p) { return String(p || '').toLowerCase().replace(/\.html?$/, '').replace(/\/+$/, '') || '/'; }
    var here = location.pathname;
    var pathEl = document.getElementById('nf-path');
    if (pathEl && here && here !== '/404' && here !== '/404.html') {
      pathEl.textContent = here.length > 120 ? here.slice(0, 117) + '...' : here;
      document.getElementById('nf-path-wrap').hidden = false;
    }
    function track(name, url) {
      try { if (typeof window.gtag === 'function') window.gtag('event', name, { link_url: url, page_path_missing: here.slice(0, 100) }); } catch (e) {}
    }
    function item(title, path, onclickName) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = path;
      a.appendChild(document.createTextNode(title));
      var sm = document.createElement('small');
      sm.textContent = 'imisofts.com' + path;
      a.appendChild(sm);
      a.addEventListener('click', function () { track(onclickName, path); });
      li.appendChild(a);
      return li;
    }
    var index = null, loading = null;
    function load() {
      if (index) return Promise.resolve(index);
      if (loading) return loading;
      loading = fetch('/search-index.json', { credentials: 'omit' })
        .then(function (r) { if (!r.ok) throw new Error('index'); return r.json(); })
        .then(function (d) {
          index = (d && d.pages || []).map(function (e) {
            return { t: e[0], p: e[1], pt: toks(e[1]), tt: toks(e[0]) };
          });
          return index;
        })
        .catch(function () { index = []; return index; });
      return loading;
    }
    // ---- "did you mean" from the missing URL ----
    function suggest(list) {
      var q = toks(here);
      if (!q.length || !list.length) return;
      var target = norm(here);
      var scored = list.map(function (e) {
        if (norm(e.p) === target) return { e: e, s: 99 };
        var s = 0, hit = 0;
        q.forEach(function (w) {
          if (e.pt.indexOf(w) >= 0) { s += 3; hit++; return; }
          for (var i = 0; i < e.pt.length; i++) {
            var p = e.pt[i];
            if (p.length >= 4 && w.length >= 4 && (p.indexOf(w) === 0 || w.indexOf(p) === 0)) { s += 2; hit++; return; }
          }
          if (e.tt.indexOf(w) >= 0) { s += 1; hit++; }
        });
        var score = s / (3 * q.length) - 0.02 * Math.max(0, e.pt.length - hit);
        return { e: e, s: score };
      }).filter(function (x) { return x.s >= 0.34; });
      scored.sort(function (a, b) { return b.s - a.s || a.e.p.length - b.e.p.length; });
      var top = scored.slice(0, 5);
      if (!top.length) return;
      var ul = document.getElementById('nf-suggest-list');
      top.forEach(function (x) { ul.appendChild(item(x.e.t, x.e.p, 'not_found_suggestion_click')); });
      document.getElementById('nf-suggest').hidden = false;
    }
    load().then(suggest);
    // ---- site search ----
    var input = document.getElementById('nf-q');
    var box = document.getElementById('nf-results');
    var active = -1;
    function render(q) {
      var words = toks(q);
      box.innerHTML = '';
      active = -1;
      if (!words.length) { box.hidden = true; return; }
      var res = index.filter(function (e) {
        var all = e.tt.concat(e.pt);
        return words.every(function (w) { return all.some(function (t) { return t.indexOf(w) === 0; }); });
      });
      res.sort(function (a, b) {
        var ta = words.every(function (w) { return a.tt.some(function (t) { return t.indexOf(w) === 0; }); }) ? 0 : 1;
        var tb = words.every(function (w) { return b.tt.some(function (t) { return t.indexOf(w) === 0; }); }) ? 0 : 1;
        return ta - tb || (a.p.indexOf('/blog/') === 0) - (b.p.indexOf('/blog/') === 0) || a.t.length - b.t.length;
      });
      res = res.slice(0, 8);
      if (!res.length) {
        var li = document.createElement('li');
        li.className = 'nf-empty';
        li.textContent = 'No matches. Try another word, or browse the blog.';
        box.appendChild(li);
      } else {
        res.forEach(function (e) { box.appendChild(item(e.t, e.p, 'not_found_search_click')); });
      }
      box.hidden = false;
    }
    if (input && box) {
      input.addEventListener('focus', function () { load(); });
      input.addEventListener('input', function () { var v = input.value; load().then(function () { render(v); }); });
      input.addEventListener('keydown', function (ev) {
        var links = box.querySelectorAll('a');
        if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
          if (!links.length) return;
          ev.preventDefault();
          active = ev.key === 'ArrowDown' ? Math.min(active + 1, links.length - 1) : Math.max(active - 1, 0);
          links.forEach(function (l, i) { l.classList.toggle('nf-active', i === active); });
        } else if (ev.key === 'Enter') {
          ev.preventDefault();
          var go = links[active >= 0 ? active : 0];
          if (go) { track('not_found_search_click', go.getAttribute('href')); location.href = go.getAttribute('href'); }
        } else if (ev.key === 'Escape') {
          box.hidden = true;
        }
      });
      document.addEventListener('click', function (ev) { if (!ev.target.closest || !ev.target.closest('.nf-search')) box.hidden = true; });
    }
  })();
  </script>
"""


def build():
    m = []
    m.append('''
  <section class="nf-hero">
    <div class="container nf-wrap">
      <div class="gl-badge">Error 404</div>
      <div class="nf-code" aria-hidden="true">4<span>0</span>4</div>
      <h1>We couldn&#x27;t find <span>that page</span></h1>
      <p class="gl-lead">The link may be old, or the page may have moved. <span id="nf-path-wrap" hidden>You asked for <code id="nf-path"></code>. </span>Try one of the closest matches below, or search the site.</p>
      <div class="nf-suggest" id="nf-suggest" hidden>
        <div class="nf-label">Did you mean</div>
        <ul id="nf-suggest-list"></ul>
      </div>
      <form class="nf-search" role="search" onsubmit="return false;">
        <label for="nf-q" class="nf-sr">Search imisofts.com</label>
        %s
        <input id="nf-q" type="search" placeholder="Search guides, services and free tools" autocomplete="off" spellcheck="false" aria-controls="nf-results">
        <ul id="nf-results" class="nf-results" hidden></ul>
      </form>
      <div class="gl-ctas nf-ctas">
        <a href="/" class="gl-btn gl-btn-primary">Back to homepage &rarr;</a>
        <a href="/blog" class="gl-btn gl-btn-secondary">Browse the blog</a>
        <a href="/contact" class="gl-btn gl-btn-secondary">Contact us</a>
      </div>
    </div>
  </section>
''' % icon('search', 20))
    m.append('''
  <section class="gl-section gl-alt">
    <div class="container">
      <div class="gl-head">
        <span class="gl-eyebrow">Popular on imisofts</span>
        <h2>What most visitors are looking for</h2>
        <p>imisofts builds cold email infrastructure, B2B lead generation and AI automation for growing businesses. Start with one of these.</p>
      </div>
      <div class="nf-grid">''')
    for ic, t, d, href in POPULAR:
        m.append('''
        <a class="gl-tile" href="%s">
          <div class="gl-icon">%s</div>
          <h3>%s</h3>
          <p>%s</p>
        </a>''' % (href, icon(ic), esc(t), esc(d)))
    m.append('''
      </div>
    </div>
  </section>

  <section class="gl-section">
    <div class="container">
      <div class="gl-head" style="margin-bottom:28px;">
        <span class="gl-eyebrow">Most-read guides</span>
        <h2>Popular guides and pricing pages</h2>
      </div>
      <div class="gl-pills nf-guides">''')
    for href, t in GUIDES:
        m.append('<a href="%s">%s</a>' % (href, esc(t)))
    m.append('''</div>
    </div>
  </section>
''')
    return page(title='Page Not Found | imisofts',
                description="The page you're looking for doesn't exist or has moved. Find cold email, lead generation and AI automation services, guides and free tools on imisofts.",
                canonical=None, robots='noindex, follow', og_url='https://imisofts.com/404',
                og_image='https://imisofts.com/og-image.jpg', schema=[], extra_css=GEO_CSS + NF_CSS,
                main_html=''.join(m), tail_js=NF_JS)


if __name__ == '__main__':
    out = build()
    with open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8') as f:
        f.write(out)
    print('wrote 404.html', len(out))
