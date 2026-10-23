/* imisofts.com free DNS propagation checker: the form and buttons.
   The engine (propagation-1.1.0.js) and the display code (propui-1.1.0.js) are the same files as in the
   SPF, DKIM & DMARC Checker extension. Lookups go straight from the browser to six public DNS providers
   over HTTPS. Nothing is sent to imisofts, and nothing is saved in the browser. */
(function () {
  'use strict';
  var P = window.ImisoftsPropagation, U = window.ImisoftsPropUI;
  var $ = function (id) { return document.getElementById(id); };
  if (!P || !U || !$('dp-form')) return;
  var busy = false, last = null;
  var LINK = 'Checked with the free DNS propagation checker by imisofts: https://imisofts.com/dns-propagation-checker';

  function ga(name, params) { if (typeof window.gtag === 'function') window.gtag('event', name, params); }
  function setPlaceholder() { $('dp-exp').placeholder = U.PLACEHOLDER[$('dp-type').value] || ''; }
  function status(text, cls) { var s = $('dp-status'); s.className = 'dp-status' + (cls ? ' ' + cls : ''); s.textContent = text; }

  function run() {
    if (busy) return;
    var name = P.cleanName($('dp-name').value);
    if (!name) { status('Enter the full record name, like test.yourdomain.com or _dmarc.yourdomain.com.', 'err'); $('dp-name').focus(); return; }
    var type = $('dp-type').value, expected = $('dp-exp').value.trim();
    busy = true;
    $('dp-go').disabled = true; $('dp-again').disabled = true;
    $('dp-name').value = name;
    status('Asking 6 DNS providers about ' + name + '...');
    P.check(name, type, expected).then(function (c) {
      if (c.error) { status('Enter a valid record name.', 'err'); return; }
      last = c;
      status(c.headline, 'sr');                // announced to screen readers; the summary shows it on screen
      U.render({ summary: $('dp-sum'), title: $('dp-sum-title'), sub: $('dp-sum-sub'), rows: $('dp-rows'), host: $('dp-host'), notes: $('dp-notes'), maxNotes: 4 }, c);
      $('dp-results').hidden = false;
      // Only the record type and the outcome are measured, never the name or value checked.
      ga('dns_propagation_check', { record_type: type, result_state: c.state, with_expected_value: expected ? 'yes' : 'no' });
    }).catch(function () {
      status('Could not reach the DNS providers. Check your connection and try again.', 'err');
    }).then(function () {
      busy = false;
      $('dp-go').disabled = false; $('dp-again').disabled = false;
    });
  }

  function copyReport() {
    if (!last) return;
    var text = P.reportText(last).replace(/Checked with the free SPF, DKIM & DMARC Checker by imisofts: \S+$/, LINK);
    U.copy(text).then(function (ok) {
      $('dp-copy').textContent = ok ? 'Copied' : 'Copy failed';
      setTimeout(function () { $('dp-copy').textContent = 'Copy report'; }, 1500);
    });
  }

  $('dp-form').addEventListener('submit', function (ev) { ev.preventDefault(); run(); });
  $('dp-again').addEventListener('click', run);
  $('dp-copy').addEventListener('click', copyReport);
  $('dp-type').addEventListener('change', setPlaceholder);
  setPlaceholder();
  document.documentElement.setAttribute('data-dp-ready', '');
})();
