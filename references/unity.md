# Unity 6+ (URP, mobile): tiers, export, import

Check the project's Unity version first (`ProjectSettings/ProjectVersion.txt`) and use the newest settings it supports. Everything below works on Unity 6 LTS and later.

## One asset, three tiers

Don't author three versions of the asset. Author **one LOD chain and one full-resolution texture set**, then let the Quality levels pick what to use:

| Quality level | LOD Bias | Maximum LOD Level | Skin Weights | Texture Mipmap Limit (per group) |
|---|---|---|---|---|
| High | 1.5 | 0 | 4 Bones | 0 (full res) |
| Medium | 1.0 | 0 | 4 Bones | 0 for Characters/Weapons, 1 for Environment/Props |
| Low | 0.6 | 1 (LOD0 never renders) | 2 Bones | 1 (half res); 2 for Environment |

- Assets with no LODs (for example a first-person view model) ignore Maximum LOD Level, so their Low tier comes only from the texture mip limit and skin weights. Budget them for Low directly.
- **Mipmap Limit Groups** (Project Settings → Quality) let one texture drop resolution per tier. Assign each texture to a group named after its category in the texture importer.
- With Maximum LOD Level = 1, **the LOD1 budget is the Low tier's hero budget.** Budget LOD1 with that in mind.
- Give each Quality level its own URP Asset. On Low: no HDR, MSAA off or 2x, shadows from one cascade with soft shadows off, render scale 0.8.

## Blender export (`scripts/export_unity.py`)

The FBX settings it applies, and why:
- `apply_scale_options='FBX_SCALE_ALL'` + `axis_forward='-Z'`, `axis_up='Y'`, and `bake_space_transform=True` **for static assets only**: the option is experimental and can break armatures and animation, so the script turns it off when the export contains an armature. Check the import: scale 1 and rotation 0 on the root. On a rigged asset that shows a −90° X root rotation, turn on the model importer's Bake Axis Conversion option if your Unity version has it, rather than rotating the asset in Blender.
- `use_mesh_modifiers=True`, `mesh_smooth_type='FACE'`, `use_tspace=True`. Bakes the weighted normals and exports tangents that match the bake.
- `add_leaf_bones=False`, `use_armature_deform_only=True`, `bake_anim=False`. A clean skeleton. Animations go in separate FBX files (`A_<Asset>_<Action>.fbx`).
- `object_types` limited to MESH, ARMATURE and EMPTY (empties carry the `SOCKET_` attach points).

**Before exporting:** apply rotation and scale on all meshes, triangulate (Triangulate modifier, Beauty, kept last in the stack) so Unity's triangulation matches the bake, and limit to 4 weights per vertex, normalized.

## Unity import checklist

**Model tab:**
- Scale Factor 1, Convert Units on.
- Read/Write off, unless gameplay reads the mesh.
- Mesh Compression Medium for props and environment pieces, Off for skinned meshes and 1P weapons (compression warps close-up shading).
- Optimize Mesh: Everything.
- Normals: Import. Tangents: Import. This keeps the baked tangent space.
- Static environment pieces: Generate Lightmap UVs **off** if you authored UV2, on otherwise.

**Rig tab:**
- Humanoid only for retargetable humanoid characters. Everything else uses Generic, with the Root node set.
- Optimize Game Objects on, exposing only the socket bones.

**Animation tab:** compression Optimal, with error thresholds 0.5 / 0.5 / 0.5.

**Materials:** Extract or remap to project materials. Use the URP Lit shader, or the project's own stylized Shader Graph if it has one.
- `T_*_A` → Base Map.
- `T_*_N` → Normal Map. Set the texture type to Normal map.
- `T_*_M` → **both** the Metallic Map and Occlusion Map slots, with Smoothness Source set to Metallic Alpha.
- Turn on GPU Instancing for props and environment. Turn on Receive Shadows only where it shows.

**Textures:**
- Android and iOS overrides use ASTC. Albedo and mask at 6×6, normal at 5×5 on hero assets and 6×6 otherwise.
- Set the max size to the authored size.
- Generate Mipmaps on, with the Mipmap Limit Group assigned. Mask and normal textures must have **sRGB off**.

**Hierarchy:** Unity turns `_LOD0.._LODn` siblings into a LODGroup. Set the screen-relative transition heights from the category file, and set Fade Mode to None on mobile.

**Colliders:** Prefer primitive colliders (box, capsule, sphere). Use a convex MeshCollider on the `_COL` mesh only when primitives can't fit the shape, and disable that object's renderer.
