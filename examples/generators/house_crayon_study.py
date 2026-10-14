#!/usr/bin/env python3
"""Pastel crayon + ink house study, using unchanged upstream pencil-case brushes.

Reuses authored geometry, not pixels from either reference or previous drawings.
Visible colour surfaces are decomposed into polygons before sparse crayon marks
are emitted. This keeps paper gaps without revealing hidden background colours.
"""
from __future__ import annotations
import argparse
import copy
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from render import render_to
from house_cutaway_study import build as build_house
from house_pen_study import build as build_pen, occlude, simplify

PAL={
    'sky':(98,167,204),'mint':(106,180,145),'peach':(231,153,123),
    'yellow':(235,203,96),'lilac':(166,142,200),'wood':(201,154,94),
    'coral':(207,109,100),'slate':(105,130,166),'cream':(231,212,163),
}
FIGURES={'bedroom-woman','standing-person','sofa-person','floor-child','entry-woman'}


def shape_mask(polygon):
    m=Image.new('1',(1354,1332))
    ImageDraw.Draw(m).polygon([tuple(p) for p in polygon],fill=1)
    return np.asarray(m,dtype=bool).copy()


def polygon_area(p):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2


def visible_polygons(mask):
    """Decompose a binary geometric mask, including holes, into simple polygons.

    Track horizontal spans until their topology changes. A chair in front of a
    wall splits the wall into a few connected strips rather than a solid fill or
    an external raster mask. The resulting scene uses only ordinary polygons.
    """
    rows=np.flatnonzero(mask.any(axis=1))
    if not len(rows):return []
    polygons=[];active=[];previous=[]
    def finish(tracks):
        for left,right in tracks:
            # Left boundary descends; the right boundary returns to the top.
            p=np.array(left+right[::-1],dtype=float)
            p=np.vstack((p,p[0]))
            p=np.round(simplify(p,.48),2).tolist()
            if len(p)>3 and polygon_area(p)>18:
                polygons.append(p)
    for y in range(int(rows[0]),int(rows[-1])+2):
        row=mask[y] if y<mask.shape[0] else np.zeros(mask.shape[1],dtype=bool)
        changes=np.diff(np.r_[False,row,False].astype(np.int8))
        spans=list(zip(np.flatnonzero(changes==1),np.flatnonzero(changes==-1)))
        connected=len(spans)==len(previous) and all(
            a<d and c<b for (a,b),(c,d) in zip(spans,previous))
        if not connected:
            finish(active)
            active=[([],[]) for _ in spans]
        for (left,right),(a,b) in zip(active,spans):
            left.extend([(int(a),y),(int(a),y+1)])
            right.extend([(int(b),y),(int(b),y+1)])
        previous=spans
    finish(active)
    return polygons


