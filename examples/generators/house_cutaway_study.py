#!/usr/bin/env python3
"""Simplified, code-drawn study of the user's supplied cutaway-house reference.

The reference is not embedded or traced automatically. Authored geometry retains
its room arrangement, sightline, daily-life gestures and light hierarchy. This is
a personal reference study, not an original showcase work or a claim of authorship
over the reference. Output remains ordinary editable scene-v1 JSON and layers.
"""
from __future__ import annotations
import argparse
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from render import render_to
from house_geometry import Drawing, lerp, wall_frame, cabinet
from house_people import bedroom_person, standing_person, sofa_person, floor_child, entry_person
from house_lower_rooms import draw_lower_rooms


def architecture_lower(g):
    g.object('house-section', '墨绿色夜色中的住宅切面')
    g.poly('silhouette',[(30,341),(203,240),(532,355),(698,258),(1305,465),
           (1305,903),(978,1094),(29,770)],'#101b18',None)
    g.poly('foundation',[(36,752),(358,864),(623,961),(977,1084),(1300,898),
           (1300,914),(978,1100),(33,778)],'#101512',None)
    g.object('lower-shell','下层的暗墙与地面')
    g.poly('laundry-wall',[(41,549),(199,605),(199,794),(41,739)],'#b09a84')
    g.poly('laundry-floor',[(42,736),(98,704),(200,755),(200,801)],'#9f7867')
    g.poly('bike-wall',[(205,607),(360,662),(360,846),(205,794)],'#a88776')
    g.poly('bike-side',[(294,639),(333,619),(358,663),(358,846),(293,823)],'#875f64')
    g.poly('bike-floor',[(206,754),(286,711),(359,793),(359,852),(206,799)],'#826861')
    g.poly('dining-back',[(371,663),(622,750),(622,946),(371,857)],'#ae8b78')
    g.poly('dining-floor',[(372,824),(457,777),(622,835),(622,950)],'#8d7164')
    g.poly('dining-side',[(457,695),(621,753),(621,841),(457,782)],'#c2a192')
    g.poly('stairwell',[(626,750),(744,693),(1067,810),(1067,1026),
            (977,1080),(626,951)],'#222824')
    g.poly('entry-back',[(802,781),(1081,878),(1081,1009),(978,1072),(803,1010)],'#a18b77')
    g.poly('entry-floor',[(809,992),(887,947),(1082,1008),(977,1078)],'#b49377')
    g.poly('kitchen-back',[(1081,810),(1296,687),(1296,899),(1081,1023)],'#80736e')
    g.poly('kitchen-floor',[(1083,948),(1245,855),(1296,893),(1083,1017)],'#827f75')
    # Sparse floorboard joints describe orientation, without filling every room.
    g.hatch('laundry-board',[(42,736),(98,704),(198,755),(198,799)],'#584f49',.36,6,19)
    g.hatch('bike-board',[(207,754),(286,711),(358,793),(358,850),(207,799)],'#574c45',.30,7,19)
    # Kitchen checkerboard is confined to the visible floor strip.
    for i in range(6):
        for j in range(3):
            x=1101+i*28+j*22; y=946-i*16+j*8
            if x+50<1297 and y+8<1009:
                g.poly(f'tile-{i}-{j}',[(x,y),(x+28,y-16),(x+50,y-8),(x+22,y+8)],
                       '#454b46' if (i+j)%2 else '#9a9688',None)
    g.line('dining-skirting',[(373,817),(456,770),(620,827)],'#e4bf9e',3,.65)


def lower_shadows(g):
    g.object('lower-room-shade','楼板下的退暗与局部反光')
    rooms=[[(41,555),(197,610),(197,798),(41,743)],
           [(206,613),(358,666),(358,851),(206,798)],
           [(373,670),(620,756),(620,950),(373,862)],
           [(1082,814),(1296,692),(1296,900),(1082,1021)]]
    for i,room in enumerate(rooms):
        g.poly(f'shade-{i}',room,'#283731',None,opacity=.12 if i!=1 else .18)
        # Shadow cast by the ceiling is a shallow band, darkest at the top.
        a,b,c,d=room
        for j in range(8):
            t=j/8*.32; u=(j+1)/8*.32
            q=[lerp(a,d,t),lerp(b,c,t),lerp(b,c,u),lerp(a,d,u)]
            g.poly(f'ceiling-shadow-{i}-{j}',q,'#202922',None,opacity=.22*(1-j/8))
    g.light('dining-warmth',442,800,110,120,'#efbe91',rooms[2],.025)


