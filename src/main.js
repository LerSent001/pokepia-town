import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {GTAOPass} from 'three/addons/postprocessing/GTAOPass.js';
import {OutputPass} from 'three/addons/postprocessing/OutputPass.js';
import {createTownMaterials} from './materials.js';
import {createRiver} from './water.js';
import './style.css';
import {createPlayer} from './player.js';
const $=id=>document.getElementById(id),TARGET_FPS=30;
const asset=path=>`${import.meta.env.BASE_URL}${path}`;
const renderer=new THREE.WebGLRenderer({canvas:$('world'),antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,1.35));renderer.setSize(innerWidth,innerHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.NeutralToneMapping;renderer.toneMappingExposure=1.0;
const scene=new THREE.Scene();scene.background=new THREE.Color('#bedcbe');scene.fog=new THREE.Fog('#bedcbe',55,105);
const aspect=innerWidth/innerHeight,camera=new THREE.OrthographicCamera(-21*aspect,21*aspect,21,-21,.1,160);
const HOME_TARGET=new THREE.Vector3(3,2,-2),HOME_OFFSET=new THREE.Vector3(8,21,31),HOME_ZOOM=2.35;
camera.position.copy(HOME_TARGET).add(HOME_OFFSET);camera.zoom=HOME_ZOOM;camera.updateProjectionMatrix();
const controls=new OrbitControls(camera,renderer.domElement);controls.target.copy(HOME_TARGET);controls.enableDamping=true;controls.dampingFactor=.09;controls.enablePan=false;controls.minZoom=1.95;controls.maxZoom=2.9;controls.minPolarAngle=.72;controls.maxPolarAngle=1.04;controls.minAzimuthAngle=-.10;controls.maxAzimuthAngle=.48;controls.update();
scene.add(new THREE.HemisphereLight('#fff9ee','#b8c4ce',2.15));
const sun=new THREE.DirectionalLight('#fff1df',2.35);sun.position.set(-16,30,18);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-24,right:24,top:24,bottom:-24,near:1,far:85});sun.shadow.bias=-.0002;sun.shadow.normalBias=.023;sun.shadow.radius=3;scene.add(sun);
const fill=new THREE.DirectionalLight('#c8e4ff',.8);fill.position.set(12,15,-15);scene.add(fill);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(230,230),new THREE.MeshStandardMaterial({color:'#a8cd6b',roughness:1}));ground.rotation.x=-Math.PI/2;ground.position.y=-2;ground.receiveShadow=true;scene.add(ground);
const manager=new THREE.LoadingManager();manager.onProgress=(url,n,total)=>{$('load-bar').style.width=`${Math.min(98,n/total*100)}%`;};
const draco=new DRACOLoader(manager).setDecoderPath(asset('draco/'));draco.setWorkerLimit(2);const loader=new GLTFLoader(manager).setDRACOLoader(draco),textureLoader=new THREE.TextureLoader(manager);
const paint=createTownMaterials(textureLoader);
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));
const ao=new GTAOPass(scene,camera,innerWidth,innerHeight,undefined,{radius:.28,distanceExponent:1,thickness:.24,samples:8},{lumaPhi:5,depthPhi:2,normalPhi:3,radius:5,samples:8});ao.blendIntensity=.30;composer.addPass(ao);composer.addPass(new OutputPass());
const species=[
{id:132,name:'Ditto',height:.95,route:[[1.4,.44,8],[3.7,.44,8],[3.7,.44,11],[1.4,.44,9.4]],speed:.65},
{id:25,name:'Pikachu',height:1.45,route:[[2.7,1.42,-.5],[5,1.42,-.5],[7.7,1.42,-.5],[3.7,1.42,-.5],[-2,1.42,-.5]],speed:.78},
{id:66,name:'Machop',height:1.6,route:[[7,.48,9.4],[10.5,.48,9.4],[7,.48,9.4],[5.3,.48,9.4]],speed:.72},
{id:54,name:'Psyduck',height:1.42,route:[[-7.8,1.43,-.25],[-5.3,1.43,-.25],[-2.5,1.43,-.25],[-6,1.43,-.25]],speed:.52},
{id:384,name:'Rayquaza',height:10,speed:1}
];
const residents=[],modelReport=[],V=new THREE.Vector3(),B=new THREE.Box3();let town=null,player=null,ready=false,paused=false,follow=null,cameraMove=null,water=null,slowWindows=0;
let toastTimer;function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),1700);}
function makeShadow(size){const canvas=document.createElement('canvas');canvas.width=64;canvas.height=64;let c=canvas.getContext('2d');let g=c.createRadialGradient(32,32,1,32,32,30);g.addColorStop(0,'rgba(49,70,29,.32)');g.addColorStop(1,'rgba(49,70,29,0)');c.fillStyle=g;c.fillRect(0,0,64,64);let m=new THREE.Mesh(new THREE.PlaneGeometry(size,size),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(canvas),transparent:true,depthWrite:false}));m.rotation.x=-Math.PI/2;return m;}
function renderPortrait(root,height,focusY=height*.49,headOnly=false){
 const prev=root.position.clone(),prevRot=root.rotation.clone();const iconScene=new THREE.Scene();iconScene.add(new THREE.HemisphereLight(0xffffff,0xa6b093,3));let l=new THREE.DirectionalLight(0xffffff,3);l.position.set(-3,6,5);iconScene.add(l);scene.remove(root);iconScene.add(root);root.position.set(0,0,0);root.rotation.set(0,.3,0);
 const iconCam=new THREE.PerspectiveCamera(30,1.4,.01,100);const h=height;iconCam.position.set(h*.2,focusY+h*.16,h*2.9);iconCam.lookAt(0,focusY,0);
 if(headOnly){root.updateMatrixWorld(true);const head=root.getObjectByName('Head');if(head){const focus=head.getWorldPosition(new THREE.Vector3());const jaw=root.getObjectByName('Jaw');const forward=jaw.getWorldPosition(new THREE.Vector3()).sub(focus).normalize();focus.addScaledVector(forward,.23);const side=new THREE.Vector3().crossVectors(forward,new THREE.Vector3(0,1,0)).normalize();iconCam.position.copy(focus).addScaledVector(forward,1.75).addScaledVector(side,.47);iconCam.position.y+=.30;iconCam.lookAt(focus);}}
 const oldClear=renderer.getClearColor(new THREE.Color());const oldAlpha=renderer.getClearAlpha();const oldSize=renderer.getSize(new THREE.Vector2());const oldRatio=renderer.getPixelRatio();renderer.setPixelRatio(1);renderer.setSize(280,200,false);renderer.setClearColor(0xffffff,0);renderer.render(iconScene,iconCam);const portrait=renderer.domElement.toDataURL('image/png');renderer.setClearColor(oldClear,oldAlpha);renderer.setPixelRatio(oldRatio);renderer.setSize(oldSize.x,oldSize.y,false);iconScene.remove(root);scene.add(root);root.position.copy(prev);root.rotation.copy(prevRot);
 return portrait;
}
async function loadResident(s,index){
 const gltf=await loader.loadAsync(asset(`models/${s.id}.glb`));const model=gltf.scene;if(s.id===25)model.rotation.x=-Math.PI/2;
 model.updateMatrixWorld(true);B.setFromObject(model);const size=B.getSize(new THREE.Vector3());const scale=s.id===384?s.height/Math.max(size.x,size.y,size.z):s.height/size.y;
 model.scale.multiplyScalar(scale);model.updateMatrixWorld(true);B.setFromObject(model);const center=B.getCenter(new THREE.Vector3());model.position.x-=center.x;model.position.z-=center.z;model.position.y-=B.min.y;
 model.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;o.frustumCulled=false;const mats=Array.isArray(o.material)?o.material:[o.material];mats.forEach(m=>{if(m.isMeshStandardMaterial){m.metalness=0;m.roughness=.96;}});if(s.id===132){const original=mats[0];o.material=new THREE.MeshStandardMaterial({map:original.map,color:'#e6b4f3',roughness:1,metalness:0,emissive:'#d9a6ed',emissiveMap:original.map,emissiveIntensity:.24,side:THREE.DoubleSide});}}});
 const root=new THREE.Group();root.add(model);scene.add(root);
 const mixer=new THREE.AnimationMixer(model);const walkClip=gltf.animations.find(a=>a.name===(s.id===384?'Town_Fly':'Town_Walk'));const idleClip=gltf.animations.find(a=>a.name==='Town_Idle');const walk=mixer.clipAction(walkClip);const idle=mixer.clipAction(idleClip);walk.play();idle.play();idle.setEffectiveWeight(0);
 const r={...s,root,model,mixer,walk,idle,phase:index*1.3,routeIndex:1,pause:0,walkWeight:1,elapsed:0};
 if(s.route)root.position.fromArray(s.route[0]);else root.position.set(-3,8,-10);
 r.shadow=makeShadow(s.id===384?4.6:s.height*1.2);scene.add(r.shadow);residents.push(r);
 model.updateMatrixWorld(true);const headNode=model.getObjectByName('Head_9'),hipsNode=model.getObjectByName('Hips_32'),footNode=model.getObjectByName('LFoot_21');const upright=s.id===25?{headY:headNode.getWorldPosition(new THREE.Vector3()).y,hipsY:hipsNode.getWorldPosition(new THREE.Vector3()).y,footY:footNode.getWorldPosition(new THREE.Vector3()).y}:undefined;
 modelReport.push({id:s.id,name:s.name,upright,animations:gltf.animations.map(a=>({name:a.name,duration:a.duration,tracks:a.tracks.length})),dimensions:size.toArray(),scale,meshes:(()=>{let n=0;model.traverse(o=>{if(o.isMesh)n++;});return n;})()});
 // Render a tiny true 3D portrait into the roster, using the same source model.
 const portrait=renderPortrait(root,s.height,undefined,s.id===384);
 const button=document.createElement('button');button.className='resident';button.title=s.name;button.dataset.id=s.id;button.setAttribute('aria-label',`Follow ${s.name}`);button.innerHTML=`<img class="portrait" src="${portrait}" alt="${s.name}"/>`;button.onclick=()=>selectResident(r);r.button=button;r.portrait=portrait;
 return r;
}
function updateResident(r,dt,t){
 r.elapsed+=dt;
 if(r.id===384){
  const a=t*.07+.4;r.root.position.set(Math.cos(a)*9,8.6+Math.sin(t*.33)*.5,-8+Math.sin(a)*4);r.root.rotation.y=-a;r.root.rotation.z=Math.sin(t*.6)*.04;r.mixer.update(dt);r.shadow.position.set(r.root.position.x,1.39,r.root.position.z);return;
 }
 if(r.pause>0){r.pause-=dt;r.walkWeight=THREE.MathUtils.damp(r.walkWeight,0,5,dt);}else{
  const dest=r.route[r.routeIndex];V.fromArray(dest).sub(r.root.position);V.y=0;const distance=V.length();
  if(distance<.13){r.routeIndex=(r.routeIndex+1)%r.route.length;r.pause=1.8+((r.routeIndex*7+r.id)%7)*.36;}else{
   V.divideScalar(distance);let angle=Math.atan2(V.x,V.z);let diff=THREE.MathUtils.euclideanModulo(angle-r.root.rotation.y+Math.PI,Math.PI*2)-Math.PI;r.root.rotation.y+=diff*Math.min(1,dt*5);
   // Local separation keeps walking residents from passing through one another.
   let speed=r.speed;for(const other of [...residents,...(player?[player]:[])]){if(other===r||other.id===384)continue;const dist=r.root.position.distanceTo(other.root.position);if(dist<1.1&&dist>.01){const toward=V.dot(other.root.position.clone().sub(r.root.position));if(toward>0)speed*=.2;}}
   r.root.position.addScaledVector(V,Math.min(distance,speed*dt));r.walkWeight=THREE.MathUtils.damp(r.walkWeight,1,5,dt);
  }
 }
 r.walk.setEffectiveWeight(r.walkWeight);r.idle.setEffectiveWeight(1-r.walkWeight);r.mixer.update(dt);
 const bob=Math.abs(Math.sin(r.elapsed*Math.PI*2))* (r.id===132?.065:.036)*r.walkWeight;
 r.root.position.y=r.route[0][1]+bob;
 if(r.id===132){const squash=Math.sin(r.elapsed*6)*.055*r.walkWeight;r.model.scale.y=r.scaleBase*(1-squash);r.model.scale.x=r.scaleBase*(1+squash*.55);r.model.scale.z=r.scaleBase*(1+squash*.55);}
 r.shadow.position.set(r.root.position.x,r.route[0][1]-.018,r.root.position.z);
}
function showSelected(r){$('selected-portrait').src=r.portrait;$('selected-portrait').alt=r.name;$('selected-name').textContent=r.name;}
function selectResident(r){follow=follow===r?null:r;cameraMove=null;residents.forEach(p=>p.button.classList.toggle('selected',p===follow));showSelected(r);if(follow){camera.zoom=r.id===384?2.08:2.55;camera.updateProjectionMatrix();}else home();}
function home(){follow=null;residents.forEach(p=>p.button.classList.remove('selected'));cameraMove={pos:HOME_TARGET.clone().add(HOME_OFFSET),target:HOME_TARGET.clone(),zoom:HOME_ZOOM};}
$('home').onclick=home;
$('player-focus').onclick=()=>{if(player){follow=player;cameraMove=null;showSelected(player);residents.forEach(r=>r.button.classList.remove('selected'));}};
$('pause').onclick=()=>{paused=!paused;$('pause').textContent=paused?'▷':'Ⅱ';$('pause').setAttribute('aria-label',paused?'Resume':'Pause');$('pause').title=paused?'Resume':'Pause';};
$('photo').onclick=()=>{composer.render();const a=document.createElement('a');a.href=renderer.domElement.toDataURL('image/png');a.download=`Pokepia-${Date.now()}.png`;a.click();toast('Saved');};
addEventListener('keydown',e=>{if(e.isComposing)return;if(e.key.toLowerCase()==='h')document.body.classList.toggle('clean');if(e.key==='Escape'||e.key.toLowerCase()==='b')home();});
let down=null;renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2(e.clientX/innerWidth*2-1,1-e.clientY/innerHeight*2),camera);if(player&&town){const hits=ray.intersectObject(town,true);const groundHit=hits.find(h=>h.face&&h.face.normal.y>.4);if(groundHit&&player.moveTo(groundHit.point)){follow=player;cameraMove=null;showSelected(player);residents.forEach(r=>r.button.classList.remove('selected'));return;}}});
const pollen=new THREE.InstancedMesh(new THREE.SphereGeometry(.018,4,3),new THREE.MeshBasicMaterial({color:'#ffffdf',transparent:true,opacity:.4}),35);scene.add(pollen);const dummy=new THREE.Object3D();
async function init(){try{
 const gltf=await loader.loadAsync(asset('town.glb'));gltf.scene.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;if(o.name==='Town_water'){o.castShadow=false;o.material=new THREE.MeshStandardMaterial({color:'#5dbdcd',roughness:.82,metalness:0});}else paint(o);});scene.add(gltf.scene);town=gltf.scene;water=createRiver(scene,textureLoader);
 for(let i=0;i<species.length;i++){const r=await loadResident(species[i],i);$('roster').append(r.button);}
 player=await createPlayer(loader,scene);player.portrait=renderPortrait(player.root,1.0,1.55);showSelected(player);renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);ao.setSize(Math.round(innerWidth*.6),Math.round(innerHeight*.6));ready=true;last=performance.now();lastSimulation=last;sampleStart=last;samples=[];
 $('load-bar').style.width='100%';$('loading').style.opacity=0;setTimeout(()=>$('loading').remove(),450);
}catch(e){console.error(e);$('load-message').textContent=e.message;}}
let last=performance.now(),lastSimulation=last,time=0,sampleStart=last,samples=[],stats={},telemetryTime=0;const history=[];
function frame(now){requestAnimationFrame(frame);if(now-last<1000/TARGET_FPS-.8)return;const ms=now-lastSimulation;lastSimulation=now;last+=Math.max(1,Math.round((now-last)/(1000/TARGET_FPS)))*(1000/TARGET_FPS);const dt=Math.min(ms/1000,.0667);if(!paused)time+=dt;
 if(ready&&!paused)for(const r of residents){if(!r.scaleBase)r.scaleBase=r.model.scale.x;updateResident(r,dt,time);}
 if(player&&ready&&!paused)player.update(dt,time);
 if(water)water.update(time);
 for(let i=0;i<35;i++){dummy.position.set(Math.sin(i*27.7)*13+Math.sin(time*.13+i)*.3,2+(i%9)*.3+Math.sin(time*.3+i)*.1,Math.cos(i*17.1)*11);dummy.updateMatrix();pollen.setMatrixAt(i,dummy.matrix);}pollen.instanceMatrix.needsUpdate=true;
 if(follow){const p=follow.root.position;const target=new THREE.Vector3(THREE.MathUtils.clamp(p.x,-7,9),follow.id===384?4.5:2.2,THREE.MathUtils.clamp(p.z-(follow===player?3:0),-7,9));const delta=target.sub(controls.target).multiplyScalar(Math.min(1,dt*2));controls.target.add(delta);camera.position.add(delta);}
 if(cameraMove){camera.position.lerp(cameraMove.pos,.11);controls.target.lerp(cameraMove.target,.11);camera.zoom=THREE.MathUtils.lerp(camera.zoom,cameraMove.zoom,.13);camera.updateProjectionMatrix();if(camera.position.distanceTo(cameraMove.pos)<.03)cameraMove=null;}
 controls.update();if(ready){renderer.info.autoReset=false;renderer.info.reset();composer.render(dt);sun.shadow.autoUpdate=false;}else renderer.render(scene,camera);
 if(ready&&!document.hidden){samples.push(ms);if(now-sampleStart>=1000){const avg=samples.reduce((a,b)=>a+b,0)/samples.length,sorted=[...samples].sort((a,b)=>a-b);stats={targetFps:30,fps:+(1000/avg).toFixed(1),frameMs:+avg.toFixed(2),p95Ms:+sorted[Math.floor(sorted.length*.95)].toFixed(2),drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,pixelRatio:renderer.getPixelRatio(),viewport:[innerWidth,innerHeight],sampleFrames:samples.length,time:+time.toFixed(1),characters:residents.length+(player?1:0),player:player?.report(),paused,water:'Three.js Water2',ao:'GTAO'};$('fps').textContent=Math.round(stats.fps);$('telemetry').textContent=JSON.stringify(stats);history.push({...stats,recordedAt:new Date().toISOString()});if(history.length>120)history.shift();slowWindows=avg>39?slowWindows+1:0;if(slowWindows>=5&&renderer.getPixelRatio()>.9){const pr=Math.max(.9,renderer.getPixelRatio()*.9);renderer.setPixelRatio(pr);composer.setPixelRatio(pr);slowWindows=0;}samples=[];sampleStart=now;telemetryTime++;if(import.meta.env.DEV&&telemetryTime%5===0)fetch('/__evidence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({stats,windows:history.slice(-5),modelReport,residents:residents.map(r=>({name:r.name,position:r.root.position.toArray(),animationTime:r.mixer.time}))})}).catch(()=>{});}}
}
addEventListener('resize',()=>{const a=innerWidth/innerHeight;camera.left=-21*a;camera.right=21*a;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);composer.setSize(innerWidth,innerHeight);ao.setSize(Math.round(innerWidth*.6),Math.round(innerHeight*.6));});
document.addEventListener('visibilitychange',()=>{last=performance.now();lastSimulation=last;sampleStart=last;samples=[];});
requestAnimationFrame(frame);init();
