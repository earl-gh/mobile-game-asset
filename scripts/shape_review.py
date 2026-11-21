# Run inside Blender (Cycles, works headless). Grey-clay review sheet for the blockout and the Shape Gate
# (references/blockout.md §5-6). No color, no texture, no custom shader: shape only.
#
# Sheet layout (3 x 3 tiles):
#   row 1: ortho FRONT | ortho SIDE | ortho TOP          (with the 1.8 m scale figure)
#   row 2: 3/4 front   | 3/4 back   | greyscale value thumbnail (if a `Col` attribute exists)
#   row 3: black silhouette 10 m front | 30 m front | 30 m side   (true game-camera pixel size)
# Prints: bbox, landmark table (empties named LM_*), landmark-pair distances, and silhouette IoU vs COMPARE.
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector

COLLECTION = "SK_Agent"        # the asset (LOD0 parts; objects ending _LOD1.. and _COL are ignored)
COMPARE = None                 # another collection (e.g. a saved copy of the blockout) for silhouette IoU
LANDMARK_PAIRS = []            # e.g. [("LM_crown", "LM_heel"), ("LM_shoulder_L", "LM_shoulder_R")]
SCALE_FIGURE = True            # 1.8 m capsule figure beside the asset in the ortho and 3/4 views
SCREEN_H, HFOV, ASPECT = 1080, 103.0, 16 / 9
OUT = "//shape_review"
TILE = 420

sc = bpy.context.scene
VFOV = 2 * math.atan(math.tan(math.radians(HFOV) / 2) / ASPECT)
out_dir = bpy.path.abspath(OUT); os.makedirs(out_dir, exist_ok=True)


def asset_objs(name):
    return [o for o in bpy.data.collections[name].all_objects if o.type == 'MESH'
            and '_LOD' not in o.name.replace('_LOD0', '') and not o.name.endswith('_COL')]


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


objs = asset_objs(COLLECTION)
LO, HI = bounds(objs)
SIZE = HI - LO
CENTER = (LO + HI) / 2
H = max(SIZE.z, 1e-3)


def scale_figure():
    if bpy.data.objects.get('ShapeReview_Figure'):
        return bpy.data.objects['ShapeReview_Figure']
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=0.12)            # head, 7.5 heads tall
    bmesh.ops.translate(bm, vec=(0, 0, 1.68), verts=bm.verts)
    b2 = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.17, radius2=0.2, depth=1.5)
    bmesh.ops.translate(bm, vec=(0, 0, 0.78), verts=b2['verts'])
    me = bpy.data.meshes.new('ShapeReview_Figure'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('ShapeReview_Figure', me); sc.collection.objects.link(o)
    gap = 0.45 + 0.1 * max(SIZE.x, SIZE.y)
    o.location = (LO.x - gap, HI.y + gap, LO.z)     # beside the asset in front, side and top views
    bpy.context.view_layer.update()
    return o


fig = scale_figure() if SCALE_FIGURE else None

# ---------- render setup ----------
sc.render.engine = 'CYCLES'; sc.cycles.samples = 24; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 2; sc.render.film_transparent = True
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
if not sc.world:
    sc.world = bpy.data.worlds.new('W')
bg = sc.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (0.6, 0.62, 0.66, 1); bg.inputs[1].default_value = 0.6

clay = bpy.data.materials.get('ShapeReviewClay') or bpy.data.materials.new('ShapeReviewClay')
pb = clay.node_tree.nodes['Principled BSDF']
pb.inputs['Base Color'].default_value = (0.42, 0.42, 0.42, 1); pb.inputs['Roughness'].default_value = 0.55

value = bpy.data.materials.get('ShapeReviewValue') or bpy.data.materials.new('ShapeReviewValue')
vn = value.node_tree.nodes; vl = value.node_tree.links
for n in list(vn):
    if n.type not in {'OUTPUT_MATERIAL'}:
        vn.remove(n)
attr = vn.new('ShaderNodeAttribute'); attr.attribute_name = 'Col'
em = vn.new('ShaderNodeEmission'); vl.new(attr.outputs['Color'], em.inputs[0])
vl.new(em.outputs[0], vn['Material Output'].inputs[0])

sil = bpy.data.materials.get('ShapeReviewSil') or bpy.data.materials.new('ShapeReviewSil')
sil.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0, 0, 0, 1)

