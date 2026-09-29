"""hoja de control: cuadrícula del plano (cada STEP m) + puntos marcados, proyectados en varios frames
  python3 dk_gridcheck.py WD f1,f2,... [--step 50] [--pts x,y;x,y] [--scene] [--out name.jpg] [--cols 3]"""
import sys, os, argparse, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dk_common import Track, read_frame, load_cfg, wd_path
ap = argparse.ArgumentParser(); ap.add_argument('wd'); ap.add_argument('frames')
ap.add_argument('--step', type=float, default=50); ap.add_argument('--pts', default=''); ap.add_argument('--scene', action='store_true')
ap.add_argument('--out', default='gridcheck.jpg'); ap.add_argument('--cols', type=int, default=3); ap.add_argument('--ext', default='-600,600,-900,300')
ap.add_argument('--tile', type=int, default=640)
a = ap.parse_args(); WD = a.wd; cfg = load_cfg(WD); tr = Track(WD)
x0, x1, y0, y1 = [float(v) for v in a.ext.split(',')]
pts = [np.float64([float(v) for v in p.split(',')]) for p in a.pts.split(';') if p.strip()]
tiles = []
for f in [int(v) for v in a.frames.split(',')]:
    im = read_frame(cfg['video'], f)
    for gx in np.arange(np.ceil(x0 / a.step) * a.step, x1 + 1, a.step):
        L = np.c_[np.full(400, gx), np.linspace(y0, y1, 400)]; uv, z = tr.to_img(f, L)
        for p, q, za, zb in zip(uv[:-1], uv[1:], z[:-1], z[1:]):
            if za > 0 and zb > 0 and np.all(np.abs(p) < 5000) and np.all(np.abs(q) < 5000): cv2.line(im, tuple(np.int32(p)), tuple(np.int32(q)), (0, 255, 255) if gx % 100 == 0 else (0, 150, 150), 1, cv2.LINE_AA)
    for gy in np.arange(np.ceil(y0 / a.step) * a.step, y1 + 1, a.step):
        L = np.c_[np.linspace(x0, x1, 400), np.full(400, gy)]; uv, z = tr.to_img(f, L)
        for p, q, za, zb in zip(uv[:-1], uv[1:], z[:-1], z[1:]):
            if za > 0 and zb > 0 and np.all(np.abs(p) < 5000) and np.all(np.abs(q) < 5000): cv2.line(im, tuple(np.int32(p)), tuple(np.int32(q)), (255, 0, 255) if gy % 100 == 0 else (150, 0, 150), 1, cv2.LINE_AA)
    if a.scene:
        sc = np.load(wd_path(WD, 'scene.npz')); uv, z = tr.to_img(f, sc['route'])
        for (x, y), zz in zip(uv, z):
            if zz > 0 and 0 <= x < im.shape[1] and 0 <= y < im.shape[0]: cv2.circle(im, (int(x), int(y)), 2, (255, 140, 0), -1)
    for p in pts:
        uv, z = tr.to_img(f, p[None])
        if z[0] > 0 and np.all(np.abs(uv[0]) < 5000): cv2.circle(im, tuple(np.int32(uv[0])), 7, (0, 0, 255), 2)
    cv2.putText(im, f'f{f}', (10, 30), 0, 0.9, (0, 255, 255), 2)
    tiles.append(cv2.resize(im, (a.tile, int(a.tile * im.shape[0] / im.shape[1]))))
while len(tiles) % a.cols: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(wd_path(WD, a.out), np.vstack([np.hstack(tiles[i:i + a.cols]) for i in range(0, len(tiles), a.cols)]))
print('->', wd_path(WD, a.out))
