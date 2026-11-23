---
name: mobile-game-asset
description: Build game-ready 3D models for Unity mobile games in a stylized, Valorant-level-of-detail look by driving Blender through Blender MCP, from either a text description or a reference image. Covers characters, creatures, environment kits, props, weapons and equipment, and vehicles, each with its own studio pipeline (blockout → topology → UV → bake → stylized texture → LODs → rig → FBX → Unity URP import) and Low/Medium/High quality tiers. Use this skill whenever the user wants to model, build, block out, retopo, texture, optimize, LOD, rig or export a 3D game asset, mentions Blender MCP, game-ready meshes, low-poly mobile models, Unity assets or a "Valorant style" look, or hands over concept art or a photo to turn into a 3D model, even if they never say "game-ready".
---

# Mobile Game Asset (Blender MCP → Unity)

You drive Blender through Blender MCP to make one shippable asset. The target is a stylized, Valorant-level-of-detail look: big readable shapes, crisp chamfers, painted albedo, no noise. It ships to Unity 6+ with URP on mobile, and it scales across the game's Low/Medium/High settings.

Work like a lead artist on a budget. Every polygon, UV island and texture channel has a job. Anything without one gets cut.

## 0. Route

1. **Pick the category**, then read its file. The category decides budgets, topology, rig and export rules:

| Category | File |
|---|---|
| Character (humanoid, playable or NPC) | `references/character.md` |
| Creature (non-humanoid, animal, monster) | `references/creature.md` |
| Environment (modular kit, structures, terrain pieces) | `references/environment.md` |
| Prop (static or simple-moving world objects) | `references/prop.md` |
| Weapon & equipment (held, worn, deployable) | `references/weapon.md` |
| Vehicle (wheeled, tracked, hover, flying) | `references/vehicle.md` |

   Pick by gameplay role, not by look: the same shape is a prop if it's set dressing, a weapon or equipment if the player holds or wears it, and a vehicle if the player rides or drives it.

2. **Read `references/unity.md`** before the export stage. It covers the quality-tier mapping and import settings.

## Right-size the work (ponytail principle)

The stages in section 2 are a ceiling, not a quota. Test runs spent about 1,100 lines of script on a 200-triangle box, and that is a failure: it buries the one decision that mattered. Scale the pipeline to the asset:

- A stage whose exit check is already met is skipped or merged into its neighbour, and the brief's "Skipped" line says so. Typical merges for small hard-surface assets: shape pass + game mesh + normals in one script, and no bake at all when the detail is texture-only (use a trim sheet, atlas or palette strip instead of a unique bake). Hero, organic and close-view assets are never texture-only: they always get the detail bake, because skipping it is what makes them look flat and toy-like.
- Aim for the fewest scripts that keep each step verifiable. Share helpers in one module instead of re-deriving them per stage.
- Never skipped: scale and pivot, normals and UV sanity, `scripts/validate.py`, export.
- Numbers in the category files (tris, texel density, bones, batches) are starting budgets, not specs. Tune them to the project's profiled devices and note what you changed, but never by cutting LOD0 for low-end phones: the quality tiers (LOD1/LOD2, mip limit) serve those, and LOD0 serves the High setting. Choose the texture size first and let the asset's unique surface area decide the px/m, keeping it consistent across the asset. Consistency matters more than hitting a prescribed figure.

## 1. Intake → Asset Brief

Start from either input. The output is the same: a short **Asset Brief**. Show it before building.

**From text:** pull out the role (who sees it, from how far, how often), size in meters, silhouette keywords, a material list, a palette of 3–5 colors with one accent, and the Part Inventory. Fill gaps with assumptions that suit the genre and **state them**. Ask only when the category or gameplay role is ambiguous, because that changes everything downstream.

