#!/usr/bin/env bash
# Batch-export every SVG in icons/ to PNG at 2x using Inkscape's CLI action API.
set -euo pipefail
mkdir -p png@2x
for f in icons/*.svg; do
  name=$(basename "$f" .svg)
  inkscape "$f" \
    --actions="export-type:png; export-dpi:192; export-filename:png@2x/${name}.png; export-do"
done
echo "exported $(ls png@2x | wc -l) icons"
