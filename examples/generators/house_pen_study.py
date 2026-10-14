#!/usr/bin/env python3
"""Redraw the house's authored geometry with the original pencil-case pens.

This is a scene-authoring pass, not an image filter. Hidden paths are clipped
against the authored foreground surfaces before transparent marks are emitted.
The prior painting and its scene are left unchanged. Only Pillow and NumPy are
used for geometric visibility; every output drawing mark uses pencil-case.
"""
from __future__ import annotations
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, ellipse, curve
from render import render_to
from house_cutaway_study import build as build_house


def dense(points, step=.8):
    result=[]
    for a,b in zip(points,points[1:]):
        count=max(1,math.ceil(math.dist(a,b)/step))
        result.extend([(a[0]+(b[0]-a[0])*i/count,
                        a[1]+(b[1]-a[1])*i/count) for i in range(count)])
    return np.array(result+[points[-1]],dtype=np.float64)


def simplify(points, tolerance=.18):
    """RDP removes sampling points on straight lines without erasing gestures."""
    if len(points)<3:
        return points
    a,b=points[0],points[-1]; vector=b-a
    length=float(vector@vector)
    if length<1e-10:
        dist=np.linalg.norm(points-a,axis=1)
    else:
        t=np.clip((points-a)@vector/length,0,1)
        dist=np.linalg.norm(points-(a+t[:,None]*vector),axis=1)
    i=int(np.argmax(dist))
    if dist[i]<=tolerance:
        return np.array([a,b])
    return np.concatenate((simplify(points[:i+1],tolerance)[:-1],
                           simplify(points[i:],tolerance)))


def visible_paths(points, covered):
    p=dense(points)
    x=np.rint(p[:,0]).astype(int);y=np.rint(p[:,1]).astype(int)
    valid=(x>=0)&(x<covered.shape[1])&(y>=0)&(y<covered.shape[0])
    visible=valid.copy()
    visible[valid]=~covered[y[valid],x[valid]]
    starts=np.flatnonzero(visible & ~np.r_[False,visible[:-1]])
    ends=np.flatnonzero(visible & ~np.r_[visible[1:],False])+1
    result=[]
    for start,end in zip(starts,ends):
        segment=p[start:end]
        if len(segment)>1 and np.linalg.norm(np.diff(segment,axis=0),axis=1).sum()>1.15:
            result.append(np.round(simplify(segment),3).tolist())
    return result


def occlude(covered, polygon):
    x0=max(0,math.floor(min(p[0] for p in polygon)))
    y0=max(0,math.floor(min(p[1] for p in polygon)))
    x1=min(covered.shape[1],math.ceil(max(p[0] for p in polygon))+1)
    y1=min(covered.shape[0],math.ceil(max(p[1] for p in polygon))+1)
    if x1<=x0 or y1<=y0:return
    mask=Image.new('1',(x1-x0,y1-y0))
    ImageDraw.Draw(mask).polygon([(x-x0,y-y0) for x,y in polygon],fill=1)
    covered[y0:y1,x0:x1] |= np.asarray(mask,dtype=bool)


def pen_settings(obj,mark):
    id=mark['id'];width=mark.get('width',1)
    color=np.array(mark.get('color',[52,48,43]))
    detail=any(key in id for key in ('book-','books-','shelf','rib-','tile-','fold',
               'weave','spine','button','hair-','face-detail','shirt-fold','radiator-rib'))
    figure=obj['id'] in {'bedroom-woman','standing-person','sofa-person','floor-child','entry-woman'}
    structural=width>=4 and not figure
    if structural:
        result=dict(width=2.55 if width>=6 else 2.05,pressure=.78,opacity=.96,
                    wobble=.48,gaps=.009,gap_length=[1,2])
    elif detail:
        result=dict(width=1.05,pressure=.50,opacity=.78,wobble=.24,
                    gaps=.025,gap_length=[1,3])
    else:
        result=dict(width=(2.0 if figure else 1.75) if width>=.9 else 1.05,pressure=.68,
                    opacity=.98 if figure else .94,wobble=.52 if width>=.9 else .25,
                    gaps=.018,gap_length=[1,3])
    # Previously pale highlights become secondary ink, never another heavy edge.
    if float(color.mean())>145:
        result['opacity']*=.7
        result['width']*=.85
    result['opacity']*=min(1,mark.get('opacity',1)/.8)
    if figure and ('face' in id or 'hand' in id):
        result.update(wobble=.15,gaps=0,step=.7)
    result.update(jitter=.12,nib=True,overdraw=0,smooth=False)
    if obj['id'] in {'front-door','upper-railing'} and width>=4:
        result['overdraw']=1
    return result