**From image:** read it in this order:
1. **Proportions.** Measure in units the image gives you (the most reliable repeated or known-size element in the picture: heads, wheels, hands, doors). Write the ratios down.
2. **Shape hierarchy.** Primary forms (the silhouette), secondary forms (panels, armor plates, big folds), tertiary forms (bolts, seams, stitching). Tertiary detail goes into the texture, not geometry.
3. **Material zones.** Each zone gets a base color hex, roughness band (matte/satin/gloss) and metal yes/no.
4. **Hidden sides.** State what you assume about the back and underside.
5. **Parts.** Read the picture for the Part Inventory: what looks hinged, sliding, flexible, glowing, or attachable.
6. In Blender, load the image as a reference empty (`empty_display_type='IMAGE'`) aligned to the matching ortho view. Compare viewport screenshots against it at the end of each stage.

**Asset Brief template** (keep it this short):
```
Asset: <PREFIX>_<Name>   Category: <cat>   Role/camera: <e.g. 1P hero, 3P at 5–30 m>
Size: <bbox in m>   Pivot: <where and why>
Budget (tris)  LOD0 <n> | LOD1 <n> | LOD2 <n>      Texture: <res> × <sets>   Materials: <n>
Texel density: <px/m>   Bones: <n or none>
Shapes: primary <...> / secondary <...> / tertiary→texture <...>
Parts: <the Part Inventory below>
Palette: <hex list, accent marked>   Assumptions: <list>
```

**Part Inventory.** Everything object-specific comes from here. The category files give rules, never part lists, so derive the parts from *this* description or image and nothing else. List each part that needs one of these:
- **Moves** (hinges, slides, spins, swings): the axis, the pivot position and the range.
- **Deforms** (bends, stretches, sways): its bone chain or deform region.
- **Attaches** (something is held by it, mounted on it, or spawns from it): the socket position and orientation.
- **Changes appearance** (emissive, recolorable, damage-swappable): the material zone.
- **Opens or hides geometry** (cavities and interiors seen only in use): what is visible when.

Parts that need none of these are plain mesh. The pivots, bones, sockets and hierarchy you build in later stages come straight from this list, named `<function>_<position>` in plain words that match the brief.

## 2. Pipeline

Each category file adds its own stages and overrides. The skeleton below is the same for every category.

| # | Stage | Exit check (verify before moving on) |
|---|---|---|
| 1 | **Blockout.** Primary forms only, at real-world scale (1 BU = 1 m), with the pivot placed. | The silhouette reads at game-camera distance in a screenshot. Size matches the brief. |
| 2 | **Shape pass.** Secondary forms, then chamfers. | Every edge you can see has a deliberate bevel width. No noise. |
| 3 | **Game mesh.** The final low poly: quads plus intentional tris, supporting loops only where they serve the silhouette or deformation. | Tri count within the LOD0 budget. Zero n-gons and non-manifold geometry. |
| 4 | **Normals.** Mark sharp edges at hard angles, add a Weighted Normal modifier (Keep Sharp), and split UVs on every sharp edge. | No smoothing gradients across flat faces in a matcap screenshot. |
| 5 | **UV.** Seams on sharp edges and hidden borders, unwrap, straighten rectilinear shells, keep texel density consistent, pack (see below). | Texel density within ±10% of target. 8 px padding at 2048, 4 px at 1024. |
| 6 | **Bake.** Duplicate the game mesh as the bake source and add the detail the game mesh lacks (bevels, cuts; Subdivision only for organic forms), then use Cycles' "Selected to Active" with a cage. Bake normal and AO, plus an edge mask (see the texture recipe). | No ray misses or skew in the screenshot. |
| 7 | **Texture.** A layered surface driven by the baked maps (`references/surface.md`); the recipe below is only the floor. Pack the mask texture. | Reads at 25% scale, holds up on a grey card, and shows tonal variation at game distance. |
| 8 | **LODs.** Author them by removing loops and collapsing hidden detail. Each LOD keeps the silhouette and UV seams. | Each LOD within budget. No UV breaks. Visible LOD pops are small. |
| 9 | **Rig / sockets** (if needed). | Deform-only skeleton, ≤ 4 weights per vertex, normalized. |
| 10 | **Export.** Run `scripts/export_unity.py`. | `scripts/validate.py` passes. |

### Organic assets: build high, then retopo (characters, creatures, anything fleshy)

Studios don't model the game mesh directly for organic forms, and neither should you. The earlier "child-made" results came from skipping this:

