"""Paper-aware drawing marks for a personal, noncommercial sketchbook.

Inspired by the layered pigment and irregular path approach in pencil-case by
Sienna Qi / 盏 & North: https://github.com/Qizhan7/pencil-case . This derivative
module is provided under PolyForm Noncommercial License 1.0.0; see ../LICENSE.
Required Notice: pencil-case — hand-built drawing skills by 盏 & North. https://github.com/Qizhan7/pencil-case

This module uses Pillow and NumPy only. ``paper`` owns its seeded random state;
``render_mark`` uses the caller's random/np.random state, mutates an RGBA base,
and returns that same image. Re-seed both generators before a mark to replay it.
Marks never regenerate paper texture. Alpha is absolute (never normalized), so
faint marks stay faint. Geometry is supplied by the caller, not invented here.
"""
from __future__ import annotations

import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

__all__ = ["paper", "render_mark"]


def _number(value, name, lo=None, hi=None):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if lo is not None:
        value = max(lo, value)
    if hi is not None:
        value = min(hi, value)
    return value


def _color(value):
    if len(value) != 3:
        raise ValueError("color must contain exactly three RGB channels")
    return tuple(round(_number(c, "color", 0, 255)) for c in value)


def _points(value, minimum=2):
    points = np.asarray(value, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < minimum:
        raise ValueError(f"geometry must contain at least {minimum} [x,y] points")
    if len(points) > 4096 or not np.isfinite(points).all():
        raise ValueError("geometry must be finite and have at most 4096 points")
    return points


def _field(width, height, scale, rng=None):
    """Correlated, bounded noise without image-specific contrast stretching."""
    rng = np.random if rng is None else rng
    small = rng.uniform(0, 1, (max(2, math.ceil(height / scale)),
                               max(2, math.ceil(width / scale)))).astype(np.float32)
    return np.clip(np.asarray(Image.fromarray(small).resize(
        (width, height), Image.Resampling.BICUBIC)), 0, 1)


def paper(width, height, color=(247, 243, 232), seed=0, grain=0.35):
    """Return an RGBA paper image and reusable HxW float32 tooth in [0,1].

    ``grain`` (0..1) changes the paper surface as well as its visible texture.
    ``seed`` is isolated from the random state used to render individual marks.
    Sizes are restricted to 1..8192 per axis and at most 20 million pixels.
    """
    width, height = int(width), int(height)
    if not (1 <= width <= 8192 and 1 <= height <= 8192 and width * height <= 20_000_000):
        raise ValueError("paper dimensions exceed the supported drawing budget")
    grain = _number(grain, "grain", 0, 1)
    rng = np.random.default_rng(seed)
    fine = rng.uniform(0, 1, (height, width)).astype(np.float32)
    fibers = _field(width, height, 3.2, rng)
    broad = _field(width, height, 95, rng)
    tooth = np.clip(0.5 + grain * ((fine - .5) * 1.30 +
                    (fibers - .5) * .70), 0, 1).astype(np.float32)
    light = (tooth - .5) * 10 + (broad - .5) * grain * 3
    rgb = np.clip(np.asarray(_color(color), np.float32) + light[..., None], 0, 255)
    return Image.fromarray(rgb.astype(np.uint8)).convert("RGBA"), tooth


def _bounds(base, pts, margin):
    x0 = max(0, math.floor(float(pts[:, 0].min()) - margin))
    y0 = max(0, math.floor(float(pts[:, 1].min()) - margin))
    x1 = min(base.width, math.ceil(float(pts[:, 0].max()) + margin) + 1)
    y1 = min(base.height, math.ceil(float(pts[:, 1].max()) + margin) + 1)
    if x0 >= x1 or y0 >= y1:
        return None
    return (x0, y0, x1, y1)


def _composite(base, box, alpha, color, opacity):
    # No min/max remapping: a 2% mark must never become opaque.
    a = np.rint(np.clip(alpha * opacity, 0, 1) * 255).astype(np.uint8)
    if not a.any():
        return base
    layer = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), color + (0,))
    layer.putalpha(Image.fromarray(a))
    base.alpha_composite(layer, (box[0], box[1]))
    return base


