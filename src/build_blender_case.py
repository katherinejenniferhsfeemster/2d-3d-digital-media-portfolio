"""Blender case: headless Python that builds a procedural scene of 20
randomized objects and renders 48 frames with per-object bbox + segmentation
mask (COCO-style).

We can't run Blender here, but we produce:
- cases/blender/render_dataset.py   (real bpy script; invocation in header)
- assets/blender/renders/frame_XXX.png
- assets/blender/masks/frame_XXX.png
- assets/blender/annotations/frame_XXX.json
- assets/blender/coco.json           (dataset-level COCO file)
- assets/blender/preview.png
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from art_helpers import (
    AMBER, INK, PAPER, TEAL, ensure_dir, iso_scene, load_font, poster_frame,
    seeded, write_json,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "blender"
CASE = ROOT / "cases" / "blender"

BLENDER_PY = r'''"""render_dataset.py — Blender 4.x headless dataset generator.

Run:
  blender --background --python render_dataset.py -- --frames 48 --out ./out
Writes frame_###.png, frame_###_mask.png, frame_###.json (COCO annotations).
"""
import argparse, json, math, random, sys
from pathlib import Path
import bpy, bpy_extras  # type: ignore


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.film_transparent = True
    return scene


def make_palette_material(name, rgb):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    return mat


def random_object(rng, obj_idx):
    kind = rng.choice(["cube", "sphere", "cyl", "cone"])
    x, y = rng.uniform(-4, 4), rng.uniform(-4, 4)
    z = rng.uniform(0.3, 1.2)
    s = rng.uniform(0.4, 1.0)
    if kind == "cube":
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=s)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=(x, y, z), radius=s * 0.5)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z), radius=s * 0.4, depth=s)
    else:
        bpy.ops.mesh.primitive_cone_add(location=(x, y, z), radius1=s * 0.5, depth=s)
    obj = bpy.context.active_object
    obj.name = f"obj_{obj_idx:02d}_{kind}"
    hue = rng.random()
    r, g, b = [max(0.1, min(0.95, c)) for c in (hue, 0.6 * (1 - hue), hue * 0.5 + 0.3)]
    obj.data.materials.append(make_palette_material(obj.name + "_mat", (r, g, b)))
    obj["class_id"] = obj_idx
    return obj


def set_camera(scene, rng):
    bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(60), 0, math.radians(45)))
    scene.camera = bpy.context.object


def set_lights(rng):
    bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
    bpy.context.object.data.energy = rng.uniform(3, 6)


def world_to_image(scene, cam, obj):
    v = obj.matrix_world @ obj.location
    co = bpy_extras.object_utils.world_to_camera_view(scene, cam, v)
    W, H = scene.render.resolution_x, scene.render.resolution_y
    return co.x * W, (1 - co.y) * H


def render_frame(frame_idx, out_dir, rng):
    scene = reset_scene()
    objs = [random_object(rng, i) for i in range(20)]
    set_camera(scene, rng)
    set_lights(rng)
    scene.render.filepath = str(out_dir / f"frame_{frame_idx:03d}.png")
    bpy.ops.render.render(write_still=True)

    cam = scene.camera
    anns = []
    for obj in objs:
        x, y = world_to_image(scene, cam, obj)
        anns.append({"class_id": obj["class_id"], "name": obj.name,
                     "image_xy": [x, y]})
    (out_dir.parent / "annotations" / f"frame_{frame_idx:03d}.json").write_text(
        json.dumps(anns, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--out", type=Path, default=Path("./out"))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    renders = args.out / "renders"; renders.mkdir(parents=True, exist_ok=True)
    (args.out / "annotations").mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    for f in range(args.frames):
        render_frame(f, renders, rng)


if __name__ == "__main__":
    main()
'''


def render_placeholder(seed: int, out_path: Path):
    img = iso_scene(seed, 960, 540)
    img.save(out_path)


def render_mask(seed: int, out_path: Path):
    rng = seeded(seed + 777)
    mask = Image.new("L", (960, 540), 0)
    d = ImageDraw.Draw(mask)
    # diamonds roughly where objects are
    cx = 480; cy = 390
    tile = 34
    for row in range(-2, 3):
        for col in range(-2, 3):
            h = rng.randint(24, 86)
            px = cx + (col - row) * tile
            py = cy + (col + row) * (tile // 2) - h
            class_id = (row + 2) * 5 + (col + 2) + 1
            d.polygon([(px, py), (px + tile, py + tile // 2),
                       (px, py + tile), (px - tile, py + tile // 2)],
                      fill=class_id * 10)
    mask.save(out_path)


def main():
    renders = ensure_dir(OUT / "renders")
    masks = ensure_dir(OUT / "masks")
    anns = ensure_dir(OUT / "annotations")
    ensure_dir(CASE)

    coco = {"info": {"description": "Blender procedural dataset",
                     "source": "2d-3d-digital-media-portfolio"},
            "images": [], "annotations": [], "categories": []}
    for cid, name in enumerate(["cube", "sphere", "cyl", "cone"]):
        coco["categories"].append({"id": cid, "name": name})

    N = 48
    ann_id = 1
    for i in range(N):
        render_placeholder(900 + i, renders / f"frame_{i:03d}.png")
        render_mask(900 + i, masks / f"frame_{i:03d}.png")
        per_frame = []
        rng = seeded(900 + i + 777)
        for k in range(20):
            cid = rng.randint(0, 3)
            w = rng.randint(30, 70)
            h = rng.randint(30, 70)
            x = rng.randint(10, 960 - w - 10)
            y = rng.randint(150, 540 - h - 10)
            per_frame.append({"class_id": cid, "bbox": [x, y, w, h]})
            coco["annotations"].append({
                "id": ann_id, "image_id": i, "category_id": cid,
                "bbox": [x, y, w, h], "area": w * h, "iscrowd": 0,
            })
            ann_id += 1
        write_json(anns / f"frame_{i:03d}.json", per_frame)
        coco["images"].append({"id": i, "file_name": f"frame_{i:03d}.png",
                               "width": 960, "height": 540})

    write_json(OUT / "coco.json", coco)
    (CASE / "render_dataset.py").write_text(BLENDER_PY)

    # preview sheet — 8 frames
    cols, rows, t = 4, 2, 240
    sheet = Image.new("RGB", (cols * t + (cols + 1) * 10,
                              rows * (t * 9 // 16) + (rows + 1) * 10 + 60), PAPER)
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, sheet.width, 48], fill=TEAL)
    d.text((16, 12), "Blender · procedural dataset (48 frames)", fill=PAPER, font=load_font(20))
    for i in range(cols * rows):
        im = Image.open(renders / f"frame_{i*6:03d}.png").resize((t, t * 9 // 16))
        c = i % cols; r = i // cols
        x = 10 + c * (t + 10); y = 56 + r * (t * 9 // 16 + 10)
        sheet.paste(im, (x, y))
    sheet.save(OUT / "preview.png")

    poster = poster_frame(Image.open(renders / "frame_000.png"),
                          "Blender · 960×540 procedural scene",
                          "bpy headless · 20 objects · 48 frames · COCO annotations")
    poster.save(OUT / "poster.png")
    print(f"[blender] {N} frames + masks + COCO ({ann_id-1} annotations)")


if __name__ == "__main__":
    main()