1. **High-detail source first.** Smooth base volumes: a Skin modifier on the proportion skeleton with graded radii (heavy at shoulder and hip, tapering at the extremities), Subdivision 2, shade smooth. Model the head as its own volume (cranium, muzzle or face, jaw, brow, and ears or equivalents the brief calls for), not as a tapered tube. Merge the volumes (Remesh modifier, voxel mode), then add the three-scale detail from `references/surface.md`. Constant-radius tubes along splines with flat shading are the main toy tell: don't use them for bodies.
2. **Retopo to the game mesh.** Use `bpy.ops.object.quadriflow_remesh` (under a `temp_override` for a 3D view) to the LOD0 face target, or fall back to the Remesh modifier followed by planar Decimate. Then correct the loops at joints and the head by hand-written edits. The high-detail source stays as the bake source.
3. **Smooth shading** with the baked normal map for organic assets; flat or hard shading is for hard-surface parts only.
4. **LOD0 is not reduced for weak hardware.** "Runs on low-end phones" is met by the tier system (LOD1 and LOD2, texture mip limit, skin weights), never by cutting LOD0 below the category budget. An earlier run cut LOD0 to a third of budget and looked toy-like because of it.
5. **Beauty pass before hand-off.** Render the hero views with the real material in Cycles (CPU is fine) or EEVEE, since Workbench hides normal maps and gloss, then check for the toy tells: constant-width limbs, a tube head with no jaw or brow, flat or uniform colour, hard facets on organic skin, parts that float or don't connect. Fix and re-render at least three times, spending the effort on the head and extremities.

**Lessons from tested runs** (each one cost a debugging pass):
- **Remesh density.** Quadriflow-style remeshers are uniform. To give the head or thin limbs more quads, warp those regions up before the remesh and back afterwards; without it thin parts collapse. Make the source manifold first and check it in code, because one non-manifold edge cancels the remesh with no useful message.
- **UV patches.** Label faces, not vertices, when splitting into patches, or faces straddling two labels stitch the patches back into one huge island. Coverage depends more on island count and padding than on packer settings: fewer, compact patches with single seams on thin parts beat many small ones. Measure coverage as unique pixels, since summed UV area counts overlaps as efficiency.
- **Texel target.** Decide it before packing from texture size, surface area and a planned utilisation, and write it into the brief. Reading it back from the result makes the validate check meaningless.
- **Region masks.** Define anatomical region masks once with smooth transitions and reuse them for geometry displacement and in the shader. Don't let edge, curvature or AO maps drive colour or gloss on smooth regions: they posterise into blotches.
- **Form checks.** Toes point away from the heel: a backward foot reads as a hoof blob however good the leg is. Orient thin flat parts so their width faces the important view axis. Bury the roots of attached parts in the underlying form, add a boss, and taper plates into the surface so they read as grown, not stuck on.
- **Debugging renders.** When a render looks wrong, swap one input at a time: stale bakes, leftover scaffold objects and bad lighting all pass for texture problems. Delete scaffolding (retopo targets and sources) once the game mesh exists, and re-run bakes after any geometry change.

### What "not generic" means here

The default tools produce amateur results when you use them as-is. Use the studio version instead:

- **UVs.** Not Smart UV Project. Mark seams on sharp edges and hidden borders, unwrap with Angle Based, run Follow Active Quads on rectilinear strips, then pack with `bpy.ops.uv.pack_islands(shape_method='CONCAVE', rotate=True, margin_method='FRACTION', margin=padding_px/texture_px)`. Give hero-visible faces more texel density only when the brief says so. Mirror or overlap shells only for symmetric parts and never on tiling surfaces, and offset the overlapping copy by +1 U during the bake.
- **Reduction.** Not a blind Decimate. Remove whole edge loops, merge hidden faces and dissolve planar faces (`limit=1°`). Use Decimate (collapse) only on organic parts, with `use_symmetry` and the UV seams protected by vertex group weighting.
- **Bevels.** Not a Bevel modifier with default settings. Use a set width per size class (for example 1 cm on weapons, 2–4 cm on props, 5–10 cm on architecture), `harden_normals=True`, `limit_method='WEIGHT'` driven by `bevel_weight_edge`, and 1–2 segments on the game mesh.
- **Shading.** Not Auto Smooth. Mark sharp edges deliberately, add a Weighted Normal modifier (Keep Sharp, Face Influence), and apply it before export.
- **Subdivision.** Never on the game mesh. On a bake source use it only for organic forms: it rounds flat hard-surface faces, so hard-surface bake sources get bevels with supporting loops instead.
- **Texturing.** Not a stock Principled BSDF with a color picker. Build the procedural stylized node stack and bake it into the texture sets (stage 7).

