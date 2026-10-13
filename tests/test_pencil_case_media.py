"""Legacy compatibility and actual upstream-brush integration checks."""
import copy
import hashlib
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render
import pencil_case_media as adapter
from test_render import scene as legacy_scene


def upstream_scene():
    scene = legacy_scene()
    scene["engine"] = "pencil-case"
    scene["objects"][0]["marks"][0].update(offset=[1, -2], layers=2, grain=.4)
    scene["objects"][0]["marks"][1].update(
        nib=True, overdraw=1, jitter=.3, gap_length=[1, 3], step=1)
    for kind in ("wax", "hatch"):
        scene["objects"].append({"id": kind, "marks": [{
            "id": "area", "kind": kind, "color": [195, 110, 50],
            "polygon": [[12, 95], [64, 105], [56, 144], [15, 139]], "opacity": .75}]})
    return scene


class PencilCaseIntegrationTests(unittest.TestCase):
    def test_default_engine_preserves_pre_adapter_pixels(self):
        # Captured before adding the adapter, with the pinned Pillow/NumPy.
        expected = "047e8fc2fe518ab750fbdbb5ebdcff29de1604914905d28e11111d56e5504421"
        self.assertEqual(hashlib.sha256(render.draw_scene(legacy_scene())[0].tobytes()).hexdigest(), expected)
        explicit = legacy_scene()
        explicit["engine"] = "natural-media"
        self.assertEqual(hashlib.sha256(render.draw_scene(explicit)[0].tobytes()).hexdigest(), expected)

    def test_actual_upstream_brushes_are_called_and_sources_are_unchanged(self):
        with patch.object(adapter.penwash, "pen_path", wraps=adapter.penwash.pen_path) as pen, \
             patch.object(adapter.penwash, "wash", wraps=adapter.penwash.wash) as wash, \
             patch.object(adapter.penwash, "hatch", wraps=adapter.penwash.hatch) as hatch, \
             patch.object(adapter.crayon, "crayon", wraps=adapter.crayon.crayon) as wax:
            image, paper, layers = render.draw_scene(upstream_scene())
            for method in (pen, wash, hatch, wax):
                self.assertTrue(method.called)
            self.assertNotEqual(image.tobytes(), paper.tobytes())
            self.assertTrue(all(layer.getbbox() for _, layer in layers))
            self.assertEqual(wash.call_args.kwargs["offset"], (1, -2))
            self.assertEqual(wash.call_args.kwargs["layers"], 2)
        expected = {
            "penwash_lib.py": "ab6856902d05e8126acd959ce52efe704e13bb349b7f6ac84cf89bb008b3f482",
            "crayon_lib.py": "b852a23ccc610613fc156a08d8c64bf3602ecf2910c458d5350678ca5c022161",
        }
        for name, digest in expected.items():
            self.assertEqual(render.sha(ROOT / "scripts/vendor" / name), digest)

    def test_replay_recompose_and_manifest_identifies_used_code(self):
        scene = upstream_scene()
        image, paper, layers = render.draw_scene(scene)
        self.assertEqual(image.tobytes(), render.draw_scene(scene)[0].tobytes())
        rebuilt = paper
        for _, layer in layers:
            rebuilt = Image.alpha_composite(rebuilt, layer)
        self.assertEqual(image.tobytes(), rebuilt.tobytes())
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            manifest = render.render_to(scene, out)
            self.assertEqual(manifest["engine"], "pencil-case")
            self.assertEqual(manifest["warnings"], [])
            self.assertEqual(set(manifest["code_sha256"]), {
                "render.py", "natural_media.py", "pencil_case_media.py",
                "vendor/penwash_lib.py", "vendor/crayon_lib.py"})
            for name, digest in manifest["code_sha256"].items():
                self.assertEqual(digest, render.sha(ROOT / "scripts" / name))
            replay = render.draw_scene(json.loads((out / "scene.json").read_text()))[0]
            self.assertEqual(replay.tobytes(), Image.open(out / "artwork.png").tobytes())

    def test_edit_and_reorder_keep_unmodified_layers_exact(self):
        original = upstream_scene()
        a = {obj["id"]: layer.tobytes() for obj, layer in render.draw_scene(original)[2]}
        changed = copy.deepcopy(original)
        changed["objects"][0]["marks"][0]["color"] = [160, 65, 95]
        changed["objects"][0]["marks"].append({
            "id": "detail", "kind": "ink", "points": [[10, 10], [50, 10]], "nib": True})
        changed["objects"].reverse()
        b = {obj["id"]: layer.tobytes() for obj, layer in render.draw_scene(changed)[2]}
        self.assertNotEqual(a.pop("leaf"), b.pop("leaf"))
        self.assertEqual(a, b)

    def test_no_rng_dimensions_texture_or_recorder_side_effects(self):
        class NoRecording:
            def snap(self, *args):
                raise AssertionError("renderer must never record a video")
        recorder = NoRecording()
        cache = {"sentinel": object()}
        old_p = (adapter.penwash.W, adapter.penwash.H)
        old_c = (adapter.crayon.W, adapter.crayon.H)
        random.seed(843)
        np.random.seed(843)
        rng, np_rng = random.getstate(), np.random.get_state()
        with patch.object(adapter.penwash, "_REC", recorder), \
             patch.object(adapter.penwash, "_TEX_CACHE", cache):
            render.draw_scene(upstream_scene())
            self.assertIs(adapter.penwash._REC, recorder)
            self.assertIs(adapter.penwash._TEX_CACHE, cache)
        self.assertEqual(old_p, (adapter.penwash.W, adapter.penwash.H))
        self.assertEqual(old_c, (adapter.crayon.W, adapter.crayon.H))
        self.assertEqual(random.getstate(), rng)
        now = np.random.get_state()
        self.assertEqual(now[0], np_rng[0])
        np.testing.assert_array_equal(now[1], np_rng[1])
        self.assertEqual(now[2:], np_rng[2:])
        with patch.object(adapter.penwash, "pen_path", side_effect=RuntimeError("failed brush")):
            with self.assertRaises(RuntimeError):
                render.draw_scene(upstream_scene())
        self.assertEqual(old_p, (adapter.penwash.W, adapter.penwash.H))
        self.assertEqual(old_c, (adapter.crayon.W, adapter.crayon.H))
        self.assertEqual(random.getstate(), rng)

    def test_zero_opacity_and_faint_marks_do_not_become_opaque(self):
        for kind in render.KINDS:
            with self.subTest(kind=kind):
                scene = upstream_scene()
                mark = {"id": "faint", "kind": kind, "color": [55, 65, 75], "opacity": 0}
                if kind in {"ink", "pencil"}:
                    mark.update(points=[[20, 120], [60, 30], [135, 90]], width=3)
                else:
                    mark["polygon"] = [[20, 30], [130, 30], [110, 130], [30, 110]]
                scene["objects"] = [{"id": "sample", "marks": [mark]}]
                image, paper, layers = render.draw_scene(scene)
                self.assertEqual(image.tobytes(), paper.tobytes())
                self.assertIsNone(layers[0][1].getbbox())
                mark["opacity"] = .02
                alpha = np.asarray(render.draw_scene(scene)[2][0][1])[..., 3]
                self.assertGreater(alpha.max(), 0)
                self.assertLessEqual(alpha.max(), 12)

    def test_bad_engine_and_engine_specific_parameters_are_rejected(self):
        for value in (None, [], 1, True, "penwash", "PENCIL-CASE"):
            scene = upstream_scene()
            scene["engine"] = value
            with self.subTest(engine=value), self.assertRaises(ValueError):
                render.validate(scene)
        cases = [
            ("ink", "overdraw", 1.1), ("ink", "overdraw", True),
            ("ink", "overdraw", 4), ("ink", "nib", 1),
            ("ink", "jitter", -1), ("ink", "step", 0),
            ("ink", "overshoot", 9), ("ink", "gap_length", [6, 2]),
            ("ink", "gap_length", [1.5, 2]), ("ink", "gap_length", [1]),
            ("ink", "gap_length", [1, 65]), ("ink", "offset", [0, 0]),
            ("wash", "layers", 0), ("wash", "layers", 2.5),
            ("wash", "layers", True), ("wash", "offset", [0]),
            ("wash", "offset", [float("nan"), 0]),
            ("wash", "overshoot", 1), ("pencil", "nib", True),
        ]
        for kind, field, value in cases:
            scene = upstream_scene()
            mark = next(m for obj in scene["objects"] for m in obj["marks"] if m["kind"] == kind)
            mark[field] = value
            with self.subTest(kind=kind, field=field, value=value), self.assertRaises(ValueError):
                render.validate(scene)
        scene = legacy_scene()
        scene["objects"][0]["marks"][1]["nib"] = True
        with self.assertRaises(ValueError):
            render.validate(scene)


if __name__ == "__main__":
    unittest.main()
