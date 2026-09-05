import bpy, math, random, json
from mathutils import Vector
from pathlib import Path
random.seed(27)
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
B={}; M={}; TREE_PLACEMENTS=[]
colors={'grass':'9fc943','grassEdge':'7eb647','grassLight':'b6d966','earth':'c3a477','stone':'dbca9d','stoneLight':'e9ddb9','stoneDark':'c3b384','sand':'efdcaa','path':'ead19d','brick':'ce8a70','brickLight':'e2a28a','red':'dc4b51','redLight':'ed6770','redDark':'ad3746','cream':'fff1d0','white':'fffbe4','wood':'b88747','woodLight':'d3a967','woodDark':'815834','trunk':'997048','leaf':'65b53d','leafLight':'8aca40','leafDark':'4b963d','pine':'397d61','pineLight':'549568','hedge':'62ac56','stem':'519250','pink':'f3a4b7','pinkLight':'ffd6db','yellow':'ffe282','lilac':'a0a4e8','blueFlower':'849ce1','glass':'67cbd0','glassLight':'b1eee3','glassDark':'339da8','metal':'454f4c','gold':'ecbf63','water':'73cfdd','roofGreen':'488b67','roofGreenLight':'64a579','rock':'999e96','rockLight':'b1b5a8'}
def mat(k):
 if k not in M:
  h=colors.get(k,k);rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)]
  # Blender materials take linear colors; convert sRGB palette.
  rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
  m=bpy.data.materials.new(k);m.diffuse_color=(*rgb,1);m.use_nodes=True
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=.78
  m.use_backface_culling=False
  M[k]=m
 return M[k]
def add(k,verts,faces,smooth=False):
 if k not in B:B[k]=[[],[],[]]
 v,f,s=B[k];n=len(v);v.extend([(a,-c,b) for a,b,c in verts]);f.extend([tuple(n+i for i in face) for face in faces]);s.extend([smooth]*len(faces))
