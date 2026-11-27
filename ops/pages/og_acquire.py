"""Branded share image for /acquire (1200x630). Run after build_acquire.py so the article count matches."""
import json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the repo root
F=lambda w,s: ImageFont.truetype(os.path.join(ROOT,'ops','fonts','Inter-%d.ttf'%w), s)
ORANGE=(244,84,7); INK=(15,23,42); MUTED=(102,112,133)
S=2  # supersample
W,H=1200*S,630*S
posts=json.load(open(os.path.join(ROOT,'blog','posts-index.json')))
n=len(posts if isinstance(posts,list) else posts.get('posts',[])); ARTICLES='%d+'%(n//10*10)

img=Image.new('RGB',(W,H),'#ffffff'); d=ImageDraw.Draw(img)
# soft warm gradient, top to bottom
for y in range(H):
    t=y/H; c=tuple(int(a+(b-a)*t) for a,b in zip((255,255,255),(255,246,241)))
    d.line([(0,y),(W,y)],fill=c)

def mark(draw, ox, oy, k, fill):
    # logo mark geometry from index.html (viewBox 0 0 900 256)
    draw.ellipse([ox+(48-18)*k, oy+(170-18)*k, ox+(48+18)*k, oy+(170+18)*k], fill=fill)
    for pts in ([(84,84),(136,84),(118,188),(66,188)], [(146,84),(198,84),(180,188),(128,188)]):
        draw.polygon([(ox+x*k, oy+y*k) for x,y in pts], fill=fill)

# faint big mark, right
ov=Image.new('RGBA',(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
mark(od, 560*S, -150*S, 4.6*S, ORANGE+(16,))
img=Image.alpha_composite(img.convert('RGBA'),ov)

# browser frame with the homepage screenshot, right side, bleeding off the edge
shot=Image.open(os.path.join(ROOT,'assets','acquire','home.webp')).convert('RGB')
fw=640*S; bar=34*S; sh=int(fw*shot.size[1]/shot.size[0]); fh=bar+sh
frame=Image.new('RGBA',(fw,fh),(255,255,255,255)); fd=ImageDraw.Draw(frame)
fd.rectangle([0,0,fw,bar],fill=(246,247,249)); fd.line([(0,bar),(fw,bar)],fill=(236,239,243),width=S)
for i in range(3): fd.ellipse([ (16+i*15)*S, 13*S, (16+i*15+9)*S, 22*S], fill=(217,221,227))
fd.rounded_rectangle([70*S,8*S,300*S,26*S],radius=6*S,fill=(255,255,255),outline=(231,234,238),width=S)
fd.text((80*S,10*S),'imisofts.com',font=F(500,12*S),fill=MUTED)
frame.paste(shot.resize((fw,sh),Image.LANCZOS),(0,bar))
mask=Image.new('L',(fw,fh),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,fw-1,fh-1],radius=14*S,fill=255)
fx,fy=690*S,112*S
shadow=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(shadow)
sd.rounded_rectangle([fx,fy+26*S,fx+fw,fy+fh+26*S],radius=14*S,fill=(15,23,42,70))
shadow=shadow.filter(ImageFilter.GaussianBlur(26*S))
img=Image.alpha_composite(img,shadow)
img.paste(frame,(fx,fy),mask)
d=ImageDraw.Draw(img)
d.rounded_rectangle([fx,fy,fx+fw-1,fy+fh-1],radius=14*S,outline=(231,234,238),width=S)

# logo lockup, top left
mark(d, 64*S-30*0.42*S, 52*S-84*0.42*S, 0.42*S, ORANGE)
d.text((64*S+ (200-30)*0.42*S, 52*S-84*0.42*S + 188*0.42*S), 'imisofts', font=F(700,int(96*0.42*S)), fill=INK, anchor='ls')

# "For sale" pill
pill='DIRECT SALE FROM THE FOUNDER'; pf=F(700,15*S)
pw=d.textlength(pill,font=pf)+ (34+12)*S
py=168*S
d.rounded_rectangle([64*S,py,64*S+pw,py+34*S],radius=17*S,fill=(255,255,255),outline=(255,217,201),width=S)
d.ellipse([78*S,py+13*S,86*S,py+21*S],fill=ORANGE)
d.text((96*S,py+17*S),pill,font=pf,fill=ORANGE,anchor='lm')

# headline
hf=F(800,96*S)
d.text((60*S,318*S),'imisofts is',font=hf,fill=(26,26,26),anchor='ls')
d.text((60*S,418*S),'for sale',font=hf,fill=ORANGE,anchor='ls')
# sub
d.text((64*S,470*S),'Website, outbound engine and monthly retainers.',font=F(500,24*S),fill=INK,anchor='ls')

# stats row
x=64*S; y=520*S
for num,lab in (('27','Domain Rating'),('8K-10K','monthly visitors'),(ARTICLES,'articles')):
    nf=F(800,34*S); lf=F(500,18*S)
    nw=d.textlength(num,font=nf); lw=d.textlength(lab,font=lf)
    w=nw+lw+ (18+18+10)*S
    d.rounded_rectangle([x,y,x+w,y+58*S],radius=14*S,fill=(255,255,255),outline=(238,240,243),width=S)
    d.text((x+18*S,y+29*S),num,font=nf,fill=ORANGE,anchor='lm')
    d.text((x+18*S+nw+10*S,y+31*S),lab,font=lf,fill=MUTED,anchor='lm')
    x+=w+12*S

out=img.convert('RGB').resize((1200,630),Image.LANCZOS)
p=os.path.join(ROOT,'og-image-acquire.jpg'); out.save(p,'JPEG',quality=88,optimize=True,progressive=True)
print('wrote',p,os.path.getsize(p))
