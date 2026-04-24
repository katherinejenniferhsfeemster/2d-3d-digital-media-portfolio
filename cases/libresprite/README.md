# Libresprite · Creature sprite atlas

**Tool**: Libresprite (Aseprite-compatible) · **Language**: Lua

A 32-creature cast, each with a 4-frame idle loop (body bob + blink on frame 3).
All 128 frames pack into a single 512 × 256 atlas with a JSON Hash manifest,
ready for a game engine, an HTML canvas, or an AI training loop that learns
sprite anatomy.

## Run

```bash
libresprite -b --script build_atlas.lua
```

[`build_atlas.lua`](build_atlas.lua) walks every `.ase` / `.aseprite` file in
`sprites/`, blits each frame into the atlas canvas, and writes an
Aseprite-compatible JSON Hash (`atlas.json`) plus the packed PNG (`atlas.png`).

## Outputs

- `assets/libresprite/atlas.png` — 512 × 256, RGBA.
- `assets/libresprite/atlas.json` — JSON Hash with per-frame geometry +
  `frameTags` for each creature's idle animation.
- `assets/libresprite/sheets/creature_00.png` … `creature_31.png` — per-creature
  4-frame strips (128 × 32).
- `assets/libresprite/poster.png` — 4× nearest-neighbour blow-up of the atlas.

## Why Libresprite

Libresprite is the FOSS fork of Aseprite. Its Lua scripting API is ~95%
compatible, so the same pipeline is portable if a team later licenses
Aseprite. JSON Hash output is the de-facto standard consumed by Phaser, Godot,
Unity and PixiJS.
