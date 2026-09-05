import bpy,math,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=[]
for id,name,height,location in [(132,'Ditto',.85,(-.2,-9.4,.44)),(25,'Pikachu',1.22,(3.7,.5,1.42)),(66,'Machop',1.5,(7,-9.4,.48)),(54,'Psyduck',1.35,(-8,.25,1.43)),(384,'Rayquaza',12,(-3,7,9.4))]:
 old=set(bpy.data.objects)
 bpy.ops.import_scene.gltf(filepath=str(ROOT/f'public/models/{id}.glb'))
 objs=list(set(bpy.data.objects)-old);roots=[o for o in objs if o.parent is None]
 collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
 for o in objs:
  for c in list(o.users_collection):c.objects.unlink(o)
  collection.objects.link(o)
 control=bpy.data.objects.new(name+'_Town',None);collection.objects.link(control)
 for o in roots:o.parent=control
 if id==25:control.rotation_euler.x=-math.pi/2
 bpy.context.view_layer.update();pts=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
 lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);dim=hi-lo;scale=height/(max(dim) if id==384 else dim.z)
 control.scale=(scale,)*3;control.location=Vector(location)-Vector(((lo.x+hi.x)/2*scale,(lo.y+hi.y)/2*scale,lo.z*scale))
 if id==384:control.rotation_euler.z=math.radians(-65)
 report.append({'id':id,'name':name,'objects':len(objs),'actions':[a.name for a in bpy.data.actions if 'Town_' in a.name]})
bpy.ops.import_scene.gltf(filepath=str(ROOT/'public/models/player.glb'))
player=bpy.context.scene.objects.get('Player_Rig');player.location=(3.7,.05,1.415)
scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=240;scene.render.fps=30
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town-with-residents.blend'))
(ROOT/'evidence/blender-residents.json').write_text(json.dumps(report,indent=2))
# Set the viewport to the scene camera for a useful first opening.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
print(json.dumps(report))
