import bpy, math, json, bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
parts=[]
def material(name,h):
 m=bpy.data.materials.new(name);rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb];m.diffuse_color=(*rgb,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=.9;return m
skin=material('Player peach','ffd0b8');hair=material('Player violet hair','674182');ink=material('Player facial ink','302634');smile=material('Player smile interior','97304f');tongue=material('Player soft mouth pink','cd5873');cheek=material('Player cheek tint','efad9f');ivory=material('Player hat ivory','fff3dc');navy=material('Player indigo cloth','48537c');sole=material('Player shoe sole','e1e4ec');shirt=material('Player blue plaid','ffffff');trim=material('Player shirt facing','839cae');accent=material('Player bag patch','9ab7c5')
# Four broad checks across the front, as in the supplied close-up.
img=bpy.data.images.new('Player blue woven checks',width=256,height=256);px=[]
for y in range(256):
 for x in range(256):
  xx=x%128;yy=y%128;c=(.44,.64,.71)
  if xx<52:c=(.26,.35,.53)
  if yy<52:c=tuple(v*.64 for v in c)
  if 72<xx<105:c=(.70,.77,.78)
  if 72<yy<105:c=tuple(v*.55+.36 for v in c)
  if xx in [21,22,116,117] or yy in [21,22,116,117]:c=(.45,.58,.68)
  px.extend((*c,1))
img.pixels=px;img.filepath_raw=str(ROOT/'public/textures/player-plaid.png');img.file_format='PNG';img.save();img.pack();img.filepath='//../public/textures/player-plaid.png';tex=shirt.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;shirt.node_tree.links.new(tex.outputs['Color'],shirt.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
def finish(o,name,mat,bone):
 o.name=name;o.data.materials.clear();o.data.materials.append(mat)
 for p in o.data.polygons:p.use_smooth=True;p.material_index=0
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bone:g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 parts.append(o);return o
def ell(name,pos,scale,mat,bone='head'):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=pos);o=bpy.context.object;o.scale=scale;return finish(o,name,mat,bone)
def rounded(name,pos,scale,r,mat,bone):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);m=o.modifiers.new('Soft edge','BEVEL');m.width=r;m.segments=6;bpy.ops.object.modifier_apply(modifier=m.name);return finish(o,name,mat,bone)
def mesh(name,verts,faces,mat,bone):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);bpy.context.view_layer.objects.active=o;return finish(o,name,mat,bone)
def interp(points,t):
 n=len(points);u=min(n-1-1e-6,t*(n-1));i=int(u);f=u-i;a=Vector(points[max(0,i-1)]);b=Vector(points[i]);c=Vector(points[i+1]);d=Vector(points[min(n-1,i+2)]);return (b*2+(c-a)*f+(a*2-b*5+c*4-d)*f*f+(-a+b*3-c*3+d)*f*f*f)*.5
# A swept, tapered surface follows the gesture; each strand has a buried root and rounded tip.
def sweep(name,points,widths,depths,mat,bone,rows=32,seg=20):
 verts=[];faces=[]
 for j in range(rows+1):
  t=j/rows;p=interp(points,t);tangent=(interp(points,min(1,t+.002))-interp(points,max(0,t-.002))).normalized();front=Vector((0,-1,0));front=(front-tangent*front.dot(tangent)).normalized();side=tangent.cross(front).normalized();idx=min(len(widths)-2,int(t*(len(widths)-1)));f=t*(len(widths)-1)-idx;w=widths[idx]*(1-f)+widths[idx+1]*f;d=depths[idx]*(1-f)+depths[idx+1]*f
  if idx==len(widths)-2 and widths[-1]<.01:
   cap=math.sqrt(max(0,1-f*f));w=widths[idx]*cap+.001;d=depths[idx]*cap+.001
  for k in range(seg):
   a=k*math.tau/seg;verts.append(tuple(p+side*math.cos(a)*w+front*math.sin(a)*d))
 for j in range(rows):
  for k in range(seg):faces.append((j*seg+k,j*seg+(k+1)%seg,(j+1)*seg+(k+1)%seg,(j+1)*seg+k))
 faces.extend([tuple(range(seg-1,-1,-1)),tuple(rows*seg+k for k in range(seg))]);return mesh(name,verts,faces,mat,bone)
