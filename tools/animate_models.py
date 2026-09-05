import struct,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def mul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
report=[]
for id in [25,54,66,132,384]:
 p=ROOT/f'public/models/{id}.glb';raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+n]);off=20+n;blen=struct.unpack_from('<I',raw,off)[0];b=bytearray(raw[off+8:off+8+blen]);original=[a.get('name') for a in j.get('animations',[])]
 def accessor(data,typ,comp):
  while len(b)%4:b.append(0)
  offset=len(b);flat=[v for row in data for v in row] if comp>1 else data;b.extend(struct.pack('<'+'f'*len(flat),*flat));view=len(j.setdefault('bufferViews',[]));j['bufferViews'].append({'buffer':0,'byteOffset':offset,'byteLength':len(flat)*4});idx=len(j.setdefault('accessors',[]));j['accessors'].append({'bufferView':view,'componentType':5126,'count':len(data),'type':typ,'min':[min(data)] if comp==1 else [min(x[i] for x in data) for i in range(comp)],'max':[max(data)] if comp==1 else [max(x[i] for x in data) for i in range(comp)]});return idx
 def clip(name,dur,walking):
  times=[i*dur/32 for i in range(33)];ti=accessor(times,'SCALAR',1);channels=[];samplers=[]
  for ni,node in enumerate(j['nodes']):
   nn=node.get('name','');axis=None;amp=0;phase=0;offset=0
   if 'Thigh' in nn:axis=0;amp=.36 if walking else .025;phase=math.pi if 'RThigh' in nn else 0
   elif 'LArm' in nn or 'RArm' in nn:axis=0;amp=.26 if walking else .04;phase=math.pi if 'LArm' in nn else 0
   elif 'Head' in nn:axis=1;amp=.075 if walking else .19
   elif 'Ear1' in nn:axis=2;amp=.1 if walking else .065
   elif 'Tail' in nn:
    axis=2;amp=.11 if id==384 else .12;digits=''.join(c for c in nn.split('_')[0] if c.isdigit());phase=-int(digits or '1')*.46
   elif id==384 and ('Spine' in nn or 'Neck' in nn):axis=2;amp=.09;phase=.9
   elif id==132 and 'arm_' in nn:axis=2;amp=.14
   if axis is None:continue
   base=node.get('rotation',[0,0,0,1]);qs=[]
   for t in times:
    ang=offset+amp*math.sin(t/dur*math.tau+phase);q=[0,0,0,math.cos(ang/2)];q[axis]=math.sin(ang/2);qs.append(mul(base,q))
   ai=accessor(qs,'VEC4',4);samplers.append({'input':ti,'output':ai,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':ni,'path':'rotation'}})
  j.setdefault('animations',[]).append({'name':name,'samplers':samplers,'channels':channels})
 clip('Town_Fly' if id==384 else 'Town_Walk',3.8 if id==384 else 1.0,True);clip('Town_Idle',3.2,False)
 j['buffers'][0]['byteLength']=len(b)
 js=json.dumps(j,separators=(',',':')).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4)
 p.write_bytes(struct.pack('<III',0x46546c67,2,12+8+len(js)+8+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b)
 report.append({'id':id,'sourceClips':original,'authoredClips':[a['name'] for a in j['animations'] if a['name'].startswith('Town_')],'skinCount':len(j.get('skins',[]))})
(ROOT/'evidence/animations.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
