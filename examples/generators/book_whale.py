#!/usr/bin/env python3
"""A humpback swims out of an old open book. Editable watercolor and pen scene."""
from pathlib import Path
import argparse
import math
import random
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from scene_tools import Scene, ellipse, curve, bezier, transform
from render import render_to


def build():
    s=Scene('旧书里游出一条鲸鱼',1400,1100,seed=314,paper=(248,246,233),grain=.45)
    rng=random.Random(82)
    navy=(38,65,88)
    teal=(46,140,143)
    def ink(o,id,p,color=navy,width=2,opacity=.76):
        return o.line(id,p,color,width=width,opacity=opacity,wobble=.52,pressure=.68,gaps=.022)
    def wash(o,id,p,c,opacity=.65,edge=.24):
        return o.fill(id,p,c,opacity=opacity,edge=edge,bleed=1.8,grain=.58)
    # An irregular, largely unpainted sky preserves the whale's long rising gesture.
    atmosphere=s.object('sea-air','从纸上漫出的淡蓝水色')
    wash(atmosphere,'halo',curve([(180,391),(221,259),(459,154),(705,138),(963,153),(1138,266),(1102,540),(869,678),(573,747),(258,695),(167,535)],closed=True),(156,199,194),.24,.06)
    wash(atmosphere,'left-wash',curve([(161,494),(236,373),(302,368),(286,513),(336,630),(525,675),(514,720),(273,687)],closed=True),(83,176,180),.22,.08)
    wash(atmosphere,'light',curve([(895,419),(1138,323),(1218,429),(1133,578),(1004,621),(926,568)],closed=True),(230,202,137),.18,.08)
    # Background currents return to the book's center instead of encircling an icon.
    currents=s.object('rising-currents','由书脊向上卷起的水流')
    wave=curve([(693,812),(656,736),(589,697),(602,641),(725,590),(801,527),(838,437),(886,420),(838,570),(745,643),(667,686),(720,755),(730,822)],closed=True)
    wash(currents,'main-ribbon',wave,(57,157,166),.49)
    wash(currents,'light-ribbon',curve([(701,799),(694,746),(625,694),(640,647),(769,585),(809,540),(755,619),(665,669),(659,692),(725,750),(726,800)],closed=True),(184,217,204),.82)
    for i in range(7):
        pts=curve([(697+i*3,811),(677+i*2,753),(609+i*6,693),(626+i*6,655),(754+i*5,591),(817+i*3,525)])
        ink(currents,f'water-ridge-{i}',pts,(58,127,144),.95+i%2*.35,.38)
    # A page has loosened into the current. Its corners share the same flow.
    flying_page=s.object('loose-page','被水流翻起的一页')
    page=curve([(884,640),(994,566),(1058,562),(1078,638),(1014,638),(920,693)],closed=True)
    wash(flying_page,'paper',page,(240,221,166),.91)
    ink(flying_page,'top',curve([(884,640),(994,566),(1058,562)]),(137,123,85),1.4,.69)
    ink(flying_page,'bottom',curve([(920,693),(1014,638),(1078,638)]),(137,123,85),1.4,.56)
    for i in range(6):
        ink(flying_page,f'page-line-{i}',curve([(928+i*3,636+i*5),(986+i*2,601+i*4),(1039+i*3,593+i*6)]),(118,141,126),.9,.48)
    # The head, back, slender peduncle and flukes form one connected silhouette.
    whale=s.object('whale-body','上游的座头鲸')
    body=curve([(319,392),(341,339),(409,288),(515,249),(633,236),(734,255),(833,281),(926,286),(991,257),(1047,185),(1130,164),(1202,160),(1166,211),(1119,242),(1090,260),(1133,279),(1182,323),(1118,326),(1066,309),(1024,285),(985,318),(923,390),(842,455),(756,505),(655,539),(551,548),(449,525),(372,486),(331,443)],closed=True)
    wash(whale,'ground',body,(123,172,181),1,.08)
    wash(whale,'blue',body,(43,95,130),.94)
    upper=curve([(327,394),(355,343),(414,292),(522,253),(636,241),(740,261),(836,287),(927,293),(991,264),(1048,188),(1131,169),(1195,165),(1122,235),(1086,259),(1137,286),(1169,317),(1106,319),(1024,280),(981,313),(921,354),(840,376),(752,381),(648,366),(548,348),(445,352),(368,383)],closed=True)
    wash(whale,'navy-back',upper,(30,57,88),.85)
    wash(whale,'teal-side',curve([(336,409),(396,371),(492,365),(591,383),(716,407),(852,410),(913,391),(844,449),(749,499),(650,529),(549,534),(449,513),(378,479)],closed=True),(61,146,157),.56)
    wash(whale,'head-highlight',curve([(342,390),(380,352),(446,328),(472,339),(419,367),(378,403)],closed=True),(110,180,183),.53)
    wash(whale,'tail-light',curve([(980,285),(1041,218),(1108,191),(1143,186),(1084,230),(1040,266),(999,301)],closed=True),(82,142,161),.54)
    ink(whale,'upper-contour',curve([(320,397),(341,344),(409,291),(515,251),(634,238),(734,256),(832,282),(926,288),(990,259)]),navy,2.9,.9)
    ink(whale,'tail-contour',curve([(991,257),(1047,185),(1130,164),(1202,160),(1166,211),(1119,242),(1090,260),(1133,279),(1182,323),(1118,326),(1066,309),(1024,285)]),navy,2.0,.9)
    ink(whale,'belly-contour',curve([(1024,285),(985,318),(923,390),(842,455),(756,505),(655,539),(551,548),(449,525),(372,486),(331,443),(319,411)]),navy,3.0,.85)
    ink(whale,'weighted-head',curve([(320,401),(332,356),(359,327),(400,296)]),(32,58,80),4.0,.74)
    ink(whale,'weighted-tail',curve([(1026,285),(1009,294),(985,320),(962,348)]),(35,60,83),3.8,.82)
    # Pale throat pleats taper toward the belly; the mouth is above their roots.
    throat=s.object('whale-throat','鲸腹浅色与喉沟')
    throatpoly=curve([(346,437),(414,461),(504,472),(593,465),(675,451),(715,468),(688,516),(633,537),(551,542),(453,520),(379,484)],closed=True)
    wash(throat,'cream-blue',throatpoly,(160,203,197),.8)
    wash(throat,'left-light',curve([(352,444),(412,463),(483,480),(493,515),(434,504),(379,479)],closed=True),(203,218,190),.57)
    for i in range(12):
        x=373+i*24
        y=453+18*math.sin(i/11*math.pi)
        end_y=542-abs(x+93-552)*.18
        ink(throat,f'pleat-{i}',bezier([(x,y),(x+12,y+29),(x+53,end_y-2),(x+93,end_y)]),(76,128,144),1.25,.65)
    throat.hatch('lower-shade',curve([(387,487),(445,512),(516,535),(607,539),(642,533),(608,522),(526,519),(447,501)],closed=True),(64,119,133),opacity=.29,width=.9,spacing=5,angle=56)
    mouth=s.object('whale-face','眼睛、嘴角与头部小结节')
    ink(mouth,'mouth',curve([(326,420),(374,442),(424,456),(486,464),(552,463),(615,451)]),(32,60,74),3.2,.92)
    ink(mouth,'lower-lip',curve([(335,437),(384,457),(429,468),(484,474)]),(54,92,104),1.35,.69)
    wash(mouth,'eye-socket',ellipse(405,414,13,8,rotate=-8),(40,69,85),.75)
    wash(mouth,'eye',ellipse(405,414,6.2,5.7),(20,43,58),1)
    wash(mouth,'eye-light',ellipse(404,412,1.9,1.6),(235,230,195),1)
    ink(mouth,'eye-crease',curve([(391,404),(405,400),(419,404)]),(68,119,130),1.6,.66)
    for i,(x,y) in enumerate([(340,387),(358,372),(377,360),(398,351),(419,344),(440,341),(341,432),(358,440)]):
        wash(mouth,f'tubercle-{i}',ellipse(x,y,5.2,3.7,rotate=-22),(131,177,173),.82)
        ink(mouth,f'tubercle-line-{i}',ellipse(x,y,5.2,3.7,rotate=-22,start=15,end=170,n=12),(31,69,94),.75,.63)
    # Dorsal fin lies at the back third and remains small relative to the flipper.
    dorsal=s.object('dorsal-fin','小背鳍')
    dp=curve([(809,277),(829,255),(851,237),(856,263),(884,285)],closed=True)
    wash(dorsal,'fin',dp,(39,69,99),.98)
    ink(dorsal,'top',curve([(809,277),(829,255),(851,237),(856,263),(884,285)]),navy,2.1,.83)
    # Near flipper bends down over the water ribbon, physically linking the two scales.
    flipper=s.object('whale-flipper','长胸鳍')
    fp=curve([(657,444),(688,458),(701,482),(687,526),(645,571),(601,616),(546,668),(520,671),(536,633),(563,588),(583,534),(612,482)],closed=True)
    wash(flipper,'ground',fp,(94,151,158),1,.1)
    wash(flipper,'navy',fp,(37,94,123),.92)
    wash(flipper,'lit-edge',curve([(663,448),(637,481),(608,540),(585,592),(549,646),(526,667),(547,629),(572,577),(589,531),(616,481)],closed=True),(170,201,183),.91)
    ink(flipper,'dark-edge',curve([(674,449),(695,470),(701,489),(683,532),(646,571),(601,616),(546,668),(521,672)]),navy,2.6,.88)
    ink(flipper,'light-edge',curve([(521,670),(536,633),(563,588),(583,534),(612,482),(651,447)]),(56,96,109),1.7,.75)
    flipper.hatch('fin-shadow',curve([(682,479),(694,494),(674,536),(627,587),(554,657),(589,606),(645,544)],closed=True),(34,76,101),opacity=.45,width=1.1,spacing=5.5,angle=128)
    for i in range(10):
        x=596-i*6; y=529+i*11
        ink(flipper,f'ridge-{i}',[(x,y),(x+10,y+3)],(51,96,120),1,.55)
    # Sparse skin marks align along the swimming direction.
    skin=s.object('whale-skin','沿身体方向的细痕')
    for i in range(27):
        x=rng.uniform(440,865); y=305+.13*(x-440)+rng.uniform(-22,26)
        ink(skin,f'skin-line-{i}',curve([(x,y),(x+12,y-1),(x+27,y+2)]),(126,180,184),.7,.38)
    for i,(x,y) in enumerate([(394,475),(421,491),(463,506),(502,518),(546,526)]):
        ink(skin,f'barnacle-{i}',ellipse(x,y,3+i%2,2,rotate=15,n=12),(85,128,132),.8,.68)
    # The book has thickness, a red cloth cover, a central valley and two bent stacks.
    ground=s.object('book-shadow','书本投影')
    wash(ground,'cast',ellipse(744,960,463,54,rotate=-5,rough=.025,seed=4),(84,119,123),.19,.08)
    cover=s.object('book-cover','旧书的朱红布面封皮')
    coverpoly=curve([(254,782),(562,707),(698,788),(1099,692),(1175,838),(1158,876),(744,1000),(664,991),(279,929)],closed=True)
    wash(cover,'cloth-ground',coverpoly,(185,90,70),1,.09)
    wash(cover,'cloth-color',coverpoly,(164,69,58),.85)
    wash(cover,'lower-spine',[(657,946),(725,959),(748,998),(665,990)],(111,60,52),.75)
    ink(cover,'cover-edge',curve([(254,782),(279,929),(664,991),(744,1000),(1158,876),(1175,838)]),(89,66,59),2.7,.81)
    ink(cover,'red-rim',curve([(277,914),(663,977),(744,986),(1156,863)]),(204,128,88),2.4,.67)
    # Separate the lower stack so curved sheets can be seen in front of the cover.
    stack=s.object('page-stack','书页厚度')
    leftstack=[(278,793),(604,828),(707,920),(699,975),(665,975),(291,916)]
    rightstack=[(710,910),(837,854),(1146,817),(1154,860),(744,977),(700,975)]
    for id,p in [('left',leftstack),('right',rightstack)]:
        wash(stack,id+'-base',p,(220,196,137),.98)
    for i in range(7):
        ink(stack,f'left-layer-{i}',curve([(288,899+i*2.5),(598,939+i*2),(665,956+i*2),(699,955+i*2)]),(136,125,84),.7,.55)
        ink(stack,f'right-layer-{i}',curve([(710,955+i*2),(748,959+i*2),(923,910+i*2),(1150,840+i*2.7)]),(136,125,84),.8,.56)
    pages=s.object('open-pages','张开的左右书页')
    lp=curve([(278,783),(387,754),(557,718),(605,731),(698,805),(705,939),(662,904),(608,879),(452,885),(291,902)],closed=True)
    rp=curve([(698,805),(772,760),(919,732),(1097,701),(1149,823),(1038,848),(851,889),(769,916),(705,939)],closed=True)
    for id,p in [('left',lp),('right',rp)]:
        for k in range(2): wash(pages,id+f'-paper-{k}',p,(246,233,189),1,.06)
    wash(pages,'left-turn',curve([(552,720),(605,733),(698,805),(705,939),(671,911),(640,850),(615,786)],closed=True),(185,170,118),.35)
    wash(pages,'spine-shadow',curve([(697,806),(721,788),(738,815),(727,887),(705,939),(689,910)],closed=True),(151,157,130),.36)
    pages.hatch('spine-hatching',curve([(683,804),(701,809),(704,934),(682,912),(670,868)],closed=True),(130,132,103),opacity=.24,width=.8,spacing=5,angle=78)
    ink(pages,'left-top',curve([(278,783),(390,753),(557,718),(606,733),(698,805)]),(130,115,79),1.7,.73)
    ink(pages,'left-bottom',curve([(292,902),(451,885),(608,879),(662,904),(705,939)]),(125,111,77),1.8,.7)
    ink(pages,'right-top',curve([(698,805),(772,760),(919,732),(1097,701),(1149,823)]),(127,115,79),1.6,.64)
    ink(pages,'right-bottom',curve([(1149,823),(1038,848),(851,889),(769,916),(705,939)]),(108,110,84),2.2,.73)
    ink(pages,'spine',curve([(698,805),(703,845),(699,894),(705,939)]),(116,113,79),2.1,.81)
    # Marks suggest lines on a page without claiming to render legible handwriting.
    page_lines=s.object('page-lines','书页上的行迹')
    for i in range(9):
        y=799+i*9
        endx=599+i*4
        pts=curve([(327,y),(442,y-23),(549,y-41),(endx,y-32)],steps=15)
        # Unequal short runs suggest old type without invented words or faux handwriting.
        for j,(a,b) in enumerate([(0,9),(11,24),(26,38 if i%3 else 32)]):
            ink(page_lines,f'left-row-{i}-run-{j}',pts[a:b],(130,138,110),.85,.47)
    for i in range(10):
        pts=curve([(770,810+i*9),(867,785+i*8),(965,767+i*8),(1093,743+i*8)],steps=15)
        for j,(a,b) in enumerate([(0,10),(12,23),(25,35),(37,46 if i%4 else 41)]):
            ink(page_lines,f'right-row-{i}-run-{j}',pts[a:b],(111,133,114),.9,.47)
    # A loose bookmark helps explain the old book without any automatic signature.
    bookmark=s.object('bookmark','从书脊垂出的布书签')
    bp=curve([(713,928),(732,935),(750,1025),(732,1012),(719,1034),(705,971)],closed=True)
    wash(bookmark,'red',bp,(182,65,51),.9)
    ink(bookmark,'edge',curve([(713,935),(708,968),(719,1034),(732,1012),(750,1025),(734,943)]),(123,69,53),1.4,.7)
    # A wave overlaps the valley to join the main current to the pages.
    emergence=s.object('water-at-spine','从书页升起的水花')
    ep=curve([(649,793),(626,755),(638,726),(661,743),(698,786),(719,803),(752,788),(797,777),(806,793),(770,818),(729,837),(697,846),(662,827)],closed=True)
    wash(emergence,'water',ep,(82,167,170),.58)
    for i,pts in enumerate([[(650,786),(665,811),(697,827),(726,824),(769,801)],[(662,763),(688,794),(716,808),(738,808)],[(690,851),(710,857),(737,849)],[(745,835),(783,824),(810,809)]]):
        ink(emergence,f'crest-{i}',curve(pts),(60,126,146),1.6,.61)
    # Small gold fish follow the current; unequal sizes reinforce distance.
    for index,(x,y,size,angle) in enumerate([(910,498,21,-30),(1011,452,15,-29),(963,531,11,-28)]):
        fish=s.object(f'gold-fish-{index}','随水流跃起的小鱼')
        shape=curve([(-size,0),(-size*.2,-size*.38),(size*.72,0),(-size*.2,size*.36)],closed=True)
        shape=transform(shape,translate=(x,y),rotate=angle)
        tail=transform([(-size*.82,0),(-size*1.5,-size*.43),(-size*1.4,size*.43)],translate=(x,y),rotate=angle)
        wash(fish,'body',shape,(214,152,57),.95)
        wash(fish,'tail',tail,(204,119,41),.93)
        ink(fish,'back',shape[:len(shape)//2],(149,106,46),1,.63)
    bubbles=s.object('water-bubbles','少量水泡')
    for i,(x,y,r) in enumerate([(239,439,8),(232,403,4),(255,365,5),(890,671,7),(936,620,3),(794,704,5),(833,650,3),(959,256,6)]):
        ink(bubbles,f'ring-{i}',ellipse(x,y,r,r*1.07,start=24,end=335,n=28),(105,161,159),1,.47)
    return s.data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'examples/gallery/book-whale')
    parser.add_argument('--overwrite',action='store_true',help='Replace an existing renderer output during deliberate iteration.')
    args=parser.parse_args()
    manifest=render_to(build(),args.out,overwrite=args.overwrite)
    print(f"Rendered {args.out / 'artwork.png'} ({len(manifest['layers'])} editable objects)")


if __name__=='__main__': main()