def fuse(objects,name,mat,bone,voxel=.008):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True);parts.remove(o)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 o.vertex_groups.clear();mod=o.modifiers.new('Continuous sculpt surface','REMESH');mod.mode='VOXEL';mod.voxel_size=voxel;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=o.modifiers.new('Soften sculpt transitions','SMOOTH');mod.factor=.8;mod.iterations=5;bpy.ops.object.modifier_apply(modifier=mod.name)
 mod=o.modifiers.new('Game topology','DECIMATE');mod.ratio=.42;bpy.ops.object.modifier_apply(modifier=mod.name)
 return finish(o,name,mat,bone)
def panel(name,points,mat,bone='head'):
 return mesh(name,points,[tuple(range(len(points)-1,-1,-1))],mat,bone)
# Wide head and low facial features; head + hair occupy about 58% of the silhouette.
rounded('Wide rounded face',(0,0,1.414),(1.19,.79,1.00),.295,skin,'head')
for s in [-1,1]:
 ell('Ear',(s*.589,.008,1.155),(.072,.058,.13),skin)
 # Flat eye decals, no protruding bead eyes.
 eye=[]
 for k in range(32):a=k*math.tau/32;eye.append((s*.213+math.cos(a)*.013,-.397,1.177+math.sin(a)*.015))
 panel('Dot eye',eye,ink)
 glint=[]
 for k in range(16):a=k*math.tau/16;glint.append((s*.213-.003+math.cos(a)*.003,-.398,1.182+math.sin(a)*.003))
 panel('Tiny eye highlight',glint,ivory)
# Smile is a thin flush opening with round corners; no raised tube lip.
verts=[]
for k in range(64):
 a=k*math.tau/64;x=math.copysign(.216,math.cos(a))+.036*math.cos(a);z=1.061+.026*math.sin(a)+.005*(abs(x)/.252)**2;verts.append((x,-.398,z))
panel('Wide quiet smile',verts,smile)
verts=[]
for k in range(48):
 a=k*math.tau/48;x=.210*math.cos(a);z=1.050+.007*math.sin(a)+.004*(abs(x)/.210)**2;verts.append((x,-.399,z))
panel('Smile inner pink',verts,tongue)
# Continuous cap of hair, open at the forehead and low behind the ears.
v=[];faces=[];N=64;R=22
for j in range(R+1):
 for i in range(N):
  phi=i*math.tau/N;front=max(0,-math.sin(phi));end=2.80-1.59*front**3-.20*abs(math.cos(phi))**4;theta=j/R*end
  rad=math.sin(theta)**(.25 if theta>math.pi/2 else 1);v.append((.635*rad*math.cos(phi),.075+.452*rad*math.sin(phi),1.535+.548*math.cos(theta)-.06*(j/R)**5*(1-front)))
