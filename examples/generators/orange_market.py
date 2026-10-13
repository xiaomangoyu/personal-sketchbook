"""A small orange stall: directional wax, overlapping fruit, a runaway orange."""
from pathlib import Path
import argparse
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scene_tools import Scene, ellipse, curve, bezier, transform
from render import render_to

GREEN = (39, 87, 67)
INK = (65, 64, 46)
ORANGE = (241, 121, 35)
PAPER = (249, 239, 211)


def wax(obj, id, shape, color, opacity=.88, direction=20, density=1.15):
    if opacity >= .75:
        # A rubbed-in first coat makes cloth and wood opaque. A lighter undercoat
        # also gives the surface a different tooth from a single noisy mask.
        under=tuple(round(c*.57+p*.43) for c,p in zip(color,PAPER))
        obj.fill(id+'-rubbed',shape,under,kind='wax',opacity=.98,
                 direction=direction,density=3.8,grain=.035)
    obj.fill(id, shape, color, kind='wax', opacity=opacity, direction=direction,
             density=density, grain=.61)


def line(obj, id, points, color=INK, width=2.5, opacity=.78, **kw):
    obj.line(id, points, color, kind='pencil', width=width, opacity=opacity,
             pressure=.72, wobble=.7, gaps=.013, **kw)


def fruit(obj, id, x, y, r, seed=1, leaf=False):
    shape = ellipse(x, y, r, r*.92, rough=.045, seed=seed, n=42)
    obj.fill(id+'-under', shape, (240, 127, 36), opacity=.7, edge=.06, grain=.3, bleed=.3)
    wax(obj, id+'-skin', shape, (246, 146, 37), .92, 25+seed%30, 1.27)
    shadow = curve([(x-r*.74,y+r*.08),(x-r*.38,y+r*.53),(x+r*.43,y+r*.57),
                    (x+r*.86,y-r*.16),(x+r*.76,y+r*.62),(x+r*.18,y+r*.9),
                    (x-r*.55,y+r*.7)], closed=True)
    wax(obj,id+'-shade',shadow,(198,80,32),.61,48,1.03)
    highlight=curve([(x-r*.64,y-r*.33),(x-r*.26,y-r*.66),(x+r*.17,y-r*.62),
                     (x+r*.34,y-r*.43),(x-r*.23,y-r*.22)],closed=True)
    wax(obj,id+'-light',highlight,(255,201,84),.58,20,1.13)
    line(obj,id+'-lower',ellipse(x,y,r,r*.92,start=25,end=155,n=20,rough=.025,seed=seed),
         (155,78,40),1.5,.58)
    line(obj,id+'-stem',[(x-3,y-r*.6),(x,y-r*.75),(x+4,y-r*.64)],GREEN,2,.8)
    if leaf:
        pts=curve([(x+1,y-r*.72),(x+21,y-r*1.14),(x+49,y-r*.97),(x+25,y-r*.64)],closed=True)
        wax(obj,id+'-leaf',pts,GREEN,.9,-24)
        line(obj,id+'-vein',[(x+1,y-r*.72),(x+33,y-r*.93)],(100,121,58),1.5,.7)


