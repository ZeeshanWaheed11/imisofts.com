/* imisofts ui-kit 1.0.0: styled, accessible dropdowns for the free tool pages.
   Each native <select> stays in the form (hidden) and keeps the value, so tool scripts keep working. */
(function () {
  'use strict';
  var CHEV = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5.5 8l4.5 4.5L14.5 8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var TICK = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M5 10.5l3 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var LENS = '<svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="9" cy="9" r="5.5" stroke="currentColor" stroke-width="1.7"/><path d="M13.2 13.2L17 17" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>';
  var uid = 0, openOne = null;

  function enhance(sel) {
    if (sel.getAttribute('data-ui') === 'on' || sel.multiple || sel.hasAttribute('data-native')) return;
    sel.setAttribute('data-ui', 'on');
    var id = 'ui-sel-' + (++uid);
    var wrap = document.createElement('div');
    wrap.className = 'ui-sel';
    sel.parentNode.insertBefore(wrap, sel);
    wrap.appendChild(sel);
    sel.classList.add('ui-native');
    sel.tabIndex = -1;
    sel.setAttribute('aria-hidden', 'true');

    var label = sel.getAttribute('aria-label') || '';
    var lab = sel.closest('label');
    if (!label && lab) label = (lab.firstChild && lab.firstChild.nodeType === 3 ? lab.firstChild.nodeValue : lab.textContent).trim();

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ui-sel-btn';
    btn.setAttribute('aria-haspopup', 'listbox');
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', id);
    if (label) btn.setAttribute('aria-label', label);
    btn.innerHTML = '<span class="v"></span>' + CHEV;
    wrap.appendChild(btn);

    var pop = document.createElement('div');
    pop.className = 'ui-pop';
    var many = sel.options.length > 8;
    var search = null;
    if (many) {
      var sb = document.createElement('div');
      sb.className = 'ui-search';
      sb.innerHTML = LENS + '<input type="text" autocomplete="off" spellcheck="false" placeholder="Search" aria-label="Search options">';
      pop.appendChild(sb);
      search = sb.querySelector('input');
    }
    var list = document.createElement('div');
    list.className = 'ui-list';
    list.id = id;
    list.setAttribute('role', 'listbox');
    if (label) list.setAttribute('aria-label', label);
    pop.appendChild(list);
    wrap.appendChild(pop);

    var items = [], active = -1;
    function build() {
      list.innerHTML = '';
      items = [];
      Array.prototype.forEach.call(sel.options, function (o, i) {
        if (o.disabled || o.hidden) return;
        var d = document.createElement('div');
        d.className = 'ui-opt';
        d.id = id + '-o' + i;
        d.setAttribute('role', 'option');
        d.setAttribute('data-i', String(i));
        d.innerHTML = '<span></span>' + TICK;
        d.firstChild.textContent = o.textContent;
        list.appendChild(d);
        items.push(d);
      });
      var empty = document.createElement('div');
      empty.className = 'ui-empty';
      empty.textContent = 'No matches';
      empty.hidden = true;
      list.appendChild(empty);
    }
    function sync() {
      var o = sel.options[sel.selectedIndex];
      btn.querySelector('.v').textContent = o ? o.textContent : '';
      items.forEach(function (d) {
        var on = Number(d.getAttribute('data-i')) === sel.selectedIndex;
        d.classList.toggle('on', on);
        d.setAttribute('aria-selected', on ? 'true' : 'false');
      });
    }
    function visible() { return items.filter(function (d) { return !d.hidden; }); }
    function setActive(d) {
      items.forEach(function (x) { x.classList.remove('act'); });
      active = -1;
      if (!d) { btn.removeAttribute('aria-activedescendant'); return; }
      d.classList.add('act');
      active = items.indexOf(d);
      btn.setAttribute('aria-activedescendant', d.id);
      var top = d.offsetTop, bottom = top + d.offsetHeight;
      if (top < list.scrollTop) list.scrollTop = top - 4;
      else if (bottom > list.scrollTop + list.clientHeight) list.scrollTop = bottom - list.clientHeight + 4;
    }
    function filter(q) {
      q = (q || '').trim().toLowerCase();
      var n = 0;
      items.forEach(function (d) { var hit = !q || d.textContent.toLowerCase().indexOf(q) !== -1; d.hidden = !hit; if (hit) n++; });
      list.querySelector('.ui-empty').hidden = n > 0;
      var v = visible();
      setActive(v[0] || null);
    }
    function open() {
      if (openOne && openOne !== api) openOne.close();
      openOne = api;
      var r = wrap.getBoundingClientRect();
      wrap.classList.toggle('up', window.innerHeight - r.bottom < 300 && r.top > 340);
      wrap.classList.add('open');
      btn.setAttribute('aria-expanded', 'true');
      if (search) { search.value = ''; filter(''); }
      var cur = items.filter(function (d) { return Number(d.getAttribute('data-i')) === sel.selectedIndex; })[0];
      setActive(cur || items[0]);
      if (search) setTimeout(function () { search.focus(); }, 30);
    }
    function close(focusBtn) {
      if (!wrap.classList.contains('open')) return;
      wrap.classList.remove('open');
      btn.setAttribute('aria-expanded', 'false');
      if (openOne === api) openOne = null;
      if (focusBtn) btn.focus();
    }
    function choose(d) {
      if (!d) return;
      var i = Number(d.getAttribute('data-i'));
      if (sel.selectedIndex !== i) {
        sel.selectedIndex = i;
        sel.dispatchEvent(new Event('input', { bubbles: true }));
        sel.dispatchEvent(new Event('change', { bubbles: true }));
      }
      sync();
      close(true);
    }
    function move(step) {
      var v = visible();
      if (!v.length) return;
      var cur = items[active];
      var k = v.indexOf(cur);
      k = k < 0 ? 0 : Math.max(0, Math.min(v.length - 1, k + step));
      setActive(v[k]);
    }
    var typed = '', typedAt = 0;
    function keys(e) {
      var isOpen = wrap.classList.contains('open');
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        if (!isOpen) { open(); return; }
        move(e.key === 'ArrowDown' ? 1 : -1);
      } else if (e.key === 'Home' && isOpen) { e.preventDefault(); setActive(visible()[0]); }
      else if (e.key === 'End' && isOpen) { e.preventDefault(); var v = visible(); setActive(v[v.length - 1]); }
      else if (e.key === 'Enter' || (e.key === ' ' && e.target === btn)) {
        e.preventDefault();
        if (!isOpen) open(); else choose(items[active]);
      } else if (e.key === 'Escape') {
        if (isOpen) { e.preventDefault(); e.stopPropagation(); close(true); }
      } else if (e.key === 'Tab') {
        close(false);
      } else if (!search && e.key.length === 1 && !e.metaKey && !e.ctrlKey && !e.altKey) {
        var now = Date.now();
        typed = (now - typedAt > 700 ? '' : typed) + e.key.toLowerCase();
        typedAt = now;
        var hit = items.filter(function (d) { return d.textContent.toLowerCase().indexOf(typed) === 0; })[0];
        if (hit) { if (!isOpen) open(); setActive(hit); }
      }
    }
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (wrap.classList.contains('open')) close(false); else open();
    });
    btn.addEventListener('keydown', keys);
    if (search) {
      search.addEventListener('input', function () { filter(search.value); });
      search.addEventListener('keydown', keys);
    }
    list.addEventListener('mousemove', function (e) {
      var d = e.target.closest ? e.target.closest('.ui-opt') : null;
      if (d && items.indexOf(d) !== active) setActive(d);
    });
    list.addEventListener('mousedown', function (e) { e.preventDefault(); });
    list.addEventListener('click', function (e) {
      var d = e.target.closest ? e.target.closest('.ui-opt') : null;
      if (d) choose(d);
    });
    sel.addEventListener('change', sync);
    var form = sel.form;
    if (form) form.addEventListener('reset', function () { setTimeout(sync, 0); });

    var api = { close: close, wrap: wrap };
    build();
    sync();
  }

  document.addEventListener('mousedown', function (e) {
    if (openOne && !openOne.wrap.contains(e.target)) openOne.close(false);
  });
  window.addEventListener('resize', function () { if (openOne) openOne.close(false); });

  function run() {
    var sels = document.querySelectorAll('main select');
    Array.prototype.forEach.call(sels, enhance);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run); else run();
})();
