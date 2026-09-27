/*
 * imisofts site measurement: Google Analytics 4 (G-ZYH120F6PK) + lead events.
 * Loaded once per page (root pages via <script defer>, blog pages via /blog/blog.js).
 * No visible output. gtag.js is fetched after the page has loaded, so it never
 * competes with page content.
 *
 * Events sent (besides GA4 enhanced measurement):
 *   generate_lead       booking completed in the Cal.com popup (lead_source)
 *   book_call_click     click on a Cal.com link or the "Book Growth Call" button
 *   contact_form_start  first interaction with the ClickUp contact form
 *   contact_click       email / phone / WhatsApp link click (contact_method)
 *   affiliate_click     click on a rel="sponsored" link (affiliate_program)
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

  // ---- contact form: first interaction with the ClickUp iframe ----
  var formStarted = false;
  window.addEventListener('blur', function () {
    if (formStarted) return;
    setTimeout(function () {
      var el = document.activeElement;
      if (el && el.tagName === 'IFRAME' && /forms\.clickup\.com/.test(el.src || '')) {
        formStarted = true;
        send('contact_form_start', { form_id: 'clickup-contact', form_name: 'Contact form' });
      }
    }, 0);
  });

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
