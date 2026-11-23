# Topology (stage 3) and the blockout gate

Read this before stage 3, on a blockout that has passed the anatomy gate in `references/anatomy.md`. Run `scripts/audit_topology.py` on the result: it measures tri/quad mix, poles, buried faces and intersections, but cannot judge edge flow, so review loops by eye.

Tags: [S] directly sourced, [C] common studio practice, weakly sourced, [J] my judgment, no source found.
Part classes: deforming organic, rigid hard-surface, static environment, tips/caps, thin sheets, hidden surfaces.
Budget unit is triangles AND vertices: UV seams, hard edges and material splits duplicate vertices at runtime. [S Polycount Polygon Count]

## 1. Quads vs triangles
The engine always triangulates (n-gons >4 sides always; quads too unless Unity "Keep Quads", which exists for tessellation only). So quads are an authoring tool, triangles are the shipped result. [S Unity, Polycount]

| Part class | Policy | Why |
|---|---|---|
| Deforming organic (skinned) | Quads required in joint zones; tris only at loop terminations, in flat non-bending areas | Loops can be selected, weighted and stepped; tris stop loops. [S Polycount, Blender wiki] |
| Subdivided / bake-source (high poly) | All quads, poles on flat areas, no tris or n-gons on curvature | Subdivision exposes every flaw; sculpt tools pinch on tris. [S Polycount Topology] |
| Rigid hard-surface | Tris fine; model quads, triangulate last | "Every edge there for a reason"; bevels cost thin tris. [S Polycount] |
| Flat non-deforming areas | Tris/n-gon fans fine, fewest tris that hold the silhouette | No deformation or shading to protect. [S/J] |
| Caps and tips | End with a 2:1 ladder into a single quad, using side counts that halve to 4 (16, 8, 4). Avoid tri fans on anything that matters | Tested: fans made poles of valence 12-24 that the audit flagged; ladders cost a few faces and removed every high pole. A fan on a tiny rigid part is acceptable. [tested] |
| Thin sheets | Quads along the strip, no long slivers; give thickness only if silhouette needs it | Thin tris waste sub-pixel raster work. [S Polycount] |
| Hidden surfaces | Delete. Never spend tris on them | Manifold rule: no internal unseen faces. [S Polycount Topology] |

Rules:
- Triangulate ONCE (Blender Triangulate modifier, apply), then bake from that mesh and export that same mesh. Why: a quad is two triangles and its diagonal ("ridge" vs "valley") changes interpolated normals/tangents; if baker and engine pick different diagonals the normal-mapped lighting zig-zags. [S Polycount, Marmoset, Mikkelsen]
- Mirrored meshes: triangulation must be mirrored too, and triangulate BEFORE mirroring. [S Polycount]
- Bake in the tangent space the engine uses (MikkTSpace; Unity default "Calculate Mikktspace"). Do not edit UVs after baking. [S Marmoset, Unity, Polycount]
- Triangulate Quad Method: any fixed choice works if it is applied once; Beauty/Shortest Diagonal give fewest slivers. [S Blender manual for options, J for recommendation]
- Weighted Normal (Keep Sharp, Face Area/Corner Angle) fixes flat-face shading on large faces; Keep Sharp does not fully stop smoothing between two sharp edges. Run it before the final triangulate, then export normals. [S manual; ordering J]
- Practical rule: model quad-dominant, add tris only where they end loops or sit in flat/hidden areas, triangulate last, verify in the engine. [C]
- Remesh/Quadriflow are NOT topology for skinned parts. Quadriflow suits subdivision/sculpt bases and does not clean intersections; Remesh adaptivity adds triangles. [S Blender manual]

## 2. Poles and valence
- Valence 3 and 5 are normal. Avoid 6+ ("star" poles pinch under deformation and subdivision). [C; Blender-oriented guide, Polycount forum]
- Put poles on flat or hidden areas, away from joints and off the silhouette. Why: poles make dimples/bumps when subdivided and shade/deform unevenly. [S Polycount Topology]
- A 3-pole condenses density, a 5-pole spreads it; use them to steer loops, not by accident. [C CG Cookie snippet]
- High-valence poles in a tested build came from cap fans and from holes placed too close together. Ladder the caps and leave at least one column of faces between neighbouring holes; valence 6+ on a deforming body is achievable to avoid. [tested]
- Audit the quad version of the mesh for poles and the triangulated version for thin and buried triangles: triangulating adds valence and raises false pole errors. [tested]
- Five-point poles are not banned (geodesic shapes use them). This is judgment, not law. [C]

