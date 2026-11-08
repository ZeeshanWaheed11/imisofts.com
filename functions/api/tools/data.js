// imisofts free SEO data tools: keyword research, SERP, rankings, backlinks, traffic, AI visibility, plagiarism.
// One POST endpoint for 14 tools. Live data from DataForSEO; the API login and password are Cloudflare secrets.
// Guard rails: origin check, strict input limits, a daily budget per visitor and per data center,
// and answers cached per data center so a repeat search costs nothing.
// Self-contained on purpose: Pages Functions turn every file under functions/ into a route.

const API = 'https://api.dataforseo.com/v3/';
const ORIGINS = [/^https:\/\/imisofts\.com$/, /^https:\/\/www\.imisofts\.com$/, /^https:\/\/[a-z0-9-]+\.imisofts-com\.pages\.dev$/];
const DAY = 86400;
const VISITOR_UNITS = 25;   // per visitor (IP) per UTC day; cached answers are free
const COLO_UNITS = 800;     // per Cloudflare data center per UTC day; the DataForSEO daily cap sits behind this
const CACHE_NAME = 'imisofts-data-tools';
const KEY_BASE = 'https://imisofts.com/__data-tools/';
const V = 'v1';             // bump to drop every cached answer

class UserError extends Error {}
class ApiError extends Error {
  constructor(code, msg) { super(msg || String(code)); this.code = code; }
}

function json(data, status, extra) {
  const headers = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', 'x-robots-tag': 'noindex' };
  if (extra) Object.assign(headers, extra);
  return new Response(JSON.stringify(data), { status: status || 200, headers });
}

// [location_code, language_code, ISO country, name]
const COUNTRIES = {
  us: [2840, 'en', 'US', 'United States'],
  uk: [2826, 'en', 'GB', 'United Kingdom'],
  ca: [2124, 'en', 'CA', 'Canada'],
  au: [2036, 'en', 'AU', 'Australia'],
  in: [2356, 'en', 'IN', 'India'],
  ae: [2784, 'en', 'AE', 'United Arab Emirates'],
  pk: [2586, 'en', 'PK', 'Pakistan'],
  sg: [2702, 'en', 'SG', 'Singapore'],
  nz: [2554, 'en', 'NZ', 'New Zealand'],
  ie: [2372, 'en', 'IE', 'Ireland'],
  za: [2710, 'en', 'ZA', 'South Africa'],
  sa: [2682, 'en', 'SA', 'Saudi Arabia'],
  de: [2276, 'de', 'DE', 'Germany'],
  fr: [2250, 'fr', 'FR', 'France'],
  es: [2724, 'es', 'ES', 'Spain'],
  it: [2380, 'it', 'IT', 'Italy'],
  nl: [2528, 'nl', 'NL', 'Netherlands'],
  br: [2076, 'pt', 'BR', 'Brazil'],
  mx: [2484, 'es', 'MX', 'Mexico'],
};
const BING = ['us', 'uk', 'ca', 'au', 'in', 'de', 'fr'];
const AMAZON = ['us', 'uk', 'ca', 'de', 'fr', 'es', 'it', 'in', 'au'];
const FATAL = new Set([40100, 40104, 40200, 40201, 40202, 40203, 40207, 40209, 40210]);

// ---------- small helpers ----------
function str(v) { return String(v == null ? '' : v); }
function num(v) { return typeof v === 'number' && isFinite(v) ? v : null; }
function clip(s, n) { s = str(s).trim(); return s.length > n ? s.slice(0, n - 1).trim() + '…' : s; }
function bare(h) { return str(h).toLowerCase().replace(/^www\./, '').replace(/\.$/, ''); }
function hostOf(u) { try { return bare(new URL(u).hostname); } catch (e) { return ''; } }
function sameSite(host, dom) { host = bare(host); return !!dom && !!host && (host === dom || host.endsWith('.' + dom)); }
function uniq(a) { return Array.from(new Set(a)); }
function enc(k) { return str(k).replace(/%/g, '%25').replace(/\+/g, '%2B'); } // SERP API decodes %## and +
function isFatal(e) { return e instanceof ApiError && FATAL.has(e.code); }
function softFail(e) { if (isFatal(e)) throw e; return []; }
function escRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

async function sha256hex(s) {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return Array.from(new Uint8Array(d)).map((b) => b.toString(16).padStart(2, '0')).join('').slice(0, 40);
}

const OPERATORS = /(^|\s)-?(allinanchor|allintext|allintitle|allinurl|cache|define|definition|filetype|inanchor|info|intext|intitle|inurl|link|site|related):/i;

export function keyword(raw, max) {
  max = max || 80;
  const s = str(raw).replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!s) throw new UserError('Enter a keyword.');
  if (s.length > max) throw new UserError('Keep the keyword under ' + max + ' characters.');
  if (s.split(' ').length > 10) throw new UserError('Use a keyword of 10 words or fewer.');
  if (OPERATORS.test(s)) throw new UserError('Search operators such as site: are not supported here. Enter a plain keyword.');
  return s.toLowerCase();
}

