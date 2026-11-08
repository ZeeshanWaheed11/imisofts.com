// imisofts free SEO tools: fetch one public web page and return only what the tools need
// (status, redirects, title, robots, canonical, links, images, visible text, robots.txt).
// Used by /broken-link-checker, /xml-sitemap-generator and /website-change-monitor.
// Self-contained on purpose: Pages Functions turn every file under functions/ into a route.

const UA = 'Mozilla/5.0 (compatible; imisofts-SEO-Tools/1.0; +https://imisofts.com/free-seo-tools)';
const MAX_BYTES = 3 * 1024 * 1024;
const TIMEOUT_MS = 12000;
const MAX_HOPS = 5;
const MAX_LINKS = 3000;
const ORIGINS = [/^https:\/\/imisofts\.com$/, /^https:\/\/www\.imisofts\.com$/, /^https:\/\/[a-z0-9-]+\.imisofts-com\.pages\.dev$/];

export function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
  });
}

export function originOk(request) {
  const o = request.headers.get('origin') || '';
  return ORIGINS.some((r) => r.test(o));
}

export function cleanUrl(raw) {
  let s = String(raw == null ? '' : raw).trim();
  if (!s) throw new Error('Enter a URL.');
  if (!/^https?:\/\//i.test(s)) s = 'https://' + s;
  let u;
  try { u = new URL(s); } catch (e) { throw new Error('That does not look like a valid URL.'); }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') throw new Error('Only http and https addresses can be checked.');
  const h = u.hostname.toLowerCase();
  if (!h.includes('.') || h === 'localhost' || /\.(localhost|local|internal|lan|home|corp)$/.test(h) ||
      /^\d{1,3}(\.\d{1,3}){3}$/.test(h) || h.startsWith('[')) {
    throw new Error('Enter a public website address.');
  }
  if (u.username || u.password) throw new Error('Addresses with a username or password are not supported.');
  u.hash = '';
  return u.toString();
}

export async function fetchFollow(url, opts) {
  const o = Object.assign({ method: 'GET', maxHops: MAX_HOPS, timeout: TIMEOUT_MS, accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8' }, opts || {});
  const chain = [];
  let current = url;
  for (let hop = 0; hop <= o.maxHops; hop++) {
    const res = await fetch(current, {
      method: o.method,
      redirect: 'manual',
      headers: { 'user-agent': UA, accept: o.accept, 'accept-language': 'en-US,en;q=0.8' },
      signal: AbortSignal.timeout(o.timeout),
    });
    const loc = res.headers.get('location');
    if (res.status >= 300 && res.status < 400 && loc) {
      chain.push({ url: current, status: res.status });
      try { if (res.body) await res.body.cancel(); } catch (e) { /* ignore */ }
      current = cleanUrl(new URL(loc, current).toString());
      continue;
    }
    return { res, finalUrl: current, chain };
  }
  const err = new Error('Too many redirects');
  err.code = 'redirects';
  err.chain = chain;
  throw err;
}

export async function readText(res, max) {
  const limit = max || MAX_BYTES;
  if (!res.body) return { text: '', bytes: 0, truncated: false };
  const reader = res.body.getReader();
  const parts = [];
  let size = 0;
  let truncated = false;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    if (size + value.byteLength > limit) {
      parts.push(value.slice(0, limit - size));
      size = limit;
      truncated = true;
      try { await reader.cancel(); } catch (e) { /* ignore */ }
      break;
    }
    parts.push(value);
    size += value.byteLength;
  }
  const buf = new Uint8Array(size);
  let off = 0;
  for (const p of parts) { buf.set(p, off); off += p.byteLength; }
  return { text: new TextDecoder('utf-8').decode(buf), bytes: size, truncated };
}

const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', ndash: '-', mdash: '-', hellip: '...', copy: '(c)', rsquo: "'", lsquo: "'", rdquo: '"', ldquo: '"' };
export function decode(s) {
  return String(s).replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const n = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      try { return String.fromCodePoint(n); } catch (x) { return m; }
    }
    const v = NAMED[e.toLowerCase()];
    return v === undefined ? m : v;
  });
}

export function attr(tag, name) {
  const m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*(?:"([^"]*)"|\'([^\']*)\'|([^\\s"\'>]+))', 'i'));
  if (!m) return null;
  return decode(m[1] != null ? m[1] : m[2] != null ? m[2] : m[3]).trim();
}

function abs(href, base) {
  if (!href) return null;
  const h = href.trim();
  if (!h || h[0] === '#' || /^(javascript|mailto|tel|sms|data|ftp|file|about|blob):/i.test(h)) return null;
  try {
    const u = new URL(h, base);
    if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
    u.hash = '';
    return u.toString();
  } catch (e) { return null; }
}

