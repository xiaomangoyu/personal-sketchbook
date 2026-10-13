#!/usr/bin/env python3
"""An inquisitive tabby has claimed the paper breakfast bag. Editable scene v1."""
from pathlib import Path
import argparse
import math
import random
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scene_tools import Scene, ellipse, curve, bezier, transform
from render import render_to

INK = (73, 62, 55)
PENCIL = (106, 84, 64)


def build():
    s = Scene('猫把早餐纸袋当成了窝', 1400, 1100, seed=121, paper=(250, 246, 232), grain=.48)
    rng = random.Random(16)
    def line(o, id, pts, color=INK, width=2.1, opacity=.78, smooth=False):
        return o.line(id, pts, color, kind='pencil', width=width, opacity=opacity,
                      pressure=.7, wobble=.55, gaps=.015, smooth=smooth)
    def wash(o, id, pts, color, opacity=.65, edge=.23):
        return o.fill(id, pts, color, opacity=opacity, edge=edge, bleed=1.6, grain=.45)
    # The tabletop leads behind the bag and across the cloth. Light falls from upper left.
    wall = s.object('morning-light', '早晨墙面与桌面')
    wash(wall, 'sunlight', [(83,144),(389,87),(653,600),(97,655)], (246,214,147), .19, .05)
    wash(wall, 'table', [(58,659),(1248,604),(1364,996),(120,1017)], (217,146,119), .24, .06)
    line(wall,'back-edge',[(67,661),(233,654),(393,644),(1218,606)],(168,126,100),1.6,.39)
    for i in range(6):
        y=785+i*38
        line(wall,f'wood-{i}',[(198+i*43,y),(428+i*26,y-9),(969+i*39,y-27)],(176,121,100),.85,.3)
    cloth=s.object('blue-cloth','前景蓝色格纹餐巾')
    poly=[(80,788),(335,708),(615,901),(423,1044),(104,987)]
    wash(cloth,'cloth-body',poly,(199,216,213),.57)
    def clipped(a,b):
        """Clip a straight weave stroke to the actual cloth, preserving its hem."""
        dx,dy=b[0]-a[0],b[1]-a[1]
        crossings=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            ex,ey=q[0]-p[0],q[1]-p[1]
            den=dx*ey-dy*ex
            if abs(den)<1e-8: continue
            u=((p[0]-a[0])*dy-(p[1]-a[1])*dx)/den
            t=((p[0]-a[0])*ey-(p[1]-a[1])*ex)/den
            if 0<=u<=1: crossings.append(t)
        if len(crossings)<2: return [a,b]
        lo,hi=max(0,min(crossings)),min(1,max(crossings))
        return [(a[0]+dx*lo,a[1]+dy*lo),(a[0]+dx*hi,a[1]+dy*hi)]
    for i in range(7):
        x=104+i*48
        line(cloth,f'warp-{i}',clipped((x-50,665-i*11),(x+165,1074-i*4)),(63,133,145),7,.32)
    for i in range(6):
        y=812+i*32
        line(cloth,f'weft-{i}',clipped((23+(i*3),y+22),(680+i*24,y-172)),(51,123,140),6,.25)
    line(cloth,'hem',[(109,977),(417,1034),(592,909)],(83,120,130),1.3,.62)
    shadow=s.object('bag-ground-shadow','纸袋接触投影')
    wash(shadow,'cast',ellipse(765,894,348,69,rotate=-5,rough=.035,seed=1),(100,111,112),.26,.05)
    wash(shadow,'contact',ellipse(730,881,207,31,rotate=-3),(95,86,68),.28,.07)
    # A green mug stays smaller and behind the cat.
    mug=s.object('tea-mug','早餐茶杯')
    handle=curve([(242,516),(194,501),(170,532),(174,591),(206,609),(240,588)])
    line(mug,'handle-back',handle,(52,117,106),17,.7)
    line(mug,'handle-light',curve([(231,525),(199,520),(190,547),(196,583),(230,580)]),(169,190,165),5,.65)
    cup=curve([(232,492),(249,650),(288,674),(376,660),(407,625),(408,486)],closed=True)
    wash(mug,'body',cup,(57,135,117),.79)
    wash(mug,'dark-side',curve([(360,510),(402,490),(403,619),(376,656),(341,657)],closed=True),(41,103,101),.62)
    line(mug,'left-wall',[(232,504),(240,596),(250,648),(288,670)],INK,2.8,.8)
    line(mug,'right-wall',[(408,500),(405,608),(376,658),(310,668)],INK,2,.65)
    rim=ellipse(320,493,88,25,rotate=-3,rough=.025,seed=8)
    wash(mug,'rim-paper',rim,(242,235,200),.94)
    wash(mug,'tea',ellipse(321,495,75,15,rotate=-3),(148,87,43),.73)
    line(mug,'rim',rim,(63,87,65),2.3,.82)
    line(mug,'highlight',[(257,535),(262,588),(271,619)],(231,232,199),5,.73)
    for i,pts in enumerate([[(302,457),(287,428),(309,398),(307,373)],[(341,458),(359,430),(343,402)]]):
        line(mug,f'steam-{i}',curve(pts),(134,134,126),1.2,.33)
    # Back rim sits behind head; dark interior creates a readable opening.
    back=s.object('bag-rear-rim','纸袋背面与袋口')
    backpoly=[(431,531),(442,477),(491,493),(535,469),(588,483),(633,473),(676,486),(733,475),(797,493),(851,480),(890,523),(851,600),(477,617)]
    wash(back,'paper',backpoly,(189,137,73),.78)
    line(back,'rim',backpoly[:11],PENCIL,2.5,.84)
    wash(back,'opening',curve([(450,535),(494,505),(725,497),(859,526),(849,597),(638,642),(478,600)],closed=True),(93,69,51),.8)
    # The head: muzzle wider than the forehead, ears anchored inside one silhouette.
    head=s.object('cat-head','虎斑猫头部')
    headpts=curve([(474,455),(461,386),(476,315),(470,213),(483,178),(564,271),(635,251),(705,269),(799,212),(801,307),(836,373),(842,439),(813,490),(757,526),(676,550),(585,537),(517,503)],closed=True)
    for i in range(2): wash(head,f'opaque-ground-{i}',headpts,(245,224,181),1,.05)
    wash(head,'fur-base',headpts,(210,163,102),.76)
    wash(head,'forehead-warm',curve([(506,287),(641,267),(726,295),(724,380),(614,388),(495,377)],closed=True),(200,142,72),.43)
    wash(head,'right-shadow',curve([(745,288),(800,307),(832,383),(832,456),(782,502),(723,525),(730,443),(752,371)],closed=True),(141,131,113),.49)
    line(head,'left-outline',curve([(482,182),(473,222),(479,315),(463,383),(475,454),(516,499)]),PENCIL,3.0,.9)
    line(head,'right-outline',curve([(797,212),(800,307),(832,375),(841,438),(814,486),(757,527)]),PENCIL,3.3,.83)
    line(head,'forehead',curve([(563,271),(607,254),(647,255),(703,269)]),PENCIL,2.1,.8)
    # Ear planes, one catching light, the other partly turned away.
    ears=s.object('cat-ears','耳朵内侧')
    for id,pts in [('left',[(489,209),(544,278),(500,309)]),('right',[(781,240),(780,310),(739,287)])]:
        wash(ears,id,curve(pts,closed=True),(200,126,118),.73)
    line(ears,'left-ridge',[(489,208),(500,271),(521,296)],PENCIL,1.8,.64)
    line(ears,'right-ridge',[(780,239),(759,273),(745,292)],PENCIL,2,.72)
    for i in range(6):
        line(ears,f'ear-fur-{i}',[(495+i*5,273+i*3),(491+i*5,245+i*4)],(239,220,174),2,.82)
    # Stripes follow skull and cheeks rather than evenly encircling the face.
    stripes=s.object('cat-tabby-markings','随头部转向的虎斑')
    stripe_shapes=[[(576,272),(587,276),(606,333),(597,346),(585,307)],[(628,260),(642,261),(653,325),(642,346),(629,304)],[(680,269),(694,274),(684,316),(671,333),(672,299)],[(498,328),(507,313),(551,340),(558,356),(531,348)],[(475,386),(480,370),(520,386),(530,400),(507,399)],[(480,430),(489,419),(531,431),(547,446),(517,445)],[(796,329),(804,345),(761,361),(744,356),(765,341)],[(828,389),(831,406),(788,414),(774,406),(800,396)],[(827,440),(819,457),(779,456),(765,442),(790,444)]]
    for i,p in enumerate(stripe_shapes):
        wash(stripes,f'tabby-{i}',curve(p,closed=True),(111,89,65),.71)
    # Cream brow, muzzle and slightly mismatched sleepy eye shapes.
    face=s.object('cat-face','绿眼睛与奶油色鼻口')
    for id,p in [('left-brow',[(514,361),(543,342),(584,350),(597,369),(557,365)]),('right-brow',[(682,365),(716,351),(757,359),(770,379),(714,372)])]:
        wash(face,id,curve(p,closed=True),(241,224,180),.77)
    muzzle=curve([(555,440),(602,420),(639,431),(671,426),(713,440),(731,473),(703,508),(652,521),(600,509),(560,481)],closed=True)
    wash(face,'muzzle',muzzle,(246,233,196),.96)
    wash(face,'chin',curve([(603,499),(693,500),(703,522),(653,540),(616,526)],closed=True),(241,231,197),.87)
    for id,p in [('left-eye',[(514,387),(535,374),(565,376),(588,393),(564,411),(538,409)]),('right-eye',[(681,396),(706,380),(735,383),(754,400),(731,417),(707,414)])]:
        pts=curve(p,closed=True)
        wash(face,id+'-white',pts,(205,205,126),.93)
        line(face,id+'-lid',curve(p[:4]),INK,4.2,.95)
        line(face,id+'-lower',curve(p[3:]+[p[0]]),PENCIL,1.7,.6)
    for id,x,y in [('left',553,393),('right',716,399)]:
        wash(face,id+'-iris',ellipse(x,y,12,16),(102,124,64),.86)
        line(face,id+'-pupil',[(x+1,y-13),(x-1,y+11)],(49,57,43),6.3,.95)
        wash(face,id+'-glint',ellipse(x-4,y-6,3.2,4),(249,244,219),1)
    nose=curve([(620,448),(638,442),(657,449),(640,463)],closed=True)
    wash(face,'nose',nose,(167,103,98),.96)
    line(face,'nose-top',[(620,448),(637,443),(654,448)],(104,72,63),2.2,.84)
    line(face,'nose-mouth',curve([(640,463),(639,476),(625,483),(609,477)]),INK,2.2,.86)
    line(face,'other-mouth',curve([(639,476),(655,484),(675,478)]),INK,2,.74)
    for i,(x,y) in enumerate([(587,457),(603,456),(600,469),(686,457),(701,461),(689,472)]):
        line(face,f'whisker-dot-{i}',[(x,y),(x+1,y+1)],PENCIL,2,.7)
    # Broken directional tufts, not an evenly hairy contour.
    fur=s.object('cat-fur-lines','面颊短毛与胡须')
    for side,origin,direction in [('l',(504,475),-1),('r',(802,473),1)]:
        for i in range(10):
            x=origin[0]+rng.uniform(-8,10); y=origin[1]+i*3
            line(fur,f'{side}-fur-{i}',[(x,y),(x+direction*rng.uniform(9,18),y-rng.uniform(0,7))],PENCIL,1.3,.52)
    whiskers=[[(605,472),(551,458),(478,451),(425,452)],[(601,480),(544,479),(481,488),(439,504)],[(602,488),(551,500),(506,518)],[(684,474),(749,461),(818,462),(883,477)],[(686,483),(750,488),(823,511),(855,526)],[(682,491),(749,512),(793,540)]]
    for i,p in enumerate(whiskers):
        line(fur,f'whisker-{i}',curve(p),(100,85,71),1.1,.68)
    for i in range(32):
        x=521+rng.uniform(0,223); y=310+rng.uniform(0,37)
        if 574<x<695: continue
        line(fur,f'brow-hair-{i}',[(x,y),(x+rng.uniform(-4,4),y+rng.uniform(7,12))],(125,93,55),1.05,.36)
    # Front paper hides the lower head; every major wrinkle starts at a folded corner.
    bag=s.object('bag-front','皱纸袋正面')
    p=[(429,553),(480,568),(507,552),(553,577),(597,563),(641,583),(691,561),(740,578),(787,553),(848,560),(881,589),(864,689),(891,807),(855,882),(556,916),(505,884),(496,790),(463,677)]
    for i in range(2): wash(bag,f'paper-ground-{i}',p,(231,200,145),1,.08)
    wash(bag,'base',p,(204,159,94),.89)
    wash(bag,'right-fold',[(792,570),(845,565),(881,589),(864,688),(891,807),(855,882),(779,890),(806,797),(785,688)],(145,112,70),.55)
    wash(bag,'left-lit',[(432,557),(503,571),(524,690),(544,808),(556,900),(509,880),(496,790),(464,677)],(240,202,132),.58)
    wash(bag,'central-light',[(552,613),(704,611),(752,743),(727,860),(572,882)],(232,193,123),.38,.07)
    line(bag,'rim',p[:11],(93,70,45),3.2,.93)
    line(bag,'outer',p[10:]+[p[0]],PENCIL,2.5,.82)
    foldpaths=[[(435,564),(491,660),(520,754)],[(480,568),(529,652),(562,671)],[(505,887),(557,839),(544,805)],[(551,904),(602,850),(653,850)],[(855,879),(805,803),(824,731),(791,638)],[(880,800),(830,810),(778,847)],[(861,686),(815,673),(791,639)],[(707,579),(731,637),(752,660)],[(598,568),(583,628),(602,669)],[(747,797),(784,753),(792,699)]]
    for i,pth in enumerate(foldpaths):
        line(bag,f'crease-{i}',pth,(124,96,58),1.5,.64)
    for i,pth in enumerate([[(497,662),(513,684),(516,715)],[(537,835),(557,860),(547,885)],[(822,737),(839,783),(865,799)],[(807,808),(826,844),(849,866)]]):
        line(bag,f'crease-light-{i}',pth,(246,215,151),4.2,.54)
    hatchpoly=[(803,663),(827,716),(808,802),(853,879),(782,889),(802,803),(784,698)]
    bag.hatch('gusset-hatching',hatchpoly,(123,97,64),opacity=.26,width=1.1,spacing=6,angle=72)
    # A single foreleg comes out over the right front lip, flattening its paper edge.
    paw=s.object('cat-paw','搭在纸袋外的一只前爪')
    pawpoly=curve([(704,505),(751,498),(783,538),(787,588),(775,648),(758,670),(739,672),(722,660),(711,636),(713,586),(699,551)],closed=True)
    for i in range(2): wash(paw,f'fur-ground-{i}',pawpoly,(239,219,171),1,.05)
    wash(paw,'base',pawpoly,(217,175,114),.93)
    wash(paw,'white-sock',curve([(716,600),(739,604),(773,594),(775,646),(759,669),(739,671),(722,658)],closed=True),(247,235,197),.97)
    wash(paw,'under-shadow',curve([(751,511),(777,536),(787,581),(775,629),(766,652),(756,639),(765,583),(751,552)],closed=True),(145,131,105),.36)
    line(paw,'right-contour',curve([(751,500),(778,538),(786,588),(775,646),(758,669),(739,671),(722,658)]),PENCIL,2.9,.88)
    line(paw,'left-contour',curve([(704,530),(714,583),(712,634),(722,658)]),PENCIL,2.0,.65)
    for i,pth in enumerate([[(710,544),(740,553),(768,550)],[(716,574),(744,582),(779,577)]]):
        line(paw,f'leg-band-{i}',curve(pth),(119,92,63),8,.68)
    for i,x in enumerate([737,753]):
        line(paw,f'toe-{i}',curve([(x,646),(x-2,658),(x+2,666)]),PENCIL,1.8,.65)
    # Breakfast on a wonky ceramic plate. Repetition follows the croissant curve.
    plate=s.object('breakfast-plate','右侧早餐碟')
    wash(plate,'shadow',ellipse(1085,830,168,47,rotate=-7),(99,114,113),.2,.07)
    wash(plate,'plate',ellipse(1070,801,177,73,rotate=-9,rough=.014,seed=2),(242,237,211),.93)
    line(plate,'outer',ellipse(1070,801,177,73,rotate=-9,rough=.014,seed=2),(79,127,137),2.3,.6)
    line(plate,'inner',ellipse(1070,801,147,50,rotate=-9),(94,142,145),1.3,.44)
    croissant=s.object('croissant','掰开前的牛角包')
    cp=curve([(935,785),(954,737),(1002,704),(1055,695),(1115,710),(1169,746),(1205,792),(1182,806),(1141,784),(1100,766),(1065,760),(1026,769),(978,800)],closed=True)
    wash(croissant,'pastry',cp,(224,151,54),.86)
    wash(croissant,'toasted',curve([(960,747),(1002,711),(1057,700),(1118,719),(1140,747),(1083,738),(1033,731),(992,752)],closed=True),(184,100,39),.43)
    line(croissant,'edge',cp,(115,78,39),2.3,.75)
    seams=[[(970,734),(997,751),(1000,784)],[(1007,708),(1033,732),(1034,765)],[(1060,697),(1079,728),(1073,760)],[(1112,713),(1122,738),(1106,769)],[(1152,737),(1155,763),(1140,782)]]
    for i,pth in enumerate(seams):
        line(croissant,f'fold-{i}',curve(pth),(124,81,35),2.3,.69)
        line(croissant,f'light-{i}',transform(curve(pth),translate=(-6,0)),(246,216,142),4,.57)
    crumbs=s.object('breakfast-crumbs','掉在桌上的碎屑')
    for i,(x,y,r) in enumerate([(996,856,5),(955,875,4),(928,843,3),(1118,862,4),(1010,893,3),(393,882,4),(356,910,3)]):
        wash(crumbs,f'crumb-{i}',[(x-r,y-r),(x+r,y),(x+1,y+r)],(191,124,51),.73)
    return s.data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'examples/gallery/breakfast-cat')
    parser.add_argument('--overwrite',action='store_true',help='Replace an existing renderer output during deliberate iteration.')
    args=parser.parse_args()
    manifest=render_to(build(),args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out / 'artwork.png'} ({len(manifest['layers'])} editable objects)")


if __name__=='__main__': main()
