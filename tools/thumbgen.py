#!/usr/bin/env python3
"""Bug Bounty & Beyond thumbnail kit.
Reusable generator for the weekly thumbnail refresh. House style:
dark grid bg, green "HACK IT, THEN FIX IT" kicker for episodes,
orange "FREE FULL COURSE" for course cuts, blue "AI SECURITY" for deep dives.
Big red+white promise, muted sub, red warning triangle (episodes/deep dives)
or green shield (courses). On-screen text ALWAYS English; Hindi videos get a
blue Hindi language tab only, always TOP-RIGHT
(never bottom-right: the duration stamp covers that corner). Set "hindi":true on any kind.

Usage:
  python3 thumbgen.py spec.json OUTDIR
spec.json = list of items, each:
  {"out":"ep14.jpg","kind":"fix","big_red":"3","big_white":"WORDS",
   "line2":"TOOK AN ACCOUNT","sub":"..."}            # episode
  {"out":"m5.jpg","kind":"course","n":8,"topic":"...","hindi":true}   # course cut
  {"out":"dd.jpg","kind":"deepdive","big_red":"OWASP","big_white":"TOP 10",
   "line2":"FOR AI APPS","sub":"...","badge":"2026"}  # deep dive
Font dir defaults to the system Inter; override with env THUMB_FONTDIR.
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BG=(12,16,24); ORANGE=(255,122,26); RED=(255,66,66); GREEN=(46,210,120)
WHITE=(245,248,252); MUTE=(150,162,178); INK=(10,13,20); BLUE=(64,156,255)
FD=os.environ.get("THUMB_FONTDIR","/usr/share/fonts/opentype/inter/")
W,H=1280,720; MAXX=880
FILES={"black":"InterDisplay-Black.otf","xbold":"InterDisplay-ExtraBold.otf",
       "bold":"InterDisplay-Bold.otf","sbold":"Inter-SemiBold.otf"}
def f(w,s):
    p=FD+FILES[w]
    if not os.path.exists(p):  # fallback to plain Inter names, then default
        alt=FD+FILES[w].replace("InterDisplay-","Inter-")
        p=alt if os.path.exists(alt) else None
    return ImageFont.truetype(p,s) if p else ImageFont.load_default()
def tw(d,s,fnt):
    b=d.textbbox((0,0),s,font=fnt);return b[2]-b[0],b[3]-b[1]
def fitfont(d,s,w,size):
    fn=f(w,size)
    while tw(d,s,fn)[0]>MAXX-60 and size>60:
        size-=4; fn=f(w,size)
    return fn
def base():
    img=Image.new("RGB",(W,H),BG)
    glow=Image.new("RGBA",(W,H),(0,0,0,0));gd=ImageDraw.Draw(glow)
    gd.ellipse([W-620,-300,W+220,420],fill=(255,66,66,40))
    gd.ellipse([-300,H-360,380,H+260],fill=(255,122,26,26))
    glow=glow.filter(ImageFilter.GaussianBlur(100))
    img=Image.alpha_composite(img.convert("RGBA"),glow).convert("RGB")
    gr=Image.new("RGBA",(W,H),(0,0,0,0));g=ImageDraw.Draw(gr)
    for x in range(0,W,48):g.line([(x,0),(x,H)],fill=(255,255,255,6))
    for y in range(0,H,48):g.line([(0,y),(W,y)],fill=(255,255,255,6))
    return Image.alpha_composite(img.convert("RGBA"),gr).convert("RGB")
def warning(img,cx,cy,sz):
    d=ImageDraw.Draw(img,"RGBA");h=sz;w=int(sz*1.15)
    pts=[(cx,cy-h//2),(cx+w//2,cy+h//2),(cx-w//2,cy+h//2)]
    d.polygon(pts,fill=(255,66,66,45));d.line(pts+[pts[0]],fill=RED,width=12,joint="curve")
    d.line([(cx,cy-h*0.18),(cx,cy+h*0.12)],fill=WHITE,width=16)
    d.ellipse([cx-9,cy+h*0.20,cx+9,cy+h*0.20+18],fill=WHITE)
def shield(img,cx,cy,sz):
    d=ImageDraw.Draw(img,"RGBA");col=GREEN;w=sz;h=int(sz*1.18);top=cy-h//2
    pts=[(cx,top),(cx+w//2,top+h*0.16),(cx+w//2,top+h*0.55),(cx,top+h),(cx-w//2,top+h*0.55),(cx-w//2,top+h*0.16)]
    d.polygon(pts,fill=(col[0],col[1],col[2],40));d.line(pts+[pts[0]],fill=col,width=12,joint="curve")
    d.line([(cx-sz*0.18,cy+sz*0.02),(cx-sz*0.03,cy+sz*0.18),(cx+sz*0.22,cy-sz*0.18)],fill=col,width=16,joint="curve")
def badge(d,text,col=ORANGE,shift=0):
    pf=f("xbold",30);bw,_=tw(d,text,pf);x1=W-64-bw-44-shift
    d.rounded_rectangle([x1,60,x1+bw+44,60+56],radius=14,fill=col);d.text((x1+22,60+11),text,font=pf,fill=INK)
HINDI_FONT=os.environ.get("THUMB_HINDI_FONT","/usr/share/fonts/truetype/freefont/FreeSansBold.ttf")
def hindi_tab(img,corner="tr"):
    """Language tab for Hindi videos. Default and house rule: TOP-RIGHT.
    Never bottom-right: YouTube's duration stamp covers that corner in search, Home and suggested."""
    if corner=="br":raise ValueError("bottom-right is covered by the duration stamp; use tr (default) or tl")
    d=ImageDraw.Draw(img);w,h=184,84
    x=0 if "l" in corner else W-w;y=0 if "t" in corner else H-h
    ex=-40 if "l" in corner else 40;ey=-40 if "t" in corner else 40
    box=[min(x,x+ex),min(y,y+ey),max(x+w,x+w+ex),max(y+h,y+h+ey)]
    d.rounded_rectangle(box,radius=22,fill=BLUE,outline=WHITE,width=3)
    try:
        fn=ImageFont.truetype(HINDI_FONT,52,layout_engine=ImageFont.Layout.RAQM);txt="\u0939\u093f\u0902\u0926\u0940"
    except Exception:
        fn=f("xbold",40);txt="HINDI"
    d.text((x+w/2,y+h/2+2),txt,font=fn,fill=WHITE,anchor="mm")
