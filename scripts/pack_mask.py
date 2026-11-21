# Run inside Blender. Packs baked images into the VStyle/Lit MAER mask (T_<Asset>_MAER):
#   R = metallic
#   G = AO and emissive share one channel: G < 0.5 encodes AO (0 = fully occluded, 0.5 = open),
#       G > 0.5 encodes emissive strength (0.5 = none, 1 = full). Emissive wins where both exist,
#       because a glowing surface is never occluded in practice.
#   B = roughness (specular strength is derived in the shader as 1 - roughness)
#   A = tint-zone ID for skins: 0 none, 0.25 / 0.5 / 0.75 = zones 1-3
# Each input is a bpy.data.images name, or a float constant.
import bpy, numpy as np

METALLIC = 0.0                 # image name or constant
AO = "T_Asset_AO_bake"         # baked AO, contact/cavity only (no large-scale occlusion: the shader owns light)
EMISSIVE = 0.0                 # image name (white = glowing) or constant
ROUGHNESS = "T_Asset_Rough_bake"
ZONE = 0.0
AO_STRENGTH = 0.6              # keep AO subtle: 1 = as baked, 0 = none
OUT_PATH = "//textures/T_Asset_MAER.png"
SIZE = 2048


def channel(src):
    if isinstance(src, (int, float)):
        return np.full(SIZE * SIZE, float(src), np.float32)
    img = bpy.data.images[src]
    if tuple(img.size) != (SIZE, SIZE):
        img = img.copy(); img.scale(SIZE, SIZE)
    px = np.empty(SIZE * SIZE * 4, np.float32)
    img.pixels.foreach_get(px)
    return px[0::4].copy()     # greyscale bakes: R holds the value


ao = 1.0 - AO_STRENGTH * (1.0 - np.clip(channel(AO), 0, 1))
em = np.clip(channel(EMISSIVE), 0, 1)
g = np.where(em > 1e-3, 0.5 + 0.5 * em, 0.5 * ao)

out = np.empty(SIZE * SIZE * 4, np.float32)
out[0::4] = np.clip(channel(METALLIC), 0, 1)
out[1::4] = g
out[2::4] = np.clip(channel(ROUGHNESS), 0, 1)
out[3::4] = np.clip(channel(ZONE), 0, 1)

name = bpy.path.display_name_from_filepath(OUT_PATH)
if name in bpy.data.images:
    bpy.data.images.remove(bpy.data.images[name])
img = bpy.data.images.new(name, SIZE, SIZE, alpha=True, float_buffer=False)
img.colorspace_settings.name = 'Non-Color'
img.alpha_mode = 'CHANNEL_PACKED'   # keep RGB intact where A is low
img.pixels.foreach_set(out)
img.filepath_raw = OUT_PATH
img.file_format = 'PNG'
img.save()
print(f"PACKED {name} -> {bpy.path.abspath(OUT_PATH)}  emissive px: {(em > 1e-3).mean():.1%}  "
      f"mean AO: {ao.mean():.2f}  mean rough: {out[2::4].mean():.2f}")
