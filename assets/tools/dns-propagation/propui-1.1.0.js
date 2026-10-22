/* SPF, DKIM & DMARC Checker by imisofts: shows a propagation check (propagation.js) as plain DOM.
   Shared by the popup and the full-tab page. DNS data is always set as text, never as HTML. */
(function (root) {
  'use strict';
  const P = root.ImisoftsPropagation;
  const STATE_TEXT = { live: 'Live', old: 'Other value', missing: 'Not found', seen: 'Answer', differs: 'Different', error: 'No answer' };
  const PLACEHOLDER = { A: '1.2.3.4', CNAME: 'target.example.com', TXT: 'paste the full text', MX: '10 mail.example.com', NS: 'ns1.example.com', AAAA: '2001:db8::1' };

  function el(tag, cls, text) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }

  function link(text, href, cls) {
    const a = el('a', cls || null, text);
    a.href = href; a.target = '_blank'; a.rel = 'noopener';
    return a;
  }

  function sub(c) {
    return c.name + ' \u00b7 ' + c.type + (c.expected ? ' \u00b7 expecting ' + c.expected.raw : '') + ' \u00b7 checked ' + new Date(c.checkedAt).toLocaleTimeString();
  }

  // The round state icon. Its symbol comes from CSS, so screen readers skip it: the row text says the same.
  function icon() {
    const i = el('span', 'pico', '');
    i.setAttribute('aria-hidden', 'true');
    return i;
  }

  // One line per DNS provider: icon, provider, what it answers, and when it checks again.
  function row(r, c) {
    const d = el('div', 'prow ' + r.state);
    d.appendChild(icon());
    const name = el('span', 'pname', r.name);
    name.title = r.full;
    d.appendChild(name);
    let val;
    if (r.state === 'error') val = 'No answer (' + r.error + ')';
    else if (r.state === 'missing') val = r.nxdomain ? 'Not found' : 'No ' + c.type + ' record';
    else val = P.ordered(r.records, c.type).map(x => x.show).join(', ');
    const v = el('span', 'pval');
    if (r.state !== 'missing' && r.state !== 'error') v.appendChild(el('span', 'sr', STATE_TEXT[r.state] + ': '));
    v.appendChild(document.createTextNode(val));
    v.title = val;
    d.appendChild(v);
    let when = '';
    if (r.state === 'missing' && r.negTtl && !c.stuck) when = 'checks again in ' + P.minutes(r.negTtl);
    else if ((r.state === 'old' || r.state === 'differs') && r.ttl && !c.stuck) when = 'checks again in ' + P.minutes(r.ttl);
    d.appendChild(el('span', 'pwhen', when));
    return d;
  }

  function renderRows(box, c) {
    box.textContent = '';
    c.results.forEach(r => box.appendChild(row(r, c)));
  }

  function renderNotes(box, c, max) {
    box.textContent = '';
    const shown = new Set();                 // the same flush links are offered once, on the first note that has them
    c.notes.slice(0, max || 3).forEach(n => {
      const d = el('div', 'pnote ' + n.level);
      d.appendChild(el('span', null, n.text));
      const links = (n.links || []).filter(x => !shown.has(x.url));
      if (links.length) {
        const l = el('span', 'pnote-links');
        links.forEach(x => { shown.add(x.url); l.appendChild(link(x.label, x.url, 'pnote-a')); });
        d.appendChild(l);
      }
      box.appendChild(d);
    });
  }

  function hostLine(c) { return P.hostText(c.zone); }

  // Everything for one check, into the given elements (any can be missing).
  function render(els, c) {
    if (els.summary) els.summary.className = 'sum psum ' + c.state;
    if (els.title) els.title.textContent = c.headline;
    if (els.sub) els.sub.textContent = sub(c);
    if (els.rows) renderRows(els.rows, c);
    if (els.host) {
      els.host.textContent = hostLine(c);
      els.host.title = c.zone && c.zone.ns && c.zone.ns.length ? 'Name servers: ' + c.zone.ns.join(', ') : '';
      els.host.hidden = !els.host.textContent;
    }
    if (els.notes) renderNotes(els.notes, c, els.maxNotes);
    if (els.whatsmydns) els.whatsmydns.href = P.whatsmydnsUrl(c.name, c.type, c.expected ? c.expected.raw : '');
  }

  // "live 4/6" style short status, for tab titles and list rows.
  function short(c) {
    if (c.state === 'error') return c.servfail ? 'DNS error' : 'no answer';
    if (c.proxied && c.state !== 'done') return 'proxied';
    if (c.stuck === 'apex') return 'not possible';
    if (c.expected) return c.state === 'done' ? 'live everywhere' : 'live ' + c.live + '/' + c.total;
    if (c.state === 'none') return 'not found';
    return c.state === 'done' ? 'same everywhere' : 'mixed answers';
  }

  // The watch page link: the check to repeat travels in the URL fragment of the extension's own page.
  function watchHash(name, type, expected) {
    return '#watch?name=' + encodeURIComponent(name) + '&type=' + encodeURIComponent(type) + (expected ? '&expect=' + encodeURIComponent(expected) : '');
  }

  function parseHash(hash) {
    const h = String(hash || '').replace(/^#/, '');
    const q = h.indexOf('?');
    const view = q < 0 ? h : h.slice(0, q);
    const params = {};
    if (q >= 0) h.slice(q + 1).split('&').forEach(kv => {
      const i = kv.indexOf('=');
      if (i > 0) { try { params[kv.slice(0, i)] = decodeURIComponent(kv.slice(i + 1)); } catch (e) { /* ignore a broken value */ } }
    });
    return { view, params };
  }

  /* ---------- recent propagation checks (kept only in this browser) ---------- */
  function getRecent() {
    try {
      const r = JSON.parse(localStorage.getItem('recentProp') || '[]');
      return Array.isArray(r) ? r.filter(x => x && typeof x.name === 'string' && P.RECORD_TYPES.includes(x.type)).slice(0, 5) : [];
    } catch (e) { return []; }
  }
  function addRecent(item) {
    try {
      const key = x => x.type + ' ' + x.name;
      const r = [item].concat(getRecent().filter(x => key(x) !== key(item))).slice(0, 5);
      localStorage.setItem('recentProp', JSON.stringify(r));
    } catch (e) { /* storage unavailable */ }
  }

  async function copy(text) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch (e) {
      const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
      let ok = false;
      try { ok = document.execCommand('copy') === true; } catch (e2) { ok = false; }
      ta.remove();
      return ok;
    }
  }

  root.ImisoftsPropUI = { el, link, icon, render, renderRows, renderNotes, hostLine, short, sub, watchHash, parseHash, getRecent, addRecent, copy, PLACEHOLDER, STATE_TEXT };
})(typeof self !== 'undefined' ? self : globalThis);
