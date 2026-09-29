"""Paso 2: cámara 3D con COLMAP (pycolmap) + poses por frame + control de calidad.
  python3 dk_sfm.py WD all            # extract, match, subset, map, perframe, qa
  python3 dk_sfm.py WD map --fix 651.5,512,288,0.0102   # re-mapear con intrínsecos fijos
Tiempos medidos (nube, 2 CPU, video 1024x576, 65 s): extract 7 min, match 14 min, map 22 min (171 keyframes), perframe 3 min.
Salidas: WD/sfm/sparse/0, WD/poses.npz (R,t por frame), WD/qa.json (tramos buenos / malos).
"""
import argparse, os, sys, json, time, sqlite3, shutil, numpy as np, cv2
from dk_common import wd_path, load_cfg, Gray

ap = argparse.ArgumentParser()
ap.add_argument('wd'); ap.add_argument('cmd', choices=['all', 'extract', 'match', 'subset', 'map', 'perframe', 'qa'])
ap.add_argument('--key-step', type=int, default=12, help='un keyframe cada N frames para el mapeo')
ap.add_argument('--fix', default='', help='intrínsecos fijos f,cx,cy,k (SIMPLE_RADIAL)')
ap.add_argument('--features', type=int, default=8000)
a = ap.parse_args()
WD = a.wd; S = wd_path(WD, 'sfm'); cfg = load_cfg(WD)
DB = wd_path(S, 'db.db'); DBK = wd_path(S, f'db_k{a.key_step}.db'); OUT = wd_path(S, 'sparse')
MAXI = 2147483647

def extract():
    import pycolmap
    t = time.time()
    ro = pycolmap.ImageReaderOptions(); ro.camera_model = 'SIMPLE_RADIAL'
    eo = pycolmap.FeatureExtractionOptions(); eo.sift.max_num_features = a.features; eo.sift.first_octave = -1
    eo.num_threads = os.cpu_count(); eo.use_gpu = False
    pycolmap.extract_features(DB, wd_path(S, 'images'), camera_mode=pycolmap.CameraMode.SINGLE, reader_options=ro, extraction_options=eo)
    print('extract %.0fs' % (time.time() - t), flush=True)

def match():
    import pycolmap
    t = time.time()
    mo = pycolmap.FeatureMatchingOptions(); mo.num_threads = os.cpu_count(); mo.use_gpu = False
    po = pycolmap.SequentialPairingOptions(); po.overlap = 12; po.quadratic_overlap = True
    pycolmap.match_sequential(DB, matching_options=mo, pairing_options=po)
    print('match %.0fs' % (time.time() - t), flush=True)

def subset():
    """copia la BD dejando solo 1 de cada key_step frames (image_names de pycolmap 4.2 no sirve para esto)"""
    c0 = sqlite3.connect(DB); c0.execute('PRAGMA wal_checkpoint(FULL)'); c0.close()
    shutil.copy(DB, DBK)
    c = sqlite3.connect(DBK)
    imgs = c.execute('select image_id,name from images').fetchall()
    base = min(int(n[2:7]) for _, n in imgs)
    keep = {i for i, n in imgs if (int(n[2:7]) - base) % a.key_step == 0}
    drop = [i for i, _ in imgs if i not in keep]
    for tb in ['matches', 'two_view_geometries']:
        rows = c.execute(f'select pair_id from {tb}').fetchall()
        c.executemany(f'delete from {tb} where pair_id=?', [(p,) for (p,) in rows if not (divmod(p, MAXI)[0] in keep and divmod(p, MAXI)[1] in keep)])
    fd = c.execute('select frame_id,data_id from frame_data').fetchall()
    dfr = [(f,) for f, d in fd if d not in keep]
    c.executemany('delete from frame_data where frame_id=?', dfr); c.executemany('delete from frames where frame_id=?', dfr)
    for tb in ['images', 'keypoints', 'descriptors']:
        c.executemany(f'delete from {tb} where image_id=?', [(i,) for i in drop])
    npair = c.execute('select count(*) from two_view_geometries where rows>15').fetchone()[0]
    if a.fix:
        c.execute('update cameras set params=?, prior_focal_length=1', (np.array([float(x) for x in a.fix.split(',')], np.float64).tobytes(),))
    c.commit(); print('keyframes', len(keep), 'pares útiles', npair, flush=True)
    if npair < len(keep): print('OJO: pocos pares; el emparejamiento secuencial crea pares a distancia 1,2,4,8... de imagen. key-step debe ser múltiplo de potencia de 2 del paso de imágenes (3 -> 6, 12, 24).')

