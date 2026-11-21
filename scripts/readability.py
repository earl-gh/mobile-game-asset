# Run inside Blender (Cycles, works headless). Gameplay-readability test from references/valorant-style.md §5.
# Renders the asset with an emission-only approximation of VStyle/Lit (ramp diffuse from one light,
# flat ambient, optional enemy fresnel, no PBR, no cast shadows) at the exact pixel size it has on screen
# at gameplay distances, against dark / mid / light environment values. Then it measures value contrast
# and the LOD silhouette match, and writes a contact sheet.
import bpy, math, os, numpy as np
from mathutils import Vector

COLLECTION = "SK_Agent"       # holds the asset; LOD meshes end in _LOD0.._LODn, parts without a suffix are in every LOD
ALBEDO = None                 # image name/path (needs a UV map) - or None to use COLOR_ATTR
COLOR_ATTR = "Col"            # colour attribute fallback when there is no albedo yet; grey if missing
CATEGORY = "character"        # character | weapon | prop | environment  (character -> contrast + fresnel tests)
TEAM = "enemy"                # enemy (red fresnel) | ally (blue) | none
DISTANCES = [10, 30]          # metres (weapon/prop: the distances it's seen at in third person)
SCREEN_H, HFOV, ASPECT = 1080, 103.0, 16 / 9   # Valorant-like PC default; set your game's mobile camera
VIEWS = [0, 90]               # camera azimuths in degrees (0 = front, the -Y side)
BACKGROUNDS = {"dark": 0.18, "mid": 0.40, "light": 0.62}   # sRGB environment values
# (min mean |dL|, max camouflaged share) per background: strict on the typical mid-value play space,
# looser on the extremes, where the shader's fresnel and depth brightening carry the read in-game.
CONTRAST = {"dark": (0.08, 0.40), "mid": (0.12, 0.25), "light": (0.08, 0.40)}
DEPTH = (8, 40, 0.25)         # VStyle/Lit _DepthStart, _DepthEnd, _DepthBrighten
LIGHT_DIR = Vector((0.45, -0.55, 0.70)).normalized()       # main light (toward the light)
RAMP = "0:0.52,0.40:0.56,0.47:0.62,0.53:0.86,0.75:0.97,1:1.0"   # gen_ramp.py 'character' preset
OUT = "//readability"

VFOV = 2 * math.atan(math.tan(math.radians(HFOV) / 2) / ASPECT)
sc = bpy.context.scene
col = bpy.data.collections[COLLECTION]
meshes = [o for o in col.all_objects if o.type == 'MESH' and not o.name.endswith('_COL')]
lods = sorted({o.name.rsplit('_', 1)[1] for o in meshes if '_LOD' in o.name}) or ['LOD0']
shared = [o for o in meshes if '_LOD' not in o.name]
lod_sets = {l: [o for o in meshes if o.name.endswith('_' + l)] + shared for l in lods}
out_dir = bpy.path.abspath(OUT); os.makedirs(out_dir, exist_ok=True)


