# Blockout and the Shape Gate

Texture and shading only decorate a shape. If the clay is ugly, the final asset is ugly, so this file gets more of your effort than any other stage. Work in **grey clay** (`scripts/shape_review.py`). Color, texture and the VStyle shader are banned from review until the Shape Gate (§6) passes.

A blockout is not "rough primitives". It's the asset's final proportions, silhouette, masses, negative space and pivots, built cheaply enough to change in seconds. Every later stage is forbidden from changing those things.

## 0. Starting from a free base

When `references/sourcing.md` found a usable base, import it with `scripts/import_base.py` before 1a. The base changes *how* you build 1b and 1c, not *what* passes the gate:
- **Measure it, don't trust it.** Snap the landmark empties (1a) onto the base and compare its ratios with the brief. Free bases are usually realistic (8 heads tall, narrow shoulders, small hands, realistic animal heads). Push them to the brief's stylized proportions with a Lattice or proportional edits, and record each change.
- **Restyle it to the Valorant shape language:** flatten broad areas into planes, sharpen creases, taper, exaggerate the defining trait, open the negative space, delete small forms. A realistic base left as-is fails Gate items 3, 5 and 6.
- **Hard surface:** use the base only as an underlay. Trace your own side profile over it, extrude, and hide the base.
- **Kitbash parts** get the asset's chamfer class and facet treatment so they don't look pasted on.
- **Retopo is still required** for organic bases. Imported topology is rarely game-ready.

## 1a. Proportion skeleton and scale card

Build the measurements before any volume exists.

1. **Scale card.** Place a 1.8 m reference figure (a capsule plus a head sphere at 7.5 heads) and a 1 m cover-height box beside the asset. It stays in every review render. Nothing gets eyeballed without it.
2. **Landmark empties.** Make one empty per measurable landmark, named and positioned from the brief or reference image. Examples:
   - character: crown, chin, shoulder L/R, elbow, wrist, hip, knee, ankle, ball of foot
   - weapon: muzzle, sight line, grip, trigger, mag well, stock butt
   - vehicle: wheel hubs, seat H-point, roof, bumpers
   - prop: footprint corners, hinge line
3. **From an image:**
   - Load it as a reference empty (`empty_display_type='IMAGE'`) in the matching ortho view, scaled so its known-size unit matches metres.
   - Snap each landmark onto the picture in front **and** side views. Where the two views disagree, trust the one with the clearer known-size unit, and log the conflict as an assumption.
4. **Write the measurement table** into the brief: each landmark's position, and the key ratios (head:body, barrel:receiver, wheelbase:length, lid:body).
5. **Exit:** print every landmark and ratio, and compare it to the brief. Everything within ±3% (±1% for anything gameplay-metric: cover height, door width, eye height, first-person sight line).

## 1b. Primary masses (the big shapes)

1. **Few masses.** Build 1–3 primary masses (at most 5 for vehicles or creatures) that, together, *are* the silhouette at 30 m. Use the simplest shapes that hold the planes:
   - boxes beveled into 45° chamfer profiles for hard surface
   - Skin-modifier volumes on the landmark skeleton for organic forms
   - extruded side profiles for weapons and vehicles: draw the side outline as a polygon from the landmarks, then extrude to width. That beats stacking cubes, and it's where weapons get their designed outline.
2. **Gesture before detail.** Give the masses direction:
   - a character's weight shift and A-pose
   - a weapon's forward sweep
   - a creature's spine curve and head carriage
   - a vehicle's stance (nose down, wheels pushed out to the corners)

   A static, axis-aligned blockout makes a static, boring asset.
