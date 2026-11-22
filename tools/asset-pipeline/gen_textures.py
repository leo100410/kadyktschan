"""Procedural, seamlessly tiling surface textures (art bible 8.4-8.6). No photos involved.

Usage: python -I gen_textures.py <out dir>   (needs numpy + imagecodecs)
Writes T_<Name>_D/_N/_ORM.png at 2048 px = 2 m (10.24 px/cm).
_D is a greyscale detail map whose mean is 0.5 linear: the master material multiplies
PaintColor by (_D * 2), so the material's albedo mean equals the palette value (art bible 8.6).
"""
import os, sys, zlib
import numpy as np
try:
    import imagecodecs
except ImportError:  # e.g. Blender's bundled Python: plain zlib PNG writer below
    imagecodecs = None

N = 2048
rng = np.random.default_rng(1986_2011)

def periodic_noise(scale_px, power=2.0):
    """Tileable fractal noise in [0,1]: white noise filtered in frequency space (FFT is periodic)."""
    f = np.fft.fftfreq(N)
    fx, fy = np.meshgrid(f, f)
    k = np.sqrt(fx ** 2 + fy ** 2)
    k[0, 0] = 1.0
    spectrum = np.fft.fft2(rng.standard_normal((N, N))) / (k * scale_px) ** power
    spectrum[0, 0] = 0
    n = np.real(np.fft.ifft2(spectrum))
    return (n - n.min()) / (n.max() - n.min())

def streaks(count, length_px, strength):
    """Vertical run-off streaks (rain under sills/joints), tileable by wrapping."""
    s = np.zeros((N, N))
    for _ in range(count):
        x, y0 = rng.integers(0, N, 2)
        w = rng.integers(10, 48)
        ln = rng.integers(length_px // 3, length_px)
        ys = (y0 + np.arange(ln)) % N
        fade = np.minimum(np.linspace(0, 8, ln), 1) * np.linspace(1, 0, ln) ** 1.5  # soft head, long tail
        for dx in range(-w, w + 1):
            s[ys, (x + dx) % N] += fade * (1 - abs(dx) / (w + 1))
    s = s / max(s.max(), 1e-6)
    return s * strength

def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)

def save(path, arr):
    if imagecodecs:
        open(path, "wb").write(imagecodecs.png_encode(arr))
        return
    import struct
    a = arr if arr.ndim == 3 else arr[..., None]
    h, w, c = a.shape
    raw = b"".join(b"\x00" + a[y].astype(np.uint8).tobytes() for y in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    ctype = {1: 0, 3: 2, 4: 6}[c]
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))

def normal_from_height(h, strength):
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(h)
    l = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    n = np.stack([nx / l, ny / l, nz / l], -1)
    return ((n * 0.5 + 0.5) * 255).astype(np.uint8)

def material(name, out, macro, fine, streak_strength, rough_base, rough_var, height_strength, macro_weight=0.55, contrast=0.09):
    m = periodic_noise(macro)            # large blotches (weathering, uneven paint)
    f = periodic_noise(fine, power=1.2)  # grain
    st = streaks(36, 1100, streak_strength)
    detail = macro_weight * m + (1 - macro_weight) * f - st
    detail = (detail - detail.mean()) / detail.std()
    lin = np.clip(0.5 + contrast * detail, 0.05, 0.95)
    lin = lin + (0.5 - lin.mean())       # exact mean 0.5 linear
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lin) * 255).round().astype(np.uint8))
    save(os.path.join(out, "T_%s_N.png" % name), normal_from_height(f * 0.7 + m * 0.3, height_strength))
    rough = np.clip(rough_base + rough_var * (f - 0.5) + 0.5 * st, 0, 1)
    orm = np.stack([np.full((N, N), 255, np.uint8), (rough * 255).astype(np.uint8), np.zeros((N, N), np.uint8)], -1)
    save(os.path.join(out, "T_%s_ORM.png" % name), orm)
    print("%-10s D mean(lin)=%.3f" % (name, lin.mean()))