for j in range(R):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
cap=mesh('Sculpted hair cap',v,faces,hair,'head');mod=cap.modifiers.new('Scalp thickness','SOLIDIFY');mod.thickness=.035;bpy.context.view_layer.objects.active=cap;bpy.ops.object.modifier_apply(modifier=mod.name)
# Asymmetrical part: three swept locks on the left, one temple curl on the right.
sweep('Main sweeping fringe',[(.22,-.09,2.025),(.07,-.335,1.94),(-.09,-.478,1.62),(-.185,-.456,1.34)],[.10,.215,.206,.003],[.07,.12,.126,.003],hair,'head',44,24)
sweep('Left sweeping fringe',[(-.06,-.06,2.023),(-.245,-.34,1.91),(-.355,-.463,1.66),(-.422,-.421,1.455)],[.10,.178,.161,.003],[.08,.115,.10,.003],hair,'head',40,24)
sweep('Outer left curl',[(-.32,-.015,1.979),(-.48,-.254,1.84),(-.556,-.319,1.74),(-.55,-.305,1.57)],[.10,.125,.106,.003],[.075,.10,.09,.003],hair,'head')
sweep('Right temple sweep',[(.22,-.04,2.04),(.444,-.278,1.872),(.568,-.308,1.567),(.526,-.25,1.17)],[.09,.17,.145,.005],[.07,.126,.116,.005],hair,'head',44,24)
for s in [-1,1]:
 bunch=[]
 bunch.append(sweep('Pigtail mass',[(s*.555,.145,1.765),(s*.748,.125,1.847),(s*.836,.153,1.79),(s*.758,.178,1.68)],[.07,.165,.151,.085],[.07,.127,.13,.07],hair,'head'))
 bunch.append(sweep('Pigtail fork A',[(s*.76,.17,1.73),(s*.783,.186,1.62),(s*.783,.19,1.534)],[.078,.067,.007],[.06,.06,.007],hair,'head',20,16))
 bunch.append(sweep('Pigtail fork B',[(s*.825,.17,1.75),(s*.916,.168,1.704),(s*.926,.177,1.633)],[.068,.064,.007],[.06,.053,.007],hair,'head',20,16))
 fuse(bunch,'One-piece forked pigtail',hair,'head',.009)
 ell('Hair band',(s*.605,.127,1.761),(.046,.122,.083),navy)
# Soft brim, shallow creased crown and curved indigo band from the supplied back view.
v=[];faces=[];N=64
for j in range(6):
 t=j/5
 for k in range(N):
  a=k*math.tau/N;rx=.20+(.405-.20)*t;ry=.145+(.302-.145)*t;z=2.048+.026*t*t+.023*math.cos(a)*t
  v.append((rx*math.cos(a),.10+ry*math.sin(a),z))
for j in range(5):
 for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
ob=mesh('Soft ivory brim',v,faces,ivory,'head');mod=ob.modifiers.new('Brim thickness','SOLIDIFY');mod.thickness=.017;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
ell('Hat soft crown',(0,.115,2.096),(.28,.225,.144),ivory)
# Ribbon wraps around the crown rather than forming a separate flat disc.
v=[];faces=[]
for j in range(2):
 for k in range(64):
  a=k*math.tau/64;v.append((.284*math.cos(a),.115+.229*math.sin(a),2.077+j*.045-.022*math.sin(a)))
for k in range(64):faces.append((k,(k+1)%64,(k+1)%64+64,k+64))
mesh('Hat indigo ribbon',v,faces,navy,'head')
# Long, flared plaid shirt and a very short lower body.
ell('Neck hidden by collar',(0,0,.908),(.095,.087,.065),skin,'spine')
v=[];faces=[];N=32
rings=[(.365,.254,.151),(.405,.244,.145),(.56,.211,.141),(.76,.214,.141),(.85,.225,.141),(.896,.13,.103)]
for z,rx,ry in rings:
 for i in range(N):
  a=i*math.tau/N;xx=math.copysign(abs(math.cos(a))**.65,math.cos(a))*rx;yy=math.copysign(abs(math.sin(a))**.65,math.sin(a))*ry;v.append((xx,yy,z))
for j in range(len(rings)-1):
 for i in range(N):faces.append((j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i))
faces.append(tuple(range(N-1,-1,-1)));body=mesh('Tailored flared plaid shirt',v,faces,shirt,'spine')
uv=body.data.uv_layers.new(name='UVMap')
for p in body.data.polygons:
 for li in p.loop_indices:co=body.data.vertices[body.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x/.52+.5,(co.z-.36)/.54)
for s in [-1,1]:
 cuff=sweep('Soft shirt sleeve',[(s*.188,0,.858),(s*.247,-.002,.827),(s*.281,-.009,.755)],[.093,.102,.08],[.112,.111,.087],shirt,'upper_arm'+str(s),12,24)
 uv=cuff.data.uv_layers.new(name='UVMap')
 for p in cuff.data.polygons:
  for li in p.loop_indices:co=cuff.data.vertices[cuff.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x/.52+.5,(co.z-.36)/.54)
 panel('Small folded collar',[(s*.008,-.122,.897),(s*.124,-.119,.89),(s*.137,-.15,.805),(s*.065,-.163,.823)],navy,'spine')
