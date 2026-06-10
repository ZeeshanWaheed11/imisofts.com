import re, sys, os
ROOT = sys.argv[1] if len(sys.argv)>1 else '.'
IDX = os.path.join(ROOT, 'blog', 'index.html')
BTN = '<div class="load-more-wrap">\n<button class="load-more-btn" id="loadMoreBtn">Load More Articles</button>\n</div>'
def match_div_end(s, start):
    d=0
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        if m.group(0)=='</div>':
            d-=1
            if d==0: return start+m.end()
        else: d+=1
    return -1
def fix(s):
    moved=0
    lmw=s.find('<div class="load-more-wrap"')
    if lmw>=0:
        end=match_div_end(s, lmw); block=s[lmw:end]
        cards=re.findall(r'<a\b[^>]*class="post-card"[^>]*>.*?</a>', block, re.S)
        if cards:                                   # cards stranded in the wrap -> move into grid, keep button
            s = s[:lmw] + BTN + s[end:]
            pg=s.find('<div class="posts-grid"'); pgend=match_div_end(s,pg); close=pgend-len('</div>')
            s = s[:close] + '\n' + '\n'.join(cards) + '\n' + s[close:]
            moved=len(cards)
    if 'load-more-btn' not in s:                    # button missing (blog.js needs it) -> add after the grid
        pg=s.find('<div class="posts-grid"'); pgend=match_div_end(s,pg)
        s = s[:pgend] + '\n' + BTN + '\n' + s[pgend:]
        moved = moved or -1
    return s, moved
if __name__=='__main__':
    s=open(IDX,encoding='utf-8').read()
    ns,n=fix(s)
    if ns!=s: open(IDX,'w',encoding='utf-8').write(ns); print(f"grid fixed (moved/restored={n})")
    else: print("no change")
