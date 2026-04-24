# 2D & 3D Digital Media Portfolio — AI Dataset Assets

**Katherine Feemster** · 2D & 3D Digital Media Specialist

Tool-agnostic, code-first digital media for an AI research program. Every asset
in this repo — 64 segmentation tiles, 24 pictograms, 12 painted scenes, 32
animated sprites, 48 rendered 3D frames, and the Godot viewer that loads them
all — is produced by a single reproducible Python pipeline that writes real
project files for **GIMP**, **Inkscape**, **Krita**, **Libresprite**,
**Blender** and **Godot**.

## What is here

| Case                                                                         | Tool         | Language      | What it proves                                                                       |
|------------------------------------------------------------------------------|--------------|---------------|--------------------------------------------------------------------------------------|
| [GIMP · batch segmentation dataset](cases/gimp/)                             | GIMP 2.10    | Script-Fu     | Headless Script-Fu batch pipeline: levels → unsharp → flatten → export. 64 tiles.    |
| [Inkscape · parametric pictogram set](cases/inkscape/)                       | Inkscape 1.3 | CLI actions   | `inkscape --actions=export-type:png` over 24 SVG pictograms at 2× DPI.               |
| [Krita · painted scene layer exporter](cases/krita/)                         | Krita 5.2    | Python plugin | Krita Python plugin exports each paint layer as image + mask + COCO label.           |
| [Libresprite · creature atlas](cases/libresprite/)                           | Libresprite  | Lua           | CLI Lua script packs 32 creatures × 4 frames into atlas.png + JSON Hash.             |
| [Blender · headless dataset render](cases/blender/)                          | Blender 4.x  | bpy / Python  | `blender --background --python` renders 48 frames with bbox + mask + COCO.           |
| [Godot · unified asset viewer](cases/godot/viewer/)                          | Godot 4      | GDScript      | `DirAccess` loader pulls every PNG from the other five cases into one runtime grid.  |

## Live preview

The GitHub Pages site shows the hero artefact of each case:

- `assets/gimp/preview.png` — 64-tile segmentation contact sheet.
- `assets/inkscape/icons_sheet.png` — 24 pictograms in a 6 × 4 grid.
- `assets/krita/preview.png` — 12 painted scenes with per-layer masks.
- `assets/libresprite/poster.png` — 32 creatures × 4 frames, upscaled 4×.
- `assets/blender/preview.png` — eight frames sampled from the 48-frame set.
- `assets/godot/preview.png` — Godot runtime loading every asset above.

## Reproducibility

```bash
pip install pillow cairosvg
python3 src/run_all.py
```

`run_all.py` chains six stages, none of which needs the native tool installed —
Pillow + cairosvg produce the deterministic raster outputs, and each case
*also* emits the native project file that opens in the real tool:

1. `build_gimp_case.py` — 64 tiles + binary masks + `batch.scm` + manifest.
2. `build_inkscape_case.py` — 24 SVGs + raster sheet + `render.sh` CLI.
3. `build_krita_case.py` — 12 real `.kra` archives + merged PNG + labels + Python plugin.
4. `build_libresprite_case.py` — `atlas.png` + `atlas.json` + `build_atlas.lua`.
5. `build_blender_case.py` — 48 frames + masks + `coco.json` + `render_dataset.py`.
6. `build_godot_case.py` — full Godot 4 project in `cases/godot/viewer/`.

Dependencies are deliberately small: `Pillow`, `cairosvg`. Installing GIMP,
Inkscape, Krita, Libresprite, Blender or Godot is only needed to **run** the
generated project files — not to regenerate the portfolio.

## Editorial style

- **Color**: teal `#2E7A7B` + amber `#D9A441` on ink `#141A21` / paper `#F7F4ED`.
- **Type**: Inter (UI) + JetBrains Mono (code).
- **Determinism**: every generator is seeded; all PNG bytes are stable.
- **Licensing**: all six tools are FOSS. No commercial SDKs in the dependency tree.

## Repo layout

```
media-portfolio/
├── src/                         # 6 generators + art_helpers.py
├── cases/                       # one folder per tool with the native project file
│   ├── gimp/batch.scm
│   ├── inkscape/render.sh
│   ├── krita/layer_export.py
│   ├── libresprite/build_atlas.lua
│   ├── blender/render_dataset.py
│   └── godot/viewer/            # full Godot 4 project
├── assets/                      # generated outputs (renders, masks, labels)
├── docs/                        # GitHub Pages site
└── .github/workflows/           # CI re-runs the pipeline on each push
```

## About the author

Senior 2D & 3D digital media specialist shipping cross-tool asset pipelines —
most recently focused on dataset generation and labelling workflows for AI
research programs. Comfortable owning a project from tool selection through
native scripting, headless rendering and CI automation.

- GitHub: [katherinejenniferhsfeemster](https://github.com/katherinejenniferhsfeemster)
