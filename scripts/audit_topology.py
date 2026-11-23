# Run inside Blender (code execution) or headless: python audit_topology.py [file.blend] [COLLECTION]
# Audits topology of every mesh in COLLECTION (or the selection; all meshes if nothing is selected):
# face mix, poles, defects, intersections, buried faces. Prints a report plus ranked ERROR/ADVISORY findings.
# Never edits geometry; a trailing Triangulate modifier is switched off while evaluating and restored in `finally`.
import bpy, bmesh, sys, math, fnmatch, re
from collections import Counter
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

COLLECTION = None            # e.g. "SK_Stalker"; None = selection
PATTERN = None               # optional fnmatch filter on object names, e.g. "*_LOD0"
CLASSES = {}                 # first matching pattern wins: {"HI_*": "static", "SK_*Prop*": "rigid", "SK_*": "deforming"}
SPLIT_ISLANDS = True         # treat each loose shell of a joined mesh as its own body for intersections / buried faces
DUP_TOL = 1e-5               # m, duplicate-vertex distance
ZERO_AREA = 1e-8             # m^2
THIN_ASPECT = 8.0            # triangle longest edge / altitude on that edge (equilateral = 1.15)
BURY_OFFSET = 1e-3           # m, shift along the normal before the inside test
MIN_TRI_PAIRS = 3            # overlapping triangle pairs needed to call two bodies "intersecting"
# verdict thresholds
BURIED_ERR_PCT = 10          # buried tris / object tris
BURIED_ADV_PCT = 3
BURIED_REMOVED_PCT = 1       # rigid part below this counts as "buried faces already removed"
MAX_DEFORM_PAIRS = 3         # intersecting pairs touching a deforming body tolerated before ERROR
MAX_IRREGULAR_PCT = 25       # deforming parts
MAX_THIN_PCT = 5
MAX_EDGE_CV = 0.6
TOP = 8                      # rows in "top offenders" lists

RAY = Vector((0.577, 0.5773, 0.5775)).normalized()   # oblique, avoids grazing axis-aligned edges

def objects():
    if COLLECTION:
        objs = [o for o in bpy.data.collections[COLLECTION].all_objects if o.type == 'MESH']
    else:
        objs = [o for o in bpy.context.selected_objects if o.type == 'MESH'] or \
               [o for o in bpy.context.scene.objects if o.type == 'MESH']
    return sorted((o for o in objs if not PATTERN or fnmatch.fnmatch(o.name, PATTERN)), key=lambda o: o.name)

def classify(o):
    for pat, cls in CLASSES.items():
        if fnmatch.fnmatch(o.name, pat):
            return cls
    return 'deforming' if o.find_armature() or any(m.type == 'ARMATURE' for m in o.modifiers) or o.vertex_groups else 'rigid'

def world_bmesh(obj):
    """bmesh copy of the evaluated mesh in world space, without a trailing Triangulate."""
    tail = []
    for m in reversed(obj.modifiers):
        if m.type != 'TRIANGULATE': break
        tail.append((m, m.show_viewport)); m.show_viewport = False
    try:
        bpy.context.view_layer.update()
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me = ev.to_mesh()
        bm = bmesh.new(); bm.from_mesh(me)
        ev.to_mesh_clear()
    finally:
        for m, v in tail: m.show_viewport = v
    bm.transform(obj.matrix_world); bm.normal_update()
    bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); bm.faces.index_update()
    return bm

def shells(bm):
    seen, out = set(), []
    for f in bm.faces:
        if f in seen: continue
        seen.add(f); stack, grp = [f], []
        while stack:
            x = stack.pop(); grp.append(x)
            for e in x.edges:
                for n in e.link_faces:
                    if n not in seen: seen.add(n); stack.append(n)
        out.append(grp)
    return out