sun = bpy.data.objects.get('ShapeReviewSun')
if not sun:
    sun = bpy.data.objects.new('ShapeReviewSun', bpy.data.lights.new('ShapeReviewSun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.5; sun.data.angle = math.radians(8)
sun.rotation_euler = (math.radians(50), 0, math.radians(35))

cam = bpy.data.objects.get('ShapeReviewCam')
if not cam:
    cam = bpy.data.objects.new('ShapeReviewCam', bpy.data.cameras.new('ShapeReviewCam')); sc.collection.objects.link(cam)
sc.camera = cam


def shoot(name, visible, mat, direction, ortho_scale=None, lens=None, frame=TILE, target=CENTER, dist=None):
    for o in sc.objects:
        if o.type == 'MESH':
            o.hide_render = o not in visible
    sc.view_layers[0].material_override = mat
    sc.render.resolution_x = sc.render.resolution_y = frame
    d = Vector(direction).normalized()
    span = max(SIZE.length, 0.5)
    if ortho_scale:
        cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho_scale
        cam.location = target + d * span * 4
    else:
        cam.data.type = 'PERSP'; cam.data.lens = lens
        cam.location = target + d * (dist or span * 2.2)
    cam.data.clip_end = span * 20
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    if abs(d.z) > 0.99:
        cam.rotation_euler = (0, 0, 0)
    path = os.path.join(out_dir, name + '.png'); sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path); img.reload()
    px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], 4)
    bpy.data.images.remove(img)
    return px


def mask(bgc, px):
    a = px[..., 3:4]
    rgb = np.array(bgc, np.float32) * (1 - a)
    return np.dstack([rgb, np.ones(rgb.shape[:2], np.float32)])


def on(bgc, px):
    rgb = px[..., :3] * px[..., 3:4] + np.array(bgc, np.float32) * (1 - px[..., 3:4])
    return np.dstack([rgb, np.ones(rgb.shape[:2], np.float32)])


