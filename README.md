# Mobile Game Asset — Valorant-style

A Claude skill that builds game-ready 3D assets in the **Valorant design language** for Unity URP (mobile or PC) by driving Blender.

## What it is

The skill turns a text description or concept image into one shippable asset that looks like it belongs in a stylized tactical hero shooter: big readable planar shapes, flat painted color, light that comes from the shader, and gameplay clarity on every quality tier.

It's built on one rule: **shape first.** Texture and shading only decorate a shape, so nothing gets UV'd, textured or shaded until a measured grey-clay blockout passes the Shape Gate.

The design language comes from Riot's [VALORANT Shaders and Gameplay Clarity](https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity). `references/valorant-style.md` marks every rule as either Riot's or the skill's own.

**Categories:** character, creature, environment kit, prop, weapon & equipment, vehicle. Each has a file in `references/`.

## How to use

1. Put this folder in your Claude skills directory.
2. Connect **Blender MCP** if you can. Without it, the skill writes the brief and one script per stage for you to run later.
3. Ask for an asset, or attach concept art:
   > "Enemy creature for my mobile hero shooter: lean wolf-like stalker, bony spine crest, club tail, glowing amber eyes. Charcoal, bone-white, orange glow."
4. Check the **Asset Brief**, then the **clay review sheet** after the blockout. Approve the shape before texturing starts.
5. In Unity, copy `unity/` into your project, then follow the material and import checklists in `references/shader.md` and `references/unity.md`.

## What it does and how

| # | Stage | How |
|---|---|---|
| 0 | **Source a free base** | Searches CC0 / CC-BY libraries (Poly Haven, Sketchfab, Quaternius, Kenney, MakeHuman…) for a base mesh instead of starting from a default primitive. Checks the licence, imports, normalizes and records provenance (`references/sourcing.md`, `import_base.py`). |
| 1 | **Brief** | Role and camera distance, size, silhouette keys at 30 m, big/medium/small ratio, palette as value bands, Part Inventory |
| 2 | **Blockout** (most of the effort) | Four measured passes: landmarks and scale figure → primary masses with gesture and taper → secondary forms and negative space → pivots, range tests and value plan (`references/blockout.md`) |
| 3 | **Shape pass** | Chamfer classes, planar faceting, cloth fold wedges, exaggerated function, no drift from the blockout |
| ■ | **Shape Gate** | Grey-clay sheet (`shape_review.py`) scored on a 10-item checklist. A failure goes back to the shape. |
| 4 | **Game mesh → normals → UV** | Budgeted topology, marked sharps plus Weighted Normal, UV only on the approved shape |
| 5 | **Bake** | Normal (chamfers and big forms; micro detail only in first person), contact AO, edge mask |
| 6 | **Color** | Flat material-color albedo with **no baked light**, MAER mask, diffuse ramps |
| 7 | **Readability** | Rendered at true gameplay pixel size with the target lighting model; contrast and fresnel tests |
| 8 | **LODs** | Same silhouette on every tier (IoU ≥ 0.95), so low-end players see what high-end players see |
| 9 | **Rig → export** | Deform-only skeleton, sockets, Unity FBX, validation |

### The light layer: `unity/`

| File | What it does |
|---|---|
| `VStyleLit.shader` | One URP shader for every category: ramp diffuse from one light, cubemap-only specular, clamped ambient, team fresnel, skin underglow, distance brightening, MAER decode. The Low tier drops instructions, not features. |
| `VStyleQuality.cs` | Switches the low shader tier from the Quality level |
| `VStyleCharacter.cs` | Sets the team fresnel color, the ambient clamp, and no cast shadows in third person |
| `VStyleAmbientZone.cs` | Sets the ambient clamp per map area |

The shader is written against the Unity 6 / URP 17 API but hasn't been compiled here. Check it in your project first.

### Scripts (`scripts/`)

| Script | Runs in | Purpose |
|---|---|---|
| `import_base.py` | Blender | Imports a free base (glTF/FBX/OBJ/.blend), refuses uncleared licences, re-faces to −Y, scales to the brief, puts the pivot at the ground, logs to `<Asset>_SOURCES.md` |
| `shape_review.py` | Blender | Clay sheet: ortho and 3/4 views, 10 m and 30 m silhouettes, value thumbnail, landmarks, IoU vs a previous version |
| `readability.py` | Blender | Target-shader preview at gameplay distances; contrast and LOD silhouette tests |
| `check_albedo.py` | Blender | Fails albedos with baked lighting, noise or out-of-range values |
| `gen_ramp.py` | any Python 3 | Diffuse and skin ramp textures (presets or custom stops) |
| `pack_mask.py` | Blender | MAER mask: R metallic, G AO / emissive, B roughness, A tint zone |
| `validate.py` | Blender | Tris per LOD, n-gons, non-manifold edges, texel density, weights, naming |
| `export_unity.py` | Blender | Unity FBX settings |

### Naming

| Pattern | Meaning |
|---|---|
| `SM_` / `SK_` | static / skinned mesh |
| `_LOD0..n` | LOD levels |
| `_COL` | collider |
| `SOCKET_<name>` | attach point |
| `T_<Asset>_A`, `_N`, `_MAER` | albedo, normal, mask |
| `T_<Asset>_RampDiffuse`, `_RampSkin` | diffuse ramps |
| `M_<Asset>` | VStyle/Lit material |

### Tests

`evals/` has four cases (character, creature, weapon, image-reference prop). Each has 20 graders, including base-model sourcing and licensing, blockout passes, the Shape Gate ordering, a light-free albedo, measured readability and tier parity.
