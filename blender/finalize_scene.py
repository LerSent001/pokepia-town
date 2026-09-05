import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
collection=bpy.data.collections.get('Ditto')
if collection:
 for ob in collection.objects:
  if ob.type!='MESH':continue
  for m in ob.data.materials:
   if not m:continue
   m.use_nodes=True;nodes=m.node_tree.nodes;links=m.node_tree.links;tex=next((n for n in nodes if n.type=='TEX_IMAGE'),None);bs=nodes.get('Principled BSDF') or nodes.new('ShaderNodeBsdfPrincipled');out=next(n for n in nodes if n.type=='OUTPUT_MATERIAL')
   bs.inputs['Roughness'].default_value=1;bs.inputs['Metallic'].default_value=0;bs.inputs['Emission Strength'].default_value=.24
   if tex:links.new(tex.outputs['Color'],bs.inputs['Base Color']);links.new(tex.outputs['Color'],bs.inputs['Emission Color'])
   links.new(bs.outputs['BSDF'],out.inputs['Surface'])
scene=bpy.context.scene;scene.render.fps=30
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town-with-residents.blend'),compress=True)
print('Final scene saved: six rigged characters, matte Ditto, 30 fps timeline.')
