#!/usr/bin/env python3
"""Four fruit studies in loose coloured pen strokes; white paper is reserved.

Masks below only select geometric stroke positions. Artwork is rendered from
editable ink paths through the original pencil-case brushes, not imagegen.
"""
import argparse
import hashlib
import math
from pathlib import Path
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, curve, ellipse
from render import render_to

SIZE=900
GREEN=(96,119,40)
OLIVE=(125,141,43)
ORANGE=(230,135,22)
GOLD=(232,172,44)
PITH=(203,185,147)


def rng_for(name):
    return random.Random(int.from_bytes(hashlib.sha256(name.encode()).digest()[:8],'big'))


def mask_for(polygon,holes=(),seams=()):
    im=Image.new('L',(SIZE,SIZE))
    d=ImageDraw.Draw(im)
    d.polygon([tuple(p) for p in polygon],fill=255)
    for poly in holes:d.polygon([tuple(p) for p in poly],fill=0)
    for points,width in seams:d.line([tuple(p) for p in points],fill=0,width=width)
    return im


class Sketch:
    def __init__(self,title,seed=84617):
        self.scene=Scene(title,width=SIZE,height=SIZE,paper=(255,255,255),grain=0,seed=seed)
        self.scene.data['engine']='pencil-case'

    def object(self,id,name=None):return self.scene.object(id,name)

    def line(self,o,id,points,color,width=3,opacity=.93):
        o.line(id,curve(points,steps=7),color,width=width,opacity=opacity,pressure=.8,
               wobble=.64,gaps=.035,gap_length=[1,2],step=.7,jitter=.16,nib=False)

    def shade(self,id,points,color,opacity=.11):
        o=self.object(id)
        o.fill('shadow',curve(points,steps=7,closed=True),color,opacity=opacity,
               grain=.6,bleed=7,edge=.08,layers=1,offset=[0,0])

    def texture(self,id,polygon,count,direction,palette,*,holes=(),seams=(),
                density=lambda x,y:1,length=(10,31),width=(2.6,5.4),name=None):
        """Loose unequal clusters with quiet spaces; no rings or row grid."""
        o=self.object(id,name)
        r=rng_for(id)
        m=mask_for(polygon,holes,seams).filter(ImageFilter.MinFilter(7))
        box=m.getbbox()
        if box is None:raise ValueError('empty authored surface')
        pixels=m.load();i=0;attempt=0
        while i<count and attempt<count*40:
            attempt+=1
            x=r.uniform(box[0],box[2]-1);y=r.uniform(box[1],box[3]-1)
            if not pixels[int(x),int(y)] or r.random()>density(x,y):continue
            base_angle=direction(x,y)+r.uniform(-.20,.20)
            size=r.uniform(*length)
            # A hand makes a few related marks and moves on; bundles have
            # different starts, lengths and widths instead of a regular mesh.
            for j in range(r.choice([1,1,2,3])):
                angle=base_angle+r.uniform(-.11,.11)
                dx,dy=math.cos(angle),math.sin(angle)
                off=j*r.uniform(2.4,5.2)
                xx=x-dy*off;yy=y+dx*off
                span=size*r.uniform(.65,1.3);bend=r.uniform(-3.7,3.7)
                pts=[[xx-dx*span*.47,yy-dy*span*.47],
                     [xx-dy*bend,yy+dx*bend],
                     [xx+dx*span*.53,yy+dy*span*.53]]
                samples=curve(pts,steps=5)
                if not all(0<=p[0]<SIZE and 0<=p[1]<SIZE and pixels[int(p[0]),int(p[1])] for p in samples):continue
                color=palette(x,y,r) if callable(palette) else r.choice(palette)
                self.line(o,f'cluster-{i}-{j}',pts,color,r.uniform(*width),r.uniform(.84,1))
            i+=1
        return o


