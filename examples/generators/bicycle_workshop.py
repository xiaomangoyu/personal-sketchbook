#!/usr/bin/env python3
"""A bicycle in the last warm light of a small repair shop.

The two axles, bottom bracket, seat tube and steering axis are connected
explicitly. Spokes and hatching are intentional geometry, not image overlays.
"""
from pathlib import Path
import argparse
import math
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scene_tools import Scene, ellipse, curve, transform
from render import render_to

INK = (61, 60, 51)


def build_scene():
    s = Scene('修车铺午后的最后一束光', 1400, 1100, seed=18301,
              paper=(249, 245, 230), grain=.54)
    backdrop = s.object('workshop-walls', '旧修车铺的墙和地面')
    backdrop.fill('wall-wash', [(90, 140), (1214, 101), (1306, 714), (136, 748)],
                  (176, 154, 114), opacity=.24, edge=.04, bleed=10, grain=.65)
    backdrop.fill('right-wall-shadow', [(856, 109), (1249, 116), (1281, 730), (1157, 712)],
                  (111, 117, 97), opacity=.23, edge=.06, bleed=10)
    backdrop.fill('floor-wash', curve([(136, 747), (558, 693), (1210, 711), (1345, 982),
                  (1169, 1050), (258, 1054), (62, 965)], closed=True),
                  (151, 141, 109), opacity=.24, edge=.06, bleed=9)
    backdrop.line('wall-base', [(115, 742), (727, 718), (1272, 737)],
                  (111, 109, 87), width=2, opacity=.4, wobble=.8)
    for i, (a, b) in enumerate([((176, 994), (547, 731)), ((572, 1038), (723, 727)),
                                ((1004, 1061), (1008, 729)), ((1235, 1001), (1139, 731))]):
        backdrop.line(f'floor-board-{i}', [a, b], (134, 124, 95), width=1.3, opacity=.35, wobble=.7)

    light = s.object('late-sunlight', '斜照进来的最后一束光')
    light.fill('light-band', [(183, 147), (371, 132), (1288, 967), (1070, 1025)],
               (234, 185, 82), opacity=.28, edge=.03, bleed=7, grain=.25)
    light.fill('light-center', [(224, 163), (333, 154), (1247, 978), (1148, 1001)],
               (255, 212, 115), opacity=.19, edge=.02, bleed=11)

    window = s.object('high-window', '高窗')
    outer = [(101, 150), (361, 139), (364, 345), (104, 356)]
    window.fill('recess', outer, (119, 112, 88), opacity=.65, edge=.1, bleed=1)
    for i, (x0, x1) in enumerate([(116, 220), (237, 349)]):
        window.fill(f'glass-{i}', [(x0, 161), (x1, 156), (x1, 334), (x0, 338)],
                    (248, 225, 160), opacity=.98, edge=.05, bleed=2)
    window.line('window-edge', outer + [outer[0]], INK, width=2.8, opacity=.62)
    window.line('mullion', [(228, 144), (229, 345)], (89, 84, 66), width=5.2, opacity=.72)
    window.line('crossbar', [(106, 249), (362, 239)], (89, 84, 66), width=4.2, opacity=.71)
    window.line('sill', [(92, 358), (373, 345)], INK, width=4.5, opacity=.63)

    board = s.object('tool-board', '挂着常用工具的木板')
    board.fill('tool-board-color', [(473, 182), (1106, 164), (1119, 391), (479, 412)],
               (173, 134, 80), opacity=.43, edge=.13, bleed=1.4)
    board.line('board-top', [(472, 183), (1106, 164), (1119, 391)],
               (108, 94, 69), width=2.3, opacity=.55)
    board.line('board-bottom', [(479, 412), (1119, 391)], (108, 94, 69), width=2, opacity=.5)
    board.hatch('board-right-shadow', [(1076, 169), (1106, 164), (1119, 391), (1080, 393)],
                (106, 94, 71), opacity=.22, spacing=8, angle=78)
    for i in range(4):
        y = 228+i*44
        board.line(f'board-grain-{i}', curve([(495, y), (665, y-7), (919, y-12), (1092, y-18)]),
                   (132, 105, 68), width=1.0, opacity=.22, wobble=1.1)
    # Each hole belongs to a modest repeat, with omissions near worn edges.
    for row in range(4):
        for col in range(12):
            if (row*7+col*3) % 9 == 0:
                continue
            x, y = 502+col*49, 217+row*49-col*1.7
            board.line(f'hole-{row}-{col}', [(x, y), (x+1, y+1)],
                       (102, 89, 64), width=2.2, opacity=.4, gaps=0)

    tools = s.object('hanging-tools', '扳手、钳子和手锯')
    def wrench(tag, x, y, length, rotate=0):
        shape = [(x-8, y+18), (x-19, y+5), (x-19, y-12), (x-8, y-21),
                 (x-9, y-3), (x+4, y+4), (x+14, y-6), (x+8, y-24),
                 (x+23, y-16), (x+24, y+2), (x+9, y+20),
                 (x+8, y+length), (x-9, y+length)]
        shape = transform(shape, rotate=rotate, origin=(x, y))
        tools.fill(tag+'-metal', shape, (110, 118, 104), opacity=.69, edge=.12, bleed=.6)
        tools.line(tag+'-edge', shape+[shape[0]], INK, width=1.6, opacity=.82)
        hole = transform(ellipse(x, y+length-10, 3.5, 5), rotate=rotate, origin=(x,y))
        tools.line(tag+'-hole', hole, INK, width=1.2, opacity=.85)
    wrench('large-spanner', 559, 233, 136, -8)
    wrench('small-spanner', 639, 233, 97, 5)
    # Pliers: two jaws meet at an actual pivot; wooden handles splay below.
    tools.line('pliers-left-jaw', [(730, 231), (737, 257), (765, 299)],
               (89, 97, 90), width=8, opacity=.91)
    tools.line('pliers-right-jaw', [(754, 230), (748, 256), (722, 303)],
               (91, 99, 91), width=8, opacity=.91)
    tools.line('pliers-left-handle', curve([(759, 290), (774, 318), (772, 344)]),
               (153, 74, 45), width=10, opacity=.82)
    tools.line('pliers-right-handle', curve([(728, 292), (713, 317), (713, 340)]),
               (153, 74, 45), width=10, opacity=.82)
    tools.line('pliers-pivot', ellipse(742, 263, 5, 5), INK, width=2, opacity=.9)
    # Screwdriver profile has a dark narrow shaft and a worn ochre grip.
    tools.line('screwdriver-shaft', [(839, 227), (837, 294)], INK, width=3.4, opacity=.8)
    tools.fill('screwdriver-grip', curve([(832, 289), (845, 289), (849, 320),
               (845, 347), (832, 349), (828, 320)], closed=True),
               (179, 118, 53), opacity=.83, edge=.18, bleed=.8)
    tools.line('grip-groove-a', [(835, 298), (834, 338)], (114, 81, 46), width=1.5, opacity=.56)
    tools.line('grip-groove-b', [(842, 297), (843, 337)], (114, 81, 46), width=1.5, opacity=.56)
    # A small hacksaw with the blade tensioned between frame ends.
    tools.line('saw-frame', curve([(920, 335), (920, 244), (1017, 239), (1044, 256), (1045, 331)]),
               (81, 102, 88), width=6, opacity=.85)
    tools.line('saw-blade', [(920, 333), (1047, 329)], (70, 76, 70), width=2.2, opacity=.87)
    tools.line('saw-handle', [(1046, 329), (1067, 353)], (146, 79, 49), width=12, opacity=.88)
    for i in range(24):
        x = 925+i*4.8
        tools.line(f'saw-tooth-{i}', [(x, 333), (x+1.5, 336)], INK, width=.75, opacity=.6)

    bench = s.object('wooden-workbench', '磨旧的修车工作台')
    bench.fill('top', [(119, 439), (1199, 410), (1274, 456), (152, 496)],
               (145, 99, 57), opacity=.77, edge=.2, bleed=1.5)
    bench.fill('front', [(152, 496), (1274, 456), (1272, 563), (157, 602)],
               (120, 91, 58), opacity=.8, edge=.17, bleed=1.2)
    bench.fill('front-lit', [(213, 493), (692, 476), (800, 579), (222, 601)],
               (204, 155, 81), opacity=.45, edge=.1, bleed=2)
    bench.fill('left-leg', [(194, 598), (232, 597), (218, 892), (183, 900)],
               (104, 85, 60), opacity=.8, edge=.1, bleed=1)
    bench.fill('right-leg', [(1193, 567), (1229, 567), (1246, 841), (1218, 847)],
               (100, 82, 59), opacity=.87, edge=.1, bleed=1)
    bench.line('table-edge', [(118, 439), (151, 496), (1275, 456), (1200, 410)],
               INK, width=3.8, opacity=.73)
    bench.line('table-front-bottom', [(157, 603), (1272, 564)], INK, width=3.3, opacity=.71)
    bench.hatch('under-top-dark', [(153, 498), (1273, 459), (1273, 477), (154, 518)],
                INK, opacity=.52, spacing=5, angle=74, width=1.1)
    bench.hatch('right-drawer-shadow', [(1111, 477), (1272, 475), (1272, 562), (1194, 566)],
                (72, 68, 50), opacity=.26, spacing=8, angle=65, width=.9)
    bench.hatch('right-leg-shadow', [(1222, 568), (1229, 568), (1246, 841), (1230, 843)],
                (73, 70, 53), opacity=.38, spacing=6, angle=35, width=1)
    for i, (x0, x1) in enumerate([(270, 529), (568, 852), (895, 1192)]):
        y = 527-(x0-270)*.035
        bench.line(f'drawer-{i}', [(x0, y), (x1, y-9), (x1, y+42), (x0, y+50), (x0, y)],
                   (75, 67, 49), width=1.6, opacity=.74)
        bench.line(f'drawer-pull-{i}', curve([((x0+x1)/2-20, y+20), ((x0+x1)/2, y+24),
                   ((x0+x1)/2+20, y+19)]), (47, 53, 48), width=3.2, opacity=.83)
    for i in range(6):
        x = 174+i*150
        bench.line(f'wood-scratch-{i}', curve([(x, 477-i*3), (x+30, 474-i*3), (x+88, 474-i*3)]),
                   (197, 157, 98), width=1.5, opacity=.6)

    still = s.object('bench-objects', '油壶、旧杯和一块布')
    # Oil can with a long spout, handle and pump cap.
    still.fill('oil-can-body', [(331, 415), (339, 365), (387, 363), (396, 412)],
               (151, 67, 42), opacity=.88, edge=.2, bleed=1)
    still.line('oil-can-edge', [(331, 415), (339, 365), (387, 363), (396, 412), (331, 415)],
               INK, width=1.8, opacity=.8)
    still.line('oil-can-spout', curve([(384, 368), (414, 343), (444, 339)]),
               (82, 91, 81), width=4.2, opacity=.85)
    still.line('oil-can-handle', curve([(337, 374), (313, 377), (313, 400), (334, 404)]),
               INK, width=3, opacity=.74)
    still.line('oil-pump', [(359, 365), (359, 351), (373, 351)], INK, width=2.2, opacity=.8)
    # The can rests on the worktop; move its complete drawing before adding mugs.
    for mark in still.value['marks']:
        key = 'points' if mark['kind'] in ('ink', 'pencil') else 'polygon'
        mark[key] = transform(mark[key], translate=(0, 38))
    still.fill('mug', [(1125, 401), (1168, 399), (1165, 442), (1130, 444)],
               (198, 190, 148), opacity=.84, edge=.19, bleed=.7)
    still.line('mug-rim', ellipse(1146, 400, 22, 5), INK, width=1.7, opacity=.8)
    still.line('mug-edge', [(1125, 402), (1130, 444), (1165, 442), (1168, 400)],
               INK, width=1.8, opacity=.8)
    still.line('mug-handle', curve([(1169, 410), (1182, 411), (1183, 427), (1166, 431)]),
               INK, width=2, opacity=.82)
    rag = curve([(736, 426), (793, 411), (826, 426), (888, 428), (867, 445),
                  (819, 448), (802, 464), (753, 449)], closed=True)
    still.fill('rag', rag, (88, 131, 141), opacity=.53, edge=.11, bleed=2)
    for i, pts in enumerate([[(741, 430), (771, 440), (802, 435)], [(790, 416), (804, 430), (825, 435)],
                              [(812, 447), (844, 437), (868, 437)]]):
        still.line(f'rag-fold-{i}', curve(pts), (64, 89, 90), width=1.5, opacity=.57)

    shade = s.object('bicycle-ground-shadow', '自行车在地上的投影')
    shade.fill('bike-shadow', curve([(157, 1005), (406, 979), (1039, 972),
               (1319, 1012), (1177, 1041), (443, 1048)], closed=True),
               (73, 90, 84), opacity=.28, edge=.03, bleed=6)
    shade.line('cast-frame-line', [(593, 997), (855, 1027), (1053, 1009)],
               (110, 101, 72), width=6, opacity=.19, wobble=1.1)

    # Wheel centers, fixed contact height and spoke attachment geometry.
    rear, front, radius = (365, 785), (1045, 785), 228
    wheels = s.object('bicycle-wheels', '两只轮胎、轮辋和交叉辐条')
    for name, (cx, cy) in [('rear', rear), ('front', front)]:
        wheels.line(name+'-tire', ellipse(cx, cy, radius, radius, rough=.004, seed=51),
                    (54, 63, 60), width=15, opacity=.91, pressure=.8, gaps=0, closed=True)
        wheels.line(name+'-rim', ellipse(cx, cy, radius-14, radius-14),
                    (112, 117, 102), width=3.5, opacity=.8, gaps=.005, closed=True)
        wheels.line(name+'-rim-highlight', ellipse(cx, cy, radius-17, radius-17, start=193, end=310),
                    (235, 215, 162), width=2.6, opacity=.7, gaps=.01)
        # Crossed spokes, with paired offsets at the hub rather than a starburst.
        for i in range(28):
            a = 2*math.pi*i/28
            b = a + (1.04 if i % 2 else -1.04)
            p = (cx+13*math.cos(a), cy+13*math.sin(a))
            q = (cx+(radius-15)*math.cos(b), cy+(radius-15)*math.sin(b))
            wheels.line(f'{name}-spoke-{i}', [p, q], (82, 95, 88),
                        width=.9, opacity=.58 if i % 3 else .73, wobble=.17, gaps=0)
        wheels.line(name+'-hub', ellipse(cx, cy, 15, 15), INK, width=3.2, opacity=.9, gaps=0)
        wheels.fill(name+'-axle', ellipse(cx, cy, 5, 5), (52, 61, 55), opacity=.95, bleed=.1, edge=0)
        wheels.line(name+'-valve', [(cx+154, cy+148), (cx+143, cy+137)],
                    INK, width=2.0, opacity=.8, gaps=0)

    frame = s.object('bicycle-frame', '暗红色钻石车架')
    seat = (575, 540)
    bracket = (642, 794)
    head_top, head_bottom = (900, 516), (924, 585)
    # Tube bodies are thick hand-ink strokes with a narrow reflected warm edge.
    tubes = [('top-tube', seat, head_top, 15), ('seat-tube', seat, bracket, 16),
             ('down-tube', head_bottom, bracket, 18), ('seat-stay', seat, rear, 9),
             ('chain-stay', rear, bracket, 9), ('head-tube', head_top, head_bottom, 19)]
    for name, a, b, width in tubes:
        frame.line(name+'-edge', [a, b], (70, 54, 41), width=width+3, opacity=.87, pressure=.75, gaps=0, wobble=.38)
        frame.line(name+'-paint', [a, b], (166, 68, 39), width=width, opacity=.94, pressure=.74, gaps=0, wobble=.35)
        frame.line(name+'-highlight', [(a[0]-2, a[1]-2), (b[0]-2, b[1]-2)],
                   (225, 157, 88), width=2.3, opacity=.72, pressure=.6, gaps=.02, wobble=.2)
    frame.line('fork-left', curve([(923, 581), (950, 675), (998, 755), front]),
               (70, 58, 44), width=10, opacity=.9, gaps=0)
    frame.line('fork-paint', curve([(923, 581), (950, 675), (998, 755), front]),
               (155, 61, 36), width=7, opacity=.88, gaps=0)
    frame.line('fork-far', curve([(914, 583), (944, 682), (990, 759), (1044, 786)]),
               (83, 78, 60), width=3.1, opacity=.73, gaps=.01)
    frame.line('seat-post', [(575, 543), (562, 491)], (102, 113, 106), width=7, opacity=.93, gaps=0)
    frame.line('seat-clamp', [(564, 537), (584, 533)], INK, width=4.2, opacity=.92)
    frame.line('head-collar-top', [(890, 516), (911, 508)], (82, 93, 86), width=5.0, opacity=.93)
    frame.line('head-collar-bottom', [(914, 588), (936, 580)], (82, 93, 86), width=4.7, opacity=.94)
    # Small braze-ons are visibly attached to their tubes.
    frame.line('down-tube-bottle-mount-a', [(817, 665), (824, 670)], INK, width=2.8, opacity=.81)
    frame.line('down-tube-bottle-mount-b', [(778, 695), (785, 700)], INK, width=2.8, opacity=.81)

    drive = s.object('chain-and-pedals', '链条、牙盘和踏板')
    chainring = (642, 794)
    # A slightly elongated rear cog and tangent chain runs.
    drive.line('rear-cog', ellipse(365, 785, 28, 28), (81, 85, 75), width=5, opacity=.86, gaps=0)
    drive.line('chain-top', [(365, 756), (642, 739)], (65, 72, 61), width=3.0, opacity=.87, gaps=0)
    drive.line('chain-bottom', [(365, 814), (642, 849)], (65, 72, 61), width=3.0, opacity=.88, gaps=0)
    drive.line('chainring-edge', ellipse(*chainring, 55, 55), (72, 80, 69), width=5, opacity=.9, gaps=0)
    drive.line('chainring-inner', ellipse(*chainring, 40, 40), (112, 119, 102), width=2.5, opacity=.84, gaps=0)
    for i in range(5):
        a = i*2*math.pi/5+.3
        drive.line(f'chainring-arm-{i}', [(642, 794), (642+38*math.cos(a), 794+38*math.sin(a))],
                   (107, 113, 99), width=7, opacity=.86, gaps=0)
    for i in range(34):
        a = i*2*math.pi/34
        drive.line(f'chainring-tooth-{i}', [(642+54*math.cos(a), 794+54*math.sin(a)),
                   (642+59*math.cos(a), 794+59*math.sin(a))], INK, width=1.9, opacity=.83, gaps=0)
    for i in range(30):
        t = i/30
        x = 365+(642-365)*t
        drive.line(f'chain-link-top-{i}', [(x, 756-17*t-1), (x+4, 756-17*t+2)],
                   (160, 155, 121), width=1.7, opacity=.74, gaps=0)
    drive.line('far-crank', [(642, 794), (682, 745)], (85, 91, 79), width=7, opacity=.7, gaps=0)
    drive.line('far-pedal', [(666, 744), (705, 741)], INK, width=8, opacity=.7, gaps=0)
    drive.line('near-crank', [(642, 794), (597, 851)], (87, 102, 94), width=10, opacity=.93, gaps=0)
    drive.line('near-crank-highlight', [(640, 796), (598, 850)], (209, 195, 146), width=2.2, opacity=.7)
    drive.line('near-pedal', [(573, 853), (621, 850)], INK, width=9, opacity=.93, gaps=0)
    drive.line('pedal-reflector', [(581, 852), (612, 850)], (204, 150, 51), width=3.8, opacity=.92)
    drive.line('center-bolt', ellipse(642, 794, 7, 7), INK, width=2.7, opacity=.97, gaps=0)

    controls = s.object('saddle-and-handlebars', '皮鞍座和弯把')
    saddle = curve([(512, 485), (527, 475), (555, 475), (576, 483), (622, 486),
                    (626, 493), (589, 501), (548, 504), (521, 499)], closed=True)
    controls.fill('leather-saddle', saddle, (112, 76, 42), opacity=.9, edge=.18, bleed=.6)
    controls.line('saddle-outline', saddle, INK, width=2.8, opacity=.85)
    controls.line('saddle-rail', curve([(533, 504), (555, 517), (594, 506)]), INK, width=3, opacity=.86)
    controls.line('saddle-top-wear', curve([(524, 484), (548, 482), (574, 490)]),
                  (211, 164, 94), width=2.1, opacity=.74)
    controls.line('stem', [(900, 516), (875, 450), (926, 440)],
                  (77, 91, 85), width=9.4, opacity=.91, gaps=0)
    controls.line('stem-highlight', [(900, 513), (878, 453), (924, 443)],
                  (225, 210, 164), width=2.4, opacity=.8)
    controls.line('handlebar', curve([(925, 440), (962, 445), (985, 465), (983, 494),
                  (963, 511), (944, 507)]), (73, 85, 77), width=8, opacity=.92, gaps=0)
    controls.line('bar-tape', curve([(980, 470), (981, 493), (963, 509), (945, 507)]),
                  (91, 91, 66), width=11, opacity=.85, gaps=0)
    for i in range(6):
        x, y = 978-i*5.3, 492+i*2.5
        controls.line(f'tape-wrap-{i}', [(x-3, y-4), (x+2, y+5)],
                      (198, 174, 118), width=1.3, opacity=.64)
    controls.line('brake-lever', curve([(973, 458), (961, 481), (963, 495)]),
                  (166, 177, 158), width=3.3, opacity=.88)
    controls.line('front-brake-cable', curve([(972, 462), (998, 498), (963, 566), (943, 615)]),
                  (72, 83, 73), width=1.2, opacity=.76, wobble=.3)
    controls.line('rear-brake-cable', curve([(931, 443), (897, 477), (777, 527), (592, 543), (545, 556)]),
                  (73, 81, 72), width=1.1, opacity=.63, wobble=.3)
    # Calipers sit at the wheel rim, not on the spokes.
    controls.line('front-caliper', curve([(923, 608), (940, 613), (954, 632)]),
                  INK, width=3.3, opacity=.85)
    controls.line('rear-caliper', curve([(538, 553), (548, 570), (545, 587)]),
                  INK, width=3.0, opacity=.8)

    # A rim strip of graphite hatching, a few frame scuffs and the kickstand.
    detail = s.object('working-marks', '用旧的痕迹和支架')
    detail.hatch('rear-tire-ground-hatch', [(268, 986), (459, 986), (440, 1011), (289, 1011)],
                 (64, 72, 59), opacity=.37, spacing=6, angle=70, width=1)
    detail.line('stand', [(622, 806), (681, 1001), (707, 1003)],
                (70, 80, 68), width=5.5, opacity=.88, gaps=0)
    detail.line('top-tube-scratch', [(709, 529), (733, 526)],
                (242, 210, 142), width=2.3, opacity=.85)
    detail.line('fork-scratch', [(959, 699), (968, 717)],
                (242, 210, 142), width=1.8, opacity=.81)
    # One dropped fastener near the foreground, together with a small spanner.
    detail.line('floor-nut', ellipse(865, 1028, 7, 4), INK, width=2.2, opacity=.74)
    detail.line('floor-washer', ellipse(911, 1031, 11, 5), INK, width=2, opacity=.65)
    detail.line('floor-spanner', [(756, 1024), (818, 1040)], (100, 113, 99), width=8, opacity=.74)
    detail.line('floor-spanner-jaw', curve([(748, 1014), (743, 1023), (751, 1031), (764, 1027)]),
                (83, 95, 80), width=4.3, opacity=.87)
    detail.line('floor-spanner-ring', ellipse(823, 1041, 10, 6, rotate=15),
                (87, 99, 86), width=3.1, opacity=.84)
    return s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'examples/gallery/bicycle-workshop')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    result = render_to(build_scene().data, args.out, args.overwrite)
    print(args.out / 'artwork.png')
    print('Warnings:', result['warnings'])


if __name__ == '__main__':
    main()