def bounds(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi


LO, HI = bounds(lod_sets[lods[0]])
CENTER, H = (LO + HI) / 2, max(HI.z - LO.z, 1e-3)
SPAN = max((HI - LO).length, H)


# ---------- preview material: emission = albedo * ramp(N.L) + fresnel ----------
def preview_material():
    m = bpy.data.materials.get('VStylePreview') or bpy.data.materials.new('VStylePreview')
    nt = m.node_tree; N, L = nt.nodes, nt.links; N.clear()
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); L.new(em.outputs[0], out.inputs[0])
    if ALBEDO:
        tex = N.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.get(ALBEDO) or bpy.data.images.load(ALBEDO, check_existing=True)
        alb = tex.outputs['Color']
    else:
        a = N.new('ShaderNodeAttribute'); a.attribute_name = COLOR_ATTR; alb = a.outputs['Color']
        if not any(COLOR_ATTR in o.data.attributes for o in meshes):
            rgb = N.new('ShaderNodeRGB'); rgb.outputs[0].default_value = (0.21, 0.21, 0.21, 1); alb = rgb.outputs[0]
    geo = N.new('ShaderNodeNewGeometry')
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = LIGHT_DIR; L.new(geo.outputs['Normal'], dot.inputs[0])
    remap = N.new('ShaderNodeMath'); remap.operation = 'MULTIPLY_ADD'
    remap.inputs[1].default_value = 0.5; remap.inputs[2].default_value = 0.5; L.new(dot.outputs['Value'], remap.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); cr = ramp.color_ramp
    stops = [(float(u), float(v)) for u, v in (s.split(':') for s in RAMP.split(','))]
    while len(cr.elements) < len(stops):
        cr.elements.new(0.5)
    for e, (u, v) in zip(cr.elements, stops):
        e.position = u; e.color = (v, v, v, 1)
    L.new(remap.outputs[0], ramp.inputs[0])
    lit = N.new('ShaderNodeMix'); lit.data_type = 'RGBA'; lit.blend_type = 'MULTIPLY'; lit.inputs[0].default_value = 1
    L.new(alb, lit.inputs[6]); L.new(ramp.outputs[0], lit.inputs[7])
    color = lit.outputs[2]
    if CATEGORY == 'character' and TEAM != 'none':
        lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
        pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.name = 'FresnelPower'
        L.new(lw.outputs['Facing'], pw.inputs[0])
        sep = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Normal'], sep.inputs[0])
        up = N.new('ShaderNodeMath'); up.operation = 'MULTIPLY_ADD'; up.inputs[1].default_value = 0.5; up.inputs[2].default_value = 0.5
        L.new(sep.outputs['Z'], up.inputs[0])
        upb = N.new('ShaderNodeMath'); upb.operation = 'POWER'; upb.inputs[1].default_value = 1.5; L.new(up.outputs[0], upb.inputs[0])
        rim = N.new('ShaderNodeMath'); rim.operation = 'MULTIPLY'; L.new(pw.outputs[0], rim.inputs[0]); L.new(upb.outputs[0], rim.inputs[1])
        add = N.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'
        add.inputs[7].default_value = (1.6, 0.18, 0.22, 1) if TEAM == 'enemy' else (0.55, 0.7, 1.0, 1)
        L.new(rim.outputs[0], add.inputs[0]); L.new(color, add.inputs[6]); color = add.outputs[2]
    L.new(color, em.inputs['Color'])
    return m


def setup():
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 0; sc.render.film_transparent = True; sc.cycles.filter_width = 1.0
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    if not sc.world:
        sc.world = bpy.data.worlds.new('W')
    sc.world.node_tree.nodes['Background'].inputs[1].default_value = 0
    sc.view_layers[0].material_override = preview_material()
    cam = bpy.data.objects.get('ReadabilityCam')
    if not cam:
        cam = bpy.data.objects.new('ReadabilityCam', bpy.data.cameras.new('ReadabilityCam'))
        sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; sc.camera = cam
    return cam


def shoot(cam, objs, px_h, az, name, fresnel_pow=4.0, brighten=1.0):
    """Render objs so the asset's height spans px_h pixels; return straight RGBA float array (sRGB)."""
    for o in sc.objects:
        if o.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'LIGHT'}:
            o.hide_render = o not in objs
    frame = max(8, int(round(px_h * SPAN / H * 1.25)))
    sc.render.resolution_x = sc.render.resolution_y = frame; sc.render.resolution_percentage = 100
    cam.data.ortho_scale = H * frame / px_h
    a = math.radians(az)
    cam.location = CENTER + Vector((math.sin(a), -math.cos(a), 0.08)) * (SPAN * 4)
    cam.rotation_euler = (CENTER - cam.location).to_track_quat('-Z', 'Y').to_euler()
    pw = sc.view_layers[0].material_override.node_tree.nodes.get('FresnelPower')
    if pw:
        pw.inputs[1].default_value = fresnel_pow
    em = sc.view_layers[0].material_override.node_tree.nodes['Emission']
    em.inputs['Strength'].default_value = brighten if CATEGORY == 'character' else 1.0
    path = os.path.join(out_dir, name + '.png'); sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(path); img.reload()
    px = np.array(img.pixels[:], np.float32).reshape(img.size[1], img.size[0], 4)
    bpy.data.images.remove(img)
    return px