def upper_shell(g):
    g.object('upper-floor','连续楼板与楼梯开口')
    # Front edge stops at the stair opening. The short left lip and the living
    # room edge meet the two upper corners of the staircase, not across its void.
    g.poly('bedroom-floor',[(38,546),(204,449),(527,563),(365,658)],'#c3a073')
    g.poly('hall-floor',[(366,649),(537,550),(843,658),(732,721),(654,766)],'#d3b489')
    g.poly('living-floor',[(735,721),(845,654),(983,571),(1298,677),(1050,820)],'#b89a72')
    g.light('bed-floor-light',175,534,171,87,'#eac78a',[(38,546),(204,449),(527,563),(365,658)],.025)
    g.light('hall-floor-light',610,622,221,120,'#f0d3a0',[(366,649),(537,550),(843,658),(732,721),(654,766)],.033)
    g.light('living-floor-light',1111,668,165,99,'#dfc38e',[(735,721),(845,654),(983,571),(1298,677),(1050,820)],.017)
    g.poly('left-slab',[(36,544),(365,658),(654,759),(654,775),(364,674),(35,561)],'#322920',None)
    g.poly('right-slab',[(735,719),(1050,811),(1299,670),(1299,686),(1050,828),(735,735)],'#362c23',None)
    for i in range(5):
        g.line(f'bed-floor-joint-{i}',[(43+i*56,550+i*19),(201+i*55,459+i*19)],'#826b50',.6,.40)
    g.object('bedroom-walls','冷蓝卧室墙面')
    g.poly('left-wall',[(35,345),(203,247),(203,450),(36,545)],'#43666a')
    g.poly('back-wall',[(204,247),(531,361),(531,566),(204,451)],'#456d6e')
    g.plane('bedroom-cool',[(204,247),(531,361),(531,566),(204,451)],'#4b7474','#33565c')
    g.light('bed-lamp-wall',193,406,103,108,'#b7b790',[(204,247),(531,361),(531,566),(204,451)],.025)
    g.poly('corner-shadow',[(205,255),(231,264),(231,460),(205,451)],'#375652',None,.5,.60)
    g.line('left-skirting',[(41,530),(202,438),(356,492)],'#b49b73',4,.8)
    g.line('bed-wall-cap',[(34,344),(203,243),(530,358)],'#102420',7,1)
    g.object('bathroom','后侧的深紫浴室')
    g.poly('bath-left',[(539,357),(698,265),(698,440),(539,529)],'#625362')
    g.poly('bath-back',[(698,265),(980,362),(980,534),(698,440)],'#594251')
    # Just a few tile grids, progressively lower contrast in the shadow.
    for i in range(1,10):
        x=699+i*24
        g.line(f'tile-v-{i}',[(x,266+(x-698)*.344),(x,440+(x-698)*.344)],'#8a6c7a',.6,.5)
    for i in range(1,8):
        y=265+i*22
        g.line(f'tile-h-{i}',[(699,y),(979,y+97)],'#8a6c7a',.6,.4)
    g.poly('shower-shadow',[(724,307),(820,340),(820,457),(724,424)],'#342e37')
    g.poly('curtain',[(756,341),(782,350),(840,327),(840,451),(806,466),(756,447)],'#aaa6a0')
    for i in range(7):
        x=762+i*11; y=346 if x<783 else 350-(x-783)*.38
        g.line(f'curtain-fold-{i}',[(x,y+5),(x-1,y+53),(x+1,y+110)],'#575763',.85,.72)
        g.oval(f'curtain-ring-{i}',x,y+1,2,3,'#958b89','#403d44',.65)
    g.line('curtain-rail',[(753,337),(782,347),(843,323)],'#cdc5b8',2,.8)
    g.line('bath-cap',[(535,357),(699,260),(982,359)],'#281d2b',7,1)
    g.object('living-wall','灰粉色的客厅墙')
    g.poly('left-plane',[(840,454),(982,372),(982,572),(840,654)],'#b58e7a')
    g.poly('right-plane',[(982,372),(1299,479),(1299,677),(982,570)],'#a5846c')
    g.poly('shelf-shadow',[(986,379),(1089,414),(1089,613),(986,577)],'#806852',None)
    g.line('living-cap',[(839,456),(982,367),(1302,475)],'#211f1b',7,1)
    g.line('right-cut',[(1302,478),(1302,678)],'#151e18',8,1)


