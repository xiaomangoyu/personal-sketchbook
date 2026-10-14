"""Optional fades preserve brush texture, placement and older scenes."""
import copy
import hashlib
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
from test_pencil_case_media import upstream_scene, adapter, render
from scene_tools import clone_object, transform


class GradientTests(unittest.TestCase):
    def test_existing_upstream_pixels_unchanged(self):
        self.assertEqual(hashlib.sha256(render.draw_scene(upstream_scene())[0].tobytes()).hexdigest(),
                         '25c8e5df179fd65762db48856b08c9c2e9ce48065f19a778b92b31f65c1b8e95')

    def test_continuous_fade_tint_and_no_alpha_increase(self):
        image=Image.new('RGBA',(101,64),(50,80,100,200))
        mark=dict(color=[50,80,100],gradient=dict(start=[10,0],end=[90,0],opacity=[1,0],color_to=[150,120,80]))
        result=np.asarray(adapter._gradient(image,mark))
        self.assertEqual(tuple(result[20,10]),(50,80,100,200))
        self.assertEqual(tuple(result[20,50]),(100,100,90,100))
        self.assertEqual(tuple(result[20,90]),(150,120,80,0))
        self.assertTrue(np.all(np.diff(result[20,:,3].astype(int))<=0))
        self.assertGreater(len(np.unique(result[20,:,3])),60)
        self.assertEqual(image.getpixel((50,20)),(50,80,100,200))

    def test_real_brush_fade_keeps_deposit_and_other_objects(self):
        base=upstream_scene()
        before={o['id']:np.asarray(im) for o,im in render.draw_scene(base)[2]}
        changed=copy.deepcopy(base)
        for m in changed['objects'][0]['marks']:
            m['gradient']=dict(start=[20,0],end=[120,0],opacity=[1,0])
        result=render.draw_scene(changed)
        again=render.draw_scene(changed)
        self.assertEqual(result[0].tobytes(),again[0].tobytes())
        for obj,layer in result[2]:
            pixels=np.asarray(layer)
            if obj['id']=='leaf':
                self.assertTrue(np.all(pixels[...,3]<=before['leaf'][...,3]))
                self.assertFalse(np.array_equal(pixels,before['leaf']))
                self.assertEqual(int(pixels[:,120:,3].max()),0)
            else:
                np.testing.assert_array_equal(pixels,before[obj['id']])
        rebuilt=result[1]
        for _,layer in result[2]:
            rebuilt=Image.alpha_composite(rebuilt,layer)
        self.assertEqual(rebuilt.tobytes(),result[0].tobytes())

    def test_translation_and_clone_move_gradient_with_geometry(self):
        scene=upstream_scene()
        obj=scene['objects'][0]
        obj['translate']=[7,11]
        m=obj['marks'][0]
        m['gradient']=dict(start=[20,30],end=[90,100],opacity=[1,.2])
        with patch.object(adapter,'render_mark',wraps=adapter.render_mark) as brush:
            render.draw_scene(scene)
        spec=brush.call_args_list[0].args[1]['gradient']
        self.assertEqual(spec['start'],[27,41])
        self.assertEqual(spec['end'],[97,111])
        cloned=clone_object(obj,'copy',translate=(13,5),scale=(2,.5),rotate=40)
        for key,point in [('start',[27,41]),('end',[97,111])]:
            self.assertEqual(cloned['marks'][0]['gradient'][key],
                             transform([point],translate=(13,5),scale=(2,.5),rotate=40)[0])
        self.assertEqual(m['gradient']['start'],[20,30])

    def test_invalid_gradients_and_unsupported_brushes(self):
        valid=dict(start=[0,0],end=[100,0],opacity=[1,0])
        cases=[None,{},dict(valid,foo=1),dict(valid,end=[0,0]),
               dict(valid,start=[float('nan'),0]),dict(valid,opacity=[True,0]),
               dict(valid,opacity=[1,1.1]),dict(valid,end=[2]),
               dict(valid,color_to=[0,.5,255])]
        for value in cases:
            scene=upstream_scene()
            scene['objects'][0]['marks'][0]['gradient']=value
            with self.subTest(value=value),self.assertRaises(ValueError):
                render.validate(scene)
        for kind,engine in [('wax','pencil-case'),('wash','natural-media')]:
            scene=upstream_scene()
            mark=copy.deepcopy(scene['objects'][0]['marks'][0])
            mark={k:v for k,v in mark.items() if k not in ('offset','layers')}
            mark.update(kind=kind,gradient=valid)
            scene.update(engine=engine,objects=[dict(id='sample',marks=[mark])])
            with self.subTest(kind=kind,engine=engine),self.assertRaises(ValueError):
                render.validate(scene)


if __name__=='__main__':
    unittest.main()
