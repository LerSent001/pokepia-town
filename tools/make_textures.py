from PIL import Image,ImageDraw,ImageFilter
import numpy as np,random,pathlib,math
random.seed(321);np.random.seed(321)
P=pathlib.Path(__file__).resolve().parents[1]/'public/textures';N=1024
# Periodic multiscale pigment variation. Seamless because each octave wraps at its edges.
def field():
 z=np.zeros((N,N),np.float32)
 for f,w in [(4,.42),(12,.27),(40,.15),(128,.09),(512,.07)]:
  a=np.random.random((f,f));a=np.pad(a,((0,1),(0,1)),mode='wrap');im=Image.fromarray(np.uint8(a*255)).resize((N+N//f,N+N//f),Image.Resampling.BICUBIC);z+=np.asarray(im,dtype=float)[:N,:N]/255*w
 return z
for name in ['grass','stone','wood','leaves','plaster','roof']:
 noise=field();base=190+noise*55
 if name=='wood':
  yy,xx=np.mgrid[:N,:N];warp=np.sin(xx/110)*13+np.sin(xx/31)*3;base+=np.sin(yy*.14+warp)*8+np.sin(yy*.65+warp*.2)*3
 arr=np.clip(base,0,255).astype('uint8');im=Image.fromarray(arr).convert('RGB');d=ImageDraw.Draw(im,'RGBA')
 if name=='grass':
  for i in range(19000):
   x=random.randrange(N);y=random.randrange(N);v=random.choice([(130,151,116,45),(253,255,194,85),(164,180,137,65)])
   h=random.randint(3,10);d.line([(x-2,y+h),(x,y),(x+2,y+h//2)],fill=v,width=random.choice([1,1,2]))
  for i in range(900):
   x=random.randrange(N);y=random.randrange(N);r=random.randrange(2,7);d.ellipse((x-r,y-r,x+r,y+r),fill=(241,246,173,25))
 elif name=='stone':
  for i in range(8500):
   x=random.randrange(N);y=random.randrange(N);r=random.choice([1,1,2,3]);d.ellipse((x,y,x+r*2,y+r),fill=random.choice([(99,91,77,28),(255,255,244,75)]))
  for i in range(45):
   x=random.randrange(N);y=random.randrange(N);points=[(x+k*3,y+random.randrange(-3,4)) for k in range(random.randrange(4,20))];d.line(points,fill=(103,106,83,33),width=1)
 elif name=='wood':
  for i in range(500):
   y=random.randrange(N);x=random.randrange(N);le=random.randrange(20,230);pts=[(x+k,y+math.sin(k/30)*random.uniform(1,3)) for k in range(le)];d.line(pts,fill=random.choice([(109,86,56,37),(255,235,182,56)]),width=random.choice([1,1,2]))
  for i in range(7):
   x=random.randrange(N);y=random.randrange(N)
   for r in range(4,25,4):d.ellipse((x-r*2.4,y-r*.4,x+r*2.4,y+r*.4),outline=(98,69,38,30),width=1)
 elif name=='leaves':
  for i in range(550):
   x=random.randrange(N);y=random.randrange(N);rx=random.randrange(10,28);ry=random.randrange(8,19)
   d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(232,244,192,random.randrange(15,65)),outline=(98,129,75,38),width=2)
   d.arc((x-rx,y-ry,x+rx,y+ry),195,340,fill=(246,255,212,80),width=3)
   d.line((x-rx*.5,y+ry*.2,x+rx*.6,y-ry*.1),fill=(150,170,112,20),width=1)
 elif name=='plaster':
  for i in range(4000):
   x=random.randrange(N);y=random.randrange(N);d.line((x,y,x+random.randint(1,6),y),fill=(130,124,110,18),width=1)
 elif name=='roof':
  for i in range(5000):
   x=random.randrange(N);y=random.randrange(N);d.line((x,y,x+random.randint(1,4),y+1),fill=(255,255,255,13),width=1)
 im.save(P/f'{name}-paint.png',optimize=True)
 print(name)
