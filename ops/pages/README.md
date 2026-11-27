# Page builders

Scripts that generate the hand-built pages of imisofts.com. Each one copies the header, footer and
sitewide styles from `about.html` (see `shell.py`), so a generated page always matches the rest of the site.

Run from the repo root:

| Script | Writes |
|---|---|
| `python3 ops/pages/build_geo.py` | `lead-generation-agency-uk.html`, `lead-generation-agency-australia.html`, `lead-generation-dubai.html` |
| `python3 ops/pages/build_404.py` | `404.html` |
| `python3 ops/pages/build_acquire.py` | `acquire.html` (imisofts for sale) |
| `python3 ops/pages/og_acquire.py` | `og-image-acquire.jpg` (share image for /acquire) |

Notes
- `geo_css.py` holds the shared landing page styles (homepage design language).
- `/acquire` images are in `/assets/acquire/`. The screenshots are real pages of the site, captured at
  1440px wide and saved as WebP. Retake them if the homepage or blog design changes.
- After a change to the header or footer, run `python3 ops/inject_nav.py` first, then rebuild these pages.
- Figures on /acquire: Domain Rating 27 (Ahrefs, checked 27 Nov 2026) and 8K to 10K monthly visitors
  (owner's figure). The article, tool and country counts are read from the site when the page is built.
