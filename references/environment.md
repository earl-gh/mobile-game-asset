# Environment (modular kits)

Riot: environments take up most of the screen, so they must be "as cheap as possible", and players "mentally block out" the environment to focus on characters. A Valorant-style map is a clean, readable space: big flat planes, chamfered edges, color-coded sites, calm surfaces, lightmapped light. The environment **supports** the characters and never competes with them.

## Budget

| | LOD0 | LOD1 | LOD2 / Cull |
|---|---|---|---|
| Kit piece (wall, floor, trim) | 50–800 tris | 50% | cull < 1% screen |
| Large landmark | 3–8k | 50% | 25% or imposter |
| Visible frame total | High 250k · Med 180k · Low 100k | | |
| Batches | High ≤ 150 · Med ≤ 110 · Low ≤ 70 | | |

- **Textures:** one trim sheet (2048), 2–4 tileables (1024), one decal atlas (1024). 256 px/m on Low, 512 on High.
- **Materials:** ≤ 4–6 for the whole kit, VStyle/Lit Environment, lightmapped.

## Blockout (the space, before any piece)

1. **Metrics first, locked:**
   - grid 0.5 m
   - character 1.8 m, eye height 1.6 m
   - cover 1.0 m (crouch) and 1.5–1.6 m (standing)
   - doors 1.4–2.0 m wide
   - corridor ≥ 3 m
   - wall 3–4 m per floor, wall thickness 0.25–0.5 m
2. **Grey-box the described space** from kit-shaped boxes on the grid. Check it from player eye height:
   - sightlines
   - cover heights
   - the readable route
   - one clear landmark silhouette per area (tower, arch, statue) for orientation
3. **Kit list from the grey-box:** the smallest set of pieces that rebuilds it. Straight runs at 1/2/4 m, corner types, openings, floor tiles, transitions. Every piece shares edge profiles.
4. **Profiles:** each kit piece is designed as an extruded side profile (base, plinth, body, cap) with large chamfers (5–10 cm). That's the Valorant architecture read: thick, soft-cornered, chunky trims.
5. **Pivots** at the bottom-left-back corner on the grid.
6. **Value plan:**
   - Walls and floors in the mid-value, low-saturation band.
   - Site color-coding (A, B and C sites) as big calm zones, not small accents.
   - Interactive or traversable things get the accent.
   - Run `shape_review.py` on the assembled grey-box. The characters in front of it must pop.

## Pipeline additions

1. **Trim sheet first:** a 2048 plane of horizontal strips (chamfers, panel lines, plinths, caps), each baked from a high-poly strip. Snap kit UVs to the strips, letting U tile freely. Big flat faces use world-scale tileables.
2. **Calm surfaces:**
   - Tileables have large soft tonal shifts (≤ 8% value) and no grime noise in the play space.
   - Decals (signage, site markers, a little wear) are mesh decals 1 mm off the surface. Use them sparingly, and keep them away from character-height backgrounds where they'd break silhouettes.
3. **Vertex color R** blends tileable A and B, for broad variation. No AO in vertex color: the lightmap carries light.
4. **UV2 for lightmaps:** Lightmap Pack, margin 0.02, uniform scale. Static pieces are lightmapped, and their diffuse comes from the lightmap, not the ramp.
5. **Colliders:** box `_COL` per piece; ramp colliders on stairs.

## LOD notes

Small pieces skip LOD1 and go straight to cull. Landmarks get an imposter at LOD2.

## Pitfalls

- No T-junctions along shared edges.
- Don't scale pieces non-uniformly in-engine: make a new piece.
- Saturated, high-contrast or busy walls behind head height are the most common clarity bug.
