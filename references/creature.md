# Creature (non-humanoid)

Anatomy drives everything. A creature reads as alive when its forms follow the skeleton, and as Valorant-like when its masses are planar and its defining trait is exaggerated: a bull's neck, a raptor's claw, a stalker's crest. Enemies get the same team-fresnel treatment as characters, so read `character.md` for the shader setup.

## Budget

| Size class | LOD0 | LOD1 | LOD2 | Bones |
|---|---|---|---|---|
| Small (critter, pet) | 2–4k | 1–2k | 500 | 15–30 |
| Medium (enemy, mount) | 7–11k | 3.5–5k | 1.5k | 35–60 |
| Boss | 16–24k | 8–12k | 4k | 60–90 |

- **Texture:** 1024 for small, 2048 for medium and boss (400–700 px/m).
- **Material:** 1, VStyle/Lit Character. Emissive eyes and weak points use MAER G.

## Blockout (most of the work)

1. **Stick skeleton first.** Measured from the reference or the brief:
   - the spine curve as 5–8 points: neck arch, back line, pelvis tilt
   - the shoulder and hip girdles
   - limb segment lengths
   - the stance: digitigrade, plantigrade or unguligrade, which decides where the visible "knee" bends
2. **Gesture.** The spine curve and head carriage *are* the creature's character: a stalker's low head and arched back, a brute's forward-thrust shoulders. Block the gesture before any volume, and check it in the side silhouette.
3. **Graded volumes:**
   - Skin-modifier radii heavy at the shoulder and hip masses, tapering hard to the wrists, ankles and tail tip.
   - The rib cage is a big wedge, the waist a pinch: the negative space under the belly sells the build.
   - Head as a separate volume with planes for cranium, brow, muzzle, jaw and cheek. Never a tapered tube.
4. **Exaggerate the defining trait** 20–30%: crest, horns, claws, club tail. It's a primary mass in the 30 m silhouette from the side, the creature's main readable view.
5. **Armour and plates** as separate faceted shells stepping over the body (2–5 cm), with overlap direction head→tail. Spikes and horns are tapered, faceted 5–6-sided cones with a sweep, not straight cones.
6. **Negative space:** between the legs, under the belly, between the crest plates, between the horns and the skull.
7. **Value plan:** body / armour / glow as separated greys. Glow zones sit where the eye goes (eyes, chest, weak points).

## Pipeline additions

1. **Bake source:** remesh-merge the volumes, push planes and creases (no smooth blob), then add big anatomy as merged volumes. The normal map carries plate edges and big muscle forms. Fine scales or pores only if the creature is seen close up, and never on a 3P enemy at mobile scale.
2. **Topology:**
   - radial loops at ball joints, 3 loops at hinges
   - 6–10-sided rings on tapering appendages
   - articulated openings get their own loop set plus a ~200-tri interior seen only when open
3. **Secondary chains:** swaying parts from the inventory get 3–8 bones (`<part>_01..`).
4. **Rig:** `root` at the ground under the center of mass → `pelvis` → spine. IK target empties at the ground contacts. ≤ 4 influences, plates 100% to one bone.
5. **LODs:**
   - LOD1: halve the appendage rings, close openings.
   - LOD2: merge digits and small spikes.

   The defining trait stays in every LOD.

## Pitfalls

- Floating girdles (shoulder blades) need a sliding bone, or the limb pinches.
- Thin membranes are thin closed geometry, not single-sided planes.
