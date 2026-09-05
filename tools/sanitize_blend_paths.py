"""Replace local absolute resource paths in the currently open Blender file."""

from pathlib import Path

import bpy


def repository_texture_path(filepath: str) -> str:
    return f"//../public/textures/{Path(filepath).name}"


changed = []
for image in bpy.data.images:
    if image.filepath and Path(bpy.path.abspath(image.filepath)).is_absolute():
        image.filepath = repository_texture_path(image.filepath)
        changed.append((image.name, image.filepath))

if bpy.context.scene.render.filepath and Path(bpy.context.scene.render.filepath).is_absolute():
    bpy.context.scene.render.filepath = "//render/"

bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath, compress=True)
print(f"Sanitized {len(changed)} image paths in {bpy.data.filepath}")
