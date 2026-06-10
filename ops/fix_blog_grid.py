import re, sys, os
ROOT = sys.argv[1] if len(sys.argv)>1 else '.'
IDX = os.path.join(ROOT, 'blog', 'index.html')
def match_div_end(s, start):
    depth=0
    for m in re.finditer(r'<div\b|</div>', s[start:]):
        if m.group(0)=='</div>':
            depth-=1
            if depth==0: return start+m.end()
        else: depth+=1
    return -1
def fix(s):
    lmw=s.find('<div class="load-more-wrap"')
    if lmw<0: return s, 0
    end=match_div_end(s, lmw)
    block=s[lmw:end]
    cards=re.findall(r'<a\b[^>]*class="post-card"[^>]*>.*?</a>', block, re.S)
    if not cards: 
        # empty wrap: just remove it
        return (s[:lmw].rstrip()+'\n'+s[end:]), 0
    s2 = s[:lmw].rstrip() + '\n' + s[end:]            # remove the whole load-more-wrap
    pg = s2.find('<div class="posts-grid"')
    pgend = match_div_end(s2, pg)
    close = pgend - len('</div>')
    s2 = s2[:close] + '\n' + '\n'.join(cards) + '\n' + s2[close:]   # append cards into the grid
    return s2, len(cards)
if __name__=='__main__':
    s=open(IDX,encoding='utf-8').read()
    ns,n=fix(s)
    if ns!=s: open(IDX,'w',encoding='utf-8').write(ns); print(f"moved {n} cards into posts-grid, removed load-more-wrap")
    else: print("no change (grid already clean)")