def bedroom(g):
    g.object('bedroom-fittings','卧室画框、书架、床头灯')
    wall_frame(g,'landscape',[(95,346),(157,310),(157,365),(95,402)],'#b59672','#7d997f',4)
    g.poly('landscape-hill',[(100,375),(115,357),(127,367),(141,345),(152,340),(152,363),(100,393)],'#657859',None)
    wall_frame(g,'portrait',[(309,295),(347,309),(347,378),(309,365)],'#a88154','#7d937d',4)
    g.path('painted-leaf',[(319,352),(318,323),(332,315),(337,337),(327,342)],'#a2a18a',None)
    for k,(x,y,w) in enumerate([(210,278,88),(207,317,90),(213,359,88)]):
        g.poly(f'shelf-{k}',[(x-9,y),(x+w,y+w*.35),(x+w+8,y+w*.35-5),(x,y-5)],'#ac7a50')
        for j in range(7-k):
            xx=x+j*10; yy=y+(xx-x)*.35
            h=17+(j*7+k*5)%15
            g.poly(f'book-{k}-{j}',[(xx,yy-h),(xx+7,yy-h+2.5),(xx+7,yy+1),(xx,yy-1)],
                   ['#997258','#c19b6c','#557976','#7c5650'][j%4],width=.65)
            g.line(f'book-spine-{k}-{j}',[(xx+2,yy-h+4),(xx+2,yy-3)],'#dcc9a1',.45,.5)
    g.poly('bedside',[(166,427),(192,410),(220,422),(193,439)],'#c59561')
    g.poly('bedside-front',[(166,427),(193,439),(193,481),(166,471)],'#997045')
    g.poly('bedside-side',[(193,439),(220,422),(220,464),(193,481)],'#73583b')
    g.line('drawer',[(168,444),(190,453)],'#422f26',.8)
    g.oval('drawer-handle',181,450,2,2,'#dfbc72',width=.6)
    g.poly('lamp-light',[(178,409),(181,372),(203,377),(214,423)],'#ead5a0',None,opacity=.32)
    g.line('lamp-stem',[(193,400),(193,369)],'#d9bd80',2)
    g.oval('lamp-foot',193,403,8,3,'#d5b473')
    g.path('lamp-shade',[(186,366),(189,355),(198,357),(202,372)],'#f7d69a',width=.8)
    # Radiator ribs conform to the back-wall plane.
    g.poly('radiator',[(237,398),(318,426),(318,478),(237,450)],'#c1c0a0')
    for i in range(17):
        x=241+i*4.3
        g.line(f'radiator-rib-{i}',[(x,404+(x-241)*.35),(x,448+(x-241)*.35)],'#686d60',.85,.8)
    g.line('rad-pipe',[(239,451),(239,460),(321,488)],'#777466',2)
    # Side wardrobe recedes behind the corridor cut wall.
    g.poly('wardrobe-front',[(345,318),(395,335),(395,478),(345,460)],'#436162')
    g.poly('wardrobe-side',[(396,336),(435,359),(435,490),(395,479)],'#6f523d')
    g.line('wardrobe-edge',[(396,335),(396,477)],'#c2905c',3)
    g.path('hanging-coat',[(401,376),(411,368),(424,382),(419,393),(422,452),(406,447),(403,402)],'#a5835d')
    g.object('bed','床、毯子与床柱')
    g.poly('bed-shadow',[(112,497),(247,545),(341,491),(346,546),(242,603),(91,550)],'#857252',None,opacity=.47)
    g.poly('bed-frame',[(108,454),(248,503),(336,454),(336,546),(248,585),(108,534)],'#b68b58')
    g.poly('bed-front',[(107,493),(248,542),(248,556),(107,507)],'#926c45')
    g.poly('under-bed',[(112,510),(241,555),(241,569),(112,524)],'#65644b',None)
    g.poly('bed-end',[(248,542),(337,493),(337,524),(248,574)],'#ba915c')
    g.poly('mattress-side',[(109,447),(246,495),(331,447),(331,495),(246,542),(109,496)],'#ccbfa0')
    g.poly('mattress-top',[(109,447),(195,397),(331,445),(246,495)],'#d4c5a3')
    g.poly('bed-sheet-top',[(158,441),(225,409),(323,445),(244,491)],'#ac6558')
    g.poly('bed-sheet-fall',[(110,451),(244,497),(323,452),(323,484),(245,529),(110,482)],'#b16958')
    g.path('pillow',[(113,434),(140,417),(178,430),(186,449),(156,462),(122,452)],'#e1d8bc')
    g.poly('blanket',[(213,486),(248,498),(277,482),(280,502),(246,520),(210,507)],'#6a8067')
    for i in range(6):
        g.line(f'blanket-thread-{i}',[(215+i*4,488+i*1.4),(214+i*4,502+i*1.4)],'#b5b08a',.6,.4)
    for i,(x,y) in enumerate([(108,454),(247,531),(334,481)]):
        g.poly(f'bed-post-{i}',[(x-3,y-14),(x+3,y-12),(x+3,y+87),(x-3,y+85)],'#c29a67',width=.9)
        g.oval(f'finial-{i}',x,y-15,4,4,'#bf9663',width=.8)
    bedroom_person(g)
    # Open window frame in front of the bed, with amber panes.
    g.object('bedroom-window','推开的卧室窗')
    g.poly('outer-frame',[(65,384),(142,412),(143,534),(64,505)],'#8d8671','#2d3632',3)
    g.poly('glass',[(71,395),(135,418),(135,520),(71,497)],'#c29d70',width=.6,opacity=.72)
    g.poly('glass-light',[(75,402),(99,410),(99,505),(75,496)],'#ebbc81',None,opacity=.48)
    g.line('window-center',[(101,406),(102,508)],'#626757',3)
    g.line('window-cross',[(70,442),(136,465)],'#626757',3)
    g.line('window-glint',[(80,407),(111,459)],'#e4cc9f',.8,.4)


