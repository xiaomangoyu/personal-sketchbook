#!/usr/bin/env python3
"""White-paper house: chromatic shadows, mixed pigments and irregular wet edges.

Reuses authored geometry and unchanged upstream brushes. Adapter spread/grain
approximate wet pigment; no reference pixels are sampled for the drawing.
"""
import argparse
import copy
import re
from pathlib import Path

import numpy as np

from house_gradient_study import build as build_lines, ROOT
from house_cutaway_study import build as build_house
from house_crayon_study import shape_mask, visible_polygons, polygon_area, FIGURES
from scene_tools import Scene, curve
from render import render_to


def pigment(obj, name):
    """Select focal surfaces; white is an authored part of the palette."""
    if obj=='bed':
        if name=='bed-sheet-top': return ([211,55,44],[240,165,35],.95)
        if name=='bed-sheet-fall': return ([180,54,83],[233,115,55],.82)
        if 'blanket' in name:return ([26,136,112],[156,184,38],.84)
        if name in {'bed-front','bed-end'} or name.startswith('bed-post-'):
            return ([173,93,21],[234,168,30],.84)
    if obj=='living-sofa':
        if name=='sofa-back':return ([27,109,91],[122,172,46],.88)
        if name=='sofa-seat':return ([57,141,61],[166,192,36],.93)
        if name=='sofa-base':return ([22,95,111],[56,150,77],.94)
        if 'cushion' in name:return ([167,160,28],[234,193,36],.72)
    if obj=='coffee-table':
        if name=='table-top':return ([193,112,12],[245,185,29],.88)
        if 'table-leg' in name or 'table-apron' in name:return ([116,74,29],[183,123,20],.77)
        if name=='pizza':return ([224,115,22],[244,196,47],.88)
    if obj=='hall-laundry':
        if name=='shirt':return ([216,68,40],[244,166,26],.94)
        if name=='iron':return ([36,95,178],[46,163,189],.78)
    if obj=='front-door':
        if name=='red-door':return ([186,68,45],[236,142,38],.77)
        if name=='door-window':return ([220,148,20],[250,213,80],.74)
    if obj in FIGURES:
        if 'shoe' in name:return ([44,63,113],[87,104,132],.76)
        if 'bag' in name:return ([197,76,35],[237,157,32],.94)
        if obj=='standing-person' and 'shirt' in name:return ([28,92,183],[89,163,205],.83)
        if obj=='standing-person' and 'trouser' in name:return ([49,80,148],[105,129,174],.77)
        if obj=='sofa-person' and ('sweater' in name or 'sleeve' in name):return ([22,85,158],[58,141,161],.92)
        if obj=='sofa-person' and 'trouser' in name:return ([201,150,42],[239,210,88],.75)
        if obj=='floor-child' and 'shirt' in name:return ([50,89,174],[117,150,200],.84)
        if obj=='bedroom-woman' and 'skirt' in name:return ([29,119,106],[87,165,133],.84)
        if obj=='bedroom-woman' and ('cardigan' in name or 'sleeve' in name):return ([176,65,100],[223,134,114],.85)
        if obj=='entry-woman' and ('torso' in name or 'sleeve' in name):return ([89,64,139],[137,125,170],.85)
        if obj=='entry-woman' and 'trouser' in name:return ([23,120,140],[76,176,165],.91)
    if obj in {'bedroom-fittings','living-fittings'}:
        if name=='lamp-shade':return ([221,150,15],[245,202,57],.82)
        if re.match(r'books?-\d+-[036]$',name):
            return ([49,117,165],[185,167,36],.74)
    if obj=='lower-laundry' and ('towel' in name or 'clothes' in name):
        return ([55,129,155],[128,176,119],.68)
    return None


