/* imisofts free SEO tools 1.1.0 (adds ?url= prefill and auto-start from the /free-seo-tools hub): Broken Link Checker, XML Sitemap Generator, Website Change Monitor.
   Runs in the browser; pages are fetched by /api/tools/page and links checked by /api/tools/check. */
(function () {
  'use strict';
  var root = document.querySelector('[data-tool]');
  if (!root) return;
  var TOOL = root.getAttribute('data-tool');

  /* ---------- helpers ---------- */
  function $(sel, el) { return (el || root).querySelector(sel); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function api(path, body) {
    return fetch('/api/tools/' + path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return { ok: false, error: 'The tool is busy. Please try again in a minute.' }; }); })
      .catch(function () { return { ok: false, error: 'Network error. Check your connection and try again.' }; });
  }
  function normalise(raw) {
    var s = String(raw || '').trim();
    if (!s) return null;
    if (!/^https?:\/\//i.test(s)) s = 'https://' + s;
    try { var u = new URL(s); u.hash = ''; return u.toString(); } catch (e) { return null; }
  }
  function host(u) { try { return new URL(u).hostname.replace(/^www\./, ''); } catch (e) { return ''; } }
  function pool(items, size, worker, onEach) {
    var i = 0, done = 0, stop = false;
    return new Promise(function (resolve) {
      if (!items.length) return resolve();
      function next() {
        if (stop) return;
        if (i >= items.length) { if (done >= items.length) resolve(); return; }
        var item = items[i++];
        Promise.resolve(worker(item)).catch(function () {}).then(function () {
          done++; if (onEach) onEach(done, items.length);
          if (done >= items.length) resolve(); else next();
        });
      }
      for (var k = 0; k < Math.min(size, items.length); k++) next();
    });
  }
  function chunk(arr, n) { var out = []; for (var i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out; }
  function download(name, text, type) {
    var blob = new Blob([text], { type: type || 'text/plain' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function csv(rows) {
    return rows.map(function (r) { return r.map(function (c) { c = String(c == null ? '' : c); return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(','); }).join('\n');
  }
  function track(name, params) { try { if (window.gtag) window.gtag('event', name, Object.assign({ tool: TOOL }, params || {})); } catch (e) {} }
  function setBusy(btn, busy, label) { btn.disabled = busy; btn.textContent = busy ? 'Working...' : label; }
  function progress(text, pct) {
    var p = $('.ft-progress'); if (!p) return;
    p.hidden = false;
    $('.ft-progress-text').textContent = text;
    $('.ft-progress-bar span').style.width = Math.max(2, Math.min(100, pct)) + '%';
  }
  function hideProgress() { var p = $('.ft-progress'); if (p) p.hidden = true; }
  function error(msg) { var e = $('.ft-error'); e.textContent = msg; e.hidden = !msg; }
  var SKIP_EXT = /\.(pdf|jpe?g|png|gif|webp|svg|ico|zip|rar|7z|gz|mp4|mp3|mov|avi|wav|docx?|xlsx?|pptx?|csv|xml|json|txt|css|js|woff2?|ttf|eot|exe|dmg|apk)(\?|$)/i;

  /* ---------- crawler shared by the link checker and the sitemap generator ---------- */
  function crawl(start, opts, onPage) {
    var startHost = host(start), queue = [start], seen = {}, pages = [], active = 0, finished = false;
    seen[start] = 1;
    function enqueue(t) {
      t = t.replace(/#.*$/, '');
      if (seen[t] || host(t) !== startHost || SKIP_EXT.test(t)) return;
      if (opts.allow && !opts.allow(t)) return;
      seen[t] = 1; queue.push(t);
    }
    return new Promise(function (resolve) {
      function finish() { if (!finished) { finished = true; resolve(pages); } }
      function pump() {
        while (active < (opts.concurrency || 3) && queue.length && pages.length + active < opts.max) {
          var u = queue.shift();
          active++;
          api('page', { url: u, want: ['links'] }).then(handle.bind(null, u));
        }
        if (!active) finish();
      }
      function handle(u, r) {
        active--;
        pages.push({ url: u, r: r });
        try { onPage(u, r, pages.length); } catch (e) {}
        if (r && r.ok) {
          if (r.finalUrl && r.finalUrl !== u) enqueue(r.finalUrl);
          if (r.status === 200 && r.links) r.links.forEach(function (l) { if (l.int) enqueue(l.u); });
        }
        pump();
      }
      pump();
    });
  }

  /* ---------- robots.txt (User-agent: * group) ---------- */
  function robotsRules(txt) {
    var groups = [], cur = null, lastWasAgent = false;
    String(txt || '').split(/\r?\n/).forEach(function (line) {
      line = line.replace(/#.*$/, '').trim(); if (!line) return;
      var i = line.indexOf(':'); if (i < 0) return;
      var k = line.slice(0, i).trim().toLowerCase(), v = line.slice(i + 1).trim();
      if (k === 'user-agent') { if (!lastWasAgent || !cur) { cur = { agents: [], rules: [] }; groups.push(cur); } cur.agents.push(v.toLowerCase()); lastWasAgent = true; return; }
      lastWasAgent = false;
      if (!cur) return;
      if (k === 'allow' || k === 'disallow') cur.rules.push({ allow: k === 'allow', path: v });
    });
    var g = groups.filter(function (x) { return x.agents.indexOf('*') >= 0; })[0];
    return g ? g.rules.filter(function (r) { return r.path; }) : [];
  }
  function robotsAllows(rules, url) {
    var u; try { u = new URL(url); } catch (e) { return true; }
    var path = u.pathname + u.search, best = null;
    rules.forEach(function (r) {
      var pat = r.path.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*');
      if (/\\\$$/.test(pat)) pat = pat.slice(0, -2) + '$';
      if (new RegExp('^' + pat).test(path) && (!best || r.path.length > best.path.length || (r.path.length === best.path.length && r.allow))) best = r;
    });
    return !best || best.allow;
  }

  /* ---------- status labels ---------- */
  function verdict(s) {
    if (s.status >= 200 && s.status < 300) return s.chain && s.chain.length ? 'redirect' : 'ok';
    if (s.status === 401 || s.status === 403 || s.status === 429 || s.status === 999) return 'blocked';
    if (s.status >= 300 && s.status < 400) return 'redirect';
    return 'broken';
  }
  var LABEL = { ok: 'OK', redirect: 'Redirect', blocked: 'Blocked', broken: 'Broken' };
  function statusText(s) {
    if (s.status === 530) return 'Domain not found (530)';
    if (s.status) return String(s.status) + (s.chain && s.chain.length ? ' after ' + s.chain.join(' > ') : '');
    return s.error || 'No response';
  }

  /* =====================================================================
     Broken Link Checker
     ===================================================================== */
  function brokenLinks() {
    var form = $('form'), btn = $('button[type=submit]'), out = $('.ft-results');
    var MAX_LINKS = 1000;
    var state = null;
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var url = normalise($('input[name=url]').value);
      if (!url) return error('Enter a page or website address, for example example.com.');
      error(''); out.hidden = true;
      var scope = $('select[name=scope]').value, external = $('input[name=external]').checked, images = $('input[name=images]').checked;
      setBusy(btn, true, 'Check links');
      track('tool_run', { scope: scope });
      var occ = {}, order = [];
      function add(target, text, from, isInt, type) {
        if (!occ[target]) { occ[target] = { u: target, int: isInt, type: type, from: [] }; order.push(target); }
        if (occ[target].from.length < 50) occ[target].from.push({ page: from, text: text });
      }
      var pagesP;
      if (scope === 'page') {
        progress('Reading the page...', 5);
        pagesP = api('page', { url: url, want: ['links'] }).then(function (r) { return [{ url: url, r: r }]; });
      } else {
        var max = parseInt(scope, 10) || 100;
        pagesP = crawl(url, { max: max, concurrency: 3 }, function (u, r, n) { progress('Crawling: ' + n + ' of up to ' + max + ' pages', 5 + 45 * n / max); });
      }
      pagesP.then(function (pages) {
        var first = pages[0] && pages[0].r;
        if (!first || !first.ok) { hideProgress(); setBusy(btn, false, 'Check links'); return error((first && first.error) || 'That page could not be read.'); }
        if (first.status >= 400) { hideProgress(); setBusy(btn, false, 'Check links'); return error('That page answered with HTTP ' + first.status + '. Check the address and try again.'); }
        var known = {};
        pages.forEach(function (p) {
          var r = p.r || {};
          known[p.url] = { url: p.url, status: r.ok ? r.status : 0, chain: (r.chain || []).map(function (c) { return c.status; }), error: r.ok ? '' : r.error };
          (r.links || []).forEach(function (l) { if (external || l.int) add(l.u, l.t, p.url, l.int, l.nf ? 'nofollow' : 'link'); });
          if (images) (r.images || []).forEach(function (im) { add(im.u, im.t ? '[image] ' + im.t : '[image]', p.url, host(im.u) === host(url), 'image'); });
        });
        var targets = order.slice(0, MAX_LINKS);
        var toCheck = targets.filter(function (t) { return !known[t]; });
        var results = {};
        targets.forEach(function (t) { if (known[t]) results[t] = known[t]; });
        progress('Checking ' + toCheck.length + ' links...', 50);
        return pool(chunk(toCheck, 5), 4, function (batch) {
          return api('check', { urls: batch }).then(function (r) {
            (r && r.results ? r.results : batch.map(function (u) { return { url: u, status: 0, error: (r && r.error) || 'Not checked' }; }))
              .forEach(function (x, i) { results[batch[i]] = x; });
          });
        }, function (d, n) { progress('Checked ' + Math.min(d * 5, toCheck.length) + ' of ' + toCheck.length + ' links', 50 + 50 * d / n); })
          .then(function () {
            state = { url: url, pages: pages.length, capped: order.length > MAX_LINKS, rows: targets.map(function (t) { var s = results[t] || { status: 0, error: 'Not checked' }; return { o: occ[t], s: s, v: verdict(s) }; }) };
            hideProgress(); setBusy(btn, false, 'Check links'); render('all');
            track('tool_done', { pages: state.pages, links: state.rows.length, broken: state.rows.filter(function (r) { return r.v === 'broken'; }).length });
          });
      });
    });
    function render(filter) {
      var rows = state.rows, c = { ok: 0, redirect: 0, blocked: 0, broken: 0 };
      rows.forEach(function (r) { c[r.v]++; });
      var rank = { broken: 0, blocked: 1, redirect: 2, ok: 3 };
      var shown = rows.filter(function (r) { return filter === 'all' || r.v === filter; }).sort(function (a, b) { return rank[a.v] - rank[b.v]; });
      out.innerHTML =
        '<div class="ft-stats">' +
          stat(state.pages, state.pages === 1 ? 'Page checked' : 'Pages crawled') + stat(rows.length, 'Unique links') +
          stat(c.broken, 'Broken', 'bad') + stat(c.redirect, 'Redirects', 'warn') + stat(c.blocked, 'Blocked', 'muted') +
        '</div>' +
        (state.capped ? '<p class="ft-note">This run checked the first ' + rows.length + ' unique links. Check single sections of a large site to see the rest.</p>' : '') +
        '<div class="ft-bar"><div class="ft-filters">' + ['all', 'broken', 'redirect', 'blocked', 'ok'].map(function (f) {
          var n = f === 'all' ? rows.length : c[f];
          return '<button type="button" data-f="' + f + '" class="' + (f === filter ? 'on' : '') + '">' + (f === 'all' ? 'All' : LABEL[f]) + ' <span>' + n + '</span></button>';
        }).join('') + '</div><button type="button" class="ft-export">Export CSV</button></div>' +
        (shown.length ? '<div class="ft-table-wrap"><table class="ft-table"><thead><tr><th>Status</th><th>Link</th><th>Anchor text</th><th>Found on</th></tr></thead><tbody>' +
          shown.slice(0, 1000).map(function (r) {
            var f = r.o.from[0] || {};
            return '<tr><td><span class="ft-pill ' + r.v + '">' + LABEL[r.v] + '</span><small>' + esc(statusText(r.s)) + '</small></td>' +
              '<td class="ft-url"><a href="' + esc(r.o.u) + '" target="_blank" rel="nofollow noopener">' + esc(r.o.u) + '</a>' +
              (r.s.finalUrl && r.s.finalUrl !== r.o.u ? '<small>Goes to ' + esc(r.s.finalUrl) + '</small>' : '') + '<small>' + (r.o.int ? 'Internal' : 'External') + (r.o.type !== 'link' ? ', ' + r.o.type : '') + '</small></td>' +
              '<td>' + esc(f.text || '') + '</td>' +
              '<td class="ft-url"><a href="' + esc(f.page || '') + '" target="_blank" rel="nofollow noopener">' + esc((f.page || '').replace(/^https?:\/\//, '')) + '</a>' + (r.o.from.length > 1 ? '<small>and ' + (r.o.from.length - 1) + ' more</small>' : '') + '</td></tr>';
          }).join('') + '</tbody></table></div>' : '<p class="ft-empty">Nothing in this group. ' + (filter === 'broken' ? 'No broken links found.' : '') + '</p>');
      out.hidden = false;
      [].slice.call(out.querySelectorAll('[data-f]')).forEach(function (b) { b.addEventListener('click', function () { render(b.getAttribute('data-f')); }); });
      out.querySelector('.ft-export').addEventListener('click', function () {
        var data = [['Status', 'HTTP', 'Link', 'Final URL', 'Type', 'Anchor text', 'Found on', 'Times found']];
        state.rows.forEach(function (r) { r.o.from.forEach(function (f) { data.push([LABEL[r.v], r.s.status || r.s.error, r.o.u, r.s.finalUrl || '', r.o.int ? 'Internal' : 'External', f.text, f.page, r.o.from.length]); }); });
        download('broken-links-' + host(state.url) + '.csv', csv(data), 'text/csv');
        track('tool_export');
      });
    }
  }
  function stat(n, label, cls) { return '<div class="ft-stat ' + (cls || '') + '"><b>' + n + '</b><span>' + label + '</span></div>'; }

  /* =====================================================================
     XML Sitemap Generator
     ===================================================================== */
  function sitemap() {
    var form = $('form'), btn = $('button[type=submit]'), out = $('.ft-results');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var url = normalise($('input[name=url]').value);
      if (!url) return error('Enter your website address, for example example.com.');
      url = new URL(url).origin + new URL(url).pathname;
      error(''); out.hidden = true;
      var max = parseInt($('select[name=max]').value, 10) || 250;
      var useRobots = $('input[name=robots]').checked, skipNoindex = $('input[name=noindex]').checked, useCanon = $('input[name=canonical]').checked, lastmod = $('input[name=lastmod]').checked;
      setBusy(btn, true, 'Generate sitemap');
      track('tool_run', { max: max });
      progress('Reading robots.txt...', 3);
      (useRobots ? api('page', { url: url, want: ['robots'] }) : Promise.resolve({ robots: '' })).then(function (rb) {
        var rules = robotsRules(rb && rb.robots);
        var allow = useRobots ? function (u) { return robotsAllows(rules, u); } : null;
        var startHost = host(url);
        return crawl(url, { max: max, concurrency: 3, allow: allow }, function (u, r, n) { progress('Crawling: ' + n + ' of up to ' + max + ' pages', 5 + 95 * n / max); })
          .then(function (pages) {
            var inc = {}, excluded = [];
            pages.forEach(function (p) {
              var r = p.r || {};
              if (!r.ok) return excluded.push([p.url, r.error || 'Could not be read']);
              if (r.status !== 200) return excluded.push([p.url, 'HTTP ' + r.status + (r.chain && r.chain.length ? ' (redirects)' : '')]);
              if (r.finalUrl && r.finalUrl !== p.url) return excluded.push([p.url, 'Redirects to ' + r.finalUrl]);
              if (r.notHtml) return excluded.push([p.url, 'Not an HTML page']);
              if (skipNoindex && /noindex/i.test((r.robots || '') + ' ' + (r.xRobots || ''))) return excluded.push([p.url, 'Marked noindex']);
              var loc = p.url;
              if (useCanon && r.canonical && r.canonical !== p.url) {
                if (host(r.canonical) !== startHost) return excluded.push([p.url, 'Canonical points to another site']);
                excluded.push([p.url, 'Canonical is ' + r.canonical]);
                loc = r.canonical;
              }
              if (useRobots && !robotsAllows(rules, loc)) return excluded.push([loc, 'Blocked by robots.txt']);
              if (!inc[loc]) inc[loc] = { loc: loc, lastmod: '' };
              if (lastmod && r.lastModified && loc === p.url) { var d = new Date(r.lastModified); if (!isNaN(d)) inc[loc].lastmod = d.toISOString().slice(0, 10); }
            });
            var list = Object.keys(inc).sort().map(function (k) { return inc[k]; });
            var xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + list.map(function (x) {
              return '  <url>\n    <loc>' + esc(x.loc) + '</loc>\n' + (x.lastmod ? '    <lastmod>' + x.lastmod + '</lastmod>\n' : '') + '  </url>';
            }).join('\n') + '\n</urlset>\n';
            hideProgress(); setBusy(btn, false, 'Generate sitemap');
            out.innerHTML =
              '<div class="ft-stats">' + stat(pages.length, 'Pages crawled') + stat(list.length, 'URLs in sitemap', 'good') + stat(excluded.length, 'Left out', 'muted') + '</div>' +
              (pages.length >= max ? '<p class="ft-note">The crawl stopped at ' + max + ' pages. Choose a higher limit if your site has more pages.</p>' : '') +
              '<div class="ft-bar"><strong>sitemap.xml</strong><div class="ft-actions"><button type="button" class="ft-copy">Copy</button><button type="button" class="ft-export">Download sitemap.xml</button></div></div>' +
              '<pre class="ft-code">' + esc(xml) + '</pre>' +
              (excluded.length ? '<details class="ft-details"><summary>Pages left out and why (' + excluded.length + ')</summary><div class="ft-table-wrap"><table class="ft-table"><thead><tr><th>URL</th><th>Reason</th></tr></thead><tbody>' +
                excluded.slice(0, 1000).map(function (x) { return '<tr><td class="ft-url">' + esc(x[0]) + '</td><td>' + esc(x[1]) + '</td></tr>'; }).join('') + '</tbody></table></div></details>' : '') +
              '<p class="ft-note">Next: upload the file to your site\'s root folder (so it opens at ' + esc(new URL(url).origin) + '/sitemap.xml), add a "Sitemap:" line to robots.txt, and submit it in Google Search Console and Bing Webmaster Tools.</p>';
            out.hidden = false;
            out.querySelector('.ft-export').addEventListener('click', function () { download('sitemap.xml', xml, 'application/xml'); track('tool_export'); });
            out.querySelector('.ft-copy').addEventListener('click', function (ev) {
              var b = ev.currentTarget;
              (navigator.clipboard ? navigator.clipboard.writeText(xml) : Promise.reject()).then(function () { b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy'; }, 1500); }).catch(function () {});
            });
            track('tool_done', { pages: pages.length, urls: list.length });
          });
      });
    });
  }

  /* =====================================================================
     Website Change Monitor
     ===================================================================== */
  var STORE = 'imisofts-change-monitor';
  function loadAll() { try { return JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { return {}; } }
  function saveAll(all) { try { localStorage.setItem(STORE, JSON.stringify(all)); return true; } catch (e) { return false; } }

  function diff(a, b) {
    // Myers O(ND) diff on two arrays; returns [{op:'=', '-', '+', v}]
    var n = a.length, m = b.length, max = n + m, v = { 1: 0 }, trace = [];
    for (var d = 0; d <= max; d++) {
      var vv = {};
      for (var k = -d; k <= d; k += 2) {
        var x = (k === -d || (k !== d && v[k - 1] < v[k + 1])) ? v[k + 1] : v[k - 1] + 1;
        var y = x - k;
        while (x < n && y < m && a[x] === b[y]) { x++; y++; }
        vv[k] = x;
        if (x >= n && y >= m) { trace.push(vv); return backtrack(trace, a, b); }
      }
      trace.push(vv); v = vv;
      if (d > 3000) break;
    }
    return a.map(function (s) { return { op: '-', v: s }; }).concat(b.map(function (s) { return { op: '+', v: s }; }));
  }
  function backtrack(trace, a, b) {
    var x = a.length, y = b.length, ops = [];
    for (var d = trace.length - 1; d > 0; d--) {
      var v = trace[d - 1], k = x - y;
      var prevK = (k === -d || (k !== d && v[k - 1] < v[k + 1])) ? k + 1 : k - 1;
      var prevX = v[prevK], prevY = prevX - prevK;
      while (x > prevX && y > prevY) { ops.push({ op: '=', v: a[x - 1] }); x--; y--; }
      if (x === prevX) ops.push({ op: '+', v: b[y - 1] }); else ops.push({ op: '-', v: a[x - 1] });
      x = prevX; y = prevY;
    }
    while (x > 0 && y > 0) { ops.push({ op: '=', v: a[x - 1] }); x--; y--; }
    return ops.reverse();
  }
  function wordDiff(oldLine, newLine) {
    var ow = oldLine.split(/(\s+)/), nw = newLine.split(/(\s+)/);
    return diff(ow, nw).map(function (p) { return p.op === '=' ? esc(p.v) : p.op === '+' ? '<ins>' + esc(p.v) + '</ins>' : '<del>' + esc(p.v) + '</del>'; }).join('');
  }

  function changeMonitor() {
    var form = $('form'), btn = $('button[type=submit]'), out = $('.ft-results'), list = $('.ft-watchlist');
    function renderList() {
      var all = loadAll(), keys = Object.keys(all);
      if (!list) return;
      if (!keys.length) { list.hidden = true; return; }
      list.hidden = false;
      list.innerHTML = '<div class="ft-bar"><strong>Pages you are monitoring in this browser</strong></div><ul>' + keys.sort().map(function (k) {
        var s = all[k];
        return '<li><button type="button" class="ft-link" data-u="' + esc(k) + '">' + esc(k.replace(/^https?:\/\//, '')) + '</button><small>Saved ' + esc(new Date(s.saved).toLocaleString()) + '</small>' +
          '<button type="button" class="ft-remove" data-del="' + esc(k) + '" aria-label="Stop monitoring">Remove</button></li>';
      }).join('') + '</ul>';
      [].slice.call(list.querySelectorAll('[data-u]')).forEach(function (b) { b.addEventListener('click', function () { $('input[name=url]').value = b.getAttribute('data-u'); form.requestSubmit ? form.requestSubmit() : btn.click(); }); });
      [].slice.call(list.querySelectorAll('[data-del]')).forEach(function (b) { b.addEventListener('click', function () { var all2 = loadAll(); delete all2[b.getAttribute('data-del')]; saveAll(all2); renderList(); }); });
    }
    renderList();
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var url = normalise($('input[name=url]').value);
      if (!url) return error('Enter the address of the page you want to monitor.');
      error(''); out.hidden = true;
      var keepChrome = !$('input[name=chrome]').checked;
      setBusy(btn, true, 'Check for changes');
      progress('Reading the page...', 30);
      api('page', { url: url, want: ['text'], keepChrome: keepChrome }).then(function (r) {
        hideProgress(); setBusy(btn, false, 'Check for changes');
        if (!r || !r.ok) return error((r && r.error) || 'That page could not be read.');
        if (r.status >= 400) return error('That page answered with HTTP ' + r.status + '.');
        var lines = r.text || [], all = loadAll(), prev = all[url], now = new Date().toISOString();
        track('tool_run', { first: prev ? 0 : 1 });
        if (!prev) {
          all[url] = { saved: now, title: r.title || '', lines: lines };
          var stored = saveAll(all);
          out.innerHTML = '<div class="ft-callout good"><strong>First version saved.</strong> ' + (stored ? 'Come back any time and click "Check for changes" to see what changed on this page since ' + esc(new Date(now).toLocaleString()) + '.' : 'Your browser did not allow saving. Turn off private browsing to keep versions.') + '</div>' +
            '<details class="ft-details"><summary>Text we saved (' + lines.length + ' lines)</summary><div class="ft-diff">' + lines.map(function (l) { return '<p>' + esc(l) + '</p>'; }).join('') + '</div></details>';
          out.hidden = false; renderList(); return;
        }
        var ops = diff(prev.lines, lines), added = 0, removed = 0, html = [], i = 0;
        while (i < ops.length) {
          if (ops[i].op === '=') { html.push({ k: '=', v: '<p>' + esc(ops[i].v) + '</p>' }); i++; continue; }
          var dels = [], adds = [];
          while (i < ops.length && ops[i].op !== '=') { (ops[i].op === '-' ? dels : adds).push(ops[i].v); i++; }
          removed += dels.length; added += adds.length;
          var pairs = Math.min(dels.length, adds.length);
          for (var p = 0; p < pairs; p++) html.push({ k: 'c', v: '<p class="chg">' + wordDiff(dels[p], adds[p]) + '</p>' });
          dels.slice(pairs).forEach(function (d) { html.push({ k: '-', v: '<p class="del"><del>' + esc(d) + '</del></p>' }); });
          adds.slice(pairs).forEach(function (a) { html.push({ k: '+', v: '<p class="add"><ins>' + esc(a) + '</ins></p>' }); });
        }
        // show changed lines with 2 lines of context around them
        var keep = html.map(function () { return false; });
        html.forEach(function (h, idx) { if (h.k !== '=') for (var j = Math.max(0, idx - 2); j <= Math.min(html.length - 1, idx + 2); j++) keep[j] = true; });
        var body = '', gap = false;
        html.forEach(function (h, idx) { if (keep[idx]) { body += h.v; gap = false; } else if (!gap) { body += '<p class="gap">...</p>'; gap = true; } });
        var changed = added || removed;
        out.innerHTML = '<div class="ft-stats">' + stat(added, 'Lines added', added ? 'good' : '') + stat(removed, 'Lines removed', removed ? 'bad' : '') + stat(lines.length, 'Lines on the page now') + '</div>' +
          '<p class="ft-note">Compared with the version saved ' + esc(new Date(prev.saved).toLocaleString()) + '.</p>' +
          (changed ? '<div class="ft-diff">' + body + '</div>' : '<div class="ft-callout">No text changes since the saved version.</div>') +
          '<div class="ft-actions"><button type="button" class="ft-save">Save this as the new version</button></div>';
        out.hidden = false;
        out.querySelector('.ft-save').addEventListener('click', function (ev) {
          var all2 = loadAll(); all2[url] = { saved: new Date().toISOString(), title: r.title || '', lines: lines }; saveAll(all2);
          ev.currentTarget.textContent = 'Saved'; ev.currentTarget.disabled = true; renderList();
        });
        track('tool_done', { added: added, removed: removed });
      });
    });
  }

  if (TOOL === 'broken-links') brokenLinks();
  else if (TOOL === 'sitemap') sitemap();
  else if (TOOL === 'change-monitor') changeMonitor();
  // Prefill from ?url= (sent by the tool picker on /free-seo-tools) and start the check
  try {
    var pre = new URLSearchParams(location.search).get('url');
    var inp = $('input[name=url]'), frm = $('form');
    if (pre && inp && frm) {
      inp.value = pre.slice(0, 2000);
      setTimeout(function () { if (frm.requestSubmit) frm.requestSubmit(); else $('button[type=submit]').click(); }, 50);
    }
  } catch (e) {}
  window.__imisoftsTools = { robotsRules: robotsRules, robotsAllows: robotsAllows, diff: diff, verdict: verdict };
})();
