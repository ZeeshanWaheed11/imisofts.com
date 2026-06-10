#!/usr/bin/env python3
"""Idempotent article-structure normalizer + pre-publish validator (shared by builders)."""
import os, re, sys, glob, html as H, json as _json
DATELINE = re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\.?$')
AFF = ['get.apollo.io/u5ocuv7me9t2','refer.instantly.ai/oovph6ghwnaa','gohighlevel.com/?fp_ref=zeeshanwaheed','apify.com?fpr=rc63q','appsumo.8odi']
def slugify(t):
    t=re.sub(r'<[^>]+>','',t); t=H.unescape(t).lower()
    t=re.sub(r'[^a-z0-9]+','-',t).strip('-'); return (t[:60] or 'section')
def convert_bold_headings(body):
    used=set(re.findall(r'id="([^"]+)"', body))
    def repl(m):
        text=m.group(1).strip()
        if DATELINE.match(text): return m.group(0)
        base=slugify(text); sid=base; k=2
        while sid in used: sid=f"{base}-{k}"; k+=1
        used.add(sid); return f'<h2 id="{sid}">{text}</h2>'
    return re.sub(r'<p><strong>([^<]{3,70})</strong></p>', repl, body)
def build_toc_items(body, has_faq):
    items=''
    for sid,txt in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S):
        label=re.sub(r'<[^>]+>','',txt).strip()
        if label: items+=f'<li><a href="#{sid}">{label}</a></li>\n'
    if has_faq: items+='<li><a href="#faq">Frequently Asked Questions</a></li>\n'
    return items
def set_toc(doc, items):
    if not items.strip(): return doc
    return re.sub(r'(<ul class="toc-list">).*?(</ul>)', lambda m:m.group(1)+'\n'+items+m.group(2), doc, flags=re.S)
def find_body(doc):
    i=doc.find('<article')
    if i<0: return None
    bs=doc.find('>', i)+1; j=doc.find('</article>', bs)
    return (bs,j) if (bs>0 and j>0) else None
def process(doc):
    changed=False
    nc=doc.replace('500+ businesses','200+ businesses').replace('#F45407;">500+</div>','#F45407;">200+</div>')
    if nc!=doc: doc=nc; changed=True
    b=find_body(doc)
    if b:
        bs,j=b; head, body, tail = doc[:bs], doc[bs:j], doc[j:]
        body2=re.sub(r'\s*—\s*', ', ', convert_bold_headings(body))
        if body2!=body: doc=head+body2+tail; changed=True
        has_faq=('id="faq"' in doc) or ('class="faq-section"' in doc)
        nd=set_toc(doc, build_toc_items(body2, has_faq))
        if nd!=doc: doc=nd; changed=True
    return doc, changed
def validate_article(doc):
    """Return a list of CRITICAL problems (empty = OK). Used as a pre-publish gate."""
    p=[]
    if doc.count('<main')!=1 or doc.count('</main>')!=1: p.append('main tag count != 1')
    if len(re.findall(r'<h1[ >]',doc))!=1: p.append('h1 count != 1')
    b=find_body(doc); body=doc[b[0]:b[1]] if b else ''
    if not body: p.append('no <article> body')
    if '—' in body or '–' in body: p.append('em/en dash in body')
    if 'class="faq-section"' not in doc: p.append('no FAQ section')
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
        try: _json.loads(blk)
        except Exception: p.append('invalid JSON-LD'); break
    if 'affiliate-disclosure' in doc and not any(a in doc for a in AFF): p.append('disclosure without affiliate link')
    if '<ul class="toc-list">' in doc and body:
        toc=set(a for t in re.findall(r'<ul class="toc-list">(.*?)</ul>',doc,re.S) for a in re.findall(r'href="#([^"]+)"',t))
        bids=re.findall(r'<h2 id="([^"]+)"', body)
        if bids and not all(x in toc for x in bids): p.append('TOC missing headings')
    return p
def main():
    root=sys.argv[1] if len(sys.argv)>1 else '.'
    n=0
    for f in sorted(glob.glob(os.path.join(root,'blog','*','index.html'))):
        d=open(f,encoding='utf-8').read()
        if '<title>Redirecting' in d or 'http-equiv="refresh"' in d: continue
        nd,ch=process(d)
        if ch: open(f,'w',encoding='utf-8').write(nd); n+=1
    print(f"fixed {n} articles")
if __name__=='__main__': main()
