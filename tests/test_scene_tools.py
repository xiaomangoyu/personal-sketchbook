import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scene_tools import Scene,bezier,clone_object,curve,ellipse,transform
from render import draw_scene,validate


class SceneToolsTests(unittest.TestCase):
    def test_transform_rotation_origin_and_scale(self):
        self.assertEqual(transform([[12,10]],origin=(10,10),scale=2,rotate=90,translate=(3,-2)),[[13.0,12.0]])
    def test_bezier_endpoints_and_convex_bounds(self):
        controls=[[0,0],[0,100],[100,100],[100,0]]
        pts=bezier(controls)
        self.assertEqual(pts[0],controls[0])
        self.assertEqual(pts[-1],controls[-1])
        self.assertTrue(all(0<=x<=100 and 0<=y<=100 for x,y in pts))
    def test_organic_ellipse_closed_and_repeatable(self):
        a=ellipse(100,100,60,30,rough=.04,seed=5)
        self.assertEqual(a,ellipse(100,100,60,30,rough=.04,seed=5))
        self.assertEqual(a[0],a[-1])
        self.assertNotEqual(a,ellipse(100,100,60,30,rough=.04,seed=6))
    def test_curve_has_correct_endpoints(self):
        pts=[[5,6],[10,20],[45,8]]
        self.assertEqual(curve(pts)[0],pts[0])
        self.assertEqual(curve(pts)[-1],pts[-1])
        self.assertEqual(curve(pts,closed=True)[0],curve(pts,closed=True)[-1])
    def test_clone_does_not_mutate_source_and_rotates_brush(self):
        s=Scene('copy',160,160)
        o=s.object('box').fill('paint',[[20,20],[40,20],[40,40]],(90,120,50),kind='wax',direction=0)
        before=copy.deepcopy(o.value)
        new=clone_object(o.value,'box2',rotate=90,origin=(20,20))
        self.assertEqual(o.value,before)
        self.assertEqual(new['marks'][0]['direction'],90)
        self.assertEqual(new['marks'][0]['polygon'][1],[20,40])
        new['marks'][0]['color'][0]=255
        self.assertEqual(o.value['marks'][0]['color'][0],90)
    def test_clone_scales_and_rotates_implicit_render_defaults(self):
        marks=[]
        for kind in ('ink','pencil','wax','wash','hatch'):
            key='points' if kind in ('ink','pencil') else 'polygon'
            marks.append({'id':kind,'kind':kind,key:[[20,20],[40,20],[40,40]]})
        source={'id':'original','marks':marks}
        before=copy.deepcopy(source)
        cloned=clone_object(source,'scaled',scale=2,rotate=90)
        by_kind={m['kind']:m for m in cloned['marks']}
        for kind in ('ink','pencil'):
            self.assertAlmostEqual(by_kind[kind]['width'],3.6)
            self.assertAlmostEqual(by_kind[kind]['wobble'],1.4)
        self.assertEqual(by_kind['wash']['bleed'],4)
        self.assertEqual(by_kind['hatch']['width'],2)
        self.assertEqual(by_kind['hatch']['spacing'],16)
        self.assertAlmostEqual(by_kind['wax']['direction'],90)
        self.assertAlmostEqual(by_kind['hatch']['angle'],150)
        self.assertEqual(source,before)
        scene=Scene('defaults',160,160)
        scene.data['objects']=[cloned]
        validate(scene.data)  # No parameters leak onto unsupported brush kinds.
    def test_clone_implicit_defaults_match_explicit_defaults_in_pixels(self):
        defaults={'ink':{'width':1.8,'wobble':.7},
                  'pencil':{'width':1.8,'wobble':.7},
                  'wax':{'direction':0},'wash':{'bleed':2},
                  'hatch':{'width':1,'spacing':8,'angle':60}}
        marks=[]
        for i,kind in enumerate(defaults):
            key='points' if kind in ('ink','pencil') else 'polygon'
            x=18+i*23
            marks.append({'id':kind,'kind':kind,key:[[x,45],[x+18,48],[x+13,79]],
                          'color':[60+20*i,100,70],'opacity':.8})
        implicit={'id':'source','translate':[3,2],'marks':marks}
        explicit=copy.deepcopy(implicit)
        for mark in explicit['marks']:
            mark.update(defaults[mark['kind']])
        actual=Scene('defaults',180,160)
        expected=Scene('defaults',180,160)
        options=dict(scale=(1.25,.8),rotate=25,origin=(70,70),translate=(5,3))
        actual.data['objects']=[clone_object(implicit,'copy',**options)]
        expected.data['objects']=[clone_object(explicit,'copy',**options)]
        self.assertEqual(draw_scene(actual.data)[0].tobytes(),
                         draw_scene(expected.data)[0].tobytes())
    def test_clone_reflects_default_brush_directions(self):
        source={'id':'original','marks':[
            {'id':kind,'kind':kind,'polygon':[[20,20],[40,20],[40,40]]}
            for kind in ('wax','hatch')]}
        cloned=clone_object(source,'reflected',scale=(-1,1),origin=(40,40))
        self.assertAlmostEqual(cloned['marks'][0]['direction'],-180)
        self.assertAlmostEqual(cloned['marks'][1]['angle'],120)
        self.assertEqual(cloned['marks'][0]['polygon'][0],[60,20])
    def test_saved_scene_renders_existing_schema(self):
        s=Scene('leaf',160,160)
        s.object('leaf').fill('body',ellipse(80,80,30,60),(80,140,60)).line('vein',[[80,30],[80,135]],width=1.6)
        with tempfile.TemporaryDirectory() as d:
            p=s.save(Path(d)/'scene.json')
            saved=json.loads(p.read_text())
            self.assertEqual(saved['version'],1)
            validate(saved)

if __name__=='__main__': unittest.main()
