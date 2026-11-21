# Character (humanoid)

In a Valorant-like game, a player is identified at 30 m by **silhouette, color blocking and the shader's team fresnel**. Detail lives in shape and flat paint, not polygons or texture noise. Characters are the most saturated, most contrasted things on screen.

## Budget

| | LOD0 | LOD1 | LOD2 | Cull |
|---|---|---|---|---|
| Playable agent | 14–18k tris | 7–9k | 3–4k | < 2% screen |
| NPC / enemy | 8–12k | 4–6k | 1.5–2.5k | < 2% |
| 1P arms (separate asset) | 6–9k | none | | |

- **Texture:** one 2048 set (about 700 px/m, face shells 1.5×).
- **Materials:** 1, VStyle/Lit Character. No alpha hair.
- **Bones:** 50–65 body, plus ≤ 12 face bones or 8–15 blendshapes.
- **LOD transitions:** 0.45 / 0.2 / 0.02. Every LOD passes the silhouette IoU test.

## Blockout (most of the work, see `blockout.md`)

1. **Proportion sheet:**
   - 7–7.5 heads tall (realistic is 8)
   - shoulders 2.2–2.5 heads wide (heroic builds up to 2.7)
   - hands about 10% oversized, feet planted slightly wide
   - A-pose with arms at 45°

   Landmark empties for crown, chin, shoulders, elbows, wrists, hips, knees, ankles and balls of the feet, measured against the 1.8 m figure.
2. **Archetype in the masses.** Decide what the silhouette says before modeling: slim athletic, heavy, tall and lean. Encode it in the torso wedge (shoulder-to-waist ratio 1.4–1.7 for athletic builds), the leg length (legs at least half the height), and the head size.
3. **Body volumes:** Skin-modifier skeleton with graded radii (`blockout.md` §4), Subdivision 2, and a separate head volume with planes for brow, cheekbone, jaw and chin. Then **flatten the planes:** thigh front, shin, forearm and chest become broad facets with creases. Valorant anatomy is planar stylization, not soft realism.
4. **Costume over the body, as layered masses.**
   - Jacket, armour and pouches sit 1–4 cm proud of what's beneath, with a visible step and overlap direction.
   - Delete any body that's covered.
   - Each garment gets 3–5 wedge folds from tension points (shoulder, elbow, belt, knee). No small wrinkles.
5. **Signature silhouette pieces.** Every agent has 1–3 shapes nobody else has: a hood, a cape, a shoulder piece, a hairstyle, a gadget on the back. They're primary or secondary masses, exaggerated 15–25%, and they must show in the 30 m black silhouette **from the front and the side**.
6. **Hair:** 4–8 big sculpted clumps with one flow direction, as opaque geometry with sharp clump edges. Hair is a silhouette element, so block it in pass 1b, not at the end.
7. **Hands:** mitten blockout first (palm block plus thumb), then fingers as 4 tapered boxes with knuckle planes. Oversized and readable.
8. **Value plan:** greyscale `Col` zones following form breaks (jacket, pants, skin, gear). The accent sits on chest, shoulders or head, where the fresnel and the camera land.

## Pipeline additions

1. **Retopo** (Organic assets in `SKILL.md`):
   - 3 loops at the elbows, knees and knuckles, with the middle loop on the pivot
   - a shoulder loop from armpit across the deltoid
   - a diagonal hip loop from crotch to iliac crest
   - mouth and eye loops
   - triangles only in flat, non-deforming areas
2. **Rigid gear** stays hard-surface (chamfer class 1–1.5 cm), bound 100% to one bone.
3. **Texture:**
   - Color-block 60/30/10. Painted brows and lip line.
   - Skin: flat, no normal detail. Its shading comes from `T_*_RampSkin` plus the underglow.
   - Write vertex color R = 1 on skin.
   - No painted core shadows: tune the ramp instead.
4. **Skeleton:** Unity HumanBodyBones names if the character uses Humanoid, all deform bones, +Y down each bone. Twist bones for forearm and upper arm, `SOCKET_` bones for weapons and gadgets, cape or hood chains from the inventory.
5. **Skinning:** automatic weights, then `vertex_group_limit_total(limit=4)`, normalize, and smooth only in the joint loops. Pose test: elbow 120°, knee 130°, shoulder up 90°. Fix candy-wrapping with twist bones.
6. **LODs:**
   - LOD1: simplified fingers, middle joint loops removed, face bones reassigned to Head.
   - LOD2: mitten hands, small gear folded into texture.

   The signature pieces stay in every LOD.

## Pitfalls

- The 30 m read comes from the head, shoulders and signature pieces. Spending tris on belts and pouches is wasted.
- Large saturated red-pink areas on the upper body compete with the enemy fresnel.
- The neck seam between head and body shares vertex normals. Weld before splitting the UVs.
- First-person arms and third-person body share socket orientations exactly.