def hall(g):
    g.object('hall-wall','橄榄色走廊与两扇门')
    g.poly('left-plane',[(368,460),(536,365),(536,564),(368,659)],'#969b80')
    g.poly('front-plane',[(536,365),(836,466),(836,662),(536,560)],'#a5a58b')
    g.plane('hall-left-light',[(368,460),(536,365),(536,564),(368,659)],'#79866f','#a7ad91')
    g.plane('hall-right-light',[(536,365),(836,466),(836,662),(536,560)],'#b0b299','#8a937b')
    g.light('pendant-wall',690,546,116,113,'#ded3a8',[(536,365),(836,466),(836,662),(536,560)],.018)
    g.poly('wall-shadow',[(537,370),(568,381),(568,571),(537,560)],'#898c75',None,opacity=.6)
    g.line('hall-top',[(366,457),(536,360),(839,462)],'#2b332a',6,1)
    g.line('hall-cut',[(366,458),(366,655)],'#273029',7,1)
    g.line('left-baseboard',[(373,646),(537,550),(835,652)],'#d8cfac',5,.95)
    # Doorways remain holes bounded by jambs; their axes follow each wall.
    wall_frame(g,'left-door',[(420,461),(476,429),(476,594),(420,626)],'#b28554','#745c42',5)
    g.poly('left-transom',[(422,442),(476,411),(476,428),(422,458)],'#678378','#bb915e',3)
    g.line('left-handle',[(459,524),(470,518)],'#e4cfac',2)
    wall_frame(g,'back-door',[(600,436),(662,457),(662,604),(600,583)],'#bd9261','#80624b',5)
    g.poly('back-transom',[(597,396),(665,419),(665,443),(597,420)],'#6a6e60','#bc9060',4)
    g.line('door-inner',[(606,443),(656,460),(656,594)],'#a17a54',.7)
    g.poly('switch',[(579,475),(587,478),(587,489),(579,486)],'#d8d6bc',width=.8)
    g.line('switch-line',[(583,479),(583,484)],width=.9)
    # Clock's ellipse is in the wall plane, not a front-facing icon.
    g.oval('clock',748,475,11,14,'#eee7ce','#6c7264',1.5,rotate=-13)
    g.line('clock-hands',[(747,465),(748,475),(742,479)],'#515c50',1.2)
    g.poly('hall-radiator',[(711,552),(780,575),(780,635),(711,612)],'#d1cbb3')
    for i in range(15):
        x=715+i*4.4
        g.line(f'hall-rib-{i}',[(x,557+(x-715)*.33),(x,609+(x-715)*.33)],'#747d6e',.8,.72)
    g.line('rad-pipe',[(716,615),(716,625),(777,647)],'#7d8777',1.5)
    # A small pendant: the floor carries the light, not a uniform glow overlay.
    g.line('pendant-wire',[(696,494),(696,518)],'#5e6556',1)
    g.oval('ceiling-rose',696,495,7,3,'#d4ccb1',width=.7)
    g.path('pendant',[(668,525),(683,514),(699,515),(720,528),(720,536),(688,542),(668,536)],'#eee4c4',width=1.1)
    g.line('pendant-rim',[(669,536),(689,541),(718,535)],'#aaa88b',.7)
    g.object('hall-laundry','熨衣板、地毯与洗衣篮')
    # Elliptical rug on the ground plane, with restrained concentric seams.
    g.oval('rug',593,670,105,54,'#ad625d','#9d6556',1.1,rotate=14)
    for k in range(3):
        from scene_tools import ellipse
        g.line(f'rug-ring-{k}',ellipse(593,670,91-k*12,44-k*6,rotate=14,n=60),'#c18a77',.6,.55)
    g.line('ironing-leg-back',[(449,623),(502,683)],'#3a453c',3)
    g.line('ironing-leg-front',[(527,642),(474,680)],'#4b4b3e',3)
    g.path('ironing-top',[(429,598),(438,595),(551,623),(553,631),(543,635),(427,607)],'#b7b29a')
    g.path('shirt',[(470,604),(484,601),(507,610),(504,623),(493,622),(491,653),(476,648)],'#c98367')
    g.line('shirt-fold',[(479,616),(489,624),(484,645)],'#915648',.8)
    g.path('iron',[(515,618),(514,598),(520,590),(526,600),(529,623)],'#3d6262')
    g.line('iron-handle',[(519,612),(519,599),(522,597),(524,613)],'#9baca0',1.2)
    g.poly('basket',[(539,675),(570,665),(614,681),(601,719),(555,704)],'#93988a')
    g.poly('basket-opening',[(539,675),(569,662),(615,678),(584,691)],'#494f45')
    for i in range(7):
        x=550+i*7
        g.line(f'basket-slots-{i}',[(x,687+(x-550)*.22),(x+4,702+(x-550)*.27)],'#525f54',1.5,.7)
    for i,(x,y,c) in enumerate([(554,669,'#457a7d'),(569,667,'#c9bcb0'),(584,672,'#b8c3ac'),(598,675,'#a67467')]):
        g.path(f'clothes-{i}',[(x-8,y+6),(x-7,y-4),(x,y-10),(x+10,y-2),(x+9,y+9),(x+2,y+11)],c,width=.65)


