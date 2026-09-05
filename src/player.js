import * as THREE from 'three';
import {findPath,groundHeight} from './navigation.js';
export async function createPlayer(loader,scene){
 const gltf=await loader.loadAsync(`${import.meta.env.BASE_URL}models/player.glb`),root=new THREE.Group(),model=gltf.scene;root.add(model);scene.add(root);root.position.set(3.7,1.415,-.05);
 model.traverse(o=>{if(o.isMesh){o.castShadow=false;o.receiveShadow=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){m.roughness=.94;m.metalness=0;if(m.map)m.map.anisotropy=8;}}});
 const mixer=new THREE.AnimationMixer(model);const walk=mixer.clipAction(gltf.animations.find(a=>a.name==='Player_Walk'));const idle=mixer.clipAction(gltf.animations.find(a=>a.name==='Player_Idle'));walk.play().setEffectiveTimeScale(1.7).setEffectiveWeight(0);idle.play();
 const shadowCanvas=document.createElement('canvas');shadowCanvas.width=64;shadowCanvas.height=64;const ctx=shadowCanvas.getContext('2d'),gradient=ctx.createRadialGradient(32,32,2,32,32,30);gradient.addColorStop(0,'rgba(65,76,45,.24)');gradient.addColorStop(1,'rgba(65,76,45,0)');ctx.fillStyle=gradient;ctx.fillRect(0,0,64,64);const shadow=new THREE.Mesh(new THREE.PlaneGeometry(.85,.65),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(shadowCanvas),transparent:true,depthWrite:false}));shadow.rotation.x=-Math.PI/2;scene.add(shadow);
 const marker=new THREE.Group();const ring=new THREE.Mesh(new THREE.RingGeometry(.21,.255,40),new THREE.MeshBasicMaterial({color:'#fff6d5',transparent:true,opacity:.85,depthWrite:false,side:THREE.DoubleSide}));ring.rotation.x=-Math.PI/2;marker.add(ring);scene.add(marker);marker.visible=false;
 let path=[],weight=0,destination=null,commands=0,arrivals=0;
 const p={name:'You',id:'player',root,model,mixer,moveTo(point){const next=findPath(root.position,point);if(!next.length)return false;path=next;destination=next.at(-1);marker.position.set(destination.x,destination.y+.025,destination.z);marker.visible=true;commands++;return true;},update(dt,t){
  let travel=1.15*dt;while(path.length&&travel>0){const n=path[0],dx=n.x-root.position.x,dz=n.z-root.position.z,d=Math.hypot(dx,dz);if(d<.035){path.shift();if(!path.length){arrivals++;marker.visible=false;}continue;}
   const step=Math.min(travel,d);root.position.x+=dx/d*step;root.position.z+=dz/d*step;travel-=step;root.position.y=THREE.MathUtils.damp(root.position.y,groundHeight(root.position.x,root.position.z)??n.y,20,dt);
   const yaw=Math.atan2(dx,dz),diff=THREE.MathUtils.euclideanModulo(yaw-root.rotation.y+Math.PI,Math.PI*2)-Math.PI;root.rotation.y+=diff*Math.min(1,dt*12);
  }
  weight=THREE.MathUtils.damp(weight,path.length?1:0,10,dt);walk.setEffectiveWeight(weight);idle.setEffectiveWeight(1-weight);mixer.update(dt);shadow.position.copy(root.position);shadow.position.y+=.015;ring.scale.setScalar(1+Math.sin(t*5)*.07);
 },report(){return {position:root.position.toArray(),destination,pathRemaining:path.length,commands,arrivals,animationTime:mixer.time,walkWeight:+weight.toFixed(3),bones:(()=>{let n=0;model.traverse(o=>{if(o.isBone)n++;});return n;})()}}};
 return p;
}
