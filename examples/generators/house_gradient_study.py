#!/usr/bin/env python3
"""Simplified house study: selective watercolour fades and varied ink on white.

Geometry is authored by the house generators; no reference pixels are sampled.
The original pencil-case brushes supply the deposit. Our adapter adds fades.
"""
import argparse
import math
from pathlib import Path
import re

from house_watercolour_study import build as build_watercolour, ROOT
from render import render_to


def keep_detail(obj, name):
    # Select complete semantic details, never random individual contour fragments.
    if name.startswith(('tile-', 'book-spine-', 'book-line-', 'tv-rain-',
                        'post-foot-', 'curtain-ring-', 'hair-detail-', 'basket-slot-')):
        return False
    patterns = [(r'.*rib-(\d+)', 4), (r'wheel-\d+-spoke-(\d+)', 3),
                (r'post-dark-\d+-(\d+)', 2), (r'stair-spindle-(\d+)', 2),
                (r'curtain-fold-(\d+)', 3), (r'books?-\d+-(\d+)', 3)]
    for pattern, interval in patterns:
        match=re.match(pattern,name)
        if match and int(match[1]) % interval:
            return False
    if any(word in name for word in ('-label','-button','-stitch','-seam','-inner','-handle-')):
        return False
    if obj=='lower-dining' and any(word in name for word in ('spoon','fork','crumb','plate-inner')):
        return False
    return True


def build():
    scene=build_watercolour()
    scene['title']='住宅剖面 · 简练线条与水彩渐变'
    # Focal colours are intentional; large walls and floors remain unpainted.
    wash_axes={
        'bed-watercolour':([280,451],[192,413],[225,166,125]),
        'sofa-watercolour':([876,630],[988,564],[158,188,167]),
        'watercolour-atmosphere':None,
    }
    removed_washes={'bed-red-pool','bed-red-lift','bedroom-corner','living-warm-air',
                    'bath-shadow','washing-reflection','rug-damp-edge','child-shoulder',
                    'standing-side','sofa-shadow','sofa-back-cushion','bedside-contact'}
    structures={'section-edges','upper-floor','lower-shell','bedroom-walls','living-wall'}
    foreground={'bed','living-sofa','upper-railing','front-door','staircase'}
    for obj in scene['objects']:
        oid=obj['id']
        kept=[]
        for mark in obj['marks']:
            name=re.sub(r'-part-\d+$','',mark['id'])
            if not keep_detail(oid,name) or mark['id'] in removed_washes:
                continue
            if mark['kind']=='wash':
                points=mark['polygon']
                xs,ys=zip(*points)
                axis=wash_axes.get(oid)
                if axis:
                    start,end,tint=axis
                else:
                    start=[min(xs),max(ys)]
                    end=[max(xs),min(ys)]
                    tint=[min(245,c+22) for c in mark['color']]
                # Small clothing folds keep some pigment at the light end.
                floor=.18 if oid=='people-watercolour' else 0
                mark['gradient']=dict(start=list(start),end=list(end),opacity=[1,floor],color_to=tint)
                mark['opacity']=min(1,mark['opacity']*1.22)
                mark['bleed']=min(8,mark['bleed']*1.25)
                mark['edge']*=.65
            elif mark['kind']=='ink':
                points=mark['points']
                length=sum(math.dist(a,b) for a,b in zip(points,points[1:]))
                person=oid.endswith('person') or oid in {'entry-woman','floor-child'}
                important=person or oid in foreground
                mark.update(color=[54,63,69] if important else [80,91,99],
                            wobble=.28 if person else .38,overdraw=0,
                            gaps=.008 if important else .018, nib=important,
                            jitter=.06)
                # Pressure/nib retain the upstream varying width; stroke roles
                # set a readable hierarchy, while the new envelope controls fade.
                if person:
                    mark.update(width=1.65,pressure=.62,opacity=.88)
                elif oid in structures:
                    mark.update(width=2.15,pressure=.52,opacity=.78)
                elif oid in foreground:
                    mark.update(width=1.8,pressure=.6,opacity=.87)
                else:
                    mark.update(width=1.65,pressure=.45,opacity=.83)
                if length>24 and not person and math.dist(points[0],points[-1])>12:
                    # Emphasise lower contacts, lose the lifted end in white.
                    start,end=points[0],points[-1]
                    if start[1]<end[1]:
                        start,end=end,start
                    floor=.65 if important or oid in structures else .48
                    mark['gradient']=dict(start=list(start),end=list(end),opacity=[1,floor])
                if name.startswith(('post-dark-','stair-spindle-')):
                    mark['width']=1.25
                if oid=='bathroom':
                    mark['opacity']*=.88
            elif mark['kind']=='hatch':
                if mark['id'] not in {'under-bed','sofa-base','table-under','entry-ground'}:
                    continue
                mark['opacity']*=.75
            kept.append(mark)
        obj['marks']=kept
    scene['objects']=[o for o in scene['objects'] if o['marks']]
    return scene


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-gradient-v5')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    scene=build()
    print(f"Rendering {sum(len(o['marks']) for o in scene['objects'])} marks",flush=True)
    manifest=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {manifest['warnings']}")
