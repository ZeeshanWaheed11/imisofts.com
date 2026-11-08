// imisofts free SEO tools: check the HTTP status of up to 5 links per call (Broken Link Checker).
// HEAD first, GET when a server refuses HEAD; redirects followed by hand so every hop is reported.
// Self-contained on purpose: Pages Functions turn every file under functions/ into a route.

const UA = 'Mozilla/5.0 (compatible; imisofts-SEO-Tools/1.0; +https://imisofts.com/broken-link-checker)';
const PER_CALL = 5;      // 5 links x (4 HEAD + 4 GET) stays under the 50 subrequest limit
const MAX_HOPS = 3;
const TIMEOUT_MS = 10000;
const ORIGINS = [/^https:\/\/imisofts\.com$/, /^https:\/\/www\.imisofts\.com$/, /^https:\/\/[a-z0-9-]+\.imisofts-com\.pages\.dev$/];

function json(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' },
  });
}

export function cleanUrl(raw) {
  let s = String(raw == null ? '' : raw).trim();
  if (!/^https?:\/\//i.test(s)) throw new Error('invalid');
  const u = new URL(s);
  const h = u.hostname.toLowerCase();
  if (!h.includes('.') || h === 'localhost' || /\.(localhost|local|internal|lan|home|corp)$/.test(h) ||
      /^\d{1,3}(\.\d{1,3}){3}$/.test(h) || h.startsWith('[') || u.username || u.password) {
    throw new Error('private');
  }
  u.hash = '';
  return u.toString();
}

async function follow(url, method) {
  const chain = [];
  let current = url;
  for (let hop = 0; hop <= MAX_HOPS; hop++) {
    const res = await fetch(current, {
      method,
      redirect: 'manual',
      headers: { 'user-agent': UA, accept: 'text/html,application/xhtml+xml,*/*;q=0.8', 'accept-language': 'en-US,en;q=0.8' },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    try { if (res.body) await res.body.cancel(); } catch (e) { /* ignore */ }
    const loc = res.headers.get('location');
    if (res.status >= 300 && res.status < 400 && loc) {
      chain.push(res.status);
      current = cleanUrl(new URL(loc, current).toString());
      continue;
    }
    return { status: res.status, finalUrl: current, chain };
  }
  return { status: -1, finalUrl: current, chain };
}

const RETRY_WITH_GET = new Set([400, 401, 403, 404, 405, 406, 410, 429, 500, 501, 502, 503, 999]);

export async function checkOne(raw) {
  let url;
  try { url = cleanUrl(raw); } catch (e) { return { url: String(raw || ''), status: 0, error: 'Not a public http(s) address' }; }
  const t0 = Date.now();
  try {
    let r = await follow(url, 'HEAD');
    if (RETRY_WITH_GET.has(r.status)) r = await follow(url, 'GET');
    const out = { url, status: r.status, finalUrl: r.finalUrl, chain: r.chain, ms: Date.now() - t0 };
    if (r.status === -1) { out.status = 0; out.error = 'Too many redirects'; }
    return out;
  } catch (e) {
    const m = String((e && e.message) || e);
    return { url, status: 0, error: /timed? ?out|timeout|aborted/i.test(m) ? 'Timed out' : 'Could not connect', ms: Date.now() - t0 };
  }
}

export async function onRequest({ request }) {
  if (request.method !== 'POST') return json({ ok: false, error: 'Use POST.' }, 405);
  const o = request.headers.get('origin') || '';
  if (!ORIGINS.some((r) => r.test(o))) return json({ ok: false, error: 'This endpoint only serves imisofts.com tools.' }, 403);
  let body;
  try { body = await request.json(); } catch (e) { return json({ ok: false, error: 'Bad request.' }, 400); }
  const urls = (Array.isArray(body.urls) ? body.urls : []).slice(0, PER_CALL);
  const results = await Promise.all(urls.map(checkOne));
  return json({ ok: true, results });
}
