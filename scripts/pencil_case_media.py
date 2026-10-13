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
from PIL import Image

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
    if opacity != 1:
        alpha = np.asarray(painted.getchannel("A"), dtype=np.float32)
        painted.putalpha(Image.fromarray(np.rint(alpha * opacity).astype(np.uint8)))
    return Image.alpha_composite(base, painted)
