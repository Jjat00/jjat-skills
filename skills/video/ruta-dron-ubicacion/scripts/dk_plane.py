"""Paso 3: plano del suelo en metros con origen en el destino.
  python3 dk_plane.py WD --frame 1800 --poly 420,430,1015,430,1022,572,415,572 \
      --scale-frame 1950 --scale-pts 468,420,706,418 --scale-m 28 \
      --dest-frame 1500 --dest 330,367
--poly: zona plana y despejada (plaza, cancha, parqueadero, potrero) en un frame con SfM bueno.
--scale-pts/--scale-m: dos puntos del suelo con distancia real conocida (largo de cancha 28 m, ancho de calle...).
--dest: base de la puerta del destino (donde nace el pin).
"""
import argparse, numpy as np, cv2
from dk_common import wd_path, Cams, project3d, undist

ap = argparse.ArgumentParser()
ap.add_argument('wd'); ap.add_argument('--frame', type=int, required=True); ap.add_argument('--poly', required=True)
ap.add_argument('--scale-frame', type=int); ap.add_argument('--scale-pts'); ap.add_argument('--scale-m', type=float)
ap.add_argument('--mpu', type=float, help='metros por unidad SfM, si ya se conoce')
ap.add_argument('--dest-frame', type=int, required=True); ap.add_argument('--dest', required=True)
a = ap.parse_args()
cams = Cams(a.wd); K, dist = cams.K, cams.dist
X = np.load(wd_path(a.wd, 'points3d.npz'))['xyz']
R, t = cams.pose(a.frame)
uv, z = project3d(X, R, t, K, dist)
poly = np.float32([float(v) for v in a.poly.split(',')]).reshape(-1, 2)
ins = np.array([zz > 0 and cv2.pointPolygonTest(poly, (float(p[0]), float(p[1])), False) >= 0 for p, zz in zip(uv, z)])
Y = X[ins]; thr = 0.005 * float(np.median(z[ins]))
print('puntos en el polígono', len(Y), 'umbral', round(thr, 5))
rng = np.random.default_rng(0); best = None
for _ in range(3000):
    s = Y[rng.choice(len(Y), 3, replace=False)]; n = np.cross(s[1] - s[0], s[2] - s[0]); nn = np.linalg.norm(n)
    if nn < 1e-12: continue
    n /= nn; d = n @ s[0]; c = int((np.abs(Y @ n - d) < thr).sum())
    if best is None or c > best[0]: best = (c, n, d)
_, n, d = best; inl = np.abs(Y @ n - d) < thr
m = Y[inl].mean(0); _, _, vt = np.linalg.svd(Y[inl] - m); n = vt[2]; d = n @ m
C = cams.center(a.frame)
if n @ C - d < 0: n, d = -n, -d
print('inliers', int(inl.sum()), 'de', len(Y), '| normal', n.round(4))

def hit(f, px):
    R, t = cams.pose(f); C = -R.T @ t
    xn = undist(px, K, dist); dr = np.c_[xn, np.ones(len(xn))] @ R
    s = (d - n @ C) / (dr @ n); return C + dr * s[:, None]

if a.mpu: mpu = a.mpu
else:
    sp = np.float64([float(v) for v in a.scale_pts.split(',')]).reshape(2, 2)
    P = hit(a.scale_frame, sp); mpu = a.scale_m / np.linalg.norm(P[1] - P[0])
print('metros por unidad SfM', round(mpu, 3))
o = hit(a.dest_frame, np.float64([float(v) for v in a.dest.split(',')]).reshape(1, 2))[0]
Rd, _ = cams.pose(a.dest_frame); xcam = Rd[0]          # eje x de la cámara en el mundo
e1 = xcam - (xcam @ n) * n; e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
np.savez(wd_path(a.wd, 'plane.npz'), n=n, d=d, o=o, e1=e1, e2=e2, mpu=mpu)
for f in list(cams.frames[::max(1, len(cams.frames) // 8)]):
    print('frame', int(f), 'altura del dron ~%.0f m' % ((n @ cams.center(f) - d) * mpu))
print('guardado plane.npz (u = derecha de la cámara del destino, v = hacia la cámara... coordenadas en metros)')
