import json,struct,math,pathlib
P=pathlib.Path(__file__).resolve().parents[1]
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def inv(q):return [-q[0],-q[1],-q[2],q[3]]
def norm(v):
 d=sum(x*x for x in v)**.5;return [x/d for x in v]
def rot(q,v):return mul(mul(q,[*v,0]),inv(q))[:3]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
for id in [25,54,66,132,384]:
 p=P/f'public/models/{id}.glb';raw=(P/f'tools/source-models/{id}.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);off=20+n;blen=struct.unpack_from('<I',raw,off)[0];b=bytearray(raw[off+8:off+8+blen]);j['animations']=[a for a in j.get('animations',[]) if not a.get('name','').startswith('Town_')]
 nodes=j['nodes'];parents={c:i for i,a in enumerate(nodes) for c in a.get('children',[])}
 def worldq(i):
  q=nodes[i].get('rotation',[0,0,0,1]);return mul(worldq(parents[i]),q) if i in parents else q
 if id in [25,54,66]:
  for ni,node in enumerate(nodes):
   if not any(t in node.get('name','') for t in ['LArm','RArm']):continue
   child=next((c for c in node.get('children',[]) if 'ForeArm' in nodes[c].get('name','')),None)
   if child is None:continue
   q=worldq(ni);direction=norm(rot(q,nodes[child]['translation']));desired=norm([direction[0]*.16,direction[1]*.16,-.98] if id==25 else [direction[0]*.27,-.96,direction[2]*.27]);qd=norm(cross(direction,desired)+[1+sum(a*b for a,b in zip(direction,desired))]);local=mul(mul(inv(q),qd),q);node['rotation']=mul(node.get('rotation',[0,0,0,1]),local)
 def accessor(data,typ,comp):
  while len(b)%4:b.append(0)
  offset=len(b);flat=[v for row in data for v in row] if comp>1 else data;b.extend(struct.pack('<'+'f'*len(flat),*flat));view=len(j.setdefault('bufferViews',[]));j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(flat)*4});idx=len(j.setdefault('accessors',[]));j['accessors'].append({'bufferView':view,'componentType':5126,'count':len(data),'type':typ,'min':[min(data)] if comp==1 else [min(x[i] for x in data) for i in range(comp)],'max':[max(data)] if comp==1 else [max(x[i] for x in data) for i in range(comp)]});return idx
 def clip(name,dur,walking):
  times=[i*dur/32 for i in range(33)];ti=accessor(times,'SCALAR',1);channels=[];samplers=[]
  for ni,node in enumerate(nodes):
   nn=node.get('name','');axis=None;amp=0;phase=0
   if 'Thigh' in nn:axis=[1,0,0];amp=.44 if walking else .015;phase=math.pi if 'RThigh' in nn else 0
   elif 'LArm' in nn or 'RArm' in nn:axis=[1,0,0];amp=(.19 if id==25 else .29) if walking else .025;phase=math.pi if 'LArm' in nn else 0
   elif 'Head' in nn:axis=[0,1,0];amp=.055 if walking else .16
   elif 'Ear1' in nn:axis=[0,0,1];amp=.08
   elif 'Tail' in nn:
    axis=[0,1,0];amp=.11 if id==384 else .12;digits=''.join(c for c in nn.split('_')[0] if c.isdigit());phase=-int(digits or '1')*.46
   elif id==384 and ('Spine' in nn or 'Neck' in nn):axis=[0,1,0];amp=.09;phase=.9
   elif id==132 and 'arm_' in nn:axis=[0,0,1];amp=.1
   if axis is None:continue
   if id==25 and axis==[0,1,0]:axis=[0,0,1]
   axis=norm(rot(inv(worldq(ni)),axis));base=node.get('rotation',[0,0,0,1]);qs=[]
   for t in times:
    ang=amp*math.sin(t/dur*math.tau+phase);q=[a*math.sin(ang/2) for a in axis]+[math.cos(ang/2)];qs.append(mul(base,q))
   ai=accessor(qs,'VEC4',4);samplers.append({'input':ti,'output':ai,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':ni,'path':'rotation'}})
  j.setdefault('animations',[]).append({'name':name,'samplers':samplers,'channels':channels})
 clip('Town_Fly' if id==384 else 'Town_Walk',3.8 if id==384 else .9,True);clip('Town_Idle',3.2,False)
 j['buffers'][0]['byteLength']=len(b);js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4);p.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b)
 print(id,'posed + walk / idle clips')