def leaves(name, out, n_leaves, size_px, elong):
    """RGBA leaf-cluster card for masked foliage: grey detail (mean 0.5 linear on leaf pixels) + alpha mask.
    Leaves gather in 4-6 lobes around twigs and thin out towards the edge, so the card's square never shows
    (user 2026-11-08: bushes read as blocks); darker inside the cluster for depth."""
    M = 1024
    yy, xx = np.mgrid[0:M, 0:M]
    lum, alpha = np.zeros((M, M)), np.zeros((M, M), bool)
    lobes = [(M / 2 + rng.uniform(-0.22, 0.22) * M, M / 2 + rng.uniform(-0.22, 0.22) * M, rng.uniform(0.1, 0.18) * M)
             for _ in range(rng.integers(4, 7))]
    for lx, ly, lr in lobes:  # twig from the centre to each lobe, under the leaves
        for t in np.linspace(0, 1, 160):
            px, py = int(M / 2 + (lx - M / 2) * t), int(M / 2 + (ly - M / 2) * t)
            lum[py - 2:py + 2, px - 2:px + 2] = 0.18
            alpha[py - 2:py + 2, px - 2:px + 2] = True
    dist = np.hypot(xx - M / 2, yy - M / 2) / (M / 2)
    for _ in range(n_leaves):
        lx, ly, lr = lobes[rng.integers(len(lobes))]
        cx, cy = (np.clip(rng.normal(lx, lr), 30, M - 30), np.clip(rng.normal(ly, lr), 30, M - 30))
        r = rng.uniform(*size_px)
        a = rng.uniform(0, np.pi)
        u = ((xx - cx) * np.cos(a) + (yy - cy) * np.sin(a)) / (r * elong)
        v = (-(xx - cx) * np.sin(a) + (yy - cy) * np.cos(a)) / r
        m = u * u + v * v < 1
        lum[m] = rng.uniform(0.35, 0.65) * (0.85 + 0.15 * (1 - np.abs(v[m]))) * (0.7 + 0.35 * dist[m])  # midrib, inner shade
        alpha |= m
    alpha &= dist < 0.97  # nothing reaches the card border
    lum[alpha] += 0.5 - lum[alpha].mean()
    lum[~alpha] = 0.5  # neutral colour under transparent pixels: no dark fringes once mip-mapped
    rgb = (lin_to_srgb(lum) * 255).round().astype(np.uint8)
    rgba = np.dstack([rgb, rgb, rgb, (alpha * 255).astype(np.uint8)])
    save(os.path.join(out, "T_%s_D.png" % name), rgba)
    print("%-10s coverage=%.2f" % (name, alpha.mean()))

def pattern_detail(name, out, motif, grain=0.25):
    """Greyscale pattern detail (mean 0.5 linear) for tinted interiors: motif(yy, xx) -> 0..1 darkness."""
    yy, xx = np.mgrid[0:N, 0:N]
    m = motif(yy, xx)
    f = periodic_noise(grain, power=1.2)
    blot = periodic_noise(0.01)
    lin = 0.6 - 0.36 * m + 0.05 * (f - 0.5) - 0.08 * (blot - 0.5)
    lin = np.clip(lin + (0.5 - lin.mean()), 0.04, 0.96)
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lin) * 255).round().astype(np.uint8))
    save(os.path.join(out, "T_%s_N.png" % name), normal_from_height(f * 0.5 + m * 0.5, 2))
    orm = np.stack([np.full((N, N), 255, np.uint8), np.full((N, N), 215, np.uint8), np.zeros((N, N), np.uint8)], -1)
    save(os.path.join(out, "T_%s_ORM.png" % name), orm)
    print("%-10s pattern" % name)

