"""Paso 4: matriz plano->cámara (N) para cada frame -> WD/cams.npz

Modo SfM (después de dk_sfm + dk_plane):
  python3 dk_track.py WD --sfm-range 1260,2280 [--to 240]
  - frames dentro de --sfm-range: N exacta desde las poses de COLMAP
  - --to: extiende con cadena de homografías frame a frame hasta ese frame (antes o después; admite "240,2400")

Modo rápido SIN SfM (un rectángulo de medida conocida en el suelo):
  python3 dk_track.py WD --anchor 1950 --rect 468,420,706,418,754,475,460,475 --rect-m 28,15 --to 240,2280
  - --rect: 4 esquinas en orden (horario o antihorario) de algo rectangular y plano: cancha, parqueadero, lote
  - --rect-m: largo del lado 1-2 y del lado 2-3 en metros
  - origen del plano = esquina 1; el pin sale de "dest" en route.json

Cadena: solo puntos KLT del suelo cerca de la ruta (corredor de --corridor m alrededor de route.json) o,
si aún no hay ruta en metros, del suelo a menos de --radius m del ancla. --passes 2 hace una primera pasada
con radio y una segunda con el corredor ya calculado.
"""
import argparse, os, json, numpy as np, cv2
from dk_common import wd_path, Gray, undist, load_cfg, fit_line, intersect, img2plane

ap = argparse.ArgumentParser()
ap.add_argument('wd')
ap.add_argument('--sfm-range')
ap.add_argument('--anchor', type=int); ap.add_argument('--rect'); ap.add_argument('--rect-m')
ap.add_argument('--to', default='', help='frames destino de la cadena, p. ej. 240 o 240,2280')
ap.add_argument('--corridor', type=float, default=75.0)
ap.add_argument('--radius', type=float, default=700.0)
ap.add_argument('--passes', type=int, default=1)
a = ap.parse_args()
WD = a.wd; cfg = load_cfg(WD)
H, W = cfg['h'], cfg['w']

if a.sfm_range:
    from dk_common import Cams, Plane
    cams = Cams(WD); pl = Plane(WD); K, dist = cams.K, cams.dist
    s0, s1 = [int(x) for x in a.sfm_range.split(',')]
    BASE = {f: pl.N(*cams.pose(f)) for f in range(s0, s1 + 1) if cams.has(f)}
    center0 = np.zeros(2)
    print('N por SfM', min(BASE), '->', max(BASE))
else:
    f0 = 0.9 * max(W, H)
    K = np.array([[f0, 0, W / 2], [0, f0, H / 2], [0, 0, 1.]]); dist = np.zeros(5)
    q = np.float64([float(v) for v in a.rect.split(',')]).reshape(4, 2)
    Lm, Wm = [float(v) for v in a.rect_m.split(',')]
    P = np.float64([[0, 0], [Lm, 0], [Lm, Wm], [0, Wm]])
    Hr, _ = cv2.findHomography(P, q)                     # metros -> píxeles
    Na = np.linalg.inv(K) @ Hr
    if Na[2, 2] < 0: Na = -Na
    BASE = {a.anchor: Na}; s0 = s1 = a.anchor; center0 = np.array([Lm / 2, Wm / 2])
    print('ancla', a.anchor, 'rectángulo', Lm, 'x', Wm, 'm (K nominal, sin distorsión)')

def rough_route(N):
    p = wd_path(WD, 'route.json')
    if not os.path.exists(p): return None
    rj = json.load(open(p)); lines = []
    for seg in rj['segments']:
        pts = [img2plane(N[o['frame']], np.float64(o['pts']), K, dist) for o in seg['obs'] if o['frame'] in N]
        if pts and len(np.vstack(pts)) >= 2: lines.append(fit_line(np.vstack(pts)))
    if not lines: return None
    if len(lines) == 1:
        m, dv = lines[0]; return np.array([m - dv * 1500, m + dv * 1500])
    corners = [intersect(l1, l2) for l1, l2 in zip(lines[:-1], lines[1:])]
    def away(line, c):
        dv = line[0] - c; n_ = np.linalg.norm(dv)
        return c + (dv / n_ if n_ > 1 else line[1]) * 1500
    return np.array([away(lines[0], corners[0])] + corners + [away(lines[-1], corners[-1])])

