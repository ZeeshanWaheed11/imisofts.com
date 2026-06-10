import os, re, sys, glob
ROOT = sys.argv[1] if len(sys.argv)>1 else '.'
AFF = ['get.apollo.io/u5ocuv7me9t2','refer.instantly.ai/oovph6ghwnaa',
       'gohighlevel.com/?fp_ref=zeeshanwaheed','apify.com?fpr=rc63q','appsumo.8odi']
DISC_RE = re.compile(r'<p class="affiliate-disclosure"[^>]*>.*?</p>\s*', re.S)
def cta(url, label):
    return (f'<p class="aff-cta" style="margin:0 0 22px;"><a href="{url}" target="_blank" '
            f'rel="noopener noreferrer sponsored" style="display:inline-block;background:#F45407;'
            f'color:#fff;font-weight:600;padding:11px 20px;border-radius:8px;text-decoration:none;">{label}</a></p>')
def process(doc, slug):
    has_aff = any(a in doc for a in AFF)
    has_disc = 'affiliate-disclosure' in doc
    if has_aff or not has_disc:
        return doc, None            # not an orphan
    if 'apollo' in slug:
        url, label = 'https://get.apollo.io/u5ocuv7me9t2', 'Try Apollo free &rarr;'
    elif 'instantly' in slug:
        url, label = 'https://refer.instantly.ai/oovph6ghwnaa', 'Try Instantly free &rarr;'
    else:
        nd = DISC_RE.sub('', doc, count=1)
        return nd, ('removed' if nd != doc else None)
    m = DISC_RE.search(doc)
    if not m: return doc, None
    nd = doc[:m.end()] + cta(url, label) + '\n' + doc[m.end():]
    return nd, 'cta'
n_cta = n_rm = 0; cta_list=[]; rm_list=[]
for f in sorted(glob.glob(os.path.join(ROOT,'blog','*','index.html'))):
    d = open(f, encoding='utf-8').read()
    if '<title>Redirecting' in d or 'http-equiv="refresh"' in d: continue
    slug = os.path.basename(os.path.dirname(f))
    nd, action = process(d, slug)
    if action:
        open(f,'w',encoding='utf-8').write(nd)
        if action=='cta': n_cta+=1; cta_list.append(slug)
        else: n_rm+=1; rm_list.append(slug)
print(f"CTAs added (re-monetized): {n_cta}")
print("  ", cta_list)
print(f"orphan disclosures removed: {n_rm}")
print("  ", rm_list)