def living_fittings(g):
    g.object('living-fittings','书架、镜子、暖色画与电视柜')
    wall_frame(g,'sunset',[(922,437),(964,413),(967,466),(926,490)],'#5b5849','#d9b186',3)
    g.path('paint-hills',[(928,479),(939,459),(949,466),(961,442),(961,467),(929,485)],'#bd815e',None)
    g.oval('paint-sun',950,444,6,7,'#e8c798',None)
    g.path('wall-clock',[(880,469),(889,465),(897,481),(893,498),(881,500),(875,489)],'#775249')
    g.oval('clock-face',887,484,6,8,'#dfc79e',width=.6)
    g.line('clock-hands',[(887,477),(887,484),(890,486)],'#4b4940',.8)
    for k,y in enumerate([413,451,492,532]):
        g.poly(f'shelf-{k}',[(991,y),(1085,y+32),(1092,y+28),(999,y-4)],'#a47d56')
        for j in range(8 if k<2 else 5):
            x=998+j*10; yy=y+(x-991)*.34
            h=18+(j*7+k*3)%13
            g.poly(f'books-{k}-{j}',[(x,yy-h),(x+7,yy-h+2),(x+7,yy),(x,yy-2)],
                   ['#645d4e','#788475','#aa8b67','#735a4c','#c3a172'][j%5],width=.55)
            g.line(f'book-line-{k}-{j}',[(x+2,yy-h+4),(x+2,yy-3)],'#d0b894',.45,.45)
    cabinet(g,'bookcase-base',990,538,93,52,'#a58e65')
    g.oval('green-bowl',1054,533,12,7,'#7d9d8c',width=.8)
    g.line('bowl-lip',[(1042,532),(1054,535),(1066,532)],'#c7c8a7',.7)
    g.oval('mirror-frame',1133,475,32,40,'#594f41','#3b3c30',3,rotate=-20)
    g.oval('mirror',1133,475,28,36,'#cbc8ae','#e2d8b7',2,rotate=-20)
    g.path('mirror-reflection',[(1109,466),(1120,447),(1142,452),(1155,470),(1148,482),(1120,479)],'#e8d7b2',None)
    g.line('mirror-glint',[(1121,448),(1148,474)],'#f2e9c9',2,.65)
    for k,(x,y,w) in enumerate([(1175,478,95),(1170,518,94)]):
        g.poly(f'wall-shelf-{k}',[(x,y),(x+w,y+w*.34),(x+w+7,y+w*.34-5),(x+7,y-5)],'#ad855a')
        for j in range(4):
            xx=x+10+j*20; yy=y+(xx-x)*.34
            if j%2:
                g.poly(f'photo-{k}-{j}',[(xx,yy-18),(xx+12,yy-14),(xx+12,yy),(xx,yy-4)],'#ccb58c','#5d5546',2)
            else:
                g.poly(f'bottle-{k}-{j}',[(xx,yy-19),(xx+4,yy-18),(xx+5,yy-8),(xx+7,yy-6),(xx+7,yy),(xx-1,yy-3),(xx-1,yy-10)],'#6e8772',width=.65)
    cabinet(g,'tv-cabinet',1070,585,108,55,'#ad9f70')
    g.poly('tv-shadow',[(1067,591),(1150,616),(1197,589),(1114,562)],'#8f865f',None,opacity=.4)
    g.poly('tv',[(1081,523),(1168,549),(1164,609),(1078,581)],'#71896b','#393e32',3)
    g.poly('tv-glass',[(1087,529),(1161,552),(1157,600),(1085,577)],'#aaba79','#bbc59a',1)
    for i in range(6):
        x=1096+i*10
        g.line(f'tv-rain-{i}',[(x,543+i%3*7+(x-1096)*.31),(x-2,550+i%3*7+(x-1096)*.31)],'#d8dca7',1,.65)
    g.line('tv-stand',[(1118,591),(1118,607),(1106,611)],'#474a36',3)
    # Window is built over the cabinet's far end as in the supplied reference.
    g.poly('window-open',[(1203,551),(1270,512),(1270,629),(1203,670)],'#838673','#343b31',4)
    g.poly('window-glass',[(1210,553),(1263,524),(1263,625),(1210,656)],'#b59169',width=.8,opacity=.68)
    g.line('window-vertical',[(1237,538),(1237,641)],'#4f5d4d',3)
    g.line('window-horizontal',[(1210,598),(1264,568)],'#4f5d4d',3)
    g.line('window-glow',[(1215,558),(1220,651)],'#e5b67e',2,.5)


