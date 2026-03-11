#!/usr/bin/env python3
"""Build Batch 2 blog posts (101-200) for imisofts.com"""

import os
import re
import json
import html as html_mod
import math

# === CONFIGURATION ===
SOURCE_DIR = "Blogpost research"
BLOG_DIR = "blog"
POSTS_INDEX = "blog/posts-index.json"
BLOG_HTML = "blog.html"
BLOG_INDEX_HTML = "blog/index.html"
SITEMAP = "sitemap.xml"

# Category mapping from Batch 2 labels to standard 7 categories
CATEGORY_MAP = {
    "Category A: Tool Comparisons & Reviews": "Platform Guides & Tutorials",
    "Category B: Pricing & Cost Breakdowns": "Strategy & Benchmarks",
    "Category C: Original Data & Benchmarks": "Strategy & Benchmarks",
    "Category D: Industry Deep-Dives": "Industry-Specific Cold Email",
    "Category E: Country Legal Guides": "European B2B Cold Email",
    "Category F: Step-by-Step Tutorials": "Platform Guides & Tutorials",
    "Category G: Problem-Solution & Troubleshooting": "Cold Email Infrastructure",
    # Lowercase variants from some source files
    "Industry Deep-Dives": "Industry-Specific Cold Email",
    "Country Legal Guides": "European B2B Cold Email",
    "Step-by-Step Tutorials": "Platform Guides & Tutorials",
    "Problem-Solution & Troubleshooting": "Cold Email Infrastructure",
    "Tool Comparisons & Reviews": "Platform Guides & Tutorials",
    "Pricing & Cost Breakdowns": "Strategy & Benchmarks",
    "Original Data & Benchmarks": "Strategy & Benchmarks",
    # Quoted/shortened variants
    "Data & Benchmarks": "Strategy & Benchmarks",
    "Troubleshooting": "Cold Email Infrastructure",
    "How-To Tutorials": "Platform Guides & Tutorials",
    "Country Legal": "European B2B Cold Email",
    "Industry": "Industry-Specific Cold Email",
}

GRADIENTS = {
    "Cold Email Infrastructure": ("linear-gradient(135deg, #F26522, #E55A1B)", "COLD EMAIL INFRASTRUCTURE"),
    "Industry-Specific Cold Email": ("linear-gradient(135deg, #1E3A5F, #2C5282)", "INDUSTRY-SPECIFIC COLD EMAIL"),
    "B2B Lead Gen & Outreach": ("linear-gradient(135deg, #059669, #047857)", "B2B LEAD GEN & OUTREACH"),
    "Email Copywriting & Sequences": ("linear-gradient(135deg, #7C3AED, #6D28D9)", "EMAIL COPYWRITING & SEQUENCES"),
    "European B2B Cold Email": ("linear-gradient(135deg, #0D9488, #0F766E)", "EUROPEAN B2B COLD EMAIL"),
    "Platform Guides & Tutorials": ("linear-gradient(135deg, #374151, #1F2937)", "PLATFORM GUIDES & TUTORIALS"),
    "Strategy & Benchmarks": ("linear-gradient(135deg, #DC2626, #B91C1C)", "STRATEGY & BENCHMARKS"),
}

CATEGORY_SLUGS = {
    "Cold Email Infrastructure": "cold-email-infrastructure",
    "Industry-Specific Cold Email": "industry-specific-cold-email",
    "B2B Lead Gen & Outreach": "b2b-lead-gen-outreach",
    "Email Copywriting & Sequences": "email-copywriting-sequences",
    "European B2B Cold Email": "european-b2b-cold-email",
    "Platform Guides & Tutorials": "platform-guides-tutorials",
    "Strategy & Benchmarks": "strategy-benchmarks",
}

# Affiliate links
AFFILIATE_LINKS = {
    "instantly": ("https://instantly.ai/?via=coldemailmarketing", 'rel="noopener noreferrer sponsored"'),
    "smartlead": ("https://smartlead.ai/?via=coldemailmarketing", 'rel="noopener noreferrer sponsored"'),
    "apollo": ("https://get.apollo.io/u5ocuv7me9t2", 'rel="noopener noreferrer sponsored"'),
    "upfirst": ("https://app.upfirst.ai/sign-up?plid=30314", 'rel="noopener noreferrer sponsored"'),
}

MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
           7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def parse_source_file(filepath):
    """Parse a source .txt file and extract frontmatter + content + FAQs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract YAML frontmatter
    fm = {}
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        content_start = fm_match.end()
        # Parse simple YAML (supports both UPPERCASE and lowercase keys)
        current_key = None
        current_list = []
        for line in fm_text.split('\n'):
            line = line.rstrip()
            # Match any key: value line (uppercase or lowercase)
            key_match = re.match(r'^([A-Za-z_]+)\s*:', line)
            if key_match:
                if current_key and current_list:
                    fm[current_key] = current_list
                    current_list = []
                key, _, val = line.partition(':')
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                # Normalize lowercase keys to uppercase
                key_upper = key.upper()
                # Map common lowercase keys
                key_map = {
                    'TITLE': 'TITLE', 'SLUG': 'URL_SLUG',
                    'URL_SLUG': 'URL_SLUG', 'CATEGORY': 'CATEGORY',
                    'DATE': 'DATE', 'DATE_PUBLISHED': 'DATE',
                    'AUTHOR': 'AUTHOR', 'META_DESCRIPTION': 'META_DESCRIPTION',
                    'WORD_COUNT': 'WORD_COUNT_TARGET', 'WORD_COUNT_TARGET': 'WORD_COUNT_TARGET',
                    'SCHEMA_TYPE': 'SCHEMA_TYPE', 'SEO_TITLE': 'SEO_TITLE',
                    'PRIMARY_KEYWORD': 'PRIMARY_KEYWORD',
                    'SECONDARY_KEYWORDS': 'SECONDARY_KEYWORDS',
                    'LLM_CITATION_PRIORITY': 'LLM_CITATION_PRIORITY',
                    'BATCH': 'BATCH', 'POST_NUMBER': 'POST_NUMBER',
                }
                normalized_key = key_map.get(key_upper, key_upper)
                current_key = normalized_key
                if val:
                    # Handle JSON array syntax like ["item1", "item2"]
                    if val.startswith('[') and val.endswith(']'):
                        try:
                            import ast
                            parsed = ast.literal_eval(val)
                            if isinstance(parsed, list):
                                fm[normalized_key] = ', '.join(str(x) for x in parsed)
                            else:
                                fm[normalized_key] = val
                        except:
                            fm[normalized_key] = val.strip('[]').replace('"', '').replace("'", '')
                    else:
                        fm[normalized_key] = val
                else:
                    current_list = []
            elif line.strip().startswith('- ') and current_key:
                current_list.append(line.strip()[2:].strip('"').strip("'"))
        if current_key and current_list:
            fm[current_key] = current_list
    else:
        content_start = 0

    remaining = text[content_start:]

    # Extract FAQ section
    faqs = []
    faq_pattern = re.findall(r'\*\*Q:\s*(.*?)\*\*\s*\n\s*A:\s*(.*?)(?=\n\n|\n\*\*Q:|\n---|\nINTERNAL|\nEXTERNAL|\nIMAGE|\nQUICK|$)', remaining, re.DOTALL)
    for q, a in faq_pattern:
        faqs.append({"question": q.strip(), "answer": a.strip()})

    # Also check for FAQ_SCHEMA section at bottom
    faq_schema_match = re.findall(r'Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\n---|$)', remaining, re.DOTALL)
    if faq_schema_match and not faqs:
        for q, a in faq_schema_match:
            q = q.strip()
            a = a.strip()
            if q and a and len(a) > 20:
                faqs.append({"question": q, "answer": a})

    # Extract QUICK_ANSWER
    quick_answer = ""
    qa_match = re.search(r'QUICK_ANSWER:\s*(.*?)(?=\n[A-Z_]+:|$)', remaining, re.DOTALL)
    if qa_match:
        quick_answer = qa_match.group(1).strip()

    # Extract main content (from # heading to FAQ or INTERNAL_LINKS)
    content_end_markers = ['## FAQ_SCHEMA:', '---\nFAQ_SCHEMA:', 'INTERNAL_LINKS:', 'EXTERNAL_LINKS:', 'IMAGE_ALT_SUGGESTIONS:', 'QUICK_ANSWER:', 'internal_links:', 'external_links:', 'image_alt_suggestions:', 'quick_answer:']
    content = remaining
    for marker in content_end_markers:
        idx = content.find(marker)
        if idx > 0:
            content = content[:idx]

    # Remove trailing --- lines
    content = re.sub(r'\n---\s*$', '', content.strip())

    return fm, content, faqs, quick_answer


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def markdown_to_html(md_text, existing_slugs=None):
    """Convert markdown content to HTML with proper h2 ids."""
    lines = md_text.split('\n')
    html_lines = []
    in_list = False
    in_ordered_list = False
    in_table = False
    in_blockquote = False
    table_rows = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip the main H1 (already in article header)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            i += 1
            continue

        # H2
        if stripped.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_ordered_list:
                html_lines.append('</ol>')
                in_ordered_list = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            heading_text = stripped[3:].strip()
            heading_id = slugify(heading_text)
            html_lines.append(f'<h2 id="{heading_id}">{inline_format(heading_text)}</h2>')
            i += 1
            continue

        # H3
        if stripped.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if in_ordered_list:
                html_lines.append('</ol>')
                in_ordered_list = False
            heading_text = stripped[4:].strip()
            html_lines.append(f'<h3>{inline_format(heading_text)}</h3>')
            i += 1
            continue

        # H4
        if stripped.startswith('#### '):
            heading_text = stripped[5:].strip()
            html_lines.append(f'<h4>{inline_format(heading_text)}</h4>')
            i += 1
            continue

        # Table detection
        if '|' in stripped and stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(stripped)
            i += 1
            # Check if next line is also table or end
            if i >= len(lines) or not (lines[i].strip().startswith('|') and lines[i].strip().endswith('|')):
                # End of table, render it
                html_lines.append(render_table(table_rows))
                in_table = False
                table_rows = []
            continue

        # Blockquote
        if stripped.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            bq_text = stripped[2:].strip()
            html_lines.append(f'<p>{inline_format(bq_text)}</p>')
            i += 1
            continue
        elif in_blockquote and stripped:
            html_lines.append('</blockquote>')
            in_blockquote = False

        # Unordered list
        if stripped.startswith('- ') or stripped.startswith('* '):
            if in_ordered_list:
                html_lines.append('</ol>')
                in_ordered_list = False
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            li_text = stripped[2:].strip()
            html_lines.append(f'<li>{inline_format(li_text)}</li>')
            i += 1
            continue
        elif in_list and (not stripped or not (stripped.startswith('- ') or stripped.startswith('* '))):
            html_lines.append('</ul>')
            in_list = False

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if ol_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            if not in_ordered_list:
                html_lines.append('<ol>')
                in_ordered_list = True
            li_text = ol_match.group(2).strip()
            html_lines.append(f'<li>{inline_format(li_text)}</li>')
            i += 1
            continue
        elif in_ordered_list and (not stripped or not re.match(r'^\d+\.', stripped)):
            html_lines.append('</ol>')
            in_ordered_list = False

        # Empty line
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == '---' or stripped == '***':
            i += 1
            continue

        # Regular paragraph
        html_lines.append(f'<p>{inline_format(stripped)}</p>')
        i += 1

    # Close any open lists
    if in_list:
        html_lines.append('</ul>')
    if in_ordered_list:
        html_lines.append('</ol>')
    if in_blockquote:
        html_lines.append('</blockquote>')

    return '\n'.join(html_lines)


def render_table(rows):
    """Render markdown table rows to HTML."""
    if len(rows) < 2:
        return ''

    html = ['<div style="overflow-x:auto;"><table>']

    # Header row
    headers = [cell.strip() for cell in rows[0].split('|')[1:-1]]
    html.append('<thead><tr>')
    for h in headers:
        html.append(f'<th>{inline_format(h)}</th>')
    html.append('</tr></thead>')

    # Body rows (skip separator row)
    html.append('<tbody>')
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.split('|')[1:-1]]
        html.append('<tr>')
        for c in cells:
            html.append(f'<td>{inline_format(c)}</td>')
        html.append('</tr>')
    html.append('</tbody></table></div>')

    return '\n'.join(html)


def inline_format(text):
    """Handle inline markdown formatting."""
    # Bold + Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Links - handle markdown links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: make_link(m.group(1), m.group(2)), text)

    return text


def make_link(text, url):
    """Create an anchor tag, applying affiliate links where appropriate."""
    # Fix double-paren URLs like ((/blog/...))
    url = url.strip('()')

    # Check for affiliate replacements
    url_lower = url.lower()
    for platform, (aff_url, aff_rel) in AFFILIATE_LINKS.items():
        if platform == "instantly" and ("instantly.ai" in url_lower or "instantly.ai" in url):
            return f'<a href="{aff_url}" target="_blank" {aff_rel}>{text}</a>'
        elif platform == "smartlead" and ("smartlead.ai" in url_lower or "smartlead.ai" in url):
            return f'<a href="{aff_url}" target="_blank" {aff_rel}>{text}</a>'
        elif platform == "apollo" and ("apollo.io" in url_lower or "get.apollo.io" in url_lower):
            return f'<a href="{aff_url}" target="_blank" {aff_rel}>{text}</a>'
        elif platform == "upfirst" and "upfirst" in url_lower:
            return f'<a href="{aff_url}" target="_blank" {aff_rel}>{text}</a>'

    # Internal links
    if url.startswith('/') or url.startswith('https://imisofts.com'):
        return f'<a href="{url}">{text}</a>'

    # External links
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'


def extract_h2s(md_text):
    """Extract H2 headings and their slugified IDs from markdown."""
    h2s = []
    for match in re.finditer(r'^## (.+)', md_text, re.MULTILINE):
        heading = match.group(1).strip()
        # Skip FAQ_SCHEMA header
        if heading.startswith('FAQ_SCHEMA') or heading.startswith('INTERNAL_LINKS') or heading.startswith('EXTERNAL_LINKS') or heading.startswith('IMAGE_ALT') or heading.startswith('QUICK_ANSWER'):
            continue
        h2s.append((slugify(heading), heading))
    return h2s


def format_date_display(date_str):
    """Convert YYYY-MM-DD to 'Month DD, YYYY'."""
    # Clean any quotes or whitespace
    date_str = date_str.strip().strip('"').strip("'")
    parts = date_str.split('-')
    year = parts[0].strip()
    month = int(parts[1].strip())
    day = int(re.sub(r'[^0-9]', '', parts[2]))
    return f"{MONTHS[month]} {day}, {year}"


def get_slug_from_frontmatter(fm):
    """Extract slug from frontmatter URL_SLUG field."""
    url_slug = fm.get('URL_SLUG', '')
    if url_slug:
        # Clean quotes and whitespace
        url_slug = url_slug.strip().strip('"').strip("'")
        # Remove /blog/ prefix if present
        slug = url_slug.strip('/').replace('blog/', '')
        return slug.strip('"').strip("'")
    return ''


def build_post_html(fm, content_html, h2s, faqs, quick_answer, slug, category, date_str, read_time, word_count, style_block, navbar_html, footer_html, script_block):
    """Build the complete blog post HTML page."""
    title = fm.get('TITLE', 'Untitled')
    meta_desc = fm.get('META_DESCRIPTION', '')[:160]
    schema_type = fm.get('SCHEMA_TYPE', 'Article')
    primary_kw = fm.get('PRIMARY_KEYWORD', '')
    secondary_kws = fm.get('SECONDARY_KEYWORDS', '')
    if isinstance(secondary_kws, list):
        secondary_kws = ', '.join(secondary_kws)
    all_keywords = f"{primary_kw}, {secondary_kws}" if secondary_kws else primary_kw

    title_escaped = html_mod.escape(title)
    meta_desc_escaped = html_mod.escape(meta_desc)
    cat_slug = CATEGORY_SLUGS.get(category, slugify(category))
    date_display = format_date_display(date_str)

    # Build TOC
    toc_items = '\n'.join([f'<li><a href="#{h2_id}">{inline_format(h2_text)}</a></li>' for h2_id, h2_text in h2s])

    # Build FAQ schema JSON-LD
    faq_schema = ""
    if faqs:
        faq_entities = []
        for faq in faqs[:5]:  # Max 5 FAQs
            faq_entities.append({
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"]
                }
            })
        faq_schema = f'''<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": {json.dumps(faq_entities, indent=4, ensure_ascii=False)}
}}
</script>'''

    # Build BlogPosting schema
    base_schema_type = "BlogPosting"
    if "HowTo" in str(schema_type):
        base_schema_type = "HowTo"

    blog_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": base_schema_type,
        "headline": title,
        "description": meta_desc,
        "author": {
            "@type": "Person",
            "name": "Zeeshan Waheed",
            "url": "https://imisofts.com/author/zeeshan-waheed/"
        },
        "publisher": {
            "@type": "Organization",
            "name": "imisofts",
            "url": "https://imisofts.com",
            "logo": {
                "@type": "ImageObject",
                "url": "https://imisofts.com/logo.svg"
            }
        },
        "datePublished": date_str,
        "dateModified": date_str,
        "url": f"https://imisofts.com/blog/{slug}/",
        "mainEntityOfPage": f"https://imisofts.com/blog/{slug}/",
        "wordCount": word_count,
        "keywords": all_keywords,
        "name": title
    }, indent=2, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://imisofts.com/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://imisofts.com/blog/"},
            {"@type": "ListItem", "position": 3, "name": category, "item": f"https://imisofts.com/blog/?cat={cat_slug}"},
            {"@type": "ListItem", "position": 4, "name": title}
        ]
    }, indent=2, ensure_ascii=False)

    # Build FAQ HTML section
    faq_html = ""
    if faqs:
        faq_items = []
        for faq in faqs[:5]:
            q_escaped = html_mod.escape(faq["question"])
            a_escaped = html_mod.escape(faq["answer"])
            faq_items.append(f'''<div class="faq-item">
<button class="faq-question" aria-expanded="false">
<h3>{q_escaped}</h3>
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
</button>
<div class="faq-answer">
<div class="faq-answer-inner">{a_escaped}</div>
</div>
</div>''')
        faq_html = f'''<section class="faq-section">
<h2 id="faq">Frequently Asked Questions</h2>
{''.join(faq_items)}
</section>'''

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_escaped} | imisofts</title>
<meta name="description" content="{meta_desc_escaped}">
<link rel="canonical" href="https://imisofts.com/blog/{slug}/">
<meta name="robots" content="max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta property="og:type" content="article">
<meta property="og:title" content="{title_escaped}">
<meta property="og:description" content="{meta_desc_escaped}">
<meta property="og:url" content="https://imisofts.com/blog/{slug}/">
<meta property="og:image" content="https://imisofts.com/og-image.jpg">
<meta property="og:site_name" content="imisofts">
<meta property="article:author" content="Zeeshan Waheed">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_escaped}">
<meta name="twitter:description" content="{meta_desc_escaped}">
<meta name="twitter:image" content="https://imisofts.com/og-image.jpg">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cg fill='%23F45407'%3E%3Ccircle cx='48' cy='170' r='18'/%3E%3Cpath d='M84,84 L136,84 L118,188 L66,188 Z'/%3E%3Cpath d='M146,84 L198,84 L180,188 L128,188 Z'/%3E%3C/g%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
{style_block}
<link rel="stylesheet" href="/blog/blog.css">
<script type="application/ld+json">
{blog_schema}
</script>
<script type="application/ld+json">
{breadcrumb_schema}
</script>
{faq_schema}
</head>
<body>
<a href="#main-content" class="skip-to-content">Skip to content</a>

{navbar_html}

<main id="main-content" class="blog-wrapper">
<div class="container">

<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span><a href="/blog/?cat={cat_slug}">{html_mod.escape(category)}</a><span>/</span><span class="current">{title_escaped}</span>
</nav>

<div class="article-header">
<h1>{title_escaped}</h1>
<div class="article-meta">
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
<a href="/author/zeeshan-waheed/" target="_blank" rel="noopener" style="color: #F45407; text-decoration: underline; font-weight: 500;">Zeeshan Waheed</a>
</div>
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
<time datetime="{date_str}">{date_display}</time>
</div>
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
{read_time} min read
</div>
<a href="/blog/?cat={cat_slug}" class="category-tag">{html_mod.escape(category)}</a>
</div>
</div>

<div class="mobile-toc">
<button class="mobile-toc-toggle" aria-expanded="false">
Table of Contents
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
</button>
<div class="mobile-toc-content">
<ul class="toc-list">
{toc_items}
</ul>
</div>
</div>

<div class="blog-content-layout">
<article class="article-content">
{content_html}
{faq_html}

<div class="blog-cta-banner">
<h2>Ready to scale your cold email infrastructure?</h2>
<p>See our packages and get started with a system built for deliverability.</p>
<a href="https://imisofts.com/cold-email-marketing#packages" class="cta-btn">
View Our Packages
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
</a>
</div>
</article>

<aside class="blog-sidebar">
<nav class="toc" aria-label="Table of contents">
<div class="toc-title">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"></path></svg>
Contents
</div>
<ul class="toc-list">
{toc_items}
</ul>
</nav>
<div class="sidebar-card">
<h3>Our Packages</h3>
<p>Cold email infrastructure built for deliverability. From 3 domains to 50+.</p>
<a href="https://imisofts.com/cold-email-marketing#packages" class="btn">View Packages</a>
</div>
<div class="sidebar-card">
<h3>Book a Call</h3>
<p>Get a free 30-minute strategy session with our team.</p>
<a href="https://cal.com/zeeshanwaheed/30min" target="_blank" rel="noopener noreferrer" class="btn btn-outline">Book Free Call</a>
</div>
</aside>
</div>

</div>
</main>

{footer_html}

{script_block}
<script src="/blog/blog.js" defer></script>
</body>
</html>'''

    return page


def apply_affiliate_links(html_text):
    """Replace any remaining direct platform URLs with affiliate URLs in HTML."""
    # Replace direct URLs that aren't already affiliate
    replacements = [
        (r'href="https?://instantly\.ai(?!/\?via)/?[^"]*"', f'href="{AFFILIATE_LINKS["instantly"][0]}" target="_blank" {AFFILIATE_LINKS["instantly"][1]}'),
        (r'href="https?://(?:www\.)?smartlead\.ai(?!/\?via)/?[^"]*"', f'href="{AFFILIATE_LINKS["smartlead"][0]}" target="_blank" {AFFILIATE_LINKS["smartlead"][1]}'),
        (r'href="https?://(?:www\.)?apollo\.io/?[^"]*"', f'href="{AFFILIATE_LINKS["apollo"][0]}" target="_blank" {AFFILIATE_LINKS["apollo"][1]}'),
        (r'href="https?://get\.apollo\.io/?[^"]*"', f'href="{AFFILIATE_LINKS["apollo"][0]}" target="_blank" {AFFILIATE_LINKS["apollo"][1]}'),
    ]
    for pattern, replacement in replacements:
        html_text = re.sub(pattern, replacement, html_text)
    return html_text


def generate_blog_card(slug, title, meta_desc, category, date_str, read_time):
    """Generate blog.html card (.blog-card format)."""
    gradient, cat_label = GRADIENTS.get(category, GRADIENTS["Cold Email Infrastructure"])
    title_escaped = html_mod.escape(title)
    desc_escaped = html_mod.escape(meta_desc)

    return f'''        <article class="blog-card">
          <div class="blog-card-image" style="background: {gradient}; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 20px; text-align: center; position: relative;">
            <span style="font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: rgba(255,255,255,0.7); margin-bottom: 8px;">{cat_label}</span>
            <span style="font-size: 14px; font-weight: 700; color: white; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{title_escaped}</span>
            <span style="position: absolute; bottom: 8px; right: 12px; font-size: 9px; color: rgba(255,255,255,0.5); font-weight: 500;">imisofts.com</span>
          </div>
          <div class="blog-card-content">
            <span class="post-category">{cat_label}</span>
            <h3 class="blog-card-title">
              <a href="/blog/{slug}/">{title_escaped}</a>
            </h3>
            <p class="blog-card-excerpt">{desc_escaped}</p>
            <div class="blog-card-footer">
              <div class="author-info">
                <a href="/author/zeeshan-waheed/" target="_blank" rel="noopener" class="author-name" style="color: #F45407; text-decoration: underline; font-weight: 500;">Zeeshan Waheed</a>
              </div>
              <div class="blog-card-meta-details">
                <span class="post-date">{date_str}</span>
                <span>{read_time} min read</span>
              </div>
            </div>
          </div>
        </article>'''


def generate_post_card(slug, title, meta_desc, category, date_str, read_time, keywords_str):
    """Generate blog/index.html card (.post-card format)."""
    gradient, cat_label = GRADIENTS.get(category, GRADIENTS["Cold Email Infrastructure"])
    title_escaped = html_mod.escape(title)
    title_attr = html_mod.escape(title)
    desc_escaped = html_mod.escape(meta_desc)
    cat_escaped = html_mod.escape(category)

    return f'''<a href="/blog/{slug}/" class="post-card" data-category="{cat_escaped}" data-title="{title_attr}" data-keywords="{html_mod.escape(keywords_str)}">
<div class="card-thumbnail" style="background: {gradient};"><span class="card-thumb-cat">{category}</span><span class="card-thumb-title">{title}</span><span class="card-thumb-brand">imisofts.com</span></div>
<div class="card-category">{cat_escaped}</div>
<h2>{title_escaped}</h2>
<p class="card-excerpt">{desc_escaped}</p>
<div class="card-footer">
<span>{date_str}</span>
<span>{read_time} min read</span>
</div>
</a>'''


def main():
    # Load existing posts-index.json
    with open(POSTS_INDEX, 'r', encoding='utf-8') as f:
        posts_index = json.load(f)

    existing_slugs = set()
    for p in posts_index:
        existing_slugs.add(p.get('slug', ''))

    # Extract template parts from existing post
    template_path = "blog/cold-email-infrastructure-setup/index.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Extract style block (between <style> and </style>)
    style_match = re.search(r'(<style>.*?</style>)', template, re.DOTALL)
    style_block = style_match.group(1) if style_match else ""

    # Extract navbar (from <header> to </header> including mobile menu)
    navbar_match = re.search(r'(<header>.*?</header>)', template, re.DOTALL)
    # Actually need from <header> through closing </nav>\n  </header>
    navbar_start = template.find('<header>')
    navbar_end = template.find('</header>') + len('</header>')
    navbar_html = template[navbar_start:navbar_end]

    # Extract footer
    footer_start = template.find('<footer')
    footer_end = template.find('</footer>') + len('</footer>')
    footer_html = template[footer_start:footer_end]

    # Extract script block
    script_start = template.find('<script>\n    // Mega-menu')
    script_end = template.find('</script>\n<script src="/blog/blog.js"') + len('</script>')
    script_block = template[script_start:script_end]

    # Read blog.html and blog/index.html for card insertion points
    with open(BLOG_HTML, 'r', encoding='utf-8') as f:
        blog_html_content = f.read()

    with open(BLOG_INDEX_HTML, 'r', encoding='utf-8') as f:
        blog_index_content = f.read()

    # Read sitemap
    with open(SITEMAP, 'r', encoding='utf-8') as f:
        sitemap_content = f.read()

    # Collect all new cards and sitemap entries
    new_blog_cards = []
    new_post_cards = []
    new_sitemap_entries = []
    new_posts_index = []

    # Process each Batch 2 source file
    source_files = sorted([f for f in os.listdir(SOURCE_DIR) if re.match(r'^1\d{2}-|^200-', f) and f.endswith('.txt')])

    print(f"Processing {len(source_files)} source files...")

    for src_file in source_files:
        filepath = os.path.join(SOURCE_DIR, src_file)
        post_num = int(re.match(r'^(\d+)-', src_file).group(1))

        fm, content, faqs, quick_answer = parse_source_file(filepath)

        title = fm.get('TITLE', 'Untitled')
        meta_desc = fm.get('META_DESCRIPTION', '')[:160]
        date_str = fm.get('DATE', '2026-03-15').strip().strip('"').strip("'")
        slug = get_slug_from_frontmatter(fm)
        if not slug:
            slug = slugify(title)

        # Map category
        raw_cat = fm.get('CATEGORY', '')
        category = CATEGORY_MAP.get(raw_cat, raw_cat)
        if category not in GRADIENTS:
            # Try to find a match
            for std_cat in GRADIENTS:
                if std_cat.lower() in raw_cat.lower():
                    category = std_cat
                    break
            else:
                category = "Cold Email Infrastructure"  # default

        # Get keywords
        primary_kw = fm.get('PRIMARY_KEYWORD', '')
        secondary_kws = fm.get('SECONDARY_KEYWORDS', '')
        if isinstance(secondary_kws, list):
            keywords_list = [primary_kw] + secondary_kws
            keywords_str = primary_kw + ' ' + ', '.join(secondary_kws)
        else:
            keywords_list = [kw.strip() for kw in f"{primary_kw}, {secondary_kws}".split(',') if kw.strip()]
            keywords_str = f"{primary_kw} {secondary_kws}"

        # Word count and read time
        word_count = len(content.split())
        read_time = max(1, math.ceil(word_count / 200))

        # Skip if slug already exists
        if slug in existing_slugs:
            print(f"  SKIP #{post_num}: {slug} (already exists)")
            continue

        # Extract H2s from content
        h2s = extract_h2s(content)
        # Add FAQ h2 if we have FAQs
        if faqs:
            h2s.append(("faq", "Frequently Asked Questions"))

        # Convert markdown to HTML
        content_html = markdown_to_html(content, existing_slugs)

        # Apply affiliate links
        content_html = apply_affiliate_links(content_html)

        # Build full HTML page
        page_html = build_post_html(
            fm, content_html, h2s, faqs, quick_answer, slug, category,
            date_str, read_time, word_count, style_block, navbar_html,
            footer_html, script_block
        )

        # Apply affiliate links to full page
        page_html = apply_affiliate_links(page_html)

        # Create directory and write file
        post_dir = os.path.join(BLOG_DIR, slug)
        os.makedirs(post_dir, exist_ok=True)
        with open(os.path.join(post_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(page_html)

        # Add to posts-index
        new_entry = {
            "number": len(posts_index) + len(new_posts_index) + 1,
            "filename": src_file,
            "title": title,
            "meta_description": meta_desc,
            "url_slug": f"/blog/{slug}",
            "primary_keyword": primary_kw,
            "secondary_keywords": secondary_kws if isinstance(secondary_kws, str) else ', '.join(secondary_kws),
            "category": category,
            "word_count_target": fm.get('WORD_COUNT_TARGET', str(word_count)),
            "schema_type": fm.get('SCHEMA_TYPE', 'Article'),
            "author": "Zeeshan Waheed",
            "date": date_str,
            "slug": slug,
            "word_count": word_count,
            "read_time": read_time,
            "has_faq": len(faqs) > 0,
            "category_normalized": category
        }
        new_posts_index.append(new_entry)
        existing_slugs.add(slug)

        # Generate cards
        new_blog_cards.append(generate_blog_card(slug, title, meta_desc, category, date_str, read_time))
        new_post_cards.append(generate_post_card(slug, title, meta_desc, category, date_str, read_time, keywords_str))

        # Generate sitemap entry
        new_sitemap_entries.append(f'''<url>
<loc>https://imisofts.com/blog/{slug}/</loc>
<lastmod>{date_str}</lastmod>
<changefreq>monthly</changefreq>
<priority>0.7</priority>
</url>''')

        print(f"  OK #{post_num}: {slug} ({word_count} words, {read_time} min, {category})")

    # === Update posts-index.json ===
    posts_index.extend(new_posts_index)
    with open(POSTS_INDEX, 'w', encoding='utf-8') as f:
        json.dump(posts_index, f, indent=2, ensure_ascii=False)
    print(f"\nUpdated posts-index.json: {len(posts_index)} total entries")

    # === Update blog.html ===
    # Insert new cards before the closing </div> of blog-grid
    blog_grid_end = blog_html_content.rfind('</div>\n    </div>\n  </section>\n\n  <!-- Newsletter')
    if blog_grid_end == -1:
        # Try another pattern
        blog_grid_end = blog_html_content.rfind('      </div>\n    </div>\n  </section>')

    if blog_grid_end > 0:
        new_cards_html = '\n'.join(new_blog_cards)
        blog_html_content = blog_html_content[:blog_grid_end] + '\n' + new_cards_html + '\n' + blog_html_content[blog_grid_end:]
    else:
        print("WARNING: Could not find blog-grid insertion point in blog.html")
        # Fallback: find last </article> before </div>
        last_article = blog_html_content.rfind('</article>')
        if last_article > 0:
            insert_point = last_article + len('</article>')
            new_cards_html = '\n'.join(new_blog_cards)
            blog_html_content = blog_html_content[:insert_point] + '\n' + new_cards_html + blog_html_content[insert_point:]

    # Update category tab counts
    for cat_name, (_, cat_label) in GRADIENTS.items():
        count = sum(1 for p in posts_index if p.get('category_normalized', p.get('category', '')) == cat_name)
        # Update count in tab
        old_pattern = f'data-category="{cat_name}"[^>]*>\\s*{cat_name}\\s*<span[^>]*>\\d+</span>'
        # Simpler: just update All count

    with open(BLOG_HTML, 'w', encoding='utf-8') as f:
        f.write(blog_html_content)
    print(f"Updated blog.html with {len(new_blog_cards)} new cards")

    # === Update blog/index.html ===
    # Insert new cards before </div> closing of posts-grid
    posts_grid_end = blog_index_content.rfind('\n</div>\n\n</div>\n</main>')
    if posts_grid_end == -1:
        posts_grid_end = blog_index_content.rfind('\n</div>\n</div>\n</main>')
    if posts_grid_end == -1:
        # Find last </a> that's a post-card
        posts_grid_end = blog_index_content.rfind('</a>\n</div>')
        if posts_grid_end > 0:
            posts_grid_end = posts_grid_end + len('</a>')

    if posts_grid_end > 0:
        new_cards_html = '\n'.join(new_post_cards)
        blog_index_content = blog_index_content[:posts_grid_end] + '\n' + new_cards_html + blog_index_content[posts_grid_end:]
    else:
        print("WARNING: Could not find posts-grid insertion point in blog/index.html")

    with open(BLOG_INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(blog_index_content)
    print(f"Updated blog/index.html with {len(new_post_cards)} new cards")

    # === Update sitemap.xml ===
    sitemap_close = '</urlset>'
    new_sitemap_xml = '\n'.join(new_sitemap_entries)
    sitemap_content = sitemap_content.replace(sitemap_close, new_sitemap_xml + '\n' + sitemap_close)
    with open(SITEMAP, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"Updated sitemap.xml with {len(new_sitemap_entries)} new entries")

    # === Update category tab counts in blog.html ===
    with open(BLOG_HTML, 'r', encoding='utf-8') as f:
        blog_html_final = f.read()

    total_posts = len(posts_index)
    # Update "All" tab count
    blog_html_final = re.sub(
        r'(data-category="all"[^>]*>All\s*<span[^>]*>)\d+(</span>)',
        f'\\g<1>{total_posts}\\2',
        blog_html_final
    )

    # Update each category tab count
    for cat_name in GRADIENTS:
        count = sum(1 for p in posts_index if p.get('category_normalized', p.get('category', '')) == cat_name)
        escaped_cat = re.escape(html_mod.escape(cat_name))
        blog_html_final = re.sub(
            f'(data-category="{escaped_cat}"[^>]*>{escaped_cat}\\s*<span[^>]*>)\\d+(</span>)',
            f'\\g<1>{count}\\2',
            blog_html_final
        )

    with open(BLOG_HTML, 'w', encoding='utf-8') as f:
        f.write(blog_html_final)
    print("Updated category tab counts in blog.html")

    print(f"\n=== BUILD COMPLETE ===")
    print(f"New posts created: {len(new_posts_index)}")
    print(f"Total posts: {len(posts_index)}")


if __name__ == '__main__':
    main()
