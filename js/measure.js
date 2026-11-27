/*
 * imisofts site measurement: Google Analytics 4 (G-ZYH120F6PK) + lead events.
 * Loaded once per page (root pages via <script defer>, blog pages via /blog/blog.js).
 * No visible output. gtag.js is fetched after the page has loaded, so it never
 * competes with page content.
 *
 * Events sent (besides GA4 enhanced measurement):
 *   generate_lead       booking completed in the Cal.com popup (lead_source cal_embed),
 *                       or a visit to /thank-you?src=cal after a booking made on cal.com
 *                       itself (lead_source cal_redirect); one lead per browser per 12 h
 *   book_call_click     click on a Cal.com link or the "Book Growth Call" button
 *   contact_form_start  first interaction with a ClickUp client form (contact / cold email)
 *   job_application_start  first interaction with the ClickUp job application form on
 *                       /careers (not a key event: applicants are not leads)
 *   contact_click       email / phone / WhatsApp link click (contact_method)
 *   affiliate_click     click on a rel="sponsored" link (affiliate_program)
 *
 * The random GA client ID is also passed into the ClickUp contact form's hidden
 * "GA client ID" field, so a lead's later stages (qualified, won) can be imported
 * into GA4 for that visitor. No name, email or other personal data is passed.
 * Since 2026-11-27 every ClickUp form also gets three hidden attribution fields:
 * "Lead source" (this session's source, e.g. google / organic), "Landing page"
 * (first page of the session, path only) and "Form page" (path only). ClickUp
 * cannot tell the page when an embedded form is sent, so each lead carries its own
 * attribution and the weekly audit counts real leads from ClickUp.
 *
 * Mark a browser as internal (excluded by the GA4 internal-traffic filter):
 * open any page once with ?internal=1 . Undo with ?internal=0 .
 */
