#!/usr/bin/env python3
"""
imisofts news publishing pipeline.
Input:  content/news/<slug>.json  (one file per article: metadata + HTML body)
Output: blog/<slug>/index.html (built from the live template) + updated
        sitemap.xml, news-sitemap.xml, feed.xml, blog/posts-index.json, blog/index.html

Run from repo root:  python3 ops/build_news.py
Idempotent: only builds articles whose page is missing or whose source is newer,
and only adds index entries that are not already present.
"""
import json, re, os, glob, sys, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'blog', 'signal-based-outbound-news-june-2026', 'index.html')
CONTENT_DIR = os.path.join(ROOT, 'content', 'news')

def esc(t): return (t or '').replace('&','&amp;')

def submit_indexnow(urls):
    """Best-effort IndexNow ping so Bing (and ChatGPT retrieval) pick up new/updated pages fast. Never breaks the build."""
    import urllib.request
    KEY="8f91c62405dc13875a9db237c23b51f6"
    urls=list(dict.fromkeys(urls))
    try:
        payload=json.dumps({"host":"imisofts.com","key":KEY,"keyLocation":f"https://imisofts.com/{KEY}.txt","urlList":urls}).encode()
        req=urllib.request.Request("https://api.indexnow.org/indexnow",data=payload,headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
        with urllib.request.urlopen(req,timeout=20) as r:
            print("indexnow: submitted %d url(s), HTTP %s"%(len(urls), getattr(r,"status",r.getcode())))
    except Exception as e:
        print("indexnow: skipped (%s)"%e)

import datetime as _dtmod
def human_date(iso):
    return _dtmod.date.fromisoformat(iso[:10]).strftime('%B %-d, %Y')

def fix_chrome(s, date_iso):
    """Heal the visible byline date and the client-count claim. Idempotent."""
    dp=date_iso[:10]
    s=re.sub(r'<time datetime="[^"]*">[^<]*</time>', '<time datetime="%s">%s</time>'%(dp, human_date(dp)), s, count=1)
    s=s.replace('Join 500+ businesses','Join 200+ businesses')
    s=s.replace('#F45407;">500+</div>','#F45407;">200+</div>')
    return s

def faq_items_html(faqs):
    out=''
    for q,a in faqs:
        out+=f'<div class="faq-item"><button class="faq-question">{q}<span>+</span></button><div class="faq-answer"><div class="faq-answer-inner"><p>{a}</p></div></div></div>'
    return out

def cta_html(h2):
    return (f'<div class="blog-cta-banner"><h2>{h2}</h2>'
            f'<p>We design, build, and run it for you, integrated with the tools you already use. Free audit in 24 hours.</p>'
            f'<a href="/free-audit" class="cta-btn">Get Your Free Audit <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg></a></div>')

def build_article(meta, tpl):
    slug=meta['slug']; URL=f'https://imisofts.com/blog/{slug}/'
    T=meta['title']; TH=esc(T); DESC=meta['desc']; DATE=meta['date']; KW=meta.get('keywords','')
    faqs=[(q,a) for q,a in meta['faqs']]
    s=tpl
    s=s.replace('https://imisofts.com/blog/signal-based-outbound-news-june-2026/',URL)
    s=re.sub(r'<title>[^<]*</title>',f'<title>{TH}</title>',s,count=1)
    for pat,val in [('description',DESC),('og:description',DESC),('twitter:description',DESC)]:
        s=re.sub(r'(<meta (?:property|name)="'+pat+r'" content=")[^"]*(")',lambda m:m.group(1)+DESC+m.group(2),s,count=1)
    for pat in ['og:title','twitter:title']:
        s=re.sub(r'(<meta (?:property|name)="'+pat+r'" content=")[^"]*(")',lambda m:m.group(1)+TH+m.group(2),s,count=1)
    news=json.dumps({"@context":"https://schema.org","@type":"NewsArticle","headline":T,"description":DESC,"url":URL,"mainEntityOfPage":URL,"datePublished":DATE,"dateModified":DATE,"author":{"@type":"Person","name":"Zeeshan Waheed","url":"https://imisofts.com/author/zeeshan-waheed/"},"publisher":{"@type":"Organization","name":"imisofts","url":"https://imisofts.com","logo":{"@type":"ImageObject","url":"https://imisofts.com/og-image.jpg"}},"image":"https://imisofts.com/og-image.jpg","articleSection":"Industry News","keywords":KW},indent=1)
    crumb=json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://imisofts.com/"},{"@type":"ListItem","position":2,"name":"Blog","item":"https://imisofts.com/blog/"},{"@type":"ListItem","position":3,"name":"Industry News","item":"https://imisofts.com/blog/?cat=industry-news"},{"@type":"ListItem","position":4,"name":T,"item":URL}]},indent=1)
    faqsch=json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},indent=1)
    def repl(m):
        try: o=json.loads(m.group(1))
        except: return m.group(0)
        t=o.get('@type')
        nb={'NewsArticle':news,'BreadcrumbList':crumb,'FAQPage':faqsch}.get(t)
        return '<script type="application/ld+json">\n'+nb+'\n</script>' if nb else m.group(0)
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',repl,s,flags=re.S)
    s=re.sub(r'<span class="current">[^<]*</span>',f'<span class="current">{TH}</span>',s,count=1)
    s=re.sub(r'<h1>[^<]*</h1>',f'<h1>{TH}</h1>',s,count=1)
    faq_section=f'<section class="faq-section" id="faq">\n<h2>Frequently Asked Questions</h2>\n{faq_items_html(faqs)}\n</section>'
    body=meta['body']+'\n'+cta_html(meta.get('cta','Want this built for your business?'))+'\n'+faq_section
    i=s.find('<article class="article-content">'); j=s.find('</article>')
    s=s[:i]+'<article class="article-content">\n'+body+'\n'+s[j:]
    s=fix_chrome(s, DATE)
    s=re.sub(r'(\d+)\s*min read', '%d min read'%meta.get('read_time',6), s, count=1)
    # validate
    mainpart=s[s.find('<article'):s.find('</article>')]
    assert mainpart.count(chr(8212))==0, f'{slug}: em-dash in body'
    assert s.count('<main')==1 and s.count('</main>')==1, f'{slug}: main tag issue'
    nfaq=mainpart.count('class="faq-item"')
    assert nfaq==len(faqs), f'{slug}: faq count mismatch {nfaq} vs {len(faqs)}'
    return s

