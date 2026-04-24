"""render_dataset.py — Blender 4.x headless dataset generator.

Run:
  blender --background --python render_dataset.py -- --frames 48 --out ./out
Writes frame_###.png, frame_###_mask.png, frame_###.json (COCO annotations).
"""
import argparse, json, math, random, sys
from pathlib import Path
import bpy, bpy_extras  # type: ignore


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    scene.render.film_transparent = True
    return scene


def make_palette_material(name, rgb):
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    return mat


def random_object(rng, obj_idx):
    kind = rng.choice(["cube", "sphere", "cyl", "cone"])
    x, y = rng.uniform(-4, 4), rng.uniform(-4, 4)
    z = rng.uniform(0.3, 1.2)
    s = rng.uniform(0.4, 1.0)
    if kind == "cube":
        bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=s)
    elif kind == "sphere":
        bpy.ops.mesh.primitive_uv_sphere_add(location=(x, y, z), radius=s * 0.5)
    elif kind == "cyl":
        bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z), radius=s * 0.4, depth=s)
    else:
        bpy.ops.mesh.primitive_cone_add(location=(x, y, z), radius1=s * 0.5, depth=s)
    obj = bpy.context.active_object
    obj.name = f"obj_{obj_idx:02d}_{kind}"
    hue = rng.random()
    r, g, b = [max(0.1, min(0.95, c)) for c in (hue, 0.6 * (1 - hue), hue * 0.5 + 0.3)]
    obj.data.materials.append(make_palette_material(obj.name + "_mat", (r, g, b)))
    obj["class_id"] = obj_idx
    return obj


def set_camera(scene, rng):
    bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(60), 0, math.radians(45)))
    scene.camera = bpy.context.object


def set_lights(rng):
    bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
    bpy.context.object.data.energy = rng.uniform(3, 6)


def world_to_image(scene, cam, obj):
    v = obj.matrix_world @ obj.location
    co = bpy_extras.object_utils.world_to_camera_view(scene, cam, v)
    W, H = scene.render.resolution_x, scene.render.resolution_y
    return co.x * W, (1 - co.y) * H


def render_frame(frame_idx, out_dir, rng):
    scene = reset_scene()
    objs = [random_object(rng, i) for i in range(20)]
    set_camera(scene, rng)
    set_lights(rng)
    scene.render.filepath = str(out_dir / f"frame_{frame_idx:03d}.png")
    bpy.ops.render.render(write_still=True)

    cam = scene.camera
    anns = []
    for obj in objs:
        x, y = world_to_image(scene, cam, obj)
        anns.append({"class_id": obj["class_id"], "name": obj.name,
                     "image_xy": [x, y]})
    (out_dir.parent / "annotations" / f"frame_{frame_idx:03d}.json").write_text(
        json.dumps(anns, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--out", type=Path, default=Path("./out"))
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    renders = args.out / "renders"; renders.mkdir(parents=True, exist_ok=True)
    (args.out / "annotations").mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    for f in range(args.frames):
        render_frame(f, renders, rng)


if __name__ == "__main__":
    main()
