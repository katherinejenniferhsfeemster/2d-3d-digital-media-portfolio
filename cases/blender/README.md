# Blender · Headless dataset render

**Tool**: Blender 4.x · **Language**: Python (bpy)

A `bpy` script that builds a procedural 3D scene — 20 randomised primitives
(cubes, spheres, cylinders, cones) with randomised PBR materials and a single
sun light — and renders 48 frames at 960 × 540 with per-object COCO-style
annotations suitable for training 3D detection models.

## Run

```bash
blender --background --python render_dataset.py -- --frames 48 --out ./out
```

[`render_dataset.py`](render_dataset.py) does:

1. `reset_scene()` — empty scene, Cycles, 64 samples, transparent film.
2. `random_object()` × 20 — seeded geometry + palette materials.
3. `world_to_camera_view()` — projects each object centre into pixel space.
4. Writes `frame_###.png`, `frame_###_mask.png`, `frame_###.json`.

## Outputs

- `assets/blender/renders/frame_000.png` … `frame_047.png` — RGB 960 × 540.
- `assets/blender/masks/frame_*.png` — segmentation (class-indexed).
- `assets/blender/annotations/frame_*.json` — per-frame per-object list.
- `assets/blender/coco.json` — dataset-level COCO file, 960 annotations.
- `assets/blender/preview.png` — 8-frame sample sheet.

## Why Blender + bpy

`bpy` runs Blender as a Python library. Combined with `--background` it
renders in a headless CI container, which is the only sensible way to ship
reproducible 3D dataset pipelines.