## 3. Edge flow at joints and deformation zones
- Highest topology effort goes to hips, shoulders, elbows, knees, mouth corners, hands/fingers. [S Polycount Topology]
- At least 2 loops across a bend, 3 where the range is large; main loop on the pivot, support loops either side. Why: with 1 loop the bend collapses; weights fall off gradually across loops. [forum S for 2 loops, 3+ weak; pivot placement J]
- Inner side of a hinge may be one collapsing polygon, not a middle edge. [forum]
- Rig a rough weight pass and test extreme poses BEFORE locking topology. [forum]
- Step density by halving edge count per step (1:2), absorbed by a tri pair or a 3/5 pole in a non-bending area; never jump from dense ring to a long tri. Why: sub-pixel slivers cost raster work and shade badly. [C/J; slivers S Polycount]
- Static, rigid, non-deforming parts do not need loops; spend nothing on flow there. [C]
- A cheap way to get deliberate loops from an approved blockout volume: ray-march a ring of rays from a centre line at planned stations, so loops land exactly at joints and support positions. The ray length must exceed the largest local radius and the centre must sit inside the volume. Pick side counts that halve to 4. [tested]
- The limb-to-torso junction is the weak spot: the joint centre is inside the torso, so the loops are really armpit and groin loops (hole rim, transition loop, first limb ring), and weights jump across the hole rim, causing flat skirt panels and cracks. Plan a gradual weight falloff there and pose-test early. Do the pose test before trusting the audit: it found the junction problem the audit could not. [tested]
- Build LODs by running the same builder with coarser parameters, not by decimating, and drop the side count right after a limb root so the step does not create slivers. [tested]

## 4. Intersecting geometry policy
Acceptable (studio practice): rigid hard-surface details as floaters baked into the normal map; instanced/modular static meshes; buried faces removed. Why: normal maps store direction, not depth, so floaters are cheap; instance-based engines render them fine. [S Polycount NMM, forum]
Not acceptable: skinned deforming meshes; silhouette-defining joins; any parts that share normals or one tangent-space bake region. Why: floaters slide apart when deformed; baker rays and averaged normals break at the intersection. [J for skinned; S for bake issues]

Costs of needless intersections: wasted triangles on buried surface; bake ray artifacts, AO darkening/halos near floaters, cage skew growing with floater distance; coplanar z-fighting; UV space spent on invisible areas; aliasing where low-poly edges overlap in-game. [S Polycount, Marmoset; z-fighting and UV waste C]

Joining rules:
1. Prefer one contiguous low-poly mesh where the budget allows (fewer bake overlaps, less in-game aliasing, better UVs). [S Polycount Texture Baking, NMM]
2. To merge: boolean/remesh union then clean up, or place the part ON the skin (within about 1 mm) as a separate shell. Tested: a 3 mm sink left 10% of the part buried, and 1.5 mm above the skin showed a gap, so sinking "a limited depth" is impractical. For organic parts the best join was fusing into the body with hole-and-bridge: equal vertex counts on both sides, one relaxed transition loop, a gap between neighbouring holes, and never projecting the transition loop back onto the surface (it tangles). [tested]
3. For a smooth silhouette join, add a collar/boss: a small ring with 1 loop of bevel at the host surface. [J]
4. Keep seams (UV, hard edge, material, mesh breaks) on hidden borders: underside, back, inner side. [C; hard edges need UV splits S Polycount/Marmoset]
5. If a floater must stay: separate object/bake group, exploded or Ignore Backfaces/limited cage distance for the bake, move back afterwards. [S Polycount, Marmoset]
6. Never let two coplanar faces overlap; offset or delete one. [C]

## 5. Triangle budget distribution
- Ask the lead for the asset budget; the wiki gives no universal number. [S Polycount]
- Spend where it shows: silhouette first (curvature, not flat runs), then deformation zones, then close-view/focal detail. [S Polycount Topology: add polys where there is curvature]
- Starting split (tune per asset): about 50% silhouette, 30% deformation, 20% close-view detail; deformation share is ~0 for rigid parts. [J, no source]
- The rest (flat areas, small bevels, surface detail) goes to normal map/texture/shader, not geometry. Prefer hard edge + matching UV split over geometric bevels (cheaper), noting opinions differ. [S Polycount NMM]
- Count tris with modifiers applied AND check vertex count (hard edges, UV splits). [S]

## 6. Blockout review gate
Lock a grey-box before detail, UV, bake or texture: changes after bake invalidate UVs, normals and weights. Source evidence covers level/environment greyboxing (scale, silhouette, sightlines, detail deferred); the per-asset gate below is my synthesis. [S partial, J]

Deferred until after the gate: high-poly detail, bevels, UVs, bakes, materials/texture, LODs, rig weights, fine props.

### Blockout gate checklist
- [ ] Silhouette reads at game camera distance (render at target size, grey, side + front + 3/4). PASS: each part class identifiable; FAIL: merges into blob.
- [ ] Proportions and scale: real-unit dimensions vs. a scale reference (capsule/mannequin/door); 1 Blender unit = 1 m, scale applied.
- [ ] Part inventory: every part in the concept/spec exists, named, no extras.
- [ ] Pivots and axes: origin at the agreed point (base or joint), forward/up per Unity import, rotation/scale applied.
- [ ] Joint locations: pivots sit on the bend points; room for 2-3 loops each side.
- [ ] Tri budget by region: silhouette / deformation / detail within band; total <= budget (hard fail over).
- [ ] Intersection and buried-face counts: zero buried faces on skinned parts; floaters only on rigid hard-surface and listed; no coplanar overlaps.
- [ ] Topology audit: no n-gons >4 in deforming zones, no poles of valence 6+, poles off joints/silhouette, no slivers, manifold, no internal faces.
- [ ] Sign-off recorded; later changes need a re-gate. All items [J] thresholds; adjust per project.
