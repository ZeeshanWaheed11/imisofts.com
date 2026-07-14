#!/usr/bin/env python3
"""
imisofts affiliate / evergreen review pipeline (sibling of build_news.py).
Input:  content/affiliate/<slug>.json
Output: blog/<slug>/index.html built from the live template, but with Article
        schema (NOT NewsArticle), category "Reviews", an auto affiliate disclosure,
        and sponsored-normalized affiliate links. Updates sitemap.xml, posts-index.json,
        blog/index.html, feed.xml. Deliberately NOT added to news-sitemap.xml (evergreen).
Run from repo root: python3 ops/build_affiliate.py
Idempotent: builds pages missing/newer; only adds index entries not already present.
"""
import json, re, os, glob, sys, subprocess
import datetime as _dtmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'blog', 'signal-based-outbound-news-june-2026', 'index.html')
CONTENT_DIR = os.path.join(ROOT, 'content', 'affiliate')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DISCLOSURE = ('<p class="affiliate-disclosure" style="font-size:14px;line-height:1.6;'
              'color:#475569;background:#f8fafc;border-left:3px solid #F45407;'
              'padding:11px 15px;border-radius:6px;margin:0 0 22px;">'
              '<strong>Affiliate disclosure:</strong> some links in this article are partner links. '
              'If you start a paid plan through them, imisofts may earn a commission at no extra cost to you. '
              'We only recommend tools we actually use to run client campaigns.</p>')

def esc(t): return (t or '').replace('&','&amp;')
def human_date(iso): return _dtmod.date.fromisoformat(iso[:10]).strftime('%B %-d, %Y')

