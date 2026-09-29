"""Paso 1: preparar el video.
  python3 dk_prep.py VIDEO WD [--start 8] [--end 76] [--sheet 5]
Crea: WD/project.json, WD/contact.jpg (hoja con tiempos), WD/gray.npy (+meta) y WD/sfm/images (1 de cada 3 frames).
"""
import argparse, os, json, numpy as np, cv2
from dk_common import save_cfg, wd_path

ap = argparse.ArgumentParser()
ap.add_argument('video'); ap.add_argument('wd')
ap.add_argument('--start', type=float, default=0.0, help='segundo inicial del tramo útil')
ap.add_argument('--end', type=float, default=None, help='segundo final del tramo útil')
ap.add_argument('--sheet', type=float, default=5.0, help='cada cuántos segundos va una miniatura en la hoja')
ap.add_argument('--sfm-step', type=int, default=3)
a = ap.parse_args()
os.makedirs(wd_path(a.wd, 'sfm', 'images'), exist_ok=True)
cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
f0 = int(a.start * fps); f1 = min(n - 1, int((a.end if a.end else n / fps) * fps))
cfg = dict(video=os.path.abspath(a.video), fps=fps, w=W, h=H, n_frames=n, f0=f0, f1=f1, sfm_step=a.sfm_step)
save_cfg(a.wd, cfg)
print(json.dumps(cfg, indent=1))
gray = np.lib.format.open_memmap(wd_path(a.wd, 'gray.npy'), mode='w+', dtype=np.uint8, shape=(f1 - f0 + 1, H, W))
json.dump({'f0': f0}, open(wd_path(a.wd, 'gray_meta.json'), 'w'))
thumbs = []; every = max(1, int(round(a.sheet * fps)))
i = 0
while True:
    ok, im = cap.read()
    if not ok or i > f1: break
    if i % every == 0:
        t = cv2.resize(im, (320, int(320 * H / W)))
        cv2.putText(t, f'{i / fps:5.1f}s f{i}', (6, 18), 0, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        thumbs.append(t)
    if i >= f0:
        gray[i - f0] = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        if (i - f0) % a.sfm_step == 0:
            cv2.imwrite(wd_path(a.wd, 'sfm', 'images', f'f_{i:05d}.png'), im)
    i += 1
gray.flush()
cols = 6
while len(thumbs) % cols: thumbs.append(np.zeros_like(thumbs[0]))
sheet = np.vstack([np.hstack(thumbs[k:k + cols]) for k in range(0, len(thumbs), cols)])
cv2.imwrite(wd_path(a.wd, 'contact.jpg'), sheet, [cv2.IMWRITE_JPEG_QUALITY, 85])
print('frames', f0, '->', f1, '| imágenes SfM:', len(os.listdir(wd_path(a.wd, 'sfm', 'images'))))
