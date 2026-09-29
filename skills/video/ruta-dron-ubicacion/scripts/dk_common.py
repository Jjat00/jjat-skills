"""dronekit: helpers compartidos.

Convenciones
- WD (carpeta de trabajo) guarda todo: project.json, gray.npy, sfm/, poses.npz, plane.npz, chain.npz, route.json...
- Frames = índices del video original (0-based).
- Coordenadas del plano del suelo en METROS, origen en el destino (la puerta del local).
- N_f (3x3): plano (u, v, 1) -> coordenadas normalizadas de la cámara del frame f (la 3a fila es profundidad).
"""
import json, os, sys, numpy as np, cv2

def wd_path(wd, *p):
    return os.path.join(wd, *p)

def load_cfg(wd):
    p = wd_path(wd, 'project.json')
    return json.load(open(p)) if os.path.exists(p) else {}

def save_cfg(wd, cfg):
    json.dump(cfg, open(wd_path(wd, 'project.json'), 'w'), indent=1, ensure_ascii=False)

# ---------------- video ----------------
def read_frame(video, f):
    cap = cv2.VideoCapture(video); cap.set(cv2.CAP_PROP_POS_FRAMES, int(f)); ok, im = cap.read(); cap.release()
    if not ok: raise RuntimeError(f'no se pudo leer el frame {f}')
    return im

class Gray:
    """frames en gris guardados en gray.npy (memmap) con su offset en gray_meta.json"""
    def __init__(self, wd):
        self.a = np.load(wd_path(wd, 'gray.npy'), mmap_mode='r')
        self.f0 = json.load(open(wd_path(wd, 'gray_meta.json')))['f0']
    def __getitem__(self, f):
        return np.asarray(self.a[int(f) - self.f0])
    def has(self, f):
        return 0 <= int(f) - self.f0 < len(self.a)

# ---------------- cámara ----------------
class Cams:
    """poses por frame de SfM (poses.npz: frames, R, t, K, dist)"""
    def __init__(self, wd, name='poses.npz'):
        P = np.load(wd_path(wd, name))
        self.frames = P['frames']; self.R = P['R']; self.t = P['t']; self.K = P['K']; self.dist = P['dist']
        self.idx = {int(f): i for i, f in enumerate(self.frames)}
    def has(self, f): return int(f) in self.idx
    def pose(self, f): i = self.idx[int(f)]; return self.R[i], self.t[i]
    def center(self, f): R, t = self.pose(f); return -R.T @ t

def undist(uv, K, dist):
    return cv2.undistortPoints(np.float64(uv).reshape(-1, 1, 2), K, dist).reshape(-1, 2)

def distort_px(xn, K, dist):
    x, y = xn[:, 0], xn[:, 1]; r2 = x * x + y * y; d = 1 + dist[0] * np.minimum(r2, 4.0)
    return np.c_[K[0, 0] * x * d + K[0, 2], K[1, 1] * y * d + K[1, 2]]

def project3d(X, R, t, K, dist):
    Xc = X @ R.T + t; z = Xc[:, 2]
    zz = np.where(z > 1e-9, z, 1.0)
    return distort_px(Xc[:, :2] / zz[:, None], K, dist), z

# ---------------- plano ----------------
class Plane:
    """plane.npz: n, d (n.X = d), o (origen 3D = destino), e1, e2 (base), mpu (metros por unidad SfM)"""
    def __init__(self, wd):
        p = np.load(wd_path(wd, 'plane.npz'))
        self.n, self.d, self.o, self.e1, self.e2, self.mpu = p['n'], float(p['d']), p['o'], p['e1'], p['e2'], float(p['mpu'])
    def N(self, R, t):
        M = np.zeros((3, 3))
        M[:, 0] = R @ (self.e1 / self.mpu); M[:, 1] = R @ (self.e2 / self.mpu); M[:, 2] = R @ self.o + t
        return M
    def to_plane(self, X):
        Y = np.atleast_2d(X) - self.o; return np.c_[Y @ self.e1, Y @ self.e2] * self.mpu
    def to_world(self, uv):
        uv = np.atleast_2d(uv); return self.o + (uv[:, :1] * self.e1 + uv[:, 1:2] * self.e2) / self.mpu

