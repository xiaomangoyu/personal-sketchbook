"""Schema-v1 adapter for the unmodified pencil-case drawing libraries.

Ink, wash, wax and hatch call the upstream brushes rather than approximating
their marks. Paper and graphite use natural_media. The renderer supplies a
separate Python/NumPy random seed for each stable mark ID.

Required Notice: pencil-case — hand-built drawing skills by 盏 & North.
https://github.com/Qizhan7/pencil-case
PolyForm Noncommercial 1.0.0; see ../LICENSE.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import numpy as np
from PIL import Image, ImageFilter, ImageDraw

import natural_media
from vendor import crayon_lib as crayon
from vendor import penwash_lib as penwash

_LOCK = RLock()


@contextmanager
def _brush_context(size):
    """Bound legacy module state to one mark; never record video or retain maps."""
    with _LOCK:
        old = (penwash.W, penwash.H, crayon.W, crayon.H,
               penwash._REC, penwash._TEX_CACHE)
        try:
            penwash.set_size(*size)
            crayon.set_size(*size)
            penwash._REC = None
            # Upstream caches full-canvas water maps. Retaining thousands of
            # one-off mark seeds would leak memory and complicate replay.
            penwash._TEX_CACHE = {}
            yield
        finally:
            penwash.W, penwash.H, crayon.W, crayon.H = old[:4]
            penwash._REC, penwash._TEX_CACHE = old[4:]


def source_files(kinds):
    """Files actually used by this scene, in addition to renderer and paper."""
    files = [Path(__file__)]
    if kinds & {"ink", "wash", "hatch"}:
        files.append(Path(penwash.__file__))
    if "wax" in kinds:
        files.append(Path(crayon.__file__))
    return files


def _ink(base, mark, color):
    points = [tuple(p) for p in mark["points"]]
    if mark.get("closed", False) and points[-1] != points[0]:
        points.append(points[0])
    width, pressure = mark.get("width", 1.8), mark.get("pressure", .5)
    return penwash.pen_path(
        base, points, ink=color,
        width=(width * (.5 + .45 * pressure), width * (.9 + .45 * pressure)),
        alpha=(round(120 + 50 * pressure), round(195 + 60 * pressure)),
        wobble=mark.get("wobble", .7), gaps=mark.get("gaps", .025),
        smooth=mark.get("smooth", False), overdraw=mark.get("overdraw", 0),
        jitter=mark.get("jitter", 0), nib=mark.get("nib", False),
        overshoot=mark.get("overshoot", 0),
        gap_len=tuple(mark.get("gap_length", [2, 6])), step=mark.get("step", 2),
    )


def _wax(base, mark, color):
    grain = mark.get("grain", .6)
    mask = crayon.soft_mask([tuple(p) for p in mark["polygon"]],
                           feather=.5 + grain * 2.5, grow=round(grain * 2))
    area = float(np.asarray(mask, dtype=np.float32).sum()) / 255
    # Count scales with painted area, not the entire canvas. Each upstream
    # mark remains a short run of pigment dots, with paper visible between.
    count = max(1, round(area / 90 * mark.get("density", 1)))
    return crayon.crayon(
        base, mask, color, direction=mark.get("direction", 0), n=count,
        length=(10, 32), dot=(.8 + .5 * grain, 1.5 + 1.1 * grain),
        spread=10 + 18 * grain, jitter=round(4 + 16 * grain),
        alpha=(110, 215),
    )


def _gradient(painted, mark):
    """Fade the original brush deposit in scene coordinates; retain its texture."""
    spec = mark.get("gradient")
    box = painted.getbbox()
    if spec is None or box is None:
        return painted
    x0, y0 = spec["start"]
    dx, dy = np.subtract(spec["end"], spec["start"])
    yy, xx = np.mgrid[box[1]:box[3], box[0]:box[2]]
    t = np.clip(((xx-x0)*dx + (yy-y0)*dy)/(dx*dx+dy*dy), 0, 1)
    t = t*t*(3-2*t)
    pixels = np.array(painted.crop(box), dtype=np.float32)
    a, b = spec["opacity"]
    pixels[..., 3] *= a+(b-a)*t
    if "color_to" in spec:
        # Offset the deposited colour rather than replacing its local variation.
        delta = np.subtract(spec["color_to"], mark.get("color", [65,62,57]))
        pixels[..., :3] += t[..., None]*delta
    patch = Image.fromarray(np.rint(np.clip(pixels, 0, 255)).astype(np.uint8))
    result = painted.copy()
    result.paste(patch, box[:2])
    return result


def _wet_edges(painted, mark):
    """Optional irregular spread and pigment grain over the upstream deposit.

    This is an appearance approximation, not fluid transport. Work only near
    painted pixels; untouched paper and other object layers remain unchanged.
    """
    spread, grain = mark.get("spread", 0), mark.get("granulation", 0)
    box = painted.getbbox()
    if (not spread and not grain) or box is None:
        return painted
    margin = int(np.ceil(spread*3))+4
    box = (max(0,box[0]-margin), max(0,box[1]-margin),
           min(painted.width,box[2]+margin), min(painted.height,box[3]+margin))
    crop = painted.crop(box)
    pixels = np.array(crop, dtype=np.float32)
    alpha = pixels[...,3].copy()
    size = crop.size

    def field(cell):
        noise = np.random.uniform(0,255,(max(2,int(size[1]/cell)),max(2,int(size[0]/cell))))
        return np.asarray(Image.fromarray(noise.astype(np.uint8)).resize(size,Image.Resampling.BICUBIC),dtype=np.float32)/255

    if spread:
        radius = int(np.ceil(spread))
        expanded = crop.getchannel("A").filter(ImageFilter.MaxFilter(radius*2+1))
        expanded = np.asarray(expanded.filter(ImageFilter.GaussianBlur(spread*.28+.25)),dtype=np.float32)
        wetness = np.clip((field(18)-.28)*1.8,0,1)
        halo = np.maximum(0,expanded-alpha)*wetness*.72
        combined = alpha+halo
        # New pigment outside the old alpha footprint has the mark's hue,
        # not the black RGB of transparent pixels.
        color = np.array(mark.get("color",[65,62,57]),dtype=np.float32)
        pixels[...,:3] = (pixels[...,:3]*alpha[...,None]+color*halo[...,None])/np.maximum(combined[...,None],1e-6)
        alpha = combined
    if grain:
        # Tiny paper gaps within pigment plus slower deposits; no global noise.
        tooth = .58*field(1.3)+.42*field(3.5)
        alpha *= 1-grain*np.clip((.8-tooth)*1.15,0,.75)
    pixels[...,3] = alpha
    result = painted.copy()
    result.paste(Image.fromarray(np.rint(np.clip(pixels,0,255)).astype(np.uint8)),box[:2])
    return result


def render_mark(base, mark, *, tooth=None):
    """Return composited RGBA; schema/type checks belong to render.validate.

    Opacity scales a completed transparent mark exactly once, including its
    repeated strokes and pigment edges. Zero opacity leaves the base intact.
    """
    if mark["kind"] == "pencil":
        return natural_media.render_mark(base, mark, tooth=tooth)
    opacity = mark.get("opacity", 1)
    if opacity == 0:
        return base
    color = tuple(mark.get("color", [65, 62, 57]))
    blank = Image.new("RGBA", base.size)
    with _brush_context(base.size):
        if mark["kind"] == "ink":
            painted = _ink(blank, mark, color)
        elif mark["kind"] == "wash":
            painted = penwash.wash(
                blank, mark["polygon"], color, alpha=(100, 175),
                offset=tuple(mark.get("offset", [3, 2])),
                layers=mark.get("layers", 2), edge=mark.get("edge", .35),
                feather=mark.get("bleed", 2), texture=mark.get("grain", .45),
            )
        elif mark["kind"] == "wax":
            painted = _wax(blank, mark, color)
        elif mark["kind"] == "hatch":
            width = mark.get("width", 1)
            painted = penwash.hatch(
                blank, penwash.poly_mask(mark["polygon"]), ink=color,
                angle=mark.get("angle", 65), spacing=mark.get("spacing", 6),
                width=(width * .6, width * 1.2), alpha=(110, 195),
            )
        else:
            raise ValueError(f"unsupported mark kind: {mark['kind']}")
    if mark["kind"] == "wash":
        if "clip_polygons" in mark:
            # Paint once, then keep visible regions. Independent washes per
            # region would produce pigment/edge seams at occlusion splits.
            mask = Image.new("L", base.size)
            draw = ImageDraw.Draw(mask)
            for polygon in mark["clip_polygons"]:
                draw.polygon([tuple(p) for p in polygon], fill=255)
            alpha = np.asarray(painted.getchannel("A"), dtype=np.uint16)
            painted.putalpha(Image.fromarray((alpha*(np.asarray(mask,dtype=np.uint16)//255)).astype(np.uint8)))
        painted = _wet_edges(painted, mark)
    painted = _gradient(painted, mark)
    if opacity != 1:
        alpha = np.asarray(painted.getchannel("A"), dtype=np.float32)
        painted.putalpha(Image.fromarray(np.rint(alpha * opacity).astype(np.uint8)))
    return Image.alpha_composite(base, painted)