def orange():
    s=Sketch('整颗剥皮橘子 · 松散彩色干笔')
    # Front-facing dome: crown is high, body is broad below it; no central
    # cross-section, pie sectors or all-over polar coordinate texture.
    outline=curve([(296,322),(328,283),(382,264),(433,267),(466,281),
        (489,277),(536,275),(590,298),(638,343),(671,399),(678,455),
        (654,507),(618,548),(569,578),(515,596),(462,603),(406,595),
        (353,575),(302,543),(267,501),(247,452),(249,400),(270,354)],steps=7,closed=True)
    s.shade('contact-shadow',[(260,567),(367,573),(476,604),(610,580),(666,576),
             (639,615),(532,648),(393,637),(298,606)],(147,157,117),.14)

    # Unequal peel flaps. Body shape is removed from their geometry, so their
    # ink never shows through the white spaces between the front fruit strokes.
    back=curve([(325,347),(302,292),(295,224),(318,177),(363,156),(423,166),
                (449,160),(455,182),(446,199),(465,213),(450,240),(467,262),(421,315)],closed=True)
    left=curve([(297,548),(240,555),(202,527),(175,478),(157,413),(166,353),
                (187,305),(205,310),(201,336),(225,348),(220,374),(249,391),(280,432)],closed=True)
    right=curve([(627,554),(675,534),(713,492),(743,435),(747,392),(764,425),
                 (771,479),(754,537),(716,584),(670,607),(612,609)],closed=True)
    front=curve([(375,559),(348,600),(305,628),(315,652),(299,680),(326,714),
                 (372,743),(429,750),(473,730),(496,698),(489,675),(513,654),(519,618),(492,587)],closed=True)
    peel_specs=[
        ('back-peel',back,[(305,282),(299,224),(318,180),(363,158),(408,166),(450,160)],
         [(306,226),(317,180),(365,155),(418,165),(450,160),(427,181),(367,173),(334,197)],-.23),
        ('left-peel',left,[(187,306),(164,355),(158,413),(176,478),(202,526),(240,553),(291,548)],
         [(186,308),(163,352),(155,408),(174,477),(201,526),(240,551),(281,548),(230,531),(195,472),(181,411),(186,348)],1.08),
        ('right-peel',right,[(746,396),(769,474),(754,535),(715,582),(671,606),(619,609)],
         [(746,394),(773,475),(755,537),(716,584),(670,609),(623,609),(676,584),(716,546),(743,494)],2.11),
        ('front-peel',front,[(300,681),(326,714),(372,743),(429,750),(473,730)],
         [(300,680),(327,714),(373,744),(430,751),(476,729),(436,728),(393,727),(350,703)],.40)]
    for id,poly,edge,skin,angle in peel_specs:
        s.texture(id+'-pith',poly,27,lambda x,y,a=angle:a,[(208,193,156),(221,204,170)],
                  holes=[outline],length=(14,40),width=(1.8,3.1),density=lambda x,y:.68)
        skin_poly=curve(skin,closed=True)
        s.texture(id+'-green',skin_poly,70,lambda x,y,a=angle:a, [GREEN,OLIVE,(85,112,35)],
                  holes=[outline],length=(8,26),width=(2.8,5.6))
        o=s.object(id+'-edge')
        # Trim visible contour runs using the same fruit exclusion.
        visible=mask_for([(0,0),(899,0),(899,899),(0,899)],holes=[outline]).load()
        run=[];piece=0
        for p in curve(edge,steps=14):
            if visible[int(p[0]),int(p[1])]:run.append(p)
            elif len(run)>2:
                s.line(o,f'outer-{piece}',run,GREEN,3.3);run=[];piece+=1
            else:run=[]
        if len(run)>2:s.line(o,f'outer-{piece}',run,GREEN,3.3)
        # A few pale torn edges, never a complete identical border per flap.
        for j in range(0,len(poly)-22,29):
            p=poly[j:j+23]
            if all(visible[int(x),int(y)] for x,y in p):s.line(o,f'torn-{j}',p,(211,195,150),2.0,.84)

    # Curved longitudinal seams wrap down a whole globe; back shoulders pass
    # behind the crown. Front lobes are broad and unequal rather than wedges.
    seams=[
        curve([(460,319),(404,334),(359,376),(337,432),(337,493),(362,546),(406,590)],steps=12),
        curve([(466,320),(438,361),(424,411),(426,478),(447,547),(478,598)],steps=12),
        curve([(472,320),(512,350),(544,399),(560,455),(553,516),(524,579)],steps=12),
        curve([(479,317),(548,329),(606,369),(637,418),(640,468),(616,544)],steps=12),
        curve([(454,311),(407,291),(368,299),(310,336),(266,393)],steps=10),
        curve([(480,309),(517,294),(568,306),(625,344)],steps=10)]
    seam_masks=[(p,5 if i<4 else 4) for i,p in enumerate(seams)]
    # A few pith branches break up the fibres without exposing flesh rays.
    seam_masks.extend([(curve([(352,402),(375,421),(367,448)],steps=7),5),
                       (curve([(552,486),(582,493),(594,519)],steps=7),5)])

    def direction(x,y):
        if y<350:return -.40 if x<465 else .37
        # Nearly vertical at the front, curling round the sides.
        return math.pi/2 + (x-470)/315 + .18*math.sin((y-330)/85)
    def palette(x,y,r):
        if y<352:return r.choice([GOLD,ORANGE,(220,143,29)])
        if y>515 or x<320:return r.choice([ORANGE,(217,117,20),(233,151,28)])
        return r.choice([ORANGE,GOLD,(240,163,37)])
    def density(x,y):
        # An irregular light patch on the upper-right bulge, not a whole ring.
        q=((x-548)/67)**2+((y-385)/51)**2
        return .28 if q<1 else .86
    s.texture('fruit-flesh',outline,700,direction,palette,seams=seam_masks,
              density=density,length=(10,32),width=(3.6,7.2),name='鼓起的橘瓣与不规则线束')
    o=s.object('fruit-contours','局部轮廓与橘络')
    for i,pts in enumerate([
        [(294,324),(329,287),(381,267),(432,270)],
        [(502,280),(538,279),(588,301),(632,342)],
        [(670,413),(675,456),(651,504),(616,544)],
        [(265,476),(286,518),(330,553),(372,578)],
        [(428,598),(460,602),(503,598),(539,589)]]):
        s.line(o,f'outer-{i}',pts,ORANGE,2.1,.84)
    for i,p in enumerate(seams[:4]):
        # Do not outline every seam from top to bottom; enough to show its bow.
        s.line(o,f'seam-{i}',p[13:38],(222,161,62),1.6,.58)
    # Crown is a little irregular depression, high on the fruit, not a centre disc.
    for i,p in enumerate([[(457,310),(463,317),(461,323)],[(468,309),(472,317),(468,325)],
                           [(479,312),(476,320)],[(454,317),(459,325),(466,329)]]):
        s.line(o,f'crown-{i}',p,(178,100,49),2.8,.87)
    return s.scene.data


