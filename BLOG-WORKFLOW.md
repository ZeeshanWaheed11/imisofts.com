# Blog Post Creation Workflow — imisofts.com

> Comprehensive guide for adding 100+ blog posts per batch.
> Last updated: March 10, 2026

---

## File Architecture

```
imisofts.com/
├── blog.html                    ← MAIN blog listing page (served at /blog)
├── blog/
│   ├── index.html               ← Secondary listing page (served at /blog/)
│   ├── blog.css                 ← Blog-specific styles (article layout, TOC, FAQ)
│   ├── blog.js                  ← Blog JS (TOC highlighting, filters, FAQ accordion)
│   ├── posts-index.json         ← Master post registry (ALL posts with metadata)
│   └── [slug]/
│       └── index.html           ← Individual blog post page
├── sitemap.xml                  ← Must include all blog post URLs
├── robots.txt                   ← Sitemap reference
└── index.html                   ← Homepage
```

### CRITICAL: Two Listing Pages

| File | URL | Purpose |
|------|-----|---------|
| `blog.html` (root) | `/blog` | **PRIMARY** listing page users see |
| `blog/index.html` | `/blog/` | Secondary listing (with trailing slash) |

**Both must be updated when adding posts.** Past mistakes happened because only `blog/index.html` was updated while `blog.html` (the real page) was ignored.

---

## 7 Standard Categories

| Category | Gradient | Hex Colors |
|----------|----------|------------|
| Cold Email Infrastructure | Orange | `#F26522, #E55A1B` |
| B2B Lead Gen & Outreach | Green | `#059669, #047857` |
| Email Copywriting & Sequences | Purple | `#7C3AED, #6D28D9` |
| Platform Guides & Tutorials | Dark Gray | `#374151, #1F2937` |
| Industry-Specific Cold Email | Navy Blue | `#1E3A5F, #2C5282` |
| European B2B Cold Email | Teal | `#0D9488, #0F766E` |
| Strategy & Benchmarks | Red | `#DC2626, #B91C1C` |

### Category Assignment Rules

- **Cold Email Infrastructure**: DNS, domains, warmup, deliverability, servers, IPs, sending limits, bounce rates, tracking domains, SPF/DKIM/DMARC, BIMI
- **B2B Lead Gen & Outreach**: Lead lists, targeting, ICP, data enrichment, scraping, campaign management, personalization, multi-channel outreach
- **Email Copywriting & Sequences**: Subject lines, first lines, CTAs, templates, follow-ups, A/B testing, spintax, copy frameworks, sequences
- **Platform Guides & Tutorials**: Instantly, SmartLead, Apollo, Clay, n8n, GoHighLevel, tool comparisons, setup guides, AI tools
- **Industry-Specific Cold Email**: Posts targeting a specific industry (SaaS, law firms, real estate, insurance, etc.)
- **European B2B Cold Email**: GDPR, country-specific guides (UK, Germany, Netherlands, etc.), localization, opt-in vs opt-out
- **Strategy & Benchmarks**: ROI, benchmarks, agency vs DIY, cold email vs other channels, scaling strategies, industry trends

---

## Step-by-Step: Adding New Blog Posts

### Step 1: Create Post Files

For each new post, create `blog/[slug]/index.html` with this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Standard meta tags -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Post Title] | imisofts</title>
  <meta name="description" content="[160-char description]">
  <link rel="canonical" href="https://imisofts.com/blog/[slug]/">
  <meta name="robots" content="max-snippet:-1, max-image-preview:large">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="[Post Title]">
  <meta property="og:url" content="https://imisofts.com/blog/[slug]/">
  <meta property="article:author" content="Zeeshan Waheed">

  <!-- JSON-LD Schema -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "[Post Title]",
    "author": {"@type": "Person", "name": "Zeeshan Waheed", "url": "https://imisofts.com/author/zeeshan-waheed/"},
    "datePublished": "[YYYY-MM-DD]",
    "url": "https://imisofts.com/blog/[slug]/"
  }
  </script>

  <!-- INLINE STYLES: Copy the full <style> block from an existing post -->
  <style>
    /* ... navbar styles + blog article styles ... */
  </style>
  <link rel="stylesheet" href="/blog/blog.css">
