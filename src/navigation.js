// World-space walk surface, matching the authored terraces, bridge and garden.
const inside=(x,z,a,b,c,d)=>x>=a&&x<=b&&z>=c&&z<=d;
const circles=[[-13.4,-11.1,.55],[-8.1,-10.1,.55],[-1.5,-8.1,.62],[.15,-5.4,.55],[10.5,-7.2,.62],[12.4,-3.7,.55],[-1.8,-11.3,.5],[-13,12,.55],[11.9,11.5,.6],[9.6,6.8,.48],[-9.9,7.3,.48],[-5.1,9.2,1.8],[1,-3,.85],[9,-3,.85],[-1.4,-6.3,.8],[11,-8.2,.8],[7,11.4,.85],[11,6.5,.8],[-.6,7,.85],[1.65,-1,.36],[7.7,-1,.36],[-7.4,-.8,.36],[1.7,7,.36],[5.75,7,.36],[10.8,9.5,.36]];
const blocks=[
 [1.45,8.8,-10.5,-4.22],[-13.5,-8.3,-10.7,-6.1],[-13.3,-8,-5.9,-2.1],
 [-8.9,-6.8,6.65,9.05],[-3.3,-1.2,6.65,9.05],[-8.95,-6.55,10.35,12.75],[-3.5,-1.2,10.35,12.75],
 [5.4,9.6,6.35,7.85],[5.6,11.6,11.7,13.55],[-2.5,1.1,12.55,14],[-12.65,-10.8,8.2,11.8],
 [-5.8,-2.9,-2.65,-1.3],[8.9,12,-2.65,-1.25],[-9.45,-4.85,-2.65,-1.25],[-2.95,.95,-.6,.72],[7.55,11.85,-.6,.72],
 [-.75,2.55,-2.5,-1.85],[6.05,9.85,-2.5,-1.85],[-13.5,-8,5.4,6.1],[5.8,13.5,5.35,6.1]
];
export function groundHeight(x,z){
 // Bridge and stair treads are the only route across the stream.
 if(inside(x,z,2.75,4.65,.65,6.75)){
  if(z<1.05)return 1.34;if(z<1.4)return 1.15;if(z<5.75)return .985;if(z<6.06)return .80;if(z<6.48)return .56;return .48;
 }
 if(inside(x,z,-6.15,-4.05,12.8,14.6))return z<13.25?1.18:z<13.66?.94:z<14.08?.70:.46;
 if(inside(x,z,-8.85,-1.4,6.85,12.8))return 1.38;
 if(inside(x,z,-13.35,13.35,-12.3,1.24)){
  if(inside(x,z,-6.68,-3.48,-12.3,-5.45))return null;
  return z> -1.46 || inside(x,z,2.35,4.8,-7.8,1.2)?1.415:1.33;
 }
 if(inside(x,z,-13.3,12.9,6.2,15.2)){
  if(inside(x,z,-9.55,-.72,6.2,13.3))return null;
  return inside(x,z,2.3,4.9,6.2,12.3)||inside(x,z,-12.5,10.5,8.25,10.6)?.485:.39;
 }
 return null;
}
export function walkable(x,z){const y=groundHeight(x,z);if(y===null)return false;return !blocks.some(b=>inside(x,z,...b))&&!circles.some(([a,b,r])=>Math.hypot(x-a,z-b)<r);}
const STEP=.3,MINX=-13.5,MINZ=-12.3,NX=91,NZ=93;
const nodes=Array.from({length:NX*NZ},(_,i)=>{let x=MINX+(i%NX)*STEP,z=MINZ+Math.floor(i/NX)*STEP;return {id:i,x,z,y:groundHeight(x,z),valid:walkable(x,z)};});
function neighbors(n){const x=n.id%NX,z=Math.floor(n.id/NX),out=[];for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++){if(!a&&!b)continue;if(x+a<0||x+a>=NX||z+b<0||z+b>=NZ)continue;const m=nodes[n.id+a+b*NX];if(!m.valid||Math.abs(m.y-n.y)>.28)continue;if(a&&b&&(!nodes[n.id+a].valid||!nodes[n.id+b*NX].valid))continue;out.push(m);}return out;}
function nearest(x,z,max=2){let best=null,d=max;for(const n of nodes){if(!n.valid)continue;const nd=Math.hypot(n.x-x,n.z-z);if(nd<d){best=n;d=nd;}}return best;}
export function findPath(from,to){
 const start=nearest(from.x,from.z,1.2),end=nearest(to.x,to.z,1.45);if(!start||!end)return [];
 const score=new Map([[start.id,0]]),parents=new Map(),open=new Set([start.id]),closed=new Set();
 while(open.size){let id=-1,best=Infinity;for(const k of open){const n=nodes[k],f=score.get(k)+Math.hypot(n.x-end.x,n.z-end.z);if(f<best){best=f;id=k;}}
 if(id===end.id){const path=[];for(let k=id;k!==undefined;k=parents.get(k)){const n=nodes[k];path.unshift({x:n.x,y:n.y,z:n.z});}return path;}
 open.delete(id);closed.add(id);const n=nodes[id];for(const m of neighbors(n)){if(closed.has(m.id))continue;const g=score.get(id)+Math.hypot(m.x-n.x,m.z-n.z);if(g<(score.get(m.id)??Infinity)){score.set(m.id,g);parents.set(m.id,id);open.add(m.id);}}
 }return [];
}
