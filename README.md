# Mobile Game Asset

A Claude skill that builds game-ready 3D models for Unity mobile games by driving Blender. Assets are stylized, with big readable shapes, crisp chamfers and painted color.

## What it is

The skill turns a text description or a reference image into one shippable asset for **Unity 6+ (URP, mobile)**. It works like a lead artist on a budget: every polygon, UV island and texture channel has a job.

It covers six categories, each with its own rules in `references/`:

| Category | File |
|---|---|
| Character (humanoid) | `character.md` |
| Creature (non-humanoid) | `creature.md` |
| Environment (modular kits) | `environment.md` |
| Prop | `prop.md` |
| Weapon & equipment | `weapon.md` |
| Vehicle | `vehicle.md` |

## How to use

1. Install the skill: put this folder in your Claude skills directory.
2. Connect **Blender MCP** if you can. Without it, the skill writes the brief and one Python script per stage for you to run in Blender later.
3. Ask for an asset in plain words, or attach concept art:
   > "Build a compact SMG for my mobile shooter: boxy receiver, vented shroud, folding stock. Off-white, dark grey, orange accent."
4. Review the **Asset Brief** it shows before building, and correct any assumptions.
5. Import the exported FBX and textures into Unity using the checklist at the end of the run.

## What it does and how

**1. Brief.** It reads the request or image and writes a short brief:
- size, pivot and triangle budgets per LOD
- texture size and texel density
- palette
- a **Part Inventory** listing what moves, deforms, attaches, glows or opens

**2. Pipeline.** It runs these stages, skipping any that a small asset doesn't need:

| Stage | How |
|---|---|
| Blockout → shape pass | Real-world scale and weighted bevels. Organic forms are built high-detail with the Skin modifier, then retopologized. |
| Game mesh → normals | Hits the LOD0 budget with marked sharp edges and a Weighted Normal modifier. No auto smooth, no subdivision on the game mesh. |
| UV | Seams on sharp edges, angle-based unwrap, consistent texel density, packed with padding |
| Bake | Normal, AO and edge mask from a detail source mesh (Cycles, Selected to Active) |
| Texture | Stylized node stack (zone colors, gradient, AO, edge highlight, roughness bands) plus `surface.md` layering, baked to albedo / normal / mask |
| LODs | Edge loops removed by hand, never a blind decimate. The silhouette and UV seams are kept. |
| Rig / sockets | Deform-only skeleton, at most 4 weights per vertex, `SOCKET_` empties taken from the Part Inventory |
| Export | `scripts/export_unity.py`, checked with `scripts/validate.py` |

**3. Unity tiers.** One LOD chain and one texture set serve the Low, Medium and High quality settings, through LOD Bias, Maximum LOD Level and Mipmap Limit Groups (`references/unity.md`).

**4. Hand-off.** The finished asset comes with:
- the as-built brief
- the validation report (tris, materials, texel density, bones)
- the list of exported files
- the Unity import checklist
- a list of what was skipped

### Bundled scripts

| Script | Purpose |
|---|---|
| `validate.py` | Checks tris per LOD, n-gons, non-manifold edges, texel density, materials, weights and naming |
| `pack_mask.py` | Packs the mask texture: R metallic, G AO, B zone ID, A smoothness |
| `export_unity.py` | Exports FBX with Unity axis and scale settings |

### Naming

`SM_` / `SK_` meshes · `_LOD0..n` · `_COL` colliders · `SOCKET_<name>` · `T_<Asset>_A|N|M` · `M_<Asset>`

### Tests

`evals/` holds four test cases: a character, a creature, a weapon, and an image-reference prop. Each case has a prompt and graders.
