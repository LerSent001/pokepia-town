import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.name.startswith('Town_') and o.type=='MESH':o.select_set(True)
restore=[]
for obj in bpy.context.selected_objects:
 if obj.name.startswith('Town_QTree'):continue
 for material in obj.data.materials:
  if not material or not material.use_nodes:continue
  bsdf=material.node_tree.nodes.get('Principled BSDF')
  if not bsdf:continue
  bsdf.inputs['Base Color'].default_value=material.diffuse_color
  for inp in ['Base Color','Normal']:
   for link in list(bsdf.inputs[inp].links):
    restore.append((material,link.from_socket,link.to_socket));material.node_tree.links.remove(link)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/town.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=6,export_draco_position_quantization=14,export_draco_normal_quantization=10)
for material,src,dst in restore:material.node_tree.links.new(src,dst)
size=(ROOT/'public/town.glb').stat().st_size
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town-with-residents.blend'),compress=True)
print(json.dumps({'town_glb_bytes':size,'selected_objects':len(bpy.context.selected_objects)}))
