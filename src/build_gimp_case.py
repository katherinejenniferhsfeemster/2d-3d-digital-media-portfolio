"""GIMP case: batch Script-Fu pipeline that normalizes, masks, and exports a
synthetic overhead-imagery dataset for an AI building-segmentation task.

When run here (no GIMP binary in sandbox), we produce:
- assets/gimp/tiles/*.png     (64 synthetic tiles)
- assets/gimp/masks/*.png     (binary building masks)
- assets/gimp/preview.png     (contact sheet)
- cases/gimp/batch.scm         (the Script-Fu batch script that GIMP would run)
- cases/gimp/manifest.json    (dataset manifest with per-tile bboxes)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from art_helpers import (
    AMBER, INK, PAPER, TEAL, ensure_dir, load_font, poster_frame,
    synthetic_photo_mask, synthetic_photo_tile, write_json,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "gimp"
CASE = ROOT / "cases" / "gimp"

SCRIPT_FU = r"""; batch.scm — GIMP 2.10 Script-Fu
; Batch-normalize, mask, and export a dataset for AI building segmentation.
; Invoke:
;   gimp -i -b '(batch-prepare-dataset "assets/gimp/tiles" "assets/gimp/out")' -b '(gimp-quit 0)'

(define (batch-prepare-dataset in-dir out-dir)
  (let* ((files (cadr (file-glob (string-append in-dir "/*.png") 1))))
    (for-each
      (lambda (path)
        (let* ((img   (car (gimp-file-load RUN-NONINTERACTIVE path path)))
               (draw  (car (gimp-image-get-active-drawable img)))
               (base  (car (gimp-image-get-name img))))
          ; 1. auto levels (normalize exposure)
          (gimp-levels-stretch draw)
          ; 2. unsharp mask (mild, radius 1.2, amount 0.4)
          (plug-in-unsharp-mask RUN-NONINTERACTIVE img draw 1.2 0.4 0)
          ; 3. flatten + export PNG
          (gimp-image-flatten img)
          (file-png-save RUN-NONINTERACTIVE img
                         (car (gimp-image-get-active-drawable img))
                         (string-append out-dir "/" base)
                         base 0 9 1 1 1 1 1)
          (gimp-image-delete img)))
      files)))
"""


def build_contact_sheet(tile_paths, out_path: Path, cols: int = 8, tile: int = 128):
    n = len(tile_paths)
    rows = (n + cols - 1) // cols
    W = cols * tile + (cols + 1) * 6
    H = rows * tile + (rows + 1) * 6 + 64
    sheet = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 0, W, 48], fill=TEAL)
    font = load_font(20)
    d.text((16, 12), "GIMP · AI Building Segmentation Dataset", fill=PAPER, font=font)
    for i, p in enumerate(tile_paths):
        c = i % cols
        r = i // cols
        x = 6 + c * (tile + 6)
        y = 54 + r * (tile + 6)
        im = Image.open(p).resize((tile, tile))
        sheet.paste(im, (x, y))
    sheet.save(out_path)


def main():
    tiles_dir = ensure_dir(OUT / "tiles")
    masks_dir = ensure_dir(OUT / "masks")
    ensure_dir(CASE)

    manifest = {"tiles": [], "meta": {
        "tool": "GIMP 2.10 (Script-Fu)", "pipeline": "load → levels stretch → unsharp → flatten → export",
        "task": "AI building segmentation dataset prep"}}
    tile_paths = []
    for i in range(64):
        img, bboxes = synthetic_photo_tile(1000 + i, 256)
        mask = synthetic_photo_mask(bboxes, 256)
        tile_path = tiles_dir / f"tile_{i:03d}.png"
        mask_path = masks_dir / f"tile_{i:03d}.png"
        img.save(tile_path)
        mask.save(mask_path)
        tile_paths.append(tile_path)
        manifest["tiles"].append({
            "image": f"tiles/tile_{i:03d}.png",
            "mask": f"masks/tile_{i:03d}.png",
            "bboxes": bboxes,
        })

    write_json(OUT / "manifest.json", manifest)
    (CASE / "batch.scm").write_text(SCRIPT_FU)
    build_contact_sheet(tile_paths, OUT / "preview.png")

    # hero poster
    hero = Image.open(tile_paths[0]).resize((960, 540))
    poster = poster_frame(hero, "GIMP · building segmentation tile",
                          "Script-Fu: levels stretch → unsharp → flatten → export")
    poster.save(OUT / "poster.png")

    print(f"[gimp] {len(tile_paths)} tiles + masks, manifest, Script-Fu written")


if __name__ == "__main__":
    main()
