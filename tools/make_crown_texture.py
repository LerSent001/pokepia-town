from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import random,math
random.seed(31);N=1024
im=Image.new('RGB',(N,N),(147,153,139));d=ImageDraw.Draw(im)
for row in range(-1,15):
 for col in range(-1,17):
  x=col*72+(row%2)*36;y=row*78;v=random.randrange(-8,9)
  # Rounded shingle-like leaves painted as a single crown surface.
  pts=[(x-39,y-22),(x-35,y+10),(x-22,y+33),(x,y+49),(x+22,y+33),(x+36,y+10),(x+39,y-22),(x,y-38)]
  d.polygon(pts,fill=(165+v,174+v,148+v))
  d.line(pts[1:7],fill=(115+v,133+v,103+v),width=4)
  d.ellipse((x-29,y-29,x+27,y+24),fill=(191+v,201+v,171+v))
  d.arc((x-30,y-30,x+30,y+30),195,310,fill=(217+v,226+v,193+v),width=6)
  d.line([(x-2,y-12),(x,y+17),(x,y+32)],fill=(178+v,192+v,155+v),width=2)
im=im.filter(ImageFilter.GaussianBlur(1.3));im.save(Path(__file__).resolve().parents[1]/'public/textures/leaves-paint.png')