def wallpaper_motif(yy, xx):
    """Small half-drop flower every 128 px (12.5 cm), like the 1970s rolls in photo R4."""
    P = 128
    cx = (xx % P) - P / 2
    cy = ((yy + (xx // P % 2) * P // 2) % P) - P / 2
    petals = sum(np.exp(-(((cx - 14 * np.cos(a)) ** 2 + (cy - 14 * np.sin(a)) ** 2) / 40)) for a in np.linspace(0, 2 * np.pi, 5, endpoint=False))
    stripe = np.exp(-((xx % 256) - 128) ** 2 / 8) * 0.35
    return np.clip(petals + np.exp(-(cx ** 2 + cy ** 2) / 20) * 0.8 + stripe, 0, 1)

def carpet_motif(yy, xx):
    """Dense diamond lattice with nested rhombi, 256 px (25 cm) period - wall-carpet ornament."""
    P = 256
    u, v = np.abs((xx % P) - P / 2), np.abs((yy % P) - P / 2)
    d = (u + v) / P
    rings = (np.sin(d * np.pi * 10) > 0.3).astype(float)
    cross = ((u < 10) | (v < 10)).astype(float) * 0.6
    return np.clip(rings * 0.7 + cross, 0, 1)


def fabric(name, out):
    """Fine woven upholstery with worn patches; threads repeat below 1 cm on the 2 m tile."""
    yy, xx = np.mgrid[0:N, 0:N]
    warp = np.sin(xx * 2 * np.pi / 4)
    weft = np.sin(yy * 2 * np.pi / 8)
    weave = warp * weft
    wear = periodic_noise(0.02)
    lum = 0.5 + 0.028 * weave + 0.06 * (wear - wear.mean())
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lum) * 255).round().astype(np.uint8))
    save(os.path.join(out, "T_%s_N.png" % name), normal_from_height(weave * 0.04, 0.8))
    rough = np.clip(0.87 + 0.08 * (wear - 0.5), 0, 1)
    orm = np.stack([np.full((N, N), 255, np.uint8), (rough * 255).astype(np.uint8), np.zeros((N, N), np.uint8)], -1)
    save(os.path.join(out, "T_%s_ORM.png" % name), orm)


def veneer(name, out):
    """Directional cabinet veneer: long grain and narrow pores, with faded varnish."""
    yy, xx = np.mgrid[0:N, 0:N]
    phase = xx * 52 * np.pi / N + 0.7 * np.sin(yy * 2 * np.pi / N) + 0.25 * np.sin(yy * 6 * np.pi / N)
    grain = np.sin(phase) * 0.5 + np.sin(phase * 3) * 0.2
    pores = np.maximum(0, np.cos(phase * 9) - 0.86) * 2
    wear = periodic_noise(0.015)
    lum = 0.5 + 0.075 * grain - 0.1 * pores + 0.035 * wear
    lum += 0.5 - lum.mean()
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lum) * 255).round().astype(np.uint8))
    save(os.path.join(out, "T_%s_N.png" % name), normal_from_height(grain * 0.04 - pores * 0.1, 1.2))
    rough = np.clip(0.6 + 0.16 * (wear - 0.5) + pores * 0.15, 0, 1)
    orm = np.stack([np.full((N, N), 255, np.uint8), (rough * 255).astype(np.uint8), np.zeros((N, N), np.uint8)], -1)
    save(os.path.join(out, "T_%s_ORM.png" % name), orm)

