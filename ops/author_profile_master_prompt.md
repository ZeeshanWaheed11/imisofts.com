# Master Prompt — Author Profile Page (imisofts)

Save this file as `/ops/author_profile_master_prompt.md` and follow it every time you create or update the author page. Site is custom static (HTML/CSS/JS), no CMS.

## BRAND / PATHS (override if different)

* `BRAND_NAME`: imisofts
* `BASE_URL`: https://imisofts.com
* `HOMEPAGE`: /index.html
* `AUTHOR_SLUG`: zeeshan-waheed
* `AUTHOR_PAGE`: /author/zeeshan-waheed/index.html
* `BLOG_INDEX`: /blog/index.html
* `POSTS_DIR`: /blog/
* `SERVICES_URL`: /ai-automation/
* `CONTACT_URL`: /contact/
* `BRAND_HEX`: #F45407
* `ASSETS_IMG_DIR`: /assets/author/
* `AUTHOR_NAME`: Zeeshan Waheed
* `AUTHOR_TITLE`: Founder & CEO at imisofts
* `AUTHOR_IMAGE`: https://cdn.shopify.com/s/files/1/0780/0376/5469/files/zeeshan-waheed-thumb.jpg?v=1757561134
* `AUTHOR_URL`: https://imisofts.com/author/zeeshan-waheed/ (canonical for this page)
* `LINKEDIN_URL`: https://www.linkedin.com/in/izeeshanwaheed/
* `INSTAGRAM_URL`: https://www.instagram.com/izeeshanwaheed/
* `FIVERR_URL`: https://www.fiverr.com/impressive_zee?public_mode=true 
* `UPWORK_URL`: https://upwork.com/freelancers/izeeshanwaheed (update if needed)
* `Book_A_Meeting_URL`: https://cal.com/zeeshanwaheed/30min (or your GHL form iframe)

## HARD REQUIREMENTS

1. **Header & Footer Parity** — Copy the header and footer from `/index.html` 1:1 (same markup, classes, assets). Run an automated diff (ignore whitespace). If mismatch, fix.
2. **Fully Responsive** — Reuse existing site CSS/system. No layout shifts. Images have explicit width/height.
3. **Author Link Everywhere** —
   * Blog index cards: show circular avatar + name hyperlinking to `AUTHOR_PAGE`.
   * Single post byline + author box: link name & avatar to `AUTHOR_PAGE`.
4. **Strong SEO + AI Discoverability** — Titles, meta descriptions, canonical, OG/Twitter, JSON-LD (Person + WebPage + BreadcrumbList), internal links, sitemap.
5. **No third-party heavy JS widgets** beyond the form embed.

## PAGE STRUCTURE (minimum 5 sections)

Create `/author/zeeshan-waheed/index.html` with these sections between the copied header/footer:

1. **Hero / Identity**
   * Headshot (`AUTHOR_IMAGE`), name, `AUTHOR_TITLE`, short 2–3 line value prop.
   * Primary CTA buttons: Work with me → `SERVICES_URL`, Book a call → `FORM_URL`.
   * Social icon row (LinkedIn, Instagram, Fiverr, Upwork) with accessible labels.

2. **About Zeeshan**
   * 2–3 short paragraphs; highlight outcomes for SMBs, startups, agencies.
   * Bullet list: specialties (AI automation, cold email infra, Shopify, n8n, Instantly, Clay, Apollo, Pinecone).

3. **Expertise & Services**
   * 3–6 cards (AI Voice Agents, Cold Email Automation, LinkedIn Lead Gen, Shopify Design, AI Integrations).
   * Each card: 1-sentence benefit + "Learn more" linking to `SERVICES_URL`.

4. **Selected Results / Testimonials**
   * 3–4 results with metrics (e.g., booked meetings, open rates, installs).
   * Optional testimonial quotes (short, attributed).

5. **Resources & Latest Posts**
   * List 3–6 latest blog posts (title, date, read time).
   * Ensure each item links to its post and "See all posts" → `BLOG_INDEX`.

6. **Contact / Form**
   * Embed your form or Calendly (`FORM_URL`).
   * Secondary contact info. Privacy note.

Optional extras: Media & Talks, Certifications, FAQ (3–5 Q&As).

## SOCIAL ICONS (inline SVG — copy into buttons/links)

Use accessible links with SVGs (size 18–20, aria-label). Example:

```html
<a href="LINKEDIN_URL" target="_blank" rel="noopener" aria-label="LinkedIn">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" role="img"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452z"/></svg>
</a>
<!-- Repeat for Instagram, Fiverr, Upwork with their SVGs or simple text + icon -->
```

## SEO & AI DISCOVERABILITY (in `<head>`)

* `<title>`: "Zeeshan Waheed — Founder & CEO at imisofts | AI Automation, Shopify, Cold Email" (≤60 chars if possible).
* `<meta name="description">` (150–160 chars): action-oriented summary + services.
* Canonical: `<link rel="canonical" href="AUTHOR_URL">`
* **Open Graph / Twitter:**
  * `og:type=profile` or `website`, `og:title`, `og:description`, `og:url=AUTHOR_URL`, `og:image` (use `AUTHOR_IMAGE` or a 1200×630 cover), `twitter:card=summary_large_image`.
