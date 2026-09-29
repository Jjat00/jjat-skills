"""dronekit - renderizador de la ruta animada sobre el video del dron.

Lee de <kit>: params.json, cams.npz (N plano->cámara por frame), scene.npz (ruta en metros), fuentes .ttf.
Escribe en <out>:
  final{tag}.mp4    compuesto listo para publicar (H.264 CRF 16)
  plate{tag}.mp4    fondo retimeado, escalado a 1080p y con color
  overlay{tag}.mov  gráficos con alfa (ProRes 4444) alineados con plate
  (--tail) final_tail.mp4 / plate_tail.mp4 / overlay_tail.mov / endcard.mov  -> cierre de marca

Uso:
  python3 render_route.py KIT OUT --src 330,900,1800      # previews JPG de esos frames del video original
  python3 render_route.py KIT OUT --range 0,120           # un tramo (en frames de salida)
  python3 render_route.py KIT OUT --tail                  # cierre
  python3 render_route.py KIT OUT --scale 0.5 --range 0,99999   # versión rápida de baja resolución
"""
import sys, os, json, math, subprocess, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ap = argparse.ArgumentParser()
ap.add_argument('kit'); ap.add_argument('out')
ap.add_argument('--frames', default='')          # output frame indices to dump as PNG previews
ap.add_argument('--src', default='')             # source frame numbers to preview (nearest output frame)
ap.add_argument('--params', default='params.json')
ap.add_argument('--range', default='')   # a,b output frames (chunked render)
ap.add_argument('--tail', action='store_true')  # render end-card section only
ap.add_argument('--no-video', action='store_true')
ap.add_argument('--scale', type=float, default=1.0)  # render scale (0.5 for fast previews)
args = ap.parse_args()
KIT, OUT = args.kit, args.out
os.makedirs(OUT, exist_ok=True)
P = json.load(open(os.path.join(KIT, args.params)))
CAM = np.load(os.path.join(KIT, P.get('cams', 'cams.npz')))
SC = np.load(os.path.join(KIT, P.get('scene', 'scene.npz')))

OUT_W, OUT_H = P.get('out_size', [1920, 1080])
W, H = int(OUT_W * args.scale), int(OUT_H * args.scale)
SS = 2                                    # supersampling for vector layers
from fractions import Fraction
_cap = cv2.VideoCapture(os.path.join(KIT, P['source'])); _fps = _cap.get(cv2.CAP_PROP_FPS); _cap.release()
FPS_Q = Fraction(_fps).limit_denominator(1001); FPS = float(FPS_Q)
_cap = cv2.VideoCapture(os.path.join(KIT, P['source']))
SRC_W, SRC_H = int(_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); _cap.release()
if abs(SRC_W / SRC_H - W / H) > 0.01:
    sys.exit(f'El video fuente ({SRC_W}x{SRC_H}) y out_size ({OUT_W}x{OUT_H}) deben tener la misma proporción; para 9:16 recortar después en Resolve.')
KX = W / SRC_W

# ---------------- camera (plane homographies) ----------------
cam_frames = CAM['frames']; cam_N = CAM['N']
K0 = CAM['K']; k1 = float(CAM['dist'][0])
fi = {int(f): i for i, f in enumerate(cam_frames)}

def camera(src_frame):
    return cam_N[fi[int(src_frame)]], None

def project(Xp, N, _unused=None, s=1.0):
    """plane points (M,2) in meters -> pixel coords at output res * s, plus validity"""
    q = np.c_[Xp, np.ones(len(Xp))] @ N.T
    z = q[:, 2]
    front = z > 1e-9
    zz = np.where(front, z, 1.0)
    x = q[:, 0] / zz; y = q[:, 1] / zz
    r2 = x * x + y * y
    d = 1 + k1 * np.minimum(r2, 4.0)
    u = (K0[0, 0] * x * d + K0[0, 2]) * KX * s
    v = (K0[1, 1] * y * d + K0[1, 2]) * KX * s
    uv = np.stack([u, v], 1)
    front &= np.all(np.abs(uv) < 2.5e4 * s, axis=1)
    return uv, front

