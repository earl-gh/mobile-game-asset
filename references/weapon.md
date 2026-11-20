# Weapon & equipment

A held item is on screen constantly in first person and fills a big part of the frame, so it's the highest-fidelity asset per pixel. The same item in the world (carried by others, dropped, deployed) is tiny. So build **two meshes from one source**. Every part, pivot and socket comes from the Part Inventory.

## Budget

| | LOD0 | LOD1 | LOD2 | Texture |
|---|---|---|---|---|
| 1P view | 7–12k tris | none | none | 2048 set |
| 3P / world | 1.5–3k | 800 | cull | the same set at mip 1–2 (no separate texture) |
| Small gadget / consumable | 1.5–4k (1P), 600 (3P) | | | 1024 |

- **Texel density:** highest on the asset, biased toward what the player sees most (the side facing the camera at 1.25×, hidden sides at 0.75×). Aim for at least about 2000 px/m. A small item on one 2048 set will land well above that, which is fine.
- **Materials:** 1. **Bones (1P):** one per independently animated part from the inventory, plus a root.

## Pipeline additions

1. **Scale and orientation.** Use real dimensions from the brief. Define the object's *use direction* (where it points, strikes or projects) and keep it consistent: −Y in Blender becomes +Z forward in Unity. Place the pivot at the hand contact point.
2. **Sockets from the inventory.** One empty per attach point: where the hand or off-hand grips (for IK), where the player's eye aligns (if the item is aimed), and where effects or projectiles originate. Misaligned eye or grip sockets force animation fixes later, so check them in an ortho screenshot.
3. **Hard-surface bake source (mid-poly workflow).**
   - Build the game mesh first, then duplicate it.
   - Add a weighted Bevel (2–3 segments, `profile=0.7`) to make the bake source. Skip Subdivision here: it rounds flat panels.
   - Boolean cuts (vents, grip texture, engravings) are applied **on the bake source only**. The game mesh carries them as normal-map detail.
   - This gives AAA-crisp edges at mobile tri counts.
4. **Game mesh priorities.**
   - Spend segments on the silhouette: round parts on the top and sides facing the camera get 8–16 sides, hidden ones get 6.
   - Small add-on details stay floating, not stitched into the main body. They bake and shade cleaner.
5. **Moving parts.** Each part marked "moves" in the inventory is a separate object with its pivot at its true hinge or slide axis, skinned 100% to its own bone (no soft weights on hard surfaces).
6. **Skin-ready UVs.** Give each recolorable zone from the inventory contiguous shells. Paint a zone-ID into the mask's B channel so a Unity skin shader can recolor by zone without new albedos (base albedo plus tint zones).
7. **Texture emphasis.**
   - Edge wear only on exposed convex edges, from the curvature mask, kept stylized and clean.
   - A painted top-to-bottom gradient.
   - Emissive zones as small as the inventory allows.
8. **Build the 3P mesh from the 1P one.** Delete interiors and hidden parts, reduce side counts to 6–8, merge floating details, and keep the same UV layout so it reuses the 1P texture at a lower mip. Keep bones only for motion that is visible from outside.
9. **Worn equipment.** Follow `character.md`: skin it to the body bones and hide the faces it covers. Thrown or deployed items follow `prop.md` rules, with a socket for effects.

## Pitfalls

- Mesh Compression must be Off for 1P meshes, because it wobbles close-up vertices.
- Transparent or see-through parts in the 1P view: use one opaque material with a painted gradient. A transparent pass in the middle of the screen is expensive.