def planks_motif(yy, xx):
    """Floor boards 12.8 cm wide, staggered butt joints (stand-in for herringbone parquet, see decision log)."""
    w, L = 128, 1024
    row = yy // w
    offset = (row * 389) % L
    joint_x = ((xx + offset) % L) < 6
    joint_y = (yy % w) < 4
    tone = ((row * 7919 + (xx + offset) // L * 104729) % 13) / 13.0 * 0.5
    grain = (np.sin((xx + offset) * 0.08 + row * 1.7) * 0.5 + 0.5) * 0.15
    return np.clip(np.where(joint_x | joint_y, 1.0, tone + grain), 0, 1)

def grass(name, out):
    """RGBA card of tapered grass blades rising from the bottom edge (tundra grass / cotton grass stems)."""
    M = 1024
    yy, xx = np.mgrid[0:M, 0:M]
    lum, alpha = np.full((M, M), 0.5), np.zeros((M, M), bool)
    for _ in range(130):  # sparse enough to read as blades, not as a block, from a few metres away
        x0 = rng.uniform(20, M - 20)
        h = rng.uniform(0.45, 0.98) * M
        lean = rng.uniform(-0.25, 0.25)
        w0 = rng.uniform(5, 11)
        t = (M - 1 - yy) / h                       # 0 at the bottom, 1 at the blade tip
        cx = x0 + lean * (M - 1 - yy) ** 1.3 / M ** 0.3
        m = (t >= 0) & (t <= 1) & (np.abs(xx - cx) < w0 * (1 - t) + 0.6)
        lum[m] = rng.uniform(0.35, 0.65) * (0.75 + 0.5 * t[m])
        alpha |= m
    lum[alpha] += 0.5 - lum[alpha].mean()
    lum[~alpha] = 0.5
    rgb = (lin_to_srgb(lum) * 255).round().astype(np.uint8)
    save(os.path.join(out, "T_%s_D.png" % name), np.dstack([rgb, rgb, rgb, (alpha * 255).astype(np.uint8)]))
    print("%-10s coverage=%.2f" % (name, alpha.mean()))

def grime(name, out):
    """Building-scale weathering multiplier (1 = clean, lower = darker), tile = 16 m: long run-off streaks,
    damp blotches, grain. Not a _D map: the master multiplies it in by GrimeStrength (atmosphere-target.md)."""
    st = np.zeros((N, N))
    for _ in range(120):
        x, y0 = rng.integers(0, N, 2)
        w = rng.integers(8, 50)
        ln = rng.integers(200, 900)
        ys = (y0 + np.arange(ln)) % N
        fade = np.minimum(np.linspace(0, 6, ln), 1) * np.linspace(1, 0, ln) ** 1.1 * rng.uniform(0.4, 1.0)
        prof = 1 - np.abs(np.arange(-w, w + 1)) / (w + 1)
        for dx, pv in zip(range(-w, w + 1), prof):
            st[ys, (x + dx) % N] = np.maximum(st[ys, (x + dx) % N], fade * pv)
    blotch = np.clip((periodic_noise(0.003) - 0.45) * 2.2, 0, 1)
    fine = periodic_noise(0.3, power=1.2)
    dark = np.clip(0.6 * st + 0.4 * blotch + 0.08 * (fine - 0.5), 0, 0.8)
    lin = 1 - dark
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lin) * 255).round().astype(np.uint8))
    print("%-10s mean=%.3f min=%.3f" % (name, lin.mean(), lin.min()))

def card_save(out, name, lum, alpha):
    """RGBA card for the masked master: grey detail (mean 0.5 linear under the mask) + alpha."""
    lum = lum.copy()
    lum[alpha] += 0.5 - lum[alpha].mean()
    lum[~alpha] = 0.5
    rgb = (lin_to_srgb(np.clip(lum, 0.02, 0.98)) * 255).round().astype(np.uint8)
    save(os.path.join(out, "T_%s_D.png" % name), np.dstack([rgb, rgb, rgb, (alpha * 255).astype(np.uint8)]))
    print("%-10s coverage=%.3f" % (name, alpha.mean()))


