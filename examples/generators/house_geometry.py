"""Small authoring helpers for the house study; emits ordinary scene-v1 marks."""
from scene_tools import Scene, curve, ellipse


def rgb(value):
    if isinstance(value, str):
        return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))
    return tuple(value)


class Drawing:
    def __init__(self):
        self.scene = Scene('住宅剖面 · 用户参考临摹试稿', width=1354, height=1332,
                           seed=73109, paper=(34, 43, 37), grain=.19)
        self.current = None

    def object(self, id, name=None):
        self.current = self.scene.object(id, name)

    def line(self, id, points, color='#34302b', width=1, opacity=.8, smooth=False):
        self.current.line(id, points, rgb(color), width=width, opacity=opacity,
                          wobble=.18 if width < 2 else .25, pressure=.65,
                          smooth=smooth, gaps=.006)

    def poly(self, id, points, fill, outline='#292c28', width=1.1, opacity=1):
        # Two pigment passes make walls/furniture opaque enough for occlusion.
        # This study needs broad dark/light planes, rather than pale paper gaps.
        for i in range(2):
            self.current.fill(f'{id}-pigment-{i}', points, rgb(fill), opacity=opacity,
                              grain=.09, edge=.10, bleed=0)
        if outline is not None:
            self.line(id+'-edge', list(points)+[points[0]], outline, width, .92)

    def path(self, id, points, fill, outline='#34302b', width=1):
        self.poly(id, curve(points, steps=5, closed=True), fill, outline, width)

    def oval(self, id, cx, cy, rx, ry, fill, outline='#34302b', width=1, rotate=0):
        self.poly(id, ellipse(cx,cy,rx,ry,rotate=rotate,n=40), fill, outline, width)

    def hatch(self, id, points, color='#34302b', opacity=.25, spacing=5, angle=63):
        self.current.hatch(id, points, rgb(color), opacity=opacity, spacing=spacing,
                           width=.65, angle=angle)

    def plane(self, id, p, start, end, steps=18):
        """Authored light falloff across a quadrilateral, still just polygons."""
        a,b=rgb(start),rgb(end)
        for i in range(steps):
            t=i/steps; u=(i+1)/steps
            color=tuple(round(v+(w-v)*(t+u)/2) for v,w in zip(a,b))
            q=[lerp(p[0],p[1],t),lerp(p[0],p[1],u),
               lerp(p[3],p[2],u),lerp(p[3],p[2],t)]
            self.poly(f'{id}-{i}',q,color,None)

    def light(self,id,cx,cy,rx,ry,color,clip,opacity=.03):
        """Concentric pigment glazes, geometrically clipped to a room surface."""
        for i in range(15):
            size=1-i*.055
            p=clip_convex(ellipse(cx,cy,rx*size,ry*size,n=50),clip)
            if len(p)>=3:
                self.poly(f'{id}-{i}',p,color,None,opacity=opacity)


def lerp(a, b, t):
    return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)


def clip_convex(subject, boundary):
    """Sutherland-Hodgman clipping keeps light and ink inside the house."""
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(boundary,boundary[1:]+boundary[:1]))
    sign=1 if area>0 else -1
    def cross(a,b,p):
        return sign*((b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]))
    out=list(subject)
    for a,b in zip(boundary,boundary[1:]+boundary[:1]):
        incoming=out;out=[]
        if not incoming: break
        prev=incoming[-1]; dp=cross(a,b,prev)
        for curr in incoming:
            dc=cross(a,b,curr)
            if (dc>=0)!=(dp>=0):
                out.append(lerp(prev,curr,dp/(dp-dc)))
            if dc>=0: out.append(curr)
            prev,dp=curr,dc
    return out


def wall_frame(g, id, p, frame='#ac7c52', inside='#647f73', width=5):
    g.poly(id, p, inside, frame, width)
    g.line(id+'-inner',p+[p[0]],'#363a31',.8)


def cabinet(g, id, x, y, w, h, color='#8d7960', slope=.35):
    """Cabinet in the long right-down wall plane."""
    p=[(x,y),(x+w,y+w*slope),(x+w,y+h+w*slope),(x,y+h)]
    g.poly(id,p,color)
    for i,t in enumerate((.5,)):
        g.line(id+f'-door-{i}',[(x+w*t,y+w*t*slope),(x+w*t,y+h+w*t*slope)],width=.8)
    for i,dx in enumerate((w*.44,w*.56)):
        g.oval(id+f'-handle-{i}',x+dx,y+dx*slope+h*.52,1.3,2,'#cfb589',width=.5)
