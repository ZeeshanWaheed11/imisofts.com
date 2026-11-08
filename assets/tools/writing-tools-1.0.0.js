/* imisofts free AI writing tools 1.0.0. One script for every writing tool page.
   AI tools call /api/tools/write; the lorem ipsum generator runs in the browser. */
(function () {
  'use strict';
  var root = document.querySelector('[data-wtool]');
  if (!root) return;
  var TOOL = root.getAttribute('data-wtool'), OUTPUT = root.getAttribute('data-output') || 'text', ENGINE = root.getAttribute('data-engine') || 'ai';
  var form = root.querySelector('form'), btn = form.querySelector('button[type=submit]'), label = btn.textContent;
  var out = root.querySelector('.ft-results'), err = root.querySelector('.ft-error');

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function track(n, p) { try { if (window.gtag) window.gtag('event', n, Object.assign({ tool: TOOL }, p || {})); } catch (e) {} }
  function showError(m) { err.textContent = m || ''; err.hidden = !m; }
  function busy(b) { btn.disabled = b; btn.textContent = b ? 'Working...' : label; }
  function copy(text, b) {
    var done = function () { var t = b.textContent; b.textContent = 'Copied'; setTimeout(function () { b.textContent = t; }, 1400); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done).catch(function () {});
    else { var ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand('copy'); done(); } catch (e) {} ta.remove(); }
  }
  function counts(s) { var w = (s.trim().match(/\S+/g) || []).length; return w + ' words, ' + s.length + ' characters'; }

  // live character counters on text inputs
  [].slice.call(form.querySelectorAll('[data-max]')).forEach(function (el) {
    var c = form.querySelector('[data-count-for="' + el.name + '"]');
    if (!c) return;
    var max = +el.getAttribute('data-max');
    var upd = function () { c.textContent = el.value.length + ' / ' + max; c.classList.toggle('over', el.value.length > max); };
    el.addEventListener('input', upd); upd();
  });

  function readFields() {
    return new Promise(function (resolve, reject) {
      var data = {}, pending = [];
      [].slice.call(form.elements).forEach(function (el) {
        if (!el.name) return;
        if (el.type === 'file') {
          var f = el.files && el.files[0];
          if (!f) return;
          if (f.size > 1048576) return reject(new Error('Please use an image up to 1 MB.'));
          if (!/^image\/(png|jpe?g|webp)$/.test(f.type)) return reject(new Error('Please use a JPG, PNG or WebP image.'));
          pending.push(new Promise(function (ok) { var r = new FileReader(); r.onload = function () { data[el.name] = r.result; ok(); }; r.readAsDataURL(f); }));
        } else data[el.name] = el.value;
      });
      Promise.all(pending).then(function () { resolve(data); });
    });
  }

  function render(text) {
    var html = '';
    if (OUTPUT === 'list') {
      var items = text.split(/\n+/).map(function (l) { return l.replace(/^\s*(\d+[.)]|[-*•])\s*/, '').trim(); }).filter(Boolean);
      html = '<ol class="wt-list">' + items.map(function (it, i) {
        return '<li><span>' + esc(it) + '</span><button type="button" class="wt-copy" data-i="' + i + '">Copy</button></li>';
      }).join('') + '</ol>';
      out.innerHTML = '<div class="ft-bar"><strong>' + items.length + ' results</strong><div class="ft-actions"><button type="button" class="wt-all">Copy all</button><button type="button" class="wt-again">Generate again</button></div></div>' + html;
      [].slice.call(out.querySelectorAll('.wt-copy')).forEach(function (b) { b.addEventListener('click', function () { copy(items[+b.getAttribute('data-i')], b); track('tool_copy'); }); });
      out.querySelector('.wt-all').addEventListener('click', function (e) { copy(items.join('\n'), e.currentTarget); track('tool_copy'); });
    } else {
      html = '<div class="wt-text">' + text.split(/\n{2,}/).map(function (p) { return '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>'; }).join('') + '</div>';
      out.innerHTML = '<div class="ft-bar"><small class="wt-count">' + counts(text) + '</small><div class="ft-actions"><button type="button" class="wt-all">Copy</button><button type="button" class="wt-again">Generate again</button></div></div>' + html;
      out.querySelector('.wt-all').addEventListener('click', function (e) { copy(text, e.currentTarget); track('tool_copy'); });
    }
    out.querySelector('.wt-again').addEventListener('click', function () { submit(); });
    out.hidden = false;
  }

  /* lorem ipsum, generated in the browser */
  var LOREM = 'lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum'.split(' ');
  function sentence() {
    var n = 8 + Math.floor(Math.random() * 10), w = [];
    for (var i = 0; i < n; i++) w.push(LOREM[Math.floor(Math.random() * LOREM.length)]);
    var s = w.join(' '); return s.charAt(0).toUpperCase() + s.slice(1) + '.';
  }
  function lorem(fields) {
    var count = Math.max(1, Math.min(20, parseInt(fields.paragraphs || '3', 10) || 3)), ps = [];
    var startClassic = !/^no/i.test(String(fields[Object.keys(fields).filter(function (k) { return k !== 'paragraphs'; })[0]] || 'Yes'));
    for (var p = 0; p < count; p++) {
      var ss = [], n = 4 + Math.floor(Math.random() * 3);
      for (var i = 0; i < n; i++) ss.push(sentence());
      ps.push(ss.join(' '));
    }
    if (startClassic) ps[0] = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. ' + ps[0];
    return ps.join('\n\n');
  }

  function submit() {
    showError('');
    busy(true);
    readFields().then(function (fields) {
      track('tool_run');
      if (ENGINE === 'local') { busy(false); render(lorem(fields)); track('tool_done'); return; }
      return fetch('/api/tools/write', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ tool: TOOL, fields: fields }) })
        .then(function (r) { return r.json().catch(function () { return { ok: false, error: 'The tool is busy. Please try again in a minute.' }; }); })
        .then(function (j) {
          busy(false);
          if (!j || !j.ok) return showError((j && j.error) || 'Something went wrong. Please try again.');
          render(j.text); track('tool_done');
        });
    }).catch(function (e) { busy(false); showError(e.message || 'Network error. Please try again.'); });
  }
  form.addEventListener('submit', function (e) { e.preventDefault(); if (!form.reportValidity || form.reportValidity()) submit(); });
})();