def dist_to_poly(Pp, V):
    d = np.full(len(Pp), np.inf)
    for p, q in zip(V[:-1], V[1:]):
        e = q - p; L = e @ e; t = np.clip(((Pp - p) @ e) / max(L, 1e-9), 0, 1)
        d = np.minimum(d, np.linalg.norm(Pp - (p + t[:, None] * e), axis=1))
    return d

ys, xs = np.mgrid[2:H:4, 2:W:4]
pix = np.c_[xs.ravel(), ys.ravel()].astype(np.float64)
ph = np.c_[undist(pix, K, dist), np.ones(len(pix))]
def mask_for(Nf, RR):
    p = ph @ np.linalg.inv(Nf).T; uv = p[:, :2] / p[:, 2:3]
    z = (np.c_[uv, np.ones(len(uv))] @ Nf.T)[:, 2]
    ok = z > 0
    ok &= (dist_to_poly(uv, RR) < a.corridor) if RR is not None else (np.linalg.norm(uv - center0, axis=1) < a.radius)
    m = np.zeros((H, W), np.uint8); m[ys.ravel()[ok], xs.ravel()[ok]] = 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8)); m[:4] = 0; m[-4:] = 0; m[:, :4] = 0; m[:, -4:] = 0
    return m

G = Gray(WD)
lk = dict(winSize=(21, 21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
def chain(N, RR, target):
    start, stepd = (s0, -1) if target < s0 else (s1, 1)
    f = start; low = 1e9
    while f != target:
        g = f + stepd
        A, B = G[f], G[g]
        pts = cv2.goodFeaturesToTrack(A, 2500, 0.003, 6, mask=mask_for(N[f], RR), blockSize=7)
        p1, st, _ = cv2.calcOpticalFlowPyrLK(A, B, pts, None, **lk)
        p0r, st2, _ = cv2.calcOpticalFlowPyrLK(B, A, p1, None, **lk)
        ok = (st.ravel() == 1) & (st2.ravel() == 1) & (np.linalg.norm((pts - p0r).reshape(-1, 2), axis=1) < 0.5)
        P0 = undist(pts.reshape(-1, 2)[ok], K, dist); P1 = undist(p1.reshape(-1, 2)[ok], K, dist)
        h, inl = cv2.findHomography(P0, P1, cv2.USAC_MAGSAC, 1.0 / K[0, 0], maxIters=5000, confidence=0.999)
        Ng = h @ N[f]
        if Ng[2, 2] < 0: Ng = -Ng
        N[g] = Ng; low = min(low, int(inl.sum()))
        if g % 100 == 0: print('  cadena', g, int(inl.sum()), '/', len(P0), flush=True)
        f = g
    print(f'  cadena hasta {target}: mínimo de inliers {low}' + ('  <- POCO, revisar' if low < 150 else ''))

targets = [int(x) for x in a.to.split(',') if x.strip()]
N = dict(BASE)
for ps in range(max(1, a.passes)):
    RR = None if (ps == 0 and a.passes > 1) else rough_route(N)
    print(f'pasada {ps + 1}:', 'corredor de la ruta' if RR is not None else f'suelo a < {a.radius:.0f} m del ancla')
    N = dict(BASE)
    for tg in targets: chain(N, RR, tg)
fr = np.array(sorted(N))
np.savez(wd_path(WD, 'cams.npz'), frames=fr, N=np.stack([N[f] for f in fr]), K=K, dist=dist, sfm_range=np.array([s0, s1]))
print('cams.npz', fr[0], '->', fr[-1])