(function () {
  'use strict';
  if (window.__imMeasure) return;
  window.__imMeasure = true;

  var GA_ID = 'G-ZYH120F6PK';
  var host = location.hostname;
  if (host !== 'imisofts.com' && host !== 'www.imisofts.com') return;
  if (navigator.webdriver) return;

  var search = location.search || '';

  var internal = false;
  try {
    if (/[?&]internal=1\b/.test(search)) localStorage.setItem('im_internal', '1');
    if (/[?&]internal=0\b/.test(search)) localStorage.removeItem('im_internal');
    internal = localStorage.getItem('im_internal') === '1';
  } catch (e) { /* storage blocked: treat as external */ }

  var LEAD_KEY = 'im_lead_ts';
  var LEAD_WINDOW = 12 * 60 * 60 * 1000;
  function leadRecently() {
    try { var t = parseInt(localStorage.getItem(LEAD_KEY) || '0', 10); return t && Date.now() - t < LEAD_WINDOW; }
    catch (e) { return false; }
  }
  function markLead() {
    try { localStorage.setItem(LEAD_KEY, String(Date.now())); } catch (e) { /* ignore */ }
  }

  // Thank-you page: read our own ?src=, then drop every query parameter before GA
  // reads the URL (booking tools can append names and email addresses).
  var isThanks = /^\/thank-you(\.html)?\/?$/.test(location.pathname);
  var thanksSrc = '';
  if (isThanks) {
    var sm = /[?&]src=([a-z0-9_-]{1,30})/i.exec(search);
    thanksSrc = sm ? sm[1].toLowerCase() : '';
    if (search && window.history && history.replaceState) {
      try { history.replaceState(null, '', location.pathname + location.hash); } catch (e) { /* ignore */ }
    }
  }

  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag = gtag;

  // Consent Mode v2 defaults: analytics counted for every visitor in every country
  // (Zeeshan's decision, 2026-09-27: no banner, count everyone); ads storage,
  // ad user data and ad personalisation off everywhere.
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'granted'
  });
  gtag('set', 'ads_data_redaction', true);

  function contentGroup() {
    var p = location.pathname.replace(/\.html$/, '');
    if (/page not found/i.test(document.title) || p === '/404') return '404';
    if (p === '/' || p === '/index') return 'Home';
    if (p === '/blog' || p === '/blog/') return 'Blog index';
    if (p.indexOf('/blog/') === 0) {
      var section = '';
      var nodes = document.querySelectorAll('script[type="application/ld+json"]');
      for (var i = 0; i < nodes.length && !section; i++) {
        var m = /"articleSection"\s*:\s*"([^"]{1,60})"/.exec(nodes[i].textContent || '');
        if (m) section = m[1];
      }
      return 'Blog: ' + (section || 'Article');
    }
    if (p.indexOf('/author/') === 0) return 'Author';
    if (/^\/thank-you\/?$/.test(p)) return 'Thank-you page';
    if (/^\/(contact|pricing|free-audit)\/?$/.test(p)) return 'Conversion page';
    if (/^\/(about|careers|case-studies|faq|support|products|api-docs|privacy-policy|terms-of-service|cookie-policy)\/?$/.test(p)) return 'Company page';
    return 'Service page';
  }

  var config = {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    content_group: contentGroup()
  };
  if (internal) config.traffic_type = 'internal';
  if (/[?&]gadebug=1\b/.test(search)) config.debug_mode = true;

  gtag('js', new Date());
  gtag('config', GA_ID, config);

  function send(name, params) {
    try { gtag('event', name, params || {}); } catch (e) { /* never break the page */ }
  }

  if (isThanks && !leadRecently()) {
    send('generate_lead', { lead_source: thanksSrc === 'cal' ? 'cal_redirect' : (thanksSrc ? 'thanks_' + thanksSrc : 'thank_you_page') });
    markLead();
  }

  // ---- lead: booking completed inside the Cal.com popup ----
  var lastLead = 0;
  var seenBookings = {};
  function onBooking(e) {
    var d = (e && e.detail && e.detail.data) || {};
    var id = d.uid || (d.booking && d.booking.uid) || '';
    var now = Date.now();
    if ((id && seenBookings[id]) || now - lastLead < 15000) return;
    if (id) seenBookings[id] = 1;
    lastLead = now;
    send('generate_lead', { lead_source: 'cal_embed' });
    if (window.google_tag_manager) markLead();
  }
  function hookCal() {
    var Cal = window.Cal;
    if (!Cal || !Cal.ns) return false;
    var names = Object.keys(Cal.ns);
    for (var i = 0; i < names.length; i++) {
      var api = Cal.ns[names[i]];
      if (typeof api !== 'function' || api.__imHooked) continue;
      api.__imHooked = true;
      api('on', { action: 'bookingSuccessfulV2', callback: onBooking });
      api('on', { action: 'bookingSuccessful', callback: onBooking });
    }
    return names.length > 0;
  }
  if (!hookCal()) {
    document.addEventListener('DOMContentLoaded', hookCal);
    window.addEventListener('load', hookCal);
  }

  // ---- clicks: booking CTAs, contact links, sponsored links ----
  var PROGRAMS = [
    [/instantly/, 'instantly'], [/apollo/, 'apollo'], [/smartlead/, 'smartlead'],
    [/apify/, 'apify'], [/gohighlevel|highlevel/, 'gohighlevel'], [/appsumo|8odi\.net/, 'appsumo'],
    [/brightdata/, 'brightdata'], [/(^|\.)kit\.com|convertkit/, 'kit'], [/leadpages/, 'leadpages'],
    [/close\.com/, 'close'], [/monday\.com/, 'monday'], [/brevo/, 'brevo']
  ];
  function program(hostname) {
    for (var i = 0; i < PROGRAMS.length; i++) if (PROGRAMS[i][0].test(hostname)) return PROGRAMS[i][1];
    var parts = hostname.split('.');
    return parts.length > 1 ? parts[parts.length - 2] : hostname;
  }
  function text(el) {
    var t = ((el.innerText || el.textContent || el.getAttribute('aria-label') || '') + '')
      .replace(/\s+/g, ' ').trim().slice(0, 100);
    return /@/.test(t) ? 'email address' : t;
  }

  function onClick(e) {
    if (e.type === 'auxclick' && e.button !== 1) return;
    var t = e.target;
    if (!t || !t.closest) return;

    var calEl = t.closest('[data-cal-link]');
    if (calEl) {
      send('book_call_click', {
        link_text: text(calEl) || calEl.getAttribute('data-button-text') || 'Book call button',
        link_url: 'cal.com/' + (calEl.getAttribute('data-cal-link') || '')
      });
      return;
    }

    var a = t.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var rel = (a.getAttribute('rel') || '').toLowerCase();

    if (/^mailto:/i.test(href)) { send('contact_click', { contact_method: 'email', link_text: text(a) }); return; }
    if (/^tel:/i.test(href)) { send('contact_click', { contact_method: 'phone', link_text: text(a) }); return; }
    if (/^(https?:)?\/\/(wa\.me|api\.whatsapp\.com|chat\.whatsapp\.com)\//i.test(href) || /^whatsapp:/i.test(href)) {
      send('contact_click', { contact_method: 'whatsapp', link_text: text(a) });
      return;
    }

    var url;
    try { url = new URL(href, location.href); } catch (err) { return; }

    if (/(^|\.)cal\.com$/i.test(url.hostname)) {
      send('book_call_click', { link_text: text(a), link_url: url.hostname + url.pathname });
      return;
    }

    if (rel.indexOf('sponsored') !== -1) {
      send('affiliate_click', {
        affiliate_program: program(url.hostname.toLowerCase()),
        link_domain: url.hostname,
        link_url: url.href.slice(0, 300),
        link_text: text(a)
      });
    }
  }
  document.addEventListener('click', onClick, true);
  document.addEventListener('auxclick', onClick, true);

  // ---- ClickUp forms: which embedded form is which ----
  var JOB_FORM = /2kzmpqh8-2798/;   // "Job Application Form - Careers" (list Job Applications)
  function isClickupFrame(el) {
    return !!(el && el.tagName === 'IFRAME' && /forms\.clickup\.com/.test(el.getAttribute('src') || ''));
  }

  // ---- first interaction with a ClickUp form ----
  var formStarted = false;   // any ClickUp form touched: never reload a form after this
  var contactSent = false, jobSent = false;
  window.addEventListener('blur', function () {
    setTimeout(function () {
      var el = document.activeElement;
      if (!isClickupFrame(el)) return;
      formStarted = true;
      if (JOB_FORM.test(el.getAttribute('src') || '')) {
        if (jobSent) return;
        jobSent = true;
        send('job_application_start', { form_id: 'clickup-job', form_name: 'Job application form' });
      } else {
        if (contactSent) return;
        contactSent = true;
        send('contact_form_start', { form_id: 'clickup-contact', form_name: 'Contact form' });
      }
    }, 0);
  });

  // ---- lead attribution: this session's source and landing page ----
  // Kept in sessionStorage so the form page still knows how the visitor arrived.
  // Paths only, never query strings; no personal data.
  function clean(v) { return String(v || '').replace(/[^\w .\/:()@+-]/g, '').slice(0, 100); }
  function decodeSafe(v) { try { return decodeURIComponent(v.replace(/\+/g, ' ')); } catch (e) { return v; } }
  var AI_RX = /chatgpt|openai|perplexity|claude\.ai|anthropic|gemini\.google|copilot|meta\.ai|deepseek|grok|mistral|phind|you\.com|poe\.com/i;
  function sessionSource() {
    var m, us = '', um = '';
    if ((m = /[?&]utm_source=([^&#]{1,80})/i.exec(search))) us = decodeSafe(m[1]).toLowerCase();
    if ((m = /[?&]utm_medium=([^&#]{1,80})/i.exec(search))) um = decodeSafe(m[1]).toLowerCase();
    if (us) return us + ' / ' + (um || (AI_RX.test(us) ? 'ai-assistant' : '(none)'));
    var host = '';
    try { host = document.referrer ? new URL(document.referrer).hostname.replace(/^www\./, '').toLowerCase() : ''; }
    catch (e) { host = ''; }
    if (!host || /(^|\.)imisofts\.com$/.test(host)) return '(direct)';
    if (AI_RX.test(host)) return host + ' / ai-assistant';
    if (/^(mail|accounts|docs|drive|sites)\.google\./.test(host)) return host + ' / referral';
    var se = /(^|\.)(google|bing|duckduckgo|yahoo|yandex|baidu|ecosia|brave|naver)\./.exec(host + '.');
    if (se) return se[2] + ' / organic';
    if (/(^|\.)(linkedin\.com|lnkd\.in|facebook\.com|fb\.com|instagram\.com|t\.co|x\.com|twitter\.com|reddit\.com|youtube\.com|pinterest\.com|tiktok\.com|quora\.com)$/.test(host)) return host + ' / social';
    return host + ' / referral';
  }
  var leadSource = '', landingPage = '';
  try {
    leadSource = sessionStorage.getItem('im_src') || '';
    landingPage = sessionStorage.getItem('im_land') || '';
    if (!leadSource) { leadSource = clean(sessionSource()); sessionStorage.setItem('im_src', leadSource); }
    if (!landingPage) { landingPage = clean(location.pathname); sessionStorage.setItem('im_land', landingPage); }
  } catch (e) {
    leadSource = leadSource || clean(sessionSource());
    landingPage = landingPage || clean(location.pathname);
  }

  // ---- pass attribution (and the GA client ID) into the ClickUp forms ----
  // The forms have hidden fields with these names; ClickUp fills hidden fields from
  // the form URL. A daily upload can send later lead stages to GA4 for the client ID.
  // A form is never reloaded once someone has started typing in it.
  function clientIdFromCookie() {
    var m = /(?:^|;\s*)_ga=GA\d\.\d\.(\d+\.\d+)/.exec(document.cookie || '');
    return m ? m[1] : '';
  }
  function withParams(src, params) {
    var add = [];
    for (var k in params) {
      if (!Object.prototype.hasOwnProperty.call(params, k) || !params[k]) continue;
      var key = encodeURIComponent(k);
      if (src.indexOf(key + '=') !== -1) continue;
      add.push(key + '=' + encodeURIComponent(params[k]));
    }
    if (!add.length) return src;
    return src + (src.indexOf('?') === -1 ? '?' : '&') + add.join('&');
  }
  function tagForms(cid) {
    var frames = document.querySelectorAll('iframe');
    for (var i = 0; i < frames.length; i++) {
      var f = frames[i];
      var src = f.getAttribute('src') || '';
      if (!/^https:\/\/forms\.clickup\.com\//.test(src)) continue;
      if (formStarted || document.activeElement === f) continue;
      var params = { 'Lead source': leadSource, 'Landing page': landingPage, 'Form page': clean(location.pathname) };
      if (cid && !JOB_FORM.test(src)) params['GA client ID'] = cid;
      var next = withParams(src, params);
      if (next !== src) f.setAttribute('src', next);
    }
  }
  try { tagForms(clientIdFromCookie()); } catch (e) { /* never break the page */ }
  var cidTries = 0;
  function pollClientId() {
    var cid = clientIdFromCookie();
    if (cid) { try { tagForms(cid); } catch (e) { /* ignore */ } return; }
    if (++cidTries < 40) setTimeout(pollClientId, 500);
  }
  if (document.readyState === 'complete') pollClientId();
  else window.addEventListener('load', pollClientId);

  // ---- load gtag.js after the page has finished loading ----
  var loaded = false;
  function loadTag() {
    if (loaded) return;
    loaded = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }
  function scheduleTag() {
    if ('requestIdleCallback' in window) window.requestIdleCallback(loadTag, { timeout: 1500 });
    else setTimeout(loadTag, 200);
  }
  if (document.readyState === 'complete') scheduleTag();
  else window.addEventListener('load', scheduleTag);
  // First interaction before load: fetch the tag right away so early clicks are not lost.
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) {
    window.addEventListener(ev, loadTag, { once: true, passive: true });
  });
  // Safety net for very slow pages.
  setTimeout(loadTag, 6000);
})();