export function domain(raw) {
  let s = str(raw).trim().toLowerCase();
  if (!s) throw new UserError('Enter a domain, for example example.com.');
  if (!/^[a-z][a-z0-9+.-]*:\/\//.test(s)) s = 'https://' + s;
  let h;
  try { h = new URL(s).hostname; } catch (e) { throw new UserError('That does not look like a domain. Try example.com.'); }
  h = bare(h);
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(h) || h.startsWith('[')) throw new UserError('Enter a domain name, not an IP address.');
  if (h.length > 253 || !/^([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$/.test(h) || /\.\d+$/.test(h) || /(^|\.)(localhost|local|internal|lan|home|corp)$/.test(h)) {
    throw new UserError('That does not look like a domain. Try example.com.');
  }
  return h;
}

export function target(raw) {
  let s = str(raw).trim();
  if (!s) throw new UserError('Enter a domain or a page URL.');
  if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(s)) s = 'https://' + s;
  let u;
  try { u = new URL(s); } catch (e) { throw new UserError('That does not look like a domain or URL. Try example.com.'); }
  const h = domain(u.hostname);
  if ((u.pathname && u.pathname !== '/') || u.search) {
    if (!/^https?:$/.test(u.protocol)) throw new UserError('Use an http or https address.');
    u.hash = '';
    const full = u.toString();
    if (full.length > 500) throw new UserError('That URL is too long.');
    return { kind: 'page', target: full };
  }
  return { kind: 'domain', target: h };
}

function country(raw, list) {
  const c = str(raw || 'us').toLowerCase();
  if (!(list || Object.keys(COUNTRIES)).includes(c)) throw new UserError('Pick a country from the list.');
  return c;
}
function device(raw) { return raw === 'mobile' ? 'mobile' : 'desktop'; }

// ---------- DataForSEO ----------
async function dfs(env, path, task, ms) {
  const auth = 'Basic ' + btoa(env.DATAFORSEO_LOGIN + ':' + env.DATAFORSEO_PASSWORD);
  let r;
  try {
    r = await fetch(API + path, {
      method: 'POST',
      headers: { authorization: auth, 'content-type': 'application/json' },
      body: JSON.stringify([task]),
      signal: AbortSignal.timeout(ms || 45000),
    });
  } catch (e) {
    throw new ApiError(e && (e.name === 'TimeoutError' || e.name === 'AbortError') ? 'timeout' : 'network', str(e && e.message));
  }
  let j;
  try { j = await r.json(); } catch (e) { throw new ApiError(r.status === 401 ? 40100 : 'http' + r.status, 'Bad response'); }
  if (!j || j.status_code !== 20000) throw new ApiError((j && j.status_code) || r.status, j && j.status_message);
  const t = (j.tasks || [])[0];
  if (!t) throw new ApiError('notask', 'No task in response');
  if (t.status_code === 40102) return { result: [], cost: num(t.cost) || 0 }; // no search results
  if (t.status_code !== 20000) throw new ApiError(t.status_code, t.status_message);
  return { result: t.result || [], cost: num(t.cost) || 0 };
}

export function apiError(e) {
  const c = e && e.code;
  if (c === 'timeout') return [504, 'The data source took too long to answer. Please try again.'];
  if (c === 40200 || c === 40210 || c === 40203) return [503, "Our free data checks have reached today's limit. Please try again tomorrow."];
  if (c === 40202 || c === 40209) return [429, 'Lots of people are using the tools right now. Please try again in a minute.'];
  if (c === 40100 || c === 40104 || c === 40201 || c === 40207) return [503, 'This tool is being switched on. Please try again a little later.'];
  if (c === 40204) return [503, 'This check is not available right now. Please try another tool.'];
  if (c === 40501 || c === 40503 || c === 40506 || c === 40402) return [400, 'This search could not run with those settings. Try another country, or check the keyword or domain.'];
  if (c === 'allfailed') return [502, 'The AI assistants did not answer this time. Please try again.'];
  return [502, 'We could not get the data right now. Please try again in a minute.'];
}

// ---------- shaping helpers ----------
function kwRow(it, fallback) {
  if (!it || typeof it !== 'object') return null;
  const ki = it.keyword_info || {};
  const kp = it.keyword_properties || {};
  const si = it.search_intent_info || {};
  return { k: str(it.keyword || fallback), v: num(ki.search_volume), kd: num(kp.keyword_difficulty), cpc: num(ki.cpc), comp: ki.competition_level || null, intent: si.main_intent || null };
}

function trend(ki) {
  const m = (ki && Array.isArray(ki.monthly_searches)) ? ki.monthly_searches.slice() : [];
  return m.filter((x) => x && x.year && x.month)
    .sort((a, b) => (a.year - b.year) || (a.month - b.month))
    .slice(-12)
    .map((x) => ({ y: x.year, m: x.month, v: num(x.search_volume) }));
}

function serpItems(res) { return (res && res[0] && Array.isArray(res[0].items)) ? res[0].items : []; }

function organic(items, limit) {
  return (items || []).filter((i) => i && i.type === 'organic').slice(0, limit || 100).map((i) => ({
    pos: num(i.rank_group), title: clip(i.title, 160), url: str(i.url), domain: bare(i.domain || hostOf(i.url)), desc: clip(i.description, 280),
  }));
}

function mdToText(md) {
  return clip(str(md)
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/\[\d+(,\s*\d+)*\]/g, '')
    .replace(/^#{1,6}\s*/gm, '')
    .replace(/\*\*|__/g, '')
    .replace(/^\s*[*-]\s+/gm, '• ')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n'), 6000);
}

function aiText(item) {
  const parts = [];
  (item.items || []).forEach((e) => { if (e) { if (e.title) parts.push(e.title); if (e.text) parts.push(e.text); } });
  return parts.join('\n\n');
}

function aiSources(item) {
  const refs = [], links = [], seen = new Set();
  (function walk(node, depth) {
    if (!node || depth > 8 || typeof node !== 'object') return;
    if (Array.isArray(node)) { node.forEach((n) => walk(n, depth + 1)); return; }
    if (typeof node.url === 'string' && /^https?:\/\//.test(node.url)) {
      const key = node.url.split('#')[0];
      const row = { title: clip(node.title || node.source || hostOf(node.url), 140), url: node.url, domain: hostOf(node.url), source: node.source ? clip(node.source, 60) : null };
      if (node.type === 'ai_overview_reference' && !seen.has(key)) { seen.add(key); refs.push(row); }
      else if (node.type === 'link_element' && !seen.has('l:' + key)) { seen.add('l:' + key); links.push(row); }
    }
    for (const k in node) { const v = node[k]; if (v && typeof v === 'object') walk(v, depth + 1); }
  })(item, 0);
  const have = new Set(refs.map((r) => r.url.split('#')[0]));
  links.forEach((l) => { if (!have.has(l.url.split('#')[0])) { have.add(l.url.split('#')[0]); refs.push(l); } });
  return refs.slice(0, 30);
}

function llmText(res) {
  const r = res && res[0];
  const parts = [], cited = [], read = [], seen = new Set();
  const add = (list, a) => {
    if (!a || typeof a.url !== 'string' || !/^https?:\/\//.test(a.url)) return;
    const key = a.url.split('#')[0];
    if (seen.has(key)) return;
    seen.add(key);
    list.push({ title: clip(a.title || hostOf(a.url), 140), url: a.url, domain: hostOf(a.url) });
  };
  if (!r) return { text: '', sources: [] };
  (r.items || []).forEach((item) => {
    if (!item || item.type === 'reasoning') return;
    (item.sections || []).forEach((sec) => {
      if (!sec) return;
      if (sec.text) parts.push(sec.text);
      (sec.annotations || []).forEach((a) => add(cited, a));
    });
    (item.annotations || []).forEach((a) => add(cited, a));
    (item.search_results || []).forEach((a) => add(read, a));
  });
  (r.search_results || []).forEach((a) => add(read, a));
  const sources = cited.map((s) => Object.assign(s, { cited: true })).concat(read.map((s) => Object.assign(s, { cited: false })));
  return { text: parts.join('\n\n'), sources };
}

function brandTerms(brand, site) {
  const terms = new Set();
  const b = str(brand).trim().toLowerCase();
  if (b) terms.add(b);
  const asDomain = b.replace(/^https?:\/\//, '').replace(/^www\./, '').replace(/\/.*$/, '');
  if (/^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(asDomain)) { terms.add(asDomain); const base = asDomain.split('.')[0]; if (base.length >= 3) terms.add(base); }
  if (site) { terms.add(site); const base = site.split('.')[0]; if (base.length >= 3) terms.add(base); }
  return Array.from(terms).filter((t) => t.length >= 2);
}

function mentions(text, terms) {
  const t = str(text).toLowerCase();
  return terms.some((term) => new RegExp('(^|[^a-z0-9])' + escRe(term) + '($|[^a-z0-9])', 'i').test(t));
}

function words(s) { return str(s).toLowerCase().replace(/[^a-z0-9À-ɏ\s']/gi, ' ').split(/\s+/).filter(Boolean); }

export function phraseHit(sentence, haystack) {
  const w = words(sentence), h = ' ' + words(haystack).join(' ') + ' ';
  const n = Math.min(5, w.length);
  for (let i = 0; i + n <= w.length; i++) { if (h.includes(' ' + w.slice(i, i + n).join(' ') + ' ')) return true; }
  return false;
}

export function pickSentences(text, max) {
  let parts = str(text).split(/(?<=[.!?])\s+/).map((s) => s.replace(/["“”]/g, '').replace(/\s+/g, ' ').trim()).filter(Boolean);
  let cands = parts.filter((s) => s.split(' ').length >= 7);
  if (cands.length < 2) {
    const w = str(text).replace(/["“”]/g, '').split(/\s+/).filter(Boolean);
    cands = [];
    for (let i = 0; i < w.length; i += 16) cands.push(w.slice(i, i + 16).join(' '));
    cands = cands.filter((s) => s.split(' ').length >= 7);
  }
  cands = uniq(cands.map((s) => s.split(' ').slice(0, 30).join(' ').replace(/[.!?;:,]+$/, '')));
  if (cands.length <= max) return cands;
  const out = [], step = cands.length / max;
  for (let i = 0; i < max; i++) out.push(cands[Math.floor(i * step)]);
  return out;
}

function topEntries(obj, n) {
  if (!obj || typeof obj !== 'object') return [];
  return Object.keys(obj).filter((k) => k && typeof obj[k] === 'number').sort((a, b) => obj[b] - obj[a]).slice(0, n).map((k) => ({ k, v: obj[k] }));
}

function summary(s) {
  s = s || {};
  return {
    score: num(s.rank), backlinks: num(s.backlinks), rd: num(s.referring_domains), rmd: num(s.referring_main_domains),
    rd_nofollow: num(s.referring_domains_nofollow), ips: num(s.referring_ips), subnets: num(s.referring_subnets),
    broken: num(s.broken_backlinks), spam: num(s.backlinks_spam_score), first_seen: s.first_seen || null,
    nofollow: s.referring_links_attributes && num(s.referring_links_attributes.nofollow),
    tlds: topEntries(s.referring_links_tld, 6), countries: topEntries(s.referring_links_countries, 6),
    types: topEntries(s.referring_links_types, 6), platforms: topEntries(s.referring_links_platform_types, 6),
  };
}

function compLabel(c) { c = num(c); return c == null ? null : (c >= 0.75 ? 'HIGH' : c >= 0.35 ? 'MEDIUM' : 'LOW'); }

// ---------- the tools ----------
export const TOOLS = {
  'keyword-generator': {
    units: 1, ttl: 7 * DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), country: country(i.country) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const res = (await call('dataforseo_labs/google/keyword_suggestions/live', { keyword: n.keyword, location_code: loc, language_code: lang, include_seed_keyword: true, limit: 100, order_by: ['keyword_info.search_volume,desc'] }))[0] || {};
      const rows = (res.items || []).map((it) => kwRow(it)).filter((r) => r && r.k);
      if (rows.length < 10) {
        const res2 = (await call('dataforseo_labs/google/keyword_ideas/live', { keywords: [n.keyword], location_code: loc, language_code: lang, limit: 100, order_by: ['keyword_info.search_volume,desc'] }).catch(softFail))[0] || {};
        const have = new Set(rows.map((r) => r.k));
        (res2.items || []).forEach((it) => { const r = kwRow(it); if (r && r.k && !have.has(r.k)) { have.add(r.k); rows.push(r); } });
      }
      const seed = res.seed_keyword_data ? kwRow(res.seed_keyword_data, n.keyword) : null;
      return { keyword: n.keyword, country: n.country, seed, total: num(res.total_count), rows };
    },
  },

  'keyword-difficulty-checker': {
    units: 1, ttl: 7 * DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), country: country(i.country) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const [ov, serp] = await Promise.all([
        call('dataforseo_labs/google/keyword_overview/live', { keywords: [n.keyword], location_code: loc, language_code: lang, include_serp_info: true }),
        call('serp/google/organic/live/regular', { keyword: enc(n.keyword), location_code: loc, language_code: lang, depth: 10 }).catch(softFail),
      ]);
      const it = ((ov[0] || {}).items || [])[0];
      const top = organic(serpItems(serp), 10);
      if (!it) return { keyword: n.keyword, country: n.country, found: false, top };
      const ab = it.avg_backlinks_info || {};
      const si = it.serp_info || {};
      return Object.assign(kwRow(it, n.keyword), {
        keyword: n.keyword, country: n.country, found: true, trend: trend(it.keyword_info),
        rd: num(ab.referring_main_domains) != null ? num(ab.referring_main_domains) : num(ab.referring_domains),
        bl: num(ab.backlinks), features: (si.serp_item_types || []).filter((t) => t !== 'organic').slice(0, 20),
        results: num(si.se_results_count), top,
      });
    },
  },

  'serp-checker': {
    units: 2, ttl: DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), country: country(i.country), device: device(i.device) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const [serp, ov] = await Promise.all([
        call('serp/google/organic/live/advanced', { keyword: enc(n.keyword), location_code: loc, language_code: lang, device: n.device, depth: 10 }),
        call('dataforseo_labs/google/keyword_overview/live', { keywords: [n.keyword], location_code: loc, language_code: lang }).catch(softFail),
      ]);
      const r0 = serp[0] || {};
      const items = r0.items || [];
      const org = organic(items, 10);
      const ranks = {};
      const doms = uniq(org.map((o) => o.domain).filter(Boolean));
      if (doms.length) {
        try {
          const br = await call('backlinks/bulk_ranks/live', { targets: doms, rank_scale: 'one_hundred' });
          ((br[0] || {}).items || []).forEach((x) => { if (x && x.target) ranks[bare(x.target)] = num(x.rank); });
        } catch (e) { if (isFatal(e)) throw e; }
      }
      org.forEach((o) => { o.authority = Object.prototype.hasOwnProperty.call(ranks, o.domain) ? ranks[o.domain] : null; });
      const paa = [], related = [];
      items.forEach((i) => {
        if (!i) return;
        if (i.type === 'people_also_ask') (i.items || []).forEach((q) => { if (q && q.title) paa.push(clip(q.title, 160)); });
        if (i.type === 'related_searches') (i.items || []).forEach((q) => { const t = typeof q === 'string' ? q : (q && (q.title || q.query)); if (t) related.push(clip(t, 120)); });
      });
      const kw = kwRow(((ov[0] || {}).items || [])[0], n.keyword);
      return {
        keyword: n.keyword, country: n.country, device: n.device, volume: kw ? kw.v : null, kd: kw ? kw.kd : null,
        results: num(r0.se_results_count), features: uniq((r0.item_types || []).filter((t) => t !== 'organic')),
        organic: org, paa: uniq(paa).slice(0, 8), related: uniq(related).slice(0, 10), aio: items.some((i) => i && i.type === 'ai_overview'),
      };
    },
  },

  'keyword-rank-checker': {
    units: 2, ttl: DAY / 2,
    unitsFor: (n) => 2 * n.keywords.length,
    validate(i) {
      const d = domain(i.domain);
      const list = str(i.keywords).split(/[\n,]+/).map((s) => s.trim()).filter(Boolean);
      if (!list.length) throw new UserError('Enter at least one keyword.');
      if (list.length > 3) throw new UserError('Check up to 3 keywords at a time.');
      return { domain: d, keywords: uniq(list.map((k) => keyword(k))), country: country(i.country), device: device(i.device) };
    },
    key: (n) => ({ keywords: n.keywords, country: n.country, device: n.device }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const lists = await Promise.all(n.keywords.map(async (k) => {
        try {
          const res = await call('serp/google/organic/live/regular', { keyword: enc(k), location_code: loc, language_code: lang, device: n.device, depth: 100 });
          return { keyword: k, results: organic(serpItems(res), 100).map((o) => ({ pos: o.pos, url: o.url, domain: o.domain, title: o.title })) };
        } catch (e) { if (isFatal(e)) throw e; return { keyword: k, error: true, results: [] }; }
      }));
      if (lists.every((l) => l.error)) throw new ApiError('allfailed', 'All keyword checks failed');
      return { country: n.country, device: n.device, lists };
    },
    post(d, n) {
      return {
        domain: n.domain, country: d.country, device: d.device,
        rows: d.lists.map((l) => {
          if (l.error) return { keyword: l.keyword, error: true };
          const mine = l.results.filter((o) => sameSite(o.domain, n.domain));
          return { keyword: l.keyword, pos: mine.length ? mine[0].pos : null, url: mine.length ? mine[0].url : null, title: mine.length ? mine[0].title : null, more: mine.slice(1, 4).map((m) => m.pos), top: l.results.slice(0, 3), checked: l.results.length };
        }),
      };
    },
  },

  'website-traffic-checker': {
    units: 2, ttl: 7 * DAY,
    validate: (i) => ({ domain: domain(i.domain), country: country(i.country) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const [ov, kws, pages] = await Promise.all([
        call('dataforseo_labs/google/domain_rank_overview/live', { target: n.domain, location_code: loc, language_code: lang }),
        call('dataforseo_labs/google/ranked_keywords/live', { target: n.domain, location_code: loc, language_code: lang, item_types: ['organic'], limit: 20, order_by: ['ranked_serp_element.serp_item.etv,desc'] }).catch(softFail),
        call('dataforseo_labs/google/relevant_pages/live', { target: n.domain, location_code: loc, language_code: lang, item_types: ['organic'], limit: 10, order_by: ['metrics.organic.etv,desc'] }).catch(softFail),
      ]);
      const m = ((((ov[0] || {}).items || [])[0]) || {}).metrics || {};
      const o = m.organic || {}, p = m.paid || {};
      const z = (k) => num(o[k]) || 0;
      return {
        domain: n.domain, country: n.country, found: !!num(o.count),
        traffic: num(o.etv), keywords: num(o.count), value: num(o.estimated_paid_traffic_cost),
        paid_traffic: num(p.etv), paid_keywords: num(p.count),
        positions: [['1 to 3', z('pos_1') + z('pos_2_3')], ['4 to 10', z('pos_4_10')], ['11 to 20', z('pos_11_20')], ['21 to 50', z('pos_21_30') + z('pos_31_40') + z('pos_41_50')], ['51 to 100', z('pos_51_60') + z('pos_61_70') + z('pos_71_80') + z('pos_81_90') + z('pos_91_100')]],
        movement: { new: num(o.is_new), up: num(o.is_up), down: num(o.is_down), lost: num(o.is_lost) },
        top_keywords: ((kws[0] || {}).items || []).map((it) => {
          const kd = it.keyword_data || {}, si = ((it.ranked_serp_element || {}).serp_item) || {};
          return { k: str(kd.keyword), pos: num(si.rank_group), v: num((kd.keyword_info || {}).search_volume), etv: num(si.etv), url: str(si.url) };
        }).filter((r) => r.k),
        top_pages: ((pages[0] || {}).items || []).map((it) => { const mo = ((it.metrics || {}).organic) || {}; return { url: str(it.page_address), etv: num(mo.etv), keywords: num(mo.count) }; }).filter((r) => r.url),
      };
    },
  },

  'website-authority-checker': {
    units: 1, ttl: 3 * DAY,
    validate: (i) => ({ domain: domain(i.domain) }),
    async run(n, call) {
      const s = (await call('backlinks/summary/live', { target: n.domain, include_subdomains: true, rank_scale: 'one_hundred', backlinks_status_type: 'live', internal_list_limit: 10 }))[0];
      return Object.assign({ domain: n.domain, found: !!s }, summary(s));
    },
  },

  'backlink-checker': {
    units: 2, ttl: 3 * DAY,
    validate: (i) => target(i.target),
    async run(n, call) {
      const base = { target: n.target, backlinks_status_type: 'live', rank_scale: 'one_hundred' };
      if (n.kind === 'domain') base.include_subdomains = true;
      const [sum, list] = await Promise.all([
        call('backlinks/summary/live', Object.assign({ internal_list_limit: 10 }, base)),
        call('backlinks/backlinks/live', Object.assign({ mode: 'one_per_domain', exclude_internal_backlinks: true, limit: 100, order_by: ['domain_from_rank,desc'] }, base)),
      ]);
      const l0 = list[0] || {};
      const links = (l0.items || []).map((b) => ({
        from: str(b.url_from), title: clip(b.page_from_title, 140), domain: bare(b.domain_from), dr: num(b.domain_from_rank), pr: num(b.page_from_rank),
        anchor: clip(b.anchor, 120), dofollow: !!b.dofollow, type: b.item_type || null, to: str(b.url_to), first_seen: b.first_seen || null, last_seen: b.last_seen || null, is_new: !!b.is_new,
      })).filter((b) => b.from);
      return Object.assign({ target: n.target, kind: n.kind, found: !!sum[0] }, summary(sum[0]), { total_domains: num(l0.total_count), links });
    },
  },

  'ai-overview-tracker': {
    units: 1, ttl: DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), domain: str(i.domain).trim() ? domain(i.domain) : null, country: country(i.country), device: device(i.device) }),
    key: (n) => ({ keyword: n.keyword, country: n.country, device: n.device }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const res = await call('serp/google/organic/live/advanced', { keyword: enc(n.keyword), location_code: loc, language_code: lang, device: n.device, depth: 10, load_async_ai_overview: true });
      const items = serpItems(res);
      const aio = items.find((i) => i && i.type === 'ai_overview');
      const out = { keyword: n.keyword, country: n.country, device: n.device, has: !!aio, organic: organic(items, 10).map((o) => ({ pos: o.pos, url: o.url, domain: o.domain, title: o.title })) };
      if (aio) { out.text = mdToText(aio.markdown || aiText(aio)); out.sources = aiSources(aio); }
      return out;
    },
    post(d, n) {
      d.domain = n.domain;
      if (n.domain) {
        const hit = (d.sources || []).findIndex((s) => sameSite(s.domain, n.domain));
        d.cited = d.has ? (hit >= 0 ? hit + 1 : 0) : null;
        const o = d.organic.find((x) => sameSite(x.domain, n.domain));
        d.your_pos = o ? o.pos : null;
      }
      return d;
    },
  },

  'ai-mode-tracker': {
    units: 1, ttl: DAY,
    validate: (i) => ({ keyword: keyword(i.keyword, 200), domain: str(i.domain).trim() ? domain(i.domain) : null, country: country(i.country), device: device(i.device) }),
    key: (n) => ({ keyword: n.keyword, country: n.country, device: n.device }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const res = await call('serp/google/ai_mode/live/advanced', { keyword: enc(n.keyword), location_code: loc, language_code: lang, device: n.device }, 60000);
      const items = serpItems(res);
      const ai = items.find((i) => i && i.type === 'ai_overview') || null;
      return { keyword: n.keyword, country: n.country, device: n.device, has: !!ai, text: ai ? mdToText(ai.markdown || aiText(ai)) : '', sources: ai ? aiSources(ai) : [] };
    },
    post(d, n) {
      d.domain = n.domain;
      if (n.domain) {
        const hit = d.sources.findIndex((s) => sameSite(s.domain, n.domain));
        d.cited = d.has ? (hit >= 0 ? hit + 1 : 0) : null;
      }
      return d;
    },
  },

  'ai-visibility-checker': {
    units: 3, ttl: DAY,
    validate(i) {
      const brand = str(i.brand).replace(/\s+/g, ' ').trim();
      if (brand.length < 2 || brand.length > 60) throw new UserError('Enter your brand name (2 to 60 characters).');
      const prompt = str(i.prompt).replace(/\s+/g, ' ').trim();
      if (prompt.length < 8) throw new UserError('Enter a question your buyers ask AI, for example: best CRM for small law firms.');
      if (prompt.length > 300) throw new UserError('Keep the question under 300 characters.');
      return { brand, website: str(i.website).trim() ? domain(i.website) : null, prompt, country: country(i.country) };
    },
    key: (n) => ({ prompt: n.prompt.toLowerCase(), country: n.country }),
    async run(n, call) {
      const iso = COUNTRIES[n.country][2];
      const P = [
        ['chatgpt', 'ChatGPT', 'ai_optimization/chat_gpt/llm_responses/live', { user_prompt: n.prompt, model_name: 'gpt-4.1-mini', web_search: true, web_search_country_iso_code: iso, max_output_tokens: 900, temperature: 0.3 }],
        ['gemini', 'Gemini', 'ai_optimization/gemini/llm_responses/live', { user_prompt: n.prompt, model_name: 'gemini-2.5-flash', web_search: true, max_output_tokens: 1200 }],
        ['perplexity', 'Perplexity', 'ai_optimization/perplexity/llm_responses/live', { user_prompt: n.prompt, model_name: 'sonar', max_output_tokens: 900 }],
      ];
      const platforms = await Promise.all(P.map(async ([id, name, path, task]) => {
        try {
          const x = llmText(await call(path, task, 80000));
          if (!x.text) return { id, name, ok: false };
          return { id, name, ok: true, text: clip(x.text, 6000), sources: x.sources.slice(0, 20) };
        } catch (e) { if (isFatal(e)) throw e; return { id, name, ok: false }; }
      }));
      if (!platforms.some((p) => p.ok)) throw new ApiError('allfailed', 'No assistant answered');
      return { prompt: n.prompt, country: n.country, platforms };
    },
    post(d, n) {
      const terms = brandTerms(n.brand, n.website);
      const counts = {};
      d.brand = n.brand; d.website = n.website;
      d.platforms.forEach((p) => {
        if (!p.ok) return;
        p.mentioned = mentions(p.text, terms);
        p.cited = n.website ? p.sources.some((s) => s.cited && sameSite(s.domain, n.website)) : null;
        p.read = n.website ? p.sources.some((s) => sameSite(s.domain, n.website)) : null;
        p.sources.forEach((s) => { if (s.domain && !(n.website && sameSite(s.domain, n.website))) counts[s.domain] = (counts[s.domain] || 0) + 1; });
      });
      d.answered = d.platforms.filter((p) => p.ok).length;
      d.visible = d.platforms.filter((p) => p.ok && (p.mentioned || p.cited)).length;
      d.top_sites = Object.keys(counts).sort((a, b) => counts[b] - counts[a]).slice(0, 10).map((k) => ({ domain: k, count: counts[k] }));
      return d;
    },
  },

  'youtube-keyword-tool': {
    units: 2, ttl: 7 * DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), country: country(i.country) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const variants = uniq([n.keyword, /^how to /.test(n.keyword) ? n.keyword + ' for beginners' : 'how to ' + n.keyword, n.keyword + ' for', 'best ' + n.keyword]);
      const [acs, yt] = await Promise.all([
        Promise.all(variants.map((v) => call('serp/google/autocomplete/live/advanced', { keyword: enc(v), location_code: loc, language_code: lang, client: 'youtube' }).catch(softFail))),
        call('serp/youtube/organic/live/advanced', { keyword: enc(n.keyword), location_code: loc, language_code: lang }).catch(softFail),
      ]);
      const ideas = [];
      const seen = new Set();
      acs.forEach((res) => serpItems(res).forEach((it) => {
        const s = str(it && it.suggestion).replace(/\s+/g, ' ').trim().toLowerCase();
        if (s && !seen.has(s) && s.length <= 80 && s.split(' ').length <= 10) { seen.add(s); ideas.push(s); }
      }));
      if (!seen.has(n.keyword)) ideas.unshift(n.keyword);
      const list = ideas.slice(0, 40);
      const vol = {};
      if (list.length) {
        const ov = await call('dataforseo_labs/google/keyword_overview/live', { keywords: list, location_code: loc, language_code: lang }).catch(softFail);
        ((ov[0] || {}).items || []).forEach((it) => { if (it && it.keyword) vol[str(it.keyword).toLowerCase()] = num((it.keyword_info || {}).search_volume); });
      }
      const videos = serpItems(yt).filter((i) => i && i.type === 'youtube_video').slice(0, 10).map((v) => ({
        title: clip(v.title, 140), url: str(v.url), channel: clip(v.channel_name, 80), views: num(v.views_count), published: v.publication_date || null, duration: v.duration_time || null, shorts: !!v.is_shorts,
      }));
      if (!list.length && !videos.length) return { keyword: n.keyword, country: n.country, ideas: [], videos: [] };
      return { keyword: n.keyword, country: n.country, ideas: list.map((k) => ({ k, gv: Object.prototype.hasOwnProperty.call(vol, k) ? vol[k] : null })), videos };
    },
  },

  'amazon-keyword-tool': {
    units: 1, ttl: 7 * DAY,
    validate: (i) => ({ keyword: keyword(i.keyword), country: country(i.country, AMAZON) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const res = (await call('dataforseo_labs/amazon/related_keywords/live', { keyword: n.keyword, location_code: loc, language_code: lang, depth: 2, include_seed_keyword: true, limit: 100 }))[0] || {};
      const rows = [], seen = new Set();
      (res.items || []).forEach((it) => {
        const kd = (it && it.keyword_data) || {};
        const k = str(kd.keyword).toLowerCase();
        if (!k || seen.has(k)) return;
        seen.add(k);
        rows.push({ k, v: num((kd.keyword_info || {}).search_volume), depth: num(it.depth) });
      });
      rows.sort((a, b) => (b.v || 0) - (a.v || 0));
      const sd = res.seed_keyword_data || null;
      const sinfo = sd ? (sd.keyword_info || (sd.keyword_data || {}).keyword_info || {}) : {};
      return { keyword: n.keyword, country: n.country, seed: sd ? { k: n.keyword, v: num(sinfo.search_volume) } : null, rows };
    },
  },

  'bing-keyword-tool': {
    units: 2, ttl: 7 * DAY,
    validate: (i) => ({ keyword: keyword(i.keyword, 100), country: country(i.country, BING) }),
    async run(n, call) {
      const [loc, lang] = COUNTRIES[n.country];
      const res = await call('keywords_data/bing/keywords_for_keywords/live', { keywords: [n.keyword], location_code: loc, language_code: lang, sort_by: 'search_volume' });
      const rows = [], seen = new Set();
      (res || []).forEach((r) => {
        const k = str(r && r.keyword).toLowerCase();
        if (!k || seen.has(k)) return;
        seen.add(k);
        rows.push({ k, v: num(r.search_volume), cpc: num(r.cpc), comp: compLabel(r.competition) });
      });
      rows.sort((a, b) => (b.v || 0) - (a.v || 0));
      return { keyword: n.keyword, country: n.country, rows: rows.slice(0, 300) };
    },
  },

  'plagiarism-checker': {
    units: 2, ttl: DAY,
    validate(i) {
      const text = str(i.text).replace(/\s+/g, ' ').trim();
      const count = text ? text.split(' ').length : 0;
      if (count < 25) throw new UserError('Paste at least 25 words.');
      if (count > 1500 || text.length > 12000) throw new UserError('Paste up to 1,500 words at a time.');
      return { text, exclude: str(i.exclude).trim() ? domain(i.exclude) : null };
    },
    key: (n) => ({ text: n.text }),
    async run(n, call) {
      const picks = pickSentences(n.text, 8);
      if (!picks.length) throw new UserError('We could not find full sentences to check. Paste complete sentences.');
      const rows = await Promise.all(picks.map(async (s) => {
        try {
          const res = await call('serp/google/organic/live/regular', { keyword: '"' + enc(s) + '"', location_code: 2840, language_code: 'en', depth: 10 });
          const r0 = res[0] || {};
          return { s, spell: (r0.spell && r0.spell.type) || null, hits: organic(r0.items || [], 10).map((o) => ({ url: o.url, title: o.title, domain: o.domain, desc: o.desc })) };
        } catch (e) { if (isFatal(e)) throw e; return { s, error: true, hits: [] }; }
      }));
      if (rows.every((r) => r.error)) throw new ApiError('allfailed', 'All sentence checks failed');
      return { rows };
    },
    post(d, n) {
      const agg = {};
      const rows = d.rows.map((r) => {
        const fallback = r.spell && /no_results|showing_results|including_results/.test(r.spell);
        const matches = (r.error || fallback) ? [] : r.hits.filter((h) => !(n.exclude && sameSite(h.domain, n.exclude)) && phraseHit(r.s, h.title + ' ' + h.desc)).map((h) => ({ url: h.url, title: h.title, domain: h.domain }));
        matches.forEach((m) => { const k = m.url; agg[k] = agg[k] || { url: m.url, title: m.title, domain: m.domain, count: 0 }; agg[k].count++; });
        return { s: r.s, error: !!r.error, matches: matches.slice(0, 5) };
      });
      const checked = rows.filter((r) => !r.error).length;
      const found = rows.filter((r) => r.matches.length).length;
      return { checked, found, percent: checked ? Math.round((found / checked) * 100) : 0, rows, sources: Object.keys(agg).map((k) => agg[k]).sort((a, b) => b.count - a.count).slice(0, 10), exclude: n.exclude };
    },
  },
};

// ---------- budget counters (Cache API, per data center) ----------
async function readCount(cache, req) {
  try { const r = await cache.match(req); return r ? (parseInt(await r.text(), 10) || 0) : 0; } catch (e) { return 0; }
}
function writeCount(cache, req, n) {
  return cache.put(req, new Response(String(n), { headers: { 'content-type': 'text/plain', 'cache-control': 'max-age=90000' } }));
}

export async function onRequest(context) {
  const { request, env } = context;
  const later = (p) => { try { if (context.waitUntil) context.waitUntil(p.catch(() => {})); } catch (e) { /* ignore */ } };
  if (request.method !== 'POST') return json({ ok: false, error: 'Use POST.' }, 405);
  const origin = request.headers.get('origin') || '';
  if (!ORIGINS.some((r) => r.test(origin))) return json({ ok: false, error: 'This endpoint only serves imisofts.com tools.' }, 403);

  let body;
  try {
    const txt = await request.text();
    if (txt.length > 40000) throw new Error('too big');
    body = JSON.parse(txt);
  } catch (e) { return json({ ok: false, error: 'Bad request.' }, 400); }
  const name = str(body && body.tool);
  const def = Object.prototype.hasOwnProperty.call(TOOLS, name) ? TOOLS[name] : null;
  if (!def) return json({ ok: false, error: 'Unknown tool.' }, 400);

  let n;
  try { n = def.validate((body && typeof body.input === 'object' && body.input) || {}); }
  catch (e) { return json({ ok: false, error: e instanceof UserError ? e.message : 'Please check what you entered.' }, 400); }

  if (!env || !env.DATAFORSEO_LOGIN || !env.DATAFORSEO_PASSWORD) {
    return json({ ok: false, error: 'This tool is being switched on. Please try again a little later.', code: 'setup' }, 503);
  }

  let cache = null;
  try { cache = await caches.open(CACHE_NAME); } catch (e) { cache = null; }
  const hash = await sha256hex(V + '|' + name + '|' + JSON.stringify(def.key ? def.key(n) : n));
  const cacheReq = new Request(KEY_BASE + 'r/' + name + '/' + hash);
  const respond = (data, cached, left, extra) => json({ ok: true, tool: name, cached, left, data: def.post ? def.post(data, n) : data }, 200, extra);

  if (cache) {
    try {
      const hit = await cache.match(cacheReq);
      if (hit) return respond(await hit.json(), true, null);
    } catch (e) { /* treat as a miss */ }
  }

  const units = def.unitsFor ? def.unitsFor(n) : def.units;
  const day = new Date().toISOString().slice(0, 10);
  const ip = request.headers.get('cf-connecting-ip') || request.headers.get('x-real-ip') || 'unknown';
  const visitorReq = new Request(KEY_BASE + 'v/' + (await sha256hex(day + '|' + ip)));
  const coloReq = new Request(KEY_BASE + 'c/' + day);
  let usedVisitor = 0, usedColo = 0;
  if (cache) {
    [usedVisitor, usedColo] = await Promise.all([readCount(cache, visitorReq), readCount(cache, coloReq)]);
    if (usedVisitor + units > VISITOR_UNITS) {
      return json({ ok: false, error: "You've used today's free data checks. They reset at 00:00 UTC. Results you already ran stay free to open again.", code: 'visitor_limit' }, 429);
    }
    if (usedColo + units > COLO_UNITS) {
      return json({ ok: false, error: 'Our free data checks are very busy today. Please try again tomorrow.', code: 'busy' }, 429);
    }
  }

  let cost = 0;
  const call = async (path, task, ms) => { const r = await dfs(env, path, task, ms); cost += r.cost; return r.result; };
  const count = () => { if (cache) later(Promise.all([writeCount(cache, visitorReq, usedVisitor + units), writeCount(cache, coloReq, usedColo + units)])); };

  let data;
  try {
    data = await def.run(n, call);
  } catch (e) {
    if (cost > 0) count();
    if (e instanceof UserError) return json({ ok: false, error: e.message }, 400);
    const [status, msg] = apiError(e);
    return json({ ok: false, error: msg, code: e && e.code != null ? String(e.code) : 'error' }, status, { 'x-data-cost': cost.toFixed(4) });
  }

  if (cache) later(cache.put(cacheReq, new Response(JSON.stringify(data), { headers: { 'content-type': 'application/json', 'cache-control': 'max-age=' + def.ttl } })));
  count();
  return respond(data, false, Math.max(0, VISITOR_UNITS - usedVisitor - units), { 'x-data-cost': cost.toFixed(4) });
}
