"""layer_export.py — Krita Python plugin.

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
