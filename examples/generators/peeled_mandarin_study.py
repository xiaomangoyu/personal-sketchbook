#!/usr/bin/env python3
"""A peeled mandarin in coloured contours and short form-following strokes.

Original pencil-case pen paths, authored geometry, no sampled reference pixels.
White pith and membranes are unpainted paper, not white paint over a solid fill.
"""
import argparse
import copy
import math
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, curve, bezier
from render import render_to

GREEN=(94,116,29)
MOSS=(119,138,40)
PITH=(201,185,146)
PALE=(220,204,161)
ORANGE=(229,142,19)
AMBER=(211,112,17)
GOLD=(235,177,47)


def stroke(o,id,points,color,width=3,opacity=.96):
    o.line(id,points,color,width=width,opacity=opacity,pressure=.85,
           wobble=.52,gaps=.025,gap_length=[1,2],step=.7,
           nib=False,jitter=.20,overdraw=0)


def curved(o,id,points,color,width=3,opacity=.96):
    stroke(o,id,curve(points,steps=8),color,width,opacity)


def peel(scene,id,outline,green_runs,pith_runs,skin_paths):
    o=scene.object(id,'翻开的橘皮与白瓤')
    rng=random.Random(sum(map(ord,id)))
    curved(o,'pith-outline',outline,PALE,2.5,.83)
    for i,p in enumerate(green_runs):curved(o,f'green-edge-{i}',p,GREEN,4.1)
    for i,p in enumerate(pith_runs):
        if i%5==3:continue
        p=[[x+rng.uniform(-6,6),y+rng.uniform(-3,3)] for x,y in p]
        if i%4==2:p=p[1:]
        curved(o,f'pith-fibre-{i}',p,PITH,rng.uniform(2.1,3.5),.72)
    for i,p in enumerate(skin_paths):curved(o,f'skin-{i}',p,GREEN if i%4 else MOSS,3.6+(i%3)*.65)
    return o


def fruit_point(theta,t):
    """A dome seen obliquely; its visible crown is above the silhouette centre."""
    outer=1+.018*math.cos(8*theta+.4)+.009*math.sin(3*theta)
    x=522+249*outer*math.cos(theta)
    y=476+222*outer*math.sin(theta)
    apex=(548,406)
    curl=26*math.sin(theta+.5)*math.sin(math.pi*t)
    # The front expands sideways before turning down: curved meridians on a
    # rounded whole fruit rather than straight radii on a cut orange disc.
    side=math.sin(t*math.pi/2)
    depth=t**1.15 if math.sin(theta)>0 else t
    return [apex[0]+side*(x-apex[0])-math.sin(theta)*curl,
            apex[1]+depth*(y-apex[1])+math.cos(theta)*curl]


def hide_peel_behind_fruit(objects):
    """Trim hidden ink geometrically; unpainted fruit membranes stay white."""
    def outside(p):
        x,y=(p[0]-522)/249,(p[1]-476)/222
        theta=math.atan2(y,x)
        boundary=1+.018*math.cos(8*theta+.4)+.009*math.sin(3*theta)
        return math.hypot(x,y)>boundary+.008
    for obj in objects:
        if not obj['id'].endswith('peel'):continue
        marks=[]
        for mark in obj['marks']:
            dense=[]
            for a,b in zip(mark['points'],mark['points'][1:]):
                n=max(1,math.ceil(math.dist(a,b)))
                dense.extend([[a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n] for i in range(n)])
            dense.append(mark['points'][-1])
            run=[];pieces=[]
            for point in dense:
                if outside(point):run.append(point)
                else:
                    if len(run)>3:pieces.append(run)
                    run=[]
            if len(run)>3:pieces.append(run)
            for k,points in enumerate(pieces):
                m=copy.deepcopy(mark);m['id']+=f'-visible-{k}';m['points']=points
                marks.append(m)
        obj['marks']=marks