def material(obj,id,original):
    """Return a pigment family, relative colour strength, and stroke direction."""
    if obj in {'house-section','section-edges','lower-room-shade'}:
        return None
    if any(k in id for k in ('shadow','light','reflection','glass-light','glow','shade','under-bed')):
        return None
    if obj=='bedroom-walls':
        return ('mint',.90,88) if 'wall' in id else None
    if obj=='hall-wall':
        if 'plane' in id:return ('yellow',.88,82)
        if 'door' in id:return ('wood',.76,86)
        if 'transom' in id:return ('sky',.60,88)
        return None
    if obj=='bathroom':
        return ('lilac',.82,85) if id in {'bath-left','bath-back'} else None
    if obj=='living-wall':return ('peach',.88,90)
    if obj=='upper-floor':
        return ('wood',.73,20) if 'floor' in id else ('slate',.32,20)
    if obj=='lower-shell':
        if 'floor' in id:return ('wood',.54,20)
        if 'laundry' in id:return ('sky',.73,80)
        if 'bike' in id:return ('lilac',.55,85)
        if 'dining' in id:return ('peach',.70,87)
        if 'entry' in id:return ('yellow',.65,75)
        if 'kitchen' in id:return ('mint',.65,87)
        return None
    if obj=='bed':
        if 'sheet' in id:return ('coral',.90,28)
        if 'blanket' in id:return ('mint',.95,90)
        if 'mattress' in id:return None
        return ('wood',.83,17)
    if obj=='hall-laundry':
        if id=='rug':return ('coral',.78,18)
        if 'shirt' in id:return ('peach',.95,70)
        if 'clothes' in id:
            return (['sky','yellow','mint','lilac'][int(id[-1])%4],.90,70)
        if 'basket' in id:return ('slate',.50,70)
        if 'iron' in id:return ('sky',.90,90)
        return None
    if obj=='living-sofa':return ('mint',1.05,25)
    if obj=='staircase':
        if 'tread' in id:return ('wood',.82,-28)
        if 'riser' in id:return ('lilac',.47,-29)
        return None
    if obj=='upper-railing':return ('wood',.75,85)
    if obj=='front-door':
        if 'window' in id:return ('yellow',1.05,78)
        return ('coral',1.02,85)
    if obj=='entry-details':
        if 'coat-wall' in id:return ('peach',.75,84)
        if 'coat-0' in id:return ('yellow',1.05,85)
        if 'coat-1' in id:return ('sky',1.0,85)
        return ('wood',.62,18)
    if obj in FIGURES:
        if any(x in id for x in ('face','neck','hand','arm','ankle')) and 'shirt' not in id:
            return ('peach',.66,70)
        if 'hair' in id:return ('slate',.76,85)
        if 'shoe' in id:return ('slate',.84,12)
        if 'bag' in id:return ('coral',1.10,55)
        if obj=='bedroom-woman':return ('mint' if 'skirt' in id else 'coral',.97,80)
        if obj=='standing-person':return ('sky' if 'shirt' in id else 'slate',.92,85)
        if obj=='sofa-person':return ('yellow' if 'trouser' in id else 'sky',1.00,30)
        if obj=='entry-woman':return ('mint' if 'trouser' in id else 'lilac',1.0,80)
        return ('sky',1.0,80)
    if obj in {'bedroom-fittings','living-fittings'}:
        if any(x in id for x in ('book-','books-')):
            index=sum(ord(c) for c in id)%5
            return (['sky','coral','yellow','mint','lilac'][index],1.10,90)
        if any(x in id for x in ('lamp','pendant','paint-sun')):return ('yellow',.95,65)
        if 'radiator' in id or 'clock-face' in id:return None
        if any(x in id for x in ('glass','tv','bowl','landscape','leaf','portrait')):
            return ('mint',.85,82)
        if 'mirror' in id:return ('yellow',.30,35)
        if 'sunset' in id or 'hills' in id:return ('peach',.83,12)
        return ('wood',.78,20)
    if obj=='bedroom-window':return ('yellow',.75,87)
    if obj=='coffee-table':
        if 'pizza' in id:return ('yellow',1.20,20)
        if 'laptop' in id:return ('slate',.85,36)
        if 'table' in id:return ('wood',.80,20)
        if 'remote' in id:return ('lilac',.96,35)
        return None
    if obj=='lower-laundry':
        if 'glass' in id or 'inner' in id:return ('sky',.96,90)
        if any(x in id for x in ('face','side','top','door-rim','open-door')):return None
        if any(x in id for x in ('clothes','towel','detergent','tin','carton')):
            return (['sky','coral','yellow','mint'][sum(ord(c) for c in id)%4],.83,70)
        return ('wood',.55,15)
    if obj=='lower-bicycle-store':return None
    if obj=='lower-dining':
        if any(x in id for x in ('plate','cup','pot')):return ('mint',.72,30)
        return ('wood',.61,20)
    if obj=='lower-kitchen':
        if 'fridge' in id:return ('lilac',.56,87)
        if 'cabinet' in id:return ('mint',.77,80)
        return None
    return None


def build():
    source=build_house()
    pen=build_pen(ink_only=True)
    out=copy.deepcopy(pen)
    out['title']='住宅剖面 · 粉彩蜡笔与钢笔'
    out['canvas']['paper']=[250,248,239]
    out['canvas']['grain']=.38
    out['objects']=[]
    covered=np.zeros((1332,1354),dtype=bool)
    groups=[]
    for obj in reversed(source['objects']):
        colors=[]
        for mark in reversed(obj['marks']):
            if mark['kind']!='wash' or not mark['id'].endswith('-pigment-0'):
                continue
            id=mark['id'].removesuffix('-pigment-0')
            # The previous study's light/gradient glazes aren't physical objects.
            if mark.get('opacity',1)<=.8:continue
            if any(id.startswith(prefix) for prefix in ('bedroom-cool-','hall-left-light-',
                       'hall-right-light-')):continue
            mask=shape_mask(mark['polygon'])
            visible=mask & ~covered
            settings=material(obj['id'],id,mark['color'])
            if settings and visible.sum()>24:
                family,strength,direction=settings
                for k,poly in enumerate(visible_polygons(visible)):
                    if polygon_area(poly)<24:continue
                    for pass_number in range(3 if polygon_area(poly)>6000 else 2):
                        # Multiple dry passes, without a solid colour undercoat.
                        # The second pass shifts colour and direction slightly.
                        color=PAL[family]
                        if pass_number==1:
                            tint=PAL['yellow'] if family in {'wood','mint','peach'} else PAL['sky']
                            color=tuple(round(v*.85+w*.15) for v,w in zip(color,tint))
                        colors.append(dict(id=f'{id}-part-{k}-wax-{pass_number}',kind='wax',
                            polygon=poly,color=list(color),opacity=min(1,.91*strength),
                            density=4,grain=.70,direction=direction+(-8,9,0)[pass_number]))
            covered |= mask
        if colors:
            groups.append(dict(id='pastel-'+obj['id'],name=obj.get('name',obj['id'])+' · 蜡笔',
                               marks=list(reversed(colors))))
    out['objects'].extend(reversed(groups))
    for obj in pen['objects']:
        for m in obj['marks']:
            if m['kind']=='ink':
                m['color']=[66,77,89] if obj['id'] not in FIGURES else [69,68,82]
                m['opacity']*=.83 if obj['id'] not in FIGURES else .92
            elif m['kind']=='hatch':
                m['color']=[105,103,132]
                m['opacity']*=.72
        out['objects'].append(obj)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-crayon-v3')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    scene=build()
    count=sum(len(o['marks']) for o in scene['objects'])
    print(f'Rendering {count} upstream drawing marks',flush=True)
    result=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {result['warnings']}")