</head>
<body>
  <!-- HEADER: Copy exact navbar from index.html (lines 1625-1904) -->
  <header>
    <!-- ... navbar ... -->
  </header>

  <main>
    <!-- Breadcrumb -->
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="/">Home</a> <span>/</span>
      <a href="/blog/">Blog</a> <span>/</span>
      <a href="/blog/?cat=[category-slug]">[Category Name]</a> <span>/</span>
      <span>[Post Title]</span>
    </nav>

    <div class="blog-layout">
      <article class="article-container">
        <header class="article-header">
          <h1>[Post Title]</h1>
          <div class="article-meta">
            <div class="article-meta-item">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
              <a href="/author/zeeshan-waheed/" target="_blank" rel="noopener" style="color: #1a1a1a; text-decoration: none;">Zeeshan Waheed</a>
            </div>
            <!-- date and read time meta items -->
          </div>
        </header>

        <!-- Article body with h2 sections (each h2 needs an id for TOC) -->
        <h2 id="section-slug">Section Title</h2>
        <p>Content...</p>
      </article>

      <!-- Sidebar with TOC -->
      <aside class="blog-sidebar">
        <div class="toc">
          <h3>Table of Contents</h3>
          <ul class="toc-list">
            <li><a href="#section-slug">Section Title</a></li>
          </ul>
        </div>
      </aside>
    </div>
  </main>

  <!-- FOOTER: Copy exact footer from index.html -->

  <!-- Navbar JS (copy from existing post) -->
  <script>
    // megaTabSwitch, toggleMobileMenu, toggleMobileSection, scroll effect
  </script>
  <script src="/blog/blog.js" defer></script>
</body>
</html>
```

### Step 2: Update posts-index.json

Add each new post to `blog/posts-index.json`:

```json
{
  "slug": "post-slug",
  "title": "Post Title",
  "meta_description": "160-character description",
  "category": "Cold Email Infrastructure",
  "date": "2026-03-10",
  "read_time": 8,
  "keywords": ["keyword1", "keyword2"]
}
```

### Step 3: Rebuild blog.html (PRIMARY listing page)

This is the **most critical step** and the one most often missed.

Use the Python rebuild script:

```python
import json, re, html as html_mod

with open('blog/posts-index.json') as f:
    posts = json.load(f)

GRADIENTS = {
    "Cold Email Infrastructure": ("linear-gradient(135deg, #F26522, #E55A1B)", "COLD EMAIL INFRASTRUCTURE"),
    "Industry-Specific Cold Email": ("linear-gradient(135deg, #1E3A5F, #2C5282)", "INDUSTRY-SPECIFIC COLD EMAIL"),
    "B2B Lead Gen & Outreach": ("linear-gradient(135deg, #059669, #047857)", "B2B LEAD GEN & OUTREACH"),
    "Email Copywriting & Sequences": ("linear-gradient(135deg, #7C3AED, #6D28D9)", "EMAIL COPYWRITING & SEQUENCES"),
    "European B2B Cold Email": ("linear-gradient(135deg, #0D9488, #0F766E)", "EUROPEAN B2B COLD EMAIL"),
    "Platform Guides & Tutorials": ("linear-gradient(135deg, #374151, #1F2937)", "PLATFORM GUIDES & TUTORIALS"),
    "Strategy & Benchmarks": ("linear-gradient(135deg, #DC2626, #B91C1C)", "STRATEGY & BENCHMARKS"),
}

