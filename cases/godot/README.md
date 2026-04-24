# Godot · Unified asset viewer

**Tool**: Godot 4.2 · **Language**: GDScript

A full Godot 4 project at [`viewer/`](viewer/) that loads every PNG shipped
by the other five cases — GIMP tiles, Inkscape pictograms, Krita scenes,
Libresprite sheets, Blender frames — and arranges them in an 8-column grid
inside a single scene. One entrypoint to QA the whole pipeline end-to-end.

## Run

```bash
godot --path ./cases/godot/viewer
```

Or headless for screenshot tests:

```bash
godot --headless --path ./cases/godot/viewer
```

## Structure

- [`project.godot`](viewer/project.godot) — project config, GL-compatibility
  renderer, 1280 × 720 window.
- [`main.tscn`](viewer/main.tscn) — single `Main` scene, `GridContainer` with
  8 columns.
- [`main.gd`](viewer/main.gd) — `DirAccess`-driven loader that scans five
  asset dirs at boot and builds a `TextureRect` per PNG.
- [`icon.svg`](viewer/icon.svg) — teal project icon.

## Why Godot

Godot is MIT-licensed, 100 MB, boots in ms, and its scripting language is
tuned for exactly this kind of glue work. Using it as the runtime dashboard
for other tools' outputs proves the five cases really do produce
engine-ready assets.
