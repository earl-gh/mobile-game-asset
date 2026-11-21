# Weapon & equipment

A held item is on screen constantly in first person and fills much of the frame. It's the highest-fidelity asset per pixel, and the one place close-up detail is allowed. The same item in third person is tiny. So build **two meshes from one source**.

## Budget

| | LOD0 | LOD1 | LOD2 | Texture |
|---|---|---|---|---|
| 1P view | 7–12k | none | none | 2048 set |
| 3P / world | 1.5–3k | 800 | cull | same set at mip 1–2 |
| Small gadget | 1.5–4k (1P), 600 (3P) | | | 1024 |

- **Texel density:** at least about 2000 px/m on 1P, with the camera-facing side 1.25× and the hidden side 0.75×.
- **Material:** 1, VStyle/Lit Weapon (smoothstep diffuse plus cubemap specular; the Low tier keeps specular).
- **Bones (1P):** one per moving part, plus a root.

## Blockout (most of the work)

1. **Landmarks first:**
   - muzzle, sight line (top of the optic or iron sights), grip, trigger, mag well, stock butt
   - real dimensions from the brief
   - grip angle 15–20° back from vertical
   - the use direction along −Y (it becomes Unity +Z)
2. **The side profile is the design.**
   - Draw the weapon's full side outline as one polygon from the landmarks, then extrude it to the receiver width.
   - Inset and extrude the profile for width changes (handguard narrower than the receiver, mag slimmer than the well).
   - This gives the deliberate, designed outline Valorant weapons have. Never stack cubes.
3. **Shape language:**
   - A boxy receiver with big 45° chamfers on the top edges.
   - A forward sweep: angled front faces, raked mags and handguards.
   - One dominant mass (the receiver) with the barrel, mag and stock as medium forms.
   - Exaggerate the mag, muzzle device and optic by 10–20%.
4. **Negative space:** the trigger guard, the gap between the grip and the mag, the stock's skeleton cutouts, the vent openings in a shroud. These carry the weapon's identity at 3P scale.
5. **1P camera check in clay**, early: a camera at the eye socket, 60–70° FOV, weapon at the view-model position.
   - Lower-right silhouette readable.
   - Top line clean.
   - Sight centered.
   - Nothing intersects the near clip plane.
6. **Moving parts** (bolt, charging handle, folding stock, mag) split and range-tested in clay.
7. **Value plan:**
   - dominant body color 60%
   - secondary (grip, mag, rail) 30%
   - accent 10% on the top or side the player sees in 1P

## Pipeline additions

1. **Sockets:** grip, off-hand grip (IK), eye or sight alignment, muzzle and shell-eject points. Verify them in an ortho screenshot.
2. **Hard-surface mid-poly:**
   - The game mesh comes first. Duplicate it, add a weighted Bevel (2–3 segments, `profile=0.7`) as the bake source, and apply Boolean cuts (vents, knurling, engravings) on the source only.
   - Chamfer class 1 cm, so highlights catch the cubemap.
3. **Game mesh:** round parts facing the camera get 8–16 sides, hidden ones 6. Small add-ons stay floating (not stitched in) for clean shading.
4. **Texture:**
   - Edge wear only on convex edges (2–6 px, toward bare metal).
   - No painted gradient and no AO in the albedo.
   - Micro detail (knurling, text) in the 1P normal map only.
   - Skin zones as contiguous shells, tint IDs in MAER A.
5. **3P mesh from 1P:** delete interiors and hidden faces, 6–8 sides, merge floating details, same UVs. It must pass the silhouette test against 1P at 10 m.
6. **Worn equipment** follows `character.md`; thrown or deployed items follow `prop.md`.

## Pitfalls

- Mesh Compression Off on 1P meshes.
- No transparency in the 1P view: scope glass is opaque with a painted gradient, or a separate mirror-like material only where Riot also uses rendered reflections (scope glass).
- First-person weapons are the only things that may cast realtime shadows (onto the hands).
