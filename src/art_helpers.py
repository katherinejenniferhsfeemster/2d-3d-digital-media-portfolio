"""Shared helpers for deterministic procedural art generation.

Used by all six case generators (GIMP, Inkscape, Krita, Libresprite, Blender, Godot).
Pillow is the universal renderer; when a native tool is available we ALSO write
the tool's native project file (Script-Fu, SVG, .kra, Lua, .py for Blender, GDScript).
"""
from __future__ import annotations

import colorsys
import json
import math
import random
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---- palette ----------------------------------------------------------------
TEAL = (46, 122, 123)
AMBER = (217, 164, 65)
INK = (20, 26, 33)
PAPER = (247, 244, 237)
MUTED = (92, 102, 114)

PALETTE_CREATURE = [
    (48, 112, 164), (205, 92, 72), (120, 168, 96), (216, 176, 72),
    (140, 104, 176), (76, 156, 156), (208, 128, 160), (96, 128, 80),
]


def seeded(seed: int) -> random.Random:
    return random.Random(seed)


def hsv(h: float, s: float, v: float):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_font(size: int, mono: bool = False):
    candidates = []
    if mono:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ---- poster frame -----------------------------------------------------------
def poster_frame(img: Image.Image, title: str, subtitle: str = "") -> Image.Image:
    """Wrap a raw render with an editorial caption bar."""
    W = img.width
    bar_h = 96
    out = Image.new("RGB", (W, img.height + bar_h), PAPER)
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    d.rectangle([0, img.height, W, img.height + bar_h], fill=PAPER)
    d.line([(0, img.height), (W, img.height)], fill=TEAL, width=2)
    title_font = load_font(28)
    sub_font = load_font(16, mono=True)
    d.text((28, img.height + 18), title, fill=INK, font=title_font)
    if subtitle:
        d.text((28, img.height + 56), subtitle, fill=MUTED, font=sub_font)
    return out


# ---- creature sprites (reused by libresprite + godot) ------------------------
def creature_sprite(seed: int, size: int = 32) -> Image.Image:
    """Tiny symmetric pixel-art creature."""
    rng = seeded(seed)
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = PALETTE_CREATURE[seed % len(PALETTE_CREATURE)]
    accent = PALETTE_CREATURE[(seed + 3) % len(PALETTE_CREATURE)]
    cx = size // 2
    cy = size // 2 + 2
    # body ellipse
    d.ellipse([cx - 10, cy - 8, cx + 10, cy + 9], fill=body, outline=INK)
    # belly
    d.ellipse([cx - 6, cy - 2, cx + 6, cy + 7], fill=accent)
    # head
    head_y = cy - 12
    d.ellipse([cx - 7, head_y - 7, cx + 7, head_y + 5], fill=body, outline=INK)
    # eyes symmetric
    d.ellipse([cx - 4, head_y - 2, cx - 2, head_y], fill=INK)
    d.ellipse([cx + 2, head_y - 2, cx + 4, head_y], fill=INK)
    # antennae
    for dx in (-4, 4):
        d.line([(cx + dx, head_y - 6), (cx + dx * 2, head_y - 10)], fill=INK)
        d.ellipse([cx + dx * 2 - 1, head_y - 11, cx + dx * 2 + 1, head_y - 9], fill=accent)
    # legs
    for i, lx in enumerate((cx - 7, cx - 3, cx + 3, cx + 7)):
        ly = cy + 8 + (i % 2)
        d.line([(lx, cy + 6), (lx + (1 if i % 2 else -1), ly)], fill=INK, width=1)
    return img


def creature_frame(seed: int, frame_idx: int, total_frames: int = 4, size: int = 32) -> Image.Image:
    """Animated idle: bob up/down, blink at frame 2."""
    base = creature_sprite(seed, size)
    dy = [0, -1, 0, -1][frame_idx % 4]
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.paste(base, (0, dy), base)
    if frame_idx % 4 == 2:  # blink
        d = ImageDraw.Draw(canvas)
        head_y = size // 2 + 2 - 12 + dy
        cx = size // 2
        d.line([(cx - 4, head_y - 1), (cx - 2, head_y - 1)], fill=INK)
        d.line([(cx + 2, head_y - 1), (cx + 4, head_y - 1)], fill=INK)
    return canvas


