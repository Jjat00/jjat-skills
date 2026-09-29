"""Extiende un cams.npz existente con cadena de homografías del suelo (hacia atrás o hacia adelante).

  python3 dk_extend.py WD --to 0 [--radius 450] [--corridor 70 --route-m route_m.json]

- Parte del frame con cámara más cercano al objetivo (el primero si --to es menor, el último si es mayor).
- Máscara por frame: suelo (z>0) a menos de --radius m del punto de suelo en la parte baja-centro del cuadro,
  o, si se da --route-m (lista de polilíneas en metros), a menos de --corridor m de ellas.
- Reemplaza/añade los frames nuevos y guarda WD/cams.npz (copia de respaldo en cams_prev.npz).
"""
import argparse, json, shutil, numpy as np, cv2
from dk_common import wd_path, Gray, undist, load_cfg

ap = argparse.ArgumentParser()
ap.add_argument('wd'); ap.add_argument('--to', type=int, required=True)
ap.add_argument('--radius', type=float, default=450.0)
ap.add_argument('--corridor', type=float, default=70.0)
ap.add_argument('--route-m', default='')
ap.add_argument('--from-frame', type=int, default=None, help='frame de partida (por defecto el borde del rango con cámara)')
a = ap.parse_args()
WD = a.wd; cfg = load_cfg(WD); H, W = cfg['h'], cfg['w']
C = np.load(wd_path(WD, 'cams.npz'))
K, dist = C['K'], C['dist']
N = {int(f): n for f, n in zip(C['frames'], C['N'])}
lo, hi = min(N), max(N)
start = a.from_frame if a.from_frame is not None else (lo if a.to < lo else hi)
stepd = -1 if a.to < start else 1
ROUTE = None
if a.route_m:
    ROUTE = [np.float64(p) for p in json.load(open(a.route_m))]

ys, xs = np.mgrid[2:H:4, 2:W:4]
pix = np.c_[xs.ravel(), ys.ravel()].astype(np.float64)
ph = np.c_[undist(pix, K, dist), np.ones(len(pix))]

def dist_to_poly(Pp, V):
    d = np.full(len(Pp), np.inf)
    for p, q in zip(V[:-1], V[1:]):
        e = q - p; L = e @ e; t = np.clip(((Pp - p) @ e) / max(L, 1e-9), 0, 1)
        d = np.minimum(d, np.linalg.norm(Pp - (p + t[:, None] * e), axis=1))
    return d

def to_plane(Nf, px):
    h = np.c_[undist(np.float64(px), K, dist), np.ones(len(px))] @ np.linalg.inv(Nf).T
    return h[:, :2] / h[:, 2:3], h[:, 2]

def mask_for(Nf):
    p = ph @ np.linalg.inv(Nf).T; uv = p[:, :2] / p[:, 2:3]
    z = (np.c_[uv, np.ones(len(uv))] @ Nf.T)[:, 2]
    ok = z > 0
    if ROUTE is not None:
        d = np.min([dist_to_poly(uv, R) for R in ROUTE], axis=0); ok &= d < a.corridor
    else:
        c, _ = to_plane(Nf, [[W / 2, H * 0.92]]); ok &= np.linalg.norm(uv - c[0], axis=1) < a.radius
    m = np.zeros((H, W), np.uint8); m[ys.ravel()[ok], xs.ravel()[ok]] = 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8)); m[:4] = 0; m[-4:] = 0; m[:, :4] = 0; m[:, -4:] = 0
    return m

G = Gray(WD)
lk = dict(winSize=(21, 21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
f = start; low = 1e9; newN = {}
cur = N[start]
while f != a.to:
    g = f + stepd
    A, B = G[f], G[g]
    mk = mask_for(cur)
    if (mk > 0).mean() < 0.08:
        print('  máscara pequeña en', f, round(float((mk > 0).mean()), 3), '-> mitad baja del cuadro', flush=True)
        mk = np.zeros((H, W), np.uint8); mk[H // 3:-4, 4:-4] = 255
    pts = cv2.goodFeaturesToTrack(A, 2500, 0.003, 6, mask=mk, blockSize=7)
    p1, st, _ = cv2.calcOpticalFlowPyrLK(A, B, pts, None, **lk)
    p0r, st2, _ = cv2.calcOpticalFlowPyrLK(B, A, p1, None, **lk)
    ok = (st.ravel() == 1) & (st2.ravel() == 1) & (np.linalg.norm((pts - p0r).reshape(-1, 2), axis=1) < 0.5)
    P0 = undist(pts.reshape(-1, 2)[ok], K, dist); P1 = undist(p1.reshape(-1, 2)[ok], K, dist)
    h, inl = cv2.findHomography(P0, P1, cv2.USAC_MAGSAC, 1.0 / K[0, 0], maxIters=5000, confidence=0.999)
    Ng = h @ cur   # h ~ identidad con h33 = 1: conserva el signo (no usar N[2,2], el origen puede quedar detrás)
    cur = Ng; newN[g] = Ng; low = min(low, int(inl.sum()))
    if g % 30 == 0:
        c, _ = to_plane(cur, [[W / 2, H * 0.92], [W / 2, H * 0.5]])
        print('  cadena', g, int(inl.sum()), '/', len(P0), 'mask %.2f' % (mk > 0).mean(), 'suelo abajo', c[0].round(1), 'centro', c[1].round(1), flush=True)
    f = g
print(f'cadena {start} -> {a.to}: mínimo de inliers {low}' + ('  <- POCO, revisar' if low < 150 else ''))
shutil.copy(wd_path(WD, 'cams.npz'), wd_path(WD, 'cams_prev.npz'))
N.update(newN)
fr = np.array(sorted(N))
np.savez(wd_path(WD, 'cams.npz'), frames=fr, N=np.stack([N[f] for f in fr]), K=K, dist=dist)
print('cams.npz', fr[0], '->', fr[-1])