rounded('Narrow shirt facing',(0,-.147,.637),(.020,.009,.447),.004,trim,'spine')
for z in [.48,.61,.745]:ell('Subtle cloth button',(0,-.155,z),(.006,.003,.006),ivory,'spine')
# Both arms, wrists, palms and fingers are fused before assigning blended weights.
for s in [-1,1]:
 limb=[]
 limb.append(sweep('Arm volume',[(s*.251,0,.803),(s*.303,-.002,.661),(s*.339,-.013,.48),(s*.38,-.024,.341)],[.044,.039,.036,.032],[.046,.041,.037,.034],skin,None,40,20))
 limb.append(ell('Palm volume',(s*.393,-.031,.294),(.070,.031,.058),skin,None))
 for i,(offset,length) in enumerate([(-.048,.095),(-.017,.13),(.015,.125),(.046,.10)]):
  x=s*(.393+offset);end=s*(.393+offset*1.75)
  limb.append(sweep('Finger volume',[(x,-.032,.276),(s*(.393+offset*1.2),-.042,.221),(end,-.052,.275-length)],[.018,.016,.003],[.018,.016,.003],skin,None,16,12))
 limb.append(sweep('Thumb volume',[(s*.34,-.03,.325),(s*.303,-.041,.29),(s*.286,-.05,.229)],[.031,.027,.004],[.028,.024,.004],skin,None,20,14))
 armobj=fuse(limb,'Continuous arm and open hand '+str(s),skin,None,.006)
 groups={k:armobj.vertex_groups.new(name=k+str(s)) for k in ['upper_arm','forearm','hand']}
 def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
 for vert in armobj.data.vertices:
  z=vert.co.z
  if z>.57:w=smooth((z-.57)/.17);weights={'upper_arm':w,'forearm':1-w}
  else:w=smooth((z-.32)/.13);weights={'forearm':w,'hand':1-w}
  for name,w in weights.items():
   if w>0:groups[name].add([vert.index],w,'REPLACE')
# One cloth pelvis with short legs, not two spherical shorts pieces.
pants=[];pants.append(rounded('Pants pelvis',(0,.005,.338),(.36,.252,.17),.05,navy,None))
for s in [-1,1]:pants.append(rounded('Short trouser leg',(s*.104,.008,.24),(.145,.205,.19),.034,navy,None))
pants=fuse(pants,'Continuous short trousers',navy,None,.008);groups={n:pants.vertex_groups.new(name=n) for n in ['hips','thigh-1','thigh1']}
for vert in pants.data.vertices:
 z=vert.co.z;w=max(0,min(1,(.34-z)/.10));groups['hips'].add([vert.index],1-w,'REPLACE');groups['thigh'+str(-1 if vert.co.x<0 else 1)].add([vert.index],w,'REPLACE')
for s in [-1,1]:
 rounded('Short sock',(s*.111,0,.154),(.112,.137,.123),.03,ivory,'shin'+str(s))
 rounded('Rounded shoe sole',(s*.116,-.052,.035),(.199,.317,.055),.026,sole,'foot'+str(s))
 ell('Smooth blue shoe',(s*.116,-.065,.098),(.099,.154,.073),navy,'foot'+str(s))
 # Broad toe panel and subtle strap, without miniature sneaker hardware.
 sweep('Shoe strap',[(s*.116-.08,-.05,.13),(s*.116,-.078,.163),(s*.116+.08,-.05,.13)],[.014,.014,.014],[.008,.008,.008],trim,'foot'+str(s),16,10)