def mesh_stats(obj, bm):
    faces = Counter(min(len(f.verts), 5) for f in bm.faces)   # 3 tri, 4 quad, 5 n-gon
    nt, nq, ng = faces[3], faces[4], faces[5]
    ref = 4 if nq >= nt else 6                                # regular valence of a quad- vs tri-dominant mesh
    inner = [v for v in bm.verts if v.link_faces and not v.is_boundary]
    hist = Counter(len(v.link_edges) for v in inner)
    irregular = sum(c for k, c in hist.items() if k != ref)
    worst = max(inner, key=lambda v: abs(len(v.link_edges) - ref), default=None)
    kd = kdtree.KDTree(len(bm.verts))
    for v in bm.verts: kd.insert(v.co, v.index)
    kd.balance()
    dups = sum(1 for v in bm.verts if any(i < v.index for _, i, _ in kd.find_range(v.co, DUP_TOL)))
    thin = 0
    for f in bm.faces:
        if len(f.verts) == 3:
            L = max(e.calc_length() for e in f.edges); A = f.calc_area()
            thin += A < 1e-12 or L * L / (2 * A) > THIN_ASPECT
    lens = [e.calc_length() for e in bm.edges]
    mean = sum(lens) / len(lens) if lens else 0
    cv = (sum((l - mean) ** 2 for l in lens) / len(lens)) ** .5 / mean if mean else 0
    dl = bm.verts.layers.deform.active
    wgroup = None
    if worst and dl and worst[dl]:
        wgroup = obj.vertex_groups[max(worst[dl].items(), key=lambda kv: kv[1])[0]].name
    return dict(
        tri=nt, quad=nq, ngon=ng, tris=sum(len(f.verts) - 2 for f in bm.faces), ref=ref, hist=hist,
        irregular_pct=100 * irregular / max(1, sum(hist.values())),
        low=hist[ref - 1], high=sum(c for k, c in hist.items() if k > ref),
        severe=sum(c for k, c in hist.items() if k >= ref + 2),
        worst=(len(worst.link_edges), tuple(round(x, 3) for x in worst.co), wgroup) if worst else None,
        nonmanifold=sum(1 for e in bm.edges if len(e.link_faces) > 2),
        boundary=sum(1 for e in bm.edges if len(e.link_faces) == 1),
        loose_v=sum(1 for v in bm.verts if not v.link_edges), loose_e=sum(1 for e in bm.edges if not e.link_faces),
        zero=sum(1 for f in bm.faces if f.calc_area() < ZERO_AREA), dups=dups, thin=thin, thin_pct=100 * thin / max(1, nt),
        cv=cv)

def make_bodies(obj, bm, cls):
    groups = shells(bm) if SPLIT_ISLANDS else [list(bm.faces)]
    tri_of = {}
    for t in bm.calc_loop_triangles(): tri_of.setdefault(t[0].face.index, []).append([l.vert.index for l in t])
    coords, dl, bodies = [v.co.copy() for v in bm.verts], bm.verts.layers.deform.active, []
    for k, grp in enumerate(groups):
        tris = [t for f in grp for t in tri_of[f.index]]
        w = Counter()
        if dl:
            for f in grp:
                for v in f.verts:
                    for g, x in v[dl].items(): w[obj.vertex_groups[g].name] += x
        pts = [v.co for f in grp for v in f.verts]
        c = sum(pts, Vector()) / len(pts)   # centre in the label so shells of a joined mesh can be found in the viewport
        label = obj.name if len(groups) == 1 else f"{obj.name}#{k}" + (f"({w.most_common(1)[0][0]}" if w else "(") + f" @{c.x:.2f},{c.y:.2f},{c.z:.2f})"
        bodies.append(dict(
            name=label, obj=obj, cls=cls, faces=grp, tris=sum(len(f.verts) - 2 for f in grp),
            ntri=sum(len(f.verts) == 3 for f in grp), nquad=sum(len(f.verts) == 4 for f in grp), nngon=sum(len(f.verts) > 4 for f in grp),
            closed=all(len(e.link_faces) == 2 for f in grp for e in f.edges),
            lo=Vector(map(min, zip(*pts))), hi=Vector(map(max, zip(*pts))),
            bvh=BVHTree.FromPolygons(coords, tris, all_triangles=True), buried=0, buried_tris=0))
    return bodies

def inside(p, bvh):
    n, o = 0, p
    for _ in range(40):
        loc = bvh.ray_cast(o, RAY)[0]
        if loc is None: break
        n += 1; o = loc + RAY * 1e-5
    return n % 2 == 1

def comparable(a, b):
    """Different LODs of one asset sit on top of each other by design: never compare them."""
    stem = lambda o: re.sub(r"_LOD\d+$", "", o.name)
    return a is not b and not (a["obj"] is not b["obj"] and stem(a["obj"]) == stem(b["obj"]))

def boxes_touch(a, b):
    return all(a['lo'][i] <= b['hi'][i] and b['lo'][i] <= a['hi'][i] for i in range(3))

