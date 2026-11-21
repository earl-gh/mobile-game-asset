---
name: mobile-game-asset
description: Build game-ready 3D assets in the Valorant design language (stylized realism, big readable planar shapes, flat painted color, shader-driven light, gameplay clarity) for Unity URP on mobile or PC, by driving Blender through Blender MCP from a text description or a reference image, starting from a licence-checked free base model (CC0 / CC-BY from Poly Haven, Sketchfab, Quaternius, Kenney, MakeHuman and similar) instead of default primitives when one fits. Puts a detailed, measured, verified blockout first, then the shape pass, game mesh, texturing to a flat albedo plus MAER mask, the bundled VStyle/Lit ramp shader, readability tests at gameplay distance, LODs that keep the silhouette, rig and FBX export. Covers characters, creatures, environment kits, props, weapons and equipment, and vehicles. Use it whenever the user wants to block out, model, retopo, texture, LOD, rig or export a 3D game asset, mentions Valorant, Riot, a stylized hero-shooter look, game-ready or low-poly models, Unity assets or Blender MCP, or hands over concept art to turn into a model.
---

# Valorant-style game asset (Blender MCP → Unity)

You drive Blender to make one shippable asset that looks like it belongs in a game like Valorant. The look comes from three places, and each has an owner:

| Layer | Owner | What it does |
|---|---|---|
| **Shape** | the mesh (stages 1–3) | Big confident planes, chamfered creases, exaggerated function. Most of the look, and nearly all of the readability. |
| **Color** | a flat albedo plus the MAER mask (stages 6–7) | Material color and value bands. **No light painted in.** |
| **Light** | the bundled `unity/VStyleLit.shader` | Ramp diffuse from one light, cubemap specular, clamped ambient, team fresnel, depth brightening |

Read `references/valorant-style.md` first. It holds the design language, sourced from Riot's own article, and the readability tests. Then read the category file. Every rule serves Riot's three pillars: **performance, competitive integrity and art**.

## Non-negotiables

1. **Shape first, always.** Texture and shading cannot rescue an ugly shape: they only decorate it. An ugly asset with a perfect texture is still an ugly asset. So most of the effort goes into the blockout and shape pass, judged in **grey clay with no color at all**, and nothing is UV'd, baked, textured or shaded until the **Shape Gate** passes. If the shape is wrong later, you go back to the shape. Never patch it in paint.
2. **The albedo carries no light:** no AO multiply, no top-down gradient, no painted form shadows. `scripts/check_albedo.py` must pass.
3. **No noise in third-person assets.** Micro-detail goes only in first-person or close-up normal maps.
4. **Quality tiers never change what a player can see.** LOD silhouettes match at gameplay distance (IoU ≥ 0.95), there are no character cast shadows in the play space, and tiers drop shader instructions, not features.
5. **Readability is measured.** `scripts/readability.py` must pass for characters, creatures and interactables, and it runs first on the blockout.
6. **Start from a free base, not a default primitive,** when one exists (`references/sourcing.md`): CC0 or CC-BY bases from Poly Haven, Sketchfab, Quaternius, Kenney, MakeHuman and similar, imported with `scripts/import_base.py`. Licence cleared and provenance recorded, never ripped game assets. A base is raw material: it still goes through the measured blockout and the Shape Gate.
7. **Be honest:** a code-built organic asset is a correct, clean base for an artist to finish. Say so in the brief.

## 0. Route

| Category | File |
|---|---|
| Character (humanoid, playable or NPC) | `references/character.md` |
| Creature (non-humanoid) | `references/creature.md` |
| Environment (modular kit, structures) | `references/environment.md` |
| Prop (static or simple-moving) | `references/prop.md` |
| Weapon & equipment (held, worn, deployable) | `references/weapon.md` |
| Vehicle | `references/vehicle.md` |

