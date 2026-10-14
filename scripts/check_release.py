#!/usr/bin/env python3
"""Check gallery reproducibility, published links and publication file boundaries."""
from __future__ import annotations
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from urllib.parse import unquote
from PIL import Image
from render import draw_scene,validate

ROOT=Path(__file__).resolve().parents[1]


def check(render=False):
    failures=[]
    counts={'scenes':0,'edits':0,'studies':0,'links':0,'replayed':0}
    rows=json.loads((ROOT/'examples/catalog.json').read_text())['scenes']
    targets=[(r['id'],ROOT/'examples/gallery'/r['id']) for r in rows]
    targets.append(('blue-umbrella',ROOT/'examples/edits/blue-umbrella'))
    targets.extend((str(p.parent.relative_to(ROOT)),p.parent)
                   for p in sorted((ROOT/'examples/studies').rglob('scene.json')))
    for name,base in targets:
        scene=validate(json.loads((base/'scene.json').read_text()))
        manifest=json.loads((base/'manifest.json').read_text())
        if hashlib.sha256((base/'artwork.png').read_bytes()).hexdigest()!=manifest['artwork_sha256']:
            failures.append(name+': artwork hash differs from manifest')
        if manifest['warnings']: failures.append(name+': '+str(manifest['warnings']))
        category='studies' if base.is_relative_to(ROOT/'examples/studies') else ('edits' if name=='blue-umbrella' else 'scenes')
        counts[category]+=1
        if render:
            image,paper,layers=draw_scene(scene)
            expected=Image.open(base/'artwork.png').convert('RGBA')
            if image.tobytes()!=expected.tobytes(): failures.append(name+': replay differs from artwork')
            merged=paper.copy()
            recorded={item['id']:item['sha256'] for item in manifest['layers']}
            if set(recorded)!={obj['id'] for obj,_ in layers}: failures.append(name+': layer IDs differ from manifest')
            for obj,layer in layers:
                merged=Image.alpha_composite(merged,layer)
                stream=BytesIO()
                layer.save(stream,format='PNG')
                if hashlib.sha256(stream.getvalue()).hexdigest()!=recorded.get(obj['id']):
                    failures.append(name+': replay layer hash differs: '+obj['id'])
            if merged.tobytes()!=image.tobytes(): failures.append(name+': layers do not recompose')
            counts['replayed']+=1
    for row in rows:
        if not (ROOT/row['generator']).is_file(): failures.append(row['id']+': missing generator')
        if not (ROOT/'docs/images'/f"{row['id']}-thumb.jpg").is_file(): failures.append(row['id']+': missing thumbnail')
    for path in [ROOT/'README.md',ROOT/'SKILL.md',*sorted((ROOT/'references').glob('*.md'))]:
        text=path.read_text()
        links=re.findall(r'(?:src|href)=["\']([^"\']+)["\']',text)+re.findall(r'\]\(([^)]+)\)',text)
        for value in links:
            value=value.strip('<>')
            if value.startswith(('http:','https:','#','mailto:')): continue
            value=unquote(value.split('#')[0])
            if not value: continue
            counts['links']+=1
            if not (path.parent/value).exists(): failures.append(f'{path.relative_to(ROOT)}: missing {value}')
    # Only repository-bound deliverables; external review folders and installed skills are not part of publication.
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(x in p.parts for x in ('.git','.venv','__pycache__','.review','build','output','layers')): continue
        if p.name.startswith('.env') or p.suffix in ('.pem','.key','.p12'): failures.append('unexpected sensitive file: '+str(p.relative_to(ROOT)))
        if p.suffix in ('.py','.md','.json','.yaml','.yml','.txt'):
            txt=p.read_text(encoding='utf-8')
            if re.search(r'/(?:Users/[^/\s]+|private/tmp)/',txt): failures.append('local absolute path in '+str(p.relative_to(ROOT)))
    comparison=json.loads((ROOT/'examples/edits/blue-umbrella/comparison.json').read_text())
    before=json.loads((ROOT/comparison['before']).read_text())
    after=json.loads((ROOT/comparison['after']).read_text())
    old={l['id']:l['sha256'] for l in before['layers']}
    new={l['id']:l['sha256'] for l in after['layers']}
    unchanged=[k for k in old if k!='umbrella' and old[k]==new.get(k)]
    if set(old)!=set(new) or len(unchanged)!=len(old)-1 or old.get('umbrella')==new.get('umbrella'):
        failures.append('local edit isolation failed')
    original=json.loads((ROOT/comparison['before']).with_name('scene.json').read_text())
    edited=json.loads((ROOT/comparison['after']).with_name('scene.json').read_text())
    originals={o['id']:o for o in original['objects']}
    edits={o['id']:o for o in edited['objects']}
    if any(originals[k]!=edits.get(k) for k in originals if k!='umbrella'):
        failures.append('unrelated scene objects changed')
    if {k:v for k,v in original.items() if k!='objects'}!={k:v for k,v in edited.items() if k!='objects'}:
        failures.append('scene settings changed in local edit')
    if failures: raise ValueError('\n'.join(failures))
    return counts


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--render',action='store_true',help='replay gallery, edit and studies; recompose and verify layer hashes')
    args=p.parse_args()
    try: print(json.dumps(check(args.render),ensure_ascii=False))
    except (ValueError,OSError,KeyError) as e: p.exit(1,str(e)+'\n')
