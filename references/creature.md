# Creature (non-humanoid)

Anatomy drives everything. The model reads as alive when its forms follow the skeleton and its silhouette exaggerates the species' defining trait (a bull's neck, a raptor's claw, a spider's leg span).

## Budget

| Size class | LOD0 | LOD1 (Low hero) | LOD2 | Bones |
|---|---|---|---|---|
| Small (critter, pet) | 2–4k | 1–2k | 500 | 15–30 |
| Medium (enemy, mount) | 7–11k | 3.5–5k | 1.5k | 35–60 |
| Boss | 16–24k | 8–12k | 4k | 60–90 |

- **Texture:** 1024 for small, 2048 for medium and boss creatures (texel density 400–700 px/m).
- **Materials:** 1 opaque material, plus 1 alpha-clip material if needed for fur or membrane cards. Use emissive eyes or weak points through the mask's emission. Put emission in the albedo alpha only if the project shader supports it; otherwise add a small 4th mask channel in a custom Shader Graph.

## Pipeline additions

1. **Skeleton first.** Build a stick skeleton from the reference: spine curve, limb lengths and joint angles. Measure leg segments from the image and confirm the digitigrade, plantigrade or unguligrade stance. Then block out volumes around the bones, because that keeps joints where the topology needs them.
2. **Bake source.**
   - Follow "Organic assets: build high, then retopo" in `SKILL.md`: Skin-modifier body with graded radii, a separate head volume, big anatomy (muscle masses, plates, protrusions from the brief) added as merged volumes rather than hand-sculpted strokes, then Remesh-merge.
   - Carry detail at three scales (`references/surface.md`): primary in the silhouette, secondary in the bevels and normal map, and fine surface pattern (scales, pores, wrinkles) built on the bake source and baked into the normal map, then echoed in the albedo masks. Hand-painting patterns into the albedo alone is what reads as childish.
   - Spend where the eye goes: about a third of the triangle budget on the head and extremities, since that's where a toy look shows first. Give the head a real jaw, brow and muzzle volume rather than a blobby tube.
3. **Topology.**
   - Use radial loops at every ball joint and 3 loops at each hinge, found from the skeleton you built.
   - Long tapering appendages need an even ring count of 6–10 sides, scaled down toward the tip.
   - Articulated openings (anything that opens and shows an interior): a separate loop set around the opening, and an interior cavity of about 200 tris, visible only when it opens.
4. **Secondary motion chains.** Every appendage the inventory marks as swaying or lagging gets a bone chain (3–8 bones) set up for Unity's `Animation Rigging` or a jiggle solver. Name the chains `<part>_01..`.
5. **Rig.**
   - Generic rig with the root at the ground under the center of mass, named `root`. Then `pelvis`, then the spine.
   - Add an IK target empty at each ground contact so Unity's Animation Rigging can plant the feet, named from the inventory.
   - Use ≤ 4 influences. Rigid parts (hard plates and protrusions) are 100% bound to one bone.
6. **Fur, feathers or similar (if the brief has them).** Use 1–3 shell layers of alpha-clip cards only along the silhouette, at most 150 cards. Elsewhere, paint the clumps into the albedo with an edge-highlight pass.
7. **LODs.**
   - LOD1: halve the ring counts on limbs and appendages, and close any articulated opening (drop its cavity).
   - LOD2: no alpha cards, and merge small digits or fine parts into their parent.
   - From LOD1 on, collapse the secondary chain weights to the parent bone, so fewer bones are evaluated.

## Pitfalls

- Study how each limb attaches to the torso in the reference. If the real anatomy has a floating girdle (like a shoulder blade), give it a sliding bone, or the limb pinches.
- Thin membranes or sheets: single-sided geometry needs a double-sided material. On mobile, model them as thin closed geometry instead, so you avoid a second shader variant.