def intersections(bodies):
    out = []
    for i, a in enumerate(bodies):
        for b in bodies[i + 1:]:
            if comparable(a, b) and boxes_touch(a, b):
                n = len(a['bvh'].overlap(b['bvh']))
                if n >= MIN_TRI_PAIRS: out.append((n, a, b))
    return sorted(out, key=lambda x: -x[0])

def bury(bodies):
    """Count faces whose (normal-offset) centroid is inside another CLOSED body. Parity test, other bodies only."""
    for a in bodies:
        for f in a['faces']:
            p = f.calc_center_median() + f.normal * BURY_OFFSET
            if any(comparable(a, b) and b["closed"] and all(b['lo'][k] <= p[k] <= b['hi'][k] for k in range(3)) and inside(p, b['bvh'])
                   for b in bodies):
                a['buried'] += 1; a['buried_tris'] += len(f.verts) - 2

def audit(collection=None, pattern=None):
    global COLLECTION, PATTERN
    COLLECTION = collection if collection is not None else COLLECTION
    PATTERN = pattern if pattern is not None else PATTERN
    objs, stats, bodies, bms = objects(), {}, [], []
    if not objs: print("AUDIT: no mesh objects"); return
    for o in objs:
        bm = world_bmesh(o); bms.append(bm)
        stats[o.name] = dict(cls=classify(o), **mesh_stats(o, bm))
        bodies += make_bodies(o, bm, stats[o.name]['cls'])
    pairs = intersections(bodies); bury(bodies)
    F = []                                                                # (severity, score, text)
    def add(sev, score, text): F.append((sev, score, text))

    for o in objs:
        s = stats[o.name]; mine = [b for b in bodies if b['obj'] is o]
        s['buried_tris'] = sum(b['buried_tris'] for b in mine); s['buried_pct'] = 100 * s['buried_tris'] / max(1, s['tris'])
        h = " ".join(f"{k}:{v}" for k, v in sorted(s['hist'].items()) if k < 10) + (f" 10+:{sum(v for k, v in s['hist'].items() if k >= 10)}" if any(k >= 10 for k in s['hist']) else "")
        print(f"\n{o.name} [{s['cls']}] {s['tris']} tris-equiv | faces tri {s['tri']} / quad {s['quad']} / ngon {s['ngon']}"
              f" (tri:quad {s['tri'] / max(1, s['quad']):.2f}) | {len(mine)} shell(s)")
        print(f"   valence {h} | poles v{s['ref'] - 1}: {s['low']}, v>{s['ref']}: {s['high']} (v>={s['ref'] + 2}: {s['severe']}),"
              f" irregular {s['irregular_pct']:.0f}% | worst pole {s['worst']}")
        print(f"   non-manifold {s['nonmanifold']} | boundary edges {s['boundary']} | loose v/e {s['loose_v']}/{s['loose_e']} | zero-area {s['zero']}"
              f" | dup verts {s['dups']} | thin tris {s['thin']} ({s['thin_pct']:.0f}%) | edge CV {s['cv']:.2f}"
              f" | buried {sum(b['buried'] for b in mine)} faces = {s['buried_tris']} tris ({s['buried_pct']:.1f}%)")
        for k, txt in (('nonmanifold', "non-manifold edges (3+ faces on an edge)"), ('loose_v', "loose vertices"), ('loose_e', "loose edges"),
                       ('zero', "zero-area faces"), ('dups', "duplicate vertices")):
            if s[k]: add('ERROR', 50, f"{o.name}: {s[k]} {txt}")
        if s['severe']: add('ERROR', 80 + s['severe'], f"{o.name}: {s['severe']} pole(s) of valence >= {s['ref'] + 2}, worst {s['worst'][0]} at {s['worst'][1]} {s['worst'][2] or ''}: star-shaped, shades and deforms badly")
        if s['cls'] == 'deforming':
            if s['ngon']: add('ERROR', 70, f"{o.name}: {s['ngon']} n-gons on a deforming mesh (unpredictable triangulation under skinning)")
            if s['tri'] > 0.2 * max(1, s['tri'] + s['quad']): add('ADVISORY', 30, f"{o.name}: {100 * s['tri'] / (s['tri'] + s['quad']):.0f}% of faces are triangles on a deforming mesh (joints/bends want quad loops)")
            if s['irregular_pct'] > MAX_IRREGULAR_PCT: add('ADVISORY', 25, f"{o.name}: {s['irregular_pct']:.0f}% irregular vertices on a deforming mesh (poles away from joints are fine, in bends they pinch)")
        if s['thin_pct'] > MAX_THIN_PCT: add('ADVISORY', 20, f"{o.name}: {s['thin']} long thin triangles (aspect > {THIN_ASPECT:g}), shading and skinning artifacts")
        if s['cv'] > MAX_EDGE_CV: add('ADVISORY', 10, f"{o.name}: edge-length variation {s['cv']:.2f} (uneven density, texel and deformation inconsistency)")
        if s['buried_pct'] > BURIED_ERR_PCT: add('ERROR', 60 + s['buried_pct'] / 10, f"{o.name}: {s['buried_tris']} tris ({s['buried_pct']:.0f}%) buried inside other bodies: wasted budget, delete them")
        elif s['buried_pct'] > BURIED_ADV_PCT: add('ADVISORY', 40 + s['buried_pct'], f"{o.name}: {s['buried_tris']} tris ({s['buried_pct']:.1f}%) buried inside other bodies")

    total = sum(n for n, _, _ in pairs)
    print(f"\nINTERSECTIONS: {len(pairs)} body pair(s), {total} overlapping triangle pairs (pairs under {MIN_TRI_PAIRS} ignored)")
    for n, a, b in pairs[:TOP]: print(f"   {n:5d}  {a['name']} [{a['cls']}] x {b['name']} [{b['cls']}]")
    deform_p = [p for p in pairs if 'deforming' in (p[1]['cls'], p[2]['cls'])]
    rigid_p = [p for p in pairs if 'deforming' not in (p[1]['cls'], p[2]['cls']) and 'static' not in (p[1]['cls'], p[2]['cls'])
               and max(stats[p[1]['obj'].name]['buried_pct'], stats[p[2]['obj'].name]['buried_pct']) > BURIED_REMOVED_PCT]
    if deform_p: add('ERROR' if len(deform_p) > MAX_DEFORM_PAIRS else 'ADVISORY', 55 + len(deform_p),
                     f"{len(deform_p)} intersecting pair(s) involve deforming parts ({sum(p[0] for p in deform_p)} tri pairs), worst {deform_p[0][1]['name']} x {deform_p[0][2]['name']}: shells slide through each other when posed")
    if rigid_p: add('ADVISORY', 35 + len(rigid_p), f"{len(rigid_p)} intersecting rigid pair(s) whose buried faces were not removed, worst {rigid_p[0][1]['name']} x {rigid_p[0][2]['name']}")

    allt = sum(s['tris'] for s in stats.values()); bt = sum(s['buried_tris'] for s in stats.values())
    print(f"\nBURIED FACES: {bt} of {allt} tris ({100 * bt / max(1, allt):.1f}%) lie inside another closed body")
    for b in sorted(bodies, key=lambda b: -b['buried_tris'])[:TOP]:
        if b['buried_tris']: print(f"   {b['buried_tris']:5d} tris ({100 * b['buried_tris'] / b['tris']:.0f}% of body)  {b['name']}")
    if SPLIT_ISLANDS and len(bodies) > len(objs):
        print(f"\nSHELLS (largest {TOP}): name tris | tri/quad/ngon | closed")
        for b in sorted(bodies, key=lambda b: -b['tris'])[:TOP]: print(f"   {b['tris']:5d}  {b['ntri']}/{b['nquad']}/{b['nngon']}  {'closed' if b['closed'] else 'OPEN'}  {b['name']}")
    open_n = sum(not b['closed'] for b in bodies)
    if open_n: print(f"   note: {open_n} open shell(s) cannot act as containers, so buried counts are a lower bound")

    F.sort(key=lambda f: (f[0] != 'ERROR', -f[1]))
    print("\nFINDINGS (errors must be fixed, advisories are judgement calls):")
    for sev, _, text in F: print(f"   {sev:8s} {text}")
    n_err = sum(f[0] == 'ERROR' for f in F)
    print(f"AUDIT: {n_err} error(s), {len(F) - n_err} advisory(ies) over {len(objs)} object(s), {allt} tris")
    for bm in bms: bm.free()
    return dict(stats=stats, bodies=bodies, pairs=pairs, findings=F)

if __name__ != "audit_topology":      # importing it as a module (tests) does not auto-run
    blends = [a for a in sys.argv[1:] if a.lower().endswith(".blend")]
    if blends and bpy.data.filepath.replace("\\", "/") != blends[0].replace("\\", "/"): bpy.ops.wm.open_mainfile(filepath=blends[0])
    rest = [a for a in sys.argv[1:] if not a.lower().endswith(".blend")]
    audit(rest[0] if rest and rest[0] in bpy.data.collections else None)
