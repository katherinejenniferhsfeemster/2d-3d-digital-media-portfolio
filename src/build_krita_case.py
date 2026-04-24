"""Krita case: Python plugin that auto-exports each layer of a painted scene as
image, mask, and a COCO-style label.json for AI dataset prep.

We can't run Krita here, but:
- Every .kra file is a zipped OpenRaster-like bundle (content.xml + layers).
- We emit real .kra archives containing the painted image and a mergedimage.png
  so the artefact opens in Krita if installed.
- We also provide the Krita-Python plugin (layer_export.py) that would run inside
  Krita's Script menu.

Outputs:
- assets/krita/scenes/scene_XX.kra
- assets/krita/renders/scene_XX.png          (merged render)
- assets/krita/masks/scene_XX_mask.png       (segmentation mask)
- assets/krita/labels/scene_XX.json          (per-layer labels)
- assets/krita/preview.png                    (contact sheet)
- cases/krita/layer_export.py                 (Krita plugin source)
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from art_helpers import (
    AMBER, INK, PAPER, TEAL, ensure_dir, hsv, load_font, poster_frame, seeded, write_json,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "krita"
CASE = ROOT / "cases" / "krita"

PLUGIN_PY = r'''"""layer_export.py — Krita Python plugin.

Install: copy into ~/.config/krita-5.2.0/pykrita/ and enable via
Settings ▸ Configure Krita ▸ Python Plugin Manager ▸ "Layer Exporter".