Pick by gameplay role, not by look: the same shape is a prop if it's set dressing, equipment if the player holds or wears it, and a vehicle if they ride it. Always also read `references/sourcing.md` (free base models), `references/blockout.md` (stage 1 in detail), `references/shader.md` (the light layer) and, before export, `references/unity.md`.

## Right-size the work

Stages are a ceiling, not a quota. The exception is the blockout: it is never skipped or merged.
- Small hard-surface props can merge shape pass, game mesh and normals into one script, and skip the unique bake (use the trim sheet or a palette strip).
- Hero, organic and close-view assets always get the bake.
- Use the fewest scripts that keep each step verifiable, with shared helpers in one module.
- Numbers in category files are starting budgets. Tune them to profiled devices, never by cutting LOD0. Low hardware is served by LOD1+, mip limits and the low shader tier.

## 1. Intake → Asset Brief

**From text:**
- Pull out the gameplay role (who sees it, from how far, how often) and the size in metres.
- Name the **silhouette keys**: the 2–3 shapes that must read at 30 m.
- Note the shape language (big/medium/small) and the palette as value bands (dominant / secondary / accent, with sRGB values).
- Build the Part Inventory.
- Fill gaps with assumptions that suit the genre and **state them**. Ask only when the category or role is ambiguous.

**From image:** read it in this order.
1. **Proportions**, measured in the image's most reliable known-size unit (heads, wheels, hands, doors). Write the ratios down.
2. **Shape hierarchy:** big (silhouette), medium (plates, panels, big folds), small (straps, fasteners). Small detail goes into the texture or the 1P normal map, never into third-person geometry.
3. **Material zones:** albedo hex, value band, roughness band, metal yes/no.
4. **Hidden sides:** state your assumption for the back and underside.
5. **Parts:** what's hinged, sliding, flexible, glowing or attachable.

**Asset Brief** (keep it this short, and show it before building):
```
Asset: <PREFIX>_<Name>   Category: <cat>   Role/camera: <e.g. 3P enemy at 5–40 m; 1P hero>
Size: <bbox m>   Pivot: <where, why>   Grid/metrics: <cover height, door width… if relevant>
Silhouette keys @30 m: <2–3 shapes>     Shape ratio: big <…> / medium <…> / small <…>
Budget (tris) LOD0 <n> | LOD1 <n> | LOD2 <n>    Texture <res> × <sets>   Materials <n>   Texel <px/m>
Palette (sRGB value): dominant <hex, v> 60% / secondary <hex, v> 30% / accent <hex, v> 10% / emissive <hex>
Shader: VStyle/Lit <category>, ramp <preset>, team fresnel <yes/no>
Base: <title, author, licence, URL — or "none: <why>">   Parts: <Part Inventory>   Bones: <n or none>
Assumptions: <list>   Quality honesty: <what is final, what is an artist base>
```