### Stylized texture recipe (stage 7)

This is the floor, not the finish. Flat zones, one gradient and soft AO on their own read as a toy, so for any organic, hero or close-view asset layer `references/surface.md` on top. Build the base as one material in Blender, then bake it down to images:

1. **Zone colors.** Flat base color per material zone. Drive the zones with vertex color or a baked ID map. Keep values mid-range, with no pure black or white.
2. **Gradient.** Object-space Z, multiplied: about 0.85 at the bottom up to 1.05 at the top. This gives a "painted light from above" feel.
3. **AO.** The baked AO, multiplied at 30–50% strength. That's enough to ground the forms without looking dirty.
4. **Edge highlight.** Blender has no curvature bake, so make the convex-edge mask one of two ways: an Emission bake of Geometry → Pointiness on the bake source (needs enough geometry density along the bevels), or derive it from the baked normal map. Run the mask through a ColorRamp at 0.55–0.6 and use it to lighten the albedo by 10–20%. This gives the crisp painted-chamfer look.
5. **Roughness.** In broad bands per zone (matte 0.8, satin 0.5, gloss 0.25), with edges slightly glossier.
6. **Bake** to albedo (Emission bake of the color stack, so lighting doesn't leak in), normal (tangent, OpenGL Y+ matches Unity), and the mask texture.
7. **Pack** with `scripts/pack_mask.py`: R = metallic, G = AO, A = smoothness. That's one texture assigned to both the URP Lit *Metallic* and *Occlusion* slots, which saves a texture fetch and some memory.

## 3. Driving Blender MCP

- **One stage per code call.** Name objects, materials and images deterministically, and make each call idempotent: delete or replace what already exists, don't duplicate it. Print stats at the end of each call (tris, objects, materials, UV islands) so you can verify without guessing.
- **Look after every stage.** Take a viewport screenshot (a matcap for shape stages, material preview for textures) and compare it to the brief or reference. Fix the problem before moving on, because errors compound downstream.
- **Prefer `bmesh` and the data API over `bpy.ops`.** Operators fail without the right context over MCP. When you need one, wrap it in `with bpy.context.temp_override(...)`.
- **Protect work.** After each stage, save a new version: `bpy.ops.wm.save_as_mainfile(filepath=".../<Asset>_v###.blend", copy=True)`. Never overwrite the user's open file without asking.
- **Run the bundled scripts** by reading the file and sending its contents to the code-execution tool, with parameters set at the top.
- **No Blender MCP connected?** Write the brief to `<Asset>_brief.md` and one script per stage (`<Asset>_stage01_blockout.py` and so on) so the user can run them later. Say so.

## 4. Naming (Unity-ready)

`SK_` skinned mesh · `SM_` static mesh · `T_<Asset>_A|N|M` (albedo, normal, mask) · `M_<Asset>` · `<Mesh>_LOD0..n` (Unity builds the LODGroup from these suffixes) · `<Mesh>_COL` collider · `SOCKET_<name>` empties for attach points (names come from the Part Inventory). Units in meters, +Y up and -Z forward after export. Asset pivot at the ground contact point or the gameplay pivot.

## 5. Hand-off

End with:
- the Asset Brief (as built, with real numbers)
- the `validate.py` report (tris per LOD, materials, texel density, bones and influences, issues found)
- the export file list
- the Unity import checklist from `references/unity.md`
- anything you skipped, plus any assumption the user should confirm
