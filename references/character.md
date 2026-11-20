# Character (humanoid)

These are the gameplay-readable heroes. In a Valorant-style game, a player is identified from 30 m by silhouette and color blocking, so detail lives in shape and paint, not polygons.

## Budget

| | LOD0 (High/Med) | LOD1 (Low hero) | LOD2 | Cull |
|---|---|---|---|---|
| Playable hero | 14–18k tris | 7–9k | 3–4k | < 2% screen |
| NPC / enemy | 8–12k | 4–6k | 1.5–2.5k | < 2% |
| 1P arms (separate asset) | 6–9k | none (1P never LODs) | | |

- **Texture:** one 2048 set for body and head (texel density about 700 px/m, with the face shells at 1.5×). Add a separate 512 hair or alpha card set only if cards are needed.
- **Materials:** at most 2 (opaque, plus alpha-clip hair). **Bones:** 50–65 body, plus at most 12 face bones or 8–15 blendshapes (not both).
- **LOD transition heights:** 0.45 / 0.2 / 0.02.

## Pipeline additions

Build the body and head by "Organic assets: build high, then retopo" in `SKILL.md` before the steps below. Rigid worn pieces stay hard-surface.

1. **Proportion sheet first.** A stylized hero is 7–7.5 heads tall (realistic is 8): heroic shoulders, readable hands about 10% oversized, feet planted wide. Block the body out from an edge skeleton with a Skin modifier (a radius per joint) plus Subdivision 1–2, since stacked primitives read as a mannequin, and keep primitives for rigid worn pieces. Pose it in an **A-pose with arms at 45°**. Unity Humanoid handles A-pose, and the shoulder deforms better than in a T-pose.
2. **Costume over a body.** Model what the brief shows as the surface. Never model a full body underneath clothing, since hidden faces are wasted budget. Delete everything that's covered. Rigid worn pieces are separate floating meshes in the bake source and merged into the game mesh where they don't deform.
3. **Deformation topology:**
   - 3 loops around each joint (elbow, knee, finger knuckles), with the middle loop on the pivot.
   - The shoulder needs a loop running from the armpit across the deltoid.
   - The hip needs a diagonal loop from the crotch to the iliac crest.
   - Use evenly spaced quads on the limbs. Triangles go only in flat, non-deforming areas.
   - Face: mouth and eye loops for stylized expressions.
   - Cloth or accessories that hang and move (from the inventory) get their own bone chain rather than deform topology.
4. **Hair or head coverings (if the brief has any).** Solid sculpted clumps (Valorant style). This means opaque geometry with a painted strand gradient, not alpha cards, because alpha overdraw is expensive on mobile. Use alpha-clip cards only for wisps at the edges.
5. **Texture emphasis.**
   - Color-block the silhouette: primary color 60%, secondary 30%, accent 10%. Put the accent on a gameplay-readable spot that the brief's palette points to.
   - Paint forms into the albedo: a soft core shadow under the chin, under the brow and in the clothing folds.
   - The normal map carries only the chamfers and big fold forms. Skin stays without normal detail, for a clean read.
   - Faces: painted eyebrows and lip line, with eyes as separate mesh-plus-texture so gaze bones can move them.
6. **Skeleton.** Build a clean game skeleton directly with code. If the character will use Unity's Humanoid rig, name the standard bones with the exact names Unity's avatar mapper expects (Unity's HumanBodyBones set). Every bone is a deform bone. Roll the bones so +Y runs down the bone, consistently on both sides.
   - Add everything else as non-humanoid children, taken from the inventory: twist bones where limbs twist badly, sockets for carried or worn items, and chains for cloth or accessories.
   - Don't export a Rigify control rig. Build one only if the user animates in Blender, and constrain it to this skeleton.
7. **Skinning.** Bind with automatic weights, then fix the weights in code:
   - Use `vertex_group_limit_total(limit=4)` and normalize.
   - Smooth the weights only in the joint loops.
   - Rigid armor goes 100% to a single bone.
   - Run a quick pose test (elbow 120°, knee 130°, shoulder up 90°) and take a screenshot. Fix candy-wrapper twisting with the twist bones, not with more geometry.
8. **LODs.**
   - LOD1: simplify the fingers, take the middle joint loop out on the big joints, and turn the face loops into a planar face.
   - LOD2: mitten hands, and fold small accessories into the texture.
   - Drop the face bones from LOD1 onward by setting their weights to the Head bone.

## Pitfalls

- Be honest in the brief about what code-built organic forms are: a clean, correctly topologized base for an artist to polish, not a hero-final sculpt. Don't call it final.
- The neck seam between head and body shells must share vertex normals, so weld them before you split the UVs.
- If the game has both first-person arms and third-person bodies, every shared socket needs the same orientation in both. Otherwise carried items misalign between views.
