"""Geometry helpers for editable scenes; output stays compatible with scene v1."""
from __future__ import annotations
import copy
import json
import math
import random
from pathlib import Path


def transform(points, *, translate=(0, 0), scale=1, rotate=0, origin=(0, 0)):
    sx, sy = (scale, scale) if isinstance(scale, (int, float)) else scale
    c, s = math.cos(math.radians(rotate)), math.sin(math.radians(rotate))
    result = []
    for x, y in points:
        x, y = (x-origin[0])*sx, (y-origin[1])*sy
        result.append([round(x*c-y*s+origin[0]+translate[0], 3), round(x*s+y*c+origin[1]+translate[1], 3)])
    return result


def ellipse(cx, cy, rx, ry, *, rotate=0, start=0, end=360, n=64, rough=0, seed=0):
    if n < 2 or rx <= 0 or ry <= 0:
        raise ValueError('ellipse requires n >= 2 and positive radii')
    rng = random.Random(seed)
    phase = [rng.uniform(0, 2*math.pi) for _ in range(3)]
    pts = []
    for i in range(n+1):
        a = math.radians(start+(end-start)*i/n)
        r = 1+rough*(.55*math.sin(3*a+phase[0])+.30*math.sin(5*a+phase[1])+.15*math.sin(7*a+phase[2]))
        pts.append([cx+rx*math.cos(a)*r, cy+ry*math.sin(a)*r])
    return transform(pts, rotate=rotate, origin=(cx,cy))


def bezier(points, steps=32):
    if len(points) != 4 or steps < 1:
        raise ValueError('bezier requires four control points and positive steps')
    return [[round((1-t)**3*points[0][j]+3*(1-t)**2*t*points[1][j]+3*(1-t)*t*t*points[2][j]+t**3*points[3][j],3) for j in (0,1)] for t in [i/steps for i in range(steps+1)]]


def curve(points, steps=10, closed=False):
    if len(points)<2 or steps<1:
        raise ValueError('curve requires two or more control points and positive steps')
    p = [list(v) for v in points]
    if closed and p[-1] == p[0]:
        p.pop()
    src = [p[-1] if closed else p[0]]+p+[p[0] if closed else p[-1], p[1] if closed else p[-1]]
    out=[]
    for i in range(1,len(p)+(1 if closed else 0)):
        a,b,c,d=src[i-1:i+3]
        for k in range(steps):
            t=k/steps
            out.append([round(.5*(2*b[j]+(-a[j]+c[j])*t+(2*a[j]-5*b[j]+4*c[j]-d[j])*t*t+(-a[j]+3*b[j]-3*c[j]+d[j])*t*t*t),3) for j in (0,1)])
    out.append(p[0] if closed else p[-1])
    return out


def clone_object(obj, new_id, *, translate=(0,0), scale=1, rotate=0, origin=(0,0)):
    """Copy geometry and brush dimensions without sharing mutable data.

    Missing values use natural_media's render defaults before transformation.
    Nonuniform scales use the geometric mean for scalar brush dimensions;
    directional marks follow the transformed direction vector.
    """
    size_defaults={
        'ink': {'width':1.8,'wobble':.7},
        'pencil': {'width':1.8,'wobble':.7},
        'wash': {'bleed':2},
        'hatch': {'width':1,'spacing':8},
        'wax': {},
    }
    direction_defaults={'wax':('direction',0),'hatch':('angle',60)}
    new=copy.deepcopy(obj)
    old_offset=new.pop('translate',[0,0])
    new['id']=new_id
    sx,sy=(scale,scale) if isinstance(scale,(int,float)) else scale
    factor=math.sqrt(abs(sx*sy))
    for mark in new['marks']:
        key='points' if mark['kind'] in ('ink','pencil') else 'polygon'
        pts=transform(mark[key],translate=old_offset)
        mark[key]=transform(pts,translate=translate,scale=scale,rotate=rotate,origin=origin)
        if 'clip_polygons' in mark:
            mark['clip_polygons']=[transform(transform(p,translate=old_offset),translate=translate,
                                             scale=scale,rotate=rotate,origin=origin)
                                   for p in mark['clip_polygons']]
        if 'gradient' in mark:
            for endpoint in ('start','end'):
                pts=transform([mark['gradient'][endpoint]],translate=old_offset)
                mark['gradient'][endpoint]=transform(pts,translate=translate,scale=scale,rotate=rotate,origin=origin)[0]
        for key,default in size_defaults[mark['kind']].items():
            mark[key]=mark.get(key,default)*factor
        if 'spread' in mark:
            mark['spread']*=factor
        if mark['kind'] in direction_defaults:
            key,default=direction_defaults[mark['kind']]
            angle=math.radians(mark.get(key,default))
            mark[key]=(math.degrees(math.atan2(sy*math.sin(angle),sx*math.cos(angle)))+rotate+180)%360-180
    return new


class Marks:
    def __init__(self, value):
        self.value=value
    def line(self, id, points, color=(57,51,47), *, kind='ink', width=2, opacity=.85, **kw):
        if kind not in ('ink','pencil'):
            raise ValueError('line kind must be ink or pencil')
        self.value['marks'].append(dict(id=id,kind=kind,points=[list(p) for p in points],color=list(color),width=width,opacity=opacity,**kw))
        return self
    def fill(self, id, polygon, color, *, kind='wash', opacity=.65, **kw):
        if kind not in ('wax','wash'):
            raise ValueError('fill kind must be wax or wash')
        self.value['marks'].append(dict(id=id,kind=kind,polygon=[list(p) for p in polygon],color=list(color),opacity=opacity,**kw))
        return self
    def hatch(self, id, polygon, color=(70,60,50), *, opacity=.45, width=1, spacing=7, angle=60):
        self.value['marks'].append(dict(id=id,kind='hatch',polygon=[list(p) for p in polygon],color=list(color),opacity=opacity,width=width,spacing=spacing,angle=angle))
        return self


class Scene:
    def __init__(self,title,width=1200,height=1000,seed=42,paper=(249,246,235),grain=.42):
        self.data=dict(version=1,title=title,seed=seed,canvas=dict(width=width,height=height,paper=list(paper),grain=grain),objects=[])
    def object(self,id,name=None):
        obj=dict(id=id,name=name or id,marks=[])
        self.data['objects'].append(obj)
        return Marks(obj)
    def save(self,path):
        from render import validate
        validate(self.data)
        p=Path(path)
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(self.data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        return p