def fit(px, size=TILE):
    """Nearest-neighbour upscale to the tile, centred on the tile's corner colour."""
    k = max(1, size // max(px.shape[:2]))
    px = np.kron(px, np.ones((k, k, 1), np.float32))[:size, :size]
    t = np.ones((size, size, 4), np.float32); t[..., :3] = px[0, 0, :3]
    y, x = (size - px.shape[0]) // 2, (size - px.shape[1]) // 2
    t[y:y + px.shape[0], x:x + px.shape[1]] = px
    return t


def game_px(dist):
    return SCREEN_H * H / (2 * dist * math.tan(VFOV / 2))


def silhouette(objs_, d_m, direction, tag):
    px_h = game_px(d_m)
    frame = max(8, int(round(px_h * max(SIZE.length, H) / H * 1.2)))
    return shoot(tag, objs_, sil, direction, ortho_scale=H * frame / px_h, frame=frame)


view_objs = objs + ([fig] if fig else [])
LO2, HI2 = bounds(view_objs)
C2 = (LO2 + HI2) / 2
ortho = max((HI2 - LO2).x, (HI2 - LO2).y, (HI2 - LO2).z) * 1.12
paper = (0.86, 0.85, 0.82)
tiles = [
    on(paper, shoot('front', view_objs, clay, (0, -1, 0), ortho_scale=ortho, target=C2)),
    on(paper, shoot('side', view_objs, clay, (1, 0, 0), ortho_scale=ortho, target=C2)),
    on(paper, shoot('top', view_objs, clay, (0, 0, 1), ortho_scale=ortho, target=C2)),
    on(paper, shoot('q_front', view_objs, clay, (0.6, -0.75, 0.3), lens=50, target=C2, dist=(HI2 - LO2).length * 2.4)),
    on(paper, shoot('q_back', view_objs, clay, (-0.6, 0.75, 0.3), lens=50, target=C2, dist=(HI2 - LO2).length * 2.4)),
]
if any('Col' in o.data.attributes for o in objs):
    v = shoot('value', objs, value, (0.6, -0.75, 0.3), lens=50, dist=SIZE.length * 2.4)
    g = (0.2126 * v[..., 0] + 0.7152 * v[..., 1] + 0.0722 * v[..., 2])[..., None]
    tiles.append(on((0.5, 0.5, 0.5), np.dstack([g, g, g, v[..., 3:4]])))
else:
    tiles.append(np.ones((TILE, TILE, 4), np.float32) * np.array([*paper, 1], np.float32))
white = (1, 1, 1)
tiles += [fit(mask(white, silhouette(objs, 10, (0, -1, 0), 'sil_10m_front'))),
          fit(mask(white, silhouette(objs, 30, (0, -1, 0), 'sil_30m_front'))),
          fit(mask(white, silhouette(objs, 30, (1, 0, 0), 'sil_30m_side')))]
tiles = [fit(t) if t.shape[0] != TILE else t for t in tiles]
rows = [np.concatenate(tiles[i:i + 3], 1) for i in (0, 3, 6)]
sheet = np.concatenate(rows[::-1], 0)
img = bpy.data.images.new('shape_review_sheet', sheet.shape[1], sheet.shape[0], alpha=True)
img.pixels.foreach_set(sheet.ravel()); img.filepath_raw = os.path.join(out_dir, 'shape_review_sheet.png')
img.file_format = 'PNG'; img.save()

# ---------- numbers ----------
print(f"BBOX  W(x) {SIZE.x:.3f}  D(y) {SIZE.y:.3f}  H(z) {SIZE.z:.3f} m   min z {LO.z:+.3f}")
print(f"SCREEN  {game_px(10):.0f} px tall at 10 m, {game_px(30):.0f} px at 30 m ({SCREEN_H}p, {HFOV:.0f} deg hFOV)")
lms = sorted((o for o in bpy.data.objects if o.name.startswith('LM_')), key=lambda o: o.name)
for o in lms:
    p = o.matrix_world.translation
    print(f"LM  {o.name:<22} x {p.x:+.3f}  y {p.y:+.3f}  z {p.z:+.3f}")
for a, b in LANDMARK_PAIRS:
    pa, pb_ = bpy.data.objects[a].matrix_world.translation, bpy.data.objects[b].matrix_world.translation
    print(f"DIST {a} -> {b}: {(pa - pb_).length:.3f} m")
if COMPARE:
    other = asset_objs(COMPARE)
    for tag, d in (('front', (0, -1, 0)), ('side', (1, 0, 0))):
        allo = objs + other
        lo_, hi_ = bounds(allo); ctr = (lo_ + hi_) / 2; sc_ = max(hi_ - lo_) * 1.1
        a = shoot('cmp_a_' + tag, objs, sil, d, ortho_scale=sc_, frame=256, target=ctr)[..., 3] > 0.5
        b = shoot('cmp_b_' + tag, other, sil, d, ortho_scale=sc_, frame=256, target=ctr)[..., 3] > 0.5
        print(f"IOU  {COLLECTION} vs {COMPARE} {tag}: {(a & b).sum() / max((a | b).sum(), 1):.3f}")
sc.view_layers[0].material_override = None
for o in sc.objects:
    if o.type == 'MESH':
        o.hide_render = False
if fig:
    fig.hide_render = True
print(f"SHAPE_REVIEW sheet -> {img.filepath_raw}")