def map_():
    import pycolmap
    if a.fix and os.path.exists(DBK):
        c = sqlite3.connect(DBK)
        c.execute('update cameras set params=?, prior_focal_length=1', (np.array([float(x) for x in a.fix.split(',')], np.float64).tobytes(),)); c.commit(); c.close()
    os.makedirs(OUT, exist_ok=True)
    opt = pycolmap.IncrementalPipelineOptions(); opt.num_threads = os.cpu_count(); opt.multiple_models = False
    opt.ba_global_max_num_iterations = 25; opt.ba_local_max_num_iterations = 15
    if a.fix:
        opt.ba_refine_focal_length = False; opt.ba_refine_extra_params = False; opt.ba_refine_principal_point = False
    t = time.time()
    recs = pycolmap.incremental_mapping(DBK, wd_path(S, 'images'), OUT, options=opt)
    print('map %.0fs' % (time.time() - t), flush=True)
    for k, r in recs.items(): print(k, r.summary())

def perframe():
    """pose de TODOS los frames: puntos 2D-3D de los dos keyframes vecinos seguidos con KLT + PnP"""
    import pycolmap
    rec = pycolmap.Reconstruction(wd_path(OUT, '0'))
    cam = list(rec.cameras.values())[0]; f, cx, cy, k1 = cam.params
    K = np.array([[f, 0, cx], [0, f, cy], [0, 0, 1.]]); dist = np.array([k1, 0, 0, 0, 0.])
    print('cámara', cam.params, flush=True)
    G = Gray(WD)
    kf = {}
    for im in rec.images.values():
        fr = int(im.name[2:7]); c = im.cam_from_world() if callable(im.cam_from_world) else im.cam_from_world
        p2 = []; p3 = []
        for p in im.points2D:
            if p.has_point3D(): p2.append(p.xy); p3.append(rec.points3D[p.point3D_id].xyz)
        kf[fr] = (c.rotation.matrix(), np.asarray(c.translation), np.float32(p2), np.float64(p3))
    keys = sorted(kf)
    lk = dict(winSize=(21, 21), maxLevel=4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 40, 0.01))
    def lkstep(A, B, cur):
        nx, st, _ = cv2.calcOpticalFlowPyrLK(A, B, cur, None, **lk)
        bk, st2, _ = cv2.calcOpticalFlowPyrLK(B, A, nx, None, **lk)
        fb = np.linalg.norm((cur - bk).reshape(-1, 2), axis=1)
        return nx, (st.ravel() == 1) & (st2.ravel() == 1) & (fb < 0.6)
    out = {}
    for kb, ka in zip(keys[:-1], keys[1:]):
        fw = {}; bw = {}
        _, _, p2, p3 = kf[kb]; cur = p2.reshape(-1, 1, 2).copy(); v = np.ones(len(p2), bool)
        for x in range(kb, ka - 1):
            cur, ok = lkstep(G[x], G[x + 1], cur); v &= ok; fw[x + 1] = (cur.reshape(-1, 2).copy(), v.copy(), p3)
        _, _, p2b, p3b = kf[ka]; cur = p2b.reshape(-1, 1, 2).copy(); v = np.ones(len(p2b), bool)
        for x in range(ka, kb + 1, -1):
            cur, ok = lkstep(G[x], G[x - 1], cur); v &= ok; bw[x - 1] = (cur.reshape(-1, 2).copy(), v.copy(), p3b)
        out[kb] = kf[kb][:2]
        for t in range(kb + 1, ka):
            q1, v1, A3 = fw[t]; q2, v2, B3 = bw[t]
            P2 = np.concatenate([q1[v1], q2[v2]]).astype(np.float64); P3 = np.concatenate([A3[v1], B3[v2]])
            R0, t0 = kf[kb if t - kb <= ka - t else ka][:2]
            ok, rv, tv, inl = cv2.solvePnPRansac(P3, P2, K, dist, rvec=cv2.Rodrigues(R0)[0], tvec=t0.reshape(3, 1).copy(),
                                                 useExtrinsicGuess=True, reprojectionError=1.5, iterationsCount=200)
            inl = inl.ravel(); rv, tv = cv2.solvePnPRefineLM(P3[inl], P2[inl], K, dist, rv, tv)
            out[t] = (cv2.Rodrigues(rv)[0], tv.ravel())
    out[keys[-1]] = kf[keys[-1]][:2]
    fr = np.array(sorted(out))
    np.savez(wd_path(WD, 'poses.npz'), frames=fr, R=np.stack([out[t][0] for t in fr]), t=np.stack([out[t][1] for t in fr]), K=K, dist=dist)
    np.savez(wd_path(WD, 'points3d.npz'), xyz=np.array([p.xyz for p in rec.points3D.values()]))
    print('poses', fr[0], '->', fr[-1], len(fr), flush=True)

