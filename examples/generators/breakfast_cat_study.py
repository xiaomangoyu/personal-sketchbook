#!/usr/bin/env python3
"""A quieter second study: a sleepy cat leaning over a crumpled breakfast bag.

Uses the original pencil-case ink and wash brushes through the editable renderer.
The old gallery image is retained for comparison.
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scene_tools import Scene, curve, ellipse, transform
from render import render_to

INK = (58, 52, 44)
SOFT = (108, 98, 83)


def build(ink_only=False):
    scene = Scene('纸袋里的午睡 · 笔触修订', 900, 1100, seed=2213,
                  paper=(249, 247, 239), grain=.65)
    scene.data['engine'] = 'pencil-case'

    def pen(obj, name, points, *, width=1.45, opacity=.91, soft=False,
            smooth=True, gaps=.055, overdraw=0, **kw):
        return obj.line(name, points, SOFT if soft else INK, width=width * 1.22,
                        opacity=opacity, smooth=smooth, wobble=1.05,
                        pressure=.5, gaps=gaps, gap_length=[2, 5], step=1.6,
                        nib=True, jitter=.18, overdraw=overdraw, **kw)

    def wash(obj, name, points, color, opacity=.22, *, offset=(1, 2), edge=.16):
        return obj.fill(name, points, color, opacity=opacity, layers=1,
                        offset=list(offset), grain=.64, bleed=1.4, edge=edge)

    # Small, disconnected contact marks establish the table without filling it.
    ground = scene.object('ground', '少量着地线')
    wash(ground, 'bag-contact', curve([(410,832),(469,828),(554,835),(616,836),
         (644,845),(562,852),(447,844)], closed=True), (146,143,129), .16)
    pen(ground, 'left-table', [(175,836),(239,838),(293,836)], soft=True,
        width=.7, opacity=.36, smooth=False, gaps=.14)
    pen(ground, 'right-table', [(601,849),(652,850),(697,847)], soft=True,
        width=.65, opacity=.30, gaps=.18)

    # Only visible negative spaces inside the opening are shaded: no opaque cat cutout.
    opening = scene.object('bag-opening', '纸袋口与空隙')
    wash(opening, 'left-gap', [(368,593),(388,579),(404,592),(414,615),(394,626)],
         (121,100,72), .34)
    wash(opening, 'right-gap', [(528,603),(574,595),(615,601),(608,620),(555,630)],
         (104,89,70), .30)
    pen(opening, 'left-lip', [(364,596),(383,577),(397,582)], width=1.3,
        smooth=False, overdraw=1)
    pen(opening, 'rear-right-fold', [(494,587),(525,594),(572,589),(611,598)],
        width=.95, opacity=.70, smooth=False)
    pen(opening, 'right-corner', [(614,601),(628,611),(620,627)],
        width=.85, opacity=.65, smooth=False, gaps=.01)

    # One tilted, three-quarter head, deliberately not a mirrored face symbol.
    head = scene.object('cat-head', '偏头睡着的小猫')
    def face(points):
        return transform(points, rotate=-13, translate=(451,565))
    wash(head, 'near-ear-pink', face([(-47,-63),(-39,-38),(-22,-45)]),
         (213,150,150), .47, offset=(0,1))
    wash(head, 'far-ear-pink', face([(27,-43),(45,-58),(40,-30)]),
         (213,150,150), .35, offset=(1,0))
    wash(head, 'forehead-warmth', face([(-28,-37),(-4,-47),(20,-40),(15,-23),
         (-2,-18),(-27,-22)]), (181,154,104), .37)
    wash(head, 'near-cheek-warmth', face([(-49,2),(-29,5),(-23,21),(-42,25)]),
         (190,158,112), .25)
    pen(head, 'near-ear', face([(-53,-14),(-50,-33),(-51,-69),(-22,-45)]),
        width=1.5, smooth=False, overdraw=1, gaps=.035)
    pen(head, 'forehead', face([(-19,-45),(-5,-48),(13,-45)]),
        width=1.2, gaps=.015)
    pen(head, 'far-ear', face([(19,-44),(46,-67),(43,-31),(48,-18)]),
        width=1.55, smooth=False, gaps=.025)
    pen(head, 'left-face', face([(-54,-4),(-57,6),(-49,16),(-52,23),(-40,27)]),
        width=1.55, smooth=False, gaps=.035, overdraw=1)
    pen(head, 'cheek', face([(45,-6),(50,10),(40,23),(36,29),(22,35)]),
        width=1.35, gaps=.045)
    pen(head, 'chin', face([(-34,30),(-21,35),(-7,34)]),
        width=1.65, gaps=.015)
    pen(head, 'near-ear-inner', face([(-43,-55),(-37,-38),(-31,-42)]),
        width=.75, soft=True, opacity=.52, smooth=False, gaps=.075)
    pen(head, 'far-ear-inner', face([(36,-48),(34,-34)]),
        width=.7, soft=True, opacity=.47, smooth=False)
    # The eyes follow the same tilted facial plane, with a shorter far eye.
    # Fine features use a smaller tremor than contour lines.
    for name,pts,width in [
        ('near-eye',[(-38,-1),(-32,3),(-25,3),(-19,0)],2.05),
        ('far-eye',[(3,-5),(8,-2),(15,-4)],1.70),
        ('nose',[(-25,15),(-18,15),(-23,19),(-25,15)],1.65),
        ('muzzle-left',[(-23,19),(-26,24),(-33,23)],.85),
        ('muzzle-right',[(-23,19),(-20,24),(-15,23)],.85),
    ]:
        head.line(name,face(pts),INK,kind='ink',width=width,opacity=.98,
                  pressure=.45,wobble=.35,gaps=0,smooth=True,nib=True,jitter=.08)
    for name,pts in [
        ('whisker-left-1',[(-43,17),(-62,12),(-76,12)]),
        ('whisker-left-2',[(-43,21),(-60,25),(-72,29)]),
        ('whisker-right-1',[(-2,14),(18,10),(32,10)]),
        ('whisker-right-2',[(-2,19),(18,23),(28,29)]),
    ]:
        pen(head,name,face(pts),width=.6,opacity=.65,gaps=.07)
    for i,pts in enumerate([
        [(-18,-38),(-13,-27),(-12,-21)],
        [(-5,-41),(-1,-31),(0,-26)],
        [(-49,3),(-39,7)],
        [(37,9),(28,12)],
    ]):
        pen(head,f'tabby-{i}',face(pts),width=1.25,soft=True,opacity=.49,
            smooth=False,gaps=.09)

    # Shoulder disappears into the bag; only one resting foreleg crosses the front rim.
    cat = scene.object('cat-paw', '搭过袋口的前爪')
    pen(cat,'shoulder',[(482,599),(501,600),(515,612),(520,626)],
        width=1.4,gaps=.035)
    wash(cat,'paw-shade',curve([(507,620),(517,629),(522,654),(516,674),
         (506,677),(512,654)],closed=True),(170,151,118),.18,offset=(1,1))
    pen(cat,'paw-outside',[(520,626),(524,646),(522,664),(515,676),(506,678)],
        width=1.45,gaps=.025,overdraw=1)
    pen(cat,'paw-inside',[(496,623),(497,638),(501,652)],
        width=1.0,gaps=.075)
    pen(cat,'paw-tip',[(500,663),(501,672),(506,677)],width=1.15,gaps=.025)
    pen(cat,'toe-a',[(509,670),(509,678)],width=.7,smooth=False,gaps=0)
    pen(cat,'toe-b',[(515,668),(515,675)],width=.65,smooth=False,gaps=0)
    pen(cat,'paw-stripe',[(506,625),(514,628)],soft=True,width=1.45,opacity=.44,
        smooth=False,gaps=.035)

    # Front folds are drawn around the foreleg, so no rear line runs through it.
    bag = scene.object('bag-front', '有宽折痕的软纸袋')
    wash(bag,'left-fold-color',curve([(368,624),(393,637),(423,686),(415,753),
         (437,814),(414,827),(401,779),(390,724)],closed=True),
         (189,155,104),.40,offset=(2,1))
    wash(bag,'right-fold-color',[(590,641),(624,621),(615,694),(611,767),
         (595,827),(578,830),(587,779),(581,743),(597,683)],
         (198,166,120),.28,offset=(-1,2))
    wash(bag,'bottom-fold-color',[(425,813),(475,824),(557,825),(593,816),
         (581,837),(487,840),(431,833)],(194,160,113),.28)
    pen(bag,'front-left-lip',[(365,617),(388,631),(411,615),(439,633),(474,623),(490,625)],
        width=1.2,smooth=False,gaps=.045)
    pen(bag,'front-right-lip',[(533,631),(558,640),(592,631),(625,617)],
        width=1.15,smooth=False,gaps=.045)
    pen(bag,'left-upper-side',[(364,624),(376,664),(388,709),(396,738)],
        width=1.2,gaps=.08)
    pen(bag,'left-lower-side',[(401,768),(408,796),(416,823),(433,831)],
        width=1.1,overdraw=1,gaps=.065)
    pen(bag,'right-side',[(625,629),(619,675),(620,714)],
        width=.85,opacity=.63,gaps=.11)
    pen(bag,'right-lower-side',[(611,766),(610,798),(591,833)],
        width=1.15,gaps=.055)
    pen(bag,'bottom',[(437,835),(473,839),(522,839),(558,842),(588,835)],
        width=1.1,gaps=.06)
    for name,pts in [
        ('fold-left',[(386,648),(423,690),(414,731)]),
        ('fold-middle',[(425,750),(443,777),(436,794)]),
        ('fold-bottom',[(419,824),(449,801),(466,809)]),
        ('fold-right',[(605,669),(581,713),(588,737)]),
    ]:
        pen(bag,name,pts,width=.75,soft=True,opacity=.55,smooth=False,gaps=.10)
    pen(bag,'fold-pressure',[(393,643),(410,667),(416,684)],
        width=.8,opacity=.59,smooth=False,gaps=.06)
    # Short hatching stays in the compressed, lower-left fold.
    for i in range(6):
        pen(bag,f'fold-hatch-{i}',[(413+i*3,799+i*2),(425+i*4,817+i*1.5)],
            width=.55,soft=True,opacity=.37,smooth=False,gaps=.12)

    cup = scene.object('tea-cup', '旁边的一小杯茶')
    wash(cup,'tea',ellipse(254,754,35,8,rotate=3,rough=.08,seed=9),
         (155,119,76),.70,offset=(0,1),edge=.18)
    wash(cup,'cool-side',curve([(278,763),(291,758),(286,804),(277,821),
         (264,824),(272,803)],closed=True),(154,180,167),.40,offset=(1,1))
    pen(cup,'rim-front',[(217,753),(228,765),(259,767),(287,760)],
        width=1.05,gaps=.05)
    pen(cup,'rim-back',[(218,751),(241,746),(265,747),(286,754)],
        width=.75,opacity=.75,gaps=.07)
    pen(cup,'left-wall',[(216,761),(220,796),(226,817)],
        width=1.0,gaps=.07)
    pen(cup,'bottom',[(228,822),(249,827),(271,824),(282,818)],
        width=1.0,gaps=.045)
    pen(cup,'right-wall',[(291,767),(289,793),(286,808)],
        width=.8,gaps=.08)
    pen(cup,'handle',[(290,768),(310,771),(312,791),(299,804),(289,802)],
        width=1.0,gaps=.05)
    pen(cup,'handle-inner',[(294,776),(302,779),(301,791),(292,796)],
        width=.7,opacity=.72,gaps=.10)
    pen(cup,'steam',[(249,728),(257,718),(251,705)],
        soft=True,width=.55,opacity=.29,gaps=.16)
    # Place the group on the page; retain the authored line weights at this scale.
    for obj in scene.data['objects']:
        for mark in obj['marks']:
            key = 'points' if mark['kind'] in ('ink','pencil') else 'polygon'
            mark[key] = transform(mark[key], scale=1.12, origin=(450,650), translate=(0,-65))
    if ink_only:
        for obj in scene.data['objects']:
            obj['marks'] = [m for m in obj['marks'] if m['kind'] in ('ink','pencil','hatch')]
        scene.data['objects'] = [o for o in scene.data['objects'] if o['marks']]
    return scene.data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT/'examples/studies/breakfast-cat-v2')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--ink-only', action='store_true', help='inspect pose and selective contours before adding pigment')
    args = parser.parse_args()
    result = render_to(build(args.ink_only), args.out, overwrite=args.overwrite)
    print(f"Rendered {args.out / 'artwork.png'}; warnings: {result['warnings']}")
