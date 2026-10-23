/*
 * SPF, DKIM & DMARC Checker by imisofts
 * DNS propagation checks. Asks six public DNS resolvers for one record at the same time, over
 * DNS-over-HTTPS, and compares their answers. Nothing is stored or sent anywhere else.
 *
 * The six resolvers all allow these requests from any origin, so no browser permission is needed:
 *   JSON API (application/dns-json): Google Public DNS, Cloudflare, AliDNS, DNS.SB
 *   RFC 8484 wire format (application/dns-message): Control D, DNS4EU
 *
 * Notes on the DNS rules used below:
 *  - A resolver keeps a record for its TTL, so a changed record shows its old value there until the
 *    cached copy expires (RFC 1035). The TTL a resolver returns is the time left on its copy.
 *  - A "not found" answer is cached too, for the TTL of the SOA record in the authority section
 *    (RFC 2308). Looking a name up before it exists can therefore hide it for that long.
 *  - A CNAME cannot sit at the zone apex or next to other records (RFC 1034 section 3.6.2).
 */
(function (root) {
  'use strict';

  const TYPE_CODES = { A: 1, NS: 2, CNAME: 5, SOA: 6, MX: 15, TXT: 16, AAAA: 28 };
  const TYPE_NAMES = { 1: 'A', 2: 'NS', 5: 'CNAME', 6: 'SOA', 15: 'MX', 16: 'TXT', 28: 'AAAA' };
  const RECORD_TYPES = ['A', 'CNAME', 'TXT', 'MX', 'NS', 'AAAA'];
  const TIMEOUT_MS = 8000;
  const RCODES = { 1: 'FORMERR', 2: 'SERVFAIL', 4: 'NOTIMP', 5: 'REFUSED' };

  const PROVIDERS = [
    { id: 'google', name: 'Google', full: 'Google Public DNS', kind: 'json', base: 'https://dns.google/resolve' },
    { id: 'cloudflare', name: 'Cloudflare', full: 'Cloudflare 1.1.1.1', kind: 'json', base: 'https://cloudflare-dns.com/dns-query', accept: 'application/dns-json' },
    { id: 'alidns', name: 'AliDNS', full: 'AliDNS (Alibaba Cloud, China)', kind: 'json', base: 'https://dns.alidns.com/resolve', numericType: true },
    { id: 'dnssb', name: 'DNS.SB', full: 'DNS.SB', kind: 'json', base: 'https://doh.dns.sb/dns-query', accept: 'application/dns-json' },
    { id: 'controld', name: 'Control D', full: 'Control D (unfiltered)', kind: 'wire', base: 'https://freedns.controld.com/p0' },
    { id: 'dns4eu', name: 'DNS4EU', full: 'DNS4EU (unfiltered, European Union)', kind: 'wire', base: 'https://unfiltered.joindns4.eu/dns-query' }
  ];

  // Name servers of common DNS hosts. Used to tell the user where a record has to be added.
  const DNS_HOSTS = [
    [/\.ns\.cloudflare\.com$/, 'Cloudflare'],
    [/(^|\.)domaincontrol\.com$/, 'GoDaddy'],
    [/(^|\.)registrar-servers\.com$/, 'Namecheap'],
    [/(^|\.)namecheaphosting\.com$/, 'Namecheap hosting'],
    [/(^|\.)awsdns-\d+\.(com|net|org|co\.uk)$/, 'Amazon Route 53'],
    [/(^|\.)azure-dns\.(com|net|org|info)$/, 'Microsoft Azure DNS'],
    [/^ns-cloud-[a-z]\d+\.googledomains\.com$/, 'Google Cloud DNS'],
    [/(^|\.)googledomains\.com$/, 'Google Domains (Squarespace)'],
    [/(^|\.)squarespacedns\.com$/, 'Squarespace'],
    [/(^|\.)digitalocean\.com$/, 'DigitalOcean'],
    [/(^|\.)linode\.com$/, 'Linode (Akamai)'],
    [/(^|\.)vultr\.com$/, 'Vultr'],
    [/(^|\.)(hetzner\.com|hetzner\.de|your-server\.de|first-ns\.de|second-ns\.de|second-ns\.com)$/, 'Hetzner'],
    [/(^|\.)ovh\.(net|ca)$/, 'OVHcloud'],
    [/(^|\.)ui-dns\.(com|org|de|biz)$/, 'IONOS'],
    [/(^|\.)porkbun\.com$/, 'Porkbun'],
    [/(^|\.)(dns-parking\.com|hostinger\.(com|io))$/, 'Hostinger'],
    [/(^|\.)bluehost\.com$/, 'Bluehost'],
    [/(^|\.)hostgator\.com$/, 'HostGator'],
    [/(^|\.)siteground\.net$/, 'SiteGround'],
    [/(^|\.)wixdns\.net$/, 'Wix'],
    [/(^|\.)name\.com$/, 'Name.com'],
    [/(^|\.)dynadot\.com$/, 'Dynadot'],
    [/(^|\.)gandi\.net$/, 'Gandi'],
    [/(^|\.)hover\.com$/, 'Hover'],
    [/(^|\.)(namesilo\.com|dnsowl\.com)$/, 'NameSilo'],
    [/(^|\.)dnsimple\.com$/, 'DNSimple'],
    [/(^|\.)nsone\.net$/, 'NS1'],
    [/(^|\.)dnsmadeeasy\.com$/, 'DNS Made Easy'],
    [/(^|\.)ultradns\.(com|net|org|biz|info|co\.uk)$/, 'UltraDNS'],
    [/(^|\.)akam\.net$/, 'Akamai'],
    [/(^|\.)vercel-dns\.com$/, 'Vercel'],
    [/(^|\.)cloudns\.net$/, 'ClouDNS'],
    [/(^|\.)he\.net$/, 'Hurricane Electric'],
    [/(^|\.)worldnic\.com$/, 'Network Solutions'],
    [/(^|\.)zoho\.com$/, 'Zoho'],
    [/(^|\.)secureserver\.net$/, 'GoDaddy'],
    [/(^|\.)123-reg\.co\.uk$/, '123 Reg'],
    [/(^|\.)inwx\.(de|eu|net)$/, 'INWX'],
    [/(^|\.)eurodns\.com$/, 'EuroDNS'],
    [/(^|\.)netlify\.com$/, 'Netlify']
  ];

  // Cloudflare's published ranges (cloudflare.com/ips-v4 and /ips-v6, read 21 Oct 2026).
  const CF_V4 = ['173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22', '141.101.64.0/18',
    '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22', '198.41.128.0/17',
    '162.158.0.0/15', '104.16.0.0/13', '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22'];
  const CF_V6 = ['2400:cb00::/32', '2606:4700::/32', '2803:f800::/32', '2405:b500::/32', '2405:8100::/32',
    '2a06:98c0::/29', '2c0f:f248::/32'];

  /* ---------- names and values ---------- */

  // A record name as typed or pasted: a full name such as test.acme.com, _dmarc.acme.com or
  // google._domainkey.acme.com. A URL or an email address is reduced to its host name.
  function cleanName(input) {
    let s = String(input || '').trim().toLowerCase();
    if (!s) return '';
    s = s.replace(/^[\s"'\u2018-\u201f<(]+|[\s"'\u2018-\u201f>),;]+$/g, '');
    s = s.replace(/^[a-z][a-z0-9+.-]*:\/\//, '').replace(/^mailto:/, '');
    s = s.split(/[/?#\s]/)[0];
    if (s.includes('@')) s = s.split('@').pop();
    s = s.replace(/:\d+$/, '').replace(/\.+$/, '');
    if (/[\u0080-\uffff]/.test(s)) {
      try { s = new URL('http://' + s).hostname; } catch (e) { return ''; }
    }
    if (s.length > 253 || !/^[a-z0-9_*-]+(\.[a-z0-9_-]+)+$/.test(s)) return '';
    const labels = s.split('.');
    if (labels.some(l => !l || l.length > 63)) return '';
    if (labels.slice(1).some(l => l.includes('*'))) return '';
    if (/^\d+$/.test(labels[labels.length - 1])) return '';
    return s;
  }

  function host(s) { return String(s || '').trim().toLowerCase().replace(/^[a-z][a-z0-9+.-]*:\/\//, '').split(/[/?#\s]/)[0].replace(/\.+$/, ''); }

  function isIPv4(s) {
    const m = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/.exec(String(s || '').trim());
    return !!m && m.slice(1).every(x => +x <= 255 && String(+x) === x.replace(/^0+(?=\d)/, ''));
  }

  function normIPv4(s) { return isIPv4(s) ? String(s).trim().split('.').map(n => String(+n)).join('.') : String(s || '').trim(); }

  // IPv6 in its RFC 5952 form, so answers written differently still compare equal. '' if invalid.
  function normIPv6(s) {
    let t = String(s || '').trim().toLowerCase();
    if (!t || !/^[0-9a-f:.]+$/.test(t)) return '';
    let tail = [];
    const v4 = /(\d+\.\d+\.\d+\.\d+)$/.exec(t);
    if (v4) {
      if (!isIPv4(v4[1])) return '';
      const p = v4[1].split('.').map(Number);
      tail = [((p[0] << 8) | p[1]).toString(16), ((p[2] << 8) | p[3]).toString(16)];
      t = t.slice(0, -v4[1].length);
      if (t.endsWith(':') && !t.endsWith('::')) t = t.slice(0, -1);
    }
    const halves = t.split('::');
    if (halves.length > 2) return '';
    const head = halves[0] ? halves[0].split(':') : [];
    const rest = halves.length === 2 && halves[1] ? halves[1].split(':') : [];
    let groups;
    if (halves.length === 2) {
      const fill = 8 - head.length - rest.length - tail.length;
      if (fill < 1) return '';
      groups = head.concat(new Array(fill).fill('0'), rest, tail);
    } else {
      groups = head.concat(tail);
    }
    if (groups.length !== 8 || groups.some(g => !/^[0-9a-f]{1,4}$/.test(g))) return '';
    groups = groups.map(g => parseInt(g, 16).toString(16));
    let best = -1, bestLen = 1;
    for (let i = 0; i < 8;) {
      if (groups[i] !== '0') { i++; continue; }
      let j = i; while (j < 8 && groups[j] === '0') j++;
      if (j - i > bestLen) { best = i; bestLen = j - i; }
      i = j;
    }
    if (best < 0) return groups.join(':');
    return groups.slice(0, best).join(':') + '::' + groups.slice(best + bestLen).join(':');
  }

  // TXT data as the JSON resolvers write it: Google joins the strings, the others quote each one.
  function joinTxt(data) {
    const d = String(data || '').trim();
    if (!d.startsWith('"')) return d;
    const parts = d.match(/"((?:[^"\\]|\\.)*)"/g);
    if (!parts) return d;
    return parts.map(p => p.slice(1, -1).replace(/\\(\d{3}|.)/g, (m, x) => (x.length === 3 ? String.fromCharCode(+x) : x))).join('');
  }

  // A typed TXT value: drop outer quotes, join "split" "strings", and treat every run of spaces as one.
  function normTxt(s) {
    let t = String(s || '').trim();
    if (/^"[\s\S]*"$/.test(t)) t = joinTxt(t);
    return t.replace(/\s+/g, ' ').trim();
  }

  // One record as a comparable value (value) and as text to show (show).
  function normRecord(type, data, txtParts) {
    if (type === 'A') { const v = String(data || '').trim(); return { value: v, show: v }; }
    if (type === 'AAAA') { const v = normIPv6(data) || String(data || '').trim().toLowerCase(); return { value: v, show: v }; }
    if (type === 'CNAME' || type === 'NS') { const v = host(data); return { value: v, show: v }; }
    if (type === 'MX') {
      const m = /^\s*(\d+)\s+(\S+)\s*$/.exec(String(data || ''));
      if (!m) { const v = host(data); return { value: v, show: v, pref: null, host: v }; }
      const h = host(m[2]);
      return { value: (+m[1]) + ' ' + h, show: (+m[1]) + ' ' + (h || '.'), pref: +m[1], host: h };
    }
    if (type === 'TXT') {
      const v = txtParts ? txtParts.join('') : joinTxt(data);
      return { value: v, show: v, parts: txtParts ? txtParts.length : (String(data || '').match(/"((?:[^"\\]|\\.)*)"/g) || [0]).length };
    }
    if (type === 'SOA') {
      const p = String(data || '').trim().split(/\s+/);
      return { value: String(data || '').trim(), show: String(data || '').trim(), mname: host(p[0]), minimum: +p[6] || 0 };
    }
    return { value: String(data || ''), show: String(data || '') };
  }

  // The expected value typed by the user, split into the parts that must all be present.
  // TXT: by default the typed text only has to appear in a record; with whole, it has to be the whole record.
  function parseExpected(type, input, whole) {
    const raw = String(input || '').trim();
    if (!raw) return null;
    if (type === 'TXT') { const t = normTxt(raw); return t ? { type, raw, parts: [t], whole: !!whole } : null; }
    const items = raw.split(/[\s,;]+/).filter(Boolean);
    if (type === 'A') return { type, raw, parts: items.map(normIPv4), invalid: items.filter(x => !isIPv4(x)) };
    if (type === 'AAAA') return { type, raw, parts: items.map(x => normIPv6(x) || x.toLowerCase()), invalid: items.filter(x => !normIPv6(x)) };
    if (type === 'CNAME') return { type, raw, parts: [host(items[0])] };
    if (type === 'NS') return { type, raw, parts: items.map(host) };
    if (type === 'MX') {
      const parts = [];
      for (let i = 0; i < items.length; i++) {
        if (/^\d+$/.test(items[i]) && items[i + 1]) { parts.push({ pref: +items[i], host: host(items[i + 1]) }); i++; }
        else parts.push({ pref: null, host: host(items[i]) });
      }
      return { type, raw, parts };
    }
    return { type, raw, parts: items };
  }

  // A TXT value compared as a whole: runs of spaces, spaces around ";" and a final ";" do not count
  // (DKIM and DMARC ignore them, RFC 6376 and RFC 7489; SPF has no ";").
  function txtKey(s) { return String(s || '').replace(/\s*;\s*/g, ';').replace(/;+$/, '').replace(/\s+/g, ' ').trim(); }

  function matches(type, expected, records) {
    if (!expected || !records.length) return false;
    const values = records.map(r => r.value);
    if (type === 'TXT') {
      const want = expected.parts[0];
      if (expected.whole) return records.some(r => txtKey(r.value) === txtKey(want));
      return records.some(r => r.value.replace(/\s+/g, ' ').includes(want));
    }
    if (type === 'CNAME') return values.includes(expected.parts[0]);
    if (type === 'MX') return expected.parts.every(p => records.some(r => r.host === p.host && (p.pref === null || r.pref === p.pref)));
    return expected.parts.every(p => values.includes(p));
  }

  /* ---------- IP ranges ---------- */

  function v4int(ip) { return ip.split('.').reduce((n, x) => ((n << 8) | (+x)) >>> 0, 0); }
  function inV4(ip, cidr) {
    const [base, bits] = cidr.split('/'); const b = +bits;
    const mask = b === 0 ? 0 : (0xffffffff << (32 - b)) >>> 0;
    return ((v4int(ip) & mask) >>> 0) === ((v4int(base) & mask) >>> 0);
  }
  function v6groups(ip) {
    const n = normIPv6(ip); if (!n) return null;
    const halves = n.split('::');
    const head = halves[0] ? halves[0].split(':') : [];
    const tail = halves.length === 2 && halves[1] ? halves[1].split(':') : [];
    const fill = halves.length === 2 ? new Array(8 - head.length - tail.length).fill('0') : [];
    return head.concat(fill, tail).map(g => parseInt(g, 16));
  }
  function inV6(ip, cidr) {
    const g = v6groups(ip); const [base, bits] = cidr.split('/'); const bg = v6groups(base);
    if (!g || !bg) return false;
    let left = +bits;
    for (let i = 0; i < 8 && left > 0; i++) {
      const take = Math.min(16, left);
      const mask = (0xffff << (16 - take)) & 0xffff;
      if ((g[i] & mask) !== (bg[i] & mask)) return false;
      left -= take;
    }
    return true;
  }
  function isCloudflareIP(ip) {
    if (isIPv4(ip)) return CF_V4.some(c => inV4(ip, c));
    return normIPv6(ip) ? CF_V6.some(c => inV6(ip, c)) : false;
  }

  /* ---------- DNS wire format (RFC 1035, RFC 8484) ---------- */

  function wireQuery(name, type) {
    const b = [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1];       // id 0, recursion desired, 1 question, 1 additional (EDNS)
    for (const label of name.split('.')) {
      if (!label) continue;
      b.push(label.length);
      for (let i = 0; i < label.length; i++) b.push(label.charCodeAt(i) & 0x7f);
    }
    b.push(0, TYPE_CODES[type] >> 8, TYPE_CODES[type] & 255, 0, 1);
    b.push(0, 0, 41, 16, 0, 0, 0, 0, 0, 0, 0);            // OPT: 4096-byte payload, no DNSSEC records
    let s = '';
    for (const x of b) s += String.fromCharCode(x);
    return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  function parseWire(buf) {
    const len = buf.length;
    if (len < 12) throw new Error('short DNS answer');
    const u16 = o => { if (o + 2 > len) throw new Error('bad DNS answer'); return (buf[o] << 8) | buf[o + 1]; };
    const u32 = o => { if (o + 4 > len) throw new Error('bad DNS answer'); return ((buf[o] << 24) | (buf[o + 1] << 16) | (buf[o + 2] << 8) | buf[o + 3]) >>> 0; };
    function readName(o) {
      const labels = []; let pos = o; let next = -1; let jumps = 0;
      for (;;) {
        if (pos >= len) throw new Error('bad DNS name');
        const l = buf[pos];
        if (l === 0) { pos++; break; }
        if ((l & 0xc0) === 0xc0) {
          if (next < 0) next = pos + 2;
          pos = ((l & 0x3f) << 8) | buf[pos + 1];
          if (++jumps > 64) throw new Error('DNS name loop');
          continue;
        }
        if (l & 0xc0) throw new Error('bad DNS label');
        if (pos + 1 + l > len) throw new Error('bad DNS name');
        let s = '';
        for (let i = pos + 1; i < pos + 1 + l; i++) s += String.fromCharCode(buf[i]);
        labels.push(s); pos += 1 + l;
      }
      return { name: labels.join('.'), next: next >= 0 ? next : pos };
    }
    const rcode = buf[3] & 0x0f;
    const counts = [u16(4), u16(6), u16(8), u16(10)];
    let off = 12;
    for (let i = 0; i < counts[0]; i++) off = readName(off).next + 4;
    function rr() {
      const nm = readName(off); const p = nm.next;
      const type = u16(p), ttl = u32(p + 4), rdlen = u16(p + 8), rd = p + 10;
      if (rd + rdlen > len) throw new Error('bad DNS record');
      const t = TYPE_NAMES[type];
      const out = { name: nm.name, type: t || type, ttl };
      if (t === 'A' && rdlen === 4) out.data = [buf[rd], buf[rd + 1], buf[rd + 2], buf[rd + 3]].join('.');
      else if (t === 'AAAA' && rdlen === 16) {
        const g = []; for (let i = 0; i < 16; i += 2) g.push(((buf[rd + i] << 8) | buf[rd + i + 1]).toString(16));
        out.data = g.join(':');
      } else if (t === 'CNAME' || t === 'NS') out.data = readName(rd).name + '.';
      else if (t === 'MX') out.data = u16(rd) + ' ' + readName(rd + 2).name + '.';
      else if (t === 'TXT') {
        const parts = []; let q = rd;
        while (q < rd + rdlen) {
          const l = buf[q];
          parts.push(text(buf.subarray(q + 1, Math.min(q + 1 + l, rd + rdlen))));
          q += 1 + l;
        }
        out.txt = parts;
      } else if (t === 'SOA') {
        const m = readName(rd); const r = readName(m.next); const n = r.next;
        out.data = m.name + '. ' + r.name + '. ' + [u32(n), u32(n + 4), u32(n + 8), u32(n + 12), u32(n + 16)].join(' ');
      }
      off = rd + rdlen;
      return out;
    }
    const answer = []; const authority = [];
    for (let i = 0; i < counts[1]; i++) answer.push(rr());
    for (let i = 0; i < counts[2]; i++) authority.push(rr());
    return { rcode, answer, authority };
  }

  // TXT bytes are usually ASCII; decode them as UTF-8 so other text shows as written.
  function text(bytes) {
    if (typeof TextDecoder === 'function') return new TextDecoder('utf-8').decode(bytes);
    let s = ''; for (const b of bytes) s += String.fromCharCode(b); return s;
  }

  /* ---------- asking one resolver ---------- */

  async function ask(provider, name, type, fetchImpl, timeoutMs) {
    const f = fetchImpl || fetch;
    const t0 = Date.now();
    const ctrl = typeof AbortController === 'function' ? new AbortController() : null;
    const timer = ctrl ? setTimeout(() => ctrl.abort(), timeoutMs || TIMEOUT_MS) : null;
    const res = { id: provider.id, name: provider.name, full: provider.full, ok: false, error: '', rcode: null,
      records: [], chain: [], ttl: null, negTtl: null, zone: '', ms: 0 };
    try {
      let rcode, answer, authority;
      if (provider.kind === 'json') {
        const url = provider.base + '?name=' + encodeURIComponent(name) + '&type=' + (provider.numericType ? TYPE_CODES[type] : type);
        const r = await f(url, { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined, headers: provider.accept ? { accept: provider.accept } : {} });
        if (!r.ok) throw Object.assign(new Error('HTTP ' + r.status), { code: 'http' });
        const j = await r.json();
        rcode = j.Status;
        const conv = a => ({ name: host(a.name), type: TYPE_NAMES[a.type] || a.type, ttl: a.TTL, data: a.data });
        answer = (j.Answer || []).map(conv); authority = (j.Authority || []).map(conv);
      } else {
        const r = await f(provider.base + '?dns=' + wireQuery(name, type), { cache: 'no-store', signal: ctrl ? ctrl.signal : undefined, headers: { accept: 'application/dns-message' } });
        if (!r.ok) throw Object.assign(new Error('HTTP ' + r.status), { code: 'http' });
        const w = parseWire(new Uint8Array(await r.arrayBuffer()));
        rcode = w.rcode;
        const conv = a => Object.assign({}, a, { name: host(a.name) });
        answer = w.answer.map(conv); authority = w.authority.map(conv);
      }
      res.rcode = rcode;
      if (rcode !== 0 && rcode !== 3) { res.error = RCODES[rcode] || 'RCODE ' + rcode; return res; }
      res.ok = true;
      const recs = answer.filter(a => a.type === type);
      res.records = recs.map(a => Object.assign(normRecord(type, a.data, a.txt), { ttl: a.ttl }));
      if (type !== 'CNAME') res.chain = answer.filter(a => a.type === 'CNAME').map(a => host(a.data));
      if (recs.length) res.ttl = Math.min.apply(null, recs.map(a => a.ttl));
      const soa = authority.find(a => a.type === 'SOA');
      if (soa) { res.zone = soa.name; if (!recs.length) res.negTtl = soa.ttl; }
      res.nxdomain = rcode === 3;
      return res;
    } catch (e) {
      res.error = e && e.name === 'AbortError' ? 'timeout' : (e && e.code === 'http' ? e.message : 'network');
      return res;
    } finally {
      if (timer) clearTimeout(timer);
      res.ms = Date.now() - t0;
    }
  }

  /* ---------- where the zone is hosted ---------- */

  function hostName(nsList) {
    for (const ns of nsList) for (const [re, label] of DNS_HOSTS) if (re.test(ns)) return label;
    return '';
  }

  async function findZone(name, fetchImpl) {
    const g = PROVIDERS[0];
    // Ask for the SOA of the name. A name that is a CNAME answers for its target's zone, so ask its parent instead.
    let q = name, soa = null;
    for (let i = 0; i < 4; i++) {
      soa = await ask(g, q, 'SOA', fetchImpl);
      if (!soa.ok || !soa.chain.length || q.split('.').length <= 2) break;
      q = q.split('.').slice(1).join('.');
    }
    if (!soa || !soa.ok) return { zone: '', ns: [], host: '', exists: null };
    const zone = soa.records.length ? q : soa.zone;
    if (!zone) return { zone: '', ns: [], host: '', exists: null };
    // An apex that is only a top-level domain (or a common second-level one) means the name's domain does not exist.
    const labels = zone.split('.');
    if (labels.length === 1 || (labels.length === 2 && labels[1].length === 2 && /^(co|com|net|org|gov|ac|edu|or|ne|go)$/.test(labels[0]))) {
      return { zone: '', ns: [], host: '', exists: false };
    }
    const ns = await ask(g, zone, 'NS', fetchImpl);
    const list = ns.ok ? ns.records.map(r => r.value).filter(Boolean).sort() : [];
    return { zone, ns: list, host: hostName(list), exists: true };
  }

  /* ---------- one full check ---------- */

  function signature(r) { return r.records.map(x => x.value).sort().join('\n'); }

  // Records in one stable order (MX by preference), so two providers with the same answer read the same.
  function ordered(records, type) {
    const list = (records || []).slice();
    if (type === 'MX') {
      const pref = x => (typeof x.pref === 'number' ? x.pref : 65536);
      return list.sort((a, b) => (pref(a) - pref(b)) || String(a.host || '').localeCompare(String(b.host || '')));
    }
    return list.sort((a, b) => String(a.value).localeCompare(String(b.value), 'en', { numeric: true }));
  }

  function countOf(n) { return n + ' DNS provider' + (n === 1 ? '' : 's'); }

  async function check(nameInput, type, expectedInput, opts) {
    const o = opts || {};
    const name = cleanName(nameInput);
    if (!name) return { error: 'name' };
    if (!RECORD_TYPES.includes(type)) return { error: 'type' };
    const expected = parseExpected(type, expectedInput, o.wholeTxt);
    const providers = o.providers || PROVIDERS;
    // A zone that was already looked up (the checklist shares one) is used as it is.
    const zoneLookup = o.zone !== undefined ? Promise.resolve(o.zone)
      : o.skipZone ? Promise.resolve(null) : findZone(name, o.fetch).catch(() => null);
    const [results, zone] = await Promise.all([
      Promise.all(providers.map(p => ask(p, name, type, o.fetch, o.timeoutMs))),
      zoneLookup
    ]);
    return analyse({ name, type, expected, results, zone, checkedAt: o.now || Date.now(), fetch: o.fetch, timeoutMs: o.timeoutMs, extraLookups: !o.skipExtra });
  }

  async function analyse(c) {
    const { name, type, expected, results } = c;
    const answered = results.filter(r => r.ok);
    let live = 0;
    for (const r of results) {
      if (!r.ok) r.state = 'error';
      else if (!r.records.length) r.state = 'missing';
      else if (expected) r.state = matches(type, expected, r.records) ? 'live' : 'old';
      else r.state = 'seen';
      if (r.state === 'live') live++;
    }
    // Without an expected value, the answer most resolvers give is the reference.
    const groups = [];
    for (const r of answered.filter(x => x.records.length)) {
      const sig = signature(r);
      let g = groups.find(x => x.sig === sig);
      if (!g) { g = { sig, records: r.records, providers: [] }; groups.push(g); }
      g.providers.push(r.name);
    }
    groups.sort((a, b) => b.providers.length - a.providers.length);
    if (!expected && groups.length > 1) {
      for (const r of results) if (r.state === 'seen' && signature(r) !== groups[0].sig) r.state = 'differs';
    }
    const total = results.length;
    const missing = results.filter(r => r.state === 'missing').length;
    const errors = total - answered.length;
    const n = answered.length;
    // "Live everywhere" (done) needs an answer from every provider: one that could not be asked is not counted as live.
    // SERVFAIL and similar codes are answers too: the providers reached the name servers and got an error.
    // Said when nobody answered normally and at least one got such an error, or when such errors outnumber
    // the normal answers and nobody has the record (a new domain whose name servers are not ready yet).
    const rcodeFails = results.filter(r => !r.ok && r.rcode !== null).length;
    const servfail = n === 0 ? rcodeFails > 0 : rcodeFails > n && !results.some(r => r.records.length);
    let state, headline;
    if (!n) { state = 'error'; headline = servfail ? 'DNS providers could not resolve this name' : 'No DNS provider answered. Check your connection and try again.'; }
    else if (expected) {
      if (live === total) { state = 'done'; headline = total === 1 ? 'Live on 1 DNS provider' : 'Live on all ' + countOf(total); }
      else if (live > 0) { state = 'partial'; headline = 'Live on ' + live + ' of ' + countOf(total); }
      else { state = 'none'; headline = missing === n ? 'Not found on any DNS provider yet' : 'Not live yet: 0 of ' + countOf(total); }
    } else if (missing === n) { state = 'none'; headline = 'Not found on any DNS provider'; }
    else if (groups.length === 1 && !missing && !errors) { state = 'done'; headline = total === 1 ? 'Found on 1 DNS provider' : 'All ' + countOf(total) + ' give the same answer'; }
    else if (groups.length === 1) { state = 'partial'; headline = 'Found on ' + (n - missing) + ' of ' + countOf(total); }
    else { state = 'partial'; headline = 'DNS providers give ' + groups.length + ' different answers'; }

    const out = { name, type, expected, results, groups, zone: c.zone, checkedAt: c.checkedAt, state, headline,
      live, answered: n, total, missing, errors, servfail, proxied: false, stuck: '', notes: [] };
    await addNotes(out, c);                 // a note can replace the headline with a clearer one
    if (errors && n) out.headline += ' (' + errors + (errors === 1 ? ' provider' : ' providers') + ' could not be checked)';
    return out;
  }

  // A duration as an upper bound: 140 s reads "3 min", never less than the time really left.
  function minutes(sec) {
    const s = Math.max(0, Math.ceil(sec || 0));
    if (s < 60) return s + ' s';
    const m = Math.ceil(s / 60);
    if (m < 60) return m + ' min';
    const h = Math.floor(m / 60), r = m % 60;
    return h + ' h' + (r ? ' ' + r + ' min' : '');
  }

  // Google and Cloudflare let anyone clear their copy of a name. Offered only when one of them has a stale copy.
  function flushLinks(list) {
    const links = [];
    if (list.some(r => r.id === 'google')) links.push({ label: 'Flush Google', url: 'https://dns.google/cache' });
    if (list.some(r => r.id === 'cloudflare')) links.push({ label: 'Purge Cloudflare', url: 'https://one.one.one.one/purge-cache/' });
    return links;
  }
  function flushText(links) {
    if (!links.length) return '';
    const who = links.length === 2 ? 'Google\'s and Cloudflare\'s copies' : links[0].label === 'Flush Google' ? 'Google\'s copy' : 'Cloudflare\'s copy';
    return ' You can clear ' + who + ' now.';
  }

  // Where the zone is hosted, in words: the DNS host when known, else its name servers.
  function hostText(z) {
    if (!z || !z.zone) return '';
    if (z.host) return 'DNS for ' + z.zone + ' is hosted at ' + z.host + '.';
    if (!z.ns || !z.ns.length) return '';
    return 'DNS for ' + z.zone + ' is hosted on ' + z.ns.slice(0, 2).join(' and ') + (z.ns.length > 2 ? ' (and ' + (z.ns.length - 2) + ' more)' : '') + '.';
  }

  async function addNotes(out, c) {
    const { name, type, results, zone } = out;
    const N = out.notes;
    const where = zone && zone.host ? zone.host : '';
    const nobodyHasIt = out.answered > 0 && out.missing === out.answered;
    // 1. The record cannot exist where it was looked up (only said when no provider has it).
    if (zone && zone.exists === false && nobodyHasIt) {
      N.push({ kind: 'nodomain', level: 'fail', text: 'The domain of ' + name + ' does not exist in DNS. Check the spelling, and that the domain is registered.' });
      out.headline = 'The domain does not exist in DNS';
    }
    // 1b. The providers got errors from the domain's name servers.
    if (out.servfail) {
      const codes = [...new Set(results.filter(r => !r.ok && r.rcode !== null).map(r => r.error))].join(' or ');
      N.push({ kind: 'servfail', level: 'fail', text: (out.answered ? 'Most DNS providers' : 'The DNS providers') + ' got an error (' + codes + ') for ' + name +
        '. This usually means the domain\'s name servers are not set up yet or are not answering, or its DNSSEC setup is broken. Check the name servers at your domain registrar.' });
      if (out.answered) out.headline = 'Most DNS providers could not resolve this name';
    }
    // 2. Resolvers that remember an earlier "not found".
    const neg = results.filter(r => r.state === 'missing' && r.negTtl > 0);
    const someHave = results.some(r => r.state === 'live' || r.state === 'seen' || r.state === 'differs' || r.state === 'old');
    if (neg.length && (someHave || out.expected)) {
      const longest = Math.max.apply(null, neg.map(r => r.negTtl));
      const links = flushLinks(neg);
      N.push({ kind: 'negcache', level: someHave ? 'warn' : 'info',
        text: (someHave
          ? neg.length + (neg.length === 1 ? ' provider still remembers' : ' providers still remember') + ' "not found" from an earlier lookup. '
          : 'If the record was added in the last few minutes, providers may still remember an earlier "not found". ') +
          'They check again within ' + minutes(longest) + '.' + flushText(links),
        links });
    }
    // 3. Resolvers with a different value than the one expected.
    const old = results.filter(r => r.state === 'old');
    if (old.length) {
      const longest = Math.max.apply(null, old.map(r => r.ttl || 0));
      const links = flushLinks(old);
      if (out.live === 0 && !out.errors && old.length === out.answered && out.groups.length === 1) {
        // Everyone agrees on another value: a recent change still cached, or a typo in the record or the expected value.
        N.push({ kind: 'oldvalue', level: 'warn', text: 'Every DNS provider has a different value from the one you expect.' + (longest > 0
          ? ' If you changed the record recently, they check again within ' + minutes(longest) + '.' + flushText(links) + ' If it stays the same after that, compare the value at your DNS host with the one typed here.'
          : ' Compare the value at your DNS host with the one typed here.'), links: longest > 0 ? links : [] });
      } else if (longest > 0) {
        N.push({ kind: 'oldvalue', level: 'warn', text: old.length + (old.length === 1 ? ' provider still has' : ' providers still have') +
          ' a different value cached. They check again within ' + minutes(longest) + '.' + flushText(links), links });
      }
    }
    if (!out.expected && results.some(r => r.state === 'differs')) {
      const longest = Math.max.apply(null, results.filter(r => r.records.length).map(r => r.ttl || 0));
      if (longest > 0) {
        N.push({ kind: 'differs', level: 'info', text: 'DNS providers see different answers. Big sites often answer differently by region. For your own record it usually means a recent change: ' +
          'each provider checks again when its copy expires, all within ' + minutes(longest) + '. Add the value you expect to see which ones have it.' });
      }
    }
    // 4. Not found anywhere: point at the DNS host.
    if (out.state === 'none' && nobodyHasIt) {
      N.push({ kind: 'notfound', level: 'fail', text: name + ' has no ' + type + ' record on any provider. Check the name' +
        (where ? ', and that the record was added at ' + where + ', where ' + zone.zone + ' is hosted.' : ' and that the record was saved at your DNS host.') });
    }
    // 5. Cloudflare's proxy (orange cloud) answers with its own addresses, and no CNAME at all.
    //    A name that is a real CNAME to a Cloudflare-hosted target shows the CNAME in the chain, so it is not flagged.
    if (c.extraLookups && zone && zone.host === 'Cloudflare') {
      if (type === 'CNAME' && nobodyHasIt && zone.zone !== name) {   // the root is flattened even when "DNS only" (note 6)
        const a = await ask(PROVIDERS[0], name, 'A', c.fetch, c.timeoutMs).catch(() => null);
        if (a && a.ok && !a.chain.length && a.records.length && a.records.every(r => isCloudflareIP(r.value))) {
          out.proxied = true; out.stuck = 'proxied';        // waiting will not help: no CNAME shows while the proxy is on
          N.push({ kind: 'proxied', level: 'warn', text: name + ' answers with Cloudflare addresses instead of a CNAME, so it is proxied (orange cloud). ' +
            'Tracking domains for cold email tools need "DNS only" (grey cloud): in Cloudflare, click the orange cloud on this record.' });
          out.headline = 'No CNAME visible: Cloudflare\'s proxy is on';
        }
      } else if ((type === 'A' || type === 'AAAA') && out.expected && !out.expected.parts.some(isCloudflareIP)) {
        const seen = results.filter(r => r.records.length);
        if (seen.length && seen.every(r => !r.chain.length && r.records.every(x => isCloudflareIP(x.value)))) {
          out.proxied = true; out.stuck = 'proxied';        // the expected address never shows while the proxy is on
          N.push({ kind: 'proxied', level: 'warn', text: 'Cloudflare\'s proxy (orange cloud) is on for ' + name + ', so the world sees Cloudflare\'s addresses instead of ' +
            out.expected.raw + '. That is normal for a website. If a service needs your real address, set the record to "DNS only".' });
          if (out.live === 0) out.headline = 'Cloudflare\'s proxy is on, so its addresses show instead';
        }
      }
    }
    // 6. A CNAME cannot sit at the apex.
    if (type === 'CNAME' && zone && zone.zone === name && out.state === 'none') {
      if (nobodyHasIt) { out.stuck = 'apex'; out.headline = 'A CNAME cannot be used at the root of a domain'; }
      N.push({ kind: 'apexcname', level: 'info', text: name + ' is the root of the domain, and a CNAME cannot be used there. DNS hosts offer ALIAS, ANAME or "CNAME flattening" for the root instead.' });
    }
    // 7. TXT: two SPF records break SPF.
    if (type === 'TXT') {
      const spf = (out.groups[0] ? out.groups[0].records : []).filter(r => /^v=spf1(\s|$)/i.test(r.value));
      if (spf.length > 1) N.push({ kind: 'twospf', level: 'fail', text: name + ' has ' + spf.length + ' SPF records. Receivers treat that as an error (RFC 7208): merge them into one record.' });
    }
    // 8. The expected value does not look like this record type.
    if (out.expected && out.expected.invalid && out.expected.invalid.length) {
      N.push({ kind: 'badexpected', level: 'info', text: '"' + out.expected.invalid.join(' ') + '" is not a valid ' + (type === 'A' ? 'IPv4' : 'IPv6') + ' address, so it can never match.' });
    }
    // A missing domain or Cloudflare's proxy explains a miss better than the generic notes.
    const drop = new Set();
    if (N.some(x => x.kind === 'nodomain')) { drop.add('negcache'); drop.add('notfound'); }
    if (out.servfail) { drop.add('negcache'); drop.add('notfound'); }
    if (out.proxied) { drop.add('notfound'); drop.add('negcache'); drop.add('oldvalue'); }
    if (out.stuck === 'apex') { drop.add('notfound'); drop.add('negcache'); }
    const order = ['nodomain', 'servfail', 'badexpected', 'proxied', 'apexcname', 'twospf', 'notfound', 'negcache', 'oldvalue', 'differs'];
    const kept = N.filter(x => !drop.has(x.kind)).sort((a, b) => order.indexOf(a.kind) - order.indexOf(b.kind));
    N.length = 0; kept.forEach(x => N.push(x));
  }

  /* ---------- a list of records (new domain checklist) ---------- */

  // One record per line, in any of these shapes:
  //   TXT @ v=spf1 include:_spf.google.com ~all        (type, name, value)
  //   @ TXT v=spf1 ...                                  (name, type, value)
  //   test.acme.com. 300 IN A 1.2.3.4                   (zone file)
  //   CNAME track acme.trackingdomain.com Proxied Auto  (a row copied from a DNS host's table)
  // "@" or an empty name means the domain itself; a short name is joined to the domain.
  const HEADER_WORDS = /^(type|name|host|hostname|value|content|data|target|points|to|ttl|priority|pref|proxy|status|record|records)$/i;
  const TAIL_WORDS = /^(auto|automatic|default|proxied)$/i;
  const TTL_UNITS = /^(s|secs?|seconds?|m|mins?|minutes?|h|hrs?|hours?|d|days?)$/i;
  const TTL_UNITS_LONG = /^(secs?|seconds?|mins?|minutes?|hrs?|hours?|days?)$/i;

  // DNS host tables put the TTL and the proxy status after the value: "Auto", "1 Hour", "3600", "Proxied", "DNS only".
  // TXT text is free, so only words that cannot plausibly end a TXT value are dropped there.
  function dropTail(tokens, type) {
    const t = tokens.slice();
    const txt = type === 'TXT';
    while (t.length > 1) {
      const last = t[t.length - 1], prev = t[t.length - 2];
      if (txt ? /^(auto|automatic)$/i.test(last) : TAIL_WORDS.test(last)) t.pop();
      else if (/^only$/i.test(last) && /^dns$/i.test(prev) && t.length > 2) t.splice(-2);
      else if ((txt ? TTL_UNITS_LONG : TTL_UNITS).test(last) && /^\d+$/.test(prev) && t.length > 2) t.splice(-2);
      else if (!txt && /^\d+[smhd]$/i.test(last)) t.pop();
      else if (/^\d+$/.test(last) && type !== 'MX' && (!txt || +last >= 60)) t.pop();
      else break;
    }
    return t;
  }

  function parseRecords(input, domainInput) {
    const domain = cleanName(domainInput);
    const records = [], errors = [];
    const lines = String(input || '').split(/\r?\n/);
    const underDomain = t => { const x = t.toLowerCase().replace(/\.$/, ''); return !!domain && (x === domain || x.endsWith('.' + domain)); };
    lines.forEach((line, i) => {
      const raw = line.trim();
      if (!raw || /^(#|;|\/\/)/.test(raw)) return;
      const tokens = raw.split(/\s+/);
      if (tokens.every(t => HEADER_WORDS.test(t))) return;            // a table header such as "Type Name Value TTL"
      let ti = tokens.findIndex(t => RECORD_TYPES.includes(t));
      if (ti < 0) ti = tokens.findIndex(t => RECORD_TYPES.includes(t.toUpperCase()));
      if (ti < 0) { errors.push({ line: i + 1, text: raw, msg: 'No record type (A, CNAME, TXT, MX, NS or AAAA) on this line.' }); return; }
      const type = tokens[ti].toUpperCase();
      if (tokens[ti + 1] && /^record$/i.test(tokens[ti + 1])) tokens.splice(ti + 1, 1);   // "A Record @ 1.2.3.4"
      // Type first ("TXT @ value"): the next word is the name, unless it is clearly part of the value.
      // Name first ("@ TXT value", or a zone file line): the name is the first word that is not a TTL or "IN".
      let nm, valueTokens;
      if (ti === 0) {
        const looksLikeName = t => !!t && /^(@|[a-z0-9_*-]+(\.[a-z0-9_-]+)*\.?)$/i.test(t) && !/^\d+$/.test(t) && !isIPv4(t);
        const rest = dropTail(tokens.slice(1), type);
        // "NS ns1.host.com ns2.host.com": the name servers of the domain itself, written without a name.
        // Needs the domain above; a first word ending in "." is a full name, unless every word does.
        const nsOnly = type === 'NS' && !!domain && rest.length >= 2 && rest.every(t => t.includes('.') && !underDomain(t)) &&
          (!/\.$/.test(rest[0]) || rest.every(t => /\.$/.test(t)));
        if (nsOnly) { nm = '@'; valueTokens = rest; }
        else if (tokens.length > 2 && looksLikeName(tokens[1])) { nm = tokens[1]; valueTokens = tokens.slice(2); }
        else { nm = '@'; valueTokens = tokens.slice(1); }
      } else {
        const before = tokens.slice(0, ti).filter(t => !/^\d+$/.test(t) && !/^IN$/i.test(t));
        nm = before.length ? before[0] : '@';
        valueTokens = tokens.slice(ti + 1);
      }
      if (type === 'TXT' && /^"/.test(valueTokens[0] || '') && valueTokens.join(' ').lastIndexOf('"') > 0) {
        const j = valueTokens.join(' ');                           // quoted text: whatever follows the last quote is not part of it
        valueTokens = j.slice(0, j.lastIndexOf('"') + 1).split(' ');
      } else {
        valueTokens = dropTail(valueTokens, type);
      }
      if (type === 'A' || type === 'AAAA') {
        // One address per line in DNS host tables; anything after the addresses is not part of the value.
        const ok = x => (type === 'A' ? isIPv4(x) : !!normIPv6(x));
        const ips = [];
        for (const x of valueTokens) { const v = x.replace(/,$/, ''); if (ok(v)) ips.push(v); else break; }
        if (ips.length) valueTokens = ips;
      } else if (type === 'CNAME') {
        valueTokens = valueTokens.slice(0, 1);
      } else if (type === 'MX') {
        if (valueTokens.length === 3 && /^\d+$/.test(valueTokens[2])) valueTokens.pop();
        if (valueTokens.length === 2 && /^\d+$/.test(valueTokens[1]) && !/^\d+$/.test(valueTokens[0])) valueTokens.reverse();
      }
      const rest = valueTokens.join(' ').trim();
      let full;
      if (nm === '@') full = domain;
      else if (/\.$/.test(nm)) full = cleanName(nm);
      else if (underDomain(nm)) full = cleanName(nm);
      else if (domain) full = cleanName(nm + '.' + domain);
      else full = cleanName(nm);
      if (!full) { errors.push({ line: i + 1, text: raw, msg: domain ? 'The name on this line is not valid.' : 'Add the domain above, or write the full name (for example test.acme.com).' }); return; }
      if (!rest) { errors.push({ line: i + 1, text: raw, msg: 'No value after the record type.' }); return; }
      records.push({ type, name: full, expected: type === 'TXT' ? normTxt(rest) : rest, line: i + 1 });
    });
    return { domain, records: records.slice(0, 30), errors, cut: records.length > 30 };
  }

  // Checks every record of a list. TXT values are compared as whole records, since the list holds the full values.
  async function checkList(records, opts) {
    const o = opts || {};
    const out = new Array(records.length);
    // The domain's zone is looked up once, and shared by the records inside it (for the host and proxy notes).
    const dom = cleanName(o.domain);
    const first = dom || (records[0] ? records[0].name : '');
    const zone = !o.skipZone && records.length && first ? await findZone(first, o.fetch).catch(() => null) : null;
    const under = (nm, z) => nm === z || nm.endsWith('.' + z);
    // A typed domain that does not exist has no zone, but its rows still learn that it does not exist.
    const inZone = nm => !!zone && (zone.zone ? under(nm, zone.zone) : zone.exists === false && !!dom && under(nm, dom));
    let next = 0;
    async function worker() {
      while (next < records.length) {
        const i = next++;
        const r = records[i];
        out[i] = await check(r.name, r.type, r.expected, { fetch: o.fetch, providers: o.providers, zone: inZone(r.name) ? zone : null, wholeTxt: true, now: o.now, timeoutMs: o.timeoutMs });
        if (o.onProgress) o.onProgress(i, out[i]);
      }
    }
    await Promise.all([worker(), worker(), worker()]);
    return { results: out, zone, checkedAt: o.now || Date.now() };
  }

  /* ---------- text report and links ---------- */

  function whatsmydnsUrl(name, type, expectedRaw) {
    let u = 'https://www.whatsmydns.net/#' + type + '/' + name;
    const e = String(expectedRaw || '').trim();
    if (e && type !== 'TXT' && !/\s/.test(e)) u += '/' + encodeURIComponent(e);
    return u;
  }

  function stateWord(r) {
    return { live: 'LIVE', old: 'OTHER VALUE', missing: 'NOT FOUND', seen: 'ANSWER', differs: 'DIFFERENT', error: 'NO ANSWER' }[r.state] || r.state;
  }

  const REPORT_LINK = 'https://imisofts.com/spf-dkim-dmarc-checker';

  function reportText(c) {
    const lines = ['DNS propagation check: ' + c.name + ' ' + c.type + (c.expected ? ' (expected: ' + c.expected.raw + ')' : '')];
    lines.push(c.headline + ', checked ' + new Date(c.checkedAt).toLocaleString());
    lines.push('');
    for (const r of c.results) {
      const vals = ordered(r.records, c.type).map(x => x.show).join(' | ');
      let extra = '';
      if (r.state === 'missing' && r.negTtl && !c.stuck) extra = ' (checks again in ' + minutes(r.negTtl) + ')';
      else if ((r.state === 'old' || r.state === 'differs') && r.ttl && !c.stuck) extra = ' (checks again in ' + minutes(r.ttl) + ')';
      else if (r.state === 'error') extra = ' (' + r.error + ')';
      lines.push(r.full + ': ' + stateWord(r) + (vals ? ': ' + vals : '') + extra);
    }
    const z = c.zone;
    if (z && z.zone && (z.host || (z.ns && z.ns.length))) {
      lines.push('', z.host ? 'DNS for ' + z.zone + ' is hosted at ' + z.host + (z.ns.length ? ' (' + z.ns.join(', ') + ')' : '') + '.'
        : 'DNS for ' + z.zone + ' is hosted on ' + z.ns.join(', ') + '.');
    }
    for (const n of c.notes) lines.push('', 'Note: ' + n.text);
    lines.push('', 'Checked with the free SPF, DKIM & DMARC Checker by imisofts: ' + REPORT_LINK);
    return lines.join('\n');
  }

  root.ImisoftsPropagation = {
    PROVIDERS, RECORD_TYPES, TYPE_CODES, DNS_HOSTS,
    cleanName, isIPv4, normIPv4, normIPv6, joinTxt, normTxt, normRecord, parseExpected, matches,
    isCloudflareIP, wireQuery, parseWire, ask, findZone, hostName, hostText, check, analyse, ordered, minutes,
    parseRecords, checkList, whatsmydnsUrl, reportText, REPORT_LINK
  };
})(typeof self !== 'undefined' ? self : globalThis);
