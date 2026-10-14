#!/usr/bin/env python3
"""Revise only the skin and seed layers of the loose-fruits strawberry."""
import argparse
import copy
import json
import math
from pathlib import Path
from loose_fruit_studies import ROOT, Sketch, curve, ellipse, mask_for, rng_for
from render import render_to


def build():
    original=json.loads((ROOT/'examples/studies/loose-fruits-v2/strawberry/scene.json').read_text())
    s=Sketch('草莓 · 短笔与籽窝',84620)
    poly=curve([(437,294),(399,276),(353,291),(315,320),(291,365),(295,416),
        (316,475),(346,539),(384,605),(429,677),(461,705),(491,677),
        (532,617),(576,550),(614,479),(634,416),(632,364),(610,322),
        (571,288),(526,277),(480,297)],steps=8,closed=True)
    calyx=[[(461,301),(424,270),(371,270),(336,252),(378,294),(420,313)],
        [(459,301),(444,258),(410,226),(452,238),(475,269)],
        [(466,298),(487,251),(531,222),(515,269),(489,301)],
        [(473,300),(528,275),(572,285),(607,306),(551,306),(514,323)],
        [(461,299),(436,320),(416,354),(449,341),(474,316)],
        [(477,302),(502,320),(523,350),(491,336),(471,319)]]
    leaves=[curve(p,steps=8,closed=True) for p in calyx]
    from PIL import ImageFilter
    seed_area=mask_for(poly,holes=leaves).filter(ImageFilter.MinFilter(31)).load()
    r=rng_for('berry-seed-pockets-v3');seeds=[]
    for _ in range(5000):
        if len(seeds)==48:break
        x=r.uniform(308,618);y=r.uniform(310,684)
        if not seed_area[int(x),int(y)]:continue
        if any((x-a)**2+(y-b)**2<r.uniform(32,39)**2 for a,b,*_ in seeds):continue
        seeds.append((x,y,r.uniform(3.2,4.6),r.uniform(5.2,7.4),(x-460)/420))
    holes=leaves+[ellipse(x,y,rx+4,ry+4,rotate=math.degrees(a),n=20) for x,y,rx,ry,a in seeds]
    s.texture('berry-skin',poly,1150,lambda x,y:rng_for(f'{int(x)//21}-{int(y)//19}').uniform(-math.pi,math.pi),
        lambda x,y,r:r.choice([(214,64,62),(229,83,70),(216,78,83)] if x>464 or y>510
                              else [(235,108,82),(237,126,92),(222,89,73)]),
        holes=holes,density=lambda x,y:.27 if ((x-366)/32)**2+((y-369)/63)**2<1 else .9,
        length=(3,10),width=(3.5,7))
    o=s.object('berry-seeds')
    for i,(x,y,rx,ry,a) in enumerate(seeds):
        def at(u,v):return (x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a))
        # Broken crescent indicates a shallow pocket, not a ring around a dot.
        s.line(o,f'pocket-{i}',[at(rx+2,-ry*.3),at(rx+3,ry*.5),at(1,ry+3),at(-rx*.6,ry+1)],
               (178,66,65),r.uniform(1.5,2.3),r.uniform(.54,.79))
        s.line(o,f'seed-{i}',[at(-.6,-ry*.6),at(.2,0),at(-.4,ry*.5)],
               r.choice([(205,159,68),(221,179,82),(217,172,75)]),r.uniform(3,4.4),.94)
    result=copy.deepcopy(original)
    replacements={o['id']:o for o in s.scene.data['objects']}
    result['objects']=[replacements.get(o['id'],o) for o in result['objects']]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/strawberry-texture-v3')
    args=p.parse_args()
    result=render_to(build(),args.out)
    print('Rendered; warnings:',result['warnings'])
