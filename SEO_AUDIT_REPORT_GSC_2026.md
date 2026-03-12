# SEO Audit Report — imisofts.com
## Google Search Console Indexing & Full Site Audit
### Date: March 12, 2026

---

## INSTRUCTIONS FOR CLAUDE CHROME EXTENSION

> **Copy the URL lists and prompts below into the Claude Chrome Extension while viewing your Google Search Console account to perform a complete indexing audit.**

---

## TABLE OF CONTENTS

1. [Site Overview](#1-site-overview)
2. [Complete URL Inventory (252 URLs)](#2-complete-url-inventory)
3. [GSC Indexing Check — Prompts for Claude Extension](#3-gsc-indexing-check-prompts)
4. [Technical SEO Audit](#4-technical-seo-audit)
5. [On-Page SEO Audit](#5-on-page-seo-audit)
6. [Structured Data Audit](#6-structured-data-audit)
7. [Redirect & Crawl Efficiency Audit](#7-redirect--crawl-efficiency-audit)
8. [Security Headers Audit](#8-security-headers-audit)
9. [Issues Found & Recommendations](#9-issues-found--recommendations)
10. [Action Items Checklist](#10-action-items-checklist)

---

## 1. SITE OVERVIEW

| Property | Value |
|---|---|
| **Domain** | imisofts.com |
| **Platform** | Static HTML (Netlify hosting) |
| **Total Pages in Sitemap** | 252 |
| **Core Pages** | 38 |
| **Blog Posts** | 213 |
| **Blog Index** | 1 |
| **Author Pages** | 1 (Zeeshan Waheed) |
| **Sitemap** | https://imisofts.com/sitemap.xml |
| **Robots.txt** | https://imisofts.com/robots.txt |
| **RSS Feed** | https://imisofts.com/feed.xml |
| **Last Sitemap Update** | 2026-03-10 |
| **Non-indexed Pages** | 5 (admin-login, admin-dashboard, client-login, client-dashboard, 404) |

---

## 2. COMPLETE URL INVENTORY

### 2A. Core Pages (38 URLs) — CHECK ALL IN GSC

```
https://imisofts.com/
https://imisofts.com/about
https://imisofts.com/contact
https://imisofts.com/pricing
https://imisofts.com/faq
https://imisofts.com/support
https://imisofts.com/careers
https://imisofts.com/products
https://imisofts.com/case-studies
https://imisofts.com/free-audit
https://imisofts.com/api-docs
https://imisofts.com/launch-your-saas
https://imisofts.com/openclaw-setup
https://imisofts.com/privacy-policy
https://imisofts.com/terms-of-service
https://imisofts.com/cookie-policy
https://imisofts.com/cold-email-marketing
https://imisofts.com/cold-email-saas
https://imisofts.com/cold-email-recruiters
https://imisofts.com/ai-automation
https://imisofts.com/ai-automation-ecommerce
https://imisofts.com/ai-mobile-apps
https://imisofts.com/lead-generation
https://imisofts.com/lead-generation-agencies
https://imisofts.com/web-development
https://imisofts.com/ecommerce
https://imisofts.com/digital-marketing
https://imisofts.com/crm-development
https://imisofts.com/gohighlevel-services
https://imisofts.com/gohighlevel-real-estate
https://imisofts.com/shopify-apps
https://imisofts.com/shopify-app-reviews
https://imisofts.com/hire-ai-engineer
https://imisofts.com/hire-cold-email-expert
https://imisofts.com/hire-gohighlevel-developer
https://imisofts.com/hire-n8n-developer
https://imisofts.com/hire-shopify-expert
https://imisofts.com/author/zeeshan-waheed
```

### 2B. Blog Index (1 URL)

```
https://imisofts.com/blog/
```

### 2C. Blog Posts (213 URLs) — CHECK ALL IN GSC

#### Cold Email Infrastructure (20 posts)
```
https://imisofts.com/blog/cold-email-infrastructure-setup/
https://imisofts.com/blog/private-server-vs-google-workspace-cold-email/
https://imisofts.com/blog/cold-email-domain-strategy/
https://imisofts.com/blog/spf-dkim-dmarc-cold-email-setup/
https://imisofts.com/blog/cold-email-warmup-strategy/
https://imisofts.com/blog/cold-email-deliverability/
https://imisofts.com/blog/cold-email-inbox-rotation/
https://imisofts.com/blog/google-postmaster-tools-cold-email/
https://imisofts.com/blog/bimi-email-setup/
https://imisofts.com/blog/cold-email-bounce-rate/
https://imisofts.com/blog/cold-email-sending-limits/
https://imisofts.com/blog/cold-email-tracking-domain/
https://imisofts.com/blog/cold-email-infrastructure-cost/
https://imisofts.com/blog/dedicated-ip-cold-email/
https://imisofts.com/blog/cold-email-domain-purchasing/
https://imisofts.com/blog/mx-records-cold-email/
https://imisofts.com/blog/cold-email-spam-filter-avoidance/
https://imisofts.com/blog/cold-email-infrastructure-provider/
https://imisofts.com/blog/email-server-cold-outreach/
https://imisofts.com/blog/cold-email-sender-reputation/
```

#### Cold Email by Industry (22 posts)
```
https://imisofts.com/blog/cold-email-ai-startups/
https://imisofts.com/blog/cold-email-saas-companies/
https://imisofts.com/blog/cold-email-recruitment-agencies/
https://imisofts.com/blog/cold-email-real-estate-investors/
https://imisofts.com/blog/cold-email-commercial-cleaning/
https://imisofts.com/blog/cold-email-insurance-agents/
https://imisofts.com/blog/cold-email-cybersecurity-companies/
https://imisofts.com/blog/cold-email-podcast-guest-booking/
https://imisofts.com/blog/cold-email-business-lending/
https://imisofts.com/blog/cold-email-marketing-agencies/
https://imisofts.com/blog/cold-email-amazon-sellers/
https://imisofts.com/blog/cold-email-financial-advisors/
https://imisofts.com/blog/cold-email-luxury-golf-travel/
https://imisofts.com/blog/cold-email-startups/
https://imisofts.com/blog/cold-email-b2b-services/
https://imisofts.com/blog/cold-email-review-management/
https://imisofts.com/blog/white-label-cold-email-infrastructure/
https://imisofts.com/blog/cold-email-for-event-companies/
https://imisofts.com/blog/cold-email-for-logistics-companies/
https://imisofts.com/blog/cold-email-for-law-firms/
https://imisofts.com/blog/cold-email-for-lead-generation/
https://imisofts.com/blog/cold-email-for-user-acquisition/
```

#### Lead Generation & Prospecting (12 posts)
```
https://imisofts.com/blog/apollo-lead-generation/
https://imisofts.com/blog/clay-vs-apollo/
https://imisofts.com/blog/icp-definition-b2b/
https://imisofts.com/blog/email-verification-cold-email/
https://imisofts.com/blog/linkedin-cold-email-multi-channel/
https://imisofts.com/blog/lead-scraping-cold-email/
https://imisofts.com/blog/personalization-at-scale-cold-email/
https://imisofts.com/blog/cold-email-lead-list-building/
https://imisofts.com/blog/smartlead-supersearch/
https://imisofts.com/blog/data-enrichment-cold-email/
https://imisofts.com/blog/cold-email-targeting-strategy/
https://imisofts.com/blog/b2b-outbound-sales-strategy/
```

#### Cold Email Copywriting & Strategy (14 posts)
```
https://imisofts.com/blog/cold-email-campaign-management/
https://imisofts.com/blog/cold-email-sequences-3-5-touch-framework/
https://imisofts.com/blog/cold-email-subject-lines-formulas/
https://imisofts.com/blog/plain-text-vs-html-cold-email/
https://imisofts.com/blog/spintax-cold-email/
https://imisofts.com/blog/cold-email-ab-testing/
https://imisofts.com/blog/cold-email-cta/
https://imisofts.com/blog/cold-email-first-line/
https://imisofts.com/blog/cold-email-follow-up/
https://imisofts.com/blog/cold-email-templates-b2b/
https://imisofts.com/blog/loom-video-cold-email/
https://imisofts.com/blog/cold-email-copy-by-industry/
https://imisofts.com/blog/cold-email-spam-trigger-words/
https://imisofts.com/blog/cold-email-value-proposition/
```

#### Cold Email Performance & ROI (6 posts)
```
https://imisofts.com/blog/cold-email-reply-rates/
https://imisofts.com/blog/cold-email-landing-page/
https://imisofts.com/blog/cold-email-reply-rate-benchmarks/
https://imisofts.com/blog/scale-cold-email-5000-per-day/
https://imisofts.com/blog/hire-cold-email-agency-vs-diy/
https://imisofts.com/blog/cold-email-roi/
```

#### European & International Cold Email (10 posts)
```
https://imisofts.com/blog/cold-email-uk-b2b-strategy/
https://imisofts.com/blog/cold-email-netherlands-b2b/
https://imisofts.com/blog/cold-email-germany-b2b/
https://imisofts.com/blog/gdpr-cold-email-compliance/
https://imisofts.com/blog/cold-email-sweden-finland/
https://imisofts.com/blog/cold-email-ireland/
https://imisofts.com/blog/start-cold-email-agency-europe/
https://imisofts.com/blog/cold-email-opt-in-vs-opt-out-map/
https://imisofts.com/blog/cold-email-localization-dutch-german/
https://imisofts.com/blog/cold-email-european-startups/
```

#### Tool Guides & Setup (10 posts)
```
https://imisofts.com/blog/instantly-setup-guide/
https://imisofts.com/blog/smartlead-setup-guide/
https://imisofts.com/blog/apollo-search-filters/
https://imisofts.com/blog/n8n-cold-email-automation/
https://imisofts.com/blog/gohighlevel-cold-email-crm/
https://imisofts.com/blog/instantly-vs-smartlead-2026/
https://imisofts.com/blog/instantly-warmup-settings/
https://imisofts.com/blog/clay-data-enrichment-guide/
https://imisofts.com/blog/cold-email-tool-stack/
https://imisofts.com/blog/instantly-pool-rotation-setup/
```

#### Comparisons & Reviews (24 posts)
```
https://imisofts.com/blog/cold-email-vs-linkedin-ads/
https://imisofts.com/blog/cold-email-deliverability-audit/
https://imisofts.com/blog/cold-email-mistakes/
https://imisofts.com/blog/cold-email-in-2026/
https://imisofts.com/blog/cold-email-agency-dubai/
https://imisofts.com/blog/instantly-vs-lemlist/
https://imisofts.com/blog/instantly-vs-saleshandy/
https://imisofts.com/blog/instantly-vs-quickmail/
https://imisofts.com/blog/instantly-vs-reply-io/
https://imisofts.com/blog/instantly-vs-mailshake/
https://imisofts.com/blog/smartlead-vs-saleshandy/
https://imisofts.com/blog/smartlead-vs-lemlist/
https://imisofts.com/blog/smartlead-vs-quickmail/
https://imisofts.com/blog/apollo-vs-zoominfo/
https://imisofts.com/blog/apollo-vs-lusha/
https://imisofts.com/blog/apollo-vs-cognism/
https://imisofts.com/blog/apollo-vs-rocketreach/
https://imisofts.com/blog/clay-vs-clearbit/
https://imisofts.com/blog/clay-vs-seamless-ai/
https://imisofts.com/blog/instantly-vs-woodpecker/
https://imisofts.com/blog/instantly-vs-gmass/
https://imisofts.com/blog/instantly-vs-snov-io/
https://imisofts.com/blog/instantly-review-2026/
https://imisofts.com/blog/smartlead-review-2026/
```

#### Best-of Lists & Alternatives (4 posts)
```
https://imisofts.com/blog/apollo-review-2026/
https://imisofts.com/blog/best-email-warmup-tools-2026/
https://imisofts.com/blog/best-b2b-lead-scraping-tools-2026/
https://imisofts.com/blog/best-instantly-alternatives-2026/
```

#### Pricing & Cost Analysis (16 posts)
```
https://imisofts.com/blog/best-apollo-alternatives-2026/
https://imisofts.com/blog/cold-email-cost-per-lead/
https://imisofts.com/blog/cold-email-agency-pricing-2026/
https://imisofts.com/blog/cold-email-infrastructure-cost-breakdown/
https://imisofts.com/blog/instantly-pricing-plans-2026/
https://imisofts.com/blog/smartlead-pricing-plans-2026/
https://imisofts.com/blog/how-much-does-cold-email-cost-2026/
https://imisofts.com/blog/cost-to-send-1000-cold-emails-2026/
https://imisofts.com/blog/private-email-server-cost-2026/
https://imisofts.com/blog/cold-email-budget-calculator/
https://imisofts.com/blog/cold-email-vs-linkedin-ads-cost/
https://imisofts.com/blog/apollo-pricing-plans-2026/
https://imisofts.com/blog/cold-email-vs-google-ads-cost/
https://imisofts.com/blog/lemlist-pricing-2026/
https://imisofts.com/blog/woodpecker-pricing-2026/
https://imisofts.com/blog/cold-email-vs-sdr-cost/
```

#### Statistics & Data (15 posts)
```
https://imisofts.com/blog/cold-email-open-rates-by-industry-2026/
https://imisofts.com/blog/cold-email-response-rate-statistics-2026/
https://imisofts.com/blog/email-deliverability-benchmarks-2026/
https://imisofts.com/blog/cold-email-conversion-rates/
https://imisofts.com/blog/b2b-email-outreach-statistics-2026/
https://imisofts.com/blog/cold-email-vs-warm-email-conversion/
https://imisofts.com/blog/follow-ups-cold-email-data/
https://imisofts.com/blog/best-time-send-cold-emails-2026/
https://imisofts.com/blog/cold-email-subject-line-data/
https://imisofts.com/blog/cold-email-campaign-metrics-kpis/
https://imisofts.com/blog/cold-email-personalization-impact-data/
https://imisofts.com/blog/cold-email-word-count-data/
https://imisofts.com/blog/email-warmup-duration-data/
https://imisofts.com/blog/cold-email-bounce-rate-benchmarks/
https://imisofts.com/blog/cold-email-ab-test-results/
```

#### Industry-Specific Use Cases — Batch 2 (15 posts)
```
https://imisofts.com/blog/cold-email-seed-stage-startups/
https://imisofts.com/blog/cold-email-saas-demo-booking/
https://imisofts.com/blog/cold-email-consulting-firms/
https://imisofts.com/blog/cold-email-it-staffing/
https://imisofts.com/blog/cold-email-home-services/
https://imisofts.com/blog/cold-email-accounting-firms/
https://imisofts.com/blog/cold-email-ecommerce-b2b-wholesale/
https://imisofts.com/blog/cold-email-healthcare-companies/
https://imisofts.com/blog/cold-email-construction-companies/
https://imisofts.com/blog/cold-email-private-equity/
https://imisofts.com/blog/cold-email-venture-capital/
https://imisofts.com/blog/cold-email-coaches-consultants/
https://imisofts.com/blog/cold-email-web-design-agencies/
https://imisofts.com/blog/cold-email-mortgage-brokers/
https://imisofts.com/blog/cold-email-managed-service-providers/
```

#### Legal / Compliance by Country (10 posts)
```
https://imisofts.com/blog/cold-email-laws-united-states/
https://imisofts.com/blog/cold-email-laws-united-kingdom/
https://imisofts.com/blog/cold-email-laws-canada/
https://imisofts.com/blog/cold-email-laws-australia/
https://imisofts.com/blog/cold-email-laws-france/
https://imisofts.com/blog/cold-email-laws-germany/
https://imisofts.com/blog/cold-email-laws-singapore/
https://imisofts.com/blog/cold-email-laws-uae/
https://imisofts.com/blog/cold-email-laws-india/
https://imisofts.com/blog/cold-email-laws-sweden/
```

#### How-To / Tutorial Guides (10 posts)
```
https://imisofts.com/blog/email-warmup-setup-guide/
https://imisofts.com/blog/cold-email-writing-framework/
https://imisofts.com/blog/find-business-email-methods/
https://imisofts.com/blog/cold-email-deliverability-checklist/
https://imisofts.com/blog/dmarc-monitoring-setup-guide/
https://imisofts.com/blog/email-sending-pools-guide/
https://imisofts.com/blog/email-list-verification-guide/
https://imisofts.com/blog/apollo-lead-scraping-tutorial/
https://imisofts.com/blog/domain-redirect-cold-email-setup/
https://imisofts.com/blog/cold-emails-going-to-spam-fix/
```

#### Troubleshooting / Fix Guides (10 posts)
```
https://imisofts.com/blog/email-domain-blacklisted-check-fix/
https://imisofts.com/blog/low-cold-email-reply-rate-fix/
https://imisofts.com/blog/cold-email-bouncing-fix/
https://imisofts.com/blog/instantly-inboxes-disconnected-fix/
https://imisofts.com/blog/email-warmup-not-working/
https://imisofts.com/blog/cold-emails-not-getting-opens/
https://imisofts.com/blog/dmarc-failing-fix/
https://imisofts.com/blog/spf-record-too-many-lookups-fix/
https://imisofts.com/blog/cold-email-campaign-not-generating-leads/
```

#### Featured / Pillar Content (15 posts)
```
https://imisofts.com/blog/ai-agents-smb-automation-2025/
https://imisofts.com/blog/ai-marketing-automation-smb-growth-2025/
https://imisofts.com/blog/ai-sales-agents-autonomous-cold-email-2025/
https://imisofts.com/blog/best-cold-email-software-2026/
https://imisofts.com/blog/best-cold-email-subject-lines-2025/
https://imisofts.com/blog/cold-email-deliverability-inbox-placement-2026/
https://imisofts.com/blog/cold-email-domain-warmup-2026/
https://imisofts.com/blog/cold-email-marketing-instantly-ai-2025/
https://imisofts.com/blog/cold-email-sending-limits-2025/
https://imisofts.com/blog/cold-email-templates-5m-revenue-2025/
https://imisofts.com/blog/how-many-domains-cold-email-2026/
https://imisofts.com/blog/instantly-ai-lead-generation-guide-2025/
https://imisofts.com/blog/instantly-vs-lemlist-comparison-2026/
https://imisofts.com/blog/instantly-vs-smartlead-comparison-2025/
https://imisofts.com/blog/n8n-workflow-generator-ai-2025/
https://imisofts.com/blog/saleshandy-vs-instantly-vs-smartlead-2025/
```

---

## 3. GSC INDEXING CHECK PROMPTS

### How to Use These Prompts

Open your Google Search Console property for `imisofts.com`, then use the Claude Chrome Extension with the following prompts to audit indexing status.

---

### PROMPT 1: Full Indexing Status Check

> **Paste this into Claude Chrome Extension while on GSC "Pages" report:**
>
> I need you to analyze the Google Search Console indexing report visible on screen for imisofts.com. Please check:
>
> 1. How many pages are currently indexed vs not indexed?
> 2. What are the top "Why pages aren't indexed" reasons?
> 3. Are there any pages with "Crawled - currently not indexed" status?
> 4. Are there any pages with "Discovered - currently not indexed" status?
> 5. Any "Excluded by noindex tag" pages that shouldn't be excluded?
> 6. Any "Duplicate without user-selected canonical" issues?
> 7. Any "Duplicate, Google chose different canonical" issues?
> 8. What is the overall indexing health percentage?
>
> My sitemap has 252 URLs total. I expect approximately 252 indexed pages.

---

### PROMPT 2: URL Inspection — Core Pages

> **Paste this into Claude Chrome Extension while on GSC URL Inspection tool. Inspect each URL one by one:**
>
> I'm checking the URL inspection results for imisofts.com. For the URL currently displayed, please tell me:
>
> 1. Is it indexed or not?
> 2. What is the crawl date?
> 3. Is the canonical URL correct (should match the URL itself)?
> 4. Is the page mobile-friendly?
> 5. Are there any Rich Results detected?
> 6. Any issues or warnings?
>
> Here are ALL 38 core pages that need inspection (check each one):
>
> - https://imisofts.com/
> - https://imisofts.com/about
> - https://imisofts.com/contact
> - https://imisofts.com/pricing
> - https://imisofts.com/faq
> - https://imisofts.com/support
> - https://imisofts.com/careers
> - https://imisofts.com/products
> - https://imisofts.com/case-studies
> - https://imisofts.com/free-audit
> - https://imisofts.com/api-docs
> - https://imisofts.com/launch-your-saas
> - https://imisofts.com/openclaw-setup
> - https://imisofts.com/cold-email-marketing
> - https://imisofts.com/cold-email-saas
> - https://imisofts.com/cold-email-recruiters
> - https://imisofts.com/ai-automation
> - https://imisofts.com/ai-automation-ecommerce
> - https://imisofts.com/ai-mobile-apps
> - https://imisofts.com/lead-generation
> - https://imisofts.com/lead-generation-agencies
> - https://imisofts.com/web-development
> - https://imisofts.com/ecommerce
> - https://imisofts.com/digital-marketing
> - https://imisofts.com/crm-development
> - https://imisofts.com/gohighlevel-services
> - https://imisofts.com/gohighlevel-real-estate
> - https://imisofts.com/shopify-apps
> - https://imisofts.com/shopify-app-reviews
> - https://imisofts.com/hire-ai-engineer
> - https://imisofts.com/hire-cold-email-expert
> - https://imisofts.com/hire-gohighlevel-developer
> - https://imisofts.com/hire-n8n-developer
> - https://imisofts.com/hire-shopify-expert
> - https://imisofts.com/privacy-policy
> - https://imisofts.com/terms-of-service
> - https://imisofts.com/cookie-policy
> - https://imisofts.com/author/zeeshan-waheed

---

### PROMPT 3: Blog Post Indexing Batch Check

> **Paste this into Claude Chrome Extension while on GSC "Pages" report filtered by "/blog/":**
>
> I'm looking at the GSC Pages report filtered to show /blog/ URLs for imisofts.com. I have 213 blog posts + 1 blog index = 214 blog URLs total.
>
> Please analyze what's on screen and tell me:
>
> 1. How many blog URLs are indexed?
> 2. How many blog URLs are NOT indexed?
> 3. List any blog URLs with status "Crawled - currently not indexed"
> 4. List any blog URLs with status "Discovered - currently not indexed"
> 5. List any blog URLs excluded for any other reason
> 6. Which blog posts were most recently crawled?
> 7. Which blog posts haven't been crawled in over 30 days?
>
> Expected: All 214 blog URLs should be indexed.

---

### PROMPT 4: Newly Created Pages Check

> **Paste this into Claude Chrome Extension while on GSC URL Inspection:**
>
> I need to verify indexing status of our NEWEST pages (created in the last 60 days). Please check URL inspection for each of these and report the status:
>
> **New Blog Posts (2026):**
> - https://imisofts.com/blog/best-cold-email-software-2026/
> - https://imisofts.com/blog/instantly-vs-lemlist-comparison-2026/
> - https://imisofts.com/blog/cold-email-deliverability-inbox-placement-2026/
> - https://imisofts.com/blog/cold-email-domain-warmup-2026/
> - https://imisofts.com/blog/how-many-domains-cold-email-2026/
> - https://imisofts.com/blog/cold-email-in-2026/
> - https://imisofts.com/blog/instantly-vs-smartlead-2026/
> - https://imisofts.com/blog/instantly-review-2026/
> - https://imisofts.com/blog/smartlead-review-2026/
> - https://imisofts.com/blog/apollo-review-2026/
> - https://imisofts.com/blog/best-email-warmup-tools-2026/
> - https://imisofts.com/blog/best-b2b-lead-scraping-tools-2026/
> - https://imisofts.com/blog/best-instantly-alternatives-2026/
> - https://imisofts.com/blog/best-apollo-alternatives-2026/
> - https://imisofts.com/blog/cold-email-agency-pricing-2026/
> - https://imisofts.com/blog/instantly-pricing-plans-2026/
> - https://imisofts.com/blog/smartlead-pricing-plans-2026/
> - https://imisofts.com/blog/how-much-does-cold-email-cost-2026/
> - https://imisofts.com/blog/cost-to-send-1000-cold-emails-2026/
> - https://imisofts.com/blog/private-email-server-cost-2026/
> - https://imisofts.com/blog/apollo-pricing-plans-2026/
> - https://imisofts.com/blog/lemlist-pricing-2026/
> - https://imisofts.com/blog/woodpecker-pricing-2026/
> - https://imisofts.com/blog/cold-email-open-rates-by-industry-2026/
> - https://imisofts.com/blog/cold-email-response-rate-statistics-2026/
> - https://imisofts.com/blog/email-deliverability-benchmarks-2026/
> - https://imisofts.com/blog/b2b-email-outreach-statistics-2026/
> - https://imisofts.com/blog/best-time-send-cold-emails-2026/
>
> **New Service Pages:**
> - https://imisofts.com/cold-email-saas
> - https://imisofts.com/cold-email-recruiters
> - https://imisofts.com/ai-automation-ecommerce
> - https://imisofts.com/gohighlevel-real-estate
> - https://imisofts.com/launch-your-saas
> - https://imisofts.com/openclaw-setup
> - https://imisofts.com/lead-generation-agencies
> - https://imisofts.com/hire-ai-engineer
> - https://imisofts.com/hire-cold-email-expert
> - https://imisofts.com/hire-gohighlevel-developer
> - https://imisofts.com/hire-n8n-developer
> - https://imisofts.com/hire-shopify-expert
>
> For any page NOT indexed, tell me the reason and whether I should request indexing.

---

### PROMPT 5: Sitemap Status Check

> **Paste this into Claude Chrome Extension while on GSC "Sitemaps" section:**
>
> I'm looking at the Sitemaps report in Google Search Console for imisofts.com.
>
> Please tell me:
> 1. Is sitemap.xml successfully submitted and processed?
> 2. How many URLs were discovered in the sitemap?
> 3. When was the sitemap last read by Google?
> 4. Are there any sitemap errors or warnings?
> 5. How does the discovered URL count compare to my expected 252 URLs?

---

### PROMPT 6: Core Web Vitals Check

> **Paste this into Claude Chrome Extension while on GSC "Core Web Vitals" report:**
>
> Analyze the Core Web Vitals report for imisofts.com:
>
> 1. What is the LCP (Largest Contentful Paint) status? Good/Needs Improvement/Poor?
> 2. What is the FID/INP (Interaction to Next Paint) status?
> 3. What is the CLS (Cumulative Layout Shift) status?
> 4. How many URLs have "Good" status vs "Poor" status?
> 5. Are there specific URL groups with performance issues?
> 6. Mobile vs Desktop performance comparison?

---

### PROMPT 7: Mobile Usability Check

> **Paste this into Claude Chrome Extension while on GSC "Mobile Usability" report:**
>
> Analyze the Mobile Usability report for imisofts.com:
>
> 1. How many pages have mobile usability issues?
> 2. What types of issues are reported? (text too small, clickable elements too close, content wider than screen, etc.)
> 3. Are any specific pages flagged?
> 4. What is the trend — improving or declining?

---

### PROMPT 8: Rich Results / Enhancements Check

> **Paste this into Claude Chrome Extension while on GSC "Enhancements" section:**
>
> Check ALL enhancement reports available for imisofts.com:
>
> 1. **FAQ** — How many pages have valid FAQ markup? Any errors?
> 2. **Breadcrumbs** — How many pages have valid breadcrumb markup? Any errors?
> 3. **Articles** — How many blog posts have valid Article markup? Any errors?
> 4. **Organization** — Is the Organization schema detected?
> 5. **Sitelinks Search Box** — Is it showing?
> 6. Any other rich result types detected?
> 7. Any structured data errors or warnings?

---

### PROMPT 9: Security & Manual Actions

> **Paste this into Claude Chrome Extension while on GSC "Security & Manual Actions":**
>
> Check the Security & Manual Actions reports:
>
> 1. Are there any manual actions against imisofts.com?
> 2. Are there any security issues detected?
> 3. Is the site flagged for any policy violations?

---

### PROMPT 10: Search Performance Summary

> **Paste this into Claude Chrome Extension while on GSC "Performance" report (last 3 months):**
>
> Analyze the search performance data for imisofts.com over the last 3 months:
>
> 1. Total clicks, impressions, average CTR, average position
> 2. Top 20 performing pages by clicks
> 3. Top 20 performing queries
> 4. Any pages with high impressions but low CTR (opportunity for title/description optimization)?
> 5. Any pages with declining clicks trend?
> 6. Mobile vs Desktop vs Tablet performance split
> 7. Top performing countries

---

## 4. TECHNICAL SEO AUDIT

### 4A. Sitemap Configuration
| Check | Status | Notes |
|---|---|---|
| Sitemap exists | PASS | `/sitemap.xml` with 252 URLs |
| Sitemap referenced in robots.txt | PASS | `Sitemap: https://imisofts.com/sitemap.xml` |
| All pages included | PASS | 38 core + 214 blog URLs = 252 |
| Proper lastmod dates | PASS | All set to 2026-03-10 |
| changefreq set | PASS | weekly/daily/monthly as appropriate |
| Priority values set | PASS | 1.0 homepage, 0.9 service, 0.7 blog |
| No non-canonical URLs in sitemap | PASS | All URLs match canonical tags |
| No noindex URLs in sitemap | PASS | Admin/client pages excluded |

### 4B. Robots.txt
| Check | Status | Notes |
|---|---|---|
| robots.txt exists | PASS | Accessible at root |
| Allows crawling | PASS | `User-agent: * / Allow: /` |
| Sitemap declared | PASS | Points to correct sitemap |
| No accidental blocks | PASS | No Disallow rules blocking content |

### 4C. Canonical Tags
| Check | Status | Notes |
|---|---|---|
| All pages have canonical | PASS | Self-referencing canonicals on all pages |
| Canonical matches URL | PASS | No mismatches found |
| HTTPS canonical | PASS | All use https:// |
| Trailing slash consistency | PASS | Blog uses trailing slash, pages don't |

### 4D. URL Structure
| Check | Status | Notes |
|---|---|---|
| Clean URLs | PASS | No query strings, no file extensions in URLs |
| Lowercase URLs | PASS | All lowercase |
| No special characters | PASS | Hyphens only |
| Trailing slash consistency | PASS | 301 redirects normalize trailing slashes |
| No duplicate URL patterns | PASS | Redirects handle /page vs /page/ |

### 4E. Redirect Configuration
| Check | Status | Notes |
|---|---|---|
| Trailing slash 301s | PASS | 27 trailing-slash redirects configured |
| Common misspelling 301s | PASS | /blogs -> /blog, /contact-us -> /contact, etc. |
| Old URL patterns | PASS | /home, /index, /index.html -> / |
| Security probe 410s | PASS | 80+ WordPress/CMS/exploit paths return 410 |
| No redirect chains | PASS | All redirects are single-hop |

---

## 5. ON-PAGE SEO AUDIT

### 5A. Title Tags
| Page | Title | Length | Status |
|---|---|---|---|
| Homepage | AI Automation Agency \| Cold Email & Growth \| imisofts | 60 | GOOD |
| Cold Email Marketing | Cold Email Marketing \| 95%+ Inbox Rate \| imisofts | 51 | GOOD |
| AI Automation | Top AI Automation Services \| Reduce Manual Work 70% in Weeks | 62 | OK (slightly long) |
| Blog | Blog \| imisofts - Cold Email Infrastructure & B2B Outbound | 60 | GOOD |
| All other pages | Checked | 50-65 | GOOD |

**Title Tag Summary:** All pages have unique, keyword-optimized titles within acceptable length.

### 5B. Meta Descriptions
| Page | Length | Status |
|---|---|---|
| Homepage | 156 chars | OPTIMAL |
| Cold Email Marketing | 150 chars | OPTIMAL |
| AI Automation | 152 chars | OPTIMAL |
| Blog Index | 145 chars | GOOD |
| Cold Email in 2026 (blog) | 108 chars | SHORT — could be longer |

**Meta Description Summary:** Most pages have optimal meta descriptions (150-160 chars). A few blog posts could be improved.

### 5C. H1 Tags
| Check | Status | Notes |
|---|---|---|
| Every page has H1 | PASS | All pages have a single H1 |
| H1 is unique per page | PASS | No duplicate H1s found |
| H1 contains target keyword | PASS | All H1s align with page topic |

### 5D. Open Graph Tags
| Check | Status | Notes |
|---|---|---|
| og:title | PASS | Present on all pages |
| og:description | PASS | Present on all pages |
| og:url | PASS | Present on all pages |
| og:type | PASS | "website" for pages, "article" for blog |
| og:image | PARTIAL | Missing on 8 pages (admin, client, policy pages) |
| og:site_name | PASS | "imisofts" on all pages |

### 5E. Twitter Card Tags
| Check | Status | Notes |
|---|---|---|
| twitter:card | PASS | "summary_large_image" on all pages |
| twitter:title | PASS | Present on all pages |
| twitter:description | PASS | Present on all pages |

---

## 6. STRUCTURED DATA AUDIT

### 6A. Schema Types Found
| Schema Type | Pages | Status |
|---|---|---|
| Organization | Homepage | PASS — comprehensive company info |
| Service/Product | Service pages | PASS — includes OfferCatalog with pricing |
| BlogPosting | All 213 blog posts | PASS — author, dates, wordCount |
| FAQPage | Select blog posts & pricing | PASS — great for SERP features |
| BreadcrumbList | Most pages | PASS |
| Person | Author page | PASS — Zeeshan Waheed with credentials |
| ProfessionalService | Contact page | PASS |
| LocalBusiness | Contact page | PASS |

### 6B. Structured Data Issues
| Issue | Severity | Details |
|---|---|---|
| Blog index missing Blog/CollectionPage schema | MEDIUM | /blog/ page lacks structured data |
| Blog posts missing author email in schema | LOW | Only name referenced, no social/email |
| Some service pages missing BreadcrumbList | LOW | Could improve navigation signals |

---

## 7. REDIRECT & CRAWL EFFICIENCY AUDIT

### 7A. 301 Redirects (URL Normalization)
- **27 trailing-slash redirects** for core pages
- **19 common misspelling/old-URL redirects** (blogs, contact-us, portfolio, etc.)
- All redirects are single-hop (no chains)

### 7B. 410 Gone Responses (Crawl Waste Prevention)
- **80+ security probe URLs** return 410 (WordPress, CMS, exploit paths)
- **14 file extension patterns** blocked (*.sql, *.bak, *.zip, etc.)
- **6 audit/report files** return 410
- This is excellent for crawl budget optimization

### 7C. Pages Intentionally NOT Indexed
| Page | Method | Status |
|---|---|---|
| /admin-login | X-Robots-Tag: noindex (via _headers) | CORRECT |
| /admin-dashboard | X-Robots-Tag: noindex (via _headers) | CORRECT |
| /client-login | X-Robots-Tag: noindex (via _headers) | CORRECT |
| /client-dashboard | X-Robots-Tag: noindex (via _headers) | CORRECT |
| /404 | X-Robots-Tag: noindex (via _headers) | CORRECT |

---

## 8. SECURITY HEADERS AUDIT

| Header | Status | Value |
|---|---|---|
| Strict-Transport-Security | PASS | max-age=31536000; includeSubDomains |
| X-Content-Type-Options | PASS | nosniff |
| X-Frame-Options | PASS | DENY |
| Referrer-Policy | PASS | strict-origin-when-cross-origin |
| Content-Security-Policy | PASS | Comprehensive CSP configured |
| Permissions-Policy | PASS | Restricts camera, microphone, geolocation |
| Cache-Control | PASS | Appropriate per content type |

---

## 9. ISSUES FOUND & RECOMMENDATIONS

### CRITICAL ISSUES
None found. The site has strong technical SEO foundations.

### MEDIUM PRIORITY ISSUES

| # | Issue | Impact | Recommendation |
|---|---|---|---|
| 1 | Blog index page (/blog/) missing structured data | May miss Blog/CollectionPage rich results | Add Blog or CollectionPage schema to /blog/index.html |
| 2 | 8 pages missing og:image | Poor social sharing appearance for admin/policy pages | Add og:image to privacy-policy, terms-of-service, cookie-policy, api-docs |
| 3 | 17 pages using generic og:image | Lower CTR on social shares | Create unique og:image for each service page |
| 4 | Some blog meta descriptions too short | Lower CTR in SERPs | Audit all blog meta descriptions, ensure 150-160 chars |

### LOW PRIORITY ISSUES

| # | Issue | Impact | Recommendation |
|---|---|---|---|
| 5 | Blog posts lack author social links in schema | Minor rich result opportunity | Add sameAs links to BlogPosting author |
| 6 | Some service pages missing BreadcrumbList | Minor navigation signal | Add BreadcrumbList to all service pages |
| 7 | No AggregateRating schema on hire pages | Missing star ratings in SERPs | Add review/rating schema if testimonials exist |
| 8 | RSS feed shows 99 posts, not all 213 | Some posts missing from feed distribution | Update feed.xml to include all posts or latest 50 |

---

## 10. ACTION ITEMS CHECKLIST

### Immediate Actions (Do in GSC)
- [ ] Submit sitemap (https://imisofts.com/sitemap.xml) if not already submitted
- [ ] Run URL Inspection on ALL 38 core pages — request indexing for any not indexed
- [ ] Run URL Inspection on all 28 newest "2026" blog posts — request indexing for any not indexed
- [ ] Run URL Inspection on all 12 new service pages — request indexing for any not indexed
- [ ] Check "Pages" report for any "Crawled - currently not indexed" URLs
- [ ] Check "Pages" report for any "Discovered - currently not indexed" URLs
- [ ] Check for any "Duplicate, Google chose different canonical" issues
- [ ] Verify Core Web Vitals are all "Good"
- [ ] Verify no manual actions or security issues
- [ ] Check all Enhancement reports for structured data errors

### Code Fixes (After GSC Audit)
- [ ] Add Blog/CollectionPage schema to /blog/index.html
- [ ] Add og:image to 8 pages missing it (policy pages, api-docs)
- [ ] Audit and fix any short meta descriptions on blog posts
- [ ] Update feed.xml with all latest posts
- [ ] Add BreadcrumbList to service pages missing it

### Monitoring (Ongoing)
- [ ] Check GSC weekly for new indexing issues
- [ ] Monitor Core Web Vitals monthly
- [ ] Re-submit sitemap after every batch of new blog posts
- [ ] Track "Pages" report for crawl budget issues
- [ ] Monitor rich results for new structured data errors

---

## APPENDIX: QUICK REFERENCE

### Total URL Count by Type
| Type | Count |
|---|---|
| Core service/content pages | 37 |
| Blog index | 1 |
| Blog posts | 213 |
| Author pages | 1 |
| **Total in Sitemap** | **252** |
| Non-indexed internal pages | 5 |
| **Total HTML files** | **257** |

### Key Files
| File | Purpose |
|---|---|
| /sitemap.xml | XML sitemap (252 URLs) |
| /robots.txt | Crawler directives |
| /feed.xml | RSS feed |
| /_redirects | 301/410 redirect rules |
| /_headers | Security & caching headers |
| /data/posts.json | Blog post metadata |
| /blog/posts-index.json | Blog post index (213 entries) |

---

*Report generated: March 12, 2026*
*Total pages audited: 252*
*Domain: imisofts.com*