# ---------------- scene (plane coords, meters) ----------------
C = SC['route']            # (N,2) centerline
Sarc = SC['s']
Lat = SC['lateral']        # (N,2)
U = 1.0
FB = SC['dest'] if 'dest' in SC.files else SC['frostbyte']   # destino (2,); 'frostbyte' es el nombre de la clave en kits viejos
START = C[0]
L_TOTAL = float(Sarc[-1])

def route_at(s):
    s = np.clip(s, 0, L_TOTAL)
    i = np.clip(np.searchsorted(Sarc, s) - 1, 0, len(Sarc) - 2)
    a = (s - Sarc[i]) / np.maximum(Sarc[i + 1] - Sarc[i], 1e-9)
    p = C[i] + (C[i + 1] - C[i]) * a[..., None]
    lat = Lat[i] + (Lat[i + 1] - Lat[i]) * a[..., None]
    lat /= np.linalg.norm(lat, axis=-1, keepdims=True)
    return p, lat

# ---------------- timing ----------------
def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2

def ease_out_back(x, k=1.6):
    x = min(max(x, 0.0), 1.0)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2

def smoothstep(a, b, x):
    x = min(max((x - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)

# output frame -> source frame (retime with speed ramp)
def speed_at(ts):
    keys = P['speed_keys']
    if ts <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t0 <= ts < t1:
            return v0 + (v1 - v0) * smoothstep(t0, t1, ts)
    return keys[-1][1]

def build_timeline():
    s = P['src_start'] * FPS; end = P['src_end'] * FPS
    src = []; blend = []
    while s < end:
        src.append(int(s)); blend.append(s - int(s))
        s += speed_at(s / FPS)
    return src, blend

SRC, SRC_FRAC = build_timeline()
_miss = [f for f in (SRC[0], SRC[-1]) if int(f) not in fi]
if _miss:
    sys.exit(f'src_start/src_end salen del rango con cámara ({int(cam_frames[0])}-{int(cam_frames[-1])} frames = '
             f'{cam_frames[0] / FPS:.1f}-{cam_frames[-1] / FPS:.1f} s). Ajustar params.json.')
N_OUT = len(SRC)
t_src = lambda k: SRC[k] / FPS           # source seconds at output frame k
t_out = lambda k: k / FPS

# ---------------- colors (BGR) ----------------
def hex2bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)
COL = hex2bgr(P['color'])          # main blue
COL_L = hex2bgr(P['color_light'])  # light blue
WHITE = np.array([255, 255, 255], np.float32)

# ---------------- layer drawing helpers ----------------
def poly_px(uv, s):
    return np.int32(np.round(uv * 8))  # 3 fractional bits for cv2 shift

def fill(mask, polys, val=255):
    if polys:
        cv2.fillPoly(mask, polys, val, lineType=cv2.LINE_AA, shift=3)

def runs(valid):
    """contiguous True runs -> list of (i0, i1) inclusive"""
    out = []; i = 0; n = len(valid)
    while i < n:
        if valid[i]:
            j = i
            while j + 1 < n and valid[j + 1]: j += 1
            out.append((i, j)); i = j + 1
        else:
            i += 1
    return out

def ribbon(mask, s0, s1, off0, off1, R, t, step_m=None, val=255):
    """fill ground ribbon between arc length s0..s1, lateral offsets off0..off1 (meters)"""
    if s1 <= s0: return
    step_m = step_m or P['sample_m']
    n = max(2, int((s1 - s0) / step_m) + 1)
    ss = np.linspace(s0, s1, n)
    p, lat = route_at(ss)
    A = p + lat * off0 * U; B = p + lat * off1 * U
    ua, fa = project(A, R, t, SS); ub, fb = project(B, R, t, SS)
    v = fa & fb
    polys = []
    for i0, i1 in runs(v):
        if i1 - i0 < 1: continue
        poly = np.concatenate([ua[i0:i1 + 1], ub[i0:i1 + 1][::-1]])
        polys.append(poly_px(poly, SS))
    fill(mask, polys, val)

def ground_ring(mask, center, r_out_m, r_in_m, R, t, n=96, val=255):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    circ = lambda r: center[None, :] + np.c_[np.cos(ang), np.sin(ang)] * r
    uo, fo = project(circ(r_out_m), R, t, SS)
    if not fo.all(): return
    polys = [poly_px(uo, SS)]
    if r_in_m > 0:
        ui, fi_ = project(circ(r_in_m), R, t, SS)
        if not fi_.all(): return
        polys.append(poly_px(ui, SS))
    fill(mask, polys, val)

def chevrons(mask, s_max, phase, R, t, val=255):
    w = P['band_w']; sp = P['chev_spacing']; ln = P['chev_len']; th = P['chev_thick']
    half = w * 0.30
    s_c = phase % sp
    polys = []
    while s_c < s_max - 2:
        if s_c > ln + 2:
            loc = np.array([[s_c - ln, -half], [s_c, 0], [s_c - ln, half],
                            [s_c - ln - th, half], [s_c - th, 0], [s_c - ln - th, -half]])
            p, lat = route_at(loc[:, 0])
            X = p + lat * loc[:, 1:2] * U
            uv, f = project(X, R, t, SS)
            if f.all(): polys.append(poly_px(uv, SS))
        s_c += sp
    for pl in polys:
        fill(mask, [pl], val)

def down(m):
    return cv2.resize(m, (W, H), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0

# ---------------- card sprite ----------------
# fuentes: font_title / font_body en params.json (nombre del .ttf en el KIT); por defecto Poppins
FONT_B = os.path.join(KIT, P.get('font_title', 'Poppins-Bold.ttf')); FONT_M = os.path.join(KIT, P.get('font_body', 'Poppins-Medium.ttf'))
for _f in (FONT_B, FONT_M):
    if not os.path.exists(_f): sys.exit(f'Falta la fuente {_f}: cópiala de assets/fonts/ al KIT')

def make_card(title, subtitle, scale):
    S = 2
    ft = ImageFont.truetype(FONT_B, int(44 * scale * S)); fs = ImageFont.truetype(FONT_M, int(20 * scale * S))
    tmp = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    sp_t = int(3 * scale * S)
    tw = sum(tmp.textlength(c, font=ft) for c in title) + sp_t * (len(title) - 1)
    sw = tmp.textlength(subtitle, font=fs)
    icon = int(60 * scale * S); px, py = int(22 * scale * S), int(18 * scale * S); gap = int(18 * scale * S)
    bw = int(px + icon + gap + max(tw, sw) + px); bh = int(py * 2 + icon)
    sh = int(28 * scale * S); tip = int(12 * scale * S)
    Wc, Hc = bw + 2 * sh, bh + 2 * sh + tip
    im = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0))
    shadow = Image.new('RGBA', (Wc, Hc), (0, 0, 0, 0)); ds = ImageDraw.Draw(shadow)
    ds.rounded_rectangle([sh, sh + 8 * S, sh + bw, sh + bh + 8 * S], radius=int(20 * scale * S), fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12 * S * scale)); im.alpha_composite(shadow)
    d = ImageDraw.Draw(im)
    x0, y0 = sh, sh
    navy = tuple(P['card_bg']) + (236,)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=int(20 * scale * S), fill=navy,
                        outline=(130, 195, 255, 110), width=max(2, int(1.5 * S)))
    cxm = x0 + bw // 2
    d.polygon([(cxm - tip, y0 + bh - 1), (cxm + tip, y0 + bh - 1), (cxm, y0 + bh + tip)], fill=navy)
    # icon: gradient circle + pin
    cx, cy = x0 + px + icon // 2, y0 + bh // 2
    g = Image.new('RGBA', (icon, icon), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    c0 = np.array(P['icon_top']); c1 = np.array(P['icon_bottom'])
    for i in range(icon // 2, 0, -1):
        q = i / (icon / 2); c = tuple(int(v) for v in (c0 * (1 - q) + c1 * q))
        gd.ellipse([icon / 2 - i, icon / 2 - i, icon / 2 + i, icon / 2 + i], fill=c + (255,))
    im.alpha_composite(g, (cx - icon // 2, cy - icon // 2))
    pw = int(icon * 0.40); ph = int(icon * 0.52); pin = Image.new('RGBA', (pw * 4, ph * 4), (0, 0, 0, 0)); pd = ImageDraw.Draw(pin)
    r = pw * 2; pd.ellipse([0, 0, pw * 4 - 1, pw * 4 - 1], fill=(255, 255, 255, 255))
    pd.polygon([(pw * 4 * .10, r * 1.30), (pw * 4 * .90, r * 1.30), (pw * 2, ph * 4 - 1)], fill=(255, 255, 255, 255))
    ir = r * 0.42; pd.ellipse([r - ir, r - ir, r + ir, r + ir], fill=(0, 0, 0, 0))
    pin = pin.resize((pw, ph), Image.LANCZOS); im.alpha_composite(pin, (cx - pw // 2, cy - ph // 2 - int(1 * S)))
    tx = x0 + px + icon + gap
    bt = ft.getbbox(title); th = bt[3] - bt[1]; bs = fs.getbbox(subtitle); shh = bs[3] - bs[1]
    tot = th + int(10 * S * scale) + shh
    x = tx; y = cy - tot // 2 - bt[1]
    for ch in title:
        d.text((x, y), ch, font=ft, fill=(255, 255, 255, 255)); x += d.textlength(ch, font=ft) + sp_t
    d.text((tx, cy - tot // 2 + th + int(10 * S * scale) - bs[1] + int(2 * S)), subtitle, font=fs, fill=tuple(P['sub_color']) + (255,))
    im = im.resize((Wc // S, Hc // S), Image.LANCZOS)
    arr = np.asarray(im).astype(np.float32) / 255.0   # RGBA
    anchor = ((sh + bw / 2) / S, (sh + bh + tip) / S)  # tip point
    return arr, anchor

CARD, CARD_ANCHOR = make_card(P['title'], P['subtitle'], args.scale)

def paste_rgba(dst_rgb, dst_a, spr, x, y, alpha=1.0, scale=1.0):
    """composite straight-alpha RGBA sprite (float) onto premultiplied layer (dst_rgb premult BGR, dst_a)"""
    if scale != 1.0:
        hh, ww = spr.shape[:2]
        spr = cv2.resize(spr, (max(1, int(ww * scale)), max(1, int(hh * scale))), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    hh, ww = spr.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    xa, ya = max(0, x0), max(0, y0); xb, yb = min(W, x0 + ww), min(H, y0 + hh)
    if xa >= xb or ya >= yb: return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]
    a = s[..., 3:4] * alpha
    rgb = s[..., [2, 1, 0]] * 255.0
    dst_rgb[ya:yb, xa:xb] = rgb * a + dst_rgb[ya:yb, xa:xb] * (1 - a)
    dst_a[ya:yb, xa:xb] = a[..., 0] + dst_a[ya:yb, xa:xb] * (1 - a[..., 0])

# ---------------- background ----------------
def get_bg(src, k):
    f = SRC[k]; a = src.get(f).astype(np.float32)
    sp = speed_at(f / FPS)
    if sp > 1.4:
        b = src.get(f + 1).astype(np.float32)
        a = a * 0.6 + b * 0.4
    return np.clip(a, 0, 255).astype(np.uint8)

class Source:
    def __init__(self, path):
        self.cap = cv2.VideoCapture(path); self.pos = -1; self.img = None
    def get(self, f):
        if f < self.pos or f > self.pos + 90:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, f); self.pos = f - 1
        while self.pos < f:
            ok, im = self.cap.read(); self.pos += 1
            if ok: self.img = im
        return self.img

LUT = None
def grade(img):
    global LUT
    up = cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    bl = cv2.GaussianBlur(up, (0, 0), 1.6 * args.scale)
    up = up + (up - bl) * P['sharpen']
    # contrast / saturation
    g = P['grade']
    x = np.clip(up / 255.0, 0, 1)
    x = 0.5 + (x - 0.5) * g['contrast'] + g['brightness']
    lum = (x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299)[..., None]
    x = lum + (x - lum) * g['saturation']
    x = np.clip(x, 0, 1) ** g['gamma']
    # slight cool shadows / warm highlights
    x[..., 0] += g['cool_shadows'] * (1 - lum[..., 0]) ** 2
    x[..., 2] += g['warm_highlights'] * lum[..., 0] ** 2
    return np.clip(x * 255, 0, 255)

VIG = None
def vignette(img):
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        VIG = (1 - P['vignette'] * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None]
    return img * VIG

def draw_marker(rgb, a, emis, center, vis, tt_out, R, tt, n_rings=1, speed=1.0, big=1.0):
    WS, HS = W * SS, H * SS
    dr = P['dot_r']
    m_out = np.zeros((HS, WS), np.uint8); ground_ring(m_out, center, dr, 0, R, tt)
    m_core = np.zeros((HS, WS), np.uint8); ground_ring(m_core, center, dr * 0.42, 0, R, tt)
    rg = np.zeros((HS, WS), np.uint8)
    for j in range(n_rings):
        ph = (tt_out * speed + j / n_rings) % 1.0
        r = dr + ph * P['ring_r'] * big
        ground_ring(rg, center, r, max(0.0, r - 0.55), R, tt, val=int(255 * (1 - ph) ** 1.4))
    Mo = down(m_out) * vis * 0.92; Mc = down(m_core) * vis; Rg = down(rg) * vis
    for lay, col in ((Rg, COL_L), (Mo, COL), (Mc, WHITE)):
        rgb = col * lay[..., None] + rgb * (1 - lay[..., None]); a = lay + a * (1 - lay)
    emis = emis + COL_L * (Rg * 1.1 + Mo * 0.9)[..., None] + WHITE * (Mc * 0.6)[..., None]
    return rgb, a, emis

# ---------------- per-frame overlay ----------------
def overlay_frame(k):
    """returns premultiplied BGR (float 0..255), alpha (0..1), emissive (for bloom) BGR float"""
    ts = t_src(k); R, tt = camera(SRC[k])
    WS, HS = W * SS, H * SS
    # route head
    d0, d1 = P['draw_src'][0], P['draw_src'][1]
    prog = ease_io((ts - d0) / (d1 - d0))
    s_head = prog * L_TOTAL
    fade_all = smoothstep(P['src_end'] - 0.8, P['src_end'] - 0.05, ts) if P.get('fade_route_at_end') else 0.0
    rgb = np.zeros((H, W, 3), np.float32); a = np.zeros((H, W), np.float32); emis = np.zeros((H, W, 3), np.float32)
    wband = P['band_w']
    if s_head > 0.5:
        m_band = np.zeros((HS, WS), np.uint8); ribbon(m_band, 0, s_head, -wband / 2, wband / 2, R, tt)
        cap_c = route_at(np.array([s_head]))[0][0]
        ground_ring(m_band, cap_c, wband / 2, 0, R, tt)            # rounded head / end cap
        ground_ring(m_band, C[0], wband / 2, 0, R, tt)             # rounded start cap
        m_edge = np.zeros((HS, WS), np.uint8)
        e = P['edge_w']
        ribbon(m_edge, 0, s_head, -wband / 2, -wband / 2 + e, R, tt)
        ribbon(m_edge, 0, s_head, wband / 2 - e, wband / 2, R, tt)
        m_chev = np.zeros((HS, WS), np.uint8)
        chevrons(m_chev, s_head, P['chev_speed'] * t_out(k), R, tt)
        # hot head: graded ribbons over last hot_len meters
        m_hot = np.zeros((HS, WS), np.uint8)
        hl = P['hot_len']; nseg = 14
        if prog < 1.0:
            for j in range(nseg):
                sa = s_head - hl * (1 - j / nseg); sb = s_head - hl * (1 - (j + 1) / nseg)
                ribbon(m_hot, max(0, sa), max(0, sb), -wband / 2, wband / 2, R, tt, step_m=1.0, val=int(40 + 215 * ((j + 1) / nseg) ** 2))
        B = down(m_band); E = down(m_edge); Cv = down(m_chev); Ht = down(m_hot)
        ab = B * P['band_alpha']
        rgb = COL * ab[..., None]; a = ab.copy()
        # edges
        ae = E * P['edge_alpha']
        rgb = COL_L * ae[..., None] + rgb * (1 - ae[..., None]); a = ae + a * (1 - ae)
        # chevrons
        ac = Cv * P['chev_alpha']
        rgb = (COL_L * 0.35 + WHITE * 0.65) * ac[..., None] + rgb * (1 - ac[..., None]); a = ac + a * (1 - ac)
        # head
        rgb = WHITE * Ht[..., None] + rgb * (1 - Ht[..., None]); a = Ht + a * (1 - Ht)
        emis = COL * (B * 0.35)[..., None] + COL_L * (E * 0.9 + Cv * 0.8)[..., None] + (WHITE * 0.6 + COL_L * 0.4) * (Ht * 1.4)[..., None]
        # head flare (screen space)
        if 0 < prog < 1:
            ph, fh = project(route_at(np.array([s_head]))[0], R, tt, 1)
            if fh[0]:
                fl = np.zeros((H, W), np.float32)
                cv2.circle(fl, tuple(np.int32(ph[0])), max(2, int(5 * args.scale)), 1.0, -1, cv2.LINE_AA)
                fl = cv2.GaussianBlur(fl, (0, 0), 6 * args.scale) * 3.0
                emis += (WHITE * 0.8 + COL_L * 0.2) * np.clip(fl, 0, 1)[..., None] * 1.5
    # start marker
    st_in = smoothstep(P['start_marker_src'], P['start_marker_src'] + 0.5, ts)
    st_out = 1 - smoothstep(P['start_marker_off_src'], P['start_marker_off_src'] + 0.6, ts)
    stv = st_in * st_out
    if stv > 0.01:
        rgb, a, emis = draw_marker(rgb, a, emis, START, stv, t_out(k), R, tt, n_rings=1, speed=0.9)
    # end marker + beam + card
    arrive = d1 - 0.15
    ev = smoothstep(arrive, arrive + 0.4, ts)
    if ev > 0.01:
        rgb, a, emis = draw_marker(rgb, a, emis, FB, ev, t_out(k), R, tt, n_rings=2, speed=0.7, big=1.3)
        # beam: vertical 3D line from ground up beam_h meters
        base, fb0 = project(FB[None], R, tt, 1)
        side, fb1 = project(np.array([FB + np.array(P['beam_dir'])]), R, tt, 1)
        top = base.copy()
        if fb0[0] and fb1[0]:
            top[0, 1] = base[0, 1] - np.linalg.norm(side[0] - base[0]) * P['beam_h']
        if fb0[0] and fb1[0]:
            b = base[0]; tp = top[0]
            grow = ease_io((ts - arrive) / 0.5)
            tp_draw = b + (tp - b) * grow
            # clamp so the card stays on screen
            ch, cw = CARD.shape[0], CARD.shape[1]
            min_tip_y = ch - (ch - CARD_ANCHOR[1]) + 18 * args.scale
            if tp_draw[1] < min_tip_y: tp_draw = np.array([tp_draw[0], min_tip_y])
            lay = np.zeros((H * SS, W * SS), np.uint8)
            cv2.line(lay, tuple(np.int32(b * SS * 8)), tuple(np.int32(tp_draw * SS * 8)), 255, max(1, int(2.2 * args.scale * SS)), cv2.LINE_AA, 3)
            Ln = down(lay) * ev
            # gradient: brighter at the base
            yy = np.linspace(0, 1, H)[:, None]
            span = max(1.0, b[1] - tp_draw[1])
            g = np.clip(0.55 + 0.45 * (yy * H - tp_draw[1]) / span, 0.55, 1.0).astype(np.float32)
            Ln = Ln * g
            rgb = WHITE * Ln[..., None] + rgb * (1 - Ln[..., None]); a = Ln + a * (1 - Ln)
            emis += (COL_L * 0.7 + WHITE * 0.3) * Ln[..., None] * 1.6
            # card
            cv_ = smoothstep(arrive + 0.35, arrive + 0.85, ts)
            if cv_ > 0.001:
                sc = 0.82 + 0.18 * ease_out_back((ts - arrive - 0.35) / 0.55)
                cx = tp_draw[0] - CARD_ANCHOR[0] * sc
                cy = tp_draw[1] - CARD_ANCHOR[1] * sc - 4 * args.scale
                cx = np.clip(cx, 16 * args.scale, W - CARD.shape[1] * sc - 16 * args.scale)
                paste_rgba(rgb, a, CARD, cx, cy, alpha=cv_, scale=sc)
    if fade_all > 0:
        rgb *= (1 - fade_all); a *= (1 - fade_all); emis *= (1 - fade_all)
    return rgb, a, emis

def bloom(emis):
    b1 = cv2.GaussianBlur(emis, (0, 0), 5 * args.scale)
    b2 = cv2.GaussianBlur(cv2.resize(emis, (W // 4, H // 4), interpolation=cv2.INTER_AREA), (0, 0), 6 * args.scale)
    b2 = cv2.resize(b2, (W, H), interpolation=cv2.INTER_LINEAR)
    return (b1 * P['bloom_small'] + b2 * P['bloom_large'])

def composite(bg, rgb, a, emis, bl=None):
    out = bg * (1 - a[..., None]) + rgb
    if bl is None: bl = bloom(emis)
    out = 255 - (255 - out) * (1 - np.clip(bl / 255.0, 0, 1))   # screen blend
    return np.clip(out, 0, 255)

def overlay_rgba(rgb, a, emis, bl=None):
    """straight-alpha RGBA for editing software: layer + bloom approximated as colored alpha"""
    if bl is None: bl = bloom(emis)
    bl = np.clip(bl / 255.0, 0, 1)
    ba = np.clip(bl.max(axis=2), 0, 1)
    bl_col = np.where(ba[..., None] > 1e-4, bl * 255.0 / np.maximum(ba[..., None], 1e-4), 0)
    prem = rgb + bl_col * ba[..., None] * (1 - a[..., None])
    A = a + ba * (1 - a)
    col = np.where(A[..., None] > 1e-4, prem / np.maximum(A[..., None], 1e-4), 0)
    return np.dstack([np.clip(col, 0, 255), np.clip(A * 255, 0, 255)]).astype(np.uint8)  # BGRA

# ---------------- end card ----------------
def endcard_frame(j, n):
    """BGRA end card frame j of n (dark scrim + centered title)"""
    tt = j / FPS
    arr = np.zeros((H, W, 4), np.float32)
    scrim = smoothstep(0, 0.5, tt) * 0.62
    arr[..., :3] = np.array(P['card_bg'][::-1], np.float32) * 0.6
    arr[..., 3] = scrim
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(FONT_B, int(110 * args.scale)); fs = ImageFont.truetype(FONT_M, int(34 * args.scale)); fh = ImageFont.truetype(FONT_M, int(30 * args.scale))
    ap_t = ease_out_back((tt - 0.25) / 0.6, 1.2); op_t = smoothstep(0.2, 0.6, tt)
    op_s = smoothstep(0.55, 0.95, tt); op_h = smoothstep(0.8, 1.2, tt)
    title = P['title']; sp = int(10 * args.scale)
    tw = sum(d.textlength(c, font=ft) for c in title) + sp * (len(title) - 1)
    x = (W - tw) / 2; y = H * 0.40 + (1 - ap_t) * 30 * args.scale
    for ch in title:
        d.text((x, y), ch, font=ft, fill=(255, 255, 255, int(255 * op_t)), anchor='ls'); x += d.textlength(ch, font=ft) + sp
    # accent line
    lw = 90 * args.scale * smoothstep(0.45, 0.9, tt)
    d.rounded_rectangle([W / 2 - lw, H * 0.40 + 34 * args.scale, W / 2 + lw, H * 0.40 + 40 * args.scale], radius=3, fill=tuple(P['icon_bottom']) + (int(255 * op_s),))
    d.text((W / 2, H * 0.40 + 92 * args.scale), P['subtitle'], font=fs, fill=tuple(P['sub_color']) + (int(255 * op_s),), anchor='ms')
    if P.get('handle'):
        d.text((W / 2, H * 0.40 + 150 * args.scale), P['handle'], font=fh, fill=(255, 255, 255, int(210 * op_h)), anchor='ms')
    spr = np.asarray(im).astype(np.float32) / 255.0
    sa = spr[..., 3:4]
    col = arr[..., :3] * (1 - sa) * arr[..., 3:4] + spr[..., [2, 1, 0]] * 255 * sa
    A = sa[..., 0] + arr[..., 3] * (1 - sa[..., 0])
    colS = np.where(A[..., None] > 1e-4, col / np.maximum(A[..., None], 1e-4), 0)
    return np.dstack([colS, A * 255]).clip(0, 255).astype(np.uint8), col, A

# ---------------- main ----------------
def ff(path, pix_in, extra):
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', pix_in,
           '-s', f'{W}x{H}', '-r', f'{FPS_Q.numerator}/{FPS_Q.denominator}', '-i', 'pipe:0'] + extra + [path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)

if __name__ == '__main__':
    src = Source(os.path.join(KIT, P['source']))
    dump = [int(x) for x in args.frames.split(',') if x.strip()]
    for sf in [int(x) for x in args.src.split(',') if x.strip()]:
        dump.append(int(np.argmin(np.abs(np.array(SRC) - sf))))
    print('output frames:', N_OUT, 'duration %.2fs' % (N_OUT / FPS), flush=True)
    if dump:
        for k in dump:
            k = min(k, N_OUT - 1)
            bg = vignette(grade(get_bg(src, k)))
            rgb, a, emis = overlay_frame(k)
            cv2.imwrite(os.path.join(OUT, f'prev_{k:04d}.jpg'), composite(bg, rgb, a, emis).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
        sys.exit(0)
    endN = int(P['endcard_sec'] * FPS)
    X264F = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p']
    X264P = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p']
    PR4444 = ['-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le', '-alpha_bits', '16', '-vendor', 'apl0']
    if not args.tail:
        a0, a1 = (0, N_OUT)
        if args.range:
            a0, a1 = [int(x) for x in args.range.split(',')]; a1 = min(a1, N_OUT)
        tag = f'_{a0:05d}' if args.range else ''
        p_final = ff(os.path.join(OUT, f'final{tag}.mp4'), 'bgr24', X264F)
        p_plate = ff(os.path.join(OUT, f'plate{tag}.mp4'), 'bgr24', X264P)
        p_ovl = ff(os.path.join(OUT, f'overlay{tag}.mov'), 'bgra', PR4444)
        for k in range(a0, a1):
            bg = vignette(grade(get_bg(src, k)))
            rgb, a, emis = overlay_frame(k)
            bl = bloom(emis)
            p_final.stdin.write(composite(bg, rgb, a, emis, bl).astype(np.uint8).tobytes())
            p_plate.stdin.write(bg.astype(np.uint8).tobytes())
            p_ovl.stdin.write(overlay_rgba(rgb, a, emis, bl).tobytes())
            if k % 30 == 0: print(f'frame {k}/{N_OUT}', flush=True)
        for p in (p_final, p_plate, p_ovl):
            p.stdin.close(); p.wait()
        print('done range', a0, a1, flush=True)
        sys.exit(0)
    # ---- tail: end card over a slow push-in on the last frame ----
    k = N_OUT - 1
    bg = vignette(grade(get_bg(src, k)))
    rgb, a, emis = overlay_frame(k)
    bl = bloom(emis)
    base = composite(bg, rgb, a, emis, bl)
    ov0 = overlay_rgba(rgb, a, emis, bl)
    p_final = ff(os.path.join(OUT, 'final_tail.mp4'), 'bgr24', X264F)
    p_plate = ff(os.path.join(OUT, 'plate_tail.mp4'), 'bgr24', X264P)
    p_ovl = ff(os.path.join(OUT, 'overlay_tail.mov'), 'bgra', PR4444)
    p_end = ff(os.path.join(OUT, 'endcard.mov'), 'bgra', PR4444)
    for j in range(endN):
        z = 1 + 0.03 * (j / endN)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
        fr = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        pl = cv2.warpAffine(bg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ov = cv2.warpAffine(ov0, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        ec, col, A = endcard_frame(j, endN)
        out = fr * (1 - A[..., None]) + col
        p_final.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
        p_plate.stdin.write(np.clip(pl, 0, 255).astype(np.uint8).tobytes())
        p_ovl.stdin.write(ov.tobytes())
        p_end.stdin.write(ec.tobytes())
    for p in (p_final, p_plate, p_ovl, p_end):
        p.stdin.close(); p.wait()
    print('done tail', endN, flush=True)
