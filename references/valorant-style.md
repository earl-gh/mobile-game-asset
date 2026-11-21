# Valorant design language

Read this before the brief. Every rule below is either **[Riot]**, stated in Riot's article [VALORANT Shaders and Gameplay Clarity](https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity), or **[House]**, a production rule this skill adds to get that look with Blender and Unity. Don't present a House rule as Riot's.

## 1. The three pillars

**[Riot]** Every visual decision balances **performance, competitive integrity and art**, "evenly in the middle of this triangle". Realism, immersion and cinematics are explicitly not pillars.

Consequences for an asset:
- **The look lives in the shader, not the texture.** **[Riot]** Valorant lights dynamic objects with a single directional light styled by an artist-authored gradient ("we use a single light and style the heck out of it"). Specular comes from panoramic HDR captures with painted hotspots, and ambient is clamped per area. So the albedo must not contain light: no painted form shadows, no top-down gradient, no AO multiply. The ramp places the core shadow, and the albedo is "the general color of a surface".
- **Quality settings never change what a player can see.** **[Riot]** "no differences between low, medium, and high graphics quality settings that could change the competitive landscape". There are no dynamic shadows in the playable space, and cast shadows appear only on your own first-person hands and weapon. Low settings cut shader *instructions*, never gameplay features.
- **Environment is cheap and quiet; characters must pop.** **[Riot]** Players "mentally block out the environment", and characters "need to always stand out from their environment".

## 2. Shape language [House]

Valorant reads as *stylized realism*: real-world construction logic (seams, straps, fasteners, panel breaks), simplified into big confident planes.

| Rule | Do | Don't |
|---|---|---|
| **Big / medium / small** | About 60% of the silhouette from 1–3 big masses, about 30% medium forms (plates, pouches, sleeves), at most 10% small (straps, clips, vents). | Even distribution of same-size parts (reads as clutter at 30 m). |
| **Planar faceting** | Broad flat or gently curved planes meeting at **sharp, chamfered creases**. Hard surface: 45° chamfers. Cloth: folds as 3–5 large wedge shapes. | Soft blobby subdivision on hard objects. Tubes with uniform radius. |
| **Taper and direction** | Forms taper toward extremities and lean in one design direction (forward-swept on weapons, upward on characters). | Parallel-sided, symmetric-by-default forms. |
| **Exaggerate the function** | Oversize the part that tells you what it is: the mag, the muzzle, the hands, the hero gadget, the head of the creature. | Scaling everything up evenly. |
| **Chamfer classes** | One chamfer width per size class, kept on the whole asset (see the category file). Chamfers catch the cubemap highlight, and that's the "crisp edge" look. | Mixed random bevel widths; no bevels at all. |
| **Detail budget by distance** | Small detail exists only where the camera gets close: 1P weapons, 1P hands, character-select close-ups. Third-person and world views carry big and medium forms only. | Rivets, scratches and micro-panels on a third-person mesh. |
| **Clean negative space** | Gaps between masses (arm and torso, stock and grip) are readable holes in the silhouette. | Filling gaps with straps and pouches until the silhouette is a blob. |

## 3. Color and value [House, built on Riot's readability pillar]

- **Character identity palette.** One dominant hue (about 60% of visible area), one secondary (about 30%), one accent (about 10%) on a gameplay-readable spot (chest, shoulders, head, ability device). Keep skin as its own value band.
- **Value bands, not just hue.** Plan each zone's albedo value (sRGB luminance, 0–1). Neighbouring big zones differ by at least 0.15 so the asset reads in greyscale. Albedo stays in 0.06–0.85: no pure black or white, since the ramp shader needs headroom.
- **Saturation ladder.** Characters and interactables are the most saturated things in the game. Environment albedo is about 20–35% less saturated and lower in contrast. Props sit between, unless they're interactive (then accent-colored).
- **Reserved signals.** Saturated red-pink belongs to the **enemy fresnel** **[Riot: enemies have a red fresnel, allies a neutral blue]**. Don't put large saturated red areas on a character's upper silhouette, because they compete with it. Ability and interaction accents use emissive, which the shader keeps on every tier.
- **Material color logic.** Painted variation in the albedo must be explained by the *material* (dye fade, worn paint on edges, darker stitching, a different fabric panel). Never by *light* (darker underneath, lighter on top, shadow in folds).

## 4. Surface vocabulary [House]

Albedo values below are sRGB luminance ranges. Roughness and metallic go to the MAER mask.

| Material | Albedo value | Roughness | Metal | Normal map carries | Albedo may carry |
|---|---|---|---|---|---|
| Painted metal / polymer (gear, weapons) | per palette | 0.35–0.55 | 0 | chamfers, panel lines | edge-wear to bare metal on **convex** edges only, 2–6 px wide |
| Bare / machined metal | 0.55–0.75 | 0.2–0.4 | 1 | chamfers | slight hue shift (warm steel, cool aluminium) |
| Fabric / cloth | per palette | 0.7–0.9 | 0 | big folds and seams only | stitching lines, dye panels |
| Leather / rubber | 0.12–0.35 | 0.55–0.8 | 0 | chamfers, seams | edge lightening on folds |
| Skin | per character | 0.5–0.65 | 0 | **none** (flat for a clean read) | painted brows, lip line, subtle cheek/nose warmth |
| Hair (sculpted clumps) | per character | 0.45–0.6 | 0 | clump forms | strand gradient root→tip inside each clump |
| Glowing tech / emissive | 0.5–0.9 | 0.3 | 0 | none | flat color; glow comes from the MAER emissive range |
| Environment plaster / stone / concrete | 0.35–0.7 | 0.75–0.95 | 0 | trim-sheet chamfers | large soft tonal shifts (≤ 8%), no grime noise in play space |

**Noise budget.** High-frequency albedo detail (anything smaller than about 1/64 of the asset's screen height at its main camera distance) is noise. `scripts/check_albedo.py` measures it. Micro-detail (pores, scratches, fabric weave) goes nowhere on third-person assets and only in the normal map on 1P assets.

## 5. Readability tests (run them, don't eyeball)

`scripts/readability.py` renders the asset with a Blender approximation of the target shader (ramp diffuse, single light, flat ambient, team fresnel) against a mid-grey environment at gameplay distances. Pass criteria:

| Test | Pass |
|---|---|
| Silhouette at 30 m (character about 46 px tall at 1080p, 103° hFOV) | The role is identifiable from the black silhouette alone: weapon side, head, stance. |
| Value contrast vs environment (characters) | Mean luminance difference ≥ 0.12 **and** ≤ 25% of silhouette pixels within ±0.05 of the background. |
| Greyscale zones | The three palette zones are separable in a greyscale thumbnail. |
| LOD silhouette (all tiers) | Silhouette IoU between LOD0 and every LOD used at that distance ≥ 0.95 at 10 m and 30 m. This is the competitive-integrity test. |
| Enemy fresnel visible | The upper silhouette shows a continuous red rim at 30 m. |

## 6. Tells that break the look

- **Toy tells:** uniform tube limbs, a tube head with no jaw or brow, floating unconnected parts, saturated primary colors everywhere, no chamfers.
- **Realism tells:** grime, noise, scratches and AO baked into albedo; photo textures; micro-detail on third-person meshes; physically accurate but dark materials that fall under the ambient clamp.
- **Clarity tells:** shadows or LOD swaps that differ by tier, translucent gameplay elements, enemy-red on friendly accents, environment props more saturated than characters.
