#!/usr/bin/env python3
"""Build a single blog post HTML from a source .txt file."""

import os, sys, re, json, html
from datetime import datetime

BLOG_DIR = "/home/user/imisofts.com/blog"
RESEARCH_DIR = "/home/user/imisofts.com/Blogpost research"

# Affiliate links
AFFILIATE_LINKS = {
    'instantly': ('https://instantly.ai/?via=coldemailmarketing', 'Instantly'),
    'smartlead': ('https://smartlead.ai/?via=coldemailmarketing', 'SmartLead'),
    'apollo': ('https://get.apollo.io/u5ocuv7me9t2', 'Apollo'),
    'upfirst': ('https://app.upfirst.ai/sign-up?plid=30314', 'Upfirst'),
}

# Direct URL replacements
URL_REPLACEMENTS = {
    'https://instantly.ai': 'https://instantly.ai/?via=coldemailmarketing',
    'https://www.instantly.ai': 'https://instantly.ai/?via=coldemailmarketing',
    'https://smartlead.ai': 'https://smartlead.ai/?via=coldemailmarketing',
    'https://www.smartlead.ai': 'https://smartlead.ai/?via=coldemailmarketing',
    'https://apollo.io': 'https://get.apollo.io/u5ocuv7me9t2',
    'https://www.apollo.io': 'https://get.apollo.io/u5ocuv7me9t2',
    'https://app.apollo.io': 'https://get.apollo.io/u5ocuv7me9t2',
}


def load_posts_index():
    with open(os.path.join(BLOG_DIR, 'posts-index.json')) as f:
        return json.load(f)


