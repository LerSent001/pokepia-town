import * as THREE from 'three';
import {Water} from 'three/addons/objects/Water2.js';
// Water2 is Three.js's upstream flow-map/reflection/refraction implementation.
export function createRiver(scene,textureLoader){
 const n0=textureLoader.load(`${import.meta.env.BASE_URL}textures/water-normal-1.jpg`),n1=textureLoader.load(`${import.meta.env.BASE_URL}textures/water-normal-2.jpg`);
 const shader={...Water.WaterShader,uniforms:THREE.UniformsUtils.clone(Water.WaterShader.uniforms)};
 shader.fragmentShader=shader.fragmentShader.replaceAll('( vUv * scale )','( vec2(vUv.x*24.0,vUv.y) * scale )').replace('normal.xz * 0.05','normal.xz * 0.028');
 shader.fragmentShader=shader.fragmentShader.replace('gl_FragColor = vec4( color, 1.0 ) * mix( refractColor, reflectColor, reflectance );',`gl_FragColor=vec4(color,1.)*mix(refractColor,reflectColor,min(.38,reflectance+.07));
 float ripples=smoothstep(.49,.60,normalColor.r)*smoothstep(.47,.58,normalColor.g);
 vec3 halfSun=normalize(toEye+normalize(vec3(-.35,.8,.5)));float sparkle=pow(max(0.,dot(normal,halfSun)),70.);
 gl_FragColor.rgb=mix(gl_FragColor.rgb,vec3(.71,.97,.99),ripples*.36)+vec3(.6,.8,.8)*sparkle*.38;`);
 const river=new Water(new THREE.PlaneGeometry(82,3.25),{color:'#8adbdc',scale:2,flowDirection:new THREE.Vector2(1,.12),flowSpeed:.085,reflectivity:.04,textureWidth:512,textureHeight:256,normalMap0:n0,normalMap1:n1,shader});
 river.rotation.x=-Math.PI/2;river.position.set(0,.105,3.65);scene.add(river);
 let sceneTime=0,lastReflection=-1;const reflectedCamera=new THREE.Matrix4();const original=river.onBeforeRender;river.onBeforeRender=function(r,s,c){if(s.overrideMaterial)return;const moving=reflectedCamera.elements.some((v,i)=>Math.abs(v-c.matrixWorld.elements[i])>.001);if(sceneTime-lastReflection<(moving?.20:1.0))return;lastReflection=sceneTime;reflectedCamera.copy(c.matrixWorld);original.call(this,r,s,c);const cfg=river.material.uniforms.config.value;cfg.x=(sceneTime*.085)%.15;cfg.y=(cfg.x+.075)%.15;};
 const foamGeo=new THREE.BufferGeometry(),v=[],idx=[];
 for(const z of [2.06,5.23]){const off=v.length/3;for(let i=0;i<=180;i++){const x=-41+i*82/180;const wobble=Math.sin(x*4.2)*.02+Math.sin(x*1.4)*.017;v.push(x,.127,z+wobble,x,.127,z+wobble+(z<3?.065:-.065));if(i<180){let a=off+i*2;idx.push(a,a+2,a+1,a+1,a+2,a+3);}}}
 foamGeo.setAttribute('position',new THREE.Float32BufferAttribute(v,3));foamGeo.setIndex(idx);foamGeo.computeVertexNormals();const foam=new THREE.Mesh(foamGeo,new THREE.MeshBasicMaterial({color:'#e1fff2',transparent:true,opacity:.47,side:THREE.DoubleSide,depthWrite:false}));scene.add(foam);
 const fallTime={value:0};const fall=new THREE.Mesh(new THREE.PlaneGeometry(2.14,2.14,12,18),new THREE.ShaderMaterial({uniforms:{uTime:fallTime,tNormal:{value:n0}},transparent:true,depthWrite:false,side:THREE.DoubleSide,vertexShader:'varying vec2 vUv;void main(){vUv=uv;vec3 p=position;p.z+=sin(uv.y*22.)*.026;gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.);}',fragmentShader:`varying vec2 vUv;uniform float uTime;uniform sampler2D tNormal;void main(){vec3 n=texture2D(tNormal,vec2(vUv.x*2.,vUv.y*.75+uTime*.45)).rgb;float stripe=pow(.5+.5*sin(vUv.x*85.+n.r*3.),12.);float foam=pow(1.-vUv.y,8.);vec3 col=mix(vec3(.27,.72,.81),vec3(.91,1.,.96),stripe*.48+foam*.6+n.r*.12);gl_FragColor=vec4(col,.83);#include <tonemapping_fragment>\n#include <colorspace_fragment>}`.replace(';#include',';\n#include')}));fall.position.set(-5.1,2.2,-12.16);scene.add(fall);
 return {river,update(t){sceneTime=t;const cfg=river.material.uniforms.config.value;cfg.x=(t*.085)%.15;cfg.y=(cfg.x+.075)%.15;fallTime.value=t;foam.material.opacity=.42+Math.sin(t*.6)*.05;}};
}