def qa():
    """compara el giro de SfM contra el de la matriz esencial cada 60 frames: si difiere > 1°, ese tramo está doblado"""
    P = np.load(wd_path(WD, 'poses.npz')); idx = {int(f): i for i, f in enumerate(P['frames'])}; K = P['K']
    G = Gray(WD); sift = cv2.SIFT_create(5000)
    ang = lambda R: np.degrees(np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1)))
    rows = []; fr = P['frames']
    for f in range(int(fr[0]), int(fr[-1]) - 60, 60):
        g = f + 60
        ka, da = sift.detectAndCompute(G[f], None); kb, db = sift.detectAndCompute(G[g], None)
        m = [x for x, y in cv2.BFMatcher().knnMatch(da, db, k=2) if x.distance < 0.75 * y.distance]
        pa = np.float64([ka[x.queryIdx].pt for x in m]); pb = np.float64([kb[x.trainIdx].pt for x in m])
        E, _ = cv2.findEssentialMat(pa, pb, K, cv2.RANSAC, 0.999, 1.0); _, Re, _, _ = cv2.recoverPose(E, pa, pb, K)
        Rs = P['R'][idx[g]] @ P['R'][idx[f]].T
        Ca = -P['R'][idx[f]].T @ P['t'][idx[f]]; Cb = -P['R'][idx[g]].T @ P['t'][idx[g]]
        rows.append(dict(f=f, g=g, sfm=round(ang(Rs), 2), ess=round(ang(Re), 2), diff=round(ang(Rs @ Re.T), 2), step=round(float(np.linalg.norm(Cb - Ca)), 4)))
        print(rows[-1], flush=True)
    steps = np.array([r['step'] for r in rows]); med = float(np.median(steps))
    for r in rows: r['ok'] = bool(r['diff'] < 1.0 and r['step'] < 2.5 * med)
    good = []; cur = None
    for r in rows:
        if r['ok']:
            cur = [r['f'], r['g']] if cur is None else [cur[0], r['g']]
        elif cur: good.append(cur); cur = None
    if cur: good.append(cur)
    json.dump(dict(rows=rows, good_ranges=good), open(wd_path(WD, 'qa.json'), 'w'), indent=1)
    print('TRAMOS BUENOS:', good)

if __name__ == '__main__':
    steps = {'extract': [extract], 'match': [match], 'subset': [subset], 'map': [map_], 'perframe': [perframe], 'qa': [qa],
             'all': [extract, match, subset, map_, perframe, qa]}[a.cmd]
    for s in steps: s()
