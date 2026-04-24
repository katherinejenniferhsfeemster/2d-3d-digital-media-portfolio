# GIMP · Batch segmentation dataset

**Tool**: GIMP 2.10 · **Language**: Script-Fu (TinyScheme)

A headless Script-Fu pipeline that preps an overhead-imagery building
segmentation dataset: 64 synthetic 256 × 256 tiles are loaded, their exposure
is normalised, edges are sharpened, the layer stack is flattened, and PNG is
exported. Each tile ships with a binary mask and bbox annotations so the
output is drop-in-ready for an AI training loop.

## Run

```bash
gimp -i \
  -b '(batch-prepare-dataset "assets/gimp/tiles" "assets/gimp/out")' \
  -b '(gimp-quit 0)'
```

## Script-Fu highlights

The meat of [`batch.scm`](batch.scm) is three operations per tile:

1. `gimp-levels-stretch` — auto-expose so the dataset has consistent histogram.
2. `plug-in-unsharp-mask` (radius 1.2, amount 0.4) — stable edge emphasis.
3. `gimp-image-flatten` → `file-png-save` — predictable PNG bytes per tile.

## Outputs

- `assets/gimp/tiles/tile_000.png` … `tile_063.png` — RGB 256 × 256.
- `assets/gimp/masks/tile_000.png` … `tile_063.png` — L-mode binary masks.
- `assets/gimp/manifest.json` — per-tile bboxes + pipeline metadata.
- `assets/gimp/preview.png` — 8 × 8 contact sheet.

## Why Script-Fu

GIMP's Script-Fu runs inside the GIMP process with zero IPC overhead, which
matters when a dataset gets large. The same logic is portable to Python-Fu if
a team prefers it.
