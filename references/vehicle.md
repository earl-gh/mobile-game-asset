# Vehicle

A vehicle is a hierarchy of rigid parts with gameplay pivots. Its look in a Valorant-like game: a chunky, faceted body with big chamfers, an exaggerated stance and readable function (wheels, thrusters, turret), color-blocked like a character if players ride it, toned down like a prop if it's set dressing.

## Budget

| | LOD0 | LOD1 | LOD2 | LOD3 |
|---|---|---|---|---|
| Player-driven | 18–30k | 9–15k | 4k | 1k hull |
| AI / traffic | 6–12k | 3–6k | 1.5k | cull |

- **Texture:** one 2048 set at 300–500 px/m. Mirrored and repeated parts share UV space.
- **Interior:** only with a visible cockpit, ≤ 15% of LOD0, gone from LOD1.
- **Material:** 1 opaque VStyle/Lit Prop. Glass is opaque with a dark painted gradient: no transparency.

## Blockout (most of the work)

1. **Contact points and the H-point first:**
   - wheel hubs, track contacts or hover pads
   - seat H-point and entry height, sized against the 1.8 m figure
   - overall length, width and height from the brief

   Wheelbase and track width are locked metrics.
2. **Side profile extrusion:** the body outline from the landmarks (nose, windshield rake, roofline, tail), extruded, then tapered in the plan view (narrower at nose and tail).
3. **Stance and exaggeration:**
   - Wheels or pods pushed out to the corners, 10–20% oversized.
   - Track width wider than the body at the wheels.
   - Nose slightly down.
   - The body sits on the wheels with visible arch clearance.
4. **Negative space:** wheel arches cut deep, a gap under the chassis, an open cage or frame, handholds.
5. **Facets:** large body panels as 3–6 flat facets with creases and 3–5 cm chamfers. No smooth car-design surfacing.
6. **Hierarchy and pivots from the inventory:**
   - The root sits on the ground under the center of mass.
   - Every wheel, door, turret and hatch is a child with its pivot on the true axis and rotation applied.
   - Range-test each one in clay: steering lock, suspension travel, door swing.

   Unity physics components live on separate empties.
7. **Value plan:** body / chassis and mechanical / accent as separated greys. Lights and engines are emissive zones.

## Pipeline additions

1. **Panel gaps:** one inset loop with a chamfer, plus a normal groove.
2. **Repeated parts:** model one and instance it. Tread pattern goes in the normal map, not geometry.
3. **Damage (only if asked):** a `_dmg` swap reusing the UVs.
4. **LODs:**
   - LOD1: interior gone, round parts at half the sides.
   - LOD2: quarter sides, small articulated parts merged.
   - LOD3: hull plus bare moving shapes.

   The hierarchy is kept in every LOD where motion is visible.

## Pitfalls

- The collider is a convex `_COL` hull of ≤ 255 tris, or compound boxes.
- A rotated pivot spins around the wrong axis in Unity: apply rotation on children.
