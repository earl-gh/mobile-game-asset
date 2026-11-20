# Prop

Props fill the world, and on mobile they get placed by the hundred, so cost is per instance. A prop's job is to support the space around it, unless it's a **hero prop** (an objective, interactable, or loot cache) that should draw the eye.

## Budget

| Class | LOD0 | LOD1 (Low hero) | LOD2 | Texture |
|---|---|---|---|---|
| Small (hand-sized) | 150–600 tris | 50% | cull | shared atlas, 0.1–0.25 of a 1024 |
| Medium (about knee to waist height) | 600–2.5k | 50% | 20% | shared atlas or 512 |
| Hero / interactable | 2.5–6k | 50% | 25% | own 1024 |

- **Texel density:** match the environment (256–512 px/m), so props don't look sharper or blurrier than the floor they sit on. Hero props are allowed 1.5×.
- **Materials:** 1. Props share the kit's atlas or trim sheet whenever their materials match.

## Pipeline additions

1. **Classify** the prop as filler, dressing or hero. That decides whether it gets unique UVs or trim/atlas UVs.
2. **Size realism.** Measure against the 1.8 m character and 1 m cover height. Props that act as cover must be exactly cover height (gameplay metric, not art choice).
3. **Pivot.** Wherever the prop rests, hangs, mounts or hinges in use: the base center for floor-standing props, the contact point for wall-mounted ones, and the Part Inventory's axis for any moving part. Rotation zero, with the front facing −Y in Blender (it becomes +Z forward in Unity).
4. **Atlas packing for filler.**
   - Group 4–12 small props into one shared 1024 atlas, with UV shells laid out by prop and each prop's islands at equal texel density.
   - Unity draws them with one material, so the SRP Batcher and GPU instancing handle them cheaply.
5. **Hero prop treatment.**
   - Unique bake from a bevelled, subdivided bake source.
   - Emissive gameplay cues in the mask's emission or the albedo with a bloom-friendly accent.
   - Each moving part from the inventory is a separate child mesh with its own pivot, plus a `SOCKET_` empty wherever effects spawn.
6. **Ground contact.** Bake an AO plane under the prop's footprint into the albedo (contact darkening), or ship a 64 px blob shadow decal for Low quality.
7. **Variation without new meshes.** Make 2–3 color variants through palette swaps of the same UV layout (a different albedo, same mask and normal). For dressing props, also offer a damaged state that reuses the same mesh with one cut vertex group.

## LOD notes

- LOD1 removes chamfer segments (2 down to 1) and merges small parts.
- LOD2 turns the prop into a box-like hull plus the painted texture.
- Small props skip LOD2 and cull at 1.5–3% screen height.

## Pitfalls

- Don't use open alpha planes on filler props. On mobile, overdraw costs more than tris: model thin shapes as geometry.
- Colliders: one box or capsule per prop. A MeshCollider on a filler prop is a bug.
