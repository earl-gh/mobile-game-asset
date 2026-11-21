# Sourcing a free base model

Don't start from a default cube or a bare Skin-modifier stick figure when a decent free base exists. A good base gives you correct anatomy, mechanical logic or proportions in minutes. It is **raw material, not the asset**: it still goes through the measured blockout (`blockout.md`), the Valorant shape pass and the Shape Gate. Most bases are realistic or generic, and will need their planes, proportions and silhouette pushed hard.

## 1. When to use a base

| Situation | Use a base? |
|---|---|
| Human character | **Yes.** Body base for anatomy and proportions, then restyle. |
| Animal or creature | **Yes**, if a real animal is close (wolf, big cat, lizard, bird). Use it for the skeleton, girdles and limb proportions. |
| Real-world vehicle or weapon type | **Yes**, as a proportion and mechanical reference (wheel placement, receiver layout). Usually rebuilt as a side-profile extrusion over it. |
| Common prop (crate, barrel, chair) | Optional. Often faster to block out directly, since a chamfered profile takes minutes. |
| Modular environment kit | Rarely. Kits must fit your grid and metrics. Use free kits for grey-boxing only. |
| Fantasy or unique design with no real analogue | Use parts (a horn, a hand, a skull) and kitbash, or block out from scratch. |

## 2. Where to look (free sources)

Check each asset's own licence on its page. Sites mix licences, and terms change.

| Source | Typical licence | Good for |
|---|---|---|
| Poly Haven (polyhaven.com) | CC0 | Props, HDRIs, materials. Blender MCP often has a built-in Poly Haven search and download. |
| Sketchfab (sketchfab.com), filter "Downloadable" | Per model: CC0, CC-BY, CC-BY-SA, CC-BY-NC… | Widest range: creatures, vehicles, weapons, characters. Some Blender MCP servers have a Sketchfab search and download (needs a Sketchfab API key). |
| Quaternius (quaternius.com) | CC0 | Stylized low-poly characters, animals, weapons, vehicles. Good proportion bases. |
| Kenney (kenney.nl) | CC0 | Props and modular kits for grey-boxing |
| Poly Pizza (poly.pizza) | CC0 / CC-BY per model | Low-poly bases |
| OpenGameArt (opengameart.org) | Mixed (CC0, CC-BY, GPL…) | Game-ready odds and ends |
| Smithsonian 3D (3d.si.edu), filter CC0 | CC0 | Real animal skulls and skeletons, artifacts: anatomy reference for creatures |
| NASA 3D Resources | Free use with NASA terms | Vehicles and equipment reference |
| MakeHuman / MPFB2 (Blender add-on) | CC0 output | Human base meshes at any build, with a game-friendly topology option |
| BlenderKit (free tier) | Royalty-free, see their licence | Props, characters, materials |
| Mixamo (Adobe account) | Adobe terms, free for use in games | Rig and animation testing; a base for humanoid proportions |

## 3. Licence rules (non-negotiable)

- **Allowed for commercial games:** CC0, CC-BY (with attribution), and royalty-free licences that permit use in games.
- **Avoid:**
  - NC (non-commercial), unless the user confirms the project is non-commercial.
  - ND (no-derivatives): you will modify it.
  - CC-BY-SA, unless the user accepts share-alike terms.
  - GPL models: copyleft terms on game content are a legal question for the user.
- **Never use ripped, extracted or "fan-uploaded" assets from commercial games**, including Valorant. That includes anything titled like a real game's character, weapon or skin. The skill teaches the *design language*, not the assets.
- **Record provenance for every base and every kitbashed part:** name, author, URL, licence, date, and what you changed. `scripts/import_base.py` stores it on the objects and appends it to `<Asset>_SOURCES.md`. CC-BY attribution goes into the hand-off.
- If you can't determine the licence, don't use the asset.

## 4. Getting the file

1. **With Blender MCP:** use its asset tools if present (Poly Haven, Sketchfab and similar search and download). Prefer glTF/GLB, then FBX, then OBJ.
2. **Without them:** search the sites above. If this environment's network blocks a site, give the user the exact links and ask them to download the files into the project. Don't substitute a made-up model.
3. **Pick by shape, not looks:**
   - correct proportions and joint placement for the brief
   - clean, separable parts
   - a sensible polycount (5–100k)
   - no baked-in pose that fights an A-pose or rest pose

   Ignore textures: they get replaced.

## 5. Bringing it in (`scripts/import_base.py`)

The script:
1. imports glTF, GLB, FBX, OBJ or `.blend`
2. applies transforms
3. joins (optional)
4. rotates the base so it faces −Y
5. scales it to the brief's target dimension
6. puts the pivot at the ground contact center
7. strips materials and images (we repaint everything)
8. tags the objects with provenance
9. prints the measured bbox

Then the base enters the **blockout** as the source for pass 1b:
- **Characters and creatures:**
  - Snap the brief's landmark empties onto the base, then compare its ratios to the brief's proportion sheet (7–7.5 heads, heroic shoulders, oversized hands).
  - Fix the differences with lattice or proportional edits, or rebuild the volumes over it with the Skin-modifier method while using the base as the guide.
  - Retopo stays mandatory.
- **Hard surface:** trace the side profile over the base, then extrude your own designed outline. Delete the base afterwards, or keep it hidden as reference.
- **Kitbash parts:** each part gets the same chamfer class and planar restyle as the rest, so it doesn't look pasted on.

The Shape Gate still decides. A base that looks "realistic and fine" usually fails items 3, 5 and 6 (hierarchy, gesture, planes) until it has been restyled.
