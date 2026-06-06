# content/news: automated news publishing queue

Drop one JSON file per article here. On push, the **Publish news** GitHub Action
runs `ops/build_news.py`, which builds the full article page from the live
template and updates the sitemap, news-sitemap, RSS feed, posts index, and the
/blog grid, then commits the generated files (Cloudflare Pages deploys on push).

## File format: `content/news/<slug>.json`

```json
{
  "slug": "my-article-slug-news-june-7-2026",
  "title": "Headline With the Key Entity Up Front",
  "desc": "150-160 char meta description, fact-led, with the takeaway.",
  "keywords": "primary keyword, secondary, secondary",
  "date": "2026-06-07",
  "time": "09:00",
  "read_time": 6,
  "word_count": 1100,
  "cta": "Want this built for your business?",
  "body": "<p><strong>Month D, YYYY.</strong> Intro...</p><p><strong>What happened</strong></p><ol><li>...</li></ol><p><strong>What it means for operators</strong></p><p>...with a <a href=\"/ai-automation\">service link</a>.</p>",
  "faqs": [["Question?","Answer."], ["Question?","Answer."]]
}
```

## Rules the build enforces
- `body` is HTML (paragraphs, ordered lists, links). **No em dashes** (build fails on them).
- 5-6 FAQs for deep pieces, 3-4 for briefs; FAQPage schema is generated to match.
- The contact form, mid-article CTA (h2), navbar, and footer come from the template automatically.
- news-sitemap keeps only articles within 48h of the newest; older ones drop off automatically.

The publisher (human or the scheduled agent) only writes the JSON. The Action does the rest.
