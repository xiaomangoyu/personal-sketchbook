#!/usr/bin/env python3
"""Selective upstream watercolour on pure white, retaining the house linework.

White walls and floors are intentional negative space. Wet pigment is authored
as a few irregular washes and overlapping glazes, not a desaturated crayon layer.
The reference and previous outputs are never sampled as drawing pixels.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, curve, ellipse
from render import render_to
from house_pen_study import build as build_pen


def washes(scene):
    o=scene.object('watercolour-atmosphere','留白之间的少量冷暖洗色')
    def wash(id,points,color,opacity=.4,bleed=4,edge=.3,layers=2,soft=True):
        strength={'bed-watercolour':1.4,'sofa-watercolour':1.65,
                  'people-watercolour':1.5,'watercolour-atmosphere':1.15}.get(o.value['id'],1)
        o.fill(id,curve(points,steps=5,closed=True) if soft else points,color,
               kind='wash',opacity=min(.98,opacity*strength),grain=.83,bleed=bleed,edge=edge,
               layers=layers,offset=[.5,.5])

    # These islands of wash are smaller than the walls, and have unequal edges.
    # The hall, rear bathroom and most ground planes stay genuinely white.
    wash('bedroom-cool-air',[(45,351),(63,339),(88,327),(94,335),(82,352),
         (83,367),(70,378),(69,395),(52,407),(44,391)],(108,158,170),.22,7,.14)
    wash('bedroom-corner',[(47,353),(67,341),(64,366),(54,379),(47,382)],
         (78,127,150),.14,3,.28)
    wash('living-warm-air',[(850,471),(867,459),(876,456),(878,470),(869,484),
         (872,502),(866,520),(852,529),(847,511)],(211,154,121),.18,8,.10)
    wash('sofa-back-wall-watermark',[(899,452),(913,443),(920,447),(920,461),
         (916,475),(920,485),(912,494),(906,510),(897,515),(902,494),
         (899,482),(904,468)],(118,155,173),.29,6,.24)
    wash('bath-shadow',[(704,282),(719,287),(724,308),(723,329),(734,340),
         (728,357),(712,351),(705,326)],(134,141,173),.16,7,.10)
    wash('washing-reflection',[(52,687),(64,694),(71,713),(68,732),(59,739),(52,730)],
         (119,159,178),.16,4,.18)
    wash('entry-floor-shadow',[(858,1019),(877,1011),(901,1017),(922,1016),
         (937,1027),(916,1036),(885,1044),(863,1037)],(138,151,164),.19,6,.12)

    # Warm pigment is pooled at one end of the bed, leaving the pillow and a
    # broad highlight unpainted instead of tracing its complete perimeter.
    o=scene.object('bed-watercolour','床铺的暖红与少量青绿')
    wash('bed-red-first',[(190,435),(212,421),(235,417),(258,425),(291,436),
         (309,446),(288,456),(279,460),(263,457),(247,467),(229,468),(214,457)],
         (180,84,89),.57,3.5,.39,3)
    wash('bed-red-pool',[(248,437),(270,439),(291,443),(301,446),(285,453),
         (271,452),(253,459),(243,455)],(184,102,115),.29,2.3,.42)
    wash('bed-red-lift',[(197,438),(218,427),(231,432),(230,444),(216,449)],
         (224,159,124),.26,6,.14)
    wash('blanket-green',[(216,495),(234,501),(243,506),(261,498),(270,497),
         (267,504),(248,512),(236,512),(217,505)],(119,157,137),.28,2.4,.23)
    wash('bedside-contact',[(224,551),(244,557),(250,558),(267,549),(278,548),
         (263,557),(244,568),(226,560)],(136,143,158),.16,3,.12)

    o=scene.object('sofa-watercolour','沙发上的绿与蓝，保留垫面高光')
    wash('sofa-arm',[(867,580),(873,571),(881,576),(885,587),(882,601),
         (885,618),(878,628),(867,623),(866,605)],(71,137,115),.52,2.8,.38,3)
    wash('sofa-seat',[(890,593),(907,582),(918,575),(931,581),(949,588),
         (954,596),(938,606),(925,622),(916,625),(909,616),(891,610)],
         (94,151,124),.49,3.8,.32,3)
    wash('sofa-back-cushion',[(897,557),(907,551),(914,551),(912,563),
         (919,569),(908,575),(898,576)],(99,145,135),.31,3.6,.28)
    wash('sofa-front',[(927,640),(949,626),(971,615),(994,604),(1002,600),
         (1001,611),(982,622),(964,631),(948,643),(930,653)],
         (72,134,120),.49,2.6,.43,3)
    wash('sofa-shadow',[(934,647),(951,637),(962,635),(973,625),(989,620),
         (977,630),(957,641),(940,652)],(92,124,151),.22,3.5,.25)

    o=scene.object('people-watercolour','人物服装与包上的水彩重点')
    wash('elder-skirt',[(169,501),(184,502),(201,496),(201,507),(198,521),
         (188,526),(172,522)],(102,150,151),.46,2,.3)
    wash('elder-cardigan',[(177,461),(181,459),(181,472),(175,482),(169,484)],
         (181,127,142),.36,1.5,.28)
    wash('standing-shirt',[(819,558),(828,561),(840,559),(849,554),(849,571),
         (846,579),(850,590),(848,608),(835,607),(824,603),(822,587)],
         (114,161,184),.42,3.2,.27)
    wash('standing-side',[(813,575),(818,579),(820,595),(826,608),(819,608),(814,596)],
         (81,131,159),.23,2,.26)
    wash('seated-shirt',[(920,537),(930,537),(938,542),(947,548),(958,549),
         (962,554),(958,564),(947,561),(936,555),(925,548)],
         (50,111,156),.55,2.6,.35,3)
    wash('seated-trousers',[(958,554),(975,552),(989,551),(1001,554),
         (997,561),(982,564),(972,560),(960,563)],(213,179,122),.30,2,.22)
    wash('child-shirt',[(1075,695),(1087,701),(1102,693),(1103,708),
         (1104,719),(1090,722),(1074,718)],(102,152,180),.50,2.5,.32)
    wash('child-shoulder',[(1072,690),(1078,689),(1084,693),(1082,699),(1075,698)],
         (87,134,173),.24,2,.24)
    wash('entry-coat',[(887,903),(894,897),(900,903),(904,917),(902,931),
         (892,930),(888,921)],(133,132,166),.39,2.6,.28)
    wash('entry-trousers',[(882,946),(891,947),(891,962),(886,984),
         (886,1009),(880,1012),(879,994),(881,978)],(71,148,153),.59,2.3,.38,3)
    wash('entry-bag',[(873,933),(882,934),(891,937),(887,949),(879,948),(871,944)],
         (203,130,104),.64,2,.4,3)

    o=scene.object('small-watercolour-notes','灯、门与少数生活物件')
    wash('lamp',[(677,526),(691,520),(706,524),(714,531),(705,535),(688,536)],
         (221,188,123),.28,3,.18)
    wash('rug-sweep',[(513,646),(532,635),(552,633),(569,637),(554,642),
         (534,644),(526,654),(530,665),(542,678),(559,687),
         (579,695),(580,703),(559,699),(542,690),(526,676),(515,664)],
         (201,153,146),.26,6,.14)
    wash('rug-damp-edge',[(532,681),(548,691),(564,696),(578,697),
         (579,703),(562,701),(546,695)],(177,129,142),.18,4,.29)
    wash('shirt-on-board',[(478,607),(490,610),(495,621),(488,625),
         (486,641),(480,644),(478,630)],(209,148,119),.36,2.5,.32)
    wash('tv-light',[(1091,542),(1114,547),(1124,554),(1141,555),(1157,560),
         (1153,584),(1134,582),(1114,572),(1093,571)],(141,177,143),.27,4.5,.18)
    wash('door-bottom',[(1007,983),(1018,975),(1021,980),(1015,998),
         (1019,1010),(1035,1001),(1035,1017),(1009,1032)],
         (195,132,118),.38,3.5,.3)
    wash('door-light',[(1010,903),(1033,889),(1033,914),(1027,923),
         (1033,931),(1010,944)],(224,185,114),.31,4,.2)
    wash('washing-glass',ellipse(172,691,10,19,rotate=14,n=32),
         (121,160,181),.26,3,.23,soft=False)

    # Individual step washes make an interrupted rhythm; no continuous orange floor.
    o=scene.object('stair-watercolour','楼梯上断续的暖色与冷影')
    for i in (1,4,7,10):
        x=655+i*15;y=764+i*23;u=735+i*15;v=718+i*23
        wash(f'step-warm-{i}',[(x+13,y+1),(u-6,v+3),(u+6,v+9),
             (x+25,y+9),(x+17,y+8)],(204,165,119),.28,2.4,.24,soft=False)
    for i in (2,6,9):
        x=655+i*15;y=764+i*23;u=735+i*15;v=718+i*23
        wash(f'step-cool-{i}',[(x+19,y+14),(u+10,v+14),(u+10,v+20),(x+19,y+20)],
             (138,146,175),.20,2.4,.2,soft=False)


def build():
    pen=build_pen(ink_only=True)
    scene=Scene('住宅剖面 · 白底留白水彩',width=1354,height=1332,
                seed=pen['seed'],paper=(255,255,255),grain=0)
    scene.data['engine']='pencil-case'
    washes(scene)
    for obj in pen['objects']:
        for mark in obj['marks']:
            if mark['kind']=='ink':
                mark['color']=[65,70,76]
                mark['opacity']*=.89
                mark['overdraw']=0
            elif mark['kind']=='hatch':
                mark['color']=[114,120,132]
                mark['opacity']*=.45
        scene.data['objects'].append(obj)
    return scene.data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-watercolour-v4')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    scene=build()
    print(f"Rendering {sum(len(o['marks']) for o in scene['objects'])} upstream marks",flush=True)
    result=render_to(scene,args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {result['warnings']}")
