/* imisofts free SEO data tools: front end for /api/tools/data (keyword, SERP, rank, backlink, traffic, AI visibility, plagiarism). */
(function () {
  'use strict';
  var root = document.querySelector('[data-dtool]');
  if (!root) return;
  var tool = root.getAttribute('data-dtool');
  var form = root.querySelector('form');
  var errEl = root.querySelector('.ft-error');
  var prog = root.querySelector('.ft-progress');
  var bar = prog ? prog.querySelector('.ft-progress-bar span') : null;
  var ptext = prog ? prog.querySelector('.ft-progress-text') : null;
  var out = root.querySelector('.ft-results');
  var btn = form ? form.querySelector('button[type=submit]') : null;
  if (!form || !out) return;

  var STEPS = {
    'keyword-generator': ['Finding keyword ideas', 'Adding search volumes', 'Scoring keyword difficulty'],
    'keyword-difficulty-checker': ['Pulling keyword data', 'Checking the top 10 results', 'Scoring difficulty'],
    'serp-checker': ['Fetching the live results page', 'Reading SERP features', 'Scoring each ranking site'],
    'keyword-rank-checker': ['Searching Google', 'Reading the top 100 results', 'Finding your pages'],
    'website-traffic-checker': ['Estimating organic traffic', 'Finding top keywords', 'Finding top pages'],
    'website-authority-checker': ['Counting backlinks', 'Counting referring domains', 'Scoring authority'],
    'backlink-checker': ['Counting backlinks', 'Loading the strongest links', 'Sorting by authority'],
    'ai-overview-tracker': ['Searching Google', 'Loading the AI Overview', 'Reading cited sources'],
    'ai-mode-tracker': ['Asking Google AI Mode', 'Reading the answer', 'Reading cited sources'],
    'ai-visibility-checker': ['Asking ChatGPT, Gemini and Perplexity', 'Waiting for the answers', 'Looking for your brand', 'Collecting cited sources'],
    'youtube-keyword-tool': ['Reading YouTube suggestions', 'Loading top videos', 'Adding search volumes'],
    'amazon-keyword-tool': ['Finding Amazon keywords', 'Adding Amazon search volumes'],
    'bing-keyword-tool': ['Finding Bing keywords', 'Adding Bing search volumes'],
    'plagiarism-checker': ['Picking sentences to check', 'Searching the web for exact matches', 'Collecting matching pages'],
  };
  var SECONDS = { 'ai-visibility-checker': 45, 'ai-mode-tracker': 20, 'keyword-rank-checker': 15, 'plagiarism-checker': 15, 'youtube-keyword-tool': 12, 'serp-checker': 10, 'ai-overview-tracker': 12 };
  var CTA = {
    seo: ['Want these keywords bringing you customers?', 'Our SEO team turns keyword data into pages that rank and convert.', '/seo-services', 'See SEO services'],
    links: ['Want stronger backlinks?', 'We earn links from real, relevant sites and fix the technical issues that hold rankings back.', '/seo-services', 'See SEO services'],
    ai: ['Want AI assistants to recommend you?', 'We help brands get mentioned and cited in ChatGPT, Gemini, Perplexity and Google AI answers.', '/ai-search-optimization', 'See AI search optimization'],
    yt: ['Want a YouTube channel that grows on autopilot?', 'We plan, script and publish videos around the searches your buyers make.', '/youtube-automation', 'See YouTube automation'],
    shop: ['Selling on Amazon or your own store?', 'We build ecommerce growth systems, from product pages to automation.', '/ecommerce', 'See ecommerce services'],
  };
  var CTA_FOR = {
    'keyword-generator': 'seo', 'keyword-difficulty-checker': 'seo', 'serp-checker': 'seo', 'keyword-rank-checker': 'seo', 'website-traffic-checker': 'seo',
    'website-authority-checker': 'links', 'backlink-checker': 'links', 'bing-keyword-tool': 'seo', 'plagiarism-checker': 'seo',
    'ai-overview-tracker': 'ai', 'ai-mode-tracker': 'ai', 'ai-visibility-checker': 'ai', 'youtube-keyword-tool': 'yt', 'amazon-keyword-tool': 'shop',
  };
  var FEATURES = {
    ai_overview: 'AI Overview', people_also_ask: 'People also ask', featured_snippet: 'Featured snippet', local_pack: 'Local pack', map: 'Map',
    top_stories: 'Top stories', video: 'Videos', short_videos: 'Short videos', images: 'Images', knowledge_graph: 'Knowledge panel',
    related_searches: 'Related searches', people_also_search: 'People also search', shopping: 'Shopping', popular_products: 'Popular products',
    paid: 'Ads', answer_box: 'Answer box', discussions_and_forums: 'Discussions and forums', perspectives: 'Perspectives', carousel: 'Carousel',
    multi_carousel: 'Carousel', twitter: 'X posts', jobs: 'Jobs', events: 'Events', recipes: 'Recipes', hotels_pack: 'Hotels', top_sights: 'Top sights',
    scholarly_articles: 'Scholarly articles', questions_and_answers: 'Questions and answers', find_results_on: 'Find results on', google_reviews: 'Reviews',
    third_party_reviews: 'Reviews', app: 'Apps', math_solver: 'Math solver', currency_box: 'Currency box', stocks_box: 'Stocks', commercial_units: 'Product listings',
  };

  // ---------- helpers ----------
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function safeUrl(u) { u = String(u || ''); return /^https?:\/\//i.test(u) ? u : '#'; }
  function isNum(n) { return typeof n === 'number' && isFinite(n); }
  function na() { return '<span class="dt-na">n/a</span>'; }
  function int(n) { return isNum(n) ? Math.round(n).toLocaleString('en-US') : na(); }
  function short(n) {
    if (!isNum(n)) return na();
    var a = Math.abs(n);
    if (a >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, '') + 'B';
    if (a >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (a >= 1e4) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
    return Math.round(n).toLocaleString('en-US');
  }
  function money(n) { return isNum(n) ? '$' + (n >= 100 ? Math.round(n).toLocaleString('en-US') : n.toFixed(2)) : na(); }
  function cap(s) { s = String(s || ''); return s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : ''; }
  function link(u, text, cls) { return '<a href="' + esc(safeUrl(u)) + '" target="_blank" rel="nofollow noopener"' + (cls ? ' class="' + cls + '"' : '') + '>' + esc(text || u) + '</a>'; }
  function urlCell(u, title) { return '<td class="ft-url">' + (title ? '<b class="dt-t">' + esc(title) + '</b>' : '') + link(u, u) + '</td>'; }
  function kdLevel(kd) { return !isNum(kd) ? -1 : kd < 15 ? 0 : kd < 30 ? 1 : kd < 50 ? 2 : kd < 70 ? 3 : kd < 85 ? 4 : 5; }
  var KD_LABEL = ['Very easy', 'Easy', 'Possible', 'Difficult', 'Hard', 'Very hard'];
  function kdPill(kd) { var l = kdLevel(kd); return l < 0 ? na() : '<span class="dt-kd k' + l + '" title="' + KD_LABEL[l] + '">' + Math.round(kd) + '</span>'; }
  function intent(s) { return s ? '<span class="dt-int i-' + esc(String(s).slice(0, 3)) + '">' + esc(cap(s)) + '</span>' : na(); }
  function feature(t) { return FEATURES[t] || cap(String(t).replace(/_/g, ' ')); }
  function stat(value, label, cls) { return '<div class="ft-stat' + (cls ? ' ' + cls : '') + '"><b>' + value + '</b><span>' + esc(label) + '</span></div>'; }
  function yes(b, yesText, noText) { return b ? '<span class="ft-pill ok">' + esc(yesText || 'Yes') + '</span>' : '<span class="ft-pill broken">' + esc(noText || 'No') + '</span>'; }
  function table(head, rows, minw) {
    return '<div class="ft-table-wrap"><table class="ft-table"' + (minw ? ' style="min-width:' + minw + 'px"' : '') + '><thead><tr>' + head.map(function (h) { return '<th>' + esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' + rows.join('') + '</tbody></table></div>';
  }
  function csvCell(v) { v = v == null ? '' : String(v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
  function download(name, head, rows) {
    var text = [head].concat(rows).map(function (r) { return r.map(csvCell).join(','); }).join('\n');
    var blob = new Blob(['﻿' + text], { type: 'text/csv;charset=utf-8' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function slug(s) { return String(s || 'results').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50) || 'results'; }
  function ctaBlock() {
    var c = CTA[CTA_FOR[tool]] || CTA.seo;
    return '<div class="dt-cta"><div><b>' + esc(c[0]) + '</b><span>' + esc(c[1]) + '</span></div><a class="dt-cta-btn" href="' + c[2] + '">' + esc(c[3]) + ' &rarr;</a></div>';
  }
  function more(text, id) {
    var long = String(text || '').length > 650;
    return '<div class="dt-answer' + (long ? '' : ' open') + '" id="' + id + '"><div class="dt-answer-in">' + esc(text) + '</div></div>' + (long ? '<button type="button" class="dt-more" data-more="' + id + '">Show the full answer</button>' : '');
  }
  function sources(list, mine, max) {
    if (!list || !list.length) return '<p class="ft-empty">No sources were listed.</p>';
    return '<ol class="dt-src">' + list.slice(0, max || 30).map(function (s) {
      var me = mine && s.domain && (s.domain === mine || s.domain.slice(-(mine.length + 1)) === '.' + mine);
      return '<li' + (me ? ' class="me"' : '') + '>' + link(s.url, s.title || s.url) + '<small>' + esc(s.domain || '') + (s.cited === false ? ' · read, not cited' : '') + (me ? ' · your site' : '') + '</small></li>';
    }).join('') + '</ol>';
  }

  // ---------- renderers ----------
  var R = {};

  R['keyword-generator'] = function (d) {
    var rows = d.rows || [];
    var qs = rows.filter(function (r) { return /^(who|what|when|where|why|how|which|is|are|can|does|do|should|will|was|did)\b/.test(r.k); });
    var h = '';
    if (d.seed) h += '<div class="ft-stats">' + stat(int(d.seed.v), 'Monthly searches for "' + d.keyword + '"') + stat(isNum(d.seed.kd) ? Math.round(d.seed.kd) + ' <small>' + KD_LABEL[kdLevel(d.seed.kd)] + '</small>' : na(), 'Keyword difficulty') + stat(money(d.seed.cpc), 'Cost per click') + stat(d.seed.intent ? esc(cap(d.seed.intent)) : na(), 'Search intent') + '</div>';
    if (!rows.length) return h + '<p class="ft-empty">No keyword ideas found for this keyword and country. Try a shorter or broader keyword.</p>';
    h += '<div class="ft-bar"><div class="ft-filters"><button type="button" class="on" data-tab="all">All ideas <span>' + rows.length + '</span></button><button type="button" data-tab="q">Questions <span>' + qs.length + '</span></button></div><button type="button" class="ft-export" data-csv>Export CSV</button></div>';
    var body = function (list) { return list.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + int(r.v) + '</td><td>' + kdPill(r.kd) + '</td><td>' + money(r.cpc) + '</td><td>' + intent(r.intent) + '</td></tr>'; }); };
    h += '<div data-pane="all">' + table(['Keyword', 'Volume', 'KD', 'CPC', 'Intent'], body(rows), 620) + '</div>';
    h += '<div data-pane="q" hidden>' + (qs.length ? table(['Question', 'Volume', 'KD', 'CPC', 'Intent'], body(qs), 620) : '<p class="ft-empty">No question keywords in this set.</p>') + '</div>';
    if (isNum(d.total) && d.total > rows.length) h += '<p class="ft-note">Showing the top ' + rows.length + ' of ' + int(d.total) + ' ideas, sorted by search volume.</p>';
    return h;
  };
  R['keyword-generator'].csv = function (d) { download('keywords-' + slug(d.keyword) + '.csv', ['Keyword', 'Volume', 'KD', 'CPC', 'Intent'], (d.rows || []).map(function (r) { return [r.k, r.v, r.kd, r.cpc, r.intent]; })); };

  R['keyword-difficulty-checker'] = function (d) {
    if (!d.found) return '<p class="ft-empty">We have no difficulty data for "' + esc(d.keyword) + '" in this country yet. Try a broader keyword or another country.</p>' + topList(d.top);
    var l = kdLevel(d.kd);
    var h = '<div class="dt-hero"><div class="dt-score k' + l + '"><b>' + (isNum(d.kd) ? Math.round(d.kd) : '?') + '</b><span>/100</span></div><div><h3>' + (l >= 0 ? KD_LABEL[l] : 'No score') + '</h3><p>' + esc(kdAdvice(l, d.rd)) + '</p></div></div>';
    h += '<div class="ft-stats">' + stat(int(d.v), 'Monthly searches') + stat(money(d.cpc), 'Cost per click') + stat(d.intent ? esc(cap(d.intent)) : na(), 'Search intent') + stat(isNum(d.rd) ? int(d.rd) : na(), 'Avg referring domains, top 10') + stat(short(d.results), 'Results in Google') + '</div>';
    if (d.trend && d.trend.length > 2) h += trendChart(d.trend);
    if (d.features && d.features.length) h += '<p class="dt-label">SERP features on this keyword</p><div class="dt-chips">' + d.features.map(function (f) { return '<span>' + esc(feature(f)) + '</span>'; }).join('') + '</div>';
    return h + topList(d.top);
  };
  function kdAdvice(l, rd) {
    var need = isNum(rd) && rd > 0 ? ' Pages in the top 10 have about ' + Math.round(rd) + ' referring domains on average.' : '';
    return ['A new page with solid content can rank here.', 'Good content and a few relevant links should be enough.', 'You will need strong content and some quality backlinks.', 'Expect to need a strong page and a solid backlink profile.', 'Only strong, well-linked sites tend to rank here.', 'Dominated by very strong sites. Target longer variations first.'][Math.max(0, l)] + need;
  }
  function topList(top) {
    if (!top || !top.length) return '';
    return '<p class="dt-label">Top 10 right now</p>' + table(['#', 'Page', 'Domain'], top.map(function (o) { return '<tr><td>' + int(o.pos) + '</td>' + urlCell(o.url, o.title) + '<td>' + esc(o.domain) + '</td></tr>'; }), 560);
  }
  function trendChart(t) {
    var max = Math.max.apply(null, t.map(function (x) { return x.v || 0; })) || 1;
    var M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '<p class="dt-label">Search volume, last ' + t.length + ' months</p><div class="dt-trend">' + t.map(function (x) {
      return '<div title="' + esc(M[x.m - 1] + ' ' + x.y + ': ' + (isNum(x.v) ? x.v.toLocaleString('en-US') : 'n/a')) + '"><i style="height:' + Math.max(4, Math.round(((x.v || 0) / max) * 100)) + '%"></i><span>' + M[x.m - 1].slice(0, 1) + '</span></div>';
    }).join('') + '</div>';
  }

  R['serp-checker'] = function (d) {
    var h = '<div class="ft-stats">' + stat(int(d.volume), 'Monthly searches') + stat(isNum(d.kd) ? kdPill(d.kd) : na(), 'Keyword difficulty') + stat(short(d.results), 'Results in Google') + stat(d.aio ? 'Yes' : 'No', 'AI Overview shown', d.aio ? 'warn' : '') + '</div>';
    if (d.features && d.features.length) h += '<p class="dt-label">SERP features</p><div class="dt-chips">' + d.features.map(function (f) { return '<span>' + esc(feature(f)) + '</span>'; }).join('') + '</div>';
    if (!d.organic || !d.organic.length) return h + '<p class="ft-empty">Google returned no organic results for this search.</p>';
    h += '<p class="dt-label">Top 10 organic results (' + esc(d.device || 'desktop') + ')</p>' + table(['#', 'Page', 'Authority'], d.organic.map(function (o) {
      return '<tr><td>' + int(o.pos) + '</td>' + urlCell(o.url, o.title) + '<td>' + (isNum(o.authority) ? '<span class="dt-auth">' + Math.round(o.authority) + '</span>' : na()) + '</td></tr>';
    }), 560);
    if (d.paa && d.paa.length) h += '<p class="dt-label">People also ask</p><ul class="dt-list">' + d.paa.map(function (q) { return '<li>' + esc(q) + '</li>'; }).join('') + '</ul>';
    if (d.related && d.related.length) h += '<p class="dt-label">Related searches</p><div class="dt-chips">' + d.related.map(function (q) { return '<span>' + esc(q) + '</span>'; }).join('') + '</div>';
    return h;
  };

  R['keyword-rank-checker'] = function (d) {
    var h = table(['Keyword', 'Position', 'Ranking page', 'Top 3 right now'], (d.rows || []).map(function (r) {
      if (r.error) return '<tr><td><b>' + esc(r.keyword) + '</b></td><td colspan="3">This keyword could not be checked. Please try again.</td></tr>';
      var pos = isNum(r.pos) ? '<span class="dt-pos' + (r.pos <= 3 ? ' top' : r.pos <= 10 ? ' p1' : '') + '">' + r.pos + '</span>' + (r.more && r.more.length ? '<small>also ' + r.more.join(', ') + '</small>' : '') : '<span class="dt-na">Not in top ' + (r.checked || 100) + '</span>';
      return '<tr><td><b>' + esc(r.keyword) + '</b></td><td>' + pos + '</td>' + (r.url ? urlCell(r.url, r.title) : '<td>' + na() + '</td>') + '<td>' + (r.top || []).map(function (t) { return '<div class="dt-mini">' + int(t.pos) + '. ' + esc(t.domain) + '</div>'; }).join('') + '</td></tr>';
    }), 680);
    return '<p class="ft-note">Rankings for <b>' + esc(d.domain) + '</b> in Google, ' + esc(d.device || 'desktop') + '. Positions count organic results only.</p>' + h;
  };

  R['website-traffic-checker'] = function (d) {
    if (!d.found) return '<p class="ft-empty">We found no organic rankings for ' + esc(d.domain) + ' in this country. New and very small sites often have no data yet. Try another country.</p>';
    var h = '<div class="ft-stats">' + stat(short(d.traffic), 'Organic visits a month (est.)') + stat(short(d.keywords), 'Organic keywords') + stat(isNum(d.value) ? '$' + short(d.value) : na(), 'Traffic value a month') + stat(short(d.paid_keywords), 'Paid keywords') + '</div>';
    var max = Math.max.apply(null, (d.positions || []).map(function (p) { return p[1]; })) || 1;
    h += '<p class="dt-label">Keywords by position</p><div class="dt-bars">' + (d.positions || []).map(function (p) { return '<div><span>' + esc(p[0]) + '</span><i><em style="width:' + Math.max(2, Math.round(p[1] / max * 100)) + '%"></em></i><b>' + int(p[1]) + '</b></div>'; }).join('') + '</div>';
    if (d.top_keywords && d.top_keywords.length) h += '<p class="dt-label">Top keywords by traffic</p>' + table(['Keyword', 'Position', 'Volume', 'Traffic', 'URL'], d.top_keywords.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + int(r.pos) + '</td><td>' + int(r.v) + '</td><td>' + int(r.etv) + '</td><td class="ft-url">' + link(r.url, r.url) + '</td></tr>'; }), 700);
    if (d.top_pages && d.top_pages.length) h += '<p class="dt-label">Top pages by traffic</p>' + table(['Page', 'Traffic', 'Keywords'], d.top_pages.map(function (r) { return '<tr><td class="ft-url">' + link(r.url, r.url) + '</td><td>' + int(r.etv) + '</td><td>' + int(r.keywords) + '</td></tr>'; }), 560);
    return h + '<p class="ft-note">Traffic is an estimate from rankings and click-through rates in Google, for the country you picked. It is not your analytics data.</p>';
  };

  function authorityBlock(d, label) {
    var s = isNum(d.score) ? Math.round(d.score) : null;
    var lvl = s == null ? -1 : s < 20 ? 0 : s < 40 ? 1 : s < 60 ? 2 : s < 80 ? 3 : 4;
    var words = ['Low', 'Fair', 'Good', 'Strong', 'Very strong'];
    var dofollow = isNum(d.backlinks) && isNum(d.nofollow) && d.backlinks > 0 ? Math.max(0, Math.round((1 - d.nofollow / d.backlinks) * 100)) + '%' : na();
    var h = '<div class="dt-hero"><div class="dt-score a' + lvl + '"><b>' + (s == null ? '?' : s) + '</b><span>/100</span></div><div><h3>' + esc(label) + ': ' + (lvl >= 0 ? words[lvl] : 'No data') + '</h3><p>Authority score from the site\'s backlink profile, on a 0 to 100 scale. It is our measure, not Moz DA or Ahrefs DR, so compare sites with the same tool.</p></div></div>';
    h += '<div class="ft-stats">' + stat(short(d.backlinks), 'Backlinks') + stat(short(d.rd), 'Referring domains') + stat(dofollow, 'Dofollow links') + stat(short(d.ips), 'Referring IPs') + stat(isNum(d.spam) ? Math.round(d.spam) + '%' : na(), 'Spam score') + '</div>';
    var lists = '';
    if (d.tlds && d.tlds.length) lists += '<div><p class="dt-label">Top referring TLDs</p>' + d.tlds.map(function (x) { return '<div class="dt-kv"><span>.' + esc(x.k) + '</span><b>' + int(x.v) + '</b></div>'; }).join('') + '</div>';
    if (d.countries && d.countries.length) lists += '<div><p class="dt-label">Top referring countries</p>' + d.countries.map(function (x) { return '<div class="dt-kv"><span>' + esc(x.k) + '</span><b>' + int(x.v) + '</b></div>'; }).join('') + '</div>';
    if (lists) h += '<div class="dt-two">' + lists + '</div>';
    return h;
  }

  R['website-authority-checker'] = function (d) {
    if (!d.found || (!isNum(d.backlinks) && !isNum(d.score))) return '<p class="ft-empty">We found no backlink data for ' + esc(d.domain) + '. New sites often have no links yet.</p>';
    return authorityBlock(d, d.domain) + (isNum(d.first_seen) || d.first_seen ? '<p class="ft-note">First backlink seen: ' + esc(String(d.first_seen).slice(0, 10)) + '.</p>' : '');
  };

  R['backlink-checker'] = function (d) {
    if (!d.found && !(d.links && d.links.length)) return '<p class="ft-empty">We found no backlinks for ' + esc(d.target) + ' yet.</p>';
    var h = authorityBlock(d, d.kind === 'page' ? 'This page' : d.target);
    var links = d.links || [];
    if (!links.length) return h + '<p class="ft-empty">No live backlinks to list.</p>';
    h += '<div class="ft-bar"><p class="dt-label" style="margin:0">Strongest backlinks, one per referring domain (' + links.length + (isNum(d.total_domains) && d.total_domains > links.length ? ' of ' + int(d.total_domains) : '') + ')</p><button type="button" class="ft-export" data-csv>Export CSV</button></div>';
    h += table(['Referring page', 'Authority', 'Anchor and target', 'Type', 'First seen'], links.map(function (b) {
      return '<tr>' + urlCell(b.from, b.title) + '<td><span class="dt-auth">' + (isNum(b.dr) ? Math.round(b.dr) : '?') + '</span></td><td class="ft-url"><b class="dt-t">' + esc(b.anchor || '(no anchor text)') + '</b>' + link(b.to, b.to) + '</td><td>' + (b.dofollow ? '<span class="ft-pill ok">Dofollow</span>' : '<span class="ft-pill blocked">Nofollow</span>') + (b.type && b.type !== 'anchor' ? '<small>' + esc(cap(b.type)) + '</small>' : '') + '</td><td>' + esc(String(b.first_seen || '').slice(0, 10)) + '</td></tr>';
    }), 860);
    return h;
  };
  R['backlink-checker'].csv = function (d) { download('backlinks-' + slug(d.target) + '.csv', ['Referring page', 'Title', 'Domain', 'Authority', 'Page score', 'Anchor', 'Target URL', 'Dofollow', 'Type', 'First seen', 'Last seen'], (d.links || []).map(function (b) { return [b.from, b.title, b.domain, b.dr, b.pr, b.anchor, b.to, b.dofollow ? 'yes' : 'no', b.type, b.first_seen, b.last_seen]; })); };

  function aiAnswer(d, what) {
    var h = '';
    if (!d.has) {
      h += '<div class="ft-callout"><b>No ' + what + ' for this search.</b> Google did not show one for "' + esc(d.keyword) + '" right now. ' + (what === 'AI Overview' ? 'AI Overviews come and go, so check again in a few days.' : 'Try a longer, question-style search.') + '</div>';
    } else {
      if (d.domain) h += d.cited ? '<div class="ft-callout good"><b>' + esc(d.domain) + ' is cited.</b> It is source number ' + d.cited + ' in the ' + what + '.</div>' : '<div class="ft-callout"><b>' + esc(d.domain) + ' is not cited</b> in this ' + what + '. The sources below are the pages Google used instead.</div>';
      h += '<p class="dt-label">The ' + what + ' answer</p>' + more(d.text || '(Empty answer)', 'dt-a1');
      h += '<p class="dt-label">Cited sources (' + (d.sources || []).length + ')</p>' + sources(d.sources, d.domain);
    }
    return h;
  }
  R['ai-overview-tracker'] = function (d) {
    var h = aiAnswer(d, 'AI Overview');
    if (d.domain) h += '<p class="ft-note">Organic position for ' + esc(d.domain) + ': ' + (isNum(d.your_pos) ? '<b>#' + d.your_pos + '</b>' : 'not in the top 10') + '.</p>';
    if (d.organic && d.organic.length) h += topList(d.organic);
    return h;
  };
  R['ai-mode-tracker'] = function (d) { return aiAnswer(d, 'AI Mode'); };

  R['ai-visibility-checker'] = function (d) {
    var ok = (d.platforms || []).filter(function (p) { return p.ok; });
    var h = '<div class="dt-hero"><div class="dt-score ' + (d.visible === ok.length && ok.length ? 'a4' : d.visible ? 'a2' : 'a0') + '"><b>' + (d.visible || 0) + '</b><span>/' + ok.length + '</span></div><div><h3>' + esc(d.brand) + (d.visible ? ' shows up in ' + d.visible + ' of ' + ok.length + ' AI assistants' : ' does not show up in these AI answers') + '</h3><p>We asked: "' + esc(d.prompt) + '"</p></div></div>';
    h += '<div class="dt-plats">' + (d.platforms || []).map(function (p, i) {
      if (!p.ok) return '<div class="dt-plat"><h4>' + esc(p.name) + '</h4><p class="ft-note">No answer this time. Run the check again later.</p></div>';
      return '<div class="dt-plat"><h4>' + esc(p.name) + '</h4><div class="dt-badges">' + yes(p.mentioned, 'Mentioned', 'Not mentioned') + (p.cited === null || p.cited === undefined ? '' : ' ' + yes(p.cited, 'Site cited', 'Site not cited')) + '</div>' + more(p.text, 'dt-p' + i) + '<details class="ft-details"><summary>Sources (' + (p.sources || []).length + ')</summary>' + sources(p.sources, d.website, 12) + '</details></div>';
    }).join('') + '</div>';
    if (d.top_sites && d.top_sites.length) h += '<p class="dt-label">Sites the AI assistants used for this question</p><div class="dt-chips">' + d.top_sites.map(function (s) { return '<span>' + esc(s.domain) + ' <b>' + s.count + '</b></span>'; }).join('') + '</div><p class="ft-note">Getting mentioned on these sites is often the fastest way into AI answers.</p>';
    return h + '<p class="ft-note">AI answers change from one run to the next. Check a few different questions your buyers ask before drawing conclusions.</p>';
  };

  R['youtube-keyword-tool'] = function (d) {
    var h = '';
    if (d.ideas && d.ideas.length) {
      h += '<div class="ft-bar"><p class="dt-label" style="margin:0">YouTube search suggestions (' + d.ideas.length + ')</p><button type="button" class="ft-export" data-csv>Export CSV</button></div>';
      h += table(['Keyword', 'Google searches a month'], d.ideas.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + int(r.gv) + '</td></tr>'; }), 420);
      h += '<p class="ft-note">YouTube does not publish search volumes, so we show Google monthly searches for the same phrase as a guide to demand.</p>';
    } else h += '<p class="ft-empty">No YouTube suggestions for this keyword. Try a shorter phrase.</p>';
    if (d.videos && d.videos.length) h += '<p class="dt-label">Top videos on YouTube for "' + esc(d.keyword) + '"</p>' + table(['Video', 'Channel', 'Views', 'Published', 'Length'], d.videos.map(function (v) { return '<tr>' + urlCell(v.url, v.title) + '<td>' + esc(v.channel) + '</td><td>' + short(v.views) + '</td><td>' + esc(v.published || '') + '</td><td>' + esc(v.duration || '') + (v.shorts ? ' <span class="ft-pill blocked">Short</span>' : '') + '</td></tr>'; }), 700);
    return h;
  };
  R['youtube-keyword-tool'].csv = function (d) { download('youtube-keywords-' + slug(d.keyword) + '.csv', ['Keyword', 'Google searches a month'], (d.ideas || []).map(function (r) { return [r.k, r.gv]; })); };

  R['amazon-keyword-tool'] = function (d) {
    var rows = d.rows || [];
    var h = d.seed ? '<div class="ft-stats">' + stat(int(d.seed.v), 'Amazon searches a month for "' + d.keyword + '"') + stat(int(rows.length), 'Related Amazon keywords') + '</div>' : '';
    if (!rows.length) return h + '<p class="ft-empty">No Amazon keywords found for this term in this marketplace. Try a broader product keyword.</p>';
    h += '<div class="ft-bar"><p class="dt-label" style="margin:0">Amazon keywords by search volume</p><button type="button" class="ft-export" data-csv>Export CSV</button></div>';
    return h + table(['Keyword', 'Amazon searches a month'], rows.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + int(r.v) + '</td></tr>'; }), 420);
  };
  R['amazon-keyword-tool'].csv = function (d) { download('amazon-keywords-' + slug(d.keyword) + '.csv', ['Keyword', 'Amazon searches a month'], (d.rows || []).map(function (r) { return [r.k, r.v]; })); };

  R['bing-keyword-tool'] = function (d) {
    var rows = d.rows || [];
    if (!rows.length) return '<p class="ft-empty">Bing returned no keyword ideas for this term. Try a broader keyword.</p>';
    var h = '<div class="ft-bar"><p class="dt-label" style="margin:0">Bing keyword ideas (' + rows.length + ')</p><button type="button" class="ft-export" data-csv>Export CSV</button></div>';
    return h + table(['Keyword', 'Bing searches a month', 'CPC', 'Competition'], rows.map(function (r) { return '<tr><td><b>' + esc(r.k) + '</b></td><td>' + int(r.v) + '</td><td>' + money(r.cpc) + '</td><td>' + (r.comp ? esc(cap(r.comp)) : na()) + '</td></tr>'; }), 560);
  };
  R['bing-keyword-tool'].csv = function (d) { download('bing-keywords-' + slug(d.keyword) + '.csv', ['Keyword', 'Bing searches a month', 'CPC', 'Competition'], (d.rows || []).map(function (r) { return [r.k, r.v, r.cpc, r.comp]; })); };

  R['plagiarism-checker'] = function (d) {
    var lvl = d.percent === 0 ? 'a4' : d.percent < 30 ? 'a2' : 'a0';
    var h = '<div class="dt-hero"><div class="dt-score ' + lvl + '"><b>' + d.percent + '%</b><span>found</span></div><div><h3>' + (d.found ? d.found + ' of ' + d.checked + ' checked sentences appear online' : 'None of the ' + d.checked + ' checked sentences appear online') + '</h3><p>We searched Google for the exact wording of ' + d.checked + ' sentences from your text' + (d.exclude ? ', ignoring ' + esc(d.exclude) : '') + '.</p></div></div>';
    h += '<div class="dt-sents">' + (d.rows || []).map(function (r) {
      return '<div class="dt-sent ' + (r.error ? 'err' : r.matches.length ? 'hit' : 'clean') + '"><p>' + esc(r.s) + '</p>' + (r.error ? '<small>Could not check this sentence.</small>' : r.matches.length ? r.matches.map(function (m) { return '<small>Found on ' + link(m.url, m.domain || m.url) + '</small>'; }).join('') : '<small>No exact match found</small>') + '</div>';
    }).join('') + '</div>';
    if (d.sources && d.sources.length) h += '<p class="dt-label">Pages with matching text</p>' + table(['Page', 'Matching sentences'], d.sources.map(function (s) { return '<tr>' + urlCell(s.url, s.title) + '<td>' + s.count + '</td></tr>'; }), 520);
    return h;
  };

  // ---------- run ----------
  var timer = null;
  function startProgress() {
    if (!prog) return;
    var steps = STEPS[tool] || ['Working'];
    var total = (SECONDS[tool] || 8) * 1000, t0 = Date.now();
    prog.hidden = false;
    clearInterval(timer);
    timer = setInterval(function () {
      var f = Math.min(0.92, (Date.now() - t0) / total);
      if (bar) bar.style.width = Math.max(4, Math.round(f * 100)) + '%';
      if (ptext) ptext.textContent = steps[Math.min(steps.length - 1, Math.floor(f * steps.length / 0.92))] + '...';
    }, 250);
  }
  function stopProgress() { clearInterval(timer); if (bar) bar.style.width = '100%'; if (prog) setTimeout(function () { prog.hidden = true; if (bar) bar.style.width = '2%'; }, 250); }
  function showError(msg) { if (!errEl) return; errEl.textContent = msg; errEl.hidden = false; }
  function track(name, extra) { try { if (window.gtag) window.gtag('event', name, Object.assign({ tool: tool, page: location.pathname }, extra || {})); } catch (e) { /* ignore */ } }

  function gather() {
    var input = {};
    [].forEach.call(form.elements, function (el) {
      if (!el.name || el.disabled) return;
      input[el.name] = el.type === 'checkbox' ? el.checked : el.value;
    });
    return input;
  }

  var last = null;
  function render(d, j) {
    var fn = R[tool];
    var h = fn ? fn(d) : '<p class="ft-empty">No renderer.</p>';
    if (isNum(j.left) && j.left <= 5) h += '<p class="ft-note">You have ' + j.left + ' free data credits left today.</p>';
    out.innerHTML = h + ctaBlock();
    out.hidden = false;
    last = d;
  }

  out.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('button') : null;
    if (!t) return;
    if (t.hasAttribute('data-csv') && last && R[tool].csv) { R[tool].csv(last); track('free_tool_export'); }
    if (t.hasAttribute('data-tab')) {
      [].forEach.call(out.querySelectorAll('[data-tab]'), function (b) { b.classList.toggle('on', b === t); });
      [].forEach.call(out.querySelectorAll('[data-pane]'), function (p) { p.hidden = p.getAttribute('data-pane') !== t.getAttribute('data-tab'); });
    }
    if (t.hasAttribute('data-more')) {
      var box = document.getElementById(t.getAttribute('data-more'));
      if (box) { var open = box.classList.toggle('open'); t.textContent = open ? 'Show less' : 'Show the full answer'; }
    }
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (btn && btn.disabled) return;
    if (errEl) errEl.hidden = true;
    out.hidden = true; out.innerHTML = '';
    if (btn) btn.disabled = true;
    startProgress();
    track('free_tool_run');
    fetch('/api/tools/data', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ tool: tool, input: gather() }) })
      .then(function (r) { return r.json().catch(function () { return { ok: false, error: 'The server sent an unexpected answer. Please try again.' }; }); })
      .then(function (j) {
        stopProgress();
        if (btn) btn.disabled = false;
        if (!j || !j.ok) { showError((j && j.error) || 'Something went wrong. Please try again.'); track('free_tool_error', { code: (j && j.code) || '' }); return; }
        render(j.data, j);
        track('free_tool_result', { cached: !!j.cached });
        try { out.scrollIntoView({ behavior: 'smooth', block: 'start' }); } catch (x) { /* ignore */ }
      })
      .catch(function () { stopProgress(); if (btn) btn.disabled = false; showError('Could not reach the server. Check your connection and try again.'); });
  });

  // live word count for the plagiarism checker
  var wc = form.querySelector('[data-wc]'), area = form.querySelector('textarea[name=text]');
  if (wc && area) {
    var count = function () { var n = area.value.trim() ? area.value.trim().split(/\s+/).length : 0; wc.textContent = n.toLocaleString('en-US') + (n === 1 ? ' word' : ' words') + (n > 1500 ? ' (max 1,500)' : ''); wc.style.color = n > 1500 ? '#dc2626' : ''; };
    area.addEventListener('input', count); count();
  }

  // prefill from the hub picker (?url= or ?q=) and run once
  try {
    var qs = new URLSearchParams(location.search);
    var pre = qs.get('q') || qs.get('url');
    var first = form.querySelector('input[type=text], textarea');
    if (pre && first) {
      first.value = pre.slice(0, 500);
      setTimeout(function () { if (form.requestSubmit) form.requestSubmit(); else if (btn) btn.click(); }, 60);
    }
  } catch (e) { /* ignore */ }
})();
