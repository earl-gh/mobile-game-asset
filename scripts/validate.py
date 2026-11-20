# Run inside Blender (via Blender MCP code execution). Checks every mesh in COLLECTION
# (or the selection if COLLECTION is None) against the asset's budgets and prints a report.
import bpy, bmesh, math, re

COLLECTION = None            # e.g. "SM_Asset"; None = selected objects
TEX_SIZE = 2048              # px of the texture set the mesh uses
TEXEL_TARGET = 512           # px/m from the Asset Brief
LOD_BUDGETS = {}             # e.g. {"LOD0": 2500, "LOD1": 1250, "LOD2": 500}
MAX_INFLUENCES = 4
MAX_MATERIALS = 1

def objects():
    if COLLECTION:
        return [o for o in bpy.data.collections[COLLECTION].all_objects if o.type == 'MESH']
    return [o for o in bpy.context.selected_objects if o.type == 'MESH']

def check(obj, dg):
    issues, me = [], obj.data
    ev = obj.evaluated_get(dg).to_mesh()
    ev.calc_loop_triangles()
    tris = len(ev.loop_triangles)
    # texel density: px/m from UV area vs world area, per triangle, area-weighted
    td = None
    if ev.uv_layers.active:
        uv = ev.uv_layers.active.data
        mw = obj.matrix_world
        num = den = 0.0
        for t in ev.loop_triangles:
            a, b, c = (mw @ ev.vertices[i].co for i in t.vertices)
            wa = (b - a).cross(c - a).length / 2
            ua, ub, uc = (uv[l].uv for l in t.loops)
            uva = abs((ub.x - ua.x) * (uc.y - ua.y) - (uc.x - ua.x) * (ub.y - ua.y)) / 2
            if wa > 1e-12:
                num += math.sqrt(uva / wa) * TEX_SIZE * wa
                den += wa
        td = num / den if den else 0
        if abs(td - TEXEL_TARGET) > 0.1 * TEXEL_TARGET:
            issues.append(f"texel density {td:.0f} px/m vs target {TEXEL_TARGET}")
    else:
        issues.append("no UV map")
    obj.evaluated_get(dg).to_mesh_clear()

    ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
    if ngons: issues.append(f"{ngons} n-gons")
    bm = bmesh.new(); bm.from_mesh(me)
    nm = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
    degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-8)
    bm.free()
    if nm: issues.append(f"{nm} non-manifold edges")
    if degenerate: issues.append(f"{degenerate} zero-area faces")
    if any(abs(s - 1) > 1e-4 for s in obj.scale): issues.append(f"unapplied scale {tuple(round(s,3) for s in obj.scale)}")
    if any(abs(r) > 1e-4 for r in obj.rotation_euler) and not obj.parent:
        issues.append("unapplied rotation on root mesh")
    mats = len([s for s in obj.material_slots if s.material])
    if mats > MAX_MATERIALS: issues.append(f"{mats} materials (max {MAX_MATERIALS})")

    arm = obj.find_armature()
    if arm:
        deform = {g.index for g in obj.vertex_groups if g.name in arm.data.bones and arm.data.bones[g.name].use_deform}
        over = unnorm = 0
        for v in me.vertices:
            ws = [g.weight for g in v.groups if g.group in deform and g.weight > 1e-4]
            over += len(ws) > MAX_INFLUENCES
            unnorm += bool(ws) and abs(sum(ws) - 1) > 1e-3
        if over: issues.append(f"{over} verts > {MAX_INFLUENCES} influences")
        if unnorm: issues.append(f"{unnorm} verts with unnormalized weights")

    lod = re.search(r"_(LOD\d+)$", obj.name)
    if lod and lod.group(1) in LOD_BUDGETS and tris > LOD_BUDGETS[lod.group(1)]:
        issues.append(f"{tris} tris over {lod.group(1)} budget {LOD_BUDGETS[lod.group(1)]}")
    if not re.match(r"^(SM|SK)_", obj.name) and not obj.name.endswith("_COL"):
        issues.append("name lacks SM_/SK_ prefix")
    return tris, td, mats, issues

dg = bpy.context.evaluated_depsgraph_get()
fails = 0
for o in sorted(objects(), key=lambda o: o.name):
    tris, td, mats, issues = check(o, dg)
    fails += bool(issues)
    tdtxt = f"{td:.0f}px/m" if td is not None else "-"
    print(f"{'FAIL' if issues else 'OK  '} {o.name}: {tris} tris, {mats} mat, {tdtxt}" + ("".join(f"\n     - {i}" for i in issues)))
print(f"VALIDATE: {'PASS' if not fails else f'{fails} object(s) with issues'}")
