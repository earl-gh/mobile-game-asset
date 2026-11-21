# Unity 6+ (URP): tiers, export, import

Check the project's Unity version first (`ProjectSettings/ProjectVersion.txt`). Everything below targets Unity 6 LTS and URP 17.

## One asset, three tiers, one competitive picture

Author **one LOD chain, one texture set and one material**. Quality levels choose cost, never visibility (Riot: no tier difference "that could change the competitive landscape").

| Quality level | LOD Bias | Max LOD Level | Skin Weights | Texture Mipmap Limit | VStyle shader tier |
|---|---|---|---|---|---|
| High | 1.5 | 0 | 4 Bones | 0 | full |
| Medium | 1.0 | 0 | 4 Bones | 0 for Characters/Weapons, 1 for Environment/Props | full |
| Low | 0.8 | 0 | 2 Bones | 1 (2 for Environment) | `_VSTYLE_TIER_LOW` |

- **Max LOD Level stays 0 on every tier.** Forcing Low onto LOD1 would give low-end players different silhouettes at the same distance. LODs switch by screen size only, and every LOD must pass the `readability.py` silhouette test (IoU ≥ 0.95). This replaces the old "Low skips LOD0" rule.
- **Shadows:** no realtime shadows from characters or play-space dynamic objects on any tier. Environment shadows are baked into lightmaps. Only the local player's first-person hands and weapon may cast realtime shadows, and only onto themselves or nearby geometry. Configure each URP Asset with the main light shadows used only by the first-person layer, or turned off on Low for everyone. That's fine because no gameplay depends on them.
- **Mipmap Limit Groups:** one per category, assigned in each texture importer.
- **URP Asset per tier:** Low gets no HDR, MSAA off or 2×, render scale 0.8–0.9, and no post-processing beyond what gameplay needs.
- **Scene setup** for VStyle/Lit:
  - reflection probes (or a sky cubemap) with a hotspot painted toward the main light
  - light probes across play spaces (they feed the ambient clamp)
  - `VStyleAmbientZone` volumes in very dark or very bright areas
  - `VStyleQuality` in the boot scene

## Blender export (`scripts/export_unity.py`)

- `apply_scale_options='FBX_SCALE_ALL'`, `axis_forward='-Z'`, `axis_up='Y'`. `bake_space_transform=True` for static assets only (it can break armatures, so the script turns it off when the export contains one). On rigged imports that show a −90° X root, enable Bake Axis Conversion in the importer rather than rotating the asset in Blender.
- `use_mesh_modifiers=True`, `mesh_smooth_type='FACE'`, `use_tspace=True`: weighted normals and tangents that match the bake.
- `colors_type='LINEAR'`: the skin mask in vertex color R arrives exactly 0 or 1.
- `add_leaf_bones=False`, `use_armature_deform_only=True`, `bake_anim=False`. Animations go in separate `A_<Asset>_<Action>.fbx` files.
- `object_types` MESH, ARMATURE, EMPTY (`SOCKET_` empties ride along).
- **Before exporting:**
  - apply rotation and scale
  - Triangulate modifier last (Beauty) so Unity's triangles match the bake
  - at most 4 weights per vertex, normalized

## Unity import checklist

**Model tab:**
- Scale Factor 1, Convert Units on, Read/Write off.
- Mesh Compression: Medium for props and environment, Off for skinned and first-person meshes.
- Optimize Mesh Everything; Normals Import, Tangents Import.
- Static environment: Generate Lightmap UVs **off** if you authored UV2.

**Rig tab:** Humanoid only for retargetable humanoids, otherwise Generic with the Root node set. Optimize Game Objects on, exposing only socket bones.

**Animation tab:** Optimal compression, error thresholds 0.5 / 0.5 / 0.5.

**Materials:** one `M_<Asset>` using `VStyle/Lit`, following `references/shader.md`. GPU Instancing on for props and environment.

**Textures:**

| Texture | sRGB | Format (Android / iOS) | Notes |
|---|---|---|---|
| `T_*_A` albedo | on | ASTC 6×6 | |
| `T_*_N` normal | off | ASTC 5×5 hero, 6×6 otherwise | Type Normal map |
| `T_*_MAER` | off | ASTC 6×6 | Check that the G channel's AO/emissive split survives compression. If emissive edges band, use 5×5. |
| Ramps | off | uncompressed RGB24 | Clamp, no mips |

Max size = authored size. Mipmaps on (except ramps), with the Mipmap Limit Group set.

**Hierarchy:** `_LOD0..n` siblings become a LODGroup. Use the category file's transition heights, Fade Mode None.

**Renderers:** characters get `VStyleCharacter` (team, first-person flag, Cast Shadows managed). Environment pieces: Cast Shadows Off at runtime, Contribute GI on, Static.

**Colliders:** primitive colliders first. A convex MeshCollider on `_COL` only when primitives can't fit; disable its renderer.

## Verify in engine

A test scene with an ally and an enemy copy at 10 m and 30 m, in a dark and a bright zone. Screenshot on High and Low. The silhouettes, fresnel and emissive cues must match between tiers. Record the shader instruction counts per tier.