def submit_indexnow(urls):
    import urllib.request
    KEY="8f91c62405dc13875a9db237c23b51f6"; urls=list(dict.fromkeys(urls))
    try:
        payload=json.dumps({"host":"imisofts.com","key":KEY,"keyLocation":f"https://imisofts.com/{KEY}.txt","urlList":urls}).encode()
        req=urllib.request.Request("https://api.indexnow.org/indexnow",data=payload,headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
        with urllib.request.urlopen(req,timeout=20) as r: print("indexnow: submitted %d url(s)"%len(urls))
    except Exception as e: print("indexnow: skipped (%s)"%e)

def faq_items_html(faqs):
    return ''.join(f'<div class="faq-item"><button class="faq-question">{q}<span>+</span></button><div class="faq-answer"><div class="faq-answer-inner"><p>{a}</p></div></div></div>' for q,a in faqs)

def cta_html(h2):
    return (f'<div class="blog-cta-banner"><h2>{h2}</h2>'
            f'<p>We design, build, and run it for you, integrated with the tools you already use. Free audit in 24 hours.</p>'
            f'<a href="/free-audit" class="cta-btn">Get Your Free Audit <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg></a></div>')

def normalize_affiliate(body, aff_url):
    if not aff_url: return body
    rx=re.compile(r'<a\b[^>]*?href="'+re.escape(aff_url)+r'"[^>]*>')
    def f(m):
        sm=re.search(r'style="[^"]*"',m.group(0)); style=(' '+sm.group(0)) if sm else ''
        return f'<a href="{aff_url}" target="_blank" rel="noopener noreferrer sponsored"{style}>'
    return rx.sub(f, body)

def build_article(meta, tpl):
    slug=meta['slug']; URL=f'https://imisofts.com/blog/{slug}/'
    T=meta['title']; TH=esc(T); DESC=meta['desc']; DATE=meta['date']; KW=meta.get('keywords','')
    CAT=meta.get('category','Reviews'); CATN=CAT.lower().replace(' ','-')
    faqs=[(q,a) for q,a in meta['faqs']]
    s=tpl
    s=s.replace('https://imisofts.com/blog/signal-based-outbound-news-june-2026/',URL)
    s=re.sub(r'<title>[^<]*</title>',f'<title>{TH}</title>',s,count=1)
    for pat in ['description','og:description','twitter:description']:
        s=re.sub(r'(<meta (?:property|name)="'+pat+r'" content=")[^"]*(")',lambda m:m.group(1)+DESC+m.group(2),s,count=1)
    for pat in ['og:title','twitter:title']:
        s=re.sub(r'(<meta (?:property|name)="'+pat+r'" content=")[^"]*(")',lambda m:m.group(1)+TH+m.group(2),s,count=1)
    art=json.dumps({"@context":"https://schema.org","@type":"Article","headline":T,"description":DESC,"url":URL,"mainEntityOfPage":URL,"datePublished":DATE,"dateModified":DATE,"author":{"@type":"Person","name":"Zeeshan Waheed","url":"https://imisofts.com/author/zeeshan-waheed/"},"publisher":{"@type":"Organization","name":"imisofts","url":"https://imisofts.com","logo":{"@type":"ImageObject","url":"https://imisofts.com/og-image.jpg"}},"image":"https://imisofts.com/og-image.jpg","articleSection":CAT,"keywords":KW},indent=1)
    crumb=json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://imisofts.com/"},{"@type":"ListItem","position":2,"name":"Blog","item":"https://imisofts.com/blog/"},{"@type":"ListItem","position":3,"name":CAT,"item":f"https://imisofts.com/blog/?cat={CATN}"},{"@type":"ListItem","position":4,"name":T,"item":URL}]},indent=1)
    faqsch=json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]},indent=1)
    def repl(m):
        try: o=json.loads(m.group(1))
        except: return m.group(0)
        nb={'NewsArticle':art,'Article':art,'BreadcrumbList':crumb,'FAQPage':faqsch}.get(o.get('@type'))
        return '<script type="application/ld+json">\n'+nb+'\n</script>' if nb else m.group(0)
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',repl,s,flags=re.S)
    s=s.replace('/blog/?cat=industry-news','/blog/?cat='+CATN)
    s=s.replace('>Industry News</a>','>'+CAT+'</a>')
    s=re.sub(r'<span class="current">[^<]*</span>',f'<span class="current">{TH}</span>',s,count=1)
    s=re.sub(r'<h1>[^<]*</h1>',f'<h1>{TH}</h1>',s,count=1)
    faq_section=f'<section class="faq-section" id="faq">\n<h2>Frequently Asked Questions</h2>\n{faq_items_html(faqs)}\n</section>'
    body=normalize_affiliate(meta['body'], meta.get('affiliate_url',''))
    body=DISCLOSURE+'\n'+body+'\n'+cta_html(meta.get('cta','Want this set up for your business?'))+'\n'+faq_section
    i=s.find('<article class="article-content">'); j=s.find('</article>')
    s=s[:i]+'<article class="article-content">\n'+body+'\n'+s[j:]
    s=re.sub(r'<time datetime="[^"]*">[^<]*</time>','<time datetime="%s">%s</time>'%(DATE[:10],human_date(DATE[:10])),s,count=1)
    s=re.sub(r'(\d+)\s*min read','%d min read'%meta.get('read_time',8),s,count=1)
    mainpart=s[s.find('<article'):s.find('</article>')]
    assert mainpart.count(chr(8212))==0, f'{slug}: em-dash in body'
    assert s.count('<main')==1 and s.count('</main>')==1, f'{slug}: main tag issue'
    assert mainpart.count('class="faq-item"')==len(faqs), f'{slug}: faq count mismatch'
    assert 'affiliate-disclosure' in s, f'{slug}: disclosure missing'
    if meta.get('affiliate_url'): assert meta['affiliate_url'] in s, f'{slug}: affiliate url missing'
    _probs=[]
    try:
        import fix_articles; s=fix_articles.process(s)[0]; _probs=fix_articles.validate_article(s)
    except Exception as _e:
        print('post-process skipped:', _e); _probs=[]
    if _probs:
        raise AssertionError("%s failed QA: %s" % (slug, "; ".join(_probs)))
    return s

