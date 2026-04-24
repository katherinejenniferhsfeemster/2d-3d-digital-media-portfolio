"""Inkscape case: parametric SVG pictogram set driven by Inkscape CLI actions.

Produces:
- assets/inkscape/icons/icon_XX.svg
- assets/inkscape/icons_sheet.png       (raster contact sheet)
- assets/inkscape/icons_sheet.svg       (SVG contact sheet)
- cases/inkscape/render.sh              (the Inkscape --actions CLI invocation)
"""
from __future__ import annotations

from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw

from art_helpers import (
    AMBER, INK, PAPER, TEAL, ensure_dir, load_font, poster_frame, svg_icon,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "inkscape"
CASE = ROOT / "cases" / "inkscape"

ICON_NAMES = [
    "dataset", "model", "layer", "mask", "render", "export",
    "noise", "filter", "sample", "label", "atlas", "tile",
    "camera", "light", "mesh", "uv", "bone", "anim",
    "pipeline", "manifest", "split", "train", "eval", "deploy",
]


RENDER_SH = r"""#!/usr/bin/env bash
# Batch-export every SVG in icons/ to PNG at 2x using Inkscape's CLI action API.
set -euo pipefail
mkdir -p png@2x
for f in icons/*.svg; do
  name=$(basename "$f" .svg)
  inkscape "$f" \
    --actions="export-type:png; export-dpi:192; export-filename:png@2x/${name}.png; export-do"
done
echo "exported $(ls png@2x | wc -l) icons"
"""


def main():
    icons_dir = ensure_dir(OUT / "icons")
    ensure_dir(CASE)

    png_tiles = []
    for i, name in enumerate(ICON_NAMES):
        svg = svg_icon(name, seed=200 + i, size=96)
        svg_path = icons_dir / f"icon_{i:02d}_{name}.svg"
        svg_path.write_text(svg)
        # rasterize via cairosvg for the sheet
        png_bytes = cairosvg.svg2png(bytestring=svg.encode(), output_width=192, output_height=192)
        png_path = OUT / f"_tmp_{i:02d}.png"
        png_path.write_bytes(png_bytes)
        png_tiles.append(png_path)

    # contact sheet (6 cols x 4 rows)
    cols, rows, t = 6, 4, 160
    W = cols * t + (cols + 1) * 12
    H = rows * t + (rows + 1) * 12 + 64
    sheet = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 48], fill=TEAL)
    d.text((16, 12), "Inkscape · pictogram set (24)", fill=PAPER, font=load_font(20))
    for i, p in enumerate(png_tiles):
        c = i % cols
        r = i // cols
        x = 12 + c * (t + 12)
        y = 60 + r * (t + 12)
        im = Image.open(p).resize((t, t))
        sheet.paste(im, (x, y))
    sheet.save(OUT / "icons_sheet.png")

    # cleanup tmp PNGs
    for p in png_tiles:
        p.unlink()

    (CASE / "render.sh").write_text(RENDER_SH)

    poster = poster_frame(Image.open(OUT / "icons_sheet.png").resize((960, 720)),
                          "Inkscape · 24 pictograms",
                          "inkscape --actions=export-type:png; export-dpi:192")
    poster.save(OUT / "poster.png")
    print(f"[inkscape] {len(ICON_NAMES)} SVG icons + sheet + CLI script")


if __name__ == "__main__":
    main()