def _mask(points, width, height, scale=2):
    img = Image.new("L", (width * scale, height * scale))
    ImageDraw.Draw(img).polygon([tuple(p * scale) for p in points], fill=255)
    if scale != 1:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    return np.asarray(img, np.float32) / 255


def _blur(array, radius):
    image = Image.fromarray(np.rint(np.clip(array, 0, 1) * 255).astype(np.uint8))
    return np.asarray(image.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255


def _sample_path(points, smooth, closed):
    """Sample at approximately one-pixel spacing, bounded to 12,000 samples."""
    p = points.copy()
    if closed and np.linalg.norm(p[-1] - p[0]) > .001:
        p = np.vstack((p, p[0]))
    if smooth and len(p) > 2:
        # Catmull-Rom is opt-in; sharp corners stay sharp by default.
        pieces = []
        for i in range(len(p) - 1):
            p1, p2 = p[i], p[i + 1]
            p0 = p[i - 1] if i else (p[-2] if closed else p1)
            p3 = p[i + 2] if i + 2 < len(p) else (p[1] if closed else p2)
            t = np.linspace(0, 1, 8, endpoint=False, dtype=np.float32)[:, None]
            pieces.append(.5 * (2 * p1 + (-p0 + p2) * t +
                (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2 +
                (-p0 + 3 * p1 - 3 * p2 + p3) * t**3))
        p = np.vstack((*pieces, p[-1:]))
    lengths = np.linalg.norm(np.diff(p, axis=0), axis=1)
    keep = np.concatenate(([True], lengths > 1e-5))
    p = p[keep]
    if len(p) < 2:
        return p, np.zeros(len(p), dtype=np.float32)
    dist = np.concatenate(([0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))))
    samples = np.linspace(0, dist[-1], min(12000, max(2, math.ceil(dist[-1]) + 1)))
    sampled = np.column_stack([np.interp(samples, dist, p[:, j]) for j in range(2)])
    return sampled, samples


def _stroke(base, mark, tooth, color, opacity):
    width = _number(mark.get("width", 1.8), "width", .15, 512)
    wobble = _number(mark.get("wobble", .7), "wobble", 0, 12)
    pressure = _number(mark.get("pressure", .5), "pressure", 0, 1)
    gaps = _number(mark.get("gaps", .025), "gaps", 0, 1)
    closed = bool(mark.get("closed", False))
    p, arc = _sample_path(_points(mark.get("points")), bool(mark.get("smooth", False)), closed)
    if len(p) < 2:
        return base
    length = max(arc[-1], .001)
    # Drift is correlated over centimeters of the drawing, not independent per pixel.
    knots = np.linspace(0, length, min(1024, max(3, math.ceil(length / 28) + 1)))
    drift_values = np.random.uniform(-1, 1, len(knots))
    if closed:
        drift_values[-1] = drift_values[0]
    drift = np.interp(arc, knots, drift_values)
    drift = np.convolve(np.pad(drift, 2, mode="edge"), np.ones(5) / 5, mode="valid")
    tangent = np.gradient(p, axis=0)
    tangent /= np.maximum(np.linalg.norm(tangent, axis=1)[:, None], .001)
    p += np.column_stack((-tangent[:, 1], tangent[:, 0])) * (drift * wobble)[:, None]
    pknots = np.linspace(0, length, min(1024, max(3, math.ceil(length / 45) + 1)))
    pressure_values = np.random.uniform(.68, 1, len(pknots))
    if closed:
        pressure_values[-1] = pressure_values[0]
    weight = np.interp(arc, pknots, pressure_values)
    if not closed:
        taper = min(10, length * .16)
        # Lift is stronger at the final end, without making the whole mark feathery.
        weight *= (.60 + .40 * np.minimum(arc / max(taper, .01), 1))
        weight *= (.18 + .82 * np.minimum((length - arc) / max(taper * 1.4, .01), 1))
    widths = width * (.60 + .80 * pressure) * weight
    box = _bounds(base, p, widths.max() + 2)
    if box is None:
        return base
    w, h = box[2] - box[0], box[3] - box[1]
    scale = 2 if w * h <= 3_000_000 else 1
    img = Image.new("L", (w * scale, h * scale))
    draw = ImageDraw.Draw(img)
    p -= (box[0], box[1])
    gap_until = -1.0
    for i in range(len(p) - 1):
        step = arc[i + 1] - arc[i]
        if arc[i] >= gap_until and random.random() < gaps * min(step / 6, 1):
            gap_until = arc[i] + random.uniform(.8, 2.8)
        if arc[i] < gap_until:
            continue
        a = int(255 * (.62 + .38 * weight[i]))
        radius = max(.2, widths[i] * scale / 2)
        xy = p[i] * scale
        draw.line([tuple(xy), tuple(p[i + 1] * scale)], fill=a,
                  width=max(1, round(widths[i] * scale)))
        draw.ellipse((xy[0] - radius, xy[1] - radius, xy[0] + radius, xy[1] + radius), fill=a)
    if scale != 1:
        img = img.resize((w, h), Image.Resampling.LANCZOS)
    coverage = np.asarray(img, np.float32) / 255
    surface = tooth[box[1]:box[3], box[0]:box[2]]
    if mark["kind"] == "pencil":
        # Paper valleys take less graphite at light pressure; repeated marks build it up.
        grip = np.clip(.15 + 1.05 * surface + .35 * pressure, 0, 1)
        micro = np.random.uniform(.65, 1, (h, w)).astype(np.float32)
        coverage *= grip * micro * (.65 + .35 * pressure)
    else:
        coverage *= .93 + .07 * surface
    return _composite(base, box, coverage, color, opacity)


def _directional_field(width, height, angle):
    """Bilinear pigment streaks: long along the rubbing direction, short across."""
    y, x = np.indices((height, width), dtype=np.float32)
    a = math.radians(angle)
    u = (x * math.cos(a) + y * math.sin(a)) / 24
    v = (-x * math.sin(a) + y * math.cos(a)) / 2.2
    u -= u.min()
    v -= v.min()
    ui, vi = u.astype(np.int32), v.astype(np.int32)
    uf, vf = u - ui, v - vi
    grid = np.random.uniform(0, 1, (int(vi.max()) + 2, int(ui.max()) + 2)).astype(np.float32)
    return ((grid[vi, ui] * (1 - uf) + grid[vi, ui + 1] * uf) * (1 - vf) +
            (grid[vi + 1, ui] * (1 - uf) + grid[vi + 1, ui + 1] * uf) * vf)


def _fill(base, mark, tooth, color, opacity):
    pts = _points(mark.get("polygon"), 3)
    grain = _number(mark.get("grain", .55), "grain", 0, 1)
    bleed = _number(mark.get("bleed", 2), "bleed", 0, 32) if mark["kind"] == "wash" else 0
    box = _bounds(base, pts, 4 + bleed * 3)
    if box is None:
        return base
    w, h = box[2] - box[0], box[3] - box[1]
    shape = _mask(pts - (box[0], box[1]), w, h, 2 if w * h <= 3_000_000 else 1)
    surface = tooth[box[1]:box[3], box[0]:box[2]]
    if mark["kind"] == "wax":
        direction = _number(mark.get("direction", 0), "direction")
        density = _number(mark.get("density", 1), "density", .01, 4)
        streaks = _directional_field(w, h, direction)
        grip = np.clip(.35 + surface + streaks * .50, 0, 1.5)
        dry = np.random.uniform(0, 1, (h, w))
        pits = np.clip((dry - grain * (1 - surface) * .8) * 3, 0, 1)
        pigment = 1 - np.exp(-density * (1.05 + grip * 1.1))
        texture = (1 - grain) + grain * pits * (.55 + .45 * streaks)
        coverage = shape * pigment * texture
    else:
        edge = _number(mark.get("edge", .3), "edge", 0, 1)
        broad = _field(w, h, 55)
        tide = _field(w, h, 24)
        wet = _blur(shape, max(.35, bleed)) if bleed else shape
        body = (.68 + broad * .27) * (1 - grain * .24 + grain * surface * .24)
        # Only some parts accumulate pigment: this avoids a uniformly dark outline.
        inner_edge = shape * np.clip((1 - _blur(shape, 2 + bleed)) * 2, 0, 1)
        deposits = np.clip((tide - .38) * 2.2, 0, 1)
        blooms = np.clip((broad - .68) * 2.0, 0, .25) * grain
        coverage = wet * (body - blooms) + inner_edge * deposits * edge * .42
        coverage = np.clip(coverage, 0, 1)
    return _composite(base, box, coverage, color, opacity)


def _hatch(base, mark, tooth, color, opacity):
    pts = _points(mark.get("polygon"), 3)
    width = _number(mark.get("width", 1), "width", .15, 64)
    spacing = _number(mark.get("spacing", 8), "spacing", 2, 2048)
    angle = math.radians(_number(mark.get("angle", 60), "angle"))
    along = np.array((math.cos(angle), math.sin(angle)))
    across = np.array((-math.sin(angle), math.cos(angle)))
    projected = np.column_stack((pts @ along, pts @ across))
    count = math.ceil((projected[:, 1].max() - projected[:, 1].min()) / spacing)
    if count > 2000:
        raise ValueError("hatch would exceed 2000 lines; increase spacing")
    for v in np.arange(projected[:, 1].min() + random.uniform(0, spacing),
                       projected[:, 1].max(), spacing):
        v += random.uniform(-.12, .12) * spacing
        intersections = []
        for i, p in enumerate(projected):
            q = projected[(i + 1) % len(projected)]
            if (p[1] <= v < q[1]) or (q[1] <= v < p[1]):
                intersections.append(p[0] + (v - p[1]) * (q[0] - p[0]) / (q[1] - p[1]))
        intersections.sort()
        for start, end in zip(intersections[::2], intersections[1::2]):
            # Stop just shy of the contour. The hand need not hit every boundary.
            retreat = min((end - start) * .18, spacing * .40)
            start += random.uniform(0, retreat)
            end -= random.uniform(0, retreat)
            if end - start < .8:
                continue
            a = along * start + across * v
            b = along * end + across * v
            _stroke(base, {"kind": "ink", "points": [a, b], "width": width,
                          "wobble": .35, "pressure": random.uniform(.3, .7),
                          "gaps": .012}, tooth, color, opacity)
    return base


def render_mark(base, mark, *, tooth):
    """Render one mark onto ``base`` in place and return it.

    Common: kind, color=[r,g,b], opacity=1. Ink/pencil: points, width=1.8,
    wobble=.7 pixels, pressure=.5, gaps=.025, smooth=False, closed=False.
    Wax/wash: polygon, grain=.55. Wax: direction=0 degrees, density=1.
    Wash: edge=.3, bleed=2 pixels. Hatch: polygon, width=1, spacing=8 pixels,
    angle=60 degrees. Angles follow image coordinates (positive y down).

    ``tooth`` is the unmodified array from ``paper`` for this exact canvas.
    Fill masks are local; simple even-odd polygons are recommended. ``smooth``
    uses Catmull-Rom and can overshoot corners. This is pigment simulation,
    not a physical fluid solver or a composition/planning system.
    """
    if base.mode != "RGBA":
        raise ValueError("base must be an RGBA Pillow image")
    if not isinstance(tooth, np.ndarray) or tooth.shape != (base.height, base.width):
        raise ValueError("tooth must be the HxW array corresponding to base")
    kind = mark.get("kind")
    if kind not in {"ink", "pencil", "wax", "wash", "hatch"}:
        raise ValueError(f"unsupported mark kind: {kind!r}")
    color = _color(mark.get("color", (57, 51, 47)))
    opacity = _number(mark.get("opacity", 1), "opacity", 0, 1)
    if opacity == 0:
        return base
    if kind in {"ink", "pencil"}:
        return _stroke(base, mark, tooth, color, opacity)
    if kind in {"wax", "wash"}:
        return _fill(base, mark, tooth, color, opacity)
    return _hatch(base, mark, tooth, color, opacity)