# ---- textured dataset tile (for GIMP case) ----------------------------------
def synthetic_photo_tile(seed: int, size: int = 256) -> Image.Image:
    """Procedural 'satellite-like' tile for AI-training dataset mock."""
    rng = seeded(seed)
    img = Image.new("RGB", (size, size), (40, 50, 45))
    d = ImageDraw.Draw(img)
    # base noise via random rectangles
    for _ in range(180):
        x0 = rng.randint(0, size - 1)
        y0 = rng.randint(0, size - 1)
        w = rng.randint(2, 16)
        h = rng.randint(2, 16)
        h_ = rng.random()
        col = hsv(0.25 + h_ * 0.15, 0.35 + rng.random() * 0.3, 0.25 + rng.random() * 0.4)
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=col)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.2))
    # roads
    d = ImageDraw.Draw(img)
    for _ in range(rng.randint(1, 3)):
        if rng.random() < 0.5:
            y = rng.randint(0, size)
            d.line([(0, y), (size, y + rng.randint(-20, 20))], fill=(120, 118, 110), width=rng.randint(4, 7))
        else:
            x = rng.randint(0, size)
            d.line([(x, 0), (x + rng.randint(-20, 20), size)], fill=(120, 118, 110), width=rng.randint(4, 7))
    # buildings (target class)
    bboxes = []
    for _ in range(rng.randint(3, 8)):
        w = rng.randint(18, 36)
        h = rng.randint(18, 36)
        x = rng.randint(4, size - w - 4)
        y = rng.randint(4, size - h - 4)
        col = hsv(0.08 + rng.random() * 0.08, 0.25, 0.6 + rng.random() * 0.2)
        d.rectangle([x, y, x + w, y + h], fill=col, outline=(50, 40, 35))
        bboxes.append({"x": x, "y": y, "w": w, "h": h, "label": "building"})
    return img, bboxes


def synthetic_photo_mask(bboxes, size: int = 256) -> Image.Image:
    """Binary building mask matching the tile."""
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    for b in bboxes:
        d.rectangle([b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]], fill=255)
    return mask


# ---- icon primitives (Inkscape case) ----------------------------------------
def svg_icon(name: str, seed: int, size: int = 96) -> str:
    """Produce a clean 2-color pictogram SVG string."""
    rng = seeded(seed)
    s = size
    cx, cy = s // 2, s // 2
    teal = "#2E7A7B"
    amber = "#D9A441"
    ink = "#141A21"
    paper = "#F7F4ED"

    shapes = []
    kind = seed % 6
    if kind == 0:  # layered circles
        for i, (col, r) in enumerate(((teal, 34), (amber, 24), (ink, 8))):
            shapes.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>')
    elif kind == 1:  # grid of 3x3 dots
        for r in range(3):
            for c in range(3):
                col = teal if (r + c) % 2 == 0 else amber
                shapes.append(f'<circle cx="{24 + c * 24}" cy="{24 + r * 24}" r="6" fill="{col}"/>')
    elif kind == 2:  # chevrons
        for i, y in enumerate((24, 44, 64)):
            col = teal if i % 2 == 0 else amber
            shapes.append(f'<polyline points="16,{y+10} {cx},{y} {s-16},{y+10}" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>')
    elif kind == 3:  # hex
        pts = []
        for k in range(6):
            a = math.pi / 3 * k - math.pi / 2
            pts.append(f"{cx + 32 * math.cos(a):.1f},{cy + 32 * math.sin(a):.1f}")
        shapes.append(f'<polygon points="{" ".join(pts)}" fill="{teal}"/>')
        shapes.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{amber}"/>')
    elif kind == 4:  # stacked bars
        for i, bw in enumerate((48, 36, 24)):
            shapes.append(f'<rect x="{cx - bw/2}" y="{24 + i * 18}" width="{bw}" height="10" rx="3" fill="{teal if i %2==0 else amber}"/>')
    else:  # ring + slice
        shapes.append(f'<circle cx="{cx}" cy="{cy}" r="32" fill="none" stroke="{teal}" stroke-width="8"/>')
        shapes.append(f'<path d="M{cx},{cy} L{cx+32},{cy} A32,32 0 0 1 {cx},{cy+32} Z" fill="{amber}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {s} {s}" width="{s}" height="{s}">
  <rect width="{s}" height="{s}" fill="{paper}"/>
  {''.join(shapes)}
  <text x="{cx}" y="{s-8}" text-anchor="middle" font-family="DejaVu Sans, Inter, sans-serif" font-size="10" fill="{ink}">{name}</text>
</svg>'''


# ---- 3D-ish iso scene (Blender case placeholder render) ---------------------
def iso_scene(seed: int, W: int = 960, H: int = 540) -> Image.Image:
    """Flat-shaded iso projection of a random object grid (no Blender needed)."""
    rng = seeded(seed)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # ground
    d.rectangle([0, H * 0.62, W, H], fill=(232, 225, 210))
    cx = W // 2
    cy = int(H * 0.72)
    tile = 34
    # grid of 5x5 cubes w/ heights
    for row in range(-2, 3):
        for col in range(-2, 3):
            h = rng.randint(24, 86)
            px = cx + (col - row) * tile
            py = cy + (col + row) * (tile // 2) - h
            col_hue = 0.08 + rng.random() * 0.12
            top = hsv(col_hue, 0.25, 0.85)
            left = hsv(col_hue, 0.3, 0.6)
            right = hsv(col_hue, 0.3, 0.72)
            # top diamond
            d.polygon([(px, py), (px + tile, py + tile // 2),
                       (px, py + tile), (px - tile, py + tile // 2)], fill=top, outline=INK)
            # left face
            d.polygon([(px - tile, py + tile // 2), (px, py + tile),
                       (px, py + tile + h), (px - tile, py + tile // 2 + h)], fill=left, outline=INK)
            # right face
            d.polygon([(px, py + tile), (px + tile, py + tile // 2),
                       (px + tile, py + tile // 2 + h), (px, py + tile + h)], fill=right, outline=INK)
    return img


def write_json(path: Path, data) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2))
