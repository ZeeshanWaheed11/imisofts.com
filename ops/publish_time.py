#!/usr/bin/env python3
"""Real publish time for NEW articles. Added 2026-11-14 (SEO audit, item A1).

Why: Google News only considers articles that show a clear date AND time, and it wants the
same moment, with its time zone, in the markup and in the news sitemap. Before this change
the pages carried a bare date, and the time was typed by hand into the spec, labelled +04:00
and often ahead of the real publish moment.

Rule: the builder decides when an article was published, from its own clock.
  - first build of a slug (the page does not exist yet): now;
  - rebuild of a page that already carries a full timestamp: that same timestamp, read back
    from the page, so a rebuild never moves it;
  - every page built before this change (bare date): callers get None and keep their old
    code path, so old pages stay byte for byte the same.

Site time is Dubai, UTC+4, no daylight saving.
"""
import datetime, email.utils, os, re

TZ = datetime.timezone(datetime.timedelta(hours=4))
LABEL = 'GMT+4'
_PUB_RX = re.compile(r'"datePublished"\s*:\s*"([^"]+)"')
_MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
           'September', 'October', 'November', 'December')


def now():
    return datetime.datetime.now(datetime.timezone.utc).astimezone(TZ).replace(microsecond=0)


def parse(value):
    """A full ISO 8601 timestamp -> aware datetime in site time. A bare date or junk -> None."""
    v = str(value or '')
    if 'T' not in v:
        return None
    try:
        d = datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
    except ValueError:
        return None
    if d.tzinfo is None:
        return None
    return d.astimezone(TZ).replace(microsecond=0)


def from_html(html):
    m = _PUB_RX.search(html or '')
    return parse(m.group(1)) if m else None


def from_page(path):
    try:
        return from_html(open(path, encoding='utf-8').read())
    except OSError:
        return None


def resolve(out_path):
    """Stamp for the page at out_path: now for a page that does not exist yet, the stored
    stamp for a page that has one, None for a page built before this change."""
    if not os.path.exists(out_path):
        return now()
    return from_page(out_path)


def iso(d):
    return d.isoformat()                       # 2026-11-14T14:35:00+04:00


def date(d):
    return d.strftime('%Y-%m-%d')


def hm(d):
    return d.strftime('%H:%M')


def naive(d):
    return d.replace(tzinfo=None)              # wall time in site time, for the news sitemap merge


def rfc822(d):
    return email.utils.format_datetime(d)      # Sat, 14 Nov 2026 14:35:00 +0400


def human(d):                                  # November 14, 2026, 2:35 PM GMT+4
    return '%s %d, %d, %d:%02d %s %s' % (_MONTHS[d.month - 1], d.day, d.year, (d.hour % 12) or 12,
                                         d.minute, 'AM' if d.hour < 12 else 'PM', LABEL)


def time_tag(d):
    return '<time datetime="%s">%s</time>' % (iso(d), human(d))


def og_times(html, d):
    """Add (or refresh) article:published_time and article:modified_time in <head>. Idempotent."""
    if 'property="article:published_time"' in html:
        for prop in ('article:published_time', 'article:modified_time'):
            html = re.sub(r'(<meta property="%s" content=")[^"]*(")' % prop,
                          lambda m: m.group(1) + iso(d) + m.group(2), html, count=1)
        return html
    tags = ('<meta property="article:published_time" content="%s">\n'
            '<meta property="article:modified_time" content="%s">\n') % (iso(d), iso(d))
    for anchor in (r'<meta property="article:author" content="[^"]*">\n?',
                   r'<meta property="og:site_name" content="[^"]*">\n?'):
        m = re.search(anchor, html)
        if m:
            sep = '' if m.group(0).endswith('\n') else '\n'
            return html[:m.end()] + sep + tags + html[m.end():]
    return html.replace('</head>', tags + '</head>', 1)


def fix_dateline(body, d):
    """News bodies open with a typed dateline, <p><strong>November 14, 2026.</strong>. If it is exactly one
    day off the real publish date (a run that crossed midnight), align it. Anything else is left alone."""
    m = re.match(r'(\s*<p><strong>)(%s) (\d{1,2}), (\d{4})(\.?</strong>)' % '|'.join(_MONTHS), body or '')
    if not m:
        return body
    try:
        typed = datetime.date(int(m.group(4)), _MONTHS.index(m.group(2)) + 1, int(m.group(3)))
    except ValueError:
        return body
    if abs((typed - d.date()).days) != 1:
        return body
    return m.group(1) + '%s %d, %d' % (_MONTHS[d.month - 1], d.day, d.year) + m.group(5) + body[m.end():]


def stamp_page(html, d):
    """For a page that is committed ready-built (founder byline): put the full stamp into the visible date,
    the article markup and <head>. Returns the new html, or None when the page has no visible date or no
    bare datePublished this function recognises. Then nothing is changed, so page and markup never disagree."""
    vis = re.search(r'<time datetime="\d{4}-\d\d-\d\d">[^<]*</time>', html)
    if vis:
        new = html[:vis.start()] + time_tag(d) + html[vis.end():]
    else:
        vis = re.search(r'(<div class="article-meta-item">)\s*(?:%s) \d{1,2}, \d{4}\s*(</div>)' % '|'.join(_MONTHS), html)
        if not vis:
            return None
        new = html[:vis.start()] + vis.group(1) + time_tag(d) + vis.group(2) + html[vis.end():]
    new, n = re.subn(r'("datePublished"\s*:\s*")\d{4}-\d\d-\d\d(")', lambda m: m.group(1) + iso(d) + m.group(2), new, count=1)
    if not n:
        return None
    new = re.sub(r'("dateModified"\s*:\s*")\d{4}-\d\d-\d\d(")', lambda m: m.group(1) + iso(d) + m.group(2), new, count=1)
    return og_times(new, d)
