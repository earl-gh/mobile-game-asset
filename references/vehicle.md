# Vehicle

A vehicle is a hierarchy of rigid parts with gameplay pivots. The locomotion type (wheeled, tracked, hover, flying, sailing, legged) comes from the brief, and so does every moving part. Its cost on mobile comes from transparency, the interior, and how many copies are on screen.

## Budget

| | LOD0 | LOD1 (Low hero) | LOD2 | LOD3 |
|---|---|---|---|---|
| Player-driven | 18–30k tris | 9–15k | 4k | 1k hull |
| AI / traffic | 6–12k | 3–6k | 1.5k | cull |

- **Texture:** one 2048 set at 300–500 px/m. Repeated parts that are mirrored or identical can share one region of it. **Interior:** only on player vehicles with a visible cockpit, ≤ 15% of the LOD0 budget, removed from LOD1 onward.
- **Materials:** 2 (opaque, plus one transparent). Don't put transparency on AI vehicles at all: paint it dark into the albedo.

## Pipeline additions

1. **Measure from the strongest reference.** In an image, use the most reliable known-size element (a wheel, a door, a seat). In text, use stated dimensions. Size the vehicle against the character (about 1.8 m tall), since entry and seat heights are gameplay metrics.
2. **Hierarchy and pivots from the inventory.**
   - The root pivot sits on the ground under the center of mass, with rotation zero.
   - Every moving subsystem becomes a child object with its pivot on its true axis (the hub of a spinning part, the hinge line of a panel, the yaw and pitch axes of a mount). Name each `<function>_<position>`.
   - Apply all rotation on children, and keep each part's axis along a local axis. A rotated pivot spins around the wrong axis in Unity.
   - Unity physics components (WheelCollider and similar) live on separate empty objects, and the visual parts only follow them.
3. **Shape pass.**
   - Panel gaps: one inset loop with a chamfer in the game mesh, plus a normal-map groove.
   - Body panels use the hard-surface mid-poly bake (see `weapon.md` §3).
   - Big flat panels need enough loops to stay flat after weighted normals, so keep face weighting on.
4. **Repeated parts.** Model one and instance it, mirrored where the vehicle is symmetric. Surface tread and fine detail go in the normal map and albedo. Spend geometry only on the silhouette, and hide any face that points into the body.
5. **Damage (only if the brief asks).** Damage is a swap: a `_dmg` variant reusing the UVs, plus a dirt or scorch layer through the vertex color R channel.
6. **Emissive zones** come from the inventory (lights, displays, engines) and live in the mask. Light cones go in Unity as cookies or flares, not geometry.
7. **LODs.**
   - LOD1: interior gone (dark-tinted windows), repeated round parts at half the sides, panel-gap loops removed (normal map only).
   - LOD2: quarter sides, small articulated parts merged into the body.
   - LOD3: hull plus bare shapes for any part that still reads as moving.
   - Keep the hierarchy in every LOD where a moving part is still visible.

## Pitfalls

- The collider is a convex `_COL` hull of at most 255 tris, or compound boxes. Never use the render mesh.