def plane2img(N, uv, K, dist):
    q = np.c_[np.atleast_2d(uv), np.ones(len(np.atleast_2d(uv)))] @ N.T
    z = q[:, 2]; zz = np.where(z > 1e-12, z, 1.0)
    return distort_px(q[:, :2] / zz[:, None], K, dist), z

def img2plane(N, px, K, dist):
    xn = undist(px, K, dist); h = np.c_[xn, np.ones(len(xn))]
    p = h @ np.linalg.inv(N).T
    return p[:, :2] / p[:, 2:3]

class Track:
    """cams.npz final: N por frame (SfM o cadena de homografías)"""
    def __init__(self, wd, name='cams.npz'):
        C = np.load(wd_path(wd, name))
        self.frames = C['frames']; self.Ns = C['N']; self.K = C['K']; self.dist = C['dist']
        self.idx = {int(f): i for i, f in enumerate(self.frames)}
    def N(self, f): return self.Ns[self.idx[int(f)]]
    def to_img(self, f, uv): return plane2img(self.N(f), uv, self.K, self.dist)
    def to_plane(self, f, px): return img2plane(self.N(f), px, self.K, self.dist)

# ---------------- geometría 2D ----------------
def fit_line(pts):
    """recta por mínimos cuadrados (total least squares): punto medio + dirección unitaria"""
    P = np.asarray(pts, float); m = P.mean(0); _, _, vt = np.linalg.svd(P - m); return m, vt[0]

def intersect(l1, l2):
    (p, d), (q, e) = l1, l2
    A = np.c_[d, -e]; s = np.linalg.solve(A, q - p); return p + d * s[0]

def fillet(pts, r):
    pts = np.asarray(pts, float); out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d1 = (a - b) / np.linalg.norm(a - b); d2 = (c - b) / np.linalg.norm(c - b)
        ang = np.arccos(np.clip(d1 @ d2, -1, 1))
        if ang > np.radians(175): out.append(b); continue
        t = min(r / np.tan(ang / 2), 0.45 * np.linalg.norm(a - b), 0.45 * np.linalg.norm(c - b))
        p1 = b + d1 * t; p2 = b + d2 * t
        for u in np.linspace(0, 1, 40): out.append((1 - u) ** 2 * p1 + 2 * (1 - u) * u * b + u ** 2 * p2)
    out.append(pts[-1]); return np.array(out)

def resample(pts, step):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); s = np.r_[0, np.cumsum(seg)]
    ss = np.r_[np.arange(0, s[-1], step), s[-1]]
    return np.c_[np.interp(ss, s, pts[:, 0]), np.interp(ss, s, pts[:, 1])], ss

# ---------------- imágenes de apoyo ----------------
def grid_zoom(img, x0, y0, x1, y1, out, step=10, overlays=(), marks=()):
    """recorte ampliado con cuadrícula en coordenadas del video (para anotar puntos a ojo)
    overlays: lista de (array Nx2 px, color BGR) ; marks: lista de (x, y, color)"""
    crop = img[y0:y1, x0:x1]
    s = min(1500 / (x1 - x0), 950 / (y1 - y0))
    big = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_CUBIC); h, w = big.shape[:2]
    for x in range((x0 // step + 1) * step, x1, step):
        X = int((x - x0) * s); c = (0, 255, 255) if x % 50 == 0 else (0, 110, 110); cv2.line(big, (X, 0), (X, h), c, 1)
        if x % 50 == 0: cv2.putText(big, str(x), (X + 2, 13), 0, 0.42, (0, 255, 255), 1)
    for y in range((y0 // step + 1) * step, y1, step):
        Y = int((y - y0) * s); c = (0, 255, 255) if y % 50 == 0 else (0, 110, 110); cv2.line(big, (0, Y), (w, Y), c, 1)
        if y % 50 == 0: cv2.putText(big, str(y), (2, Y - 2), 0, 0.42, (0, 255, 255), 1)
    for pts, col in overlays:
        for x, y in pts:
            if x0 < x < x1 and y0 < y < y1: cv2.circle(big, (int((x - x0) * s), int((y - y0) * s)), 2, col, -1)
    for x, y, col in marks:
        cv2.circle(big, (int((x - x0) * s), int((y - y0) * s)), 6, col, 2)
    cv2.imwrite(out, big)
    return s
