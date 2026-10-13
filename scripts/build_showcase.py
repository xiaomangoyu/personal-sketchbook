#!/usr/bin/env python3
"""Build README images from real gallery renders and verify a local edit.

No image models are used. Originals are never resized in place.
"""
from __future__ import annotations
import argparse
import copy
import html
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
from render import render_to, validate

ROOT=Path(__file__).resolve().parents[1]
PAPER=(249,247,240)


def contained(source,size):
    result=Image.new('RGB',size,PAPER)
    im=source.convert('RGB').copy()
    im.thumbnail(size,Image.Resampling.LANCZOS)
    result.paste(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
    return result


def font(size):
    return ImageFont.load_default(size=size)


def save_jpeg(image,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    image.save(path,quality=91,optimize=True,subsampling=0)


def read_catalog():
    data=json.loads((ROOT/'examples/catalog.json').read_text())
    ids=set()
    for row in data['scenes']:
        if row['id'] in ids:
            raise ValueError('duplicate showcase id')
        ids.add(row['id'])
        for p in (ROOT/row['generator'],ROOT/'examples/gallery'/row['id']/'scene.json',ROOT/'examples/gallery'/row['id']/'artwork.png'):
            if not p.is_file():
                raise FileNotFoundError(p)
        validate(json.loads((ROOT/'examples/gallery'/row['id']/'scene.json').read_text()))
    return data['scenes']


def make_edit():
    source=ROOT/'examples/gallery/rainy-cafe'
    original=json.loads((source/'scene.json').read_text())
    updated=copy.deepcopy(original)
    umbrella=next((o for o in updated['objects'] if o['id']=='umbrella'),None)
    if umbrella is None:
        raise ValueError('rainy-cafe must have its umbrella in one named object')
    edited=[]
    for mark in umbrella['marks']:
        if mark['kind'] in ('wash','wax'):
            rgb=mark['color']
            lum=sum(rgb)/3
            mark['color']=[int(max(0,min(255,v))) for v in (42+lum*.20,91+lum*.29,143+lum*.32)]
            edited.append(mark['id'])
    if not edited:
        raise ValueError('umbrella has no pigment marks to recolor')
    out=ROOT/'examples/edits/blue-umbrella'
    after=render_to(updated,out,overwrite=(out/'manifest.json').exists())
    before=json.loads((source/'manifest.json').read_text())
    old={r['id']:r['sha256'] for r in before['layers']}
    new={r['id']:r['sha256'] for r in after['layers']}
    same=sorted(k for k in old if k!='umbrella' and old[k]==new[k])
    if len(same)!=len(old)-1 or old['umbrella']==new['umbrella']:
        raise AssertionError('edit isolation check failed')
    report={'changed_object':'umbrella','changed_marks':edited,'unchanged_layers':same,
            'unchanged_layer_count':len(same),'verified':True,
            'method':'SHA-256 comparison of exported object PNGs from the same renderer and runtime',
            'before':'examples/gallery/rainy-cafe/manifest.json',
            'after':'examples/edits/blue-umbrella/manifest.json'}
    (out/'comparison.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return out,report


def build():
    rows=read_catalog()
    cells=[]
    for row in rows:
        id=row['id']
        cells.append(f'<td width="50%"><a href="examples/gallery/{id}/artwork.png"><img src="docs/images/{id}-thumb.jpg" alt="{html.escape(row["title"])}" width="100%"></a><br><strong>{html.escape(row["title"])}</strong><br>{html.escape(row["medium"])}<p>{html.escape(row["prompt"])}</p><a href="examples/gallery/{id}/scene.json">场景 JSON</a> · <a href="{row["generator"]}">生成脚本</a></td>')
    gallery='<table>\n'+'\n'.join('<tr>\n'+cells[i]+'\n'+cells[i+1]+'\n</tr>' for i in range(0,len(cells),2))+'\n</table>'
    readme=ROOT/'README.md'
    body=readme.read_text()
    begin='<!-- GALLERY:START -->'
    end='<!-- GALLERY:END -->'
    if begin not in body or end not in body:
        raise ValueError('README gallery markers missing')
    head,tail=body.split(begin,1)
    _,tail=tail.split(end,1)
    readme.write_text(head+begin+'\n'+gallery+'\n'+end+tail)
    out=ROOT/'docs/images'
    out.mkdir(parents=True,exist_ok=True)
    for row in rows:
        with Image.open(ROOT/'examples/gallery'/row['id']/'artwork.png') as im:
            save_jpeg(contained(im,(720,560)),out/(row['id']+'-thumb.jpg'))
    heroes=[r for r in rows if r.get('hero')]
    if len(heroes)!=3:
        raise ValueError('cover requires exactly three hero artworks')
    cover=Image.new('RGB',(1800,720),PAPER)
    draw=ImageDraw.Draw(cover)
    for i,row in enumerate(heroes):
        with Image.open(ROOT/'examples/gallery'/row['id']/'artwork.png') as im:
            cover.paste(contained(im,(580,625)),(10+i*600,5))
        draw.text((30+i*600,655),row['en'],font=font(20),fill=(77,77,67))
        if i<2: draw.line((599+i*600,30,599+i*600,650),fill=(226,223,212),width=1)
    save_jpeg(cover,out/'cover.jpg')
    edit,report=make_edit()
    pair=Image.new('RGB',(1440,620),PAPER)
    d=ImageDraw.Draw(pair)
    for i,(p,label) in enumerate([(ROOT/'examples/gallery/rainy-cafe/artwork.png','Before'),(edit/'artwork.png','After - only the umbrella changed')]):
        with Image.open(p) as im: pair.paste(contained(im,(700,560)),(10+i*720,0))
        d.text((24+i*720,580),label,font=font(20),fill=(70,70,61))
    save_jpeg(pair,out/'local-edit.jpg')
    # Crops use explicit detail boxes or recorded object bounds, even in a clone without layers.
    crops=json.loads((ROOT/'examples/brush-crops.json').read_text())
    sheet=Image.new('RGB',(1500,350),PAPER)
    d=ImageDraw.Draw(sheet)
    for i,row in enumerate(crops):
        scene_root=ROOT/'examples/gallery'/row['scene']
        manifest=json.loads((scene_root/'manifest.json').read_text())
        record=next(r for r in manifest['layers'] if r['id']==row['object'])
        box=row.get('box') or record['bounds']
        if not box: raise ValueError(f'empty brush crop: {row}')
        with Image.open(scene_root/'artwork.png') as im: crop=im.crop(box)
        sheet.paste(contained(crop,(284,270)),(8+i*300,10))
        d.text((20+i*300,305),row['kind'],font=font(22),fill=(70,70,61))
    save_jpeg(sheet,out/'brushes.jpg')
    return {'scenes':len(rows),'unchanged_layers':report['unchanged_layer_count']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-scenes',action='store_true',help='rebuild the six bundled gallery scenes before making display assets')
    args=parser.parse_args()
    if args.render_scenes:
        rows=json.loads((ROOT/'examples/catalog.json').read_text())['scenes']
        for row in rows:
            subprocess.run([sys.executable,str(ROOT/row['generator']),'--out',str(ROOT/'examples/gallery'/row['id']),'--overwrite'],check=True)
    print(json.dumps(build(),ensure_ascii=False))