def leaf(s,id,pts,vein):
    poly=curve(pts,steps=8,closed=True)
    axis=math.atan2(vein[-1][1]-vein[0][1],vein[-1][0]-vein[0][0])
    s.texture(id,poly,50,lambda x,y:axis+.25*math.sin(x/30),
              [(68,110,48),(106,142,54),(133,151,57)],length=(9,28),width=(2.6,4.8))
    o=s.object(id+'-vein');s.line(o,'vein',vein,(65,103,43),2.2,.81)


def pear():
    s=Sketch('歪一点的梨 · 松散彩色干笔',84618)
    s.shade('contact-shadow',[(285,663),(347,648),(474,646),(584,662),(556,683),(411,699),(305,684)],(153,150,98),.14)
    leaf(s,'pear-leaf',[(489,242),(527,182),(598,156),(577,211),(538,239)],[(490,243),(537,208),(593,163)])
    o=s.object('pear-stem');s.line(o,'stem',[(475,267),(483,233),(479,208),(490,184)],(107,91,47),7.0)
    s.line(o,'stem-light',[(482,244),(485,222),(483,209)],(169,142,75),2.1,.75)
    poly=curve([(477,258),(443,260),(426,291),(415,346),(387,386),(338,421),
        (299,468),(278,523),(288,587),(325,638),(379,665),(438,672),
        (495,663),(548,635),(581,591),(589,539),(563,488),(525,444),
        (499,397),(495,342),(508,293),(505,270)],steps=8,closed=True)
    def direction(x,y):return 1.5+(x-442)/245
    def palette(x,y,r):
        if x<356 or y>600:return r.choice([(129,151,47),(154,159,35),(177,157,31)])
        if x>500:return r.choice([(203,163,33),(222,184,43),(167,162,40)])
        return r.choice([(196,184,49),(217,196,60),(166,169,46)])
    s.texture('pear-skin',poly,425,direction,palette,
              density=lambda x,y:.15 if ((x-407)/50)**2+((y-440)/111)**2<1 else .82,
              length=(12,39),width=(2.8,6.2))
    o=s.object('pear-outline')
    for i,p in enumerate([[(476,258),(444,263),(428,294),(416,342)],
        [(379,391),(336,426),(302,473),(281,520),(286,561)],
        [(308,615),(349,649),(390,666),(437,671)],
        [(497,661),(545,636),(577,595),(588,549)],[(506,292),(496,341),(501,393),(525,440)]]):
        s.line(o,f'edge-{i}',p,(135,145,42),2.6,.84)
    r=rng_for('pear-freckles')
    for i in range(27):
        x=r.uniform(310,560);y=r.uniform(460,620)
        s.line(o,f'freckle-{i}',[(x,y),(x+1.6,y+2.3)],(158,137,55),1.4,.66)
    s.line(o,'base-dimple',[(422,660),(432,655),(443,660)],(110,110,47),2.5,.75)
    return s.scene.data


