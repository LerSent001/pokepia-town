"""Fetch the five reference assets and keep immutable originals for animation rebuilding."""
import json,urllib.request,pathlib,concurrent.futures,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'tools/source-models';SOURCE.mkdir(exist_ok=True)
repo='Pokemon-3D-api/assets'
commit=json.load(urllib.request.urlopen(f'https://api.github.com/repos/{repo}/commits/main'))['sha']
def fetch(id):
 url=f'https://raw.githubusercontent.com/{repo}/{commit}/models/opt/regular/{id}.glb'
 p=SOURCE/f'{id}.glb';urllib.request.urlretrieve(url,p)
 return {'id':id,'url':url,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:assets=list(pool.map(fetch,[132,25,66,54,384]))
(ROOT/'evidence/asset-sources.json').write_text(json.dumps({'repository':f'https://github.com/{repo}','commit':commit,'assets':assets},indent=2))
print('Saved',len(assets),'originals at',commit)
