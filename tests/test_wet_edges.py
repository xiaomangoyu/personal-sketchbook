"""Wet-edge appearance stays deterministic, scoped and optional."""
import copy
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageDraw
from test_pencil_case_media import adapter, render, upstream_scene
from scene_tools import clone_object


class WetEdgeTests(unittest.TestCase):
    def test_visible_regions_do_not_create_new_pigment_seams(self):
        scene=upstream_scene()
        mark=scene['objects'][0]['marks'][0]
        mark.update(polygon=[[15,15],[140,15],[140,140],[15,140]],bleed=0,offset=[0,0])
        scene['objects']=scene['objects'][:1]
        scene['objects'][0]['marks']=[mark]
        before=np.asarray(render.draw_scene(scene)[2][0][1])
        mark['clip_polygons']=[[[20,20],[100,20],[100,65],[20,65]],
                               [[20,65],[100,65],[100,110],[20,110]]]
        clipped=np.asarray(render.draw_scene(scene)[2][0][1])
        np.testing.assert_array_equal(clipped[25:105,25:95],before[25:105,25:95])
        self.assertEqual(int(clipped[:,111:,3].max()),0)
        self.assertEqual(int(clipped[:19,:,3].max()),0)
        obj=scene['objects'][0]
        obj['translate']=[7,9]
        with patch.object(adapter,'render_mark',wraps=adapter.render_mark) as brush:
            render.draw_scene(scene)
        self.assertEqual(brush.call_args.args[1]['clip_polygons'][0][0],[27,29])
        cloned=clone_object(obj,'new',scale=2)
        self.assertEqual(cloned['marks'][0]['clip_polygons'][0][0],[54,58])
        self.assertEqual(mark['clip_polygons'][0][0],[20,20])

    def test_bad_clip_regions_rejected(self):
        for value in [[],None,[[[1,2],[3,4]]],[[[0,0],[1,1],[2,float('inf')]]],
                      [[(0,0),(1,1),(2,2)]],[[[0,0],[1,1],[2,2]]]*257]:
            scene=upstream_scene()
            scene['objects'][0]['marks'][0]['clip_polygons']=value
            with self.subTest(value=str(value)[:60]),self.assertRaises(ValueError):render.validate(scene)

    def test_irregular_spread_has_coloured_edges_and_clean_margins(self):
        source=Image.new('RGBA',(100,100))
        ImageDraw.Draw(source).rectangle((30,30,70,70),fill=(40,110,190,190))
        np.random.seed(19)
        grown=np.asarray(adapter._wet_edges(source,dict(color=[40,110,190],spread=6)))
        self.assertGreater(int(grown[25:30,30:70,3].max()),0)
        self.assertGreater(float(grown[28,30:70,3].std()),1)
        np.testing.assert_array_equal(grown[40:60,40:60],np.asarray(source)[40:60,40:60])
        outside=(np.asarray(source)[...,3]==0)&(grown[...,3]>0)
        np.testing.assert_array_equal(grown[...,:3][outside],np.tile([40,110,190],(outside.sum(),1)))
        self.assertEqual(int(grown[:10,:,3].max()),0)
        self.assertEqual(int(grown[-10:,:,3].max()),0)

    def test_granulation_is_local_without_adding_background_pixels(self):
        source=Image.new('RGBA',(100,100))
        ImageDraw.Draw(source).rectangle((25,25,75,75),fill=(70,160,35,210))
        np.random.seed(12)
        textured=np.asarray(adapter._wet_edges(source,dict(granulation=.8)))
        self.assertGreater(float(textured[30:70,30:70,3].std()),8)
        self.assertTrue(np.all(textured[...,3]<=np.asarray(source)[...,3]))
        self.assertEqual(int(textured[:20,:,3].max()),0)
        self.assertIs(adapter._wet_edges(source,dict(spread=0,granulation=0)),source)

    def test_real_wash_replay_and_unmodified_layers(self):
        scene=upstream_scene()
        original=render.draw_scene(scene)
        scene['objects'][0]['marks'][0].update(spread=5,granulation=.65)
        result=render.draw_scene(scene)
        self.assertEqual(result[0].tobytes(),render.draw_scene(scene)[0].tobytes())
        self.assertNotEqual(original[2][0][1].tobytes(),result[2][0][1].tobytes())
        for old,new in zip(original[2][1:],result[2][1:]):
            self.assertEqual(old[1].tobytes(),new[1].tobytes())
        rebuilt=result[1]
        for _,layer in result[2]:rebuilt=Image.alpha_composite(rebuilt,layer)
        self.assertEqual(rebuilt.tobytes(),result[0].tobytes())
        # Zero opacity still bypasses spread and pigment textures entirely.
        scene['objects']=scene['objects'][:1]
        scene['objects'][0]['marks']=scene['objects'][0]['marks'][:1]
        scene['objects'][0]['marks'][0]['opacity']=0
        self.assertIsNone(render.draw_scene(scene)[2][0][1].getbbox())

    def test_schema_limits_and_scaled_spread(self):
        for key,value in [('spread',-1),('spread',17),('spread',True),
                          ('granulation',1.1),('granulation',float('nan'))]:
            scene=upstream_scene()
            scene['objects'][0]['marks'][0][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):render.validate(scene)
        for engine,index in [('natural-media',0),('pencil-case',1)]:
            scene=upstream_scene();scene['engine']=engine
            scene['objects'][0]['marks'][index]['spread']=2
            with self.assertRaises(ValueError):render.validate(scene)
        obj=copy.deepcopy(upstream_scene()['objects'][0])
        obj['marks'][0].update(spread=3,granulation=.6)
        new=clone_object(obj,'new',scale=2)
        self.assertEqual(new['marks'][0]['spread'],6)
        self.assertEqual(new['marks'][0]['granulation'],.6)
        self.assertEqual(obj['marks'][0]['spread'],3)


if __name__=='__main__':unittest.main()