Exports the current document as (image.png, mask.png, labels.json) where every
paint layer becomes one mask channel + a COCO-style annotation.
"""
import json
from pathlib import Path
from krita import Krita, InfoObject  # type: ignore


def export_document(out_dir: str) -> None:
    doc = Krita.instance().activeDocument()
    if doc is None:
        raise RuntimeError("No active document")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    info = InfoObject()
    info.setProperty("alpha", False)

    # merged image
    doc.exportImage(str(out / f"{doc.name()}.png"), info)

    labels = {"image": f"{doc.name()}.png", "width": doc.width(),
              "height": doc.height(), "annotations": []}

    # walk layers top-down
    for i, node in enumerate(doc.topLevelNodes()):
        if not node.visible():
            continue
        mask_name = f"{doc.name()}_mask_{i:02d}_{node.name()}.png"
        # clone doc, hide everything except this layer, export
        clone = doc.clone()
        for n in clone.topLevelNodes():
            n.setVisible(n.name() == node.name())
        clone.refreshProjection()
        clone.exportImage(str(out / mask_name), info)
        clone.close()

        labels["annotations"].append({
            "layer": node.name(),
            "mask": mask_name,
            "category": node.name().split("_")[0],
        })

    (out / f"{doc.name()}_labels.json").write_text(json.dumps(labels, indent=2))
    print(f"exported {len(labels['annotations'])} layers -> {out}")
'''

# minimal Krita .kra is a zip of OpenRaster-ish files:
# - mimetype (uncompressed, first)
# - mergedimage.png
# - maindoc.xml


def make_kra(path: Path, rendered_png_bytes: bytes, w: int, h: int, layers: list[str]) -> None:
    maindoc = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE DOC PUBLIC '-//KDE//DTD krita 2.0//EN' 'http://www.koffice.org/DTD/krita-2.0.dtd'>
<DOC xmlns="http://www.calligra.org/DTD/krita" kritaVersion="5.2.0" syntaxVersion="2.0" editor="Krita">
 <IMAGE name="scene" mime="application/x-kra" width="{w}" height="{h}" colorspacename="RGBA" x-res="300" y-res="300" description="2d-3d-digital-media-portfolio">
  <layers>
{''.join(f'   <layer name="{L}" filename="layer{idx}" visible="1" opacity="255" channelflags="" nodetype="paintlayer"/>\\n' for idx, L in enumerate(layers))}  </layers>
 </IMAGE>
</DOC>
'''
    with zipfile.ZipFile(path, "w") as z:
        # mimetype must be first and stored
        z.writestr(zipfile.ZipInfo("mimetype"), "application/x-krita",
                   compress_type=zipfile.ZIP_STORED)
        z.writestr("maindoc.xml", maindoc, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("mergedimage.png", rendered_png_bytes, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("preview.png", rendered_png_bytes, compress_type=zipfile.ZIP_DEFLATED)


def paint_scene(seed: int, w: int = 512, h: int = 384):
    rng = seeded(seed)
    img = Image.new("RGB", (w, h), hsv(0.55 + rng.random() * 0.1, 0.2, 0.85))
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    dm = ImageDraw.Draw(mask)
    labels = []

    # ground
    ground_y = int(h * 0.65)
    d.rectangle([0, ground_y, w, h], fill=hsv(0.1, 0.25, 0.55))

    # mountains
    for i in range(3):
        base_y = ground_y - 10 + i * 6
        peak = rng.randint(40, 120)
        mx = rng.randint(0, w)
        d.polygon([(mx - 180, base_y), (mx, base_y - peak), (mx + 180, base_y)],
                  fill=hsv(0.55, 0.3, 0.5 - i * 0.1))

    # subjects — 3 painted "creatures"
    classes = ["creatureA", "creatureB", "creatureC"]
    mask_id = 64
    for i, cls in enumerate(classes):
        cx = 90 + i * 160 + rng.randint(-10, 10)
        cy = ground_y - 30 - rng.randint(0, 20)
        col = hsv(i * 0.25 + 0.05, 0.6, 0.75)
        d.ellipse([cx - 30, cy - 24, cx + 30, cy + 24], fill=col, outline=INK)
        d.ellipse([cx - 8, cy - 6, cx - 2, cy], fill=INK)
        d.ellipse([cx + 2, cy - 6, cx + 8, cy], fill=INK)
        dm.ellipse([cx - 30, cy - 24, cx + 30, cy + 24], fill=mask_id + i * 64)
        labels.append({"class": cls, "bbox": [cx - 30, cy - 24, 60, 48],
                       "mask_value": mask_id + i * 64})

    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
    return img, mask, labels


def main():
    for sub in ("scenes", "renders", "masks", "labels"):
        ensure_dir(OUT / sub)
    ensure_dir(CASE)

    tile_paths = []
    for i in range(12):
        img, mask, labels = paint_scene(500 + i)
        png_path = OUT / "renders" / f"scene_{i:02d}.png"
        mask_path = OUT / "masks" / f"scene_{i:02d}_mask.png"
        kra_path = OUT / "scenes" / f"scene_{i:02d}.kra"
        label_path = OUT / "labels" / f"scene_{i:02d}.json"

        img.save(png_path)
        mask.save(mask_path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        make_kra(kra_path, buf.getvalue(), img.width, img.height,
                 [l["class"] for l in labels])
        write_json(label_path, {"scene": f"scene_{i:02d}", "annotations": labels,
                                "image": f"renders/scene_{i:02d}.png",
                                "mask": f"masks/scene_{i:02d}_mask.png"})
        tile_paths.append(png_path)

    # contact sheet
    cols, rows, t = 4, 3, 240
    W = cols * t + (cols + 1) * 12
    H = rows * (t * 3 // 4) + (rows + 1) * 12 + 64
    sheet = Image.new("RGB", (W, H), PAPER)
    dd = ImageDraw.Draw(sheet)
    dd.rectangle([0, 0, W, 48], fill=TEAL)
    dd.text((16, 12), "Krita · painted AI-dataset scenes", fill=PAPER, font=load_font(20))
    for i, p in enumerate(tile_paths):
        c = i % cols
        r = i // cols
        x = 12 + c * (t + 12)
        y = 60 + r * (t * 3 // 4 + 12)
        im = Image.open(p).resize((t, t * 3 // 4))
        sheet.paste(im, (x, y))
    sheet.save(OUT / "preview.png")

    (CASE / "layer_export.py").write_text(PLUGIN_PY)
    poster = poster_frame(Image.open(tile_paths[0]).resize((960, 540)),
                          "Krita · painted scene + layer-mask export",
                          "Krita Python plugin · per-layer PNG + COCO labels.json")
    poster.save(OUT / "poster.png")

    print(f"[krita] 12 scenes (.kra + png + mask + labels) + plugin written")


if __name__ == "__main__":
    main()
