# Environment (modular kits)

Environments aren't modeled; they are **assembled** from a kit. Valorant-style maps are clean, readable spaces: big flat planes, chamfered edges, color-coded zones, and sightlines kept free of clutter. On mobile, the real budget is draw calls and overdraw, not triangles.

## Budget

| | LOD0 | LOD1 | LOD2 / Cull |
|---|---|---|---|
| Kit piece (wall, floor, trim) | 50–800 tris | 50% | cull < 1% screen |
| Large landmark (tower, statue) | 3–8k | 50% | 25%, or an imposter |
| Visible frame total | High 250k · Med 180k · Low 100k tris | | |
| Batches (after SRP Batcher and instancing) | High ≤ 150 · Med ≤ 110 · Low ≤ 70 | | |

- **Textures:** shared, not per piece. Use one **trim sheet** (2048), 2–4 tileables (1024) and one decal atlas (1024). Texel density is **256 px/m on Low and 512 px/m on High** (one mip apart, handled by the Mipmap Limit Group).
- **Materials:** a kit should share at most 4–6 materials in total.

## Pipeline additions

1. **Grid and metrics first.**
   - Pick a grid (0.5 m is a common start) and derive the metrics (wall height, cover height, opening widths, wall thickness) from the game's character controller and the brief, then lock them.
   - Pivots go at the bottom-left-back corner, snapped to the grid, so the pieces tile with integer offsets.
2. **Kit list before modeling.** Derive the pieces from the brief's layout: the smallest set that builds the described space (straight runs at a few lengths, the corner and junction types it needs, the openings, the floor and the transitions it shows). Every piece shares edge profiles so the seams line up.
3. **Trim sheet workflow.** This is the studio way, and it differs from props.
   - **Model the trim sheet first.** Take a 2048 plane split into horizontal strips (bevels, panel lines, pipe strips, vents) and bake each strip from a high-poly strip onto that plane.
   - **UV the kit pieces onto the strips.** Snap the UV shells to the strip bounds, and allow U to tile freely past 0–1.
   - Large flat faces map to the tileables in world-scale UVs.
   - Result: one material covers dozens of pieces, with no unique bake per piece.
4. **Mesh decals.** For damage, grime and signage, use floating planes 1 mm off the surface, alpha-clip on the decal atlas, and as few as possible. They add detail without unique textures.
5. **Vertex color blending.** In R, blend tileable B over A (for example clean to dirty, or paint to bare). In G, AO from Blender's "Dirty Vertex Colors" with a corrected spread. Unity's shader reads the vertex colors.
6. **UV2 for lightmaps.** Author UV2 as a non-overlapping unwrap (Lightmap Pack with 0.02 margin), and give each piece a uniform scale relative to its size. Static pieces get lightmaps; dynamic objects use light probes.
7. **Gameplay readability check.**
   - Take a screenshot from player eye height (1.6 m).
   - Anything the player must read as interactive or traversable gets the accent color.
   - Background pieces lose contrast: lower saturation and flatter gradients.
8. **Occlusion and colliders.**
   - Large opaque blocking pieces become Unity occluder static.
   - Colliders are boxes per piece, made as `_COL` cubes in Blender and turned into BoxColliders.
   - Walkable stepped surfaces get a ramp collider, not individual steps.

## LOD notes

Small kit pieces usually skip LOD1 and go straight to cull. Large landmarks get a LOD2 imposter: a baked billboard or a cross of 2 quads.

## Pitfalls

- No T-junction vertices along shared edges, or seams flicker.
- Tileable UVs must stay world-scale even when you scale an instance. Don't scale kit pieces non-uniformly in-engine; make a new piece instead.