* **JSON-LD (include both):**
  1. **Person** with `@id = AUTHOR_URL#person`, name, jobTitle, image, url, worksFor (Organization imisofts), sameAs array (LinkedIn, Instagram, Fiverr, Upwork), knowsAbout (keywords), alumniOf (optional), hasOccupation (optional).
  2. **WebPage** with `@id = AUTHOR_URL`, name, isPartOf (WebSite), about referencing the Person @id, primaryImageOfPage, breadcrumbs.
* **BreadcrumbList**: Home → Author → Zeeshan Waheed.
* **Performance**: explicit image sizes, lazy-load below the fold, preconnect to fonts if used, defer non-critical JS.

## ACCESSIBILITY & UX

* Container widths: 72–76ch for long text; cards in responsive grid (1→2→3).
* Buttons: large hit targets; focus-visible outlines.
* Contrast: use `BRAND_HEX` for accents; ensure AA contrast.
* Animations (if any): reduce-motion friendly.

## INTERNAL LINKING

* Link from Blog index header and post bylines to `AUTHOR_PAGE`.
* From Author page, link back to `/ai-automation/`, `/contact/`, and `/blog/`.
* Add "Related resources" linking to cornerstone posts.

## TECHNICAL TASKS (do all)

1. **Create Author Page** at `AUTHOR_PAGE` with the sections above; reuse site classes; minimal new CSS.
2. **Header/Footer Parity**: copy from `/index.html`; run diff.
3. **Update Blog Index**: show author avatar + linked name on each card; ensure author link points to `AUTHOR_PAGE`.
4. **Update Single Post Template**: byline + author box link to `AUTHOR_PAGE`.
5. **Sitemap**: add `AUTHOR_URL` with `<lastmod>`; ensure `robots.txt` lists the sitemap.
6. **OG Image for Author page**: if not using headshot, generate a 1200×630 SVG/PNG cover with brand gradient and centered text "Zeeshan Waheed — imisofts".
7. **JSON-LD**: insert Person + WebPage + BreadcrumbList in the Author page head.
8. **Validate**: W3C HTML, Lighthouse (SEO ≥ 95), mobile-friendly, no console errors.

## SAMPLE AUTHOR HERO (drop into main container)

```html
<section class="author-hero" style="max-width:1100px;margin:48px auto;padding:0 20px;">
  <div style="display:grid;grid-template-columns:120px 1fr;gap:24px;align-items:center;">
    <img src="AUTHOR_IMAGE" alt="AUTHOR_NAME" width="120" height="120" style="border-radius:50%;object-fit:cover;">
    <div>
      <h1 style="margin:0 0 8px;font-size:36px;line-height:1.2;">AUTHOR_NAME</h1>
      <p style="margin:0 0 16px;color:#4a5568;">AUTHOR_TITLE. AI automation, Shopify, and outbound systems that drive pipeline.</p>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <a href="SERVICES_URL" class="btn" style="background:BRAND_HEX;color:#fff;padding:10px 16px;border-radius:10px;text-decoration:none;">Work with me</a>
        <a href="FORM_URL" class="btn" style="border:2px solid BRAND_HEX;color:BRAND_HEX;padding:8px 14px;border-radius:10px;text-decoration:none;">Book a call</a>
        <span style="flex:1"></span>
        <!-- Socials -->
        <a href="LINKEDIN_URL" aria-label="LinkedIn" target="_blank" rel="noopener" style="color:BRAND_HEX;">LinkedIn</a>
        <a href="INSTAGRAM_URL" aria-label="Instagram" target="_blank" rel="noopener" style="color:BRAND_HEX;">Instagram</a>
        <a href="FIVERR_URL" aria-label="Fiverr" target="_blank" rel="noopener" style="color:BRAND_HEX;">Fiverr</a>
        <a href="UPWORK_URL" aria-label="Upwork" target="_blank" rel="noopener" style="color:BRAND_HEX;">Upwork</a>
      </div>
    </div>
  </div>
</section>
```

## FORM EMBED (Calendly or GHL)

* **Calendly**: paste your inline embed or link button.
* **GHL (LeadConnector) iframe example:**
```html
<iframe src="FORM_URL" style="width:100%;height:780px;border:none;border-radius:12px" loading="lazy"></iframe>
```

## OUTPUT CHECKLIST (print after edits)

* Author page URL: `AUTHOR_URL`
* Header/Footer parity: PASS
* SEO: `<title>`, meta description, canonical, OG/Twitter set
* JSON-LD: Person + WebPage + BreadcrumbList valid
* Blog index: author avatar + name linking to `AUTHOR_PAGE`
* Post template: byline/author box link to `AUTHOR_PAGE`
* Sitemap updated (and robots points to it)
* Performance: mobile, CLS safe, lazy-loading ok
* Accessibility: alt text, focus outlines
* Lighthouse SEO ≥ 95

Now implement the page, update links across the blog, and commit: `feat(author): add Zeeshan Waheed author page, link from blog, SEO + schema + sitemap`