def kicker_pill(d,text,col):
    pf=f("xbold",34);pw,_=tw(d,text,pf)
    d.rounded_rectangle([64,58,64+pw+52,58+64],radius=15,fill=col);d.text((64+26,58+13),text,font=pf,fill=INK)
def _hero(d,big_red,big_white):
    x,y=60,150
    if big_white:
        bigr=fitfont(d,big_red+" "+big_white,"black",150);rw,_=tw(d,big_red,bigr)
        d.text((x,y),big_red,font=bigr,fill=RED)
        d.text((x+rw+24,y+28),big_white,font=f("black",int(bigr.size*0.69)),fill=WHITE)
    else:
        d.text((x,y),big_red,font=fitfont(d,big_red,"black",150),fill=RED)
def fix(out,big_red,big_white,line2,sub,kicker="HACK IT, THEN FIX IT",hindi=False):
    img=base();d=ImageDraw.Draw(img);kicker_pill(d,kicker,GREEN);_hero(d,big_red,big_white)
    d.text((60,322),line2,font=fitfont(d,line2,"black",96),fill=WHITE)
    d.text((64,452),sub,font=f("sbold",40),fill=MUTE);warning(img,1085,300,300)
    if hindi:hindi_tab(img)
    img.save(out,quality=92)
def course(out,n,topic,hindi=False):
    img=base();d=ImageDraw.Draw(img);kicker_pill(d,"FREE FULL COURSE",ORANGE)
    big=f("black",132);d.text((60,168),str(n),font=big,fill=RED);nw,_=tw(d,str(n),big)
    d.text((60+nw+22,168+18),"ATTACKS",font=f("black",104),fill=WHITE)
    d.text((60,318),str(n),font=big,fill=GREEN);d.text((60+nw+22,318+18),"FIXES",font=f("black",104),fill=WHITE)
    d.text((64,470),topic,font=f("sbold",38),fill=MUTE);shield(img,1095,300,250)
    if hindi:hindi_tab(img)
    img.save(out,quality=92)
def deepdive(out,big_red,big_white,line2,sub,badge_txt="2026",hindi=False):
    img=base();d=ImageDraw.Draw(img);kicker_pill(d,"AI SECURITY",BLUE)
    if badge_txt:badge(d,badge_txt,col=ORANGE,shift=170 if hindi else 0)
    _hero(d,big_red,big_white);d.text((60,322),line2,font=fitfont(d,line2,"black",96),fill=WHITE)
    d.text((64,452),sub,font=f("sbold",40),fill=MUTE);warning(img,1085,300,300)
    if hindi:hindi_tab(img)
    img.save(out,quality=92)
def render(item,outdir):
    o=os.path.join(outdir,item["out"]);k=item["kind"]
    if k=="fix":fix(o,item["big_red"],item.get("big_white",""),item["line2"],item["sub"],hindi=item.get("hindi",False))
    elif k=="course":course(o,item["n"],item["topic"],item.get("hindi",False))
    elif k=="deepdive":deepdive(o,item["big_red"],item.get("big_white",""),item["line2"],item["sub"],item.get("badge","2026"),item.get("hindi",False))
    else:raise ValueError("unknown kind "+k)
    return o
if __name__=="__main__":
    spec=json.load(open(sys.argv[1]));outdir=sys.argv[2];os.makedirs(outdir,exist_ok=True)
    for it in spec:print("saved",render(it,outdir))
    print("DONE",len(spec))