def sofa(g):
    g.object('living-sofa','有人倚坐的绿沙发')
    g.poly('sofa-shadow',[(847,620),(939,666),(1024,617),(1009,605),(927,648)],'#726b51',None,opacity=.6)
    g.poly('sofa-back',[(869,553),(956,501),(977,510),(1007,575),(916,627),(868,607)],'#566753')
    g.poly('sofa-seat',[(868,591),(957,541),(1005,582),(916,635)],'#6c795e')
    g.poly('sofa-base',[(868,603),(916,636),(1008,583),(1008,611),(919,663),(868,636)],'#4e5c48')
    g.poly('cushion-a',[(875,595),(918,571),(957,593),(916,628)],'#76836a',width=.7)
    g.poly('cushion-b',[(922,568),(960,545),(1000,582),(959,608)],'#687861',width=.7)
    g.path('left-arm',[(862,566),(873,559),(889,565),(891,625),(880,637),(863,626)],'#66705a')
    g.path('right-arm',[(981,548),(992,541),(1004,549),(1020,595),(1007,608),(998,582)],'#808467')
    g.line('sofa-seam',[(883,626),(918,645),(1002,598)],'#a6ab84',.65,.4)
    g.hatch('sofa-shadow-hatch',[(871,626),(918,655),(1004,608),(1004,618),(919,667),(871,638)],'#293c2e',.21,5,72)
    for i,(x,y) in enumerate([(874,637),(923,664),(1004,614)]):
        g.line(f'leg-{i}',[(x,y),(x,y+10)],'#393b2b',4)
    sofa_person(g)
    standing_person(g)


