extends Node2D

# Loads every sprite/texture from user://assets at boot and arranges them in
# an 8-col grid. In a full build the atlas.json (libresprite) would drive
# animation, the coco.json (blender) would drive 3D preview, etc. Here we
# demonstrate the loader pattern.

const ASSET_DIRS := [
    "res://assets/libresprite",
    "res://assets/krita",
    "res://assets/blender",
    "res://assets/gimp",
    "res://assets/inkscape",
]

@onready var grid: GridContainer = $Grid

func _ready() -> void:
    for dir_path in ASSET_DIRS:
        var d := DirAccess.open(dir_path)
        if d == null:
            continue
        d.list_dir_begin()
        var name := d.get_next()
        while name != "":
            if name.ends_with(".png"):
                var tex := load(dir_path + "/" + name) as Texture2D
                if tex:
                    var rect := TextureRect.new()
                    rect.texture = tex
                    rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
                    rect.custom_minimum_size = Vector2(144, 144)
                    grid.add_child(rect)
            name = d.get_next()

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
        get_tree().quit()
