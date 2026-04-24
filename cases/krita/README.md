# Krita · Painted scene layer exporter

**Tool**: Krita 5.2 · **Interface**: Krita Python plugin

A painted-scene dataset where every paint layer becomes a separate
segmentation mask. 12 seeded scenes are produced as real `.kra` archives
(Krita's native ZIP-based format) each shipping with a merged PNG, a single
mask, and a COCO-style `labels.json` that ties every visible subject to its
bounding box and mask value.

## Install the plugin

Copy [`layer_export.py`](layer_export.py) into your Krita Python plugin
directory — on Linux that is `~/.config/krita-5.2.0/pykrita/`. Enable it via
**Settings ▸ Configure Krita ▸ Python Plugin Manager**. The plugin exposes
an `export_document(out_dir)` function callable from the **Scripter**.

## Run the export

```python
from layer_export import export_document
export_document("/tmp/dataset_out")
```

That walks the currently active document, hides everything except one layer
at a time, exports each into its own mask PNG, and writes a combined
`labels.json`.

## Outputs

- `assets/krita/scenes/scene_00.kra` … `scene_11.kra` — real Krita archives.
- `assets/krita/renders/scene_*.png` — merged RGB renders.
- `assets/krita/masks/scene_*.png` — combined L-mode masks.
- `assets/krita/labels/scene_*.json` — per-scene annotations.
- `assets/krita/preview.png` — 4 × 3 contact sheet.

## Why Krita

Krita's Python API exposes the paint graph directly — every `Node` is
scriptable, which makes layer-driven dataset prep much cleaner than
screen-scraping a commercial paint tool.
