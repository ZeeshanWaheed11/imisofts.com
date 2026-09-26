#!/usr/bin/env python3
"""Key-numbers block: one compact, dated table of the hard numbers an article states.

Why: answer engines lift tables and dated figures far more readily than prose. A page
that carries "what it costs, how many, since when" in one labelled table with a source
line gets quoted; the same facts spread over 1,500 words usually do not.

Spec field (optional, any of the three engines):

  "key_numbers": {
    "title":  "Key numbers",                       # optional, default below
    "rows": [                                      # 2 to 12 rows
      {"label": "Retell AI, per minute",  "value": "$0.07", "note": "voice only, LLM extra"},
      {"label": "Twilio US outbound, per minute", "value": "$0.014"}
    ],
    "source": "Prices read on 26 September 2026 from each vendor's pricing page."   # required
  }

Rules enforced here: every row needs a label and a value; the source line is mandatory
(a number without a date is not citable); dashes become commas (site rule); HTML is
escaped. Only specs that carry the block get it, so nothing published before 2026-09-26
changes. Idempotent through the class="key-numbers" marker.

Placement: immediately before the first <h2> of the article body (after the opening
answer and the hero), or before the CTA when the body has no <h2>. The block's own
<h2 id="key-numbers"> is picked up by fix_articles.build_toc_items, so it appears in the
table of contents.
"""
import html as _html
import re

MARK = 'class="key-numbers"'
DEFAULT_TITLE = 'Key numbers'
MAX_ROWS = 12


def _clean(t):
    t = str(t if t is not None else '')
    t = re.sub(r'\s*[‒–—]\s*', ', ', t)   # figure/en/em dash -> comma (site rule)
    t = re.sub(r'\s+', ' ', t).strip()
    return _html.escape(t, quote=True)


def spec_block(meta):
    """Return the validated key_numbers dict, or None when the spec has no usable block."""
    kn = meta.get('key_numbers') if isinstance(meta, dict) else None
    if not isinstance(kn, dict):
        return None
    rows = kn.get('rows')
    if not isinstance(rows, list):
        return None
    clean_rows = []
    for r in rows[:MAX_ROWS]:
        if not isinstance(r, dict):
            continue
        label = _clean(r.get('label'))
        value = _clean(r.get('value'))
        if not label or not value:
            continue
        clean_rows.append((label, value, _clean(r.get('note'))))
    source = _clean(kn.get('source'))
    if len(clean_rows) < 2 or not source:
        return None
    return {'title': _clean(kn.get('title')) or DEFAULT_TITLE, 'rows': clean_rows, 'source': source}


def render(meta):
    """HTML for the block, or '' when the spec has no usable key_numbers."""
    kn = spec_block(meta)
    if not kn:
        return ''
    cell = 'padding:9px 6px;border-bottom:1px solid #EEF0F3;vertical-align:top'
    trs = []
    for label, value, note in kn['rows']:
        note_html = ' <span style="color:#6B7280;font-weight:400">(%s)</span>' % note if note else ''
        trs.append('<tr><td style="%s">%s%s</td><td style="%s;text-align:right;font-weight:600;white-space:nowrap">%s</td></tr>'
                   % (cell, label, note_html, cell, value))
    return (
        '<section %s id="key-numbers-block" style="margin:28px 0;padding:18px 20px 14px;border:1px solid #E5E7EB;border-radius:12px;background:#FAFAFA">\n'
        '<h2 id="key-numbers">%s</h2>\n'
        '<table style="width:100%%;border-collapse:collapse;font-size:15px;line-height:1.45">\n'
        '<thead><tr><th style="text-align:left;padding:6px;border-bottom:2px solid #E5E7EB;font-size:13px;color:#6B7280;font-weight:600">Item</th>'
        '<th style="text-align:right;padding:6px;border-bottom:2px solid #E5E7EB;font-size:13px;color:#6B7280;font-weight:600">Number</th></tr></thead>\n'
        '<tbody>\n%s\n</tbody>\n</table>\n'
        '<p style="font-size:13px;color:#6B7280;margin:10px 0 0">%s</p>\n'
        '</section>'
    ) % (MARK, kn['title'], '\n'.join(trs), kn['source'])


def apply(html, meta):
    """Insert the block into a built page once. Returns the page unchanged when there is
    nothing to insert or the marker is already present."""
    block = render(meta)
    if not block or MARK in html:
        return html
    i = html.find('<article')
    if i < 0:
        return html
    bs = html.find('>', i) + 1
    j = html.find('</article>', bs)
    if bs <= 0 or j < 0:
        return html
    body = html[bs:j]
    # End of the editorial body: the CTA banner or the FAQ section, whichever comes first.
    m_end = re.search(r'<(div|section)[^>]*class="[^"]*(cta-banner|cta|faq-section)[^"]*"', body)
    end = m_end.start() if m_end else len(body)
    # First heading: a real <h2>, or a bold-paragraph heading that fix_articles will turn into
    # an <h2> later (older spec style). Datelines like "September 26, 2026." are not headings.
    candidates = [m.start() for m in re.finditer(r'<h2[\s>]', body[:end])]
    for m in re.finditer(r'<p><strong>([^<]{3,70})</strong></p>', body[:end]):
        if not re.match(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\.?$', m.group(1).strip()):
            candidates.append(m.start())
    pos = min(candidates) if candidates else end
    body = body[:pos] + block + '\n' + body[pos:]
    return html[:bs] + body + html[j:]
