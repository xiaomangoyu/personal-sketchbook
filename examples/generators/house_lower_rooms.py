"""Small, subdued domestic scenes for the cutaway-house reference study.

The coordinates follow the supplied 1354 x 1332 reference.  Architecture is
drawn by the parent generator; these objects stay inside its lower rooms.
"""

from math import cos, sin, pi


def draw_lower_rooms(g):
    """Draw four editable groups, ordered back to front within each room."""
    ink = '#34302c'

    # Laundry: the thin shelves and the rumpled pile give scale to the room.
    g.object('lower-laundry', '下层洗衣间')
    g.poly('shelf-upper', [(45, 575), (95, 555), (132, 568), (81, 590)],
           '#977556', outline=ink, width=1)
    g.poly('shelf-upper-edge', [(45, 575), (81, 590), (81, 597), (45, 582)],
           '#624f43', outline=ink, width=.8)
    g.line('bracket-left', [(49, 582), (49, 603), (64, 588)], ink, .9)
    g.line('bracket-right', [(112, 578), (113, 599), (128, 584)], ink, .9)
    g.poly('shelf-lower', [(46, 614), (106, 589), (143, 603), (83, 630)],
           '#9e785f', outline=ink, width=.9)
    g.poly('shelf-lower-edge', [(46, 614), (83, 630), (83, 635), (46, 620)],
           '#634738', outline=ink, width=.8)
    # Mismatched tins, a small carton and a detergent jug, no legible labels.
    for name, x, y, w, h, color in [
        ('tin-a', 61, 572, 10, 25, '#626f67'),
        ('tin-b', 76, 576, 11, 25, '#918b77'),
        ('tin-c', 91, 568, 8, 20, '#526e73'),
        ('carton', 53, 611, 13, 22, '#79474e'),
        ('tin-d', 78, 617, 9, 21, '#a58167'),
        ('tin-e', 94, 610, 11, 19, '#867e60'),
    ]:
        g.poly(name, [(x, y-h), (x+w, y-h+3), (x+w, y+3), (x, y)],
               color, outline=ink, width=.7)
        g.line(name+'-label', [(x+2, y-h+9), (x+w-2, y-h+11)],
               '#c2b394', .65, .6)
        g.line(name+'-lid', [(x, y-h+2), (x+w, y-h+5)], ink, .65)
    g.poly('laundry-detergent', [(113, 602), (112, 588), (116, 583),
                                (121, 585), (124, 590), (124, 607)],
           '#857c65', outline=ink, width=.8)
    g.poly('laundry-detergent-cap', [(116, 581), (121, 582), (121, 586), (116, 585)],
           '#413e39', outline=ink, width=.7)
    g.line('laundry-detergent-handle', [(120, 590), (122, 591), (122, 597)],
           '#413e39', .8, .8, smooth=True)

    # The rear machine is a lighter warm grey; its door sits in a foreshortened face.
    g.poly('dryer-side', [(127, 655), (142, 646), (143, 730), (128, 741)],
           '#81796f', outline=ink, width=1)
    g.poly('dryer-top', [(128, 654), (169, 633), (192, 642), (151, 665)],
           '#b2aa91', outline=ink, width=1)
    g.poly('dryer-face', [(151, 665), (192, 642), (192, 712), (151, 736)],
           '#a5a89b', outline=ink, width=1)
    g.line('dryer-panel', [(153, 677), (190, 655)], '#68685f', .9)
    g.oval('dryer-door-rim', 172, 691, 16, 27, '#5a6265', outline=ink,
           width=1.4, rotate=14)
    g.oval('dryer-door-glass', 172, 691, 12.5, 22, '#6e8993',
           outline='#a7a595', width=1, rotate=14)
    g.line('dryer-glass-light', [(172, 672), (166, 681), (164, 695)],
           '#98a4a0', 1.1, .5, smooth=True)
    g.oval('dryer-dial', 184, 656, 2.5, 3.5, '#444a48', outline=ink, width=.6)

    # Main washer: explicit top, front and side planes, and an open glass door.
    g.poly('washer-top', [(49, 674), (84, 650), (136, 668), (100, 694)],
           '#acaaa0', outline=ink, width=1)
    g.poly('washer-left-side', [(49, 674), (100, 694), (100, 765), (49, 748)],
           '#727782', outline=ink, width=1.1)
    g.poly('washer-front', [(100, 694), (136, 668), (136, 741), (100, 765)],
           '#919792', outline=ink, width=1)
    g.line('washer-panel', [(102, 705), (133, 683)], '#525857', .9)
    g.line('washer-panel-button', [(104, 701), (113, 694)], '#393f40', 1.6)
    g.oval('washer-dial', 128, 682, 2.3, 3.7, '#555351', outline=ink, width=.6)
    g.oval('washer-door-rim', 117, 722, 13.5, 24, '#494c56',
           outline=ink, width=1.5, rotate=14)
    g.oval('washer-door-inner', 117, 722, 10.5, 20, '#52666c',
           outline='#aaa39a', width=.7, rotate=14)
    g.path('washer-clothes-cream', [(108, 714), (114, 707), (120, 710),
                                  (126, 717), (122, 724), (116, 721), (113, 727)],
           '#c3b595', outline='#686764', width=.65)
    g.path('washer-clothes-blue', [(108, 722), (113, 718), (120, 727),
                                 (119, 737), (111, 739), (107, 732)],
           '#779397', outline='#4d6265', width=.6)
    g.path('washer-clothes-pink', [(111, 710), (115, 709), (115, 716),
                                 (112, 721), (108, 718)],
           '#bd9489', outline='#765e5b', width=.6)
    # Door opens toward the right and is visibly attached on one side.
    g.line('washer-door-hinge', [(131, 701), (140, 698)], ink, 1.3)
    g.oval('washer-open-door', 144, 710, 9, 25, '#bab3a8',
           outline='#45444b', width=1.5, rotate=-10)
    g.oval('washer-open-glass', 144, 710, 6.3, 20, '#7a8183',
           outline='#6a6867', width=.7, rotate=-10)
    # A bottle on top and soft, uneven towel edges in the front corner.
    g.poly('soap-bottle', [(73, 662), (74, 648), (77, 644), (82, 645), (84, 650), (83, 665)],
           '#586e74', outline=ink, width=.7)
    g.poly('soap-cap', [(76, 641), (81, 642), (81, 646), (76, 645)],
           '#a3889b', outline=ink, width=.6)
    g.line('soap-label', [(76, 654), (81, 656)], '#b2afa0', 2.5, .8)
    for n, y, color in [(0, 783, '#586275'), (1, 777, '#6f7975'),
                         (2, 771, '#a37c69'), (3, 765, '#ba9980'),
                         (4, 758, '#a39e89')]:
        g.poly(f'towel-{n}', [(146, y-8), (174, y-23), (193, y-17),
                              (193, y-8), (166, y+7), (145, y)],
               color, outline='#544843', width=.75)
        g.line(f'towel-fold-{n}', [(149, y-3), (167, y+2), (190, y-11)],
               '#665a50', .65, .75)
    g.poly('towel-top', [(150, 748), (175, 735), (193, 741), (169, 755)],
           '#c1b7a0', outline='#635b51', width=.8)
    g.line('towel-top-crease', [(158, 748), (170, 752), (186, 743)],
           '#8c806d', .8, .8)

    # Narrow bicycle store. Spokes are deliberately lighter than the frame.
    g.object('lower-bicycle-store', '下层单车储藏')
    g.poly('bicycle-floor-shadow', [(226, 800), (263, 781), (350, 821),
                                    (350, 843), (320, 846)],
           '#514844', outline='#514844', width=.2, opacity=.35)
    for wi, (cx, cy, rx, ry) in enumerate([(255, 787, 23, 30), (332, 814, 21, 30)]):
        g.oval(f'wheel-{wi}-tire', cx, cy, rx, ry, '#71615a',
               outline='#292c29', width=3, rotate=-17)
        g.oval(f'wheel-{wi}-inner', cx, cy, rx-3, ry-3, '#846b5c',
               outline='#b39d7f', width=.7, rotate=-17)
        # Apply the same rotation to elliptical spoke endpoints as the rim.
        a = -17*pi/180
        for j in range(12):
            t = j*pi/6
            dx, dy = (rx-3)*cos(t), (ry-3)*sin(t)
            ex, ey = cx+dx*cos(a)-dy*sin(a), cy+dx*sin(a)+dy*cos(a)
            g.line(f'wheel-{wi}-spoke-{j}', [(cx, cy), (ex, ey)],
                   '#3e4038', .65, .8)
        g.oval(f'wheel-{wi}-hub', cx, cy, 2.8, 3.2, '#4a4d44',
               outline='#292c29', width=.7)
    g.line('bicycle-frame-back', [(255, 787), (278, 764), (289, 805),
                                 (255, 787)], '#2d3935', 2, .95)
    g.line('bicycle-frame-front', [(278, 764), (307, 772), (289, 805),
                                  (332, 814), (307, 772)], '#43534d', 2.1, .98)
    g.line('bicycle-frame-glint', [(280, 762), (306, 770)], '#9a9b7e', .7, .7)
    g.line('bicycle-fork', [(305, 766), (332, 814)], '#282f2a', 2, .95)
    g.line('bicycle-seat-stem', [(281, 776), (275, 754)], '#302f2b', 1.8)
    g.path('bicycle-saddle', [(264, 752), (270, 749), (284, 753),
                             (285, 757), (278, 758), (269, 755)],
           '#5a473c', outline='#2b2d29', width=1)
    g.line('bicycle-handle-stem', [(307, 772), (300, 750), (299, 740)],
           '#3a4038', 2.1)
    g.line('bicycle-handlebars', [(287, 740), (297, 736), (308, 743),
                                 (312, 750), (308, 757)],
           '#393c34', 1.8, .95, smooth=True)
    g.line('bicycle-handle-grip', [(310, 750), (308, 757)], '#242b27', 3.1)
    g.oval('bicycle-crank', 289, 805, 5.5, 7.2, '#655f50',
           outline='#353a32', width=.9, rotate=-17)
    g.line('bicycle-chain', [(259, 787), (289, 798), (292, 811), (256, 790)],
           '#363b31', .8, .9)
    g.line('bicycle-pedal-arm', [(289, 805), (300, 814), (306, 813)],
           '#292d28', 1.8)
    g.line('bicycle-pedal', [(302, 810), (310, 813)], '#252c27', 2.7)
    g.line('bicycle-rack', [(236, 761), (257, 750), (280, 759)], '#3a4036', 1.1)
    g.line('bicycle-rack-stay', [(255, 787), (252, 754)], '#3d463b', .9)
    g.poly('bicycle-wall-hook', [(239, 723), (244, 721), (244, 735), (239, 737)],
           '#685647', outline='#3e3730', width=.7)
    g.line('bicycle-looped-lock', [(242, 732), (233, 740), (238, 750),
                                  (248, 746), (248, 737), (242, 732)],
           '#323a34', 1.5, .9, smooth=True)

    # Dining room: table legs and far chairs go behind the table top.
    g.object('lower-dining', '下层餐室')
    g.poly('dining-sideboard-side', [(386, 837), (415, 849), (415, 881), (386, 869)],
           '#604c43', outline=ink, width=.9)
    g.poly('dining-sideboard-top', [(386, 837), (419, 815), (448, 827), (415, 849)],
           '#806351', outline=ink, width=1)
    g.poly('dining-sideboard-front', [(415, 849), (448, 827), (448, 859), (415, 881)],
           '#765947', outline=ink, width=.9)
    g.line('dining-sideboard-division', [(432, 838), (432, 869)], '#493e36', .8)
    g.line('dining-sideboard-handle', [(429, 850), (434, 847)], '#b09773', 1.3)

    # Far chair, with a thin open back and a woven seat.
    g.line('chair-far-post-left', [(497, 819), (497, 783), (503, 779), (503, 813)],
           '#684c3c', 2)
    g.line('chair-far-post-right', [(523, 807), (523, 770), (529, 767), (529, 800)],
           '#684c3c', 2)
    g.line('chair-far-top', [(499, 784), (526, 771)], '#7f5c43', 2.2)
    g.line('chair-far-back', [(499, 793), (526, 781)], '#594232', 1.3)
    g.line('chair-far-slat', [(513, 778), (513, 798)], '#594232', 1.1)
    g.poly('chair-far-seat', [(497, 819), (524, 805), (540, 812), (513, 828)],
           '#9b795c', outline=ink, width=.9)
    g.line('chair-far-leg', [(516, 824), (516, 862)], '#5e4537', 2.4)

    # Left chair stays readable outside the table silhouette.
    g.line('chair-left-back-left', [(456, 840), (456, 806), (460, 802), (461, 837)],
           '#5d4438', 2.2)
    g.line('chair-left-back-right', [(479, 824), (479, 790), (483, 788), (483, 822)],
           '#5d4438', 2.1)
    g.line('chair-left-top', [(458, 807), (481, 792)], '#8f6b50', 2)
    g.line('chair-left-slat', [(469, 800), (469, 826)], '#684b39', 1)
    g.poly('chair-left-seat', [(456, 840), (480, 825), (498, 834), (474, 849)],
           '#9d795c', outline=ink, width=.8)
    for name, points in [('a', [(456, 841), (456, 877)]),
                         ('b', [(474, 849), (474, 887)]),
                         ('c', [(496, 835), (496, 868)])]:
        g.line('chair-left-leg-'+name, points, '#644a3a', 2.8)

    for name, points in [('back', [(550, 793), (550, 865)]),
                         ('left', [(480, 817), (480, 899)]),
                         ('right', [(607, 814), (607, 897)]),
                         ('front', [(534, 848), (534, 924)])]:
        g.line('table-leg-'+name, points, '#614637', 4)
        g.line('table-leg-highlight-'+name, [(x+1, y) for x, y in points],
               '#ad8562', .8, .6)
    g.poly('table-apron', [(470, 814), (535, 851), (615, 807),
                          (615, 816), (535, 859), (470, 822)],
           '#705040', outline=ink, width=1)
    g.poly('dining-table', [(470, 814), (548, 779), (615, 807), (535, 851)],
           '#ac846d', outline='#4a3b31', width=1.3)
    g.line('table-grain-a', [(486, 815), (550, 787), (600, 808)],
           '#85634d', .6, .65)
    g.line('table-grain-b', [(514, 833), (584, 803)], '#d0a286', .6, .4)

    # Tea for several people, a newspaper, and a little jar of stems.
    g.poly('folded-paper', [(491, 817), (503, 810), (520, 817), (508, 825)],
           '#c0b2a3', outline='#7b7468', width=.6)
    for n in range(3):
        g.line(f'paper-line-{n}', [(497+n*3, 817-n), (507+n*3, 821-n)],
               '#6c6c62', .55, .7)
    for name, cx, cy, color in [('left', 521, 810, '#b0b3a0'),
                                 ('back', 556, 802, '#bcad97'),
                                 ('front', 555, 831, '#a8a99c'),
                                 ('right', 584, 812, '#baa294')]:
        g.oval('saucer-'+name, cx, cy, 10.5, 4.6, color,
               outline='#656b61', width=.6, rotate=-8)
        g.oval('saucer-line-'+name, cx, cy, 7.6, 3.1, color,
               outline='#777b6d', width=.5, rotate=-8)
        g.path('cup-body-'+name, [(cx-4, cy-6), (cx+4, cy-6),
                                (cx+3, cy), (cx-3, cy+1)],
               '#c6b6a0', outline='#77786b', width=.65)
        g.oval('tea-'+name, cx, cy-6, 4.1, 1.9, '#766750',
               outline='#6b6e60', width=.55)
        g.line('cup-handle-'+name, [(cx+4, cy-5), (cx+7, cy-5),
                                  (cx+7, cy-2), (cx+3, cy-1)],
               '#797768', .75, .9, smooth=True)
    g.oval('tea-pot-shadow', 540, 817, 10, 4, '#847868', outline='#847868', width=.3)
    g.path('tea-pot-body', [(532, 811), (535, 806), (542, 806),
                          (546, 811), (547, 817), (539, 821), (532, 817)],
           '#aeaca0', outline='#676b60', width=.85)
    g.line('tea-pot-spout', [(534, 810), (528, 808), (530, 814), (533, 815)],
           '#72776b', 1.7, .9)
    g.line('tea-pot-handle', [(544, 810), (550, 807), (552, 813), (546, 816)],
           '#686b60', 1.5, .9, smooth=True)
    g.oval('tea-pot-lid', 539, 807, 5, 2.1, '#c0b9a7', outline='#737467', width=.6)
    g.oval('tea-pot-knob', 539, 804, 1.8, 1.9, '#878c7a', outline='#5e6558', width=.5)
    g.poly('table-jar', [(566, 790), (572, 791), (573, 799), (568, 801), (565, 798)],
           '#a5b3a4', outline='#727d6f', width=.6)
    g.line('jar-stem-a', [(569, 793), (568, 781), (566, 778)], '#6b7560', .8)
    g.line('jar-stem-b', [(570, 794), (573, 783)], '#6b7560', .7)

    # A cropped chair in front anchors the foreground edge of the little room.
    g.poly('chair-front-seat', [(572, 886), (596, 870), (616, 879), (591, 896)],
           '#99725a', outline=ink, width=.9)
    g.line('chair-front-back', [(595, 887), (595, 850), (616, 837), (616, 929)],
           '#644838', 2.4)
    g.line('chair-front-upper-rail', [(596, 858), (616, 845)], '#957354', 1.8)
    g.line('chair-front-slat', [(606, 851), (606, 876)], '#6c4e3c', 1.2)
    g.line('chair-front-leg-a', [(575, 887), (575, 926)], '#604435', 3)
    g.line('chair-front-leg-b', [(592, 896), (592, 939)], '#604435', 3)

    # Kitchen corner behind the entrance: shaded cupboards and a tall fridge.
    g.object('lower-kitchen', '下层厨房一角')
    g.poly('kitchen-counter-front', [(1150, 790), (1207, 809), (1207, 862), (1150, 843)],
           '#8a6e69', outline=ink, width=.9)
    g.poly('kitchen-counter-side', [(1207, 809), (1230, 796), (1230, 850), (1207, 862)],
           '#645959', outline=ink, width=.9)
    g.poly('kitchen-counter-top', [(1150, 782), (1172, 771), (1230, 791), (1207, 809)],
           '#a29186', outline='#4e4942', width=1.1)
    g.line('kitchen-drawer', [(1154, 804), (1202, 821)], '#6b5551', .9)
    g.line('kitchen-cupboard-seam', [(1179, 815), (1179, 852)], '#64514b', .8)
    g.line('kitchen-drawer-pull', [(1172, 806), (1181, 809)], '#c1a889', 1.6)
    g.line('kitchen-door-pull', [(1183, 826), (1183, 837)], '#b8a086', 1.2)
    g.oval('kitchen-plate', 1173, 790, 10, 4, '#c1b0a0', outline='#6b6560', width=.7)
    g.oval('kitchen-plate-inner', 1173, 790, 6.3, 2.4, '#bc9d89',
           outline='#896e5b', width=.55)
    g.oval('kitchen-mug-top', 1157, 782, 4.2, 2, '#b4a89b',
           outline='#756f60', width=.6)
    g.poly('kitchen-mug', [(1153, 782), (1161, 783), (1160, 788), (1154, 787)],
           '#aaa591', outline='#746e60', width=.6)

    g.poly('fridge-top', [(1224, 775), (1260, 756), (1287, 767), (1251, 787)],
           '#74717a', outline=ink, width=1)
    g.poly('fridge-side', [(1251, 787), (1287, 767), (1287, 880), (1251, 902)],
           '#52535c', outline=ink, width=1.2)
    g.poly('fridge-face', [(1224, 775), (1251, 787), (1251, 902), (1224, 890)],
           '#838084', outline=ink, width=1)
    g.line('fridge-freezer-seam', [(1225, 810), (1250, 821)], '#514e50', .9)
    g.line('fridge-freezer-handle', [(1244, 795), (1244, 807)], '#b4aaa1', 1.5)
    g.line('fridge-main-handle', [(1244, 832), (1244, 851)], '#b4aaa1', 1.5)
    # Imperfect pinned scraps keep the household detail without copying text.
    for n, (x, y, color) in enumerate([(1230, 792, '#9ba9a0'),
                                      (1233, 819, '#ba9b89'),
                                      (1228, 835, '#bdafa0')]):
        g.poly(f'fridge-note-{n}', [(x, y), (x+7, y+2), (x+6, y+10), (x, y+8)],
               color, outline='#5b5a53', width=.5)
        g.oval(f'fridge-magnet-{n}', x+3, y+2, 1.1, 1.1, '#826c67',
               outline='#51463d', width=.3)
    g.line('fridge-side-reflection', [(1256, 795), (1256, 890)], '#79747a', .8, .35)
