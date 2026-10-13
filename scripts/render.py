#!/usr/bin/env python3
"""Render editable, deterministic drawing scenes. Personal/noncommercial derivative.

Upstream pencil-case: https://github.com/Qizhan7/pencil-case
The source JSON describes marks; it is never evaluated as Python.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
import platform
import random
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, __version__ as pillow_version
import natural_media as media

KINDS = {"ink", "pencil", "wax", "wash", "hatch"}
ID = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}\Z")
COMMON_FIELDS = {"id", "kind", "color", "opacity"}
STROKE_FIELDS = {"points", "width", "wobble", "pressure", "gaps", "smooth", "closed"}
MARK_FIELDS = {"ink": STROKE_FIELDS, "pencil": STROKE_FIELDS,
               "wax": {"polygon", "grain", "direction", "density"},
               "wash": {"polygon", "grain", "edge", "bleed"},
               "hatch": {"polygon", "width", "spacing", "angle"}}


def number(value, label, lo, hi):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not lo <= value <= hi:
        raise ValueError(f"{label}: expected a finite number in [{lo}, {hi}]")
    return value


def color(value, label):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{label}: expected [red, green, blue]")
    for v in value:
        number(v, label, 0, 255)
        if not isinstance(v, int):
            raise ValueError(f"{label}: RGB channels must be integers")


def stable_id(value, label):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError(f"{label}: use 1–80 letters, digits, underscores or hyphens")


def validate(scene):
    if not isinstance(scene, dict) or scene.get("version") != 1:
        raise ValueError("scene.version must be 1")
    number(scene.get("seed", 0), "seed", 0, 2**32 - 1)
    if not isinstance(scene.get("seed", 0), int):
        raise ValueError("seed must be an integer")
    canvas = scene.get("canvas", {})
    if not isinstance(canvas, dict):
        raise ValueError("canvas must be an object")
    for axis in ("width", "height"):
        number(canvas.get(axis), f"canvas.{axis}", 64, 4096)
        if not isinstance(canvas[axis], int):
            raise ValueError(f"canvas.{axis} must be an integer")
    if canvas["width"] * canvas["height"] > 8_000_000:
        raise ValueError("canvas must contain at most 8 million pixels")
    color(canvas.get("paper", [247, 245, 238]), "canvas.paper")
    number(canvas.get("grain", .3), "canvas.grain", 0, 1)
    objects = scene.get("objects")
    if not isinstance(objects, list) or not 1 <= len(objects) <= 128:
        raise ValueError("objects must contain 1–128 drawing objects")
    obj_ids, count = set(), 0
    ranges = {"opacity": (0, 1), "width": (.15, 64), "wobble": (0, 12),
              "pressure": (0, 1), "gaps": (0, .5), "grain": (0, 1),
              "density": (.01, 4), "edge": (0, 1), "bleed": (0, 32),
              "spacing": (2, 100), "angle": (-360, 360), "direction": (-360, 360)}
    for obj in objects:
        if not isinstance(obj, dict):
            raise ValueError("each object must be a JSON object")
        stable_id(obj.get("id"), "object.id")
        if obj["id"].casefold() in obj_ids:
            raise ValueError(f"duplicate object id (case insensitive): {obj['id']}")
        obj_ids.add(obj["id"].casefold())
        if not isinstance(obj.get("visible", True), bool):
            raise ValueError(f"{obj['id']}.visible must be true or false")
        offset = obj.get("translate", [0, 0])
        if not isinstance(offset, list) or len(offset) != 2:
            raise ValueError(f"{obj['id']}.translate must be [dx,dy]")
        for v in offset:
            number(v, "translate", -8192, 8192)
        marks = obj.get("marks")
        if not isinstance(marks, list) or not marks:
            raise ValueError(f"{obj['id']}: marks cannot be empty")
        mark_ids = set()
        for mark in marks:
            count += 1
            if not isinstance(mark, dict):
                raise ValueError("each mark must be a JSON object")
            kind = mark.get("kind")
            if not isinstance(kind, str) or kind not in KINDS:
                raise ValueError(f"unsupported mark kind: {kind}")
            unknown = set(mark) - COMMON_FIELDS - MARK_FIELDS[kind]
            if unknown:
                raise ValueError(f"unsupported mark fields: {', '.join(sorted(unknown))}")
            stable_id(mark.get("id"), "mark.id")
            if mark["id"] in mark_ids:
                raise ValueError(f"duplicate mark id in {obj['id']}: {mark['id']}")
            mark_ids.add(mark["id"])
            color(mark.get("color", [65, 62, 57]), "mark.color")
            key = "points" if mark["kind"] in ("ink", "pencil") else "polygon"
            coords = mark.get(key)
            minimum = 2 if key == "points" else 3
            if not isinstance(coords, list) or not minimum <= len(coords) <= 4096:
                raise ValueError(f"{mark['id']}.{key}: expected {minimum}–4096 points")
            for point in coords:
                if not isinstance(point, list) or len(point) != 2:
                    raise ValueError(f"{mark['id']}.{key}: each point must be [x,y]")
                for v in point:
                    number(v, "coordinate", -8192, 8192)
            for key, (lo, hi) in ranges.items():
                if key in mark:
                    number(mark[key], f"{mark['id']}.{key}", lo, hi)
            for key in ("smooth", "closed"):
                if key in mark and not isinstance(mark[key], bool):
                    raise ValueError(f"{mark['id']}.{key} must be true or false")
    if count > 5000:
        raise ValueError("at most 5000 marks per scene")
    return scene


def mark_seed(seed, object_id, mark_id):
    key = json.dumps([seed, object_id, mark_id], ensure_ascii=True).encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:4], "big")


def draw_scene(scene):
    """Return composite, paper, (object metadata, RGBA layer) pairs. No writes."""
    validate(scene)
    c = scene["canvas"]
    seed = scene.get("seed", 0)
    paper, tooth = media.paper(c["width"], c["height"], tuple(c.get("paper", [247, 245, 238])), seed, c.get("grain", .3))
    image = paper.copy()
    layers = []
    rstate, nstate = random.getstate(), np.random.get_state()
    try:
        for obj in scene["objects"]:
            layer = Image.new("RGBA", image.size)
            if obj.get("visible", True):
                for original in obj["marks"]:
                    m = copy.deepcopy(original)
                    dx, dy = obj.get("translate", [0, 0])
                    key = "points" if m["kind"] in ("ink", "pencil") else "polygon"
                    m[key] = [[x + dx, y + dy] for x, y in m[key]]
                    s = mark_seed(seed, obj["id"], m["id"])
                    random.seed(s)
                    np.random.seed(s)
                    layer = media.render_mark(layer, m, tooth=tooth)
            image = Image.alpha_composite(image, layer)
            layers.append((obj, layer))
    finally:
        random.setstate(rstate)
        np.random.set_state(nstate)
    return image, paper, layers


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_to(scene, out, overwrite=False):
    validate(scene)
    out = Path(out)
    previous_layers = []
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        if not overwrite:
            raise ValueError(f"output is not empty: {out}; choose a new folder or pass --overwrite")
        previous = out / "manifest.json"
        if not previous.is_file():
            raise ValueError("--overwrite only accepts a previous personal-sketchbook output folder")
        previous_data = json.loads(previous.read_text())
        if previous_data.get("renderer") != "personal-sketchbook/1":
            raise ValueError("output folder belongs to a different renderer")
        # Queue only owned layer files; do not erase old output before drawing succeeds.
        for item in previous_data.get("layers", []):
            name = item.get("id", "")
            if isinstance(name, str) and ID.fullmatch(name):
                previous_layers.append(out / "layers" / f"{name}.png")
    image, paper, layers = draw_scene(scene)
    (out / "layers").mkdir(parents=True, exist_ok=True)
    for path in previous_layers:
        path.unlink(missing_ok=True)
    image.save(out / "artwork.png")
    paper.save(out / "layers" / "_paper.png")
    records, warnings = [], []
    for obj, layer in layers:
        path = out / "layers" / f"{obj['id']}.png"
        layer.save(path)
        box = layer.getbbox()
        if box is None and obj.get("visible", True):
            warnings.append(f"{obj['id']}: layer has no visible pixels; check opacity and coordinates")
        records.append({"id": obj["id"], "name": obj.get("name", obj["id"]),
                        "visible": obj.get("visible", True), "bounds": box,
                        "file": f"layers/{obj['id']}.png", "sha256": sha(path)})
    (out / "scene.json").write_text(json.dumps(scene, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = {"renderer": "personal-sketchbook/1", "title": scene.get("title", ""),
                "seed": scene.get("seed", 0), "size": image.size, "layers": records,
                "paper": "layers/_paper.png", "artwork": "artwork.png", "source": "scene.json",
                "artwork_sha256": sha(out / "artwork.png"), "warnings": warnings,
                "runtime": {"python": platform.python_version(), "pillow": pillow_version, "numpy": np.__version__},
                "code_sha256": {p.name: sha(p) for p in (Path(__file__), Path(media.__file__))},
                "upstream": {"url": "https://github.com/Qizhan7/pencil-case", "commit": "9bb75d1bdcd2b3f62edc804d751ac53f43c6c85d", "license": "PolyForm Noncommercial 1.0.0"}}
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser(description="Render editable natural-media JSON to PNG + transparent object layers")
    p.add_argument("scene", type=Path)
    p.add_argument("--out", type=Path, help="new output directory")
    p.add_argument("--overwrite", action="store_true", help="replace generated files in a previous renderer output")
    p.add_argument("--validate-only", action="store_true")
    args = p.parse_args()
    try:
        scene = validate(json.loads(args.scene.read_text(encoding="utf-8")))
        if args.validate_only:
            print(f"Valid: {args.scene}")
            return
        if args.out is None:
            p.error("--out is required unless --validate-only is used")
        result = render_to(scene, args.out, args.overwrite)
        print(json.dumps({"artwork": str(args.out.resolve() / "artwork.png"), "objects": len(result["layers"]), "warnings": result["warnings"]}, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as e:
        p.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    main()
