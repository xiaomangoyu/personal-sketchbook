#!/usr/bin/env python3
"""Rain just before closing: warm café, wet pavement and an editable umbrella.

Every shape is drawn with the actual personal-sketchbook scene renderer.
The umbrella and its pigment are isolated so the gallery can demonstrate editing.
"""
from pathlib import Path
import argparse
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scene_tools import Scene, ellipse, curve, bezier
from render import render_to

INK = (46, 61, 62)


def build_scene():
    s = Scene('雨停前的街角咖啡店', 1400, 1000, seed=71013,
              paper=(248, 245, 230), grain=.53)
    sky = s.object('rainy-atmosphere', '雨天的空气')
    sky.fill('sky', curve([(80, 235), (275, 110), (703, 103), (1025, 185),
                          (1290, 387), (1210, 685), (700, 713), (128, 636)], closed=True),
             (121, 152, 153), opacity=.23, bleed=12, edge=.05, grain=.58)
    sky.fill('far-building', [(933, 239), (1075, 221), (1086, 650), (922, 659)],
             (137, 153, 148), opacity=.28, edge=.08, bleed=3)
    for i, y in enumerate([280, 352, 435, 508]):
        sky.line(f'distant-window-{i}', [(968, y+40), (966, y), (1002, y-2), (1004, y+37)],
                 (114, 131, 129), width=1.9, opacity=.26, wobble=.55)

    road = s.object('wet-street', '雨后路面')
    road.fill('ground', curve([(74, 640), (349, 610), (920, 610), (1300, 700),
                              (1344, 874), (1078, 929), (435, 914), (76, 810)], closed=True),
              (121, 147, 143), opacity=.29, bleed=9, edge=.1, grain=.6)
    road.fill('shadow-under-shop', [(174, 654), (927, 625), (1185, 718), (670, 751), (151, 696)],
              (55, 78, 76), opacity=.31, bleed=5, edge=.12)
    road.line('curb', [(68, 732), (397, 717), (747, 703), (1194, 765)],
              INK, opacity=.45, width=2.6, wobble=1.0)
    road.line('curb-depth', [(123, 742), (449, 729), (742, 715), (1174, 775)],
              INK, opacity=.32, width=1.7, wobble=.7)
    for i, (x, y, w) in enumerate([(234, 820, 147), (471, 860, 180), (766, 813, 144),
                                  (1072, 877, 164), (961, 937, 84), (295, 754, 103)]):
        road.line(f'puddle-{i}', curve([(x-w/2, y), (x-15, y-3), (x+w/2, y+1)]),
                  (81, 112, 118), opacity=.4, width=2.2, wobble=.7)

    wall = s.object('cafe-building', '街角咖啡店')
    wall.fill('front-plaster', [(217, 209), (828, 174), (831, 642), (207, 667)],
              (201, 151, 91), opacity=.55, edge=.2, bleed=2.2, grain=.6)
    wall.fill('side-plaster', [(828, 174), (953, 248), (951, 624), (831, 642)],
              (128, 139, 125), opacity=.7, edge=.23, bleed=2)
    wall.fill('base-front', [(207, 607), (831, 583), (831, 642), (207, 668)],
              (101, 119, 106), opacity=.83, bleed=1.3, edge=.2)
    wall.hatch('side-shadow-hatch', [(845, 370), (951, 423), (951, 624), (845, 640)],
               (87, 96, 85), opacity=.25, spacing=10, angle=68)
    wall.line('left-edge', [(217, 211), (208, 668)], INK, width=2.8, opacity=.74, wobble=.65)
    wall.line('corner', [(828, 172), (832, 642), (948, 625)], INK, width=3.5, opacity=.8)
    wall.line('side-top', [(828, 174), (952, 248), (952, 411)], INK, width=2.3, opacity=.66)
    wall.line('foundation', [(197, 669), (832, 643), (958, 627)], INK, width=3.0, opacity=.66)
    # Selected broken plaster, and bricks close to the damp foundation.
    for i, pts in enumerate([[(247, 255), (245, 274), (253, 284)], [(745, 275), (764, 272), (776, 281)],
                              [(873, 291), (881, 334), (894, 349)], [(227, 577), (246, 577), (255, 588)]]):
        wall.line(f'plaster-crack-{i}', pts, (131, 119, 95), width=1.1, opacity=.42)
    for i in range(5):
        x = 250 + i*36
        wall.line(f'base-brick-{i}', [(x, 635), (x+27, 634), (x+27, 645)],
                  (87, 102, 92), width=1.1, opacity=.45)

    interior = s.object('warm-windows', '暖灯和玻璃窗')
    window = [(261, 326), (564, 313), (565, 570), (257, 583)]
    interior.fill('window-dark', window, (57, 83, 77), opacity=.94, bleed=.6, edge=.12)
    interior.fill('window-light-left', [(276, 336), (395, 332), (395, 557), (273, 562)],
                  (234, 178, 82), opacity=.94, edge=.16, bleed=2)
    interior.fill('window-light-right', [(412, 331), (548, 325), (549, 551), (412, 556)],
                  (244, 197, 109), opacity=.92, edge=.14, bleed=2)
    interior.fill('window-bottom-shadow', [(273, 490), (550, 480), (550, 552), (273, 565)],
                  (128, 99, 64), opacity=.62, edge=.1, bleed=2)
    for i, (x, y) in enumerate([(333, 385), (472, 377)]):
        interior.line(f'lamp-cord-{i}', [(x, 332), (x, y-21)], INK, width=1.8, opacity=.8)
        shade = curve([(x-25, y), (x-12, y-20), (x+9, y-20), (x+29, y), (x, y+7)], closed=True)
        interior.fill(f'lamp-shade-{i}', shade, (227, 124, 60), opacity=.88, bleed=.8, edge=.1)
        interior.line(f'lamp-edge-{i}', curve([(x-25, y), (x, y+7), (x+29, y)]),
                      (102, 86, 55), width=1.4, opacity=.7)
    # Interior shelf, cups and one crooked book.
    interior.line('shelf', [(278, 488), (548, 478)], (74, 77, 59), width=5, opacity=.85)
    for i, (x, y) in enumerate([(299, 469), (331, 469), (461, 460), (502, 459)]):
        interior.fill(f'cup-{i}', [(x, y), (x+19, y-1), (x+17, y+15), (x+3, y+16)],
                      (246, 226, 173), opacity=.9, bleed=.4, edge=.1)
        interior.line(f'cup-handle-{i}', curve([(x+18, y+2), (x+26, y+2), (x+25, y+9), (x+19, y+11)]),
                      (100, 89, 59), width=1.3, opacity=.7)
    interior.fill('book-spine', [(366, 458), (376, 456), (382, 481), (371, 482)],
                  (164, 75, 44), opacity=.78, bleed=.7, edge=.1)
    interior.line('window-border', window + [window[0]], INK, width=3.2, opacity=.86)
    interior.line('window-mullion', [(404, 321), (404, 570)], INK, width=5.0, opacity=.88)
    interior.line('window-horizontal-bar', [(260, 419), (562, 407)], INK, width=3.8, opacity=.85)
    interior.line('glass-reflection-a', [(290, 352), (309, 400)], (249, 238, 204), width=3, opacity=.5)
    interior.line('glass-reflection-b', [(304, 347), (319, 382)], (249, 238, 204), width=1.8, opacity=.5)
    interior.line('sill', [(245, 584), (580, 570)], INK, width=5.5, opacity=.75)

    door = s.object('door', '绿色木门')
    door.fill('door-frame', [(622, 313), (779, 307), (783, 636), (619, 643)],
              (51, 84, 72), opacity=.9, bleed=1, edge=.1)
    door.fill('door-glass', [(640, 333), (760, 329), (762, 514), (638, 519)],
              (227, 175, 89), opacity=.9, bleed=1, edge=.17)
    door.fill('inside-shadow', [(729, 330), (760, 329), (762, 513), (727, 515)],
              (100, 105, 72), opacity=.72, edge=.1, bleed=1.5)
    door.line('door-outline', [(622, 314), (620, 644), (783, 636), (779, 307), (622, 314)],
              INK, width=2.8, opacity=.89)
    door.line('glass-midbar', [(639, 422), (759, 416)], INK, width=2.8, opacity=.82)
    door.line('door-lower-panel', [(639, 547), (762, 542), (764, 609), (638, 615), (639, 547)],
              (41, 64, 54), width=2, opacity=.77)
    door.line('brass-handle', [(751, 520), (750, 541)], (235, 183, 87), width=4.0, opacity=.92)
    door.line('step', [(605, 648), (787, 640), (800, 652), (599, 662)], INK, width=2.6, opacity=.8)

    canopy = s.object('awning', '褪色陶红遮雨篷')
    canopy.fill('upper-fascia', [(194, 207), (833, 174), (845, 215), (186, 251)],
                (121, 75, 49), opacity=.75, bleed=1, edge=.18)
    shape = [(207, 247), (836, 211), (889, 298), (169, 337)]
    canopy.fill('canopy-red', shape, (172, 69, 44), opacity=.88, bleed=2.2, edge=.23)
    for i in range(6):
        x = 230+i*100
        canopy.fill(f'faded-stripe-{i}', [(x, 246-i*5.5), (x+27, 244-i*5.5),
                    (x+38, 329-i*5.5), (x+4, 332-i*5.5)], (234, 164, 119),
                    opacity=.65, edge=.07, bleed=.9)
    canopy.fill('valance', [(170, 332), (889, 295), (887, 323), (165, 362)],
                (144, 53, 39), opacity=.91, bleed=.8, edge=.2)
    canopy.line('awning-top', [(201, 246), (836, 211), (888, 297), (169, 336), (201, 246)],
                INK, width=2.8, opacity=.79)
    canopy.line('valance-bottom', [(166, 361), (887, 324)], INK, width=3.3, opacity=.73)
    for i in range(5):
        x = 291+i*108
        canopy.line(f'seam-{i}', [(x, 241-i*6), (x+2, 329-i*6)],
                    (110, 60, 44), width=1.1, opacity=.43)

    sign = s.object('coffee-sign', '吊牌上的杯子')
    sign.line('sign-bracket', [(946, 295), (1030, 319), (1031, 361)], INK, width=4, opacity=.8)
    sign.line('chain-a', [(982, 319), (982, 361)], INK, width=1.7, opacity=.76)
    sign.line('chain-b', [(1026, 332), (1026, 370)], INK, width=1.5, opacity=.7)
    sign.fill('sign-board', [(968, 354), (1045, 375), (1047, 451), (968, 429)],
              (44, 77, 72), opacity=.9, edge=.15, bleed=.8)
    sign.line('sign-board-edge', [(968, 354), (1045, 375), (1047, 451), (968, 429), (968, 354)],
              INK, width=2.0, opacity=.81)
    sign.line('cup-symbol', curve([(982, 390), (987, 416), (1001, 424), (1015, 422), (1020, 398)]),
              (242, 216, 161), width=2.3, opacity=.95)
    sign.line('cup-symbol-rim', [(982, 390), (1020, 398)], (242, 216, 161), width=2.2, opacity=.95)
    sign.line('cup-symbol-handle', curve([(1020, 400), (1032, 404), (1031, 415), (1018, 416)]),
              (242, 216, 161), width=2, opacity=.95)
    sign.line('steam', curve([(1001, 391), (998, 383), (1001, 377)]),
              (242, 216, 161), width=1.6, opacity=.8)

    plant = s.object('rosemary-pot', '门口的迷迭香')
    plant.value['translate'] = [0, 23]
    plant.fill('pot', [(825, 558), (878, 555), (870, 617), (834, 619)],
               (173, 96, 63), opacity=.85, edge=.22, bleed=1.2)
    plant.line('pot-contour', [(825, 559), (834, 619), (870, 617), (878, 555)],
               INK, width=2, opacity=.68)
    plant.line('pot-lip', ellipse(851, 556, 28, 7), INK, width=2.1, opacity=.69)
    rng = random.Random(442)
    for i in range(20):
        tip = (rng.uniform(806, 897), rng.uniform(464, 540))
        plant.line(f'stem-{i}', curve([(853, 555), ((853+tip[0])/2, 526), tip]),
                   (77, 98, 64), width=1.3, opacity=.78)
        for j in range(3):
            t = .35+j*.2
            x, y = 853+(tip[0]-853)*t, 555+(tip[1]-555)*t
            plant.line(f'leaf-{i}-{j}', [(x-9, y-7), (x, y), (x+8, y-11)],
                       (89, 110, 64), width=3.5, opacity=.6)

    chair = s.object('outside-stool', '没有收进去的小圆凳')
    chair.fill('stool-seat', ellipse(326, 644, 48, 12, rotate=-3),
               (143, 97, 51), opacity=.82, edge=.17, bleed=.7)
    chair.line('seat-rim', ellipse(326, 644, 48, 12, rotate=-3), INK, width=2.4, opacity=.8)
    for i, points in enumerate([[(296, 650), (285, 704)], [(352, 650), (364, 700)],
                                [(316, 654), (315, 690)], [(292, 678), (357, 675)]]):
        chair.line(f'stool-leg-{i}', points, INK, width=3, opacity=.75)
    chair.fill('cup-body', [(314, 621), (340, 620), (337, 638), (317, 639)],
               (242, 224, 182), opacity=.95, edge=.13, bleed=.4)
    chair.line('cup-outline', [(314, 621), (317, 639), (337, 638), (340, 620), (314, 621)],
               INK, width=1.4, opacity=.85)
    chair.line('cup-handle', curve([(340, 623), (349, 624), (349, 630), (339, 633)]),
               INK, width=1.3, opacity=.75)

    reflection = s.object('window-reflections', '暖光在路面上碎开')
    rng = random.Random(897)
    for i in range(19):
        y = 740+i*6.3
        x = 363 + rng.uniform(-22, 29)
        w = rng.uniform(35, 106)*(1-i*.02)
        reflection.fill(f'light-water-{i}', [(x-w, y), (x+w, y-3), (x+w+5, y+3), (x-w-4, y+5)],
                        (221, 161, 67), opacity=.19+.24*(1-i/19), edge=.04, bleed=1.5)
    for i in range(10):
        y = 720+i*8
        reflection.line(f'door-light-{i}', [(690-i*.5, y), (741-i*2.1, y-1)],
                        (221, 177, 88), width=4.6, opacity=.42-i*.02, wobble=1.1)

    person = s.object('waiting-person', '伞下等雨停的人')
    person.fill('person-shadow', ellipse(1064, 825, 64, 12), (50, 72, 75), opacity=.35, bleed=4, edge=.06)
    person.fill('coat', curve([(1029, 633), (1080, 629), (1092, 670), (1088, 739),
                             (1024, 742), (1014, 690)], closed=True),
                (176, 119, 60), opacity=.88, bleed=1.2, edge=.2)
    person.fill('far-leg', [(1060, 732), (1085, 731), (1084, 795), (1067, 799)],
                (56, 69, 68), opacity=.94, bleed=.6, edge=.1)
    person.fill('near-leg', [(1030, 733), (1055, 734), (1047, 809), (1029, 809)],
                (54, 64, 68), opacity=.9, bleed=.6, edge=.12)
    person.line('left-shoe', curve([(1046, 809), (1024, 815), (1015, 814)]),
                INK, width=9, opacity=.9)
    person.line('right-shoe', curve([(1068, 800), (1088, 802), (1094, 809)]),
                INK, width=8.5, opacity=.9)
    person.line('coat-right', curve([(1081, 646), (1090, 689), (1088, 739), (1027, 742)]),
                INK, width=2.5, opacity=.74)
    person.line('elbow-fold', curve([(1030, 679), (1048, 693), (1061, 664)]),
                (87, 80, 60), width=2.1, opacity=.72)
    person.fill('hand', ellipse(1063, 660, 7, 10, rotate=15), (191, 143, 104), opacity=.95, bleed=.5, edge=.1)

    umbrella = s.object('umbrella', '可单独改色的雨伞')
    canopy_outline = curve([(910, 613), (938, 559), (1000, 521), (1048, 513),
                            (1105, 532), (1167, 581), (1200, 639), (1146, 619),
                            (1094, 632), (1046, 616), (1000, 629), (953, 607)], closed=True)
    umbrella.fill('canopy-base-color', canopy_outline, (194, 74, 54), opacity=.93,
                  bleed=1.5, edge=.2, grain=.58)
    umbrella.fill('canopy-left-panel-color', curve([(910, 613), (938, 559), (1000, 521),
                   (1048, 513), (1000, 567), (1000, 629), (953, 607)], closed=True),
                  (224, 113, 76), opacity=.64, bleed=.8, edge=.12)
    umbrella.fill('canopy-right-panel-color', curve([(1048, 513), (1105, 532), (1167, 581),
                   (1200, 639), (1146, 619), (1094, 632), (1085, 573)], closed=True),
                  (133, 54, 53), opacity=.48, bleed=.8, edge=.1)
    umbrella.line('canopy-outline', canopy_outline, INK, width=2.7, opacity=.83)
    umbrella.line('rib-left', curve([(1048, 515), (1013, 546), (1000, 582), (1000, 629)]),
                  INK, width=1.7, opacity=.62)
    umbrella.line('rib-right', curve([(1048, 515), (1072, 542), (1088, 585), (1094, 632)]),
                  INK, width=1.6, opacity=.6)
    umbrella.line('rib-edge', curve([(1048, 515), (1112, 555), (1146, 619)]),
                  INK, width=1.1, opacity=.35)
    umbrella.line('stem', [(1048, 500), (1049, 514)], INK, width=2.8, opacity=.84)
    umbrella.line('shaft', [(1057, 621), (1062, 691)], INK, width=2.8, opacity=.8)
    umbrella.line('hook', curve([(1062, 687), (1062, 708), (1053, 713), (1047, 705)]),
                  INK, width=3.2, opacity=.83)

    branches = s.object('rain-tree', '伸进画面的枝叶')
    branches.line('branch-main', curve([(73, 136), (135, 179), (190, 205), (258, 214)]),
                  (79, 86, 67), width=5.3, opacity=.63, wobble=.85)
    branches.line('branch-a', curve([(147, 185), (164, 145), (215, 117)]),
                  (79, 86, 67), width=2.8, opacity=.64)
    branches.line('branch-b', curve([(188, 204), (216, 244), (253, 260)]),
                  (79, 86, 67), width=2.3, opacity=.54)
    rng = random.Random(631)
    for i, (x, y, rot) in enumerate([(112, 163, -20), (143, 182, 25), (173, 159, -38), (188, 137, 35),
                                    (216, 126, -40), (207, 213, 24), (239, 215, -20), (222, 242, -32),
                                    (250, 259, 26), (89, 146, 30)]):
        branches.fill(f'leaf-{i}', ellipse(x, y, rng.uniform(14, 21), 7, rotate=rot, rough=.09, seed=i),
                      (91, 114, 68), opacity=.54+rng.random()*.15, bleed=1.5, edge=.15)

    rain = s.object('last-rain', '最后几滴雨')
    for i, (x, y, length) in enumerate([(137, 356, 29), (119, 471, 33), (187, 422, 22),
                 (1102, 284, 38), (1203, 376, 32), (1174, 489, 26), (1260, 613, 32),
                 (1097, 428, 25), (979, 164, 23), (548, 93, 19), (1260, 263, 23)]):
        rain.line(f'rain-{i}', [(x, y), (x-8, y+length)], (100, 132, 144), width=1.4, opacity=.35)
    for i, (x, y) in enumerate([(912, 797), (1188, 834), (494, 786), (830, 886)]):
        rain.line(f'ripple-{i}', ellipse(x, y, 18+i*3, 3.5, start=20, end=320),
                  (96, 126, 129), width=1.3, opacity=.46)
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'examples/gallery/rainy-cafe')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    result = render_to(build_scene().data, args.out, args.overwrite)
    print(args.out / 'artwork.png')
    print('Warnings:', result['warnings'])


if __name__ == '__main__':
    main()
