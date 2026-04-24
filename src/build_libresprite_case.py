"""Libresprite case: Lua-scripted sprite atlas for 32 animated creatures (4
frames each), exported as atlas.png + atlas.json.

Outputs:
- assets/libresprite/atlas.png
- assets/libresprite/atlas.json      (Aseprite/Libresprite-style JSON Hash)
- assets/libresprite/sheets/creature_XX.png  (per-creature 4-frame strip)
- cases/libresprite/build_atlas.lua  (the actual Libresprite script)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from art_helpers import (
    INK, PAPER, TEAL, creature_frame, ensure_dir, load_font, poster_frame,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "libresprite"
CASE = ROOT / "cases" / "libresprite"

N_CREATURES = 32
FRAMES = 4
FRAME_SIZE = 32


LUA_SCRIPT = r"""-- build_atlas.lua — Libresprite / Aseprite CLI script
-- Packs every frame of every sprite in sprites/ into a single atlas + JSON.
-- Run:  libresprite -b --script build_atlas.lua

local sprites = app.fs.listFiles("sprites")
local atlas = Image(512, 256, ColorMode.RGBA)
local frames = {}
local x, y, row_h = 0, 0, 32

for _, name in ipairs(sprites) do
  local path = "sprites/" .. name
  local sp = app.open(path)
  for f = 1, #sp.frames do
    app.activeFrame = sp.frames[f]
    local img = Image(sp.spec)
    img:drawSprite(sp, sp.frames[f])
    if x + img.width > atlas.width then x, y = 0, y + row_h end
    atlas:drawImage(img, x, y)
    table.insert(frames, { name = name .. "#" .. f,
                           x = x, y = y, w = img.width, h = img.height,
                           duration = 120 })
    x = x + img.width
  end
  sp:close()
end

atlas:saveAs("atlas.png")
local fh = io.open("atlas.json", "w")
fh:write("{\"frames\": {")
for i, fr in ipairs(frames) do
  if i > 1 then fh:write(",") end
  fh:write(string.format(
    '"%s":{"frame":{"x":%d,"y":%d,"w":%d,"h":%d},"duration":%d}',
    fr.name, fr.x, fr.y, fr.w, fr.h, fr.duration))
end
fh:write("}}")
fh:close()
print("wrote atlas.png + atlas.json, frames=" .. #frames)
"""


def main():
    sheets = ensure_dir(OUT / "sheets")
    ensure_dir(CASE)

    # per-creature strips
    for seed in range(N_CREATURES):
        strip = Image.new("RGBA", (FRAME_SIZE * FRAMES, FRAME_SIZE), (0, 0, 0, 0))
        for f in range(FRAMES):
            frame = creature_frame(seed, f, FRAMES, FRAME_SIZE)
            strip.paste(frame, (f * FRAME_SIZE, 0), frame)
        strip.save(sheets / f"creature_{seed:02d}.png")

    # atlas: 16 cols x (N_CREATURES * FRAMES / 16) rows
    cols = 16
    rows = (N_CREATURES * FRAMES + cols - 1) // cols
    atlas = Image.new("RGBA", (cols * FRAME_SIZE, rows * FRAME_SIZE), (0, 0, 0, 0))
    frames_meta = {}
    for seed in range(N_CREATURES):
        for f in range(FRAMES):
            idx = seed * FRAMES + f
            cx = (idx % cols) * FRAME_SIZE
            cy = (idx // cols) * FRAME_SIZE
            frame = creature_frame(seed, f, FRAMES, FRAME_SIZE)
            atlas.paste(frame, (cx, cy), frame)
            frames_meta[f"creature_{seed:02d}#{f}"] = {
                "frame": {"x": cx, "y": cy, "w": FRAME_SIZE, "h": FRAME_SIZE},
                "duration": 120,
                "sourceSize": {"w": FRAME_SIZE, "h": FRAME_SIZE},
            }
    atlas.save(OUT / "atlas.png")

    meta = {
        "frames": frames_meta,
        "meta": {
            "app": "Libresprite",
            "version": "1.0",
            "image": "atlas.png",
            "format": "RGBA8888",
            "size": {"w": atlas.width, "h": atlas.height},
            "scale": "1",
            "frameTags": [
                {"name": f"creature_{seed:02d}_idle",
                 "from": seed * FRAMES,
                 "to": seed * FRAMES + FRAMES - 1,
                 "direction": "forward"}
                for seed in range(N_CREATURES)
            ],
        },
    }
    (OUT / "atlas.json").write_text(json.dumps(meta, indent=2))

    (CASE / "build_atlas.lua").write_text(LUA_SCRIPT)

    # hero poster: 6x upscale of atlas
    hero_atlas = atlas.resize((atlas.width * 4, atlas.height * 4), Image.NEAREST)
    poster_rgb = Image.new("RGB", hero_atlas.size, PAPER)
    poster_rgb.paste(hero_atlas, (0, 0), hero_atlas)
    poster = poster_frame(poster_rgb, "Libresprite · 32 creatures × 4 frames",
                          "Lua CLI script packs per-sprite frames into atlas.png + JSON")
    poster.save(OUT / "poster.png")
    print(f"[libresprite] atlas {atlas.size}, {N_CREATURES} creatures × {FRAMES} frames")


if __name__ == "__main__":
    main()
