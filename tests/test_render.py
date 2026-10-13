"""Behavioral checks for reproducibility, edit isolation and lossless layer export."""
import copy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import render


def scene():
    return {"version": 1, "seed": 94,
            "canvas": {"width": 160, "height": 160, "paper": [247, 245, 238], "grain": .35},
            "objects": [{"id": "leaf", "marks": [
                {"id": "paint", "kind": "wash", "polygon": [[20, 25], [105, 35], [55, 105]], "color": [60, 120, 85], "opacity": .5},
                {"id": "stem", "kind": "ink", "points": [[50, 115], [52, 70], [65, 38]], "color": [50, 60, 40], "width": 2, "smooth": True}]},
                {"id": "pencil", "marks": [{"id": "line", "kind": "pencil", "points": [[95, 120], [140, 55]], "color": [65, 60, 55], "width": 3}]}]}


class RenderingTests(unittest.TestCase):
    def test_reproducible_pixels(self):
        a = render.draw_scene(scene())[0]
        b = render.draw_scene(scene())[0]
        self.assertEqual(a.tobytes(), b.tobytes())

    def test_edit_other_object_keeps_layer_exact(self):
        a = render.draw_scene(scene())[2]
        edited = scene()
        edited["objects"][0]["marks"][0]["color"] = [165, 75, 55]
        edited["objects"][0]["marks"].append({"id": "extra", "kind": "ink", "points": [[10, 10], [40, 40]], "color": [0, 0, 0]})
        b = render.draw_scene(edited)[2]
        self.assertNotEqual(a[0][1].tobytes(), b[0][1].tobytes())
        self.assertEqual(a[1][1].tobytes(), b[1][1].tobytes())

    def test_reorder_keeps_each_object_layer(self):
        a = render.draw_scene(scene())[2]
        edited = scene()
        edited["objects"].reverse()
        b = render.draw_scene(edited)[2]
        self.assertEqual({o["id"]: im.tobytes() for o, im in a}, {o["id"]: im.tobytes() for o, im in b})

    def test_no_global_rng_side_effects(self):
        random.seed(98)
        np.random.seed(98)
        r, n = random.getstate(), np.random.get_state()
        render.draw_scene(scene())
        self.assertEqual(random.getstate(), r)
        now = np.random.get_state()
        self.assertEqual(now[0], n[0])
        np.testing.assert_array_equal(now[1], n[1])
        self.assertEqual(now[2:], n[2:])

    def test_all_media_zero_opacity_and_nonempty(self):
        for kind in render.KINDS:
            with self.subTest(kind=kind):
                mark = {"id": "test", "kind": kind, "color": [55, 60, 70], "opacity": 0}
                if kind in ("ink", "pencil"):
                    mark.update(points=[[20, 100], [65, 25], [130, 90]], width=3)
                else:
                    mark["polygon"] = [[20, 30], [130, 30], [110, 130], [30, 115]]
                s = scene()
                s["objects"] = [{"id": "sample", "marks": [mark]}]
                image, paper, layers = render.draw_scene(s)
                self.assertEqual(image.tobytes(), paper.tobytes())
                self.assertIsNone(layers[0][1].getbbox())
                mark["opacity"] = .7
                self.assertIsNotNone(render.draw_scene(s)[2][0][1].getbbox())
                mark["opacity"] = .02
                faint = np.asarray(render.draw_scene(s)[2][0][1])[..., 3]
                self.assertGreater(faint.max(), 0)
                self.assertLessEqual(faint.max(), 12)

    def test_layers_recompose_and_outputs_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "v01"
            render.render_to(scene(), out)
            manifest = json.loads((out / "manifest.json").read_text())
            rebuilt = Image.open(out / manifest["paper"]).convert("RGBA")
            for item in manifest["layers"]:
                layer = Image.open(out / item["file"]).convert("RGBA")
                self.assertLess(np.asarray(layer)[..., 3].min(), 255)
                rebuilt = Image.alpha_composite(rebuilt, layer)
            self.assertEqual(rebuilt.tobytes(), Image.open(out / "artwork.png").tobytes())
            (out / "user-notes.txt").write_text("keep")
            with self.assertRaises(ValueError):
                render.render_to(scene(), out)
            changed = scene()
            changed["objects"] = changed["objects"][:1]
            render.render_to(changed, out, overwrite=True)
            self.assertFalse((out / "layers/pencil.png").exists())
            self.assertEqual((out / "user-notes.txt").read_text(), "keep")

    def test_failed_overwrite_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "v01"
            render.render_to(scene(), out)
            before = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
            with patch.object(render, "draw_scene", side_effect=ValueError("drawing failed")):
                with self.assertRaises(ValueError):
                    render.render_to(scene(), out, overwrite=True)
            after = {p.relative_to(out): p.read_bytes() for p in out.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_invalid_input_rejected_before_writing(self):
        variants = []
        a = scene(); a["objects"][0]["id"] = "../escape"; variants.append(a)
        a = scene(); a["objects"][0]["marks"][0]["opacity"] = float("nan"); variants.append(a)
        a = scene(); a["objects"].append(copy.deepcopy(a["objects"][0])); variants.append(a)
        a = scene(); b = copy.deepcopy(a["objects"][0]); b["id"] = "LEAF"; a["objects"].append(b); variants.append(a)
        a = scene(); a["objects"][0]["marks"][0]["spacing"] = 0; variants.append(a)
        a = scene(); a["canvas"]["width"] = 100000; variants.append(a)
        a = scene(); a["objects"][0]["marks"][0]["opactiy"] = .5; variants.append(a)
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                render.validate(value)


if __name__ == "__main__":
    unittest.main()
