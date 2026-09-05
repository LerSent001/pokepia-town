# Third-Party Notices

The project-level MIT license applies only to project-authored code and assets. The following files retain their original licenses and intellectual-property restrictions.

## Pokémon 3D models

| Pokémon | Distributed file | Source file |
| --- | --- | --- |
| Ditto | `public/models/132.glb` | `models/opt/regular/132.glb` |
| Pikachu | `public/models/25.glb` | `models/opt/regular/25.glb` |
| Machop | `public/models/66.glb` | `models/opt/regular/66.glb` |
| Psyduck | `public/models/54.glb` | `models/opt/regular/54.glb` |
| Rayquaza | `public/models/384.glb` | `models/opt/regular/384.glb` |

- Source repository: https://github.com/Pokemon-3D-api/assets
- Pinned revision: `429de1288cea0d43f5b4f56305d2276e94239d65`
- Repository license: MIT, copyright 2024 Sudhanshu Ambastha. A copy is stored at `third_party/Pokemon-3D-api-assets-LICENSE.txt`.
- Exact pinned download URLs and SHA-256 values: `asset-sources.json`.
- Project modifications: skeleton-axis correction, pose correction, material tuning, Draco-compatible optimization, and authored `Town_Idle`, `Town_Walk`, or `Town_Fly` clips.

The upstream repository's MIT license covers the material published by that repository. It does not transfer ownership of Pokémon characters, names, designs, or trademarks. Those rights remain with Nintendo, Creatures Inc., GAME FREAK inc., The Pokémon Company, and their respective owners.

## Runtime libraries

| Component | Use | License | Source |
| --- | --- | --- | --- |
| Three.js r184 | WebGL rendering and loaders | MIT | https://github.com/mrdoob/three.js/tree/r184 |
| Three.js Water2 and normal maps | `src/water.js`, `public/textures/water-normal-*.jpg` | MIT | https://github.com/mrdoob/three.js/tree/r184/examples |
| Three.js GTAOPass | Ambient occlusion | MIT | https://github.com/mrdoob/three.js/blob/r184/examples/jsm/postprocessing/GTAOPass.js |
| Draco decoder | `public/draco/*` GLB mesh decompression runtime | Apache-2.0 | https://github.com/google/draco |
| Vite | Build and development server | MIT | https://github.com/vitejs/vite |
| Blender MCP | `tools/blender_mcp_addon.py` and Blender automation bridge | MIT | https://github.com/ahujasid/blender-mcp |

Dependency license texts installed through npm remain in their packages. The bundled Draco runtime is governed by its Apache-2.0 license.

## Pokopia logo and visual references

- `public/textures/pokopia-logo.png` comes from the [official Pokémon Pokopia website](https://pokopia.pokemon.com/en-us/). It is proprietary trademark artwork, is not licensed under MIT, and is included only to identify this non-commercial fan demonstration.
- User-supplied reference screenshots and published promotional artwork informed the authored scene and character proportions. The promotional image is not included in the public repository.

No affiliation, endorsement, or sponsorship is claimed. If a rights holder requests removal of a protected asset, open an issue or contact the maintainer through GitHub.