# The small bag is visible in the supplied rear view.
rounded('Small back bag',(0,.189,.652),(.248,.143,.29),.075,navy,'spine')
ell('Bag round patch',(0,.268,.67),(.052,.008,.052),accent,'spine')
for s in [-1,1]:sweep('Backpack strap',[(s*.09,.24,.78),(s*.145,.02,.858),(s*.18,-.13,.785),(s*.192,-.14,.57)],[.018,.018,.018,.018],[.010,.010,.010,.010],navy,'spine',28,10)
# Join skinned surfaces, retaining continuous blended weights at elbow and wrist.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();body=bpy.context.object;body.name='Player_SkinnedMesh';bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
body.data.validate(verbose=True);bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free();body.data.update()
arm=bpy.data.armatures.new('Player soft deformation skeleton');rig=bpy.data.objects.new('Player_Rig',arm);bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;body.select_set(False);rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(name,h,t,parent=None):
 b=arm.edit_bones.new(name);b.head=h;b.tail=t
 if parent:b.parent=arm.edit_bones[parent]
bone('hips',(0,0,.31),(0,0,.44));bone('spine',(0,0,.44),(0,0,.9),'hips');bone('head',(0,0,.9),(0,0,1.9),'spine')
for s in [-1,1]:
 ss=str(s);bone('upper_arm'+ss,(s*.235,0,.83),(s*.312,-.006,.59),'spine');bone('forearm'+ss,(s*.312,-.006,.59),(s*.376,-.024,.346),'upper_arm'+ss);bone('hand'+ss,(s*.376,-.024,.346),(s*.4,-.04,.23),'forearm'+ss)
 bone('thigh'+ss,(s*.105,0,.33),(s*.111,0,.215),'hips');bone('shin'+ss,(s*.111,0,.215),(s*.116,0,.10),'thigh'+ss);bone('foot'+ss,(s*.116,0,.10),(s*.116,-.17,.075),'shin'+ss)
bpy.ops.object.mode_set(mode='OBJECT');body.parent=rig;mod=body.modifiers.new('Smooth skeletal deformation','ARMATURE');mod.object=rig
scene=bpy.context.scene;scene.render.fps=30;rig.animation_data_create()
for name,duration,walking in [('Player_Idle',90,False),('Player_Walk',28,True)]:
 action=bpy.data.actions.new(name);rig.animation_data.action=action
 for f in range(duration+1):
  t=f/duration*math.tau
  for pb in rig.pose.bones:
   pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);s=-1 if pb.name.endswith('-1') else 1
   if pb.name.startswith('thigh'):pb.rotation_euler.x=math.sin(t)*.56*s if walking else 0
   if pb.name.startswith('shin'):pb.rotation_euler.x=max(0,-math.sin(t)*s)*.40 if walking else 0
   if pb.name.startswith('upper_arm'):pb.rotation_euler.x=-math.sin(t)*.24*s if walking else math.sin(t)*.022
   if pb.name.startswith('forearm'):pb.rotation_euler.x=-.015-(max(0,math.sin(t)*s)*.10 if walking else 0)
   if pb.name=='head':pb.rotation_euler.y=math.sin(t)*(.016 if walking else .026)
   if pb.name=='spine':pb.rotation_euler.y=math.sin(t)*(.025 if walking else .009)
   if pb.name=='hips':pb.location.y=abs(math.sin(t))*.014 if walking else math.sin(t)*.005
   pb.keyframe_insert('rotation_euler',frame=f);pb.keyframe_insert('location',frame=f)
 action.use_fake_user=True;track=rig.animation_data.nla_tracks.new();track.name=name;track.strips.new(name,0,action);track.mute=True
rig.animation_data.action=bpy.data.actions['Player_Idle'];scene.frame_start=0;scene.frame_end=90;scene.frame_set(0)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/models/player.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_cameras=False,export_lights=False)
bpy.ops.object.camera_add(location=(0,-7,1.75));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.65;scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(-3,-4,5));bpy.context.object.data.energy=350;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=5
scene.world.color=(.5,.5,.5);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=900;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/player.blend'),compress=True)
print(json.dumps({'vertices':len(body.data.vertices),'bones':len(arm.bones),'height':2.24,'headChin':.914,'headShare':(2.24-.914)/2.24,'animations':['Player_Idle','Player_Walk'],'glbBytes':(ROOT/'public/models/player.glb').stat().st_size}))
