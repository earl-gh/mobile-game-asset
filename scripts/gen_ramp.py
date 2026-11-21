# Standalone (plain Python 3, no Blender needed). Writes the diffuse ramp textures that VStyle/Lit
# samples with N·L remapped to 0..1 (Riot's "Gradient Lambert"). The artist controls the brightness of
# the core shadow, mid tone and highlight, and where the transitions between them sit.
#
#   python scripts/gen_ramp.py --preset character --out textures/T_Agent_RampDiffuse.png
#   python scripts/gen_ramp.py --stops "0:0.50,0.42:0.56,0.50:0.86,0.72:0.96,1:1.0" --out T_X_RampDiffuse.png
#
# Stops are "u:value" or "u:r/g/b" (linear, 0..1). Import in Unity with sRGB OFF, Wrap Clamp,
# Filter Bilinear, no mipmaps, no compression (it's 256x4).
import argparse, struct, zlib

PRESETS = {
    # u = N·L*0.5+0.5. 0.5 = terminator. A narrow step at the terminator gives the painted core-shadow edge;
    # the shadow side never drops below ~0.5 so nothing goes black (Valorant's diffuse "doesn't go to complete black").
    "character": "0:0.52,0.40:0.56,0.47:0.62,0.53:0.86,0.75:0.97,1:1.0",
    # Same shape, core shadow pushed warm and red (Riot: "more red in darker areas" for skin).
    "skin": "0:0.58/0.42/0.40,0.40:0.62/0.46/0.43,0.47:0.70/0.55/0.50,0.53:0.90/0.84/0.80,0.75:0.98/0.96/0.94,1:1.0/1.0/1.0",
    # Props and dynamic environment objects: softer, lower contrast so they sit behind characters.
    "prop": "0:0.60,0.45:0.66,0.55:0.85,1:0.98",
    # Debug: plain half-Lambert, for comparing against the styled ramps.
    "halflambert": "0:0.0,1:1.0",
}


def parse(stops):
    out = []
    for s in stops.split(','):
        u, v = s.split(':')
        c = [float(x) for x in v.split('/')]
        out.append((float(u), c * 3 if len(c) == 1 else c))
    return sorted(out)


def sample(stops, u):
    if u <= stops[0][0]:
        return stops[0][1]
    for (u0, c0), (u1, c1) in zip(stops, stops[1:]):
        if u <= u1:
            t = (u - u0) / max(u1 - u0, 1e-6)
            t = t * t * (3 - 2 * t)                     # smooth between stops, no linear kinks
            return [a + (b - a) * t for a, b in zip(c0, c1)]
    return stops[-1][1]


def write_png(path, w, h, rows):
    raw = b''.join(b'\x00' + bytes(r) for r in rows)
    chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', choices=PRESETS, default=None)
    ap.add_argument('--stops', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--width', type=int, default=256)
    a = ap.parse_args()
    stops = parse(a.stops or PRESETS[a.preset or 'character'])
    row = []
    for x in range(a.width):
        c = sample(stops, x / (a.width - 1))
        row += [max(0, min(255, round(v * 255))) for v in c]
    write_png(a.out, a.width, 4, [row] * 4)
    print(f"RAMP {a.out}: " + ' '.join(f"{u:.2f}->{'/'.join(f'{v:.2f}' for v in c)}" for u, c in stops))


if __name__ == '__main__':
    main()
