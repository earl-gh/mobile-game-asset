# Surface layering (Blender-only equivalent of a Painter layer stack)

Flat zone colours, one gradient and soft AO read as a toy. What separates a studio asset is **detail at three scales, and every colour or roughness layer driven by a baked map instead of a uniform fill**. Read this for any organic, hero or close-view asset; trivial hard-surface props can stay on the base recipe in `SKILL.md`.

## 1. Reference first
Before any stage, write 3–5 concrete surface traits from the text or image: the pattern (plates, scales, weave, panel lines), where dirt and wear collect, the colour variation between zones, and the roughness story. Every layer below must trace to one of these traits. Without them the layers become generic noise.

## 2. Detail at three scales
| Scale | Carried by | Example traits |
|---|---|---|
| Primary | game mesh silhouette | big masses, horns, plates |
| Secondary | game-mesh bevels and the baked normal map | muscle and plate edges, folds |
| Micro | baked normal map only | pores, scale pattern, fine ridges, scratches |

Micro and secondary detail are **built on the bake source, not by hand**: subdivide a copy of the game mesh until quads are small enough for the finest feature (about a third of its size), then add Displace modifiers driven by procedural textures (Voronoi for cells and scales, Clouds for lumps), one per scale, each masked by a vertex group so the pattern follows the anatomy and stops at joints. Bake the normal map from it to the game mesh with Selected to Active and a cage. Use the Subdivision rule from `SKILL.md`: it rounds hard-surface panels, so hard-surface sources get bevels instead.

## 3. Utility bakes (all from the bake source, Cycles)
- **Normal** (tangent), and **AO**.
- **Curvature/edge:** an Emission bake of Geometry → Pointiness. It needs dense geometry along edges, so run it on the detail source.
- **Thickness/cavity:** an Emission bake of Ambient Occlusion with *Inside* enabled, or AO baked with flipped normals.
- **Position:** an Emission bake of object-space Z (and Y if the asset is long), for height-based gradients.

## 4. The colour stack (bottom to top)
Build it as one node material, then bake it down to the albedo with an Emission bake so lighting doesn't leak in.
1. **Base colour per zone**, from the brief's palette, never pure black or white.
2. **Colour variation:** a Noise or Voronoi texture at two scales, multiplied at 10–20% strength, shifting hue slightly between regions (cooler on top, warmer underneath).
3. **Cavity colour:** curvature or AO through a Levels-style ColorRamp as a mask, tinting recesses darker and hue-shifted, with dirt between the pattern cells.
4. **AO tint** at 30–50%.
5. **Dirt and staining:** Position and thickness as the mask (low, occluded areas collect more) broken up by noise, as streaks where gravity applies. Place it as the reference traits say.
6. **Breakup:** irregular patches or mottling on a few cells or panels, so no two regions match.
7. **Edge highlight:** the convex edge mask at 10–20% lighter.

Every mask goes through a ColorRamp or Levels and a noise break, so no layer has a clean edge or a uniform strength.

## 5. Roughness logic
Per-zone base value, then: higher in occluded or dirty areas, lower on convex edges and on smooth plates, with a noise break of a few percent. This is where realism lives, more than in colour.

## 6. Seams
Hide UV seams in unseen areas and bake the albedo so the stack doesn't depend on UV tiling. Where an object-space or triplanar mask crosses a seam, check it in the preview and paint over it in the mask.

## 7. Check
Render at game distance and at 25% scale, beside the reference. The surface should show visible tonal variation, with recesses distinct from raised areas, and nothing should look like one flat colour. If it does, a layer is missing a mask.
