# The light layer: VStyle/Lit

The Valorant look is mostly a lighting model, so the skill ships one: `unity/VStyleLit.shader` (URP, forward), plus three small components. Every technique below is from Riot's article [VALORANT Shaders and Gameplay Clarity](https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity) unless marked [House].

**Honest status:** the shader was written against the URP 17 (Unity 6) ShaderLibrary API and has not been compiled inside this skill. On first use:
1. Import it.
2. Fix any API drift the console reports.
3. Read the per-tier instruction counts (Inspector → Compiled code).
4. Record them in the hand-off.

## What each part does

| Feature | Riot's technique | VStyle/Lit implementation | What the asset must provide |
|---|---|---|---|
| **Diffuse** | "Gradient Lambert": one light, N·L remapped to 0..1, then a lookup in an artist ramp that controls highlight, mid tone, core shadow and where the transitions sit | `_DiffuseRamp` sampled at N·L·0.5+0.5 | `T_<Asset>_RampDiffuse` from `scripts/gen_ramp.py` |
| **Weapon diffuse** | Older styling: smoothstep on N·L | `_CATEGORY_WEAPON`: smoothstep(lo, hi, N·L) with a shadow floor | nothing extra |
| **Environment diffuse** | Offline lightmaps (many lights, shadows) | `_CATEGORY_ENVIRONMENT` with `LIGHTMAP_ON` → URP lightmap | UV2 (lightmap UVs) on static pieces |
| **Specular** | Panoramic HDR only, roughness → blurred mip, painted hotspots aligned with the key light; spec strength = inverted roughness | `GlossyEnvironmentReflection` × (1 − roughness) × F0 | MAER B (roughness). The scene needs reflection probes or a sky cubemap with a hotspot painted toward the main light. |
| **Ambient** | Light-probe sample per object, scales diffuse and specular separately, clamped min/max per map area | SH luminance clamped to `_AmbientMin/_AmbientMax`; specular darkens faster in shade | nothing. `VStyleAmbientZone` sets the clamp per area. |
| **Team fresnel** | Red for enemies, neutral blue for allies, prefers up-facing grazing angles and the upper body | rim × up-bias × height ramp × `_FresnelColor` | correct pivot at the feet, +Y up (height ramp uses object Y) |
| **Skin** | Redder diffuse falloff, plus a wax-like underglow stronger in shade, masked by vertex color | `_SkinRamp` blended by vertex color R, underglow × shade | vertex color R = 1 on skin, 0 elsewhere; `T_<Asset>_RampSkin` |
| **Depth adjust** | Far characters brightened, fresnel larger, both clamped | `_DepthStart/_DepthEnd/_DepthBrighten`, fresnel power lerps near→far | nothing |
| **Emissive** | AO and emissive packed in one channel (< 0.5 AO, > 0.5 emissive) | MAER G decode | MAER G from `pack_mask.py` |
| **Tint zones** | [House] skins recolor without new albedos | MAER A: 0.25 / 0.5 / 0.75 → `_ZoneTint1..3` | MAER A |
| **Cast shadows** | Only first-person hands and weapon cast shadows | `VStyleCharacter` sets Cast Shadows Off unless `firstPerson` | flag on the prefab |

## Tiers: drop instructions, keep gameplay

**[Riot]** On Low, environment objects keep *either* diffuse or specular, characters drop specular, and weapons drop diffuse. Riot's counts: environment 100 → 41, characters 128 → 84, weapons 103 → 73 instructions.

VStyle/Lit does the same under the global keyword `_VSTYLE_TIER_LOW`, set by `VStyleQuality`:

| Category | Low tier removes | Always kept |
|---|---|---|
| Character | specular | ramp diffuse, skin, fresnel, depth brightening, emissive |
| Weapon | ramp diffuse (flat ambient fill) | specular, emissive |
| Environment / prop | specular, or diffuse if `_EnvLowKeepSpecular` | lightmap or ramp, emissive |

**Never tie gameplay to a tier:** fresnel, emissive cues, silhouettes and shadow visibility are identical on all tiers.

## Material setup checklist (per asset)

1. Shader `VStyle/Lit`, set the Category (Character, Weapon, Environment or Prop).
2. Textures:
   - Albedo `T_*_A` (sRGB)
   - MAER `T_*_MAER` (**sRGB off**)
   - Normal `T_*_N` (Normal map type)
   - Ramps (**sRGB off**, Clamp, no mips, no compression)
3. Characters: tune `_FresnelHeight` to the character's height, check the skin vertex colors imported (FBX `colors_type='LINEAR'`), and add `VStyleCharacter` to the prefab root.
4. Tune the ramp, not the albedo, when the core shadow looks wrong.
5. Verify in a lit test scene at 10 m and 30 m, with an ally and an enemy copy, on the High and Low quality levels. Screenshot both.

## Mobile notes [House]

- On tile-based mobile GPUs, alpha-clip disables early depth rejection. VStyle/Lit is opaque-only by design. Model thin shapes as geometry.
- One shader for all categories, using `shader_feature_local`, keeps the variant count small: 4 categories × 2 tiers × lightmap on/off. Strip unused categories in the build.
- The pass list reuses URP Lit's ShadowCaster, DepthOnly, DepthNormals and Meta passes. They work, but they make the material incompatible with the SRP Batcher. If profiling shows batching cost, copy those passes into the file with VStyle/Lit's own `UnityPerMaterial` buffer.