def build():
    s=Scene('剥开的橘子 · 彩色线描与顺形短排线',width=1000,height=1030,
            paper=(255,255,255),grain=0,seed=84617)
    s.data['engine']='pencil-case'
    rng=random.Random(84617)
    o=s.object('ground','轻淡的接触影')
    for i,(pts,alpha) in enumerate([
        ([(214,581),(258,596),(332,663),(426,691),(463,717),(399,726),(313,682),(234,625)],.14),
        ([(363,846),(424,866),(519,849),(610,787),(749,672),(776,673),(703,754),(551,870),(442,900),(378,879)],.13)]):
        o.fill(f'shadow-{i}',curve(pts,steps=6,closed=True),(165,177,125),opacity=alpha,
               bleed=9,edge=.05,grain=.75,layers=1,offset=[0,0])

    # The folded green back has an uneven tear; its white face is mostly paper.
    pith=[];skin=[]
    for i in range(13):
        y=169+i*9
        pith.append([(347-(i%3)*3,y+28),(383,y+14),(437+i%4*5,y),(474,y-5)])
    for i in range(7):
        skin.append([(358+i*3,161+i*1.8),(399,141+i*3),(460-i*2,143+i*2),(486-i*2,132+i*3)])
    peel(s,'back-peel',
         [(312,360),(306,295),(313,224),(337,179),(369,150),(415,135),(461,140),
          (486,130),(509,151),(499,170),(516,184),(506,202),(524,218),(500,245),(463,295)],
         [[(315,354),(307,294),(313,223),(337,180),(368,151),(415,137),(458,142),(486,132)]],pith,skin)

    skin=[];pith=[]
    for i in range(14):
        t=i/13
        skin.append([(191-20*math.sin(t*math.pi),314+202*t),
                     (178-14*math.sin(t*math.pi),344+194*t),
                     (198-7*math.sin(t*math.pi),384+184*t)])
    for i in range(9):
        pith.append([(222+i*4,442+i*9),(232+i*5,487+i*7),(254+i*7,533+i*7)])
    peel(s,'left-peel',
         [(332,637),(288,624),(240,605),(198,575),(172,524),(158,468),(160,399),
          (171,350),(191,314),(208,307),(203,331),(224,343),(215,369),
          (241,379),(250,411),(281,421),(298,470),(322,531)],
         [[(191,313),(171,351),(159,400),(158,469),(173,524),(198,575),(240,606),(288,626),(332,636)],
          [(184,341),(177,425),(185,492),(217,553),(267,590)]],pith,skin)

    skin=[];pith=[]
    for i in range(18):
        t=i/17
        skin.append([(815-75*t,426+190*t),(829-71*t,446+195*t),
                     (824-97*t,493+176*t),(801-122*t,543+141*t)])
    for i in range(9):
        pith.append([(806-i*3,412+i*8),(793-i*3,444+i*9),(772-i*3,470+i*9)])
    peel(s,'right-peel',
         [(688,685),(747,671),(793,636),(829,584),(851,525),(855,465),(841,419),
          (821,394),(820,423),(804,416),(803,444),(777,452),(775,482),(750,510),(724,546)],
         [[(838,422),(853,466),(850,525),(829,584),(793,635),(747,671),(688,685)]],pith,skin)

    # Foreground folded peel has a white upper face and a narrow green underside.
    skin=[];pith=[]
    for i in range(19):
        t=i/18
        skin.append([(317+141*t,775+68*t),(339+148*t,811+41*t),(379+117*t,853+6*t)])
    for i in range(10):
        y=727+i*10
        pith.append([(367+(i%3)*5,y),(409,y+17),(458+i%4*4,y+21)])
    peel(s,'front-peel',
         [(400,645),(373,676),(362,705),(327,725),(331,744),(314,766),(327,806),
          (358,836),(403,861),(451,877),(486,872),(519,849),(530,816),(526,789),
          (542,765),(544,738),(573,714),(558,690)],
         [[(315,767),(328,806),(359,836),(404,861),(451,876),(486,871),(519,849)],
          [(332,786),(379,826),(427,849),(487,853)]],pith,skin)

    hide_peel_behind_fruit(s.data['objects'])
    # Fruit sectors are individually drawn. Unequal angles avoid a clock face.
    boundaries=[-3.12,-2.53,-1.86,-1.19,-.49,.23,.96,1.65,2.37,3.16318530718]
    for seg,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
        o=s.object(f'fruit-{seg}',f'第 {seg+1} 瓣果肉')
        # A broken outer lip; no uniform dark ring around the entire fruit.
        curved(o,'outer-lip',[fruit_point(a+(b-a)*u,1) for u in [.045,.18,.36,.54,.76,.94]],
               ORANGE if seg%3 else AMBER,2.5,.87)
        # Deliberately leave wide white channels at sector boundaries.
        curved(o,'membrane',[fruit_point(a+.028,t) for t in [.20,.33,.5,.68,.85,.97]],
               GOLD,1.8,.61)
        # Crown fibres: thin, uneven bundles instead of a filled centre.
        for j in range(8):
            theta=a+(b-a)*(.12+j*.105+rng.uniform(-.015,.015))
            t0=rng.uniform(.13,.23);t1=rng.uniform(.33,.50)
            pts=[fruit_point(theta+.045*math.sin(t*4+seg),t) for t in [t0,(t0+t1)*.5,t1]]
            curved(o,f'crown-{j}',pts,GOLD if j%3 else ORANGE,rng.uniform(2.3,4))
        # Small groups of juice sacs follow the dome, not one global hatch angle.
        for band in range(6):
            for lane in range(11):
                if rng.random()<.10:continue
                u=.05+lane*.089+rng.uniform(-.016,.016)
                t=.32+band*.107+rng.uniform(-.048,.035)
                if .38<u<.45 and band in (2,3):continue
                theta=a+(b-a)*u
                length=rng.uniform(.055,.14)
                for k in range(rng.choice([2,2,3])):
                    angle=theta+k*.015
                    pts=[fruit_point(angle+.032*math.sin(q*5+seg),q)
                         for q in [t,t+length*.45,min(.969,t+length)]]
                    if band>=3 and lane%4==1:
                        pts=[fruit_point(angle+d,min(.965,t+.018*math.sin(d*22)))
                             for d in [0,.033,.068]]
                    color=ORANGE if (lane+band)%4 else AMBER
                    if t<.58:color=GOLD if seg%3 else ORANGE
                    curved(o,f'sac-{band}-{lane}-{k}',pts,color,rng.uniform(3.8,6),.99)
        # Two gentle lateral marks suggest a membrane without boxing each cell.
        for j,t in enumerate((.64,.86)):
            curved(o,f'cross-fibre-{j}',[fruit_point(a+(b-a)*u,t+.016*math.sin(u*6))
                                       for u in [.13,.27,.4]],GOLD,1.6,.67)
    o=s.object('crown','果心的短赭色纤维')
    for i in range(16):
        angle=rng.uniform(0,math.tau);r=rng.uniform(2,13)
        x=548+math.cos(angle)*r;y=406+math.sin(angle)*r*.75
        curved(o,f'fibre-{i}',[(x-2,y-5),(x+2,y+3),(x+1,y+8)],(186,91,40),rng.uniform(1.8,3.7),.92)
    return s.data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/peeled-mandarin-v1')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args();scene=build()
    print(f"Rendering {sum(len(o['marks']) for o in scene['objects'])} marks",flush=True)
    manifest=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {manifest['warnings']}")
