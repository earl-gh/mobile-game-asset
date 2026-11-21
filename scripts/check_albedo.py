# Run inside Blender. Checks an albedo against the Valorant surface rules (references/valorant-style.md):
#   1. value range  : no near-black or near-white texels (the ramp shader needs headroom)
#   2. noise budget : high-frequency energy inside UV islands (grime, photo noise, micro-scratches)
#   3. light leak   : painted lighting = albedo darkening that follows AO or a top-down height gradient
# Only texels covered by the mesh's UVs are measured. Prints PASS/FAIL per check.
import bpy, numpy as np

ALBEDO = "T_Asset_A"          # bpy.data.images name, or a file path
MESH = "SM_Asset_LOD0"        # object whose active UV map defines coverage, and whose height drives check 3
AO = None                     # optional baked AO image name/path (for the AO-leak check)
VIEW = "3P"                   # "3P" (third person / world) or "1P" (first-person, close-up allowed more detail)
RES = 512                     # analysis resolution

LIMITS = {"3P": dict(noise=0.005), "1P": dict(noise=0.010)}   # calibrated: flat zones 0.000, visible grime ~0.009
LUM_MIN, LUM_MAX = 0.04, 0.90  # sRGB luminance (0.06–0.85 is the authoring target; this is the hard limit)
LEAK_CORR = 0.10              # leak needs both: albedo changes go with height (noise dilutes this)...
LEAK_AMP = 0.06               # ...and the painted change is visible: sRGB luminance across the asset height


def load(src):
    img = bpy.data.images.get(src) or bpy.data.images.load(src, check_existing=True)
    img = img.copy(); img.scale(RES, RES)
    px = np.empty(RES * RES * 4, np.float32); img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(RES, RES, 4)


def to_srgb(c):
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.clip(c, 0, None), 1 / 2.4) - 0.055)


def raster(obj):
    """Coverage mask and per-texel world height from the UV layout (barycentric rasterisation)."""
    me = obj.data; me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    mw = obj.matrix_world
    zs = np.array([(mw @ v.co).z for v in me.vertices], np.float32)
    cov = np.zeros((RES, RES), bool); hz = np.zeros((RES, RES), np.float32)
    for t in me.loop_triangles:
        p = np.array([uv[l].uv[:] for l in t.loops], np.float32) * RES
        z = zs[list(t.vertices)]
        x0, y0 = np.floor(p.min(0)).astype(int); x1, y1 = np.ceil(p.max(0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, RES - 1), min(y1, RES - 1)
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, ay), (bx, by), (cx, cy) = p
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(d) < 1e-9:
            continue
        w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / d
        w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / d
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        sl = (slice(y0, y1 + 1), slice(x0, x1 + 1))
        cov[sl] |= inside
        hz[sl] = np.where(inside, w0 * z[0] + w1 * z[1] + w2 * z[2], hz[sl])
    return cov, hz


def box(a, r):
    """Mean filter of radius r via integral image."""
    k = 2 * r + 1
    p = np.pad(a, r, mode='edge')
    c = np.cumsum(np.cumsum(p, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)


def mbox(a, m, r):
    """Mean of a over covered texels only (empty UV space never bleeds into the measurement)."""
    w = box(m.astype(np.float32), r)
    return np.where(w > 1e-6, box(a * m, r) / np.maximum(w, 1e-6), 0)


def erode(m, r):
    return box(m.astype(np.float32), r) > 0.999


def corr(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0


alb = load(ALBEDO)
lum = to_srgb(0.2126 * alb[..., 0] + 0.7152 * alb[..., 1] + 0.0722 * alb[..., 2])
cov, hz = raster(bpy.data.objects[MESH])
inner = erode(cov, 2)                       # ignore island borders and padding
results = []

v = lum[inner]
p1, p99 = np.percentile(v, 1), np.percentile(v, 99)
results.append(("value range", LUM_MIN <= p1 and p99 <= LUM_MAX, f"p1 {p1:.3f}  p99 {p99:.3f}  (limits {LUM_MIN}-{LUM_MAX})"))

# zone borders are intended hard steps, not noise: keep texels near strong steps out of both checks
r_hp = max(1, RES // 128)
gy, gx = np.gradient(mbox(lum, cov, 1))
grad = np.hypot(gx, gy)
step = grad > 0.06
hp = lum - mbox(lum, cov, r_hp)
calm = inner & (box(step.astype(np.float32), r_hp + 1) < 1e-6)
noise = float(np.sqrt((hp[calm] ** 2).mean())) if calm.any() else 0.0
results.append(("noise budget", noise <= LIMITS[VIEW]["noise"], f"high-pass RMS {noise:.4f} (max {LIMITS[VIEW]['noise']} for {VIEW})"))

# light leak: inside colour zones, does albedo change *with* height (or with AO)?
# Compare local texel-to-texel changes, not absolute values, so zone layout (dark boots low, light hair high)
# never counts; only gradients painted within a zone do. Steps (zone borders) and island edges are excluded.
sm = lambda a: mbox(a, cov, 2)
def local_slope(field):
    fy, fx = np.gradient(sm(field)); ly, lx = np.gradient(sm(lum))
    m = calm & erode(cov, 4)
    dl = np.concatenate([lx[m], ly[m]]); df = np.concatenate([fx[m], fy[m]])
    c = corr_raw(dl, df)
    k = float((dl * df).sum() / max((df * df).sum(), 1e-12))
    return c, k

def corr_raw(a, b):
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / d) if d > 0 else 0.0

c_z, k_z = local_slope(hz)
amp = k_z * float(hz[cov].max() - hz[cov].min())
msg = f"albedo vs height corr {c_z:+.2f}, painted top-to-bottom change {amp:+.3f}"
ok = not (c_z >= LEAK_CORR and amp >= LEAK_AMP)
if AO:
    ao = load(AO)[..., 0]
    c_ao, k_ao = local_slope(ao)
    ao_amp = k_ao * float(np.ptp(ao[cov]))
    msg += f", albedo vs AO corr {c_ao:+.2f} (change {ao_amp:+.3f})"
    ok = ok and not (c_ao >= LEAK_CORR and ao_amp >= LEAK_AMP)
results.append(("no baked lighting", ok, msg + f" (fails at corr >= {LEAK_CORR} and change >= {LEAK_AMP})"))

for name, passed, info in results:
    print(f"{'PASS' if passed else 'FAIL'} {name}: {info}")
print(f"CHECK_ALBEDO: {'PASS' if all(r[1] for r in results) else 'FAIL'}  ({inner.sum()} texels measured)")