def peach():
    s=Sketch('带叶的桃子 · 松散彩色干笔',84619)
    s.shade('contact-shadow',[(277,632),(369,633),(487,630),(608,619),(581,660),(425,683),(313,670)],(163,144,135),.12)
    leaf(s,'peach-leaf-left',[(434,272),(395,233),(344,220),(288,244),(352,264),(410,282)],[(434,273),(375,251),(302,243)])
    leaf(s,'peach-leaf-right',[(459,271),(478,220),(533,193),(555,175),(548,225),(507,258)],[(459,270),(500,233),(551,181)])
    o=s.object('peach-stem');s.line(o,'stem',[(446,291),(449,265),(442,242)],(115,91,56),5)
    poly=curve([(444,292),(403,279),(354,290),(310,324),(280,370),(267,424),
        (274,488),(302,545),(341,598),(395,641),(453,661),(509,640),
        (563,594),(605,538),(627,478),(629,416),(612,358),(574,315),
        (526,289),(483,287),(461,299)],steps=8,closed=True)
    seam=curve([(462,301),(444,341),(434,399),(447,459),(475,515),(481,567),(459,632)],steps=12)
    def direction(x,y):
        return 1.5+(x-449)/240 + .24*math.sin((y-290)/115)
    def palette(x,y,r):
        if x<414:return r.choice([(236,166,88),(235,179,113),(222,142,95),(227,153,112)])
        if x>526 or y>560:return r.choice([(199,92,110),(214,112,124),(223,133,138)])
        return r.choice([(230,132,132),(235,157,143),(220,118,123)])
    s.texture('peach-skin',poly,425,direction,palette,seams=[(seam,7)],
              density=lambda x,y:.2 if ((x-365)/55)**2+((y-406)/77)**2<1 else .86,
              length=(9,28),width=(3,6.1))
    o=s.object('peach-contour')
    for i,p in enumerate([[(443,293),(403,282),(354,293),(315,323)],
                          [(281,373),(270,427),(278,480)],
                          [(307,551),(345,600),(395,640),(452,660)],
                          [(507,640),(561,594),(601,541)],
                          [(627,460),(626,410),(609,361),(572,318),(526,292),(483,289)]]):
        s.line(o,f'edge-{i}',p,(199,111,109),2.3,.8)
    s.line(o,'cleft-top',[(459,305),(446,342),(439,382)],(197,106,100),2.3,.77)
    s.line(o,'cleft-bottom',[(478,544),(481,570),(468,608),(458,630)],(187,101,111),2.4,.69)
    return s.scene.data