# Generate card HTML for each post
# Generate category tabs with counts
# Replace the <div class="blog-grid"> section in blog.html
# Replace the <div class="category-tabs"> section in blog.html
```

### Step 4: Update blog/index.html (secondary listing page)

Uses a DIFFERENT card structure (`.post-card` + `.card-thumbnail` classes):

```html
<a href="/blog/[slug]/" class="post-card" data-category="[Category Name]"
   data-title="[title]" data-keywords="[keywords]">
  <div class="card-thumbnail" style="background: [gradient];">
    <span class="card-thumb-cat">[CATEGORY LABEL]</span>
    <span class="card-thumb-title">[Title]</span>
    <span class="card-thumb-brand">imisofts.com</span>
  </div>
  <div class="post-card-body">
    <span class="post-cat-badge">[Category Name]</span>
    <h3 class="post-card-title">[Title]</h3>
    <p class="post-card-desc">[Description]</p>
    <div class="post-card-meta">
      <span>[Date]</span><span>[X] min read</span>
    </div>
  </div>
</a>
```

### Step 5: Update sitemap.xml

Add a `<url>` entry for each new post.

### Step 6: Verify Checklist

Before committing, always verify:

- [ ] `blog/posts-index.json` has all posts (count matches folder count)
- [ ] `blog.html` has all posts as `.blog-card` elements
- [ ] `blog/index.html` has all posts as `.post-card` elements
- [ ] Author name "Zeeshan Waheed" is hyperlinked with `target="_blank"` in every post
- [ ] Category tabs in `blog.html` match actual post categories
- [ ] Category badge on each post matches the category in `posts-index.json`
- [ ] `sitemap.xml` includes all post URLs
- [ ] Each `h2` in article body has an `id` attribute (for TOC linking)
- [ ] No broken `<img>` tags — use CSS gradient thumbnails instead

---

## Common Mistakes to Avoid

### 1. Editing the wrong listing page
`blog/index.html` is NOT the primary listing. `blog.html` at the root is.

### 2. Using `<img>` tags for thumbnails
External image URLs break. Always use CSS gradient thumbnails with inline styles.

### 3. Inconsistent category names
Always use the exact 7 category names from the table above. Never create new categories or use shorthand.

### 4. Missing `target="_blank"` on author links
Every author link must open in a new tab.

### 5. Different card structures in the two listing pages
`blog.html` uses `.blog-card` class. `blog/index.html` uses `.post-card` class. They have different HTML structures.

### 6. Forgetting to update posts-index.json
This is the source of truth. Both listing pages should be generated from it.

### 7. Not HTML-escaping titles
Titles with `&`, `<`, `>`, quotes must be escaped with `html.escape()`.

### 8. Broken pagination
`blog.html` previously had pagination with a non-existent `changePage()` function. All posts should be shown and filtered client-side via the category JS.

---

## Navbar Consistency

The navbar HTML, CSS, and JS are **identical** across:
- `index.html` (homepage)
- `blog.html` (blog listing)
- `blog/*/index.html` (individual posts)

The navbar consists of:
1. **Inline `<style>` block** — Contains all navbar CSS (`.navbar`, `.nav-container`, `.nav-dropdown-menu`, `.mega-menu`, etc.)
2. **HTML structure** — Inside `<header><nav class="navbar">...</nav></header>`
3. **Inline `<script>` block** — `megaTabSwitch()`, `toggleMobileMenu()`, `toggleMobileSection()`, scroll effect, mobile menu listeners

When updating the navbar, change ALL files.

---

## TOC Highlighting

`blog/blog.js` handles TOC scroll highlighting via Intersection Observer.
- Requires `<article>` to contain `<h2 id="...">` elements
- Requires `.toc-list a[href="#..."]` to match the h2 ids
- Active class `.active` is added/removed on scroll

---

## Quick Reference: File Counts

Run this to verify integrity:

```bash
echo "Post folders: $(ls -d blog/*/index.html | wc -l)"
echo "Posts in JSON: $(python3 -c 'import json; print(len(json.load(open(\"blog/posts-index.json\"))))')"
echo "Cards in blog.html: $(grep -c 'class=\"blog-card\"' blog.html)"
echo "Cards in blog/index.html: $(grep -c 'class=\"post-card\"' blog/index.html)"
echo "Sitemap entries: $(grep -c 'blog/' sitemap.xml)"
echo "Author links: $(grep -rl 'author/zeeshan-waheed.*target=\"_blank\"' blog/*/index.html | wc -l)"
```

All numbers should match.
