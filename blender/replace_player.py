import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'blender/pokepia-town-with-residents.blend'))
for old in list(bpy.data.objects):
 if old.name.startswith('Player_Rig') or old.name.startswith('Player_SkinnedMesh'):bpy.data.objects.remove(old,do_unlink=True)
for action in list(bpy.data.actions):
 if action.name.startswith('Player_'):bpy.data.actions.remove(action)
with bpy.data.libraries.load(str(ROOT/'blender/player.blend'),link=False) as (source,target):
 target.objects=[name for name in source.objects if name.startswith('Player_Rig') or name.startswith('Player_SkinnedMesh')]
for ob in target.objects:
 if ob:bpy.context.scene.collection.objects.link(ob)
rig=next(ob for ob in target.objects if ob.type=='ARMATURE');rig.name='Player_Rig';rig.location=(3.7,.05,1.415);bpy.context.scene.render.fps=30
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town-with-residents.blend'),compress=True)
print(json.dumps({'playerReplaced':True,'bones':len(rig.data.bones),'sceneObjects':len(bpy.context.scene.objects)}))