def color_notes(scene):
    """Selected strokes inside visible surfaces: most of the paper stays bare."""
    o=scene.object('selected-watercolour','少量淡彩，保留纸面')
    def wash(id,points,color,opacity=.22):
        o.fill(id,points,color,opacity=min(.47,opacity*1.35),grain=.52,edge=.25,bleed=2.4,
               layers=2,offset=[1.5,1])
    wash('cool-bedroom',[(47,350),(91,326),(91,341),(75,353),(72,384),
         (59,401),(47,409)],(91,139,145),.18)
    wash('bed-brick-red',[(192,432),(225,416),(311,445),(269,466),(242,480),(210,465)],
         (176,98,83),.30)
    wash('bed-blanket',[(216,491),(244,501),(271,488),(274,500),(245,514),(215,504)],
         (125,147,104),.20)
    wash('skirt',[(170,498),(185,499),(202,493),(201,523),(185,527),(170,522)],
         (103,145,139),.29)
    wash('cardigan',[(202,456),(207,465),(214,480),(208,487),(202,484),(205,478)],
         (163,99,113),.23)
    wash('lamp-warmth',ellipse(695,529,19,7,n=32),(207,176,94),.19)
    wash('rug',[(512,652),(548,634),(581,637),(601,647),(591,660),
         (536,660),(548,681),(584,697),(602,698),(587,708),(548,695),(521,674)],
         (172,110,101),.14)
    wash('sofa-left',[(865,582),(876,574),(884,580),(884,620),(878,628),(866,623)],
         (119,139,97),.29)
    wash('sofa-front',[(927,639),(986,604),(1004,598),(1003,611),(930,656)],
         (123,141,104),.26)
    wash('sofa-cushion',[(919,598),(937,589),(952,595),(934,610),(918,620),(905,612)],
         (136,151,111),.22)
    wash('seated-shirt',[(920,535),(931,535),(946,544),(958,546),(966,551),
         (960,566),(946,564),(933,554)],(84,136,150),.29)
    wash('standing-shirt',[(819,559),(830,563),(847,557),(850,583),(849,607),
         (828,609),(820,596)],(125,161,170),.20)
    wash('child-shirt',[(1074,695),(1085,700),(1101,692),(1103,718),
         (1087,722),(1074,718)],(119,150,170),.28)
    wash('door-red',[(1001,969),(1010,967),(1008,1031),(1038,1014),(1039,1023),
         (1001,1047)],(181,111,86),.35)
    wash('door-light',[(1010,902),(1034,888),(1034,930),(1010,944)],(219,177,100),.24)
    wash('entry-trousers',[(882,944),(891,946),(888,975),(885,1008),(879,1010)],
         (64,143,149),.33)
    wash('shoulder-bag',[(873,933),(890,936),(885,951),(871,945)],(195,125,98),.36)
    wash('tv-light',[(1091,540),(1156,557),(1153,590),(1091,571)],(162,185,128),.18)
    wash('washing-glass',ellipse(172,691,9,18,rotate=14,n=28),(123,159,174),.20)


def shadow_hatching(scene):
    o=scene.object('contact-hatching','床、沙发、楼梯的局部排线')
    patches=[
        ('under-bed',[(115,514),(156,528),(156,534),(115,520)],66,4.5,.48),
        ('sofa-base',[(932,650),(998,611),(999,618),(932,658)],67,5,.39),
        ('door-thickness',[(990,887),(995,884),(995,1051),(990,1054)],40,6,.40),
        ('table-under',[(973,664),(1038,689),(1038,694),(973,669)],65,5,.34),
        ('slab-left',[(381,672),(490,709),(490,715),(381,678)],65,5,.36),
        ('slab-right',[(1092,799),(1182,747),(1182,752),(1092,804)],70,5,.36),
        ('entry-ground',[(879,1029),(894,1033),(909,1026),(918,1025),
                          (905,1036),(888,1040)],18,4,.30),
    ]
    for i in (1,3,5,7):
        x=655+i*15; y=764+i*23;u=735+i*15;v=718+i*23
        patches.append((f'stair-{i}',[(x+18,y+13),(u+12,v+13),(u+12,v+20),(x+18,y+20)],58,5.5,.36))
    for id,poly,angle,spacing,opacity in patches:
        o.hatch(id,poly,(65,65,56),angle=angle,spacing=spacing,opacity=min(.65,opacity*1.5),width=1.1)


def build(ink_only=False):
    source=build_house()
    out=Scene('住宅剖面 · 原版钢笔淡彩',width=1354,height=1332,
              seed=source['seed'],paper=(248,246,237),grain=.26)
    out.data['engine']='pencil-case'
    if not ink_only:color_notes(out)
    shadow_hatching(out)
    covered=np.zeros((1332,1354),dtype=bool)
    object_paths=[]
    for obj in reversed(source['objects']):
        marks=[]
        for m in reversed(obj['marks']):
            if m['kind']=='ink':
                # The pigment highlights are not new structural lines.
                if any(key in m['id'] for key in ('-light','-glint','glass-light','rug-ring')):
                    continue
                for i,points in enumerate(visible_paths(m['points'],covered)):
                    marks.append(dict(id=f"{m['id']}-part-{i}",kind='ink',points=points,
                                      color=[42,47,41],**pen_settings(obj,m)))
            elif m['kind']=='wash' and m['id'].endswith('-pigment-0') and m.get('opacity',1)>.8:
                occlude(covered,m['polygon'])
        if marks:
            object_paths.append(dict(id=obj['id'],name=obj.get('name',obj['id']),
                                     marks=list(reversed(marks))))
    out.data['objects'].extend(reversed(object_paths))
    return out.data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-pen-v2')
    p.add_argument('--ink-only',action='store_true')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    scene=build(args.ink_only)
    print(f"Rendering {sum(len(o['marks']) for o in scene['objects'])} upstream marks",flush=True)
    result=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {result['warnings']}")