def build_scene():
    s=Scene('周末市场的橘子摊',1400,1080,seed=307,paper=PAPER,grain=.6)
    wall=s.object('market-wall','阳光下的旧墙')
    wall.fill('warm-wall',[(115,260),(1195,156),(1250,873),(120,901)],(214,171,120),opacity=.15,edge=.03,bleed=3)
    wax(wall,'left-warm',[(152,420),(367,392),(369,707),(130,723)],(215,161,109),.18,89,.62)
    wall.fill('alcove',[(738,292),(1104,255),(1149,724),(751,734)],(62,94,71),opacity=.64,edge=.06,bleed=2)
    for n,(a,b) in enumerate([((771,316),(1099,283)),((771,473),(1121,443)),((791,627),(1138,616))]):
        line(wall,'shelf-'+str(n),[a,b],(54,72,52),6,.68)
    jars=s.object('jars','摊后玻璃罐和纸袋')
    for i,(x,y,h,w) in enumerate([(811,477,98,31),(884,473,71,26),(1042,458,118,33)]):
        shape=curve([(x-w,y-h+15),(x-w+5,y-h),(x+w-8,y-h),(x+w,y-h+18),(x+w+1,y),(x-w,y)],closed=True)
        jars.fill('jar-'+str(i),shape,(196,203,149),opacity=.45,edge=.05,bleed=1)
        line(jars,'jar-edge-'+str(i),[(x-w,y-h+10),(x-w,y),(x+w,y),(x+w,y-h+10)],(220,215,165),1.8,.5)
        line(jars,'lid-'+str(i),[(x-w-1,y-h),(x+w,y-h)],(63,70,48),5,.9)
    shadow=s.object('ground-shadow','摊位投影')
    wax(shadow,'cast',[(165,857),(1049,782),(1295,889),(622,1000),(107,928)],(103,113,80),.23,4,.83)
    line(shadow,'pavement',[(106,994),(454,947),(744,973),(1235,925)],(142,129,99),1.6,.45)
    support=s.object('stall-frame','木制立柱')
    for i,pts in enumerate([[(207,320),(219,323),(222,920),(210,923)],[(1145,248),(1155,247),(1183,857),(1173,861)]]):
        wax(support,'pole-'+str(i),pts,(106,110,71),.92,89)
        line(support,'pole-edge-'+str(i),[pts[0],pts[3]],(59,71,53),2.8,.76)
    # Cloth canopy has a shared perspective: each stripe fans from one receding edge.
    canopy=s.object('striped-awning','绿白条纹遮阳篷')
    top_left=(227,172); top_right=(1090,133); low_left=(98,412); low_right=(1240,350)
    wax(canopy,'cloth-base',[top_left,top_right,low_right,low_left],(240,224,180),.98,106,2)
    for i in range(12):
        def lerp(a,b,t): return (a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
        t0=i/12; t1=(i+1)/12
        poly=[lerp(top_left,top_right,t0),lerp(top_left,top_right,t1),lerp(low_left,low_right,t1),lerp(low_left,low_right,t0)]
        if i%2==0:
            wax(canopy,'green-stripe-'+str(i),poly,GREEN,.92,108,1.22)
            line(canopy,'stripe-seam-'+str(i),[poly[0],poly[3]],(31,75,53),2,.5)
        else:
            wax(canopy,'cream-stripe-'+str(i),poly,(244,225,182),.32,106,.83)
    # The scalloped front lip follows the same slope rather than a row of circles.
    for i in range(12):
        x0=98+i*1142/12; x1=98+(i+1)*1142/12
        y0=412-i*62/12; y1=412-(i+1)*62/12
        lip=curve([(x0,y0),(x1,y1),(x1-5,y1+47),((x0+x1)/2,y0+63),(x0+4,y0+47)],closed=True)
        wax(canopy,'lip-'+str(i),lip,GREEN if i%2==0 else (231,207,154),.91,85,1.15)
        line(canopy,'lip-bottom-'+str(i),curve([(x0+4,y0+47),((x0+x1)/2,y0+63),(x1-5,y1+47)]),(60,83,57),1.6,.56)
    line(canopy,'roof-top',[top_left,top_right],(79,100,63),3,.72)
    line(canopy,'cloth-front',[(97,414),(558,389),(868,371),(1240,350)],(45,76,54),3,.63)
    for i,pts in enumerate([[(161,381),(194,320),(224,264)],[(477,225),(467,282),(442,354)],
                            [(902,198),(925,259),(950,297)],[(1120,262),(1140,306),(1161,332)]]):
        line(canopy,'cloth-tension-'+str(i),curve(pts),(132,151,96),2.2,.29)
    # Counter and a high rear crate establish three distinct fruit heights.
    counter=s.object('counter','深色台面和垂下的布')
    wax(counter,'counter-top',[(180,730),(1092,672),(1216,761),(326,856)],(110,103,62),.94,0)
    wax(counter,'counter-front',[(326,856),(1216,761),(1214,845),(328,934)],(89,100,59),.95,4)
    line(counter,'front-edge',[(184,733),(326,856),(1216,761)],(48,65,44),4,.89)
    wax(counter,'cloth',[(700,782),(1037,752),(1107,817),(1104,967),(1034,982),(961,968),(879,995),(811,974),(795,840)],(234,216,172),.88,83,.99)
    line(counter,'cloth-fold',curve([(907,785),(940,831),(954,924),(961,968)]),(160,143,99),2,.45)
    back=s.object('back-crate','后排叠高果箱')
    wax(back,'box-front',[(628,641),(1029,607),(1026,728),(640,772)],(172,124,64),.91,2)
    wax(back,'box-side',[(1029,607),(1116,651),(1114,756),(1026,728)],(120,101,58),.94,80)
    wax(back,'box-inner',[(596,617),(964,587),(1029,607),(628,662)],(64,81,48),.88,0)
    backfruit=s.object('back-oranges','高处参差的橘子')
    for i,(x,y,r) in enumerate([(674,599,38),(735,575,43),(796,589,39),(865,565,44),(924,578,42),(985,586,38),(699,638,45),(778,627,44),(851,626,47),(925,620,45),(995,623,37)]):
        fruit(backfruit,'fruit-'+str(i),x,y,r,i+40,leaf=i in (1,5))
    backrim=s.object('back-crate-rim','后箱前挡板')
    wax(backrim,'top-slat',[(628,661),(1031,627),(1031,649),(632,689)],(189,145,81),.95,0)
    line(backrim,'slat-top',[(628,661),(1028,625)],(85,88,50),3.5,.85)
    line(backrim,'slat-low',[(639,723),(1027,684)],(96,84,48),2.5,.7)
    for i,(x,y) in enumerate([(668,658),(990,632)]):
        wax(backrim,'corner-'+str(i),[(x,y),(x+19,y-1),(x+19,y+98),(x,y+102)],(149,107,59),.86,90)
    front=s.object('front-crate','斜着放的木箱')
    wax(front,'interior',[(250,635),(608,658),(720,755),(348,747)],(69,81,47),.97,5)
    wax(front,'left-face',[(250,635),(348,747),(348,898),(251,784)],(153,118,68),.94,62)
    wax(front,'front-face',[(348,747),(720,755),(718,900),(348,898)],(190,141,77),.93,2)
    line(front,'left-edge',[(250,635),(251,784),(348,898)],(72,78,46),4,.85)
    frontfruit=s.object('front-oranges','主角橘子堆')
    for i,(x,y,r) in enumerate([(311,621,40),(380,624,45),(444,614,42),(507,643,46),(578,663,42),(643,693,41),(343,675,50),(422,669,45),(491,698,52),(564,718,43),(395,724,51),(470,747,45),(626,733,40)]):
        fruit(frontfruit,'fruit-'+str(i),x,y,r,i+1,leaf=i in (0,4,8))
    rim=s.object('front-crate-rim','前箱木条和钉子')
    wax(rim,'upper-slat',[(344,766),(718,773),(719,802),(347,795)],(206,158,89),.96,0)
    wax(rim,'lower-slat',[(346,852),(720,857),(718,900),(348,898)],(182,129,67),.9,0)
    line(rim,'top-lip',[(342,765),(533,770),(718,773)],(93,88,51),3,.9)
    line(rim,'middle-line',[(348,833),(718,839)],(96,84,52),2,.62)
    for i,(x,y) in enumerate([(362,774),(680,780)]):
        wax(rim,'brace-'+str(i),[(x,y),(x+22,y),(x+22,y+116),(x,y+117)],(150,106,59),.9,90)
        for j in [10,97]:
            line(rim,'nail-'+str(i)+'-'+str(j),[(x+9,y+j),(x+13,y+j+1)],(76,76,52),3,.83)
    for i,pts in enumerate([[(411,789),(455,787),(497,791)],[(549,796),(595,799),(652,798)],
                            [(403,875),(464,871),(512,875),(570,873)],[(592,884),(643,883)]]):
        line(rim,'wood-grain-'+str(i),curve(pts),(131,100,56),1.8,.51)
    # Loose fruit and twigs on the cloth prevent a shop-icon symmetry.
    loose=s.object('loose-fruit','布上刚卖完一袋后留下的橘子')
    fruit(loose,'cloth-one',855,815,48,81,True)
    fruit(loose,'cloth-two',959,832,38,82)
    wax(loose,'leaf-left',curve([(800,870),(842,848),(865,856),(837,879)],closed=True),GREEN,.83,-22)
    line(loose,'twig',curve([(791,877),(824,866),(850,861)]),(94,101,55),2,.8)
    runaway=s.object('runaway-orange','滚到摊位外的橘子')
    runaway.fill('contact-shadow',ellipse(1120,973,54,10,rotate=-8),GREEN,opacity=.15,edge=.02,bleed=3)
    fruit(runaway,'orange',1107,946,39,88,True)
    line(runaway,'trail-one',curve([(995,946),(1019,961),(1042,962)]),(130,128,84),1.8,.34)
    line(runaway,'trail-two',curve([(1011,931),(1032,945),(1050,947)]),(130,128,84),1.6,.30)
    # A few asymmetrical stalks, rooted in the gap beside the stall.
    green=s.object('corner-leaves','墙角伸出的绿枝')
    line(green,'stem',curve([(122,771),(111,650),(145,539)]),GREEN,3,.7)
    for i,(x,y,dx,dy) in enumerate([(111,686,-45,-47),(117,645,45,-33),(123,606,-37,-52),(135,568,41,-38)]):
        leaf=curve([(x,y),(x+dx*.7,y+dy*.32),(x+dx,y+dy),(x+dx*.28,y+dy*.8)],closed=True)
        wax(green,'leaf-'+str(i),leaf,(72,109,67),.8,math.degrees(math.atan2(dy,dx)))
    return s


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/gallery/orange-market')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    s=build_scene()
    result=render_to(s.data,args.out,overwrite=args.overwrite)
    print(args.out.resolve()/'artwork.png')
    print('Objects:',len(result['layers']),'Warnings:',result['warnings'])


if __name__=='__main__':
    main()
