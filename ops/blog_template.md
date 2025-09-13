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

### Content Structure for High-Converting Posts:
1. Introduction (2-3 paragraphs)
   - Include credibility metrics (e.g., "5M+ emails sent", "$12M+ pipeline managed")
   - Add Quick Answer Box for busy readers:
   ```html
   <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-left: 4px solid #0ea5e9; padding: 20px; border-radius: 8px; margin: 30px 0;">
     <p style="margin: 0; font-weight: 600; color: #0c4a6e;">⚡ Quick Answer for Busy Professionals:</p>
     <p style="margin: 10px 0 0 0; color: #334155;">[Quick answer here]</p>
   </div>
   ```

2. Real World Results section (if applicable) with data table
3. 4-6 H2 sections with content
4. Comparison table (if applicable)
5. Client Success Story box:
   ```html
   <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 30px 0;">
     <h4 style="margin: 0 0 12px 0; color: #065f46;">🎯 Real Client Example:</h4>
     <p style="margin: 0; color: #064e3b;">[Success story here]</p>
   </div>
   ```
6. Cost-Saving Tips (yellow box):
   ```html
   <div style="background: #fef3c7; border: 1px solid #fbbf24; padding: 16px; border-radius: 8px; margin: 20px 0;">
     <p style="margin: 0; font-weight: 600; color: #78350f;">💰 Cost-Saving Tip:</p>
     <p style="margin: 8px 0 0 0; color: #451a03;">[Tip here]</p>
   </div>
   ```
7. FAQ Section (for service comparison posts)
8. Key takeaways box
9. Inline CTA
10. Conclusion with proof points
11. Final CTA
12. Special Offer Box (if applicable):
    ```html
    <div style="background: #f8fafc; border: 2px dashed #e2e8f0; padding: 24px; border-radius: 12px; margin: 40px 0; text-align: center;">
      <p style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 16px;">🎯 Special Offer for Readers</p>
      <p style="color: #475569; margin-bottom: 20px;">[Offer description]</p>
      <div style="display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;">
        [CTA buttons here]
      </div>
    </div>
    ```
13. Author box

### Affiliate Link Integration:
- Always use provided tracking parameters
- Format: `https://platform.com/?via=trackingcode`
- Open in new tab with `target="_blank" rel="noopener"`

### SEO Requirements:
- Title: ≤60 chars (include specific metrics when possible, e.g., "94% Inbox Rate")
- Meta description: 150-160 chars (include data points and offers)
- Canonical URL
- Structured data: BlogPosting + BreadcrumbList
- OG/Twitter cards with PNG image
- Updated sitemap.xml with correct date
- Updated feed.xml with correct date
- Blog index update with:
  - New optimized title
  - New meta description
  - Remove "~X min read" if text overflows
  - Only show date (e.g., "Sep 14, 2025")

### Common Mistakes to Avoid:
1. ❌ Using 36px logo height → ✅ Use 58px
2. ❌ White footer text → ✅ Use #999 for links/text
3. ❌ Equal footer columns → ✅ Use 2fr 1fr 1fr 1fr 1.5fr
4. ❌ Simple dropdown hover → ✅ Include all hover animations
5. ❌ Plain author name → ✅ Linked with orange color
6. ❌ Missing dropdown promo graphic → ✅ Include full SVG animation
7. ❌ Wrong footer background → ✅ Use #0a0a0a
8. ❌ Dropdown items with orange underline on hover → ✅ No borders, use background color
9. ❌ Not updating blog.html title/description → ✅ Update with optimized versions
10. ❌ Including reading time that causes overflow → ✅ Remove if needed

### Files to Update for Each Post:
1. Create blog post HTML
2. Create SVG and PNG cover images
3. Generate thumbnails (480x270, 960x540)
4. Update `/blog.html` - Add post card at top
5. Update `/sitemap.xml` - Add URL with lastmod
6. Update `/feed.xml` - Add RSS entry
7. Update `/data/posts.json` (if exists)

### Testing Checklist:
- [ ] Navbar dropdown works with proper hover effects (no orange underlines)
- [ ] Logo is correct size (58px height)
- [ ] Footer ALL text colors are gray (#999), not white
- [ ] Author name is linked with orange color and underline
- [ ] Mobile menu works
- [ ] Progress bar works
- [ ] Newsletter form works
- [ ] All internal links work
- [ ] Affiliate links have tracking parameters
- [ ] Blog index card shows updated title and description
- [ ] Blog index card doesn't overflow (remove reading time if needed)
- [ ] Dropdown promo shows in column layout with SVG graphic

---

**IMPORTANT**: Always refer to this template before creating any new blog post. The exact styling and structure must be maintained for consistency across the site.

### For High-Converting Posts (Fiverr/Service Selling):
1. Use specific metrics in intro (5M+ emails, $12M+ pipeline)
2. Add "Quick Answer" box at the top
3. Include real performance data tables
4. Add client success stories with specific ROI numbers
5. Include FAQ section for common objections
6. Add special offer boxes with discount codes
7. Use multiple colored info boxes (blue for info, green for success, yellow for tips)
8. Bold important numbers and percentages
9. Use comparison tables with "Winner" badges
10. Include cost-saving tips to show expertise

### Copy Exact Styles From:
- Full blog post: `/blog/instantly-vs-smartlead-comparison-2025/index.html`
- CSS reference: `/ops/blog_styles.css`
- This template: `/ops/blog_template.md`