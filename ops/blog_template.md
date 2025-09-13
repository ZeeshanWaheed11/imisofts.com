# imisofts Blog Post Template & Requirements

## CRITICAL: Use this template for ALL future blog posts

### Key Requirements Checklist:
- [ ] Navbar must be 100% identical to homepage (logo height: 58px, gap: 40px)
- [ ] Footer must be 100% identical to homepage (black background #0a0a0a, gray text #999)
- [ ] Author byline must link to `/author/zeeshan-waheed/` with orange color (#F45407) and underline
- [ ] Word count: ≤1000 words, no em dashes in body
- [ ] Cover image: SVG with centered text, export to PNG
- [ ] Affiliate links: Use provided tracking parameters
- [ ] Internal links: Must include at least 2 (services and contact pages)

### File Structure:
```
/blog/[slug]/index.html         - Main blog post
/assets/og/[slug].svg           - SVG cover image
/assets/og/[slug]-YYYYMMDD.png - PNG cover for social
/assets/blog/thumbs/[slug]-thumb-480.png  - Thumbnail
/assets/blog/thumbs/[slug]-thumb-960.png  - Large thumbnail
```

### Critical Style Values:

#### Navbar:
- Logo height: `58px` (NOT 36px)
- Nav menu gap: `40px` (NOT 32px)
- Dropdown menu: `min-width: 900px`, flexbox layout with grid and promo as columns
- Dropdown grid: `flex: 1`, `max-width: 560px`, `padding: 32px`
- Dropdown promo: `width: 340px`, includes animated SVG graphic
- Dropdown items hover: background `#f8f9fa`, icon gradient, title turns orange
- No borders or underlines on dropdown items

#### Footer:
- Background: `#0a0a0a` (pure black, NOT #0F172A)
- Grid: `2fr 1fr 1fr 1fr 1.5fr` (NOT equal columns)
- Text colors:
  - Main text: `#ccc`
  - Links/secondary: `#999` (NOT white)
  - Headings: `white`
  - Copyright: `#999`
- Social icons: `40x40px`, `border-radius: 10px`, `translateY(-3px)` on hover
- Footer links: `#999` color, `translateX(3px)` on hover
- Newsletter section: `rgba(255,255,255,0.05)` background
- Column headings: `14px`, uppercase, `letter-spacing: 0.5px`

#### Article Specific:
- Author byline format:
  ```html
  By <a href="/author/zeeshan-waheed/" style="color: #F45407; text-decoration: underline; font-weight: 500;">Zeeshan Waheed</a>
  ```
- Comparison tables: Use for platform comparisons
- Key takeaways: Green background box with bullet points
- CTAs: Inline CTA box + final gradient CTA
- Author box: After article, before footer (use exact HTML from template)

### Template HTML Structure:

See `/blog/instantly-vs-smartlead-comparison-2025/index.html` for the complete template.

Key sections to copy:
1. Complete `<head>` section with all meta tags
2. Entire navbar HTML (lines ~850-1100)
3. All CSS styles (lines ~130-800)
4. Footer HTML (lines ~1400-1524)
5. JavaScript for mobile menu, progress bar, ToC, newsletter

### Content Structure:
1. Introduction (2-3 paragraphs)
2. 4-6 H2 sections with content
3. Comparison table (if applicable)
4. Key takeaways box
5. Inline CTA
6. Conclusion
7. Final CTA
8. Author box

### Affiliate Link Integration:
- Always use provided tracking parameters
- Format: `https://platform.com/?via=trackingcode`
- Open in new tab with `target="_blank" rel="noopener"`

### SEO Requirements:
- Title: ≤60 chars
- Meta description: 150-160 chars
- Canonical URL
- Structured data: BlogPosting + BreadcrumbList
- OG/Twitter cards with PNG image
- Updated sitemap.xml
- Updated feed.xml
- Blog index update

### Common Mistakes to Avoid:
1. ❌ Using 36px logo height → ✅ Use 58px
2. ❌ White footer text → ✅ Use #999 for links/text
3. ❌ Equal footer columns → ✅ Use 2fr 1fr 1fr 1fr 1.5fr
4. ❌ Simple dropdown hover → ✅ Include all hover animations
5. ❌ Plain author name → ✅ Linked with orange color
6. ❌ Missing dropdown promo graphic → ✅ Include full SVG animation
7. ❌ Wrong footer background → ✅ Use #0a0a0a

### Files to Update for Each Post:
1. Create blog post HTML
2. Create SVG and PNG cover images
3. Generate thumbnails (480x270, 960x540)
4. Update `/blog.html` - Add post card at top
5. Update `/sitemap.xml` - Add URL with lastmod
6. Update `/feed.xml` - Add RSS entry
7. Update `/data/posts.json` (if exists)

### Testing Checklist:
- [ ] Navbar dropdown works with proper hover effects
- [ ] Logo is correct size (58px height)
- [ ] Footer text colors are gray (#999), not white
- [ ] Author name is linked and orange
- [ ] Mobile menu works
- [ ] Progress bar works
- [ ] Newsletter form works
- [ ] All internal links work
- [ ] Affiliate links have tracking parameters

---

**IMPORTANT**: Always refer to this template before creating any new blog post. The exact styling and structure must be maintained for consistency across the site.