def lum(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def upscale(a, size):
    k = max(1, size // a.shape[0])
    return np.kron(a, np.ones((k, k, 1), np.float32))


cam = setup()
report, cells, ok = [], [], True
for d in DISTANCES:
    px_h = SCREEN_H * H / (2 * d * math.tan(VFOV / 2))
    t = min(1, max(0, (d - DEPTH[0]) / (DEPTH[1] - DEPTH[0])))
    fp, br = 4.0 - 2.0 * t, 1 + DEPTH[2] * t           # the shader widens the fresnel and brightens with distance
    for az in VIEWS:
        base = shoot(cam, lod_sets[lods[0]], px_h, az, f"{lods[0]}_{d}m_{az}", fp, br)
        alpha = base[..., 3] > 0.5
        row = []
        for bname, bv in BACKGROUNDS.items():
            comp = base[..., :3] * base[..., 3:4] + bv * (1 - base[..., 3:4])
            row.append(np.dstack([comp, np.ones(comp.shape[:2])]))
            if CATEGORY == 'character' and alpha.any():
                L = lum(base[..., :3])[alpha]
                diff = float(np.abs(L - bv).mean()); camo = float((np.abs(L - bv) < 0.05).mean())
                mn, mx = CONTRAST[bname]
                passed = diff >= mn and camo <= mx
                ok &= passed
                report.append(f"{'PASS' if passed else 'FAIL'} contrast {d}m az{az} {bname}: mean |dL| {diff:.3f} (>={mn}), camouflaged {camo:.0%} (<={mx:.0%})")
        for lod in lods[1:]:
            other = shoot(cam, lod_sets[lod], px_h, az, f"{lod}_{d}m_{az}", fp, br)[..., 3] > 0.5
            iou = float((alpha & other).sum() / max((alpha | other).sum(), 1))
            passed = iou >= 0.95; ok &= passed
            report.append(f"{'PASS' if passed else 'FAIL'} silhouette {lods[0]} vs {lod} {d}m az{az}: IoU {iou:.3f} (>=0.95)")
        cells.append(row)
    report.append(f"INFO {d}m: asset is {px_h:.0f} px tall on a {SCREEN_H}p screen")

# contact sheet: one row per distance/view, one column per background, nearest-neighbour upscaled
C = 320
sheet_rows = []
for row in cells:
    tiles = []
    for t in row:
        t = upscale(t, C)
        pad = np.ones((C, C, 4), np.float32); pad[..., :3] = t[0, 0, :3]
        h, w = min(C, t.shape[0]), min(C, t.shape[1])
        pad[(C - h) // 2:(C - h) // 2 + h, (C - w) // 2:(C - w) // 2 + w] = t[:h, :w]
        tiles.append(pad)
    sheet_rows.append(np.concatenate(tiles, 1))
sheet = np.concatenate(sheet_rows[::-1], 0)          # Blender images are bottom-up
img = bpy.data.images.new('readability_sheet', sheet.shape[1], sheet.shape[0], alpha=True)
img.pixels.foreach_set(sheet.ravel()); img.filepath_raw = os.path.join(out_dir, 'readability_sheet.png')
img.file_format = 'PNG'; img.save()
sc.view_layers[0].material_override = None
print('\n'.join(report))
print(f"READABILITY: {'PASS' if ok else 'FAIL'}  sheet -> {img.filepath_raw}")