def box(k,x,y,z,sx,sy,sz):
 v=[(x+a*sx/2,y+b*sy/2,z+c*sz/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 add(k,v,[(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)])
def sphere(k,x,y,z,sx,sy=None,sz=None,seg=12,rings=7):
 sy=sy if sy!=None else sx;sz=sz if sz!=None else sx
 v=[];f=[]
 for j in range(rings+1):
  t=math.pi*j/rings
  for i in range(seg):
   p=2*math.pi*i/seg;v.append((x+sx*math.sin(t)*math.cos(p),y+sy*math.cos(t),z+sz*math.sin(t)*math.sin(p)))
 for j in range(rings):
  for i in range(seg):
   a=j*seg+i;b=j*seg+(i+1)%seg;f.append((a,b,b+seg,a+seg))
 add(k,v,f,True)
def cyl(k,x,y,z,r,h,rt=None,seg=12):
 rt=r if rt==None else rt;v=[];f=[]
 for yy,rr in [(y-h/2,r),(y+h/2,rt)]:
  for i in range(seg):
   a=2*math.pi*i/seg;v.append((x+rr*math.cos(a),yy,z+rr*math.sin(a)))
 for i in range(seg):a=i;b=(i+1)%seg;f.append((a,a+seg,b+seg,b))
 f.extend([tuple(range(seg)),tuple(range(seg*2-1,seg-1,-1))]);add(k,v,f,True)
def beam(k,a,b,r,seg=8):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();side=d.cross(Vector((0,1,0)))
 if side.length<.001:side=d.cross(Vector((1,0,0)))
 side.normalize();up=d.cross(side);v=[]
 for p in [a,b]:
  for i in range(seg):v.append(tuple(p+(side*math.cos(i*math.tau/seg)+up*math.sin(i*math.tau/seg))*r))
 f=[(i,(i+1)%seg,(i+1)%seg+seg,i+seg) for i in range(seg)];f.extend([tuple(range(seg)),tuple(range(seg*2-1,seg-1,-1))]);add(k,v,f,True)
def roundbox(k,x,y,z,sx,sy,sz,r=.15):
 # Rounded rectangle extrusion with a beveled top and bottom.
 r=min(r,sx/2-.001,sy/2-.001,sz/2-.001);v=[];f=[];segs=5 if r>.3 else (2 if r>.1 else 1)
 for yy,inset in [(y-sy/2,r*.45),(y-sy/2+r*.45,0),(y+sy/2-r*.45,0),(y+sy/2,r*.45)]:
  for cx,cz,start in [(1,1,0),(-1,1,90),(-1,-1,180),(1,-1,270)]:
   for i in range(segs+1):
    a=math.radians(start+i*90/segs);v.append((x+cx*(sx/2-r)+(r-inset)*math.cos(a),yy,z+cz*(sz/2-r)+(r-inset)*math.sin(a)))
 n=4*(segs+1)
 for j in range(3):
  for i in range(n):f.append((j*n+i,(j+1)*n+i,(j+1)*n+(i+1)%n,j*n+(i+1)%n))
 f.extend([tuple(range(n)),tuple(range(4*n-1,3*n-1,-1))]);add(k,v,f,True)
def halfdome(k,x,y,z,rx,ry,rz):
 v=[];f=[];seg=40;rings=12
 for j in range(rings+1):
  a=j/rings*math.pi/2
  for i in range(seg):
   b=i/seg*math.tau;v.append((x+rx*math.sin(a)*math.cos(b),y+ry*math.cos(a),z+rz*math.sin(a)*math.sin(b)))
 for j in range(rings):
  for i in range(seg):f.append((j*seg+i,j*seg+(i+1)%seg,(j+1)*seg+(i+1)%seg,(j+1)*seg+i))
 add(k,v,f,True)
def torus_front(k,x,y,z,r,t,seg=40):
 v=[];f=[]
 for i in range(seg):
  a=i*math.tau/seg
  for j in range(8):
   b=j*math.tau/8;v.append((x+(r+t*math.cos(b))*math.cos(a),y+(r+t*math.cos(b))*math.sin(a),z+t*math.sin(b)))
 for i in range(seg):
  for j in range(8):f.append((i*8+j,((i+1)%seg)*8+j,((i+1)%seg)*8+(j+1)%8,i*8+(j+1)%8))
 add(k,v,f,True)
def disc_front(k,x,y,z,r):
 v=[(x,y,z)]+[(x+r*math.cos(i*math.tau/40),y+r*math.sin(i*math.tau/40),z) for i in range(40)]
 add(k,v,[(0,i+1,(i+1)%40+1) for i in range(40)])
def terrace(x,z,w,d,top):
 box('earth',x,top/2-1.1,z,w,top+2.2,d)
 # orderly staggered stone retaining walls
 for row in range(max(1,math.ceil((top+1.6)/.62))):
  yy=-1.55+row*.61
  for i in range(math.ceil(w/1.3)):
   xx=x-w/2+.65+i*1.3
   for zz in [z-d/2-.025,z+d/2+.025]:roundbox(random.choice(['stone','stoneLight','stoneDark']),xx,yy,zz,1.24,.57,.18,.06)
  for i in range(math.ceil(d/1.3)):
   zz=z-d/2+.65+i*1.3
   for xx in [x-w/2-.025,x+w/2+.025]:roundbox(random.choice(['stone','stoneLight']),xx,yy,zz,.18,.57,1.24,.06)
 roundbox('grassEdge',x,top-.07,z,w+.18,.25,d+.18,.14)
 roundbox('grass',x,top+.06,z,w+.1,.13,d+.1,.06)
def path(x,z,w,d,y):
 roundbox('sand',x,y+.02,z,w,.12,d,.05)
 for i in range(int(w/.95)):
  for j in range(int(d/.85)):
   xx=x-w/2+.5+i*.95;zz=z-d/2+.43+j*.85
   roundbox(random.choice(['path','sand','stoneLight']),xx,y+.095,zz,.87,.045,.76,.02)
def steps(x,z,w,y,levels=5):
 for j in range(levels):
  box('stone',x,y-(j+.5)*.24,z+j*.42,w,.24,.46)
  box('stoneLight',x,y-j*.24+.015,z+j*.42-.04,w+.07,.065,.48)
def tree(x,y,z,s=1):
 # Three continuous, softly scalloped crown tiers, with broad leaf relief.
 cyl('trunk',x,y+.94*s,z,.27*s,1.88*s,.22*s,16)
 for a in range(7):
  t=a*math.tau/7;beam('woodDark',(x+math.cos(t)*.245*s,y+.12*s,z+math.sin(t)*.245*s),(x+math.cos(t)*.22*s,y+1.55*s,z+math.sin(t)*.22*s),.027*s,6)
 for tier,(h,r,hh,k) in enumerate([(1.94,1.5,.69,'leafDark'),(2.56,1.35,.68,'leaf'),(3.04,1.04,.56,'leafLight')]):
  verts=[];faces=[];n=40;rows=10
  for j in range(rows+1):
   a=math.pi*j/rows
   for i in range(n):
    t=i*math.tau/n;rr=r*math.sin(a)*(1+.062*math.sin(9*t+tier))
    yy=h+hh*math.cos(a)+.10*math.sin(9*t+tier)*math.sin(a)**3
    verts.append((x+rr*math.cos(t)*s,y+yy*s,z+rr*math.sin(t)*s))
  for j in range(rows):
   for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
  add(k,verts,faces,True)
def pine(x,y,z,s=1):
 cyl('trunk',x,y+1.2*s,z,.17*s,2.4*s)
 for h,r in [(1.1,1.15),(1.8,.96),(2.4,.69),(2.95,.4)]:cyl('pine' if h<2 else 'pineLight',x,y+h*s,z,r*s,1.35*s,0,9)
def flower(x,y,z,col='pink',s=1):
 # Low poly flower heads with five distinct petals, tilted towards the sun.
 beam('stem',(x,y,z),(x,y+.24*s,z),.018*s,5)
 for a in range(5):
  t=a*math.tau/5;sphere(col,x+math.cos(t)*.10*s,y+.27*s,z+math.sin(t)*.10*s,.094*s,.035*s,.09*s,6,3)
 sphere('yellow',x,y+.303*s,z,.057*s,.035*s,.057*s,6,3)
def grass(x,y,z,s=1):
 for i in range(5):
  a=i*2.4;h=random.uniform(.38,.68)*s;dx=math.cos(a);dz=math.sin(a)
  v=[(x-dz*.055*s,y,z+dx*.055*s),(x+dz*.055*s,y,z-dx*.055*s),(x+dx*.16*s,y+h,z+dz*.16*s)]
  add('leafLight' if i%2 else 'hedge',v,[(0,1,2)])
def bed(x,y,z,w,d,col='pink'):
 roundbox('grassEdge',x,y,z,w,.24,d,.11)
 for i in range(int(w*d*7)):
  xx=x+random.uniform(-w/2,w/2);zz=z+random.uniform(-d/2,d/2)
  sphere('hedge',xx,y+.15,zz,.32,.25,.32,10,6)
  flower(xx,y+.23,zz,col if random.random()<.68 else 'pinkLight',random.uniform(.8,1.2))
def bush(x,y,z,s=1):
 sphere('leafDark',x,y+.27*s,z,.75*s,.52*s,.67*s)
 for dx,dz in [(-.35,.1),(.3,.1),(0,-.3)]:sphere('hedge',x+dx*s,y+.55*s,z+dz*s,.5*s,.44*s,.5*s)
 for i in range(6):
  a=i*2.4;flower(x+math.cos(a)*.55*s,y+.55*s,z+math.sin(a)*.5*s,random.choice(['pink','pinkLight','yellow']),1.2*s)
def fence(x,z,length,y,axis='x'):
 n=math.ceil(length/.9)
 for i in range(n+1):
  xx=x+i*length/n if axis=='x' else x;zz=z+i*length/n if axis=='z' else z
  roundbox('wood',xx,y+.48,zz,.19,1,.19,.055);roundbox('woodLight',xx,y+.98,zz,.24,.12,.24,.04)
 for h in [.35,.73]:
  if axis=='x':box('woodLight',x+length/2,y+h,z,length,.13,.13)
  else:box('woodLight',x,y+h,z+length/2,.13,.13,length)
def lamp(x,y,z,festive=False):
 if festive:
  cyl('woodLight',x,y+1.3,z,.07,2.6);beam('woodLight',(x-.6,y+2.6,z),(x+.6,y+2.6,z),.07)
  for dx in [-.45,.45]:beam('woodDark',(x+dx,y+2.6,z),(x+dx,y+2.25,z),.025);sphere('yellow',x+dx,y+2.1,z,.17,.21,.17)
 else:
  cyl('metal',x,y+.1,z,.2,.18);cyl('metal',x,y+1.12,z,.065,2.1)
  cyl('gold',x,y+2.14,z,.17,.12);sphere('white',x,y+2.34,z,.18,.22,.18)
  cyl('metal',x,y+2.6,z,.3,.23,.08);sphere('metal',x,y+2.76,z,.065)
def bench(x,y,z):
 for xx in [-.75,.75]:
  for zz in [-.19,.24]:box('metal',x+xx,y+.27,z+zz,.075,.55,.085)
  beam('metal',(x+xx,y+.3,z-.23),(x+xx,y+1,z-.37),.042)
 for zz in [-.2,0,.2]:roundbox('woodLight',x,y+.58,z+zz,1.95,.1,.17,.04)
 for yy in [.79,1.02]:roundbox('woodLight',x,y+yy,z-.32,1.95,.18,.075,.03)
def rock(x,y,z,s):
 sphere('rock',x,y+.27*s,z,.55*s,.6*s,.45*s,7,4)
 sphere('rockLight',x+.35*s,y+.17*s,z+.17*s,.4*s,.35*s,.38*s,7,4)
def center(x,y,z):
 # Warm vertical siding and softened silhouette.
 roundbox('wood',x,y+.18,z,7,.36,4.75,.35)
 roundbox('cream',x,y+1.9,z,6.65,3.5,4.45,.6)
 for dx in [-2.9,-2.5,-2.1,-1.7,-1.3,1.3,1.7,2.1,2.5,2.9]:box('stoneLight',x+dx,y+1.7,z+2.235,.034,2.8,.022)
 roundbox('redDark',x,y+3.35,z,7.3,.65,4.95,.7)
 roundbox('cream',x,y+3.52,z,7.38,.18,5.02,.7)
 roundbox('red',x,y+3.91,z,7.4,.72,5.0,.68)
 roundbox('redLight',x,y+4.25,z,7.05,.25,4.67,.65)
 # three rounded roof lobes, flat lower skirt
 roundbox('red',x,y+4.32,z,7.1,1.22,4.7,.61)
 # arched central roof, extruded in depth
 outline=[(-1.3,3.95),(1.3,3.95)]+[(math.cos(a*math.pi/24)*1.3,4.65+math.sin(a*math.pi/24)*1.3) for a in range(25)]
 verts=[(x+xx,y+yy,z+zz) for zz in [-2.28,2.28] for xx,yy in outline];nn=len(outline)
 faces=[tuple(range(nn-1,-1,-1)),tuple(range(nn,nn*2))]+[(i,(i+1)%nn,(i+1)%nn+nn,i+nn) for i in range(nn)]
 add('red',verts,faces[:2],False);add('red',verts,faces[2:],True)
 # Pokeball emblem on upright raised central gable
 disc_front('red',x,y+4.83,z+2.31,1.12);torus_front('redLight',x,y+4.83,z+2.33,1.04,.04)
 disc_front('cream',x,y+4.96,z+2.36,.59)
 box('redDark',x,y+4.96,z+2.38,1.2,.105,.055)
 disc_front('redDark',x,y+4.96,z+2.42,.235);disc_front('cream',x,y+4.96,z+2.45,.16)
 # projecting arched entry
 roundbox('woodLight',x,y+1.55,z+2.39,2.33,2.85,.38,.16)
 roundbox('glass',x,y+1.54,z+2.62,1.95,2.69,.12,.12)
 box('glassLight',x,y+1.6,z+2.7,.035,2.45,.04)
 for dx in [-.86,.86]:box('glassDark',x+dx,y+1.5,z+2.69,.06,2.45,.05)
 torus_front('glassDark',x,y+1.56,z+2.701,.68,.028)
 box('glassDark',x,y+1.56,z+2.71,1.25,.035,.025)
 sphere('glassLight',x-.42,y+2.14,z+2.72,.13,.36,.009)
 halfdome('red',x,y+2.93,z+2.49,1.34,1.05,.79)
 roundbox('cream',x,y+2.93,z+2.56,2.7,.23,1.4,.21)
 for dx in [-2.13,2.13]:
  roundbox('wood',x+dx,y+2.45,z+2.29,1.43,.85,.17,.07)
  roundbox('glassLight',x+dx,y+2.45,z+2.39,1.2,.63,.05,.02)
  box('woodLight',x+dx,y+2.44,z+2.43,.045,.63,.02)
 # entrance mat and information kiosk
 roundbox('stone',x,y+.11,z+2.78,2.9,.19,1.45,.4)
 roundbox('pink',x-2.55,y+.65,z+2.92,.53,1.3,.3,.07)
 roundbox('white',x-2.55,y+.92,z+3.1,.46,.7,.04,.04)
 roundbox('glass',x-2.55,y+.94,z+3.13,.37,.51,.025,.015)
 disc_front('cream',x-2.55,y+.29,z+3.12,.09)
 # wooden deck
 roundbox('wood',x,y-.08,z+1.3,8.6,.25,7.6,.18)
 for j in range(15):
  for i in range(4):roundbox('woodLight' if (i+j)%3 else 'path',x-3.2+i*2.12,y+.06,z-2.05+j*.49,2.04,.1,.45,.025)
 # deck drawn after walls still below them

def cottage(x,y,z):
 roundbox('wood',x,y+.85,z,3.2,1.8,3,.14);roundbox('cream',x,y+1.03,z+.04,2.96,1.7,2.83,.1)
 # gabled roof, slopes with rows of overlapping green tiles
 for side in [-1,1]:
  for row in range(5):
   xx=x+side*(.18+row*.36);yy=y+3.06-row*.28
   for j in range(6):
    zz=z-1.6+j*.62
    v=[(xx-side*.24,yy+.17,zz),(xx+side*.24,yy-.19,zz),(xx+side*.24,yy-.19,zz+.58),(xx-side*.24,yy+.17,zz+.58)]
    add('roofGreenLight' if (j+row)%3==0 else 'roofGreen',v,[(0,1,2,3)])
 for zz in [z-1.7,z+1.95]:
  beam('woodLight',(x-2,y+1.54,zz),(x,y+3.25,zz),.09);beam('woodLight',(x,y+3.25,zz),(x+2,y+1.54,zz),.09)
 roundbox('wood',x,y+.8,z+1.53,.83,1.6,.14,.08)
 disc_front('glassLight',x,y+2.05,z+1.56,.29)
 for dx in [-1.03,1.03]:roundbox('glassLight',x+dx,y+1.05,z+1.53,.55,.65,.1,.05)

# Terrain composition: water splits upper town and a planted foreground island.
terrace(0,-5.3,29,13.8,1.2)
terrace(-1,10,27,9.1,.25)
terrace(-12.4,3.7,4.1,5,.7)
# Far cliffs, individually tiered blocks with grassy rims.
for i in range(12):
 x=-16.8+i*2.95;h=random.choice([3.8,4.7,5.6,6.2]);terrace(x,-15,2.95,4.0,h)
 if i%2==0:tree(x,h+.12,-15.1,.75)
terrace(-16,-4.5,3,13,2.7)
# water bed and waterfall ledges
box('water',0,-.05,3.65,32,.18,3.25)
box('water',-16.1,-1.35,6.5,3.2,.18,20)
box('water',15.6,-1.35,1,2.1,.18,27)
box('water',-5.1,1.26,-9.2,2.5,.08,6.1)
# creek from high cliff
box('water',-5.1,2.2,-12.23,2.2,2.15,.10)
# village paths
path(3,-.35,23,2.3,1.29)
path(3.6,-3.8,2.4,8.2,1.29)
path(-1,9.4,23,2.3,.36)
path(3.6,8.3,2.5,8,.36)
# Center and rear houses
center(5.1,1.45,-7.05)
cottage(-11.1,1.31,-8.4);cottage(-10.6,1.31,-3.8)
# fenced deck edges
fence(.9,-2.15,2.6,1.42);fence(6.4,-2.15,3.1,1.42)
steps(5,-1.9,2.2,1.4,1)
# Two transition treads connect the upper road to the bridge.
roundbox('woodLight',3.7,1.25,.84,2.6,.18,.4,.025)
roundbox('woodLight',3.7,1.06,1.2,2.6,.18,.38,.025)
# main wooden bridge between banks
for j in range(13):roundbox('woodLight' if j%3 else 'wood',3.7,.89,1.2+j*.41,2.6,.18,.38,.025)
for xx in [2.31,5.09]:
 for zz in [1.3,3.35,5.5]:cyl('wood',xx,1.0,zz,.105,1.65)
 beam('woodLight',(xx,1.72,1.2),(xx,1.72,5.55),.068)
steps(3.7,5.85,2.6,.78,2)
# little arched footbridge at back left
for j in range(10):
 xx=-7+j*.41;yy=1.47+.35*math.sin(j/9*math.pi)
 box('woodLight',xx,yy,-6.1,.38,.12,1.7)
# Front raised formal garden
terrace(-5.1,9.85,8.2,6.5,1.13)
path(-5.1,9.85,5.8,4.9,1.26)
steps(-5.1,13.1,2.8,1.15,4)
steps(-1,9.5,1.65,1.15,4)
# round stone fountain in central garden
cyl('stoneDark',-5.1,1.4,9.2,1.46,.25,1.48,32)
cyl('stoneLight',-5.1,1.57,9.2,1.39,.25,1.35,32)
cyl('water',-5.1,1.73,9.2,1.17,.06,1.17,32)
cyl('stone',-5.1,1.94,9.2,.26,.65,.19,16)
sphere('gold',-5.1,2.48,9.2,.48,.48,.48,20,12)
# small sculpted pokeball fountain centerpiece
box('woodDark',-5.1,2.48,9.67,.83,.055,.035);disc_front('cream',-5.1,2.48,9.69,.12)
# trees frame paths and roof
for x,z,s in [(-13.4,-11.1,1),(-8.1,-10.1,.94),(-1.5,-8.1,1.12),(.15,-5.4,.9),(10.5,-7.2,1.1),(12.4,-3.7,.98),(-13,12,1.1),(11.9,11.5,1.16),(9.6,6.8,.81),(-9.9,7.3,.8),(-1.8,-11.3,.8)]:tree(x,1.3 if z<1 else .4,z,s)
for x,z,s in [(13,-10.5,1.25),(14,7.5,1.0),(-13.5,7.1,1),(-8.2,-12,1)]:pine(x,1.25 if z<1 else .3,z,s)
# shaded pergola near pond
for x in [-4,-.5]:
 for z in [-11.5,-9.5]:cyl('wood',x,2.47,z,.1,2.5)
for j in range(8):box('woodLight',-2.25,3.78,-11.8+j*.37,4.1,.14,.13)
for x in [-4,-.5]:box('wood',x,3.68,-10.5,.2,.22,2.7)
for i in range(13):sphere('hedge',random.uniform(-4.2,-.3),3.95,random.uniform(-11.7,-9.4),.5,.27,.4)
# meadow beds and flower borders
for x,z,w,d,y in [(-7.9,8.2,1.6,2.3,1.26),(-2.3,8.2,1.6,2.3,1.26),(-7.8,11.55,1.7,1.9,1.26),(-2.5,11.55,1.7,1.9,1.26),(7.5,7.1,3.7,1,.4),(8.6,12.6,5.4,1.2,.4),(-.7,13.3,3,1,.4),(-11.7,10.1,1.3,3,.4),(-1.0,.1,3.4,.85,1.35),(9.7,.1,3.6,.85,1.35),(-7.2,-2,3.8,1,1.35),(11.3,-6.4,1.4,3,1.35)]:bed(x,y,z,w,d,random.choice(['pink','pinkLight','lilac']))
for x,z in [(1,-3),(9,-3),(-1.4,-6.3),(11,-8.2),(-8,-11),(-13,-6),(7,11.4),(11,6.5),(-.6,7)]:bush(x,1.38 if z<1 else .4,z,1.1)
# grass tufts outside pathways
for i in range(330):
 x=random.uniform(-13.8,13.8);z=random.choice([random.uniform(-11.7,-2.3),random.uniform(6.1,13.8)])
 if (z<0 and (0<x<9.8 or -13<x<-8)) or (z>6 and (-9.5<x<-.7 or 2.2<x<5.2 or 8.2<z<10.7)):continue
 grass(x,1.35 if z<0 else .4,z,random.uniform(.75,1.35))
# fences and town furniture
for x,z,l,y,axis in [(-12,5.7,8,.4,'x'),(6,5.7,7.6,.4,'x'),(-12.8,-.9,5,1.35,'x'),(7.5,-.9,5.4,1.35,'x'),(-14,-10.5,8.7,1.35,'z')]:fence(x,z,l,y,axis)
for x,y,z in [(1.65,1.35,-1),(7.7,1.35,-1),(-7.4,1.35,-.8),(1.7,.4,7),(5.75,.4,7),(-8.5,1.28,12),(-1.6,1.28,12),(10.8,.4,9.5)]:lamp(x,y,z,z>1)
for x,y,z in [(-4.4,1.35,-1.8),(10.4,1.35,-1.8),(8.3,.4,11.5),(-10.8,.4,12.9)]:bench(x,y,z)
for x,z in [(11,-2.5),(-1,-3.4),(-13.6,5.4),(12.7,12.7),(-8.7,-5.7)]:rock(x,1.31 if z<1 else .3,z,random.uniform(.7,1.2))
# stepping stones and lily pads are modeled, shader animates water separately
for i in range(24):
 x=random.uniform(-13.5,13.5);z=random.uniform(2.3,4.95)
 if 2<x<5.6:continue
 cyl('leaf',x,.09,z,.21,.045,.23,10)
 if i%3==0:flower(x,.09,z,'pinkLight',.67)
# sign boards with ivory inserts
for x,y,z in [(-8.5,1.3,-.5),(-8.9,.4,12.4),(7.8,1.35,-3.6)]:
 box('wood',x,y+.5,z,.09,1,.09);roundbox('wood',x,y+1,z,1.05,.69,.13,.05);box('cream',x,y+1,z+.079,.87,.49,.025)
 for j in range(3):box('woodLight',x,y+1.13-j*.1,z+.096,.53-j*.1,.025,.01)
# Facade carpentry and garden details are real geometry.
for xx in [2.15,8.05]:
 roundbox('woodLight',xx,3.05,-4.76,.16,2.9,.16,.04)
 roundbox('stoneLight',xx,1.65,-4.65,.3,.3,.35,.06)
for xx in [4.97,5.23]:beam('gold',(xx,2.55,-4.28),(xx,2.84,-4.28),.028)
for side in [-1,1]:
 xx=5.1+side*3.23
 beam('cream',(xx,4.64,-8.9),(xx,1.75,-8.9),.055)
for xx,zz in [(-4.5,-2.0),(10.5,-2.0),(8.8,11.6)]:
 for i in [-1.25,1.25]:
  roundbox('wood',xx+i,1.53 if zz<0 else .58,zz,.64,.44,.64,.09)
  roundbox('earth',xx+i,1.78 if zz<0 else .83,zz,.51,.04,.51,.04)
  for j in range(5):flower(xx+i+random.uniform(-.2,.2),1.81 if zz<0 else .86,zz+random.uniform(-.2,.2),'pinkLight',.8)
# grass speckles and small flowers on unoccupied ground
for i in range(120):
 x=random.uniform(-13,13);z=random.uniform(11.5,14)
 if -9.5<x<-.5 or 2.1<x<5.1:continue
 flower(x,.4,z,random.choice(['yellow','pinkLight']),.5)
# Continuous surroundings keep ground and river edges out of the playable view.
for side in [-1,1]:
 terrace(side*25,-6,20,15,1.2)
 terrace(side*25,12.5,20,14,.25)
 for i in range(8):
  xx=side*random.uniform(16.8,34);zz=random.choice([random.uniform(-12,-1.5),random.uniform(7,17)])
  tree(xx,1.35 if zz<1 else .4,zz,random.uniform(.9,1.4))
box('water',0,-.08,3.65,82,.16,3.25)
terrace(0,23,78,14,.25)
path(0,17.7,66,2.6,.4)
for i in range(12):
 x=-34+i*6.1;tree(x,.4,random.uniform(20,24),random.uniform(.85,1.2))
for i in range(70):
 x=random.uniform(-16,16);z=random.uniform(14.7,17)
 if 2.3<x<5.4:continue
 grass(x,.39,z,random.uniform(1,1.6))
# A denser garden edge: tall leaf clumps and layered flowering shrubs.
for x,z,w,d,y in [(-12,-11.6,2.4,1.1,1.35),(-8.1,-8.8,1.0,2.3,1.35),(-2.0,-3.0,1.7,1.3,1.35),(10.8,-3.2,2,1.0,1.35),(-12.7,7.0,1.4,1.4,.4),(8.3,6.5,2.1,1,.4),(11.7,12.9,2,1.1,.4),(-1.7,6.9,1.7,.8,.4)]:
 bed(x,y,z,w,d,'pinkLight')
for x,z,y in [(-11.7,-1.8,1.35),(-8.8,-1.75,1.35),(11.5,-1.8,1.35),(0,-2.5,1.35),(-11.1,6.5,.4),(7,6.7,.4),(10.4,10.8,.4),(-10.5,11.2,.4),(-1.7,12.9,.4)]:
 for i in range(15):
  xx=x+random.uniform(-.7,.7);zz=z+random.uniform(-.43,.43)
  for j in range(5):
   a=j*2.4;h=random.uniform(.38,.75);dx=math.cos(a);dz=math.sin(a)
   # curved pointed leaves, wide at the middle and narrowing at the tip
   verts=[(xx,y,zz),(xx+dx*.10-dz*.085,y+h*.45,zz+dz*.10+dx*.085),(xx+dx*.23,y+h,zz+dz*.23),(xx+dx*.10+dz*.085,y+h*.45,zz+dz*.10-dx*.085)]
   add('leafLight' if j%2 else 'hedge',verts,[(0,1,2,3)])
# Wildflowers along the riverbank, with breathing room around the bridge.
for i in range(100):
 x=random.uniform(-12.5,13)
 if 1.9<x<5.4:continue
 flower(x,1.36,random.uniform(.45,1.0),random.choice(['pinkLight','pink','yellow']),random.uniform(.7,1.1))
# Small fruit on shade trees and hanging vines soften the town walls.
for tx,tz in [(-1.5,-8.1),(10.5,-7.2),(-8.1,-10.1)]:
 for i in range(5):
  a=i*2.4;sphere('yellow' if i%2 else 'redLight',tx+math.cos(a)*.94,3.9+random.random()*.3,tz+math.sin(a)*.95,.11,.13,.11,10,7)
for x in [-13,-8,0,9,12.5]:
 for i in range(5):
  sphere('hedge',x+math.sin(i*2)*.12,.9-i*.19,1.72,.15,.19,.08,9,6)

# Bake buckets into a small number of draw calls.
for name,(verts,faces,smooth) in B.items():
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.materials.append(mat(name));mesh.update()
 obj=bpy.data.objects.new('Town_'+name,mesh);bpy.context.collection.objects.link(obj)
 for p,s in zip(mesh.polygons,smooth):p.use_smooth=s
# Area-weighted normals preserve flat wood and stone faces at rounded edges.
for ob in list(bpy.context.scene.objects):
 if ob.type!='MESH' or not any(ob.name=='Town_'+name for name in ['stone','stoneLight','stoneDark','wood','woodLight','woodDark','cream','red','redLight','path','grass','grassEdge']):continue
 bpy.context.view_layer.objects.active=ob;ob.select_set(True)
 mod=ob.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=100
 bpy.ops.object.modifier_apply(modifier=mod.name)
 ob.select_set(False)

# Useful Blender preview setup.
world=bpy.data.worlds.new('Sunny sky') if not bpy.data.worlds else bpy.data.worlds[0];bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.8,.9,1);world.node_tree.nodes['Background'].inputs[1].default_value=.8
bpy.ops.object.light_add(type='AREA', location=(-10,-10,24));bpy.context.object.data.energy=2300;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=10
bpy.ops.object.camera_add(location=(22,-32,29));cam=bpy.context.object;direction=Vector((0,0,2))-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=39;bpy.context.scene.camera=cam
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'public/town.glb'),export_format='GLB',export_cameras=False,export_lights=False)
report={'objects':len(B),'vertices':sum(len(v[0]) for v in B.values()),'faces':sum(len(v[1]) for v in B.values()),'blend':str(ROOT/'blender/pokepia-town.blend')}
(ROOT/'evidence/blender-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
# Painterly material maps, also available in the editable .blend project.
for name,material in M.items():
 kind=next((k for k in ['grass','leaf','hedge','pine','wood','trunk','stone','earth','path','sand','cream','white','red'] if name.startswith(k)),None)
 if not kind:continue
 texname='leaves' if kind in ['leaf','hedge','pine'] else 'wood' if kind in ['wood','trunk'] else 'stone' if kind in ['stone','earth','path','sand'] else 'plaster' if kind in ['cream','white'] else 'roof' if kind=='red' else 'grass'
 nodes=material.node_tree.nodes;links=material.node_tree.links;bsdf=nodes.get('Principled BSDF');base=tuple(bsdf.inputs['Base Color'].default_value)
 image=bpy.data.images.load(str(ROOT/f'public/textures/{texname}-paint.png'),check_existing=True);image.pack()
 tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.projection='BOX';tex.projection_blend=.25
 coords=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='SCALE';mapping.inputs[3].default_value=.55;links.new(coords.outputs['Object'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector'])
 mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.65;mix.inputs[1].default_value=base;links.new(tex.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.94
 bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.03;links.new(tex.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs[0],bsdf.inputs['Normal'])

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/pokepia-town.blend'),compress=True)
