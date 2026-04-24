# Godot 4 · Asset Viewer

Unified runtime for all five other cases.

## Run

```bash
godot --path ./cases/godot/viewer
```

Drops every PNG from `assets/libresprite`, `assets/krita`, `assets/blender`,
`assets/gimp`, `assets/inkscape` into an 8-col grid. Press Esc to exit.

## What this demonstrates

* Filesystem scan with `DirAccess`
* Dynamic `TextureRect` creation
* Single scene + single script (no project baggage)
* Works headless for screenshot tests
