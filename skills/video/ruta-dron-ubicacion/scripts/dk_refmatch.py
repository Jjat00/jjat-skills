"""ubica una captura de referencia en el video: mejor frame + homografía captura->frame (SIFT)
  python3 dk_refmatch.py WD IMG f0,f1,step  -> imprime mejor frame y guarda WD/refH_<nombre>.npz"""
import sys, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dk_common import load_cfg, wd_path
WD, img, rng = sys.argv[1], sys.argv[2], sys.argv[3]
f0, f1, st = [int(v) for v in rng.split(',')]
cfg = load_cfg(WD); ref = cv2.imread(img, 0)
sift = cv2.SIFT_create(5000); kr, dr = sift.detectAndCompute(ref, None)
cap = cv2.VideoCapture(cfg['video']); best = None
def score(f):
    cap.set(cv2.CAP_PROP_POS_FRAMES, f); ok, im = cap.read(); g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    k, d = sift.detectAndCompute(g, None)
    m = cv2.BFMatcher().knnMatch(dr, d, k=2); good = [a for a, b in m if a.distance < 0.75 * b.distance]
    if len(good) < 8: return 0, None
    src = np.float32([kr[a.queryIdx].pt for a in good]); dst = np.float32([k[a.trainIdx].pt for a in good])
    H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 3.0); return int(inl.sum()), H
for f in range(f0, f1 + 1, st):
    n, H = score(f)
    if best is None or n > best[1]: best = (f, n, H)
fb = best[0]
for f in range(max(0, fb - st + 1), fb + st):
    n, H = score(f)
    if n > best[1]: best = (f, n, H)
name = os.path.splitext(os.path.basename(img))[0]
np.savez(wd_path(WD, f'refH_{name}.npz'), H=best[2], frame=best[0])
print(name, 'frame', best[0], 'inliers', best[1])