def main():
    if not os.path.exists(TEMPLATE):
        print('ERROR: template missing', TEMPLATE); return 1
    tpl=open(TEMPLATE,encoding='utf-8').read()
    # Heal byline dates + client-count claim across ALL existing NewsArticle pages (self-healing backfill)
    for _hf in glob.glob(os.path.join(ROOT,'blog','*','index.html')):
        try: _h=open(_hf,encoding='utf-8').read()
        except: continue
        if '"NewsArticle"' not in _h: continue
        _m=re.search(r'"datePublished"\s*:\s*"([^"]+)"',_h)
        if not _m: continue
        _nh=fix_chrome(_h,_m.group(1))
        if _nh!=_h:
            open(_hf,'w',encoding='utf-8').write(_nh); print('healed byline:',_hf)
    metas=[]
    for f in sorted(glob.glob(os.path.join(CONTENT_DIR,'*.json'))):
        meta=json.load(open(f,encoding='utf-8'))
        metas.append(meta)
        out=os.path.join(ROOT,'blog',meta['slug'],'index.html')
        if (not os.path.exists(out)) or (os.path.getmtime(f) > os.path.getmtime(out)):
            os.makedirs(os.path.dirname(out),exist_ok=True)
            open(out,'w',encoding='utf-8').write(build_article(meta,tpl))
            print('built blog/%s/index.html'%meta['slug'])
    if not metas:
        print('no content files'); return 0
    # ---- posts-index.json ----
    pj=os.path.join(ROOT,'blog','posts-index.json')
    d=json.load(open(pj,encoding='utf-8')); posts=d if isinstance(d,list) else d['posts']
    have={p.get('slug') for p in posts}
    for meta in sorted(metas,key=lambda m:(m['date'],m.get('time','')), reverse=True):
        if meta['slug'] in have: continue
        kw=meta.get('keywords','')
        posts.insert(0,{"number":0,"filename":f"000-{meta['slug']}.txt","title":meta['title'],"meta_description":meta['desc'],"url_slug":f"/blog/{meta['slug']}","primary_keyword":kw.split(',')[0].strip(),"secondary_keywords":", ".join(k.strip() for k in kw.split(',')[1:]),"category":"Industry News","word_count_target":meta.get('word_count',900),"schema_type":"NewsArticle","author":"Zeeshan Waheed","date":meta['date'],"slug":meta['slug'],"word_count":meta.get('word_count',900),"read_time":meta.get('read_time',6),"has_faq":True,"category_normalized":"industry-news"})
    json.dump(posts if isinstance(d,list) else {**d,'posts':posts}, open(pj,'w',encoding='utf-8'), indent=2, ensure_ascii=False)
    # ---- sitemap.xml ----
    sm=open(os.path.join(ROOT,'sitemap.xml')).read()
    add=''
    for meta in metas:
        u=f'https://imisofts.com/blog/{meta["slug"]}/'
        if u not in sm: add+=f'<url>\n<loc>{u}</loc>\n<lastmod>{meta["date"]}</lastmod>\n<changefreq>monthly</changefreq>\n<priority>0.7</priority>\n</url>\n'
    if add: sm=sm.replace('</urlset>',add+'</urlset>'); open(os.path.join(ROOT,'sitemap.xml'),'w').write(sm)
    # ---- news-sitemap.xml: merge existing fresh entries + new specs, keep only <48h of newest ----
    def dt(m): return datetime.datetime.fromisoformat(m['date']+'T'+m.get('time','09:00')+':00')
    entries={}  # loc -> (datetime, title)
    nsp=os.path.join(ROOT,'news-sitemap.xml')
    if os.path.exists(nsp):
        old_ns=open(nsp).read()
        for blk in re.findall(r'<url>.*?</url>', old_ns, re.S):
            loc=re.search(r'<loc>(.*?)</loc>',blk); pd=re.search(r'<news:publication_date>(.*?)</news:publication_date>',blk); ti=re.search(r'<news:title>(.*?)</news:title>',blk)
            if loc and pd:
                try: d=datetime.datetime.fromisoformat(pd.group(1).replace('Z','+00:00')).replace(tzinfo=None)
                except: continue
                entries[loc.group(1)]=(d, ti.group(1) if ti else '')
    for m in metas:
        u=f'https://imisofts.com/blog/{m["slug"]}/'
        entries[u]=(dt(m), esc(m['title']))
    newest=max(d for d,_ in entries.values()) if entries else datetime.datetime.now()
    fresh={u:(d,t) for u,(d,t) in entries.items() if (newest-d).total_seconds()<=48*3600}
    nsurls=''
    for u,(d,t) in sorted(fresh.items(), key=lambda kv: kv[1][0], reverse=True):
        nsurls+=f'<url>\n<loc>{u}</loc>\n<news:news><news:publication><news:name>imisofts</news:name><news:language>en</news:language></news:publication>\n<news:publication_date>{d.isoformat()}+04:00</news:publication_date>\n<news:title>{t}</news:title></news:news>\n</url>\n'
    open(nsp,'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n'+nsurls+'</urlset>\n')
    fresh_count=len(fresh)
    # ---- feed.xml ----
    f=open(os.path.join(ROOT,'feed.xml')).read(); m0=re.search(r'<item>.*?</item>',f,re.S)
    if m0:
        items=''
        for meta in sorted(metas,key=lambda m:(m['date'],m.get('time','')), reverse=True):
            u=f'https://imisofts.com/blog/{meta["slug"]}/'
            if u in f: continue
            items+=f'<item>\n<title>{esc(meta["title"])}</title>\n<link>{u}</link>\n<guid isPermaLink="true">{u}</guid>\n<pubDate>{meta["date"]}</pubDate>\n<description>{esc(meta["desc"])}</description>\n</item>\n'
        if items: f=f.replace(m0.group(0),items+m0.group(0),1); open(os.path.join(ROOT,'feed.xml'),'w').write(f)
    # ---- blog/index.html cards ----
    subprocess.run([sys.executable, os.path.join(ROOT,'ops','sync_blog_index.py')], check=False)
    print('indexes updated; news-sitemap has %d fresh url(s)'%fresh_count)
    # ---- IndexNow auto-submit (best-effort; pings Bing -> ChatGPT retrieval) ----
    inurls=[f'https://imisofts.com/blog/{m["slug"]}/' for m in metas]+['https://imisofts.com/','https://imisofts.com/blog/']
    submit_indexnow(inurls)
    return 0

if __name__=='__main__':
    sys.exit(main())