**Part Inventory.** List each part that **moves** (axis, pivot, range), **deforms** (bone chain or region), **attaches** (socket position and orientation), **changes appearance** (emissive, recolorable zone), or **opens/hides geometry** (what's visible when). Pivots, bones, sockets and hierarchy all come from this list, named `<function>_<position>`.

## 2. Pipeline

| # | Stage | Exit check (verify before moving on) |
|---|---|---|
| 0 | **Source a base** (`references/sourcing.md`): search free CC0 / CC-BY libraries (through the Blender MCP asset tools when available) for a base that fits the brief's proportions or mechanics; import it with `scripts/import_base.py` | Licence cleared for commercial use, provenance written to `<Asset>_SOURCES.md`, base scaled, facing −Y, pivot at ground · or a stated reason why no base fits (then block out from scratch) |
| 1 | **Blockout**, four passes, using the base as the guide or source for 1b, see `references/blockout.md`: **1a** proportion skeleton and scale card · **1b** primary masses · **1c** secondary forms and negative space · **1d** part and pivot hierarchy, then value-zone planning | Measured dimensions within ±3% of the brief · silhouette keys read in a black-silhouette render at 30 m · shape ratio matches the brief · every Inventory pivot placed and tested by rotating it · `scripts/shape_review.py` sheet reviewed against the reference · **the user has seen the sheet** |
| 2 | **Shape pass:** chamfer classes, planar faceting, fold wedges, functional exaggeration | Every visible edge has its class bevel width · no soft blobs on hard parts · silhouette IoU vs blockout ≥ 0.97 (no drift) |
| ■ | **SHAPE GATE**, grey clay only (`shape_review.py`): score every item of the gate checklist in `references/blockout.md` §6, with no color, texture or custom shader allowed in the review | Every item passes. One failure sends you back to stage 1 or 2. **Stages 3+ don't start until this passes**, and the user approves the clay sheet when they're in the loop. |
| 3 | **Game mesh:** quads plus intentional tris; loops only for silhouette or deformation | Within LOD0 budget · zero n-gons and non-manifold geometry · deformation loops per category |
| 4 | **Normals:** sharp edges at hard angles, Weighted Normal (Keep Sharp, Face Influence) | No smoothing gradients across flat faces in a matcap screenshot |
| 5 | **UV:** only now, on a shape that passed the gate. Seams on sharp edges and hidden borders, angle-based unwrap, straightened strips, consistent texel density, packed | Texel density within ±10% · 8 px padding at 2048, 4 px at 1024 |
| 6 | **Bake:** a detail source duplicated from the game mesh (bevel and supporting loops for hard surface; Subdivision only for organic forms). Normal (chamfers and big forms only; micro detail only on 1P), contact AO, convex-edge mask, ID | No ray misses or skew · no micro detail on 3P normals |
| 7 | **Color:** flat albedo per zone (see "Texture rules"), MAER pack, ramps from `gen_ramp.py` | `check_albedo.py` passes · zones separable in greyscale |
| 8 | **Shader preview and readability:** `readability.py` on the textured asset, VStyle/Lit set up per `references/shader.md` | All contrast and fresnel tests pass |
| 9 | **LODs:** remove loops, collapse hidden detail, keep the silhouette and UV seams | Each LOD within budget · `readability.py` silhouette IoU ≥ 0.95 at 10 m and 30 m |
| 10 | **Rig / sockets** (if the inventory needs them) | Deform-only skeleton, ≤ 4 weights per vertex, normalized · pose test screenshot |
| 11 | **Export:** `scripts/export_unity.py` | `scripts/validate.py` passes |

### Organic assets: build high, then retopo

For characters, creatures and anything fleshy, after the blockout:
1. **High-detail source.** Skin-modifier volumes on the blockout skeleton with graded radii, Subdivision 2, and the head as its own volume (cranium, face or muzzle, jaw, brow). Merge with voxel Remesh, then push the planes: flatten broad areas (thigh front, forearm, chest) into facets, and sharpen crease lines, so the organic form still reads as Valorant's planar stylization rather than a soft blob.
2. **Retopo** with `quadriflow_remesh` (under `temp_override`) to the LOD0 target, or Remesh plus planar Decimate, then fix the joint and face loops by hand-written edits.
3. **Smooth shading** with the baked normal map on organics. Hard shading only on hard parts.
4. **Never cut LOD0 for weak hardware.**

### What "studio, not default" means

- **Bevels:** a set width per size class (weapons 1 cm, props 2–4 cm, architecture 5–10 cm), `harden_normals=True`, `limit_method='WEIGHT'` from `bevel_weight_edge`, 1–2 segments on the game mesh.
- **Shading:** marked sharp edges plus Weighted Normal, applied before export. Not Auto Smooth.
- **Subdivision:** never on the game mesh, and only on organic bake sources.
- **UVs:** not Smart UV Project. Seams on sharps, Angle Based, Follow Active Quads on strips, `pack_islands(shape_method='CONCAVE', rotate=True, margin_method='FRACTION')`.
- **Reduction:** remove whole loops, dissolve planar faces (`limit=1°`). Collapse-decimate only organic parts, with symmetry and seams protected.

### Texture rules (stage 7)

The albedo is *material color*. The shader makes the light.
1. **Zone color** per material from the brief's value bands. Albedo stays in 0.06–0.85 sRGB.
2. **Material-explained variation only:**
   - dye or fabric panels
   - stitching lines
   - worn paint to bare metal on **convex edges only** (from the edge mask, 2–6 px wide, at most 15% lighter, never on cloth)
   - hair: a strand gradient inside each clump
   - skin: painted brows, lip line, slight warmth on cheek and nose
3. **Forbidden in the albedo:** AO, cavity darkening, top-down gradients, form shadows, grime, noise, photo texture. Contact AO goes to the MAER G channel at reduced strength (`AO_STRENGTH`). Large-scale shading is the ramp's job.
4. **Normal map:** chamfers, panel lines and big folds only. Skin gets no normal detail. Micro detail only on 1P assets.
5. **Roughness** in broad bands per material (see the surface vocabulary in `valorant-style.md`). Convex edges slightly glossier, so they catch the cubemap highlight.
6. **Pack** with `scripts/pack_mask.py` into `T_<Asset>_MAER`:
   - R metallic
   - G AO (< 0.5) / emissive (> 0.5)
   - B roughness
   - A tint-zone ID
7. **Ramps:** generate `T_<Asset>_RampDiffuse` (and `_RampSkin` for characters) with `scripts/gen_ramp.py`. Tune the core-shadow position and value per character, not per texture.

## 3. Driving Blender MCP

- **One stage or blockout pass per code call.** Use deterministic names, make every call idempotent, and print stats at the end (dimensions, tris, objects, UV islands).
- **Look after every pass:**
  - blockout and shape: `scripts/shape_review.py` (clay ortho views, 3/4 views, black silhouettes at 10 m and 30 m, a greyscale thumbnail)
  - textures: `readability.py`
  - Compare against the brief or reference image. Fix before moving on.
- **Prefer `bmesh` and the data API.** Wrap any needed operator in `bpy.context.temp_override(...)`.
- **Protect work:** after each stage, `save_as_mainfile(filepath=".../<Asset>_v###.blend", copy=True)`. Never overwrite the user's file without asking.
- **Run the bundled scripts** by sending their contents with the parameters at the top set.
- **No Blender MCP connected?** Write `<Asset>_brief.md` and one script per stage (`<Asset>_stage01a_skeleton.py`, …), each printing its own exit-check numbers, and say so.

## 4. Naming (Unity-ready)

| Pattern | Meaning |
|---|---|
| `SK_` / `SM_` | skinned / static mesh |
| `<Mesh>_LOD0..n` | LOD levels |
| `<Mesh>_COL` | collider |
| `SOCKET_<name>` | attach point |
| `T_<Asset>_A` | albedo (sRGB) |
| `T_<Asset>_N` | normal |
| `T_<Asset>_MAER` | mask (linear) |
| `T_<Asset>_RampDiffuse`, `T_<Asset>_RampSkin` | diffuse ramps (linear) |
| `M_<Asset>` | VStyle/Lit material |

Metres, +Y up and −Z forward after export. Pivot at the ground contact point or the gameplay pivot. Character skin mask: vertex color R (1 = skin).

## 5. Hand-off

End with:
- the Asset Brief as built, with real numbers
- `<Asset>_SOURCES.md`, with CC-BY credits listed for the game's credits screen
- the Shape Gate clay sheet and checklist scores (blockout and final)
- the `readability.py`, `check_albedo.py` and `validate.py` reports
- the export file list
- the VStyle/Lit material settings
- the Unity checklist from `references/unity.md`
- anything you skipped or assumed
