/* Blog JS - TOC highlighting, smooth scroll, FAQ accordion, search, filtering */

(function() {
  'use strict';

  // ===== TOC Active State Highlighting =====
  function initTOC() {
    var tocLinks = document.querySelectorAll('.toc-list a, .mobile-toc-content .toc-list a');
    if (!tocLinks.length) return;

    var headings = [];
    tocLinks.forEach(function(link) {
      var id = link.getAttribute('href');
      if (id && id.startsWith('#')) {
        var el = document.getElementById(id.substring(1));
        if (el) headings.push({ el: el, link: link });
      }
    });

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function() {
        var scrollPos = window.scrollY + 120;
        var current = null;
        for (var i = 0; i < headings.length; i++) {
          if (headings[i].el.offsetTop <= scrollPos) {
            current = headings[i];
          }
        }
        tocLinks.forEach(function(l) { l.classList.remove('active'); });
        if (current) current.link.classList.add('active');
        ticking = false;
      });
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ===== Smooth Scroll for Anchor Links =====
  function initSmoothScroll() {
    document.addEventListener('click', function(e) {
      var link = e.target.closest('a[href^="#"]');
      if (!link) return;
      var target = document.getElementById(link.getAttribute('href').substring(1));
      if (target) {
        e.preventDefault();
        var offset = 96;
        var top = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top: top, behavior: 'smooth' });
        history.replaceState(null, '', link.getAttribute('href'));
      }
    });
  }

  // ===== FAQ Accordion =====
  function initFAQ() {
    document.querySelectorAll('.faq-question').forEach(function(btn) {
      btn.addEventListener('click', function() {
        var item = this.closest('.faq-item');
        var wasActive = item.classList.contains('active');
        // Close all
        document.querySelectorAll('.faq-item').forEach(function(i) {
          i.classList.remove('active');
        });
        if (!wasActive) item.classList.add('active');
      });
    });
  }

  // ===== Mobile TOC Toggle =====
  function initMobileTOC() {
    var toggle = document.querySelector('.mobile-toc-toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function() {
      this.closest('.mobile-toc').classList.toggle('open');
    });
  }

  // ===== Blog Listing: Category Filter & Search =====
  function initBlogListing() {
    var tabs = document.querySelectorAll('.cat-tab');
    var searchInput = document.getElementById('blogSearch');
    var postsContainer = document.getElementById('postsGrid');
    if (!postsContainer) return;

    var cards = Array.from(postsContainer.querySelectorAll('.post-card'));
    var loadMoreBtn = document.getElementById('loadMoreBtn');
    var visibleCount = 12;
    var currentCat = 'All';
    var searchTerm = '';

    function filterAndRender() {
      var filtered = cards.filter(function(card) {
        var catMatch = currentCat === 'All' || card.getAttribute('data-category') === currentCat;
        var searchMatch = !searchTerm ||
          card.getAttribute('data-title').toLowerCase().indexOf(searchTerm) !== -1 ||
          card.getAttribute('data-keywords').toLowerCase().indexOf(searchTerm) !== -1;
        return catMatch && searchMatch;
      });

      cards.forEach(function(c) { c.style.display = 'none'; });
      filtered.forEach(function(c, i) {
        c.style.display = i < visibleCount ? '' : 'none';
      });

      if (loadMoreBtn) {
        loadMoreBtn.style.display = filtered.length > visibleCount ? '' : 'none';
      }

      var noResults = postsContainer.querySelector('.no-results');
      if (filtered.length === 0) {
        if (!noResults) {
          noResults = document.createElement('div');
          noResults.className = 'no-results';
          noResults.textContent = 'No posts found matching your criteria.';
          postsContainer.appendChild(noResults);
        }
        noResults.style.display = '';
      } else if (noResults) {
        noResults.style.display = 'none';
      }
    }

    tabs.forEach(function(tab) {
      tab.addEventListener('click', function() {
        tabs.forEach(function(t) { t.classList.remove('active'); });
        this.classList.add('active');
        currentCat = this.getAttribute('data-category');
        visibleCount = 12;
        filterAndRender();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', function() {
        searchTerm = this.value.toLowerCase().trim();
        visibleCount = 12;
        filterAndRender();
      });
    }

    if (loadMoreBtn) {
      loadMoreBtn.addEventListener('click', function() {
        visibleCount += 12;
        filterAndRender();
      });
    }

    filterAndRender();
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initTOC();
    initSmoothScroll();
    initFAQ();
    initMobileTOC();
    initBlogListing();
  }
})();