3. **Taper everything.** No parallel-sided mass unless function demands it (a barrel, a pipe). Limbs taper toward the extremities; housings taper toward the front or top.
4. **Planar faceting from the start.** Build broad flat or gently curved planes meeting at creases. Mark the creases now (`bevel_weight_edge` = 1) so the shape pass just turns the bevel on.
5. **Exit:**
   - In the black silhouette render at 30 m, a stranger names the object and its facing.
   - The big shapes take about 60% of the silhouette area (the brief's ratio).

## 1c. Secondary forms and negative space

1. **Add medium forms only:** plates, pouches, sleeves and cuffs, mag and stock, wheel arches, crest plates. Each one must **change the silhouette or the plane structure**. If a form does neither, it's a texture detail: delete it.
2. **Cut the negative space** on purpose:
   - gap between arm and torso
   - trigger guard opening
   - space between the legs
   - gap under a vehicle chassis
   - holes in a creature's crest

   Holes are the cheapest readability there is, and blobs come from skipping them.
3. **Exaggerate function** by 10–25%: the mag, the muzzle device, the hands, the head and horns, the hero gadget, the wheels. Re-check the measurement table afterwards and record the intentional deviations.
4. **Overlap and layering.** Secondary forms sit *on* primaries with a visible step (2–4 cm at character scale) and a clear direction of overlap (top layer over bottom, front over back), like clothing over a body or armour over cloth. Flush, coplanar add-ons read as decals.
5. **Small forms stay out:** straps, buckles, bolts, vents and stitching. Note them in the brief for texture, or for the 1P normal map.
6. **Exit:**
   - The big/medium/small area ratio is about 60/30/10, small ≤ 10%.
   - Every medium form passes the "does it change the silhouette or planes" test.

## 1d. Hierarchy, pivots and value planning

1. **Split parts** exactly as the Part Inventory says. Each moving part is a separate object with its pivot on the true axis, with applied rotation, and its axis along a local axis.
2. **Test every pivot** by rotating or sliding it through its full range in a script. Render the extreme poses in clay. Things to catch:
   - intersections (lid into body, stock into grip, wheel into arch at full suspension)
   - holes that open
   - silhouettes that break
3. **Sockets:** a `SOCKET_` empty for every attach point, oriented as the inventory says.
4. **Value planning (still not texturing).** Assign each mass a flat *grey value* from the brief's value bands, as a color attribute `Col` in greys only. Render the greyscale thumbnail: the three zones must separate. If they don't, fix the zone *boundaries* (move them to follow form breaks), not the colors.

## 2. Shape pass (what turns a good blockout into a Valorant shape)

- **Chamfer classes.** One bevel width per size class on the whole asset (weapons 1 cm, character gear 1–1.5 cm, props 2–4 cm, vehicles 3–5 cm, architecture 5–10 cm). Chamfers are what catch the cubemap highlight. Without them the asset reads as a toy or CAD model.
- **Facet the curves.**
  - Large curved surfaces become 3–6 broad facets with a crease between them, not a smooth 32-segment curve.
  - Round parts get the segment count their screen size needs (category file), with the extra segments spent on the silhouette side.
- **Fold wedges** on cloth: 3–5 big triangular or wedge folds per garment, coming from tension points (shoulder, elbow, knee, belt). Never noise-like wrinkles.
- **Crisp transitions.** Where a soft part meets a hard one (glove to sleeve, rubber grip to receiver), put a visible step or seam line, never a smooth blend.
- **No drift.** After the shape pass, the silhouette IoU against the blockout stays ≥ 0.97 (`shape_review.py` with `COMPARE`). Bigger changes mean the blockout was wrong: fix it there and record it.

## 3. Ugly-shape tells (fail on sight)

| Tell | Looks like | Fix |
|---|---|---|
| Primitive stacking | Cubes and cylinders intersecting with no transitions, a "made of Lego" read | Extruded profiles, bridge the masses, step overlaps |
| Tube anatomy | Constant-radius limbs, a sausage neck, a capsule head | Graded radii per landmark, separate head volume with a jaw and brow plane |
| Blob | Everything subdivided, no creases, soft everywhere | Planar faceting, marked creases, chamfer classes |
| Clutter | Many same-size parts, a busy silhouette edge, no rest area | Delete small forms, merge medium ones, restore big planes |
| Dead pose | Axis-aligned, symmetric, no gesture | Gesture line, weight shift, a forward or up sweep |
| Wrong scale | Off against the 1.8 m card, gameplay metric missed | Back to 1a, measure |
| Flat stack | Add-ons flush with the surface, no overlap direction | 2–4 cm steps, layered overlap |
| Floating parts | Gaps where parts should connect or contact | Contact, embed, or a visible mount |
| Even ratio | Big and medium shapes the same size, nothing dominant | Push the dominant mass, shrink the rest |
| Parallel everything | No taper, no perspective in the forms | Taper toward the extremities |

## 4. Category blockout recipes

- **Character:**
  - Landmarks from the 7–7.5-head proportion sheet, shoulders 2.2–2.5 heads wide, hands 10% oversized, A-pose at 45°.
  - Skin-modifier body with graded radii: neck 0.06, deltoid 0.075, upper arm 0.055, elbow 0.045, wrist 0.035, hand 0.04, chest 0.17, waist 0.14, hip 0.16, thigh 0.085, knee 0.06, calf 0.06, ankle 0.04 m, for a 1.8 m slim build. Scale by archetype.
  - The head is its own volume with planes for cranium, brow, cheek, jaw and chin.
  - Costume masses sit *over* the body as a layered step.
  - Hair as 4–8 big clumps with a clear flow direction.
- **Creature:** stick skeleton from the reference (spine curve, girdles, limb segments, stance type) → graded skin volumes → the species' defining trait exaggerated 20–30% → head volume with jaw, brow and muzzle planes.
- **Weapon:**
  - Side profile first, as one extruded polygon from the landmarks (muzzle, sight line, grip angle 15–20° back, mag rake). Add width variation by insetting the profile.
  - Check the 1P view early: a camera at the eye socket, 60–70° FOV. The weapon's top line and sight must read there, and its silhouette lower-right of screen must say what it is.
- **Prop:** footprint and height as a gameplay metric (cover height exact) → the main body as a chamfered box or extruded profile → the hinge and interact parts split → the read-from-across-the-room test.
- **Vehicle:** wheel or contact positions and the H-point first → side profile extrusion → plan-view taper → wheel arches cut as negative space → stance (track width wider than the body at the wheels).
- **Environment kit:** grid and metrics first (cover 1.0 m, wall 3–4 m, door 1.4–2.0 m) → each kit piece as its profile on the grid → a test assembly of the described space from player eye height before any piece gets detail.

## 5. Review renders (`scripts/shape_review.py`)

One clay sheet per pass:
- orthographic front, side and top with the scale figure
- two 3/4 perspective views
- black silhouettes at 10 m and 30 m game-camera pixel size
- the greyscale value thumbnail (if `Col` exists)

The script prints the bbox, landmark distances and, with `COMPARE`, the silhouette IoU against a previous version. Show the sheet to the user at the end of 1b and at the Shape Gate.

## 6. Shape Gate checklist (all must pass, in clay)

1. **Scale:** dimensions and gameplay metrics within tolerance (§1a).
2. **Silhouette:** recognizable with its facing from the black 30 m silhouette, from front and side.
3. **Hierarchy:** big/medium/small ≈ 60/30/10, and one dominant mass is obvious.
4. **Negative space:** every intended gap is open in at least one main view.
5. **Gesture:** the asset has a direction (pose, sweep or stance), with no dead axis-aligned symmetry unless function demands it.
6. **Planes:** broad planes with creases and chamfer classes. No blob areas on hard parts, no tube anatomy on organic ones.
7. **Layering:** secondary forms step over primaries with a clear overlap direction. Nothing floats.
8. **Function:** moving parts pass their full-range clay test with no intersections.
9. **Values:** greyscale zones separate in the thumbnail.
10. **No ugly tells** from §3. Name any you found and how you fixed them.

Write the score into the brief as one line per item: `PASS` or `FIXED: <what>`. When the user is in the loop, they approve the sheet before stage 3.
