# Run inside Blender. Imports a free base model (references/sourcing.md), normalizes it for the blockout,
# and records its provenance. The base is raw material: it still goes through blockout and the Shape Gate.
import bpy, os, math, datetime
from mathutils import Vector, Matrix

FILE = "//bases/wolf.glb"          # .glb .gltf .fbx .obj .blend
NAME = "BASE_Wolf"                 # objects become BASE_<...>; collection of the same name
SOURCE = dict(title="", author="", url="", license="CC0")   # all required except author for CC0
FIT_AXIS = "z"                     # which bbox dimension to match: x | y | z
FIT_SIZE = 0.9                     # metres along FIT_AXIS (e.g. character height, wolf shoulder... use bbox)
FACING = "-Y"                      # direction the base currently faces after import: -Y +Y -X +X (rotated to -Y)
JOIN = False                       # join all meshes into one object
STRIP_MATERIALS = True             # everything gets repainted; drop imported materials and images
SOURCES_MD = "//{asset}_SOURCES.md"

OK_LICENSES = {"CC0", "CC-BY", "CC-BY-4.0", "CC-BY-3.0", "ROYALTY-FREE"}
lic = SOURCE.get("license", "").upper().replace(" ", "")
if not SOURCE.get("url") or not lic:
    raise RuntimeError("import_base: SOURCE needs url and license (see references/sourcing.md)")
if lic not in OK_LICENSES:
    raise RuntimeError(f"import_base: licence '{SOURCE['license']}' is not cleared for commercial game use; "
                     "ask the user (NC / ND / SA / GPL need an explicit decision)")

path = bpy.path.abspath(FILE)
before = set(bpy.data.objects)
ext = os.path.splitext(path)[1].lower()
if ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=path)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=path)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=path)
elif ext == ".blend":
    with bpy.data.libraries.load(path) as (src, dst):
        dst.objects = list(src.objects)
    for o in dst.objects:
        if o:
            bpy.context.scene.collection.objects.link(o)
else:
    raise RuntimeError(f"import_base: unsupported file type {ext}")
new = [o for o in bpy.data.objects if o not in before]
meshes = [o for o in new if o.type == 'MESH']
if not meshes:
    raise RuntimeError("import_base: no meshes imported")

col = bpy.data.collections.get(NAME) or bpy.data.collections.new(NAME)
if col.name not in bpy.context.scene.collection.children:
    bpy.context.scene.collection.children.link(col)
for o in new:
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)

# bake every transform (including importer axis fixes and parent chains) into mesh data
bpy.context.view_layer.update()
for o in meshes:
    mw = o.matrix_world.copy()
    if o.data.users > 1:
        o.data = o.data.copy()
    o.parent = None
    o.data.transform(mw)
    o.matrix_world = Matrix()
for o in new:
    if o.type == 'EMPTY' and not o.children:
        bpy.data.objects.remove(o)
meshes = [o for o in meshes if o.name in bpy.data.objects]

if JOIN and len(meshes) > 1:
    with bpy.context.temp_override(active_object=meshes[0], selected_editable_objects=meshes, selected_objects=meshes):
        bpy.ops.object.join()
    meshes = [meshes[0]]

# face -Y
turn = {"-Y": 0, "+X": -90, "+Y": 180, "-X": 90}[FACING]
R = Matrix.Rotation(math.radians(turn), 4, 'Z')


def bbox(objs):
    pts = [v.co for o in objs for v in o.data.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


for o in meshes:
    o.data.transform(R)
lo, hi = bbox(meshes)
dim = (hi - lo)["xyz".index(FIT_AXIS)]
s = FIT_SIZE / max(dim, 1e-6)
ground = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
M = Matrix.Scale(s, 4) @ Matrix.Translation(-ground)
for o in meshes:
    o.data.transform(M)
    o.data.update()

stamp = datetime.date.today().isoformat()
for i, o in enumerate(meshes):
    o.name = NAME if len(meshes) == 1 else f"{NAME}_{i:02d}"
    if STRIP_MATERIALS:
        o.data.materials.clear()
    for k, v in SOURCE.items():
        o[f"source_{k}"] = v
    o["source_imported"] = stamp
if STRIP_MATERIALS:
    for img in [i for i in bpy.data.images if i.users == 0]:
        bpy.data.images.remove(img)
    for m in [m for m in bpy.data.materials if m.users == 0]:
        bpy.data.materials.remove(m)

lo, hi = bbox(meshes)
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
md = bpy.path.abspath(SOURCES_MD.format(asset=NAME.replace("BASE_", "")))
new_file = not os.path.exists(md)
with open(md, "a") as f:
    if new_file:
        f.write("# Sources\n\n| Part | Title | Author | Licence | URL | Imported | Changes |\n|---|---|---|---|---|---|---|\n")
    f.write(f"| {NAME} | {SOURCE.get('title','')} | {SOURCE.get('author','')} | {SOURCE['license']} | "
            f"{SOURCE['url']} | {stamp} | scaled x{s:.3f}, rotated {turn} deg, materials stripped; restyle pending |\n")
print(f"BASE {NAME}: {len(meshes)} mesh(es), {tris} tris, scale x{s:.3f}, "
      f"bbox W {hi.x-lo.x:.3f} D {hi.y-lo.y:.3f} H {hi.z-lo.z:.3f} m, pivot at ground centre")
print(f"SOURCES -> {md}   licence {SOURCE['license']}"
      + ("  (CC-BY: attribution required in credits)" if lic.startswith("CC-BY") else ""))