def atmosphere(scene):
    o=scene.object('wet-atmosphere','少量明亮洗色，边缘留白')
    def wash(id,pts,color,end,opacity=.7,spread=5,bleed=.7,fade=.22):
        xs,ys=zip(*pts)
        o.fill(id,curve(pts,steps=5,closed=True),color,opacity=opacity,layers=3,
               grain=.8,granulation=.62,spread=spread,bleed=bleed,edge=.48,offset=[0,0],
               gradient=dict(start=[min(xs),max(ys)],end=[max(xs),min(ys)],opacity=[1,fade],color_to=end))
    wash('bedroom-teal',[(43,351),(65,336),(94,334),(116,326),(118,351),(104,371),
         (103,391),(86,408),(66,420),(44,409)], [43,156,155],[139,196,92],.68,6)
    wash('living-gold',[(849,467),(873,451),(897,443),(911,452),(904,477),
         (910,494),(890,502),(879,521),(852,531)], [231,169,22],[249,215,63],.51,6,1.2)
    wash('rug-rose',[(510,646),(536,627),(564,621),(585,624),(565,644),(543,654),
         (549,679),(575,692),(601,710),(573,712),(550,700),(527,683)],
         [194,83,126],[236,158,111],.73,4,.55,.5)
    wash('washing-blue',[(151,674),(165,670),(180,680),(186,701),(173,715),(157,711)],
         [31,122,191],[74,174,184],.68,2,.5,.44)
    wash('lamp-yellow',[(676,524),(691,519),(709,523),(719,532),(708,538),(682,538)],
         [227,166,17],[249,222,101],.75,2,.4,.6)
    # Blue shadows belong to a surface/contact; not decorative splashes in margins.
    o=scene.object('chromatic-shadows','家具接触处的钴蓝与蓝紫阴影')
    wash('bed-cast',[(140,533),(180,544),(226,560),(245,568),(281,550),(298,551),
         (265,576),(239,589),(212,580),(178,560),(153,554)],
         [45,99,197],[126,150,209],.78,4,.7,.48)
    wash('sofa-cast',[(924,657),(942,653),(1004,619),(1018,625),(1026,640),
         (1009,646),(965,676),(944,683),(928,674)],
         [45,92,186],[135,139,190],.78,4,.6,.48)
    wash('table-cast',[(976,681),(1022,690),(1059,675),(1070,687),(1052,701),
         (1019,718),(994,708),(971,697)], [47,108,202],[116,163,211],.60,3,.6,.45)
    wash('entry-cast',[(861,1018),(886,1018),(910,1021),(928,1008),(949,1003),
         (957,1010),(936,1027),(910,1045),(885,1041),(861,1034)],
         [33,111,200],[126,160,206],.83,4,.6,.55)
    o=scene.object('stair-pigments','楼梯上断续的赭黄和蓝紫')
    for i in (1,3,6,9):
        x=655+i*15;y=764+i*23;u=735+i*15;v=718+i*23
        wash(f'warm-step-{i}',[(x+8,y+1),(u-4,v+3),(u+8,v+10),(x+20,y+10)],
             [199,131,25],[239,186,68],.72,2,.5,.65)
    for i in (2,5,8,10):
        x=655+i*15;y=764+i*23;u=735+i*15;v=718+i*23
        wash(f'cool-step-{i}',[(x+16,y+13),(u+11,v+13),(u+11,v+20),(x+17,y+20)],
             [68,102,184],[149,138,188],.62,1.5,.35,.64)


def build():
    source=build_house()
    lines=build_lines()
    scene=Scene('住宅剖面 · 鲜色与水彩晕染',width=1354,height=1332,
                seed=lines['seed'],paper=(255,255,255),grain=0)
    scene.data['engine']='pencil-case'
    atmosphere(scene)
    covered=np.zeros((1332,1354),dtype=bool)
    groups=[]
    for obj in reversed(source['objects']):
        marks=[]
        for m in reversed(obj['marks']):
            if m['kind']!='wash' or not m['id'].endswith('-pigment-0') or m.get('opacity',1)<=.8:
                continue
            name=m['id'].removesuffix('-pigment-0')
            if name.startswith(('bedroom-cool-','hall-left-light-','hall-right-light-')):continue
            mask=shape_mask(m['polygon'])
            settings=pigment(obj['id'],name)
            if settings:
                color,tint,strength=settings
                xs,ys=zip(*m['polygon'])
                regions=[p for p in visible_polygons(mask & ~covered) if polygon_area(p)>8]
                if regions:
                    # Broad surfaces get both the first wet colour and a local
                    # second pigment charge. Small details keep a single wash.
                    mark=dict(id=f'{name}-wash',kind='wash',polygon=m['polygon'],clip_polygons=regions,color=color,
                              opacity=strength,layers=3,grain=.88,granulation=.65,
                              edge=.5,bleed=.5,spread=2.5,offset=[0,0],
                              gradient=dict(start=[min(xs),max(ys)],end=[max(xs),min(ys)],
                                            opacity=[1,.72],color_to=tint))
                    marks.append(mark)
                    if sum(polygon_area(p) for p in regions)>1000:
                        second=copy.deepcopy(mark)
                        second.update(id=f'{name}-charge',color=tint,opacity=.38,spread=4,bleed=.65)
                        second['gradient']=dict(start=[max(xs),min(ys)],end=[min(xs),max(ys)],opacity=[1,0])
                        marks.append(second)
                        if obj['id'] in {'bed','living-sofa','coffee-table'}:
                            pool=copy.deepcopy(mark)
                            pool.update(id=f'{name}-pool',opacity=.84,granulation=.48,grain=.7,spread=1.5)
                            pool['gradient']=dict(start=[min(xs),max(ys)],end=[max(xs),min(ys)],opacity=[1,.08])
                            marks.append(pool)
            covered |= mask
        if marks:groups.append(dict(id='pigment-'+obj['id'],name=obj.get('name',obj['id']),marks=list(reversed(marks))))
    scene.data['objects'].extend(reversed(groups))
    for obj in lines['objects']:
        marks=[]
        for m in obj['marks']:
            if m['kind']!='ink':continue
            # Coloured contours within coloured furniture avoid a uniform grey net.
            if obj['id'] in {'bed','coffee-table','front-door'}:
                m['color']=[117,78,40];m['opacity']*=.87
            elif obj['id']=='living-sofa':
                m['color']=[41,90,70];m['opacity']*=.83
            elif obj['id'] in FIGURES:
                m['color']=[57,63,88]
            else:
                m['color']=[82,97,115]
            marks.append(m)
        if marks:
            obj['marks']=marks
            scene.data['objects'].append(obj)
    return scene.data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-bloom-v6')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args(); scene=build()
    print(f"Rendering {sum(len(o['marks']) for o in scene['objects'])} marks",flush=True)
    manifest=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {manifest['warnings']}")