def main():
    if not os.path.exists(TEMPLATE): print('ERROR: template missing'); return 1
    if not os.path.isdir(CONTENT_DIR): print('no affiliate content dir'); return 0
    tpl=open(TEMPLATE,encoding='utf-8').read(); metas=[]
    for f in sorted(glob.glob(os.path.join(CONTENT_DIR,'*.json'))):
        meta=json.load(open(f,encoding='utf-8'))
        out=os.path.join(ROOT,'blog',meta['slug'],'index.html')
        if (not os.path.exists(out)) or (os.path.getmtime(f)>os.path.getmtime(out)):
            try:
                _html=build_article(meta,tpl)
            except Exception as _qe:
                print('QA BLOCK %s: %s'%(meta.get('slug','?'), _qe)); continue
            os.makedirs(os.path.dirname(out),exist_ok=True)
            open(out,'w',encoding='utf-8').write(_html); print('built blog/%s/index.html'%meta['slug'])
        metas.append(meta)
    if not metas: print('no content files'); return 0
    pj=os.path.join(ROOT,'blog','posts-index.json')
    d=json.load(open(pj,encoding='utf-8')); posts=d if isinstance(d,list) else d['posts']
    have={p.get('slug') for p in posts}
    for meta in sorted(metas,key=lambda m:m['date'],reverse=True):
        if meta['slug'] in have:
            # REFRESH: spec already indexed. Keep the card in sync with the spec
            # (date, title, desc, word count) and re-sort it to the front when the
            # date moved forward, so a refreshed evergreen post is not stranded.
            for i,pp in enumerate(posts):
                if pp.get('slug')!=meta['slug']: continue
                changed = (pp.get('date')!=meta['date'] or pp.get('title')!=meta['title'] or pp.get('meta_description')!=meta['desc'])
                if changed:
                    pp['date']=meta['date']; pp['title']=meta['title']; pp['meta_description']=meta['desc']
                    pp['word_count']=meta.get('word_count',pp.get('word_count',1500))
                    pp['read_time']=meta.get('read_time',pp.get('read_time',8))
                    posts.insert(0,posts.pop(i))
                    print('refreshed index entry %s -> %s'%(meta['slug'],meta['date']))
                break
            continue
        kw=meta.get('keywords',''); CAT=meta.get('category','Reviews')
        posts.insert(0,{"number":0,"filename":f"000-{meta['slug']}.txt","title":meta['title'],"meta_description":meta['desc'],"url_slug":f"/blog/{meta['slug']}","primary_keyword":kw.split(',')[0].strip(),"secondary_keywords":", ".join(k.strip() for k in kw.split(',')[1:]),"category":CAT,"word_count_target":meta.get('word_count',1500),"schema_type":"Article","author":"Zeeshan Waheed","date":meta['date'],"slug":meta['slug'],"word_count":meta.get('word_count',1500),"read_time":meta.get('read_time',8),"has_faq":True,"category_normalized":CAT.lower().replace(' ','-')})
    json.dump(posts if isinstance(d,list) else {**d,'posts':posts},open(pj,'w',encoding='utf-8'),indent=2,ensure_ascii=False)
    sm=open(os.path.join(ROOT,'sitemap.xml')).read(); add=''
    for meta in metas:
        u=f'https://imisofts.com/blog/{meta["slug"]}/'
        if u not in sm:
            add+=f'<url>\n<loc>{u}</loc>\n<lastmod>{meta["date"]}</lastmod>\n<changefreq>monthly</changefreq>\n<priority>0.7</priority>\n</url>\n'
        else:
            # REFRESH: keep <lastmod> equal to the spec date (idempotent: no diff
            # unless the spec date actually moved), so refreshed evergreen posts
            # send a real freshness signal instead of a stale one.
            def _bump(m,_d=meta["date"]):
                return re.sub(r'<lastmod>[^<]*</lastmod>','<lastmod>%s</lastmod>'%_d,m.group(0),count=1)
            sm=re.sub(r'<url>\s*<loc>'+re.escape(u)+r'</loc>.*?</url>',_bump,sm,count=1,flags=re.S)
    open(os.path.join(ROOT,'sitemap.xml'),'w').write(sm.replace('</urlset>',add+'</urlset>') if add else sm)
    try:
        ff=open(os.path.join(ROOT,'feed.xml')).read(); m0=re.search(r'<item>.*?</item>',ff,re.S)
        if m0:
            items=''
            for meta in sorted(metas,key=lambda m:m['date'],reverse=True):
                u=f'https://imisofts.com/blog/{meta["slug"]}/'
                if u in ff: continue
                items+=f'<item>\n<title>{esc(meta["title"])}</title>\n<link>{u}</link>\n<guid isPermaLink="true">{u}</guid>\n<pubDate>{meta["date"]}</pubDate>\n<description>{esc(meta["desc"])}</description>\n</item>\n'
            if items: open(os.path.join(ROOT,'feed.xml'),'w').write(ff.replace(m0.group(0),items+m0.group(0),1))
    except Exception as e: print('feed skip',e)
    subprocess.run([sys.executable,os.path.join(ROOT,'ops','sync_blog_index.py')],check=False)
    submit_indexnow([f'https://imisofts.com/blog/{m["slug"]}/' for m in metas]+['https://imisofts.com/','https://imisofts.com/blog/'])
    print('affiliate build done: %d spec(s)'%len(metas)); return 0

if __name__=='__main__': sys.exit(main())
