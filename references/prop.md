# Prop

Props fill the world and are placed by the hundred, so their cost is per instance. A prop either supports the space (filler and dressing: calm, environment-valued) or calls for interaction (a **hero prop**: an objective, interactable or loot cache, accent-colored and emissive-cued).

## Budget

| Class | LOD0 | LOD1 | LOD2 | Texture |
|---|---|---|---|---|
| Small (hand-sized) | 150–600 | 50% | cull | shared atlas |
| Medium (knee to waist) | 600–2.5k | 50% | 20% | shared atlas or 512 |
| Hero / interactable | 2.5–6k | 50% | 25% | own 1024 |

- **Texel density** matches the environment (256–512 px/m). Hero props may use 1.5×.
- **Material:** 1, VStyle/Lit Prop (or Environment if lightmapped static).

## Blockout

1. **Gameplay size is exact.** Cover props are exactly cover height (1.0 or 1.5 m). Interactables sit at hand height (0.9–1.2 m for the interact point). Measure against the 1.8 m figure.
2. **One readable main mass:** a chamfered box, cylinder or extruded profile with the big 45° chamfers or facets that make it read as designed, not as a default primitive. Add 1–3 medium forms: lid, base or feet, handles or bands.
3. **The interaction is a shape, not just a color.** Latch, button, handle or screen is a medium form that steps out of the main mass (2–4 cm) and faces the player's approach side.
4. **Pivots:**
   - base center for floor props
   - contact point for wall props
   - the Inventory axis for moving parts (hinge line on the back edge for lids)

   Front faces −Y. Test every moving part through its full range in clay: no intersections, no gaps.
5. **Silhouette test from across the room** (10–20 m). A hero prop must be recognizable and distinguishable from filler props of a similar size.

## Pipeline additions

1. **Classify:** filler / dressing (atlas or trim UVs, environment value band) vs hero (unique bake, accent color, emissive cue in MAER G).
2. **Hero props:** every moving part is a separate child with its own pivot. `SOCKET_` empties wherever effects spawn.
3. **Ground contact:** no AO baked into the albedo. Contact darkening comes from the lightmap (static) or a 64 px blob decal (dynamic), on **every tier**, so a prop's visual footprint never differs between tiers.
4. **Variation:** palette swaps via MAER A tint zones, so no new albedos are needed.

## LOD notes

- LOD1 reduces chamfer segments from 2 to 1 and merges small parts.
- LOD2 is a hull plus the texture, still passing the silhouette IoU test.
- Small props cull at 1.5–3% screen height.

## Pitfalls

- No open alpha planes; model thin shapes.
- One primitive collider per prop. A MeshCollider on a filler prop is a bug.
