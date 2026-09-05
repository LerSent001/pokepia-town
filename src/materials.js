import * as THREE from 'three';
const kinds={grass:['grass',.24,.008],leaf:['leaves',.65,.018],hedge:['leaves',.9,.06],pine:['leaves',.55,.05],wood:['wood',.6,.025],trunk:['wood',.6,.035],stone:['stone',.75,.035],earth:['stone',.5,.045],path:['stone',.8,.02],sand:['stone',.7,.02],cream:['plaster',.9,.012],white:['plaster',.9,.008],red:['roof',.7,.006]};
export function createTownMaterials(loader){
 const textures={};for(const n of ['grass','stone','wood','leaves','plaster','roof']){const t=loader.load(`${import.meta.env.BASE_URL}textures/${n}-paint.png`);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;textures[n]=t;}
 return function apply(o){const m=o.material;const key=Object.keys(kinds).find(k=>m.name.toLowerCase().startsWith(k));m.roughness=.94;m.metalness=0;if('specularIntensity'in m)m.specularIntensity=.15;
 if(/glass/i.test(m.name)){m.roughness=.27;m.color.multiplyScalar(1.08);return;}
 if(/metal|gold/.test(m.name)){m.roughness=.7;return;}
 if(!key)return;const [texture,scale,bump]=kinds[key];
 m.onBeforeCompile=shader=>{
 shader.uniforms.uPaint={value:textures[texture]};shader.uniforms.uPaintScale={value:scale};shader.uniforms.uBumpStrength={value:bump};
 shader.vertexShader='varying vec3 vPaintPosition;varying vec3 vPaintNormal;\n'+shader.vertexShader;
 shader.vertexShader=shader.vertexShader.replace('#include <worldpos_vertex>','#include <worldpos_vertex>\nvPaintPosition=(modelMatrix*vec4(transformed,1.)).xyz;vPaintNormal=normalize(mat3(modelMatrix)*objectNormal);');
 shader.fragmentShader=`uniform sampler2D uPaint;uniform float uPaintScale;uniform float uBumpStrength;varying vec3 vPaintPosition;varying vec3 vPaintNormal;\n`+shader.fragmentShader;
 shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
 vec3 paintWeight=pow(abs(normalize(vPaintNormal)),vec3(5.));paintWeight/=max(.001,paintWeight.x+paintWeight.y+paintWeight.z);
 vec3 paintP=vPaintPosition*uPaintScale;
 vec3 paintValue=texture2D(uPaint,paintP.zy).rgb*paintWeight.x+texture2D(uPaint,paintP.xz).rgb*paintWeight.y+texture2D(uPaint,paintP.xy).rgb*paintWeight.z;
 diffuseColor.rgb*=.24+paintValue*.9;
 float paintHeight=dot(paintValue,vec3(.333333));
 `);
 shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`#include <normal_fragment_maps>
 vec3 paintDX=dFdx(-vViewPosition),paintDY=dFdy(-vViewPosition);
 vec3 paintR1=cross(paintDY,normal),paintR2=cross(normal,paintDX);float paintDet=dot(paintDX,paintR1);
 normal=normalize(abs(paintDet)*normal-sign(paintDet)*(dFdx(paintHeight)*paintR1+dFdy(paintHeight)*paintR2)*uBumpStrength);
 `);
 };m.customProgramCacheKey=()=>`paint-${key}`;
 };
}
