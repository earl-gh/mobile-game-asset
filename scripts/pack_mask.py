# Run inside Blender. Packs baked images into the URP Lit mask texture:
# R = metallic, G = AO, B = zone ID (skin/tint zones, else 0), A = smoothness (1 - roughness).
# Each input is a bpy.data.images name, or a float constant.
import bpy, numpy as np

METALLIC = 0.0               # image name or constant
AO = "T_Asset_AO_bake"
ZONE = 0.0
ROUGHNESS = "T_Asset_Rough_bake"
OUT_PATH = "//textures/T_Asset_M.png"
SIZE = 2048

def channel(src):
    if isinstance(src, (int, float)):
        return np.full(SIZE * SIZE, float(src), np.float32)
    img = bpy.data.images[src]
    if tuple(img.size) != (SIZE, SIZE):
        img = img.copy(); img.scale(SIZE, SIZE)
    px = np.empty(SIZE * SIZE * 4, np.float32)
    img.pixels.foreach_get(px)
    return px[0::4].copy()   # bakes are greyscale; R holds the value

out = np.empty(SIZE * SIZE * 4, np.float32)
out[0::4], out[1::4], out[2::4] = channel(METALLIC), channel(AO), channel(ZONE)
out[3::4] = 1.0 - channel(ROUGHNESS)

name = bpy.path.display_name_from_filepath(OUT_PATH)
if name in bpy.data.images:
    bpy.data.images.remove(bpy.data.images[name])
img = bpy.data.images.new(name, SIZE, SIZE, alpha=True)
img.colorspace_settings.name = 'Non-Color'
img.alpha_mode = 'CHANNEL_PACKED'   # keep RGB intact where A is low
img.pixels.foreach_set(out)
img.filepath_raw = OUT_PATH
img.file_format = 'PNG'
img.save()
print(f"PACKED {name} -> {bpy.path.abspath(OUT_PATH)}")
