"""A tent leans into a mountain breeze, under broad wax skies."""
from pathlib import Path
import argparse
import math
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, ellipse, curve, bezier, transform
from render import render_to


def wax(o,id,p,c,opacity=.8,direction=0,density=1.05):
    if opacity >= .75:
        under=tuple(round(v*.57+paper*.43) for v,paper in zip(c,(247,241,221)))
        o.fill(id+'-rubbed',p,under,kind='wax',opacity=.97,direction=direction,density=3.8,grain=.025)
    o.fill(id,p,c,kind='wax',opacity=opacity,direction=direction,density=density,grain=.59)


def pencil(o,id,p,c=(58,76,67),width=2,opacity=.67,**kw):
    o.line(id,p,c,kind='pencil',width=width,opacity=opacity,pressure=.69,wobble=.65,gaps=.013,**kw)


def build_scene():
    s=Scene('风把山顶帐篷吹歪了一点',1440,1000,seed=601,paper=(247,241,221),grain=.56)
    sky=s.object('sky','大片清蓝色的天空')
    sky.fill('soft-blue',[(50,58),(1371,66),(1377,700),(69,701)],(151,197,203),opacity=.21,edge=.01,bleed=8,grain=.3)
    # Broken-edged wax rubbings leave uncoloured paper at the edges.
    wax(sky,'upper-sky',[(73,101),(205,77),(403,81),(572,71),(754,83),(984,70),(1125,86),
         (1329,67),(1358,101),(1341,208),(1370,250),(1316,281),(1176,297),(1101,281),
         (977,303),(826,290),(721,314),(607,332),(498,310),(337,325),(213,310),(112,344),
         (82,297),(100,250),(71,206)],(92,161,177),.57,4,1.05)
    wax(sky,'right-blue',[(810,248),(1027,257),(1191,231),(1357,240),(1348,324),
         (1371,364),(1317,425),(1258,430),(1109,449),(999,440),(867,469),(809,391)],(113,174,184),.14,0,.80)
    clouds=s.object('wind-clouds','被风拉长的云')
    clouds.fill('cloud-under',curve([(149,237),(208,212),(270,220),(348,179),(391,182),(427,204),(482,201),(545,224),(659,235),(529,258),(367,266),(229,260)],closed=True),(254,249,230),opacity=.84,edge=.02,bleed=2)
    wax(clouds,'cloud-top',curve([(175,230),(237,215),(278,224),(347,185),(386,184),(425,210),(483,207),(549,230),(469,236),(295,242)],closed=True),(255,250,232),.93,4,1.4)
    wax(clouds,'cloud-tail',curve([(656,317),(731,302),(794,307),(869,275),(936,285),(982,301),(1092,316),(1020,331),(833,333),(719,330)],closed=True),(251,248,225),.93,-2,1.3)
    pencil(clouds,'underside',curve([(243,270),(394,274),(572,258)]),(145,180,176),1.3,.34)
    wax(clouds,'thin-streak',curve([(193,358),(345,347),(486,353),(423,364),(261,369)],closed=True),(248,245,224),.72,0,1.25)
    distant=s.object('distant-ridge','层叠的远山')
    ridge=[(55,660),(111,634),(169,585),(220,604),(305,546),(327,521),(354,528),(377,552),(412,538),(450,496),(491,524),(522,553),(551,571),(601,549),(670,588),(701,601),(767,553),(809,520),(830,528),(857,552),(887,564),(960,523),(996,505),(1037,521),(1065,551),(1102,568),(1178,552),(1264,597),(1373,652),(1370,768),(58,767)]
    wax(distant,'blue-ridge',ridge,(129,162,154),.78,18,.97)
    wax(distant,'blue-fold',[(168,587),(222,606),(326,524),(282,622),(202,661),(101,687)],(116,147,144),.37,68,.86)
    wax(distant,'snow',[(374,550),(450,499),(491,530),(465,525),(443,519),(431,539),(417,531),(402,558)],(242,237,212),.76,18,1.04)
    mid=s.object('near-ridge','近处松绿山脊')
    shape=curve([(55,746),(165,719),(270,665),(387,663),(468,690),(608,645),(705,670),(817,630),(1008,683),(1161,655),(1373,696)])+[(1373,846),(55,847)]
    wax(mid,'ridge',shape,(93,132,112),.81,15,1.05)
    wax(mid,'ridge-light',curve([(164,718),(270,669),(391,667),(489,701),(326,729),(210,752)],closed=True),(147,165,113),.65,17,1.1)
    wax(mid,'ridge-dark',curve([(414,706),(608,649),(706,675),(628,738),(501,753)],closed=True),(64,111,96),.57,55,.85)
    pencil(mid,'ridge-edge',curve([(57,746),(165,719),(270,665),(387,663)]),(95,118,94),1.5,.35)
    ground=s.object('summit','迎风的山顶草地')
    hill=curve([(56,859),(201,814),(347,809),(500,777),(633,800),(782,751),(946,750),(1118,763),(1377,807),(1374,944),(1066,957),(815,940),(564,956),(254,948),(64,928)],closed=True)
    wax(ground,'main',hill,(171,174,91),.80,6,1.2)
    wax(ground,'left-meadow',curve([(69,862),(239,817),(376,818),(523,799),(613,826),(390,901),(97,918)],closed=True),(190,183,105),.51,19,1.02)
    wax(ground,'cool-grass',curve([(635,844),(800,788),(1021,795),(1160,796),(1369,832),(1371,914),(1125,923),(900,905),(769,934)],closed=True),(104,140,89),.55,12,1.0)
    wax(ground,'foreground-edge',curve([(59,911),(345,920),(532,908),(733,936),(982,916),(1265,916),(1374,929),(1330,950),(950,967),(717,957),(331,962),(105,942)],closed=True),(99,128,76),.49,22,.85)
    path=s.object('footpath','爬上山顶的小路')
    wax(path,'trail',curve([(192,942),(351,884),(444,872),(557,835),(633,820),(616,844),(506,891),(418,905),(322,952)],closed=True),(228,211,155),.64,-25,1.2)
    pencil(path,'trail-edge',curve([(210,937),(353,883),(442,873),(551,839)]),(160,153,104),1.5,.30)
    shadow=s.object('tent-shadow','帐篷压住的草与投影')
    wax(shadow,'shadow',curve([(762,809),(1041,785),(1301,773),(1371,830),(1248,862),(1006,864),(825,843)],closed=True),(46,86,64),.46,7,1.03)
    # Peak leans right; both ridge and guy lines connect to real corners.
    tent=s.object('tent','被风推向一侧的橘红帐篷')
    front=[(766,809),(986,510),(1131,807)]
    side=[(986,510),(1190,557),(1311,785),(1131,807)]
    tent.fill('front-under',front,(232,138,66),opacity=.6,edge=.03,bleed=.5)
    wax(tent,'front-canvas',front,(238,148,68),.94,53,1.24)
    tent.fill('side-under',side,(197,82,42),opacity=.65,edge=.02,bleed=.3)
    wax(tent,'side-canvas',side,(210,88,44),.96,74,1.26)
    wax(tent,'ridge-light',[(986,510),(1190,557),(1201,576),(991,534)],(244,166,77),.88,12,1.1)
    wax(tent,'bottom-fold',[(1131,779),(1294,758),(1311,785),(1131,807)],(157,67,38),.79,-8,.99)
    # The opening hangs from the peak; no impossible floating triangular centre.
    door=[(978,556),(840,805),(1069,804)]
    wax(tent,'door-shadow',door,(42,72,58),.97,79,1.35)
    wax(tent,'door-inner',[(977,587),(897,757),(1036,755)],(34,55,48),.86,80,1.2)
    wax(tent,'rolled-left-flap',[(978,556),(878,780),(840,805),(817,799)],(247,183,93),.95,60,1.25)
    wax(tent,'right-flap',[(978,556),(1070,804),(1101,803),(1001,585)],(208,105,48),.84,78,1.10)
    pencil(tent,'front-pole',[(766,809),(986,510),(1131,807)],(87,69,43),3.8,.89)
    pencil(tent,'back-pole',[(1190,557),(1311,785)],(89,54,39),3,.78)
    pencil(tent,'ridge',[(986,510),(1190,557)],(128,70,41),2.9,.80)
    pencil(tent,'threshold',[(840,805),(956,814),(1069,804)],(36,61,46),3,.88)
    pencil(tent,'door-zip',[(978,556),(1001,632),(1038,731),(1069,804)],(236,183,110),1.8,.71)
    pencil(tent,'side-fold-one',curve([(1019,573),(1141,688),(1252,746)]),(158,69,40),2.3,.62)
    pencil(tent,'side-fold-two',curve([(1294,770),(1228,720),(1166,700)]),(148,65,39),2.7,.71)
    pencil(tent,'front-fold',curve([(897,669),(838,758),(800,794)]),(176,104,53),2,.53)
    ropes=s.object('guy-lines','绷紧的风绳和地钉')
    for i,(a,b) in enumerate([((986,511),(658,848)),((1190,557),(1366,831)),((774,800),(698,883)),((1300,781),(1362,865))]):
        pencil(ropes,'rope-'+str(i),[a,b],(101,102,67),1.65,.8)
        pencil(ropes,'peg-'+str(i),[(b[0]-6,b[1]-4),(b[0]+5,b[1]+9),(b[0]+12,b[1]+7)],(58,73,55),3.1,.82)
    # A scarf on the ridge lifts in the same direction as grass and clouds.
    scarf=s.object('wind-ribbon','山风中翘起的一小条布')
    wax(scarf,'cloth',curve([(986,519),(1013,500),(1048,501),(1086,489),(1103,494),(1073,510),(1041,522),(1010,518)],closed=True),(235,196,88),.95,0,1.24)
    pencil(scarf,'tie',[(986,519),(980,501)],(106,90,45),1.8,.7)
    # A rolled blanket lies inside and a small thermos signals a quiet weekend.
    blanket=s.object('blanket','门口卷起的毯子')
    wax(blanket,'body',curve([(889,784),(946,772),(991,779),(996,795),(908,811),(890,804)],closed=True),(97,141,138),.88,4,1.2)
    pencil(blanket,'roll',ellipse(900,797,12,15,rotate=10,start=50,end=385,n=30),(43,88,81),2,.67)
    for i in range(3):
        pencil(blanket,'stripe-'+str(i),[(932+i*12,779),(936+i*12,804)],(178,190,151),2.4,.7)
    weekend=s.object('weekend-things','草地上的保温瓶与素描本')
    bottle=curve([(734,820),(734,769),(739,763),(754,763),(760,770),(763,819),(755,827),(742,827)],closed=True)
    wax(weekend,'flask',bottle,(61,107,112),.95,88,1.2)
    wax(weekend,'lid',[(739,753),(752,752),(755,764),(737,765)],(63,69,56),.97,0,1.3)
    pencil(weekend,'flask-highlight',[(742,775),(744,812)],(208,211,166),2.5,.7)
    bookleft=[(573,874),(620,855),(659,867),(623,891)]
    bookright=[(620,855),(666,835),(705,850),(659,867),(623,891)]
    wax(weekend,'book-cover',[(568,875),(666,832),(711,850),(624,898)],(89,112,89),.9,-20,1.05)
    weekend.fill('pages-left',bookleft,(250,239,209),opacity=.96,edge=.04,bleed=.1)
    weekend.fill('pages-right',bookright,(241,226,189),opacity=.94,edge=.04,bleed=.1)
    pencil(weekend,'spine',[(620,855),(659,867),(623,891)],(152,144,103),1.2,.65)
    for i in range(3):
        pencil(weekend,'sketch-'+str(i),[(644+i*7,858-i*3),(656+i*6,850-i*3),(669+i*7,854-i*3)],(130,141,107),.8,.38)
    pencil(weekend,'pencil',[(697,876),(737,854)],(165,121,51),4,.86)
    grass=s.object('wind-grasses','统一朝向的草茎')
    rng=random.Random(119)
    # Sparse groups with varying height; no uniform grass border.
    for cluster,(cx,cy,count) in enumerate([(139,889,9),(432,941,10),(782,921,8),(1216,916,11),(1337,867,6),(525,809,5)]):
        for n in range(count):
            x=cx+rng.uniform(-37,37); y=cy+rng.uniform(-10,10)
            h=rng.uniform(17,49); lean=rng.uniform(12,31)
            pencil(grass,f'blade-{cluster}-{n}',bezier([(x,y),(x+3,y-h*.65),(x+lean*.7,y-h),(x+lean,y-h*.83)],16),
                   (88+rng.randrange(22),115+rng.randrange(17),61),rng.uniform(1.2,2.5),rng.uniform(.45,.75))
    birds=s.object('distant-birds','山谷上空的两只小鸟')
    pencil(birds,'bird-one',curve([(572,431),(580,426),(589,433),(598,429),(608,432)]),(78,110,104),2,.62)
    pencil(birds,'bird-two',curve([(633,453),(640,449),(647,454),(654,451),(660,454)]),(92,118,110),1.7,.49)
    return s


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=ROOT/'examples/gallery/windy-camp')
    p.add_argument('--overwrite',action='store_true')
    args=p.parse_args()
    result=render_to(build_scene().data,args.out,overwrite=args.overwrite)
    print(args.out.resolve()/'artwork.png')
    print('Objects:',len(result['layers']),'Warnings:',result['warnings'])


if __name__=='__main__':
    main()