export function parseHtml(html, pageUrl) {
  const src = html.replace(/<!--[\s\S]*?-->/g, ' ').replace(/<(script|style|template)\b[\s\S]*?<\/\1\s*>/gi, ' ');
  let base = pageUrl;
  const bt = src.match(/<base\s[^>]*>/i);
  if (bt) { const b = abs(attr(bt[0], 'href'), pageUrl); if (b) base = b; }
  const tm = src.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = tm ? decode(tm[1]).replace(/\s+/g, ' ').trim() : '';
  let robots = '';
  for (const m of src.matchAll(/<meta\s[^>]*>/gi)) {
    const n = (attr(m[0], 'name') || '').toLowerCase();
    if (n === 'robots' || n === 'googlebot') robots += (robots ? ', ' : '') + (attr(m[0], 'content') || '');
  }
  let canonical = '';
  for (const m of src.matchAll(/<link\s[^>]*>/gi)) {
    const rel = (attr(m[0], 'rel') || '').toLowerCase().split(/\s+/);
    if (rel.includes('canonical')) { canonical = abs(attr(m[0], 'href'), base) || ''; break; }
  }
  const host = new URL(pageUrl).hostname.replace(/^www\./, '');
  const links = [];
  const seen = new Set();
  for (const m of src.matchAll(/<a\s([^>]*)>([\s\S]*?)<\/a\s*>/gi)) {
    if (links.length >= MAX_LINKS) break;
    const tag = '<a ' + m[1] + '>';
    const u = abs(attr(tag, 'href'), base);
    if (!u) continue;
    const relv = (attr(tag, 'rel') || '').toLowerCase();
    let text = decode(m[2].replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
    if (!text) { const im = m[2].match(/<img\s[^>]*>/i); text = im ? '[image] ' + (attr(im[0], 'alt') || '') : ''; }
    const key = u + '|' + text;
    if (seen.has(key)) continue;
    seen.add(key);
    links.push({ u, t: text.slice(0, 140), nf: /nofollow|sponsored|ugc/.test(relv) ? 1 : 0, int: new URL(u).hostname.replace(/^www\./, '') === host ? 1 : 0 });
  }
  const images = [];
  const seenImg = new Set();
  for (const m of src.matchAll(/<img\s[^>]*>/gi)) {
    if (images.length >= 500) break;
    const u = abs(attr(m[0], 'src') || attr(m[0], 'data-src'), base);
    if (!u || seenImg.has(u)) continue;
    seenImg.add(u);
    images.push({ u, t: (attr(m[0], 'alt') || '').slice(0, 140) });
  }
  return { title, robots, canonical, links, images };
}

export function visibleText(html, keepChrome) {
  let s = html.replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<(script|style|noscript|svg|template|iframe|canvas|select)\b[\s\S]*?<\/\1\s*>/gi, ' ');
  if (!keepChrome) s = s.replace(/<(nav|footer)\b[\s\S]*?<\/\1\s*>/gi, ' ');
  s = s.replace(/<\/?(p|div|section|article|li|ul|ol|h[1-6]|br|hr|tr|td|th|table|main|aside|blockquote|pre|dd|dt|dl|figcaption|header|footer|nav|form|label|button|summary|details)\b[^>]*>/gi, '\n')
    .replace(/<[^>]+>/g, ' ');
  return decode(s).split('\n').map((l) => l.replace(/\s+/g, ' ').trim()).filter((l) => l.length > 1).slice(0, 4000);
}

function errorText(e) {
  const m = String((e && (e.message || e)) || '');
  if (e && e.code === 'redirects') return 'Too many redirects';
  if (/timed? ?out|timeout|aborted/i.test(m)) return 'The site took too long to answer';
  return 'Could not connect to the site';
}

export async function onRequest({ request }) {
  if (request.method !== 'POST') return json({ ok: false, error: 'Use POST.' }, 405);
  if (!originOk(request)) return json({ ok: false, error: 'This endpoint only serves imisofts.com tools.' }, 403);
  let body;
  try { body = await request.json(); } catch (e) { return json({ ok: false, error: 'Bad request.' }, 400); }
  let url;
  try { url = cleanUrl(body.url); } catch (e) { return json({ ok: false, error: e.message }, 400); }
  const want = Array.isArray(body.want) ? body.want : ['links'];

  if (want.includes('robots')) {
    const ru = new URL('/robots.txt', url).toString();
    try {
      const { res } = await fetchFollow(ru, { accept: 'text/plain,*/*;q=0.5', maxHops: 3 });
      const r = await readText(res, 200 * 1024);
      return json({ ok: true, url: ru, status: res.status, robots: res.status === 200 ? r.text : '' });
    } catch (e) {
      return json({ ok: true, url: ru, status: 0, robots: '' });
    }
  }

  let out;
  try {
    const { res, finalUrl, chain } = await fetchFollow(url);
    const ctype = (res.headers.get('content-type') || '').toLowerCase();
    out = {
      ok: true, url, finalUrl, status: res.status, chain,
      contentType: ctype, lastModified: res.headers.get('last-modified') || '',
      xRobots: res.headers.get('x-robots-tag') || '',
    };
    if (!/html|xml/.test(ctype) && ctype) {
      try { if (res.body) await res.body.cancel(); } catch (e) { /* ignore */ }
      out.notHtml = true;
      return json(out);
    }
    const r = await readText(res);
    out.bytes = r.bytes;
    out.truncated = r.truncated;
    const p = parseHtml(r.text, finalUrl);
    out.title = p.title;
    out.robots = p.robots;
    out.canonical = p.canonical;
    if (want.includes('links')) { out.links = p.links; out.images = p.images; }
    if (want.includes('text')) out.text = visibleText(r.text, !!body.keepChrome);
  } catch (e) {
    return json({ ok: false, url, error: errorText(e) }, 200);
  }
  return json(out);
}
