"""Shared page shell for new imisofts.com pages: head assets, sitewide CSS, nav and footer
are copied byte-for-byte from about.html so the header and footer match every other page."""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the repo root


def load_shell():
    s = open(os.path.join(ROOT, 'about.html'), encoding='utf-8').read()
    i = s.index('  <!-- Favicon -->')
    j = s.index('<script type="application/ld+json">')
    assets = s[i:j].rstrip() + '\n'
    k = s.index('  <style>\n    * {')
    h = s.index('</head>')
    styles = s[k:h]
    b = s.index('<body>')
    e = s.index('  </header>') + len('  </header>')
    body_top = s[b:e] + '\n'
    f = s.index('    <footer class="footer"')
    footer = s[f:]
    assert footer.rstrip().endswith('</html>')
    assert '/js/measure.js' in styles
    return assets, styles, body_top, footer


def esc(t):
    return html.escape(t, quote=True)


def jsonld(obj):
    return '  <script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + '\n  </script>\n'


def page(*, title, description, canonical=None, robots, og_url, og_image, schema, extra_css, main_html, tail_js=''):
    assets, styles, body_top, footer = load_shell()
    out = []
    out.append('<!DOCTYPE html>\n<html lang="en">\n<head>\n')
    out.append('  <meta charset="UTF-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    out.append('  <title>%s</title>\n' % esc(title))
    out.append('  <meta name="description" content="%s">\n' % esc(description))
    if canonical:
        out.append('  <link rel="canonical" href="%s">\n' % canonical)
    out.append('  <meta name="robots" content="%s">\n\n' % robots)
    out.append('  <!-- Open Graph Tags -->\n')
    out.append('  <meta property="og:type" content="website">\n')
    out.append('  <meta property="og:title" content="%s">\n' % esc(title))
    out.append('  <meta property="og:description" content="%s">\n' % esc(description))
    out.append('  <meta property="og:url" content="%s">\n' % og_url)
    out.append('  <meta property="og:image" content="%s">\n' % og_image)
    out.append('  <meta property="og:site_name" content="imisofts">\n\n')
    out.append('  <!-- Twitter Card Tags -->\n')
    out.append('  <meta name="twitter:card" content="summary_large_image">\n')
    out.append('  <meta name="twitter:title" content="%s">\n' % esc(title))
    out.append('  <meta name="twitter:description" content="%s">\n' % esc(description))
    out.append('  <meta name="twitter:image" content="%s">\n\n' % og_image)
    out.append(assets + '\n')
    for obj in schema:
        out.append(jsonld(obj) + '\n')
    out.append(styles)
    out.append(extra_css.strip() + '\n')
    out.append('</head>\n')
    out.append(body_top + '\n')
    out.append('  <main>\n' + main_html.rstrip() + '\n  </main>\n\n')
    footer_html = footer
    if tail_js:
        marker = '  <!-- Cal floating-popup embed code begins -->'
        assert marker in footer_html
        footer_html = footer_html.replace(marker, tail_js.rstrip() + '\n' + marker, 1)
    out.append(footer_html)
    return ''.join(out)