def strawberry():
    s=Sketch('一颗草莓 · 松散彩色干笔',84620)
    s.shade('contact-shadow',[(381,687),(441,674),(521,655),(577,659),(543,696),(446,725),(401,718)],(170,131,135),.12)
    poly=curve([(437,294),(399,276),(353,291),(315,320),(291,365),(295,416),
        (316,475),(346,539),(384,605),(429,677),(461,705),(491,677),
        (532,617),(576,550),(614,479),(634,416),(632,364),(610,322),
        (571,288),(526,277),(480,297)],steps=8,closed=True)
    # Seed holes are reserved in the red stroke mask, irregularly placed and
    # compressed at the turning sides; not a perfect all-over dot lattice.
    seeds=[(365,326,6,9,-20),(422,341,5,8,-8),(483,334,5,8,6),(552,329,5,8,15),
           (329,379,4,8,-26),(392,401,6,9,-14),(452,384,5,8,0),(520,396,6,10,12),(591,383,4,9,25),
           (352,453,5,9,-19),(423,467,6,10,-5),(487,449,6,10,5),(563,459,5,10,19),
           (386,529,5,9,-12),(460,526,6,10,2),(535,534,5,9,15),
           (419,590,5,9,-8),(489,597,5,9,9),(455,658,4,7,2)]
    calyx=[
        ([(461,301),(424,270),(371,270),(336,252),(378,294),(420,313)],[(458,302),(408,288),(348,259)]),
        ([(459,301),(444,258),(410,226),(452,238),(475,269)],[(461,296),(451,265),(417,232)]),
        ([(466,298),(487,251),(531,222),(515,269),(489,301)],[(469,296),(491,262),(525,228)]),
        ([(473,300),(528,275),(572,285),(607,306),(551,306),(514,323)],[(477,303),(529,293),(596,305)]),
        ([(461,299),(436,320),(416,354),(449,341),(474,316)],[(462,304),(440,332),(422,349)]),
        ([(477,302),(502,320),(523,350),(491,336),(471,319)],[(478,307),(500,329),(520,347)])]
    holes=[ellipse(x,y,rx+3,ry+3,rotate=ang,n=20) for x,y,rx,ry,ang in seeds]
    holes.extend(curve(p,steps=8,closed=True) for p,v in calyx)
    s.texture('berry-skin',poly,485,lambda x,y:1.53+(x-463)/285,
              lambda x,y,r:r.choice([(214,64,62),(229,83,70),(216,78,83)] if x>464 or y>510
                                    else [(235,108,82),(237,126,92),(222,89,73)]),holes=holes,
              density=lambda x,y:.24 if ((x-366)/32)**2+((y-369)/63)**2<1 else .9,
              length=(9,29),width=(3,6.7))
    o=s.object('berry-seeds')
    for i,(x,y,rx,ry,ang) in enumerate(seeds):
        a=math.radians(ang)
        s.line(o,f'seed-{i}',[(x+math.sin(a)*ry*.6,y-ry*.6),(x-1,y),
                              (x-math.sin(a)*ry*.6,y+ry*.55)],(204,162,65),2.8,.9)
        s.line(o,f'seed-shadow-{i}',[(x+3,y-2),(x+4,y+4)],(167,89,61),1.6,.6)
    # Calyx overlaps the reserved white shapes in the red shoulders.
    for i,(p,v) in enumerate(calyx):
        leaf(s,f'calyx-{i}',p,v)
    o=s.object('berry-contour')
    for i,p in enumerate([[(338,303),(309,333),(293,368),(298,411)],
        [(315,470),(348,539),(384,601)],[(421,664),(451,699),(464,704),(489,679)],
        [(534,615),(576,546),(612,481)],[(634,415),(630,365),(609,325)]]):
        s.line(o,f'edge-{i}',p,(196,65,67),2.6,.83)
    s.line(o,'stem',[(469,286),(476,263),(470,244)],(75,106,46),4.5,.92)
    return s.scene.data


BUILDERS={'mandarin':orange,'pear':pear,'peach':peach,'strawberry':strawberry}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fruit',choices=['all',*BUILDERS],default='all')
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/loose-fruits-v2')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    names=list(BUILDERS) if args.fruit=='all' else [args.fruit]
    for name in names:
        scene=BUILDERS[name]()
        print(f"Rendering {name}: {sum(len(o['marks']) for o in scene['objects'])} marks",flush=True)
        result=render_to(scene,args.out/name,overwrite=args.overwrite)
        print(f"Rendered {name}; warnings: {result['warnings']}",flush=True)
    if args.fruit=='all':
        sheet=Image.new('RGB',(1800,1800),'white')
        for i,name in enumerate(names):
            sheet.paste(Image.open(args.out/name/'artwork.png').convert('RGB'),((i%2)*900,(i//2)*900))
        sheet.save(args.out/'fruit-sheet.png')


if __name__=='__main__':main()
