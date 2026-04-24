# Inkscape · Parametric pictogram set

**Tool**: Inkscape 1.3 · **Interface**: CLI `--actions`

A 24-icon pictogram family (dataset, model, layer, mask, render, export, …)
that lives as parametric SVG and renders to 2× PNG through Inkscape's action
API. Every pictogram uses the same two-colour palette (teal + amber on paper)
so it drops into documentation, slides, or an AI model's UI without visual
debt.

## Run

```bash
bash render.sh
```

[`render.sh`](render.sh) iterates over every `icons/icon_*.svg` and emits a
`png@2x/` folder at 192 DPI using:

```bash
inkscape "$f" \
  --actions="export-type:png; export-dpi:192; export-filename:${name}.png; export-do"
```

## Outputs

- `assets/inkscape/icons/icon_00_dataset.svg` … `icon_23_deploy.svg` — 96 × 96 SVG.
- `assets/inkscape/icons_sheet.png` — 6 × 4 contact sheet.

## Why CLI actions

The `--actions` interface is how Inkscape 1.2+ exposes most of its UI to
automation. It's more stable than the deprecated `--export-png` flags and
composes cleanly with shell or Makefile orchestration.