def decal_cracks(name, out):
    """Tile = 8 m (0.39 cm/px): sparse branching cracks, mostly steep or diagonal like cracks in precast panels."""
    alpha = np.zeros((N, N), bool)
    def walk(x, y, ang, steps, width, depth):
        main = ang
        for k in range(steps):
            ang += rng.normal(0, 0.22) + 0.15 * (main - ang)   # jagged but keeps its course
            x, y = x + np.cos(ang) * 2.0, y + np.sin(ang) * 2.0
            w = max(1, int(round(width * (1 - k / steps * 0.6))))
            xi, yi = int(x) % N, int(y) % N
            alpha[np.ix_([(yi + d) % N for d in range(-w // 2, w // 2 + 1)], [(xi + d) % N for d in range(-w // 2, w // 2 + 1)])] = True
            if depth < 2 and rng.random() < 0.012:
                walk(x, y, ang + rng.choice((-1, 1)) * rng.uniform(0.5, 1.1), int(steps * rng.uniform(0.2, 0.45)), width * 0.6, depth + 1)
    for _ in range(26):
        ang = np.pi / 2 + rng.choice((-1, 1)) * rng.uniform(0.0, 0.8)   # down-ish, image y grows downward
        walk(rng.uniform(0, N), rng.uniform(0, N), ang, int(rng.uniform(70, 330)), rng.uniform(1.5, 3.5), 0)
    lum = 0.35 + 0.3 * periodic_noise(0.05)
    card_save(out, name, lum, alpha)


def decal_spall(name, out):
    """Tile = 8 m: irregular patches where the paint and plaster have flaked off, with a darker broken rim."""
    n = periodic_noise(1, power=1.25)  # flaky clusters; power sets patch size (scale_px only rescales)
    alpha = n > np.quantile(n, 0.93)
    inner = np.roll(alpha, 4, 0) & np.roll(alpha, -4, 0) & np.roll(alpha, 4, 1) & np.roll(alpha, -4, 1)
    lum = 0.5 + 0.12 * (periodic_noise(0.3, power=1.2) - 0.5)
    lum[alpha & ~inner] *= 0.55                    # broken edge of the plaster
    card_save(out, name, lum, alpha)


def decal_rust(name, out):
    """Tile = 8 m: rust run-off streaks (narrow at the top, frayed at the bottom) for under sills and pipes."""
    alpha = np.zeros((N, N), bool)
    lum = np.full((N, N), 0.5)
    for _ in range(420):
        x, y0 = rng.integers(0, N, 2)
        ln = rng.integers(30, 150)
        w0 = rng.uniform(1.5, 6)
        for k in range(ln):
            w = w0 * (1 - k / ln) ** 0.5
            xs = [(x + d) % N for d in range(-int(w), int(w) + 1)]
            alpha[(y0 + k) % N, xs] = True
            lum[(y0 + k) % N, xs] = 0.35 + 0.4 * k / ln
    card_save(out, name, lum, alpha)


def ground_dirt(name, out):
    """Tile = 2 m (1 mm/px): dusty dirt with pebbles and twigs (user reference image 2026-11-07)."""
    yy, xx = np.mgrid[0:N, 0:N]
    h = periodic_noise(1, power=1.6) * 0.5 + periodic_noise(1, power=1.1) * 0.15
    lum = 0.5 + 0.18 * (periodic_noise(1, power=1.8) - 0.5) + 0.16 * (periodic_noise(1, power=0.6) - 0.5)  # + grit
    for _ in range(2600):                                   # pebbles 4-24 mm
        cx, cy, r = rng.integers(0, N), rng.integers(0, N), rng.uniform(2, 12)
        x0, x1, y0, y1 = int(cx - r - 1), int(cx + r + 2), int(cy - r - 1), int(cy + r + 2)
        sy, sx = np.mgrid[y0:y1, x0:x1]
        dd = ((sx - cx) ** 2 / (r * rng.uniform(0.7, 1.3)) ** 2 + (sy - cy) ** 2 / r ** 2)
        m = dd < 1
        iy, ix = sy[m] % N, sx[m] % N
        lum[iy, ix] = lum[iy, ix] + rng.uniform(-0.12, 0.14) + 0.05 * (1 - dd[m])  # close to the soil tone
        h[iy, ix] += 0.35 * np.sqrt(1 - dd[m])
    for _ in range(90):                                     # twigs
        x, y, a, ln = rng.uniform(0, N), rng.uniform(0, N), rng.uniform(0, np.pi), rng.integers(40, 220)
        for k in range(ln):
            a += rng.normal(0, 0.03)
            xi, yi = int(x + np.cos(a) * k) % N, int(y + np.sin(a) * k) % N
            lum[yi, xi] = lum[(yi + 1) % N, xi] = 0.22
            h[yi, xi] += 0.2
    lum = np.clip(lum, 0.05, 0.95); lum += 0.5 - lum.mean()
    save(os.path.join(out, "T_%s_D.png" % name), (lin_to_srgb(lum) * 255).round().astype(np.uint8))
    save(os.path.join(out, "T_%s_N.png" % name), normal_from_height(h, 9))
    orm = np.stack([np.full((N, N), 255, np.uint8), np.full((N, N), 235, np.uint8), np.zeros((N, N), np.uint8)], -1)
    save(os.path.join(out, "T_%s_ORM.png" % name), orm)
    print("%-10s dirt D mean(lin)=%.3f" % (name, lum.mean()))


def track(name, out, ruts):
    """Ribbon card (u = across 0..1, v = along, one tile = width x 2 width): ragged edges in alpha; with ruts =
    a gravel road with two compacted wheel tracks, a grassy crown and potholes, without = a trodden footpath."""
    u = np.tile(np.linspace(0, 1, N), (N, 1))
    edge = 0.5 - np.abs(u - 0.5)
    rag = periodic_noise(1, power=1.4)
    alpha = edge > (0.04 + 0.16 * rag) if ruts else edge > (0.08 + 0.3 * rag)
    lum = 0.5 + 0.16 * (periodic_noise(1, power=1.2) - 0.5)
    if ruts:
        for c in (0.3, 0.7):
            lum -= 0.13 * np.exp(-((u - c) / 0.06) ** 2)                       # compacted wheel tracks
        crown = np.exp(-((u - 0.5) / 0.07) ** 2) * (periodic_noise(1, power=1.3) > 0.5)
        lum -= 0.12 * crown                                                    # grass on the crown
        holes = periodic_noise(1, power=1.7) > 0.86
        lum[holes] -= 0.18                                                     # potholes
    else:
        lum -= 0.08 * np.exp(-((u - 0.5) / 0.2) ** 2)                          # worn centre
    card_save(out, name, lum, alpha)


def seed(name):
    """Independent, stable random stream per texture (a new texture must not change the others)."""
    global rng
    rng = np.random.default_rng(zlib.crc32(name.encode()))


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    only = os.environ.get("KDK_TEX_ONLY")  # e.g. LeavesBroad_A,LeavesNeedle_A: regenerate just these
    if only:
        for nm in only.split(","):
            seed(nm)
            {"LeavesBroad_A": lambda: leaves("LeavesBroad_A", out, 900, (9, 22), 1.6),
             "Fabric_A": lambda: fabric("Fabric_A", out),
             "Veneer_A": lambda: veneer("Veneer_A", out),
             "LeavesWillow_A": lambda: leaves("LeavesWillow_A", out, 350, (6, 13), 3.2),
             "LeavesAlder_A": lambda: leaves("LeavesAlder_A", out, 500, (10, 19), 1.15),
             "LeavesNeedle_A": lambda: leaves("LeavesNeedle_A", out, 2200, (3, 6), 5.0)}[nm]()
        sys.exit(0)
    seed("Plaster_A"); material("Plaster_A", out, macro=0.004, fine=0.25, streak_strength=0.2, rough_base=0.82, rough_var=0.2, height_strength=6, macro_weight=0.3, contrast=0.06)
    seed("Concrete_A"); material("Concrete_A", out, macro=0.008, fine=0.4, streak_strength=0.2, rough_base=0.88, rough_var=0.15, height_strength=10)
    seed("Ground_A"); ground_dirt("Ground_A", out)
    seed("PaintWood_A"); material("PaintWood_A", out, macro=0.01, fine=0.6, streak_strength=0.1, rough_base=0.7, rough_var=0.25, height_strength=3)
    seed("LeavesBroad_A"); leaves("LeavesBroad_A", out, 900, (9, 22), 1.6)   # birch / shrub
    seed("LeavesNeedle_A"); leaves("LeavesNeedle_A", out, 2200, (3, 6), 5.0)  # larch tufts
    seed("Wallpaper_A"); pattern_detail("Wallpaper_A", out, wallpaper_motif)
    seed("Carpet_A"); pattern_detail("Carpet_A", out, carpet_motif, grain=0.6)
    seed("Fabric_A"); fabric("Fabric_A", out)
    seed("Veneer_A"); veneer("Veneer_A", out)
    seed("LeavesWillow_A"); leaves("LeavesWillow_A", out, 350, (6, 13), 3.2)
    seed("LeavesAlder_A"); leaves("LeavesAlder_A", out, 500, (10, 19), 1.15)
    seed("Planks_A"); pattern_detail("Planks_A", out, planks_motif)
    seed("GrassBlades_A"); grass("GrassBlades_A", out)
    seed("Grime_A"); grime("Grime_A", out)
    seed("DecalCrack_A"); decal_cracks("DecalCrack_A", out)
    seed("DecalSpall_A"); decal_spall("DecalSpall_A", out)
    seed("DecalRust_A"); decal_rust("DecalRust_A", out)
    seed("Road_A"); track("Road_A", out, ruts=True)
    seed("Path_A"); track("Path_A", out, ruts=False)
