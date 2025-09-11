# imisofts — Master Prompt for Claude Code (Blog System)

> Save this file as `/ops/blog_master_prompt.md`. **Before creating any post, always read and follow this file.**
> Site is custom static (HTML/CSS/JS), no CMS.

## CORE GOALS

* Research a **trending AI topic (last 14 days)** and write a **human, concise** post (≤1000 words; **no em dashes in body**).
* Create a **fully SEO-optimized** post page and **link it on the Blog index**.
* Generate a **branded cover image** (SVG with centered text) and **export PNG** for social cards + **create index thumbnails** (WebP + PNG fallback).
* Update all **technical SEO assets** (schema, sitemap, feed, internal links).
* Keep **header & footer exactly identical** to homepage (strict parity + diff check).
* Ship **modern, fast UI/UX** for blog index and post pages.

## BRAND / PATHS (override if different)

* `BRAND_NAME`: imisofts
* `BASE_URL`: [https://imisofts.com](https://imisofts.com)
* `BLOG_INDEX`: /blog/index.html
* `POSTS_DIR`: /blog/
* `SERVICES_URL`: /ai-automation/
* `CONTACT_URL`: /contact/
* `BRAND_HEX`: #F45407
* `ASSETS_OG_DIR`: /assets/og/
* `THUMB_DIR`: /assets/blog/thumbs/
* `AUTHOR`: Zeeshan Waheed (Founder & CEO)
* `AUTHOR_IMAGE`: [https://cdn.shopify.com/s/files/1/0780/0376/5469/files/zeeshan-waheed-thumb.jpg?v=1757561134](https://cdn.shopify.com/s/files/1/0780/0376/5469/files/zeeshan-waheed-thumb.jpg?v=1757561134)
* `AUTHOR_URL` (personal page): [https://imisofts.com/](https://imisofts.com/)
* `AUTHOR_LINKEDIN`: [https://www.linkedin.com/in/izeeshanwaheed/](https://www.linkedin.com/in/izeeshanwaheed/)
* `AUTHOR_CALENDLY`: [https://calendly.com/izeeshanwaheed/30mins](https://calendly.com/izeeshanwaheed/30mins)

## SITE CHROME (STRICT)

* **Header & Footer Parity:** copy the homepage `/index.html` header and footer **1:1** (markup, classes, scripts, data-attrs).
* Run an **automated diff** (ignore whitespace) between the post page header/footer and `/index.html`. If mismatch, **fix then re-run**.

## RESEARCH (must browse first)

1. Browse for a **fresh, trending AI topic** from the **last 14 days** with practical value for founders/marketers/SMBs.
2. Collect **3–5 authoritative sources** (official docs, reputable news).
3. Save titles + URLs to `/data/sources/SLUG.json`.

## CONTENT RULES

* **≤1000 words. No em dashes** in the body (use periods, commas, colons, parentheses).
* Human, direct tone. Short sentences. Use real stats or concrete examples when possible.
* Structure: **H1** → 2–3 line intro → **4–6 H2/H3 sections** → summary.
* **Internal links:** at least **two**, must include `SERVICES_URL` and `CONTACT_URL`.
* **CTAs:** one inline (contextual to `SERVICES_URL`), one final block (to `CONTACT_URL`).
* **External citations:** 2+ with natural anchor text.
* **Key Takeaways**: short bullet list.
* Include **one limitation/risk/trade-off**.

### Visible Byline & Author Box

* Byline near top:
  `By Zeeshan Waheed · <time datetime="YYYY-MM-DD">DATE</time> · ~X min read` (X = words/200, round up).
* **Author box** (after article, before footer) — use this HTML (update only text as needed):

```html
<div class="container">
  <section class="author-box" style="max-width: 780px; margin: 48px auto; padding: 32px; background: #f9fafb; border-radius:16px; border-left:6px solid #F45407;">
    <div style="display:flex; align-items:flex-start; gap:20px;">
      <a href="https://imisofts.com/" style="display:inline-block" aria-label="Author: Zeeshan Waheed">
        <img src="https://cdn.shopify.com/s/files/1/0780/0376/5469/files/zeeshan-waheed-thumb.jpg?v=1757561134"
             alt="Zeeshan Waheed, Founder & CEO at imisofts" width="80" height="80" loading="lazy"
             style="border-radius:50%; object-fit:cover; flex-shrink:0;">
      </a>
      <div style="flex:1;">
        <h3 style="font-size:20px; font-weight:600; margin:0 0 12px; color:#1a1a1a;">About the author</h3>
        <p style="margin:0 0 16px; font-size:15px; line-height:1.6; color:#4a5568;">
          Zeeshan Waheed is the Founder &amp; CEO at imisofts. He builds AI-powered outreach systems, Shopify experiences, and automation stacks for SMBs, startups, and agencies across the GCC and US.
        </p>
        <div style="display:flex; align-items:center; gap:16px; flex-wrap:wrap;">
          <a href="/ai-automation/" style="color:#F45407; text-decoration:none; font-weight:500; font-size:14px;">See how we can help →</a>
          <a href="https://calendly.com/izeeshanwaheed/30mins" target="_blank" rel="noopener" style="color:#F45407; text-decoration:none; font-weight:500; font-size:14px;">Contact Zeeshan →</a>
          <a href="https://www.linkedin.com/in/izeeshanwaheed/" target="_blank" rel="noopener" style="display:flex; align-items:center; gap:6px; color:#F45407; text-decoration:none; font-weight:500; font-size:14px;">
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452z"/></svg>
            LinkedIn
          </a>
        </div>
      </div>
    </div>
  </section>
</div>
```

## UI/UX — BLOG INDEX PAGE

* Top area: page title + short subtitle ("Latest on AI, automation, and growth").
* **Each post card must display the author avatar** (circle) and name, and **the avatar/name must hyperlink to `AUTHOR_URL`**.
* Featured newest post at top; responsive grid (1→2→3 cols), thumbnails via `<picture>` (WebP + PNG fallback).
* Card meta: date + reading time. Hover affordance.
* Lightweight client-side search over `/data/posts.json` (title, excerpt, tags).
* Pagination or "Load more" with accessible controls.
* **Ensure Blog index itself has proper `<title>`, meta description, canonical, and `ItemList` JSON-LD.**

### Card image snippet (use per new post)

```html
<picture>
  <source type="image/webp"
    srcset="/assets/blog/thumbs/SLUG-thumb-480.webp 480w, /assets/blog/thumbs/SLUG-thumb-960.webp 960w"
    sizes="(min-width:1024px) 360px, (min-width:640px) 50vw, 100vw">
  <img src="/assets/blog/thumbs/SLUG-thumb-480.png?v=YYYYMMDD"
       alt="POST_TITLE" width="480" height="270"
       loading="lazy" decoding="async" style="width:100%;height:auto;object-fit:cover;border-radius:12px;">
</picture>
<div class="card-meta">
  <a href="AUTHOR_URL" class="author-link" aria-label="About Zeeshan Waheed">
    <img src="AUTHOR_IMAGE" alt="Zeeshan Waheed" width="24" height="24" style="border-radius:50%; vertical-align:middle;">
    <span>Zeeshan Waheed</span>
  </a>
  <span>• DATE • ~X min read</span>
</div>
```

## UI/UX — SINGLE POST PAGE

* Reading progress bar (tiny, fixed) and ToC (auto from H2s; sticky on desktop).
* Media responsive; captions supported.
* End CTA block styled with brand gradient and **white text**:

```css
.final-cta{background:linear-gradient(135deg,#F45407,#ff6b28);color:#fff!important}
.final-cta h3,.final-cta p{color:#fff!important}
```

* "Updated on" date visible near the top.

## SEO & DISCOVER (in `<head>` of each post)

* `<title>` ≤ 60 chars with primary keyword near front.
* `<meta name="description">` 150–160 chars (action-oriented).
* `<link rel="canonical" href="BASE_URL/blog/SLUG/">`
* `<link rel="alternate" type="application/rss+xml" title="imisofts Blog Feed" href="/feed.xml">`
* Robots: `index,follow,max-image-preview:large`
* **OG/Twitter** (use PNG path):

```
og:type=article
og:title=POST_TITLE
og:description=META_DESCRIPTION
og:url=BASE_URL/blog/SLUG/
og:image=BASE_URL/assets/og/SLUG-YYYYMMDD.png
og:image:alt='Cover image for "POST_TITLE" — imisofts'
twitter:card=summary_large_image
article:published_time=YYYY-MM-DDTHH:MM:SS+05:00
article:modified_time=YYYY-MM-DDTHH:MM:SS+05:00
```

### JSON-LD (BlogPosting + BreadcrumbList)

Include: headline, description, inLanguage `"en"`, mainEntityOfPage, dates, `author` as **Person** with `sameAs` (LinkedIn) and headshot, `publisher` Organization + logo, `image` as ImageObject `{url,width:1200,height:630}`, `about` + `keywords` arrays. Add `BreadcrumbList`. Add `FAQPage` if 2–4 Q&As used.

## COVER IMAGE (SVG + PNG) — **Centered Text**

* Always generate a **1200×630** SVG cover using brand colors and **centered** title text.
* **Centering rules:**

  * Text must be visually **centered** horizontally and vertically within a safe area.
  * Use `text-anchor="middle"` with `x="600"` and baseline medians (e.g., `y="315"` with line stacking via `<tspan>`).
  * Wrap title to **≤3 lines**; reduce font-size if needed to avoid overflow; side padding ~120px.
  * Add subtle gradient/pattern using `BRAND_HEX`; ensure WCAG AA contrast (white or near-white text).
  * Add small footer text `imisofts.com` centered at bottom.
* Save **SVG**: `ASSETS_OG_DIR/SLUG.svg`
* Rasterize to **PNG** 1200×630: `ASSETS_OG_DIR/SLUG-YYYYMMDD.png` (use PNG in OG/Twitter).
* **Alt text:** `Cover image for "POST_TITLE" — imisofts`.

**Minimal centered SVG skeleton (adapt at runtime):**

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F45407"/><stop offset="100%" stop-color="#eb3f00"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#g)"/>
  <g font-family="Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif" fill="#fff" text-anchor="middle">
    <text id="title" x="600" y="300" font-size="72" font-weight="700">
      <tspan x="600" dy="-36">POST TITLE LINE 1</tspan>
      <tspan x="600" dy="84">POST TITLE LINE 2</tspan>
      <tspan x="600" dy="84">POST TITLE LINE 3</tspan>
    </text>
    <text x="600" y="590" font-size="28" opacity="0.9">imisofts.com</text>
  </g>
</svg>
```

## BLOG THUMBNAILS (index cards)

* Generate from PNG cover:

  * `THUMB_DIR/SLUG-thumb-480.webp` (480×270)
  * `THUMB_DIR/SLUG-thumb-960.webp` (960×540)
  * PNG fallback: `THUMB_DIR/SLUG-thumb-480.png`
* Use the `<picture>` block in cards; append `?v=YYYYMMDD` to bust caches.

## INTERNAL LINKING THAT COMPOUNDS

* Add a **Related reading** block (2–3 internal links).
* **Retro-link** at least two older posts to the new post with a contextual sentence.
* Maintain `/data/posts.json` registry `{slug,title,date,keywords}` for filters/dedupe. If slug/title similarity > 0.8, append `-YYYYMMDD`.

## FILES TO CREATE/UPDATE

* `POSTS_DIR/SLUG/index.html` — exact header/footer, article content, ToC, progress bar, author byline/box, CTAs, SEO meta, JSON-LD, cover image references.
* `BLOG_INDEX` — add **new post card at top**; include author avatar + name linking to `AUTHOR_URL`; update page `<title>`, meta; maintain `ItemList` JSON-LD.
* `/sitemap.xml` — add post URL with `<lastmod>`; update Blog index `<lastmod>`.
* `/feed.xml` — append item with title, link, pubDate, ≤200-char excerpt, stable `guid = canonical URL` (create file if missing).
* `/robots.txt` — ensure `Sitemap: BASE_URL/sitemap.xml`.
* `ASSETS_OG_DIR/SLUG.svg` + `ASSETS_OG_DIR/SLUG-YYYYMMDD.png` (cover).
* `THUMB_DIR` thumbnails (WebP + PNG).
* `/data/sources/SLUG.json` (sources).
* `/data/posts.json` registry (create if missing).

## IMPLEMENTATION STEPS

1. **Browse** topic → choose 3–5 sources → save `/data/sources/SLUG.json`.
2. **Draft** post (≤1000 words, **no em dashes**). Add internal links, CTAs, Key Takeaways, limitation/risk.
3. **Generate** centered SVG cover → **export** PNG → generate thumbnails.
4. **Build** `POSTS_DIR/SLUG/index.html` with exact header/footer; add ToC, progress bar, byline, author box.
5. **Update** Blog index card (thumbnail, excerpt, date, read time, **author avatar + link to AUTHOR_URL**).
6. **Update** sitemap.xml, feed.xml; update `/data/posts.json`; do retro-linking.
7. **Validate**: parity diff passes; no broken links (HTTP 200); all metas present; JSON-LD valid; OG/Twitter use PNG; thumbnails load; CLS safe (explicit image sizes); **body ≤1000 words; no em dashes.**
8. **Commit**: `feat(blog): publish "<Post Title>" + SEO, cover/thumbs, sitemap, feed, parity, UX`.

## OUTPUT (print this deploy checklist)

* Post URL
* Title + meta description
* Sources (list)
* Confirmations:

  * Blog index updated **with author image + link to AUTHOR_URL**
  * Sitemap + feed updated
  * **SVG + PNG** cover generated (**centered text**)
  * JSON-LD valid (BlogPosting, BreadcrumbList)
  * Internal links + CTAs present
  * ToC + progress bar present
  * Header/footer parity confirmed (diff OK)
  * Word count ≤1000 and **no em dashes** ✅

---

**Hard constraints:**

* Post body **≤1000 words**.
* **No em dashes anywhere in the body.**
* **Cover image title text must be centered** (not too left or right).
* **Author image shown on Blog index page** and **hyperlinked to the Author personal page (`AUTHOR_URL`)**.