def living_table(g):
    g.object('coffee-table','茶几、披萨与散放的小物')
    g.poly('table-shadow',[(973,716),(1053,750),(1149,694),(1071,666)],'#847653',None,opacity=.55)
    for i,(x,y) in enumerate([(969,671),(1049,700),(1122,657)]):
        g.poly(f'table-leg-{i}',[(x,y),(x+6,y+2),(x+6,y+43),(x,y+42)],'#855b3a')
    g.poly('table-top',[(962,656),(1045,611),(1128,641),(1048,689)],'#c4935d','#514333',1.6)
    g.poly('table-apron',[(962,656),(1048,689),(1128,641),(1128,651),(1048,699),(962,667)],'#996a42')
    g.line('table-top-light',[(966,655),(1049,685),(1123,642)],'#dfb57b',1.1)
    g.poly('pizza-box',[(1025,635),(1048,621),(1081,632),(1057,647)],'#d6b87d')
    g.oval('pizza',1053,635,19,8,'#d3a156','#716139',.7,rotate=12)
    for i,(x,y) in enumerate([(1044,632),(1058,638),(1063,633),(1050,638)]):
        g.oval(f'pizza-topping-{i}',x,y,2,1.5,'#9f6846',None)
    g.poly('laptop-base',[(978,654),(1003,640),(1029,649),(1002,664)],'#746b52')
    g.poly('laptop-screen',[(1004,639),(988,608),(1012,594),(1029,625)],'#8d8b71','#3b4235',2)
    g.poly('laptop-display',[(1006,634),(992,609),(1010,600),(1024,623)],'#aaa78a',width=.7)
    g.line('keyboard',[(988,653),(1001,646),(1015,651)],'#b1ad8b',.8)
    for i,(x,y) in enumerate([(975,651),(1070,671)]):
        g.poly(f'cup-{i}',[(x-3,y-9),(x+4,y-7),(x+3,y+5),(x-3,y+3)],'#e4d5ab',width=.7)
        g.oval(f'cup-rim-{i}',x,y-8,4,2,'#97724b',width=.6)
    g.poly('remote',[(1028,669),(1043,660),(1048,663),(1033,672)],'#414b3c')
    g.line('cable',[(1138,625),(1157,640),(1138,654),(1148,667)],'#655d45',.8,.8,True)
    floor_child(g)
    g.poly('phone',[(1127,719),(1135,709),(1141,712),(1132,724)],'#ece9cf','#4f594d',1)


def stairs_and_rails(g):
    g.object('staircase','连接上下层的楼梯')
    # The stair runs toward the observer. Each tread meets the next riser;
    # endpoints (655,763)-(735,718) and (836,1034)-(916,989).
    a=(655,764); b=(735,718); dx=15; dy=23
    for i in range(12):
        x=a[0]+i*dx; y=a[1]+i*dy
        u=b[0]+i*dx; v=b[1]+i*dy
        g.poly(f'riser-{i}',[(x+15,y+10),(u+15,v+10),(u+15,v+23),(x+15,y+23)],'#a47852' if i<7 else '#91664f')
        g.poly(f'tread-{i}',[(x,y),(u,v),(u+15,v+10),(x+15,y+10)],'#c2996a' if i<7 else '#b58966')
        g.line(f'step-light-{i}',[(x+2,y+9),(u+14,v+10)],'#e6be86',1.1,.78)
    # Dark left stringer locates the flight against the cut-away void.
    g.poly('left-stringer',[(654,774),(836,1051),(836,1035),(654,757)],'#473c2d',None)
    # Downstairs radiator is behind the front stair rail.
    g.poly('entry-radiator',[(874,838),(969,871),(969,921),(874,888)],'#b1b1a0')
    for i in range(19):
        x=878+i*4.7
        g.line(f'entry-rad-{i}',[(x,844+(x-878)*.35),(x,887+(x-878)*.35)],'#687569',.8,.7)
    g.object('upper-railing','楼梯口与客厅前沿的木栏杆')
    # First railing borders stair left return; long rail borders the living slab.
    for side,(p,q) in enumerate([((735,721),(782,694)),((783,733),(1046,824))]):
        count=4 if side==0 else 17
        for i in range(count):
            x,y=lerp(p,q,i/(count-1))
            h=82
            g.line(f'post-dark-{side}-{i}',[(x,y),(x,y-h)],'#503d29',4)
            g.line(f'post-light-{side}-{i}',[(x-1,y-2),(x-1,y-h+2)],'#cda46a',1.2)
            g.oval(f'post-foot-{side}-{i}',x,y,3,2,'#715039',width=.65)
        g.line(f'rail-shadow-{side}',[(p[0],p[1]-82),(q[0],q[1]-82)],'#553e2a',8,1)
        g.line(f'rail-light-{side}',[(p[0],p[1]-84),(q[0],q[1]-84)],'#cfaa76',3,.9)
    # Sloped rail is a single continuous line from landing to lower newel.
    p=(745,716); q=(922,987)
    for i in range(8):
        x,y=lerp(p,q,i/7)
        g.line(f'stair-spindle-{i}',[(x,y),(x,y-79)],'#644a32',4)
        g.line(f'stair-spindle-light-{i}',[(x-1,y-2),(x-1,y-77)],'#d4aa75',1.2)
    g.line('sloping-handrail',[(744,636),(921,907)],'#503b2b',8,1)
    g.line('sloping-handrail-light',[(743,633),(920,904)],'#d0a16b',3,.9)
    for i,(x,y,h) in enumerate([(733,722,95),(784,737,95),(1046,822,95),(922,989,95)]):
        g.poly(f'newel-{i}',[(x-4,y),(x+4,y+2),(x+4,y-h),(x-4,y-h-2)],'#a57549',width=1.3)
        g.oval(f'newel-cap-{i}',x,y-h-3,6,4,'#c59c64',width=1)


