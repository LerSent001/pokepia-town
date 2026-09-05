import numpy as np,json,struct,pathlib,math
p=pathlib.Path(__file__).resolve().parents[1]/'tools/source-models/25.glb';b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);buf=b[28+n:];nodes=j['nodes']
def access(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];types={5126:'<f4',5123:'<u2',5125:'<u4'};dim={'SCALAR':1,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];return np.frombuffer(buf,dtype=types[a['componentType']],count=a['count']*dim,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape((-1,dim))
def matrix(t,r,s):
 x,y,z,w=r;R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
 M=np.eye(4);M[:3,:3]=R@np.diag(s);M[:3,3]=t;return M
parents={c:i for i,a in enumerate(nodes) for c in a.get('children',[])}
def pose(t):
 nd=[dict(x) for x in nodes]
 if t is not None:
  a=j['animations'][0]
  for c in a['channels']:
   sa=a['samplers'][c['sampler']];times=access(sa['input'])[:,0];out=access(sa['output']);idx=np.searchsorted(times,t);idx=max(1,min(len(times)-1,idx));u=float(np.clip((t-times[idx-1])/(times[idx]-times[idx-1]),0,1));v=out[idx-1]*(1-u)+out[idx]*u
   if c['target']['path']=='rotation':v/=np.linalg.norm(v)
   nd[c['target']['node']][c['target']['path']]=v.tolist()
 def world(i):
  n=nd[i];m=np.array(n['matrix']).reshape((4,4)).T if 'matrix'in n else matrix(n.get('translation',[0,0,0]),n.get('rotation',[0,0,0,1]),n.get('scale',[1,1,1]));return world(parents[i])@m if i in parents else m
 d={a['name']:world(i)[:3,3] for i,a in enumerate(nodes) if any(k in a.get('name','') for k in ['Head_','Hips_','LFoot_','RFoot_'])}
 return nd,d
for t in [None,0,.25,.5,.75,1,1.25,1.5,2,2.5,3,3.5,4,4.5,5]:
 _,d=pose(t);print(t,{k:np.round(v,3).tolist() for k,v in d.items()})
