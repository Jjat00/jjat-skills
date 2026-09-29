"""Paso 5: ruta en metros sobre el plano -> WD/scene.npz, y utilidades de anotación.
  python3 dk_route.py WD build                      # route.json -> scene.npz (+ reporte de ajuste)
  python3 dk_route.py WD where 600 746,350 783,417  # píxeles de un frame -> metros en el plano
  python3 dk_route.py WD check 330,600,1260,1950    # hoja con la línea central proyectada en esos frames
  python3 dk_route.py WD grid 1950 280 300 700 440  # recorte con cuadrícula (+ ruta si existe) para anotar

route.json:
{ "segments": [ {"name": "avenida", "type": "line", "obs": [{"frame": 330, "pts": [[720,429],[960,549]]}, ...]},
                {"name": "calle del parque", "type": "line", "obs": [...]} ],
  "start": {"frame": 330, "pt": [960,549]},  "end": {"frame": 1950, "pt": [515,397]},
  "dest": {"frame": 1500, "pt": [330,367]},   "fillet_m": 12 }
type "line" = calle recta (se ajusta una recta con todas las observaciones; las esquinas salen de intersecciones).
type "poly" = tramo curvo: los puntos se usan en orden como vértices.
"""
import sys, json, numpy as np, cv2
from dk_common import wd_path, Track, fit_line, intersect, fillet, resample, grid_zoom, read_frame, load_cfg

WD, cmd = sys.argv[1], sys.argv[2]
import os
tr = Track(WD) if os.path.exists(wd_path(WD, 'cams.npz')) else None
def ptsp(frame, pts): return tr.to_plane(frame, np.float64(pts))

def build():
    rj = json.load(open(wd_path(WD, 'route.json')))
    segs = []
    for seg in rj['segments']:
        obs = [(o['frame'], ptsp(o['frame'], o['pts'])) for o in seg['obs']]
        P = np.vstack([p for _, p in obs])
        if seg.get('type', 'line') == 'line':
            m, d = fit_line(P); nrm = np.array([-d[1], d[0]])
            print(f"[{seg['name']}] {len(P)} puntos, residuo máx {np.abs((P - m) @ nrm).max():.1f} m")
            for f, p in obs: print(f"   frame {f}: desvío medio {((p - m) @ nrm).mean():+.1f} m")
            segs.append(('line', (m, d)))
        else:
            segs.append(('poly', P))
    for (t1, l1), (t2, l2) in zip(segs[:-1], segs[1:]):
        if t1 == t2 == 'line':
            print('ángulo entre calles %.1f°' % np.degrees(np.arccos(abs(l1[1] @ l2[1]))))
    def proj(seg, p):
        t, g = seg
        if t == 'line': m, d = g; return m + d * ((p - m) @ d)
        return g[np.argmin(np.linalg.norm(g - p, axis=1))]
    start = proj(segs[0], ptsp(rj['start']['frame'], [rj['start']['pt']])[0])
    end = proj(segs[-1], ptsp(rj['end']['frame'], [rj['end']['pt']])[0])
    verts = [start]
    for i, (t, g) in enumerate(segs):
        if t == 'poly': verts += list(g)
        if i < len(segs) - 1:
            n_ = segs[i + 1]
            if t == 'line' and n_[0] == 'line': verts.append(intersect(g, n_[1]))
    verts.append(end)
    verts = np.array(verts)
    R = fillet(verts, rj.get('fillet_m', 12.0)); P, s = resample(R, 0.5)
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True)
    Lat = np.c_[-T[:, 1], T[:, 0]]
    dest = ptsp(rj['dest']['frame'], [rj['dest']['pt']])[0] if 'dest' in rj else np.zeros(2)
    np.savez(wd_path(WD, 'scene.npz'), route=P, s=s, lateral=Lat, dest=dest)
    print('vértices (m):', verts.round(1).tolist()); print('largo de la ruta %.0f m | destino %s' % (s[-1], dest.round(1)))

def check(frames):
    cfg = load_cfg(WD); sc = np.load(wd_path(WD, 'scene.npz')); P = sc['route']
    tiles = []
    for f in frames:
        im = read_frame(cfg['video'], f); uv, z = tr.to_img(f, P)
        for (x, y), zz in zip(uv, z):
            if zz > 0 and 0 <= x < im.shape[1] and 0 <= y < im.shape[0]: cv2.circle(im, (int(x), int(y)), 1, (255, 140, 0), -1)
        d, zd = tr.to_img(f, sc['dest'][None])
        if zd[0] > 0: cv2.circle(im, tuple(np.int32(d[0])), 6, (0, 255, 0), 2)
        cv2.putText(im, f'f{f} {f / cfg["fps"]:.1f}s', (10, 30), 0, 0.9, (0, 255, 255), 2)
        tiles.append(cv2.resize(im, (640, int(640 * im.shape[0] / im.shape[1]))))
    while len(tiles) % 3: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(wd_path(WD, 'check.jpg'), np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]))
    print('->', wd_path(WD, 'check.jpg'))

if cmd == 'build': build()
elif cmd == 'where':
    f = int(sys.argv[3]); pts = [[float(v) for v in p.split(',')] for p in sys.argv[4:]]
    for p, q in zip(pts, ptsp(f, pts)): print(p, '->', q.round(2))
elif cmd == 'check': check([int(x) for x in sys.argv[3].split(',')])
elif cmd == 'grid':
    f, x0, y0, x1, y1 = [int(v) for v in sys.argv[3:8]]
    cfg = load_cfg(WD); im = read_frame(cfg['video'], f); ov = []
    if tr is not None and os.path.exists(wd_path(WD, 'scene.npz')) and f in tr.idx:
        sc = np.load(wd_path(WD, 'scene.npz')); uv, z = tr.to_img(f, sc['route']); ov = [(uv[z > 0], (255, 140, 0))]
    out = wd_path(WD, f'grid_{f}.png'); grid_zoom(im, x0, y0, x1, y1, out, step=10 if (x1 - x0) < 600 else 25, overlays=ov); print('->', out)