def entrance(g):
    g.object('entry-details','门口的衣物、鞋与门垫')
    g.poly('coat-wall',[(1068,835),(1148,790),(1148,969),(1068,1014)],'#b48c6c')
    g.line('coat-hooks',[(1087,853),(1128,830)],'#5b4a38',4)
    for i,(x,y,c) in enumerate([(1090,855,'#b98452'),(1119,839,'#63736d')]):
        g.path(f'coat-{i}',[(x,y),(x-10,y+8),(x-15,y+42),(x-9,y+48),(x-5,y+28),
               (x-5,y+68),(x+10,y+64),(x+9,y+27),(x+15,y+43),(x+19,y+38),(x+9,y+3)],c,width=.9)
        g.line(f'coat-seam-{i}',[(x+2,y+14),(x+2,y+58)],'#665745',.8)
    g.poly('shoe-rack-top',[(1085,968),(1121,947),(1147,957),(1110,978)],'#9c7750')
    g.line('shoe-rack-leg-1',[(1088,970),(1088,995)],'#493f2e',4)
    g.line('shoe-rack-leg-2',[(1139,961),(1139,984)],'#493f2e',4)
    for i,(x,y) in enumerate([(1103,962),(1117,957),(1110,984),(1125,978)]):
        g.path(f'shoe-{i}',[(x-8,y),(x-3,y-7),(x+4,y-5),(x+9,y),(x+5,y+4),(x-6,y+4)],'#68533e',width=.7)
    g.poly('doormat',[(922,1033),(959,1013),(986,1023),(949,1045)],'#795c44')
    for i in range(7):
        g.line(f'mat-weave-{i}',[(927+i*4,1032-i*2.2),(949+i*4,1040-i*2.2)],'#b3916d',.8,.5)
    g.poly('letter',[(952,1009),(962,1003),(970,1008),(960,1014)],'#d7c5a0',width=.6)
    entry_person(g)
    # The open entry door is drawn last, as a foreground plane.
    g.object('front-door','向观者打开的红门')
    g.poly('jamb',[(988,876),(1061,833),(1061,1035),(988,1077)],'#303b33','#18271e',4)
    g.poly('red-door',[(997,887),(1045,859),(1045,1027),(997,1055)],'#994f3d','#d19769',3)
    g.poly('door-window',[(1004,897),(1038,877),(1038,935),(1004,955)],'#e1b083','#633e2d',3)
    g.poly('door-glow',[(1010,900),(1034,886),(1034,931),(1010,945)],'#f3cda1',None)
    g.poly('door-lower-panel',[(1006,978),(1037,960),(1037,1018),(1006,1036)],'#ac6250','#6c3e2f',2)
    g.line('door-handle',[(1032,954),(1044,947)],'#e2c493',3)
    g.line('door-edge-light',[(997,887),(997,1052)],'#d99971',1.2)


def finish(g):
    g.object('section-edges','楼板与墙体的剖面收口')
    for i,p in enumerate([[(34,550),(34,770)],[(201,607),(201,807)],[(365,659),(365,865)],
                          [(624,753),(624,958)],[(1302,681),(1302,906)]]):
        g.line(f'cut-{i}',p,'#18201a',8,1)
    g.line('bottom',[(32,770),(365,868),(624,962),(977,1090),(1303,905)],'#101914',8,1)
    g.line('slab-left',[(35,551),(366,665),(654,767)],'#26241d',5,1)
    g.line('slab-right',[(1048,820),(1301,678)],'#22271e',5,1)


def build():
    g=Drawing()
    architecture_lower(g)
    draw_lower_rooms(g)
    lower_shadows(g)
    upper_shell(g)
    bedroom(g)
    hall(g)
    living_fittings(g)
    sofa(g)
    living_table(g)
    stairs_and_rails(g)
    entrance(g)
    finish(g)
    return g.scene.data


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/studies/house-cutaway-v1')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    result=render_to(build(),args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out/'artwork.png'}; warnings: {result['warnings']}")
