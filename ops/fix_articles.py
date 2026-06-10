#!/usr/bin/env python3
"""Idempotent article-structure normalizer for imisofts.com blog (shared by the builders).
- Convert news-style bold-paragraph headings (<p><strong>X</strong></p>) to real <h2 id="slug">.
- Build the standard Table of Contents (<ul class="toc-list">) from body <h2 id> headings + FAQ.
- Normalize the client-count claim (500+ businesses -> 200+ businesses; clients stat box).
- Conservatively replace em dashes in the article body (house style; leaves en-dash ranges).
Leaves articles that use the older curated <div class="toc"><a class="toc-link"> format untouched.
Importable: call process(doc)->(doc, changed). Run standalone to backfill all posts.
"""
import os, re, sys, glob, html as H
DATELINE = re.compile(r'^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\.?$')
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