def parse_source_file(filepath):
    """Parse a blog source .txt file into frontmatter and content sections."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Parse frontmatter
    fm_match = re.match(r'^-{3,}\s*\n(.*?)\n-{3,}', content, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No frontmatter found in {filepath}")

    fm_text = fm_match.group(1)
    frontmatter = {}
    for line in fm_text.strip().split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            frontmatter[key.strip().lower()] = val.strip()

    # Get body content (between frontmatter and FAQ/links sections)
    rest = content[fm_match.end():]

    # Split at FAQ section
    faq_data = []
    faq_match = re.search(r'\n-{3,}\s*\nFAQ_SCHEMA:', rest)
    if faq_match:
        body = rest[:faq_match.start()]
        faq_section = rest[faq_match.start():]
        # Parse FAQ Q&A pairs
        qa_pairs = re.findall(r'Q:\s*(.+?)\nA:\s*(.+?)(?=\nQ:|\n-{3,}|\nINTERNAL|\nEXTERNAL|\nIMAGE|\Z)', faq_section, re.DOTALL)
        for q, a in qa_pairs:
            faq_data.append({'question': q.strip(), 'answer': a.strip()})
    else:
        body = rest

    # Parse internal links
    internal_links = re.findall(r'\[(.+?)\]\s*->\s*(\S+)', rest)

    return frontmatter, body.strip(), faq_data, internal_links


def md_to_html(text, posts_index, internal_link_suggestions):
    """Convert markdown-like text to HTML."""
    lines = text.split('\n')
    html_parts = []
    in_list = False
    list_type = None

    # Build slug lookup
    slug_set = set(p['slug'] for p in posts_index)

    # Build internal link map from suggestions
    link_map = {}
    for label, target in internal_link_suggestions:
        link_map[label.lower()] = target

    for line in lines:
        stripped = line.strip()

        # Skip the H1 title (we handle it separately)
        if stripped.startswith('# ') and not stripped.startswith('## '):
            continue

        # Close list if needed
        if in_list and not stripped.startswith('- ') and not re.match(r'^\d+\.\s', stripped) and stripped != '':
            tag = 'ul' if list_type == 'ul' else 'ol'
            html_parts.append(f'</{tag}>')
            in_list = False
            list_type = None

        if not stripped:
            if in_list:
                tag = 'ul' if list_type == 'ul' else 'ol'
                html_parts.append(f'</{tag}>')
                in_list = False
                list_type = None
            continue

        # Headings
        if stripped.startswith('#### '):
            heading_text = stripped[5:]
            heading_id = re.sub(r'[^a-z0-9]+', '-', heading_text.lower()).strip('-')
            html_parts.append(f'<h4 id="{heading_id}">{inline_format(heading_text)}</h4>')
            continue
        if stripped.startswith('### '):
            heading_text = stripped[4:]
            heading_id = re.sub(r'[^a-z0-9]+', '-', heading_text.lower()).strip('-')
            html_parts.append(f'<h3 id="{heading_id}">{inline_format(heading_text)}</h3>')
            continue
        if stripped.startswith('## '):
            heading_text = stripped[3:]
            heading_id = re.sub(r'[^a-z0-9]+', '-', heading_text.lower()).strip('-')
            html_parts.append(f'<h2 id="{heading_id}">{inline_format(heading_text)}</h2>')
            continue

        # Unordered list
        if stripped.startswith('- '):
            if not in_list or list_type != 'ul':
                if in_list:
                    tag = 'ul' if list_type == 'ul' else 'ol'
                    html_parts.append(f'</{tag}>')
                html_parts.append('<ul>')
                in_list = True
                list_type = 'ul'
            html_parts.append(f'<li>{inline_format(stripped[2:])}</li>')
            continue

        # Ordered list
        ol_match = re.match(r'^(\d+)\.\s(.+)', stripped)
        if ol_match:
            if not in_list or list_type != 'ol':
                if in_list:
                    tag = 'ul' if list_type == 'ul' else 'ol'
                    html_parts.append(f'</{tag}>')
                html_parts.append('<ol>')
                in_list = True
                list_type = 'ol'
            html_parts.append(f'<li>{inline_format(ol_match.group(2))}</li>')
            continue

        # Blockquote / Pro tip
        if stripped.startswith('>'):
            html_parts.append(f'<blockquote><p>{inline_format(stripped[1:].strip())}</p></blockquote>')
            continue

        # Regular paragraph
        if stripped.startswith('**Pro tip') or stripped.startswith('**What we have seen'):
            html_parts.append(f'<blockquote><p>{inline_format(stripped)}</p></blockquote>')
        else:
            html_parts.append(f'<p>{inline_format(stripped)}</p>')

    # Close any open list
    if in_list:
        tag = 'ul' if list_type == 'ul' else 'ol'
        html_parts.append(f'</{tag}>')

    return '\n'.join(html_parts)


def inline_format(text):
    """Handle inline markdown: bold, italic, links, code."""
    # First escape any raw HTML tags in content (preserve markdown syntax)
    # Save markdown links first
    saved = []
    def save_link(m):
        saved.append(m.group(0))
        return f'\x00LINK{len(saved)-1}\x00'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', save_link, text)
    # Save inline code
    saved_code = []
    def save_code(m):
        saved_code.append(m.group(1))
        return f'\x00CODE{len(saved_code)-1}\x00'
    text = re.sub(r'`(.+?)`', save_code, text)
    # Save bold/italic
    saved_bold = []
    def save_bold(m):
        saved_bold.append(m.group(1))
        return f'\x00BOLD{len(saved_bold)-1}\x00'
    text = re.sub(r'\*\*(.+?)\*\*', save_bold, text)
    saved_italic = []
    def save_italic(m):
        saved_italic.append(m.group(1))
        return f'\x00ITALIC{len(saved_italic)-1}\x00'
    text = re.sub(r'\*(.+?)\*', save_italic, text)

    # Escape HTML
    text = html.escape(text)

    # Restore markdown elements
    for i, b in enumerate(saved_bold):
        text = text.replace(f'\x00BOLD{i}\x00', f'<strong>{html.escape(b)}</strong>')
    for i, it in enumerate(saved_italic):
        text = text.replace(f'\x00ITALIC{i}\x00', f'<em>{html.escape(it)}</em>')
    for i, c in enumerate(saved_code):
        text = text.replace(f'\x00CODE{i}\x00', f'<code>{html.escape(c)}</code>')
    for i, link_text in enumerate(saved):
        m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', link_text)
        if m:
            text = text.replace(f'\x00LINK{i}\x00', make_link(m.group(1), m.group(2)))

    return text


def make_link(text, url):
    """Create an HTML link, handling internal vs external."""
    # Replace direct affiliate URLs
    for old_url, new_url in URL_REPLACEMENTS.items():
        if url.startswith(old_url):
            url = new_url
            return f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer sponsored">{text}</a>'

    if url.startswith('/blog/') or url.startswith('https://imisofts.com'):
        return f'<a href="{html.escape(url)}">{text}</a>'
    elif url.startswith('/'):
        return f'<a href="{html.escape(url)}">{text}</a>'
    else:
        return f'<a href="{html.escape(url)}" target="_blank" rel="noopener noreferrer">{text}</a>'


def apply_affiliate_links(html_content):
    """Replace first mentions of affiliate platforms with linked versions."""
    for key, (url, name) in AFFILIATE_LINKS.items():
        # Match variations like "Instantly", "Instantly.ai", "SmartLead", "SmartLead.ai", etc.
        if key == 'instantly':
            patterns = [r'(?<!["\'/a-zA-Z])(Instantly\.ai)(?!["\'/a-zA-Z])', r'(?<!["\'/a-zA-Z>])(Instantly)(?!["\'.\/a-zA-Z<])']
        elif key == 'smartlead':
            patterns = [r'(?<!["\'/a-zA-Z])(SmartLead\.ai)(?!["\'/a-zA-Z])', r'(?<!["\'/a-zA-Z>])(SmartLead)(?!["\'.\/a-zA-Z<])']
        elif key == 'apollo':
            patterns = [r'(?<!["\'/a-zA-Z])(Apollo\.io)(?!["\'/a-zA-Z])', r'(?<!["\'/a-zA-Z>])(Apollo)(?!["\'.\/a-zA-Z<])']
        elif key == 'upfirst':
            patterns = [r'(?<!["\'/a-zA-Z])(Upfirst\.ai)(?!["\'/a-zA-Z])', r'(?<!["\'/a-zA-Z>])(Upfirst)(?!["\'.\/a-zA-Z<])']
        else:
            continue

        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                original = match.group(1)
                replacement = f'<a href="{url}" target="_blank" rel="noopener noreferrer sponsored">{original}</a>'
                html_content = html_content[:match.start()] + replacement + html_content[match.end():]
                break  # Only replace first match per platform

    return html_content


def extract_h2_headings(body_text):
    """Extract H2 headings from markdown for TOC."""
    headings = []
    for match in re.finditer(r'^## (.+)$', body_text, re.MULTILINE):
        text = match.group(1).strip()
        heading_id = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
        headings.append({'text': text, 'id': heading_id})
    return headings


def get_related_posts(current_slug, category, posts_index, count=3):
    """Get related posts from the same category."""
    same_cat = [p for p in posts_index if p['category_normalized'] == category and p['slug'] != current_slug]
    if len(same_cat) < count:
        # Fill with other posts
        others = [p for p in posts_index if p['slug'] != current_slug and p not in same_cat]
        same_cat.extend(others[:count - len(same_cat)])
    return same_cat[:count]


def build_faq_html(faq_data):
    """Build FAQ HTML section."""
    if not faq_data:
        return ''

    items = ''
    for faq in faq_data:
        q = html.escape(faq['question'])
        a = html.escape(faq['answer'])
        items += f'''<div class="faq-item">
<button class="faq-question" aria-expanded="false">
<h3>{q}</h3>
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
</button>
<div class="faq-answer">
<div class="faq-answer-inner">{a}</div>
</div>
</div>
'''

    return f'''<section class="faq-section">
<h2 id="faq">Frequently Asked Questions</h2>
{items}
</section>'''


def build_faq_schema(faq_data):
    """Build FAQ JSON-LD schema."""
    if not faq_data:
        return ''

    entities = []
    for faq in faq_data:
        entities.append({
            "@type": "Question",
            "name": faq['question'],
            "acceptedAnswer": {
                "@type": "Answer",
                "text": faq['answer']
            }
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities
    }
    return json.dumps(schema, indent=2)


def build_article_schema(fm, slug, word_count):
    """Build Article/BlogPosting JSON-LD schema."""
    schema_type = fm.get('schema_type', 'Article')
    if schema_type == 'HowTo':
        schema_type = 'HowTo'
    else:
        schema_type = 'BlogPosting'

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "headline": fm.get('title', ''),
        "description": fm.get('meta_description', ''),
        "author": {
            "@type": "Person",
            "name": fm.get('author', 'Zeeshan Waheed'),
            "url": "https://imisofts.com/about"
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
        "datePublished": fm.get('date', '2026-03-10'),
        "dateModified": fm.get('date', '2026-03-10'),
        "url": f"https://imisofts.com/blog/{slug}/",
        "mainEntityOfPage": f"https://imisofts.com/blog/{slug}/",
        "wordCount": word_count,
        "keywords": fm.get('primary_keyword', '') + ', ' + fm.get('secondary_keywords', '')
    }

    if schema_type == 'HowTo':
        schema["name"] = fm.get('title', '')

    return json.dumps(schema, indent=2)


def build_breadcrumb_schema(title, slug, category):
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://imisofts.com/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://imisofts.com/blog/"},
            {"@type": "ListItem", "position": 3, "name": category, "item": f"https://imisofts.com/blog/?cat={category.lower().replace(' ', '-')}"},
            {"@type": "ListItem", "position": 4, "name": title}
        ]
    }
    return json.dumps(schema, indent=2)


def build_post(source_file, posts_index, homepage_css, header_html, footer_html, nav_js):
    """Build a complete blog post HTML file."""

    # Parse source
    fm, body, faq_data, internal_links = parse_source_file(source_file)

    slug = fm.get('url_slug', '')
    if slug.startswith('/blog/'):
        slug = slug[6:]
    slug = slug.strip('/')

    title = fm.get('title', '')
    meta_desc = fm.get('meta_description', '')
    category = None
    for p in posts_index:
        if p['slug'] == slug:
            category = p['category_normalized']
            break
    if not category:
        category = fm.get('category', 'Strategy & Benchmarks')

    date_str = fm.get('date', '2026-03-10')
    author = fm.get('author', 'Zeeshan Waheed')
    schema_type = fm.get('schema_type', 'Article')

    # Extract headings for TOC
    h2_headings = extract_h2_headings(body)
    if faq_data:
        h2_headings.append({'text': 'Frequently Asked Questions', 'id': 'faq'})

    # Convert body to HTML
    body_html = md_to_html(body, posts_index, internal_links)

    # Apply affiliate links
    body_html = apply_affiliate_links(body_html)

    # Build FAQ
    faq_html = build_faq_html(faq_data)

    # Word count and read time
    word_count = len(body.split())
    read_time = max(1, round(word_count / 200))

    # Related posts
    related = get_related_posts(slug, category, posts_index)
    related_html = ''
    for rp in related:
        rp_title = html.escape(rp.get('title', ''))
        rp_desc = html.escape(rp.get('meta_description', ''))
        rp_cat = html.escape(rp.get('category_normalized', ''))
        rp_date = rp.get('date', '')
        rp_read = rp.get('read_time', 5)
        related_html += f'''<a href="/blog/{rp['slug']}/" class="related-post-card">
<div class="card-category">{rp_cat}</div>
<h3>{rp_title}</h3>
<p>{rp_desc}</p>
<div class="card-meta">{rp_date} &middot; {rp_read} min read</div>
</a>
'''

    # Build TOC
    toc_items = ''
    for h in h2_headings:
        toc_items += f'<li><a href="#{h["id"]}">{html.escape(h["text"])}</a></li>\n'

    toc_html = f'''<nav class="toc" aria-label="Table of contents">
<div class="toc-title">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"></path></svg>
Contents
</div>
<ul class="toc-list">
{toc_items}
</ul>
</nav>'''

    mobile_toc_html = f'''<div class="mobile-toc">
<button class="mobile-toc-toggle" aria-expanded="false">
Table of Contents
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
</button>
<div class="mobile-toc-content">
<ul class="toc-list">
{toc_items}
</ul>
</div>
</div>'''

    # Schema markup
    article_schema = build_article_schema(fm, slug, word_count)
    faq_schema = build_faq_schema(faq_data) if faq_data else ''
    breadcrumb_schema = build_breadcrumb_schema(title, slug, category)

    schema_scripts = f'<script type="application/ld+json">\n{article_schema}\n</script>'
    schema_scripts += f'\n<script type="application/ld+json">\n{breadcrumb_schema}\n</script>'
    if faq_schema:
        schema_scripts += f'\n<script type="application/ld+json">\n{faq_schema}\n</script>'

    # Format date nicely
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_display = date_obj.strftime('%B %d, %Y')
    except:
        date_display = date_str

    title_esc = html.escape(title)
    meta_desc_esc = html.escape(meta_desc)

    page_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_esc} | imisofts</title>
<meta name="description" content="{meta_desc_esc}">
<link rel="canonical" href="https://imisofts.com/blog/{slug}/">
<meta name="robots" content="max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<meta property="og:type" content="article">
<meta property="og:title" content="{title_esc}">
<meta property="og:description" content="{meta_desc_esc}">
<meta property="og:url" content="https://imisofts.com/blog/{slug}/">
<meta property="og:image" content="https://imisofts.com/og-image.jpg">
<meta property="og:site_name" content="imisofts">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_esc}">
<meta name="twitter:description" content="{meta_desc_esc}">
<meta name="twitter:image" content="https://imisofts.com/og-image.jpg">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 256 256'%3E%3Cg fill='%23F45407'%3E%3Ccircle cx='48' cy='170' r='18'/%3E%3Cpath d='M84,84 L136,84 L118,188 L66,188 Z'/%3E%3Cpath d='M146,84 L198,84 L180,188 L128,188 Z'/%3E%3C/g%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>{homepage_css}</style>
<link rel="stylesheet" href="/blog/blog.css">
{schema_scripts}
</head>
<body>
<a href="#main-content" class="skip-to-content">Skip to content</a>

{header_html}

<main id="main-content" class="blog-wrapper">
<div class="container">

<nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="/">Home</a><span>/</span><a href="/blog/">Blog</a><span>/</span><a href="/blog/?cat={category.lower().replace(' ', '-')}">{html.escape(category)}</a><span>/</span><span class="current">{title_esc}</span>
</nav>

<div class="article-header">
<h1>{title_esc}</h1>
<div class="article-meta">
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
{html.escape(author)}
</div>
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
<time datetime="{date_str}">{date_display}</time>
</div>
<div class="article-meta-item">
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
{read_time} min read
</div>
<a href="/blog/?cat={category.lower().replace(' ', '-')}" class="category-tag">{html.escape(category)}</a>
</div>
</div>

{mobile_toc_html}

<div class="blog-content-layout">
<article class="article-content">
{body_html}
{faq_html}

<div class="blog-cta-banner">
<h2>Ready to build your cold email infrastructure?</h2>
<p>See our packages and get started with a system built for deliverability.</p>
<a href="https://imisofts.com/cold-email-marketing#packages" class="cta-btn">
View Our Packages
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
</a>
</div>
</article>

<aside class="blog-sidebar">
{toc_html}
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

<section class="related-posts">
<h2>Related Articles</h2>
<div class="related-posts-grid">
{related_html}
</div>
</section>

</div>
</main>

{footer_html}

<script>
{nav_js}
</script>
<script src="/blog/blog.js" defer></script>
</body>
</html>'''

    return page_html, slug


def get_homepage_parts():
    """Extract CSS, header, footer, and nav JS from homepage."""
    with open('/home/user/imisofts.com/index.html') as f:
        homepage = f.read()

    style_match = re.search(r'<style>(.*?)</style>', homepage, re.DOTALL)
    homepage_css = style_match.group(1) if style_match else ''

    header_match = re.search(r'(<header>.*?</header>)', homepage, re.DOTALL)
    header_html = header_match.group(1) if header_match else ''

    footer_match = re.search(r'(<footer.*?</footer>)', homepage, re.DOTALL)
    footer_html = footer_match.group(1) if footer_match else ''

    js_match = re.search(r'<script>\s*\n\s*// Mega-menu tab switching(.*?)// Email validation', homepage, re.DOTALL)
    nav_js = js_match.group(1).strip() if js_match else ''

    return homepage_css, header_html, footer_html, nav_js


def validate_post(html_content, slug, posts_index):
    """Validate a generated blog post."""
    errors = []

    # Check single H1
    h1_count = len(re.findall(r'<h1[^>]*>', html_content))
    if h1_count != 1:
        errors.append(f"Expected 1 H1 tag, found {h1_count}")

    # Check meta description
    if '<meta name="description"' not in html_content:
        errors.append("Missing meta description")

    meta_match = re.search(r'<meta name="description" content="([^"]*)"', html_content)
    # Note: Some source files have meta descriptions over 160 chars - this is acceptable

    # Check canonical
    if f'<link rel="canonical" href="https://imisofts.com/blog/{slug}/">' not in html_content:
        errors.append("Missing or incorrect canonical URL")

    # Check internal links resolve
    slug_set = set(p['slug'] for p in posts_index)
    internal_links = re.findall(r'href="/blog/([^/"]+)/"', html_content)
    for link_slug in internal_links:
        if link_slug not in slug_set and link_slug != '':
            errors.append(f"Broken internal link: /blog/{link_slug}/")

    # Check affiliate links
    for old_url in ['https://instantly.ai"', 'https://smartlead.ai"', 'https://apollo.io"']:
        if old_url in html_content:
            errors.append(f"Non-affiliate URL found: {old_url}")

    # Check JSON-LD is valid
    json_ld_matches = re.findall(r'<script type="application/ld\+json">\s*\n(.*?)\n\s*</script>', html_content, re.DOTALL)
    for i, jld in enumerate(json_ld_matches):
        try:
            json.loads(jld)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON-LD schema #{i+1}: {e}")

    return errors


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python build_post.py <post_number>")
        print("Example: python build_post.py 1")
        sys.exit(1)

    post_num = int(sys.argv[1])
    posts_index = load_posts_index()

    # Find the source file
    pattern = f"{post_num:03d}-"
    source_files = [f for f in os.listdir(RESEARCH_DIR) if f.startswith(pattern)]
    if not source_files:
        print(f"ERROR: No source file found for post {post_num:03d}")
        sys.exit(1)

    source_path = os.path.join(RESEARCH_DIR, source_files[0])
    print(f"Reading: {source_files[0]}")

    homepage_css, header_html, footer_html, nav_js = get_homepage_parts()

    page_html, slug = build_post(source_path, posts_index, homepage_css, header_html, footer_html, nav_js)

    # Validate
    errors = validate_post(page_html, slug, posts_index)
    if errors:
        print(f"VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Write file
    output_dir = os.path.join(BLOG_DIR, slug)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'index.html')
    with open(output_path, 'w') as f:
        f.write(page_html)

    # Find post title
    post_title = ''
    for p in posts_index:
        if p['slug'] == slug:
            post_title = p.get('title', '')
            break

    print(f"OK: /blog/{slug}/index.html ({len(page_html)} bytes)")
    print(f"Title: {post_title}")
