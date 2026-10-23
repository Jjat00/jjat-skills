"""Deportivo genérico de 2 plazas, procedural (lo usan las tomas, p. ej. ejemplo-auto.py).

La silueta lateral sale de assets/svg/auto-perfil.svg (mismo perfil que la ilustración 2D):
capó largo y bajo, parabrisas inclinado, techo fastback, cola Kamm. La carrocería es un loft
de secciones superelípticas (suaves) con pasos de rueda redondeados (Boolean con cilindros),
faldón y difusor. El look técnico sale de un material oscuro con borde fresnel cian + líneas
de contorno cian (ventanas, pasos de rueda, línea de cintura, faldón) y unas pocas secciones
tenues tipo plano CAD. Ruedas: neumático con perfil redondeado + rin de 5 radios.

Ejes: adelante = +Y, arriba = +Z, piso en z = 0. Largo 4,4 m, ancho 2,0 m, alto 1,12 m.
"""
import math

import bpy
import numpy as np

import bcomun as bc

S = 4.4 / 384.0           # metros por unidad del SVG (x 14..398 -> 4,4 m)
RUEDA_R = 28 * S          # 0,32 m
ARCO_R = 35 * S + 0.01    # 0,41 m
RUEDA_Y = ((85 - 206) * S, (315 - 206) * S)   # trasera -1,39 m, delantera +1,25 m
RUEDA_X = 0.84
RUEDA_ANCHO = 0.25


def svg_a_mundo(px, py):
    return (px - 206) * S, (123 - py) * S


# ---------------------------------------------------------------- perfiles
def _bezier_q(p0, p1, p2, n=24):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t ** 2 * np.array(p2)


def _techo_svg():
    """Línea superior del SVG (cola -> nariz) como polilínea en unidades SVG."""
    tramos = [
        np.array([(14, 76)]),
        _bezier_q((14, 76), (14, 66), (27, 63)),
        np.array([(110, 52)]),
        _bezier_q((110, 52), (150, 27), (206, 25)),
        _bezier_q((206, 25), (248, 24), (276, 42)),
        np.array([(362, 59)]),
        _bezier_q((362, 59), (389, 63), (396, 76)),
        np.array([(398, 88)]),
    ]
    P = np.vstack(tramos)
    # nos quedamos con x estrictamente creciente
    out = [P[0]]
    for p in P[1:]:
        if p[0] > out[-1][0] + 1e-6:
            out.append(p)
    return np.array(out)


_T = _techo_svg()
_TY = (_T[:, 0] - 206) * S
_TZ = (123 - _T[:, 1]) * S
Y_COLA, Y_NARIZ = _TY[0], _TY[-1]


def z_techo(y):
    return np.interp(y, _TY, _TZ)


def z_piso(y):
    """Fondo plano a 0,13 m; sube en el difusor trasero y bajo la nariz."""
    y = np.asarray(y, float)
    z = 0.13 + 0.11 * np.clip((-1.55 - y) / 0.65, 0, 1) ** 1.3
    z = z + 0.07 * np.clip((y - 1.75) / 0.45, 0, 1) ** 1.5
    return z


def z_cintura(y):
    """Altura del hombro (donde la superficie deja de ser vertical y entra la cabina/capó)."""
    zt = z_techo(y)
    return np.minimum(0.60, zt - 0.10)


_WY = [-2.2, -1.9, -1.4, -0.6, 0.3, 1.25, 1.8, 2.2]
_WV = [0.92, 0.985, 1.0, 0.95, 0.94, 0.99, 0.95, 0.86]


def medio_ancho(y):
    y = np.asarray(y, float)
    w = np.interp(y, _WY, _WV)
    # planta redondeada en los extremos (la cola queda casi plana: tipo Kamm)
    tc = np.clip((-y - 1.95) / (-Y_COLA - 1.95 + 1e-9), 0, 1)
    tn = np.clip((y - 1.6) / (Y_NARIZ - 1.6), 0, 1)
    w = w * np.maximum(np.sqrt(1 - tc ** 2), 0.86) * np.maximum(np.sqrt(1 - tn ** 2), 0.62)
    return w


def exp_superior(y):
    """Exponente de la superelipse de arriba: cabina redondeada, capó más plano."""
    h = z_techo(y) - z_cintura(y)
    return np.interp(h, [0.10, 0.50], [4.0, 2.1])


def ancho_en(y, z):
    """Medio ancho de la superficie exterior a la altura z en la sección y."""
    zb, zc, zt = z_piso(y), z_cintura(y), z_techo(y)
    W = medio_ancho(y)
    if z >= zc:
        n = exp_superior(y)
        u = min(max((z - zc) / (zt - zc), 0), 1)
        return float(W * (1 - u ** n) ** (1 / n))
    v = min(max((zc - z) / (zc - zb), 0), 1)
    return float(W * (1 - v ** 4) ** (1 / 4))


def altura_en(y, x):
    """Altura de la cara superior en (x, y) (para apoyar flechas encima)."""
    zc, zt = z_cintura(y), z_techo(y)
    W = medio_ancho(y)
    n = exp_superior(y)
    a = min(abs(x) / W, 0.999)
    return float(zc + (zt - zc) * (1 - a ** n) ** (1 / n))


# ---------------------------------------------------------------- mallas
def _anillo(y, m=64):
    zb, zc, zt = float(z_piso(y)), float(z_cintura(y)), float(z_techo(y))
    W = float(medio_ancho(y))
    n = float(exp_superior(y))
    q = 4.0
    pts = []
    # cuarto inferior derecho: de abajo al centro hacia el hombro; luego arriba hasta el techo
    k = m // 4
    for i in range(k):
        t = (i / k) * (math.pi / 2)        # 0 = fondo centro, pi/2 = hombro
        c, s = math.cos(math.pi / 2 - t), math.sin(math.pi / 2 - t)
        x = W * abs(c) ** (2 / q)
        z = zc - (zc - zb) * abs(s) ** (2 / q)
        pts.append((x, z))
    for i in range(k):
        t = (i / k) * (math.pi / 2)
        c, s = math.cos(t), math.sin(t)
        x = W * abs(c) ** (2 / n)
        z = zc + (zt - zc) * abs(s) ** (2 / n)
        pts.append((x, z))
    der = pts                               # de (0, zb) a casi (0, zt)
    izq = [(-x, z) for (x, z) in reversed(der)]
    ring = [(0.0, zb)] + der[1:] + [(0.0, zt)] + izq[:-1]
    return [(x, y, z) for (x, z) in ring]


def malla_carroceria(n_secc=150, m=64):
    ys = Y_COLA + (Y_NARIZ - Y_COLA) * (0.5 - 0.5 * np.cos(np.linspace(0, math.pi, n_secc)))
    anillos = [_anillo(float(y), m) for y in ys]
    k = len(anillos[0])
    V = [p for a in anillos for p in a]
    C = []
    for i in range(n_secc - 1):
        for j in range(k):
            a, b = i * k + j, i * k + (j + 1) % k
            C.append((a, a + k, b + k, b))
    # tapas: abanico a un punto central
    for i, sentido in ((0, 1), (n_secc - 1, -1)):
        cen = np.mean(anillos[i], axis=0)
        V.append(tuple(cen))
        ci = len(V) - 1
        for j in range(k):
            a, b = i * k + j, i * k + (j + 1) % k
            C.append((a, b, ci) if sentido == 1 else (b, a, ci))
    return V, C


def _en_poligono(py, pz, poly):
    """Punto en polígono (y, z)."""
    dentro = False
    n = len(poly)
    for i in range(n):
        y1, z1 = poly[i]
        y2, z2 = poly[(i + 1) % n]
        if (z1 > pz) != (z2 > pz):
            yc = y1 + (pz - z1) * (y2 - y1) / (z2 - z1)
            if py < yc:
                dentro = not dentro
    return dentro


def poligono_ventanas():
    tramos = [_bezier_q((124, 52), (158, 33), (204, 31)), _bezier_q((204, 31), (238, 31), (260, 44)),
              np.array([(236, 52)])]
    P = np.vstack(tramos)
    return [svg_a_mundo(px, py) for px, py in P]


# ---------------------------------------------------------------- materiales
def _mat_carroceria():
    """Pintura gris muy oscura con barniz + borde fresnel cian. Value 'Opacidad' para el corte."""
    nd = bc.Nodos("CarroceriaSuave")
    p = nd.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = bc.color("#16181d")
    p.inputs["Roughness"].default_value = 0.32
    p.inputs["Metallic"].default_value = 0.35
    if "Coat Weight" in p.inputs:
        p.inputs["Coat Weight"].default_value = 0.6
    op = nd.valor(1.0)
    info = nd.info_objeto()
    a = nd.mate("MULTIPLY", op.outputs[0], info.outputs["Alpha"])
    cuerpo = nd.mezcla(a, nd.transparente(), p.outputs[0])
    lw = nd.n("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    borde = nd.mate("POWER", lw.outputs["Facing"], 4.5)
    f = nd.mate("MULTIPLY", nd.mate("MULTIPLY", borde, 0.5), info.outputs["Alpha"])
    rim = nd.emision(bc.color(bc.PALETA["cian"]), f)
    return nd.fin(nd.suma(cuerpo, rim)), op


def _mat_vidrio(op):
    nd = bc.Nodos("Vidrio")
    p = nd.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = bc.color("#070b0e")
    p.inputs["Roughness"].default_value = 0.06
    p.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in p.inputs:
        p.inputs["Specular IOR Level"].default_value = 0.9
    info = nd.info_objeto()
    # comparte la opacidad de la carrocería (driver) por objeto
    v = nd.valor(1.0)
    a = nd.mate("MULTIPLY", v.outputs[0], info.outputs["Alpha"])
    lw = nd.n("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.3
    f = nd.mate("MULTIPLY", nd.mate("MULTIPLY", nd.mate("POWER", lw.outputs["Facing"], 3.0), 0.35), info.outputs["Alpha"])
    rim = nd.emision(bc.color(bc.PALETA["azul"]), f)
    mat = nd.fin(nd.suma(nd.mezcla(a, nd.transparente(), p.outputs[0]), rim))
    return mat, v


def mat_solido(nombre, hexa, rug=0.5, metal=0.0, emi=None):
    """Principled con opacidad por object.color[3] (para fundidos)."""
    nd = bc.Nodos(nombre)
    p = nd.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = bc.color(hexa)
    p.inputs["Roughness"].default_value = rug
    p.inputs["Metallic"].default_value = metal
    if emi:
        p.inputs["Emission Color"].default_value = bc.color(emi)
        p.inputs["Emission Strength"].default_value = 1.0
    info = nd.info_objeto()
    return nd.fin(nd.mezcla(info.outputs["Alpha"], nd.transparente(), p.outputs[0]))


# ---------------------------------------------------------------- ruedas
def _revolucion_x(perfil, n=48):
    """Revoluciona un perfil (x_local, r) alrededor del eje X. Perfil cerrado."""
    V, C = [], []
    m = len(perfil)
    for i in range(n):
        a = 2 * math.pi * i / n
        for (x, r) in perfil:
            V.append((x, r * math.cos(a), r * math.sin(a)))
    for i in range(n):
        for j in range(m):
            a0 = i * m + j
            a1 = i * m + (j + 1) % m
            b0 = ((i + 1) % n) * m + j
            b1 = ((i + 1) % n) * m + (j + 1) % m
            C.append((a0, a1, b1, b0))
    return V, C


def _perfil_neumatico(ri=0.215, ro=RUEDA_R, w=RUEDA_ANCHO, rc=0.06, k=6):
    """Sección del neumático: rectángulo con esquinas exteriores redondeadas (banda y flanco)."""
    h = w / 2
    pts = [(-h + 0.01, ri)]
    # flanco izquierdo subiendo hasta la esquina redondeada
    for i in range(k + 1):
        t = math.pi + (math.pi / 2) * i / k   # de 180° a 270° (esquina superior izquierda)
        pts.append((-h + rc + rc * math.cos(t), ro - rc - rc * math.sin(t)))
    for i in range(k + 1):
        t = -math.pi / 2 + (math.pi / 2) * i / k
        pts.append((h - rc + rc * math.cos(t), ro - rc - rc * math.sin(t)))
    pts.append((h - 0.01, ri))
    return pts


def rueda(nombre, x, y, lado, coleccion, padre):
    """Neumático + rin de 5 radios. lado = +1 (derecha) o -1: hacia dónde mira la cara exterior."""
    vacio = bc.vacio(nombre)
    vacio.location = (x, y, RUEDA_R)
    vacio.parent = padre
    piezas = []
    V, C = _revolucion_x(_perfil_neumatico(), 56)
    piezas.append(bc.objeto_malla(nombre + "_neumatico", V, C, material=MATS["neumatico"]))
    # barril del rin (cilindro abierto) y cubo
    perfil_barril = [(-0.10, 0.205), (0.10, 0.205), (0.10, 0.215), (-0.10, 0.215)]
    V, C = _revolucion_x(perfil_barril, 40)
    piezas.append(bc.objeto_malla(nombre + "_barril", V, C, material=MATS["rin"]))
    xo = lado * 0.085                      # plano de la cara del rin (hundido en la llanta)
    perfil_cubo = [(xo - 0.03, 0.0), (xo + lado * 0.012, 0.0), (xo + lado * 0.012, 0.055), (xo - 0.03, 0.055)]
    V, C = _revolucion_x(perfil_cubo, 20)
    piezas.append(bc.objeto_malla(nombre + "_cubo", V, C, material=MATS["rin"]))
    # 5 radios (cajas que se afinan hacia afuera)
    for b in range(5):
        a = 2 * math.pi * b / 5 + 0.3
        ca, sa = math.cos(a), math.sin(a)
        pv = []
        for rr, ww in ((0.045, 0.034), (0.207, 0.022)):
            for dx in (xo - 0.022, xo + lado * 0.004):
                for dw in (-ww, ww):
                    # punto en el plano YZ girado: radial (ca, sa), tangente (-sa, ca)
                    pv.append((dx, rr * ca - dw * sa, rr * sa + dw * ca))
        cs = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        piezas.append(bc.objeto_malla(nombre + "_radio", pv, cs, material=MATS["radio"]))
    for p in piezas:
        for c in p.users_collection:
            c.objects.unlink(p)
        coleccion.objects.link(p)
        p.parent = vacio
        for pol in p.data.polygons:
            pol.use_smooth = True
    # contornos emisivos: flanco (blanco tenue), labio del rin (gris) y cubo (cian)
    lineas = []
    for r, mat, rad in ((0.300, MATS["linea_blanca"], 0.006), (0.207, MATS["linea_gris"], 0.005)):
        a = np.linspace(0, 2 * math.pi, 73)
        P = np.stack([np.full_like(a, lado * (RUEDA_ANCHO / 2 + 0.003) if r > 0.25 else xo + lado * 0.006),
                      r * np.cos(a), r * np.sin(a)], axis=1)
        vs, cs = bc.tubo(P, rad, 6)
        o = bc.objeto_malla(nombre + "_contorno", vs, cs, coleccion, mat)
        o.parent = vacio
        lineas.append(o)
    a = np.linspace(0, 2 * math.pi, 25)
    P = np.stack([np.full_like(a, xo + lado * 0.014), 0.025 * np.cos(a), 0.025 * np.sin(a)], axis=1)
    vs, cs = bc.tubo(P, 0.008, 6)
    o = bc.objeto_malla(nombre + "_tapa", vs, cs, coleccion, MATS["cian"])
    o.parent = vacio
    return vacio


MATS = {}


def construir(coleccion=None, secciones_tenues=True, mezcla="DITHERED"):
    """Crea el auto. Devuelve dict con 'raiz' (vacío padre), 'opacidad' (lista de nodos Value
    a animar juntos para volver la carrocería transparente) y 'objetos' (todos, para fundidos)."""
    col = coleccion or bpy.context.scene.collection
    MATS["neumatico"] = mat_solido("Neumatico", "#141416", 0.75, 0.0)
    MATS["rin"] = mat_solido("Rin", "#3b3f47", 0.3, 0.8)
    MATS["radio"] = mat_solido("Radio", "#4a4e57", 0.3, 0.8, emi="#1d1f22")
    MATS["linea_blanca"] = bc.mat_emisivo("LineaBlanca", "#ededed", 0.55, alfa_objeto=True)
    MATS["linea_gris"] = bc.mat_emisivo("LineaGris", "#a1a09a", 0.9, alfa_objeto=True)
    MATS["cian"] = bc.mat_emisivo("LineaCian", bc.PALETA["cian"], 1.15, alfa_objeto=True)
    MATS["cian_tenue"] = bc.mat_emisivo("LineaCianTenue", "#3f6f7a", 1.0, alfa_objeto=True)
    MATS["rosa"] = bc.mat_emisivo("Calavera", bc.PALETA["rosa"], 1.4, alfa_objeto=True)
    MATS["faro"] = bc.mat_emisivo("Faro", "#ededed", 1.5, alfa_objeto=True)

    raiz = bc.vacio("Auto")
    mat_c, op_c = _mat_carroceria()
    mat_v, op_v = _mat_vidrio(op_c)
    if mezcla == "BLENDED":
        # transparencia sin grano: mezcla ordenada, sin caras traseras
        for m in (mat_c, mat_v):
            m.surface_render_method = "BLENDED"
            m.use_backface_culling = True
            if hasattr(m, "use_transparency_overlap"):
                m.use_transparency_overlap = False
    V, C = malla_carroceria()
    carro = bc.objeto_malla("Carroceria", V, C, col, mat_c)
    carro.data.materials.append(mat_v)
    carro.parent = raiz
    me = carro.data
    poly = poligono_ventanas()
    for p in me.polygons:
        p.use_smooth = True
        c = p.center
        nrm = p.normal
        if _en_poligono(c.y, c.z, poly):
            lateral = abs(nrm.x) > 0.5
            parabrisas = nrm.y > 0.25 and c.y > 0.15 and abs(c.x) < 0.75
            luneta = nrm.y < -0.2 and c.y < -0.3 and abs(c.x) < 0.7
            if lateral or parabrisas or luneta:
                p.material_index = 1
    # pasos de rueda: Boolean diferencia con 4 cilindros (solo el costado exterior)
    corte = bpy.data.collections.new("CortesArcos")
    bpy.context.scene.collection.children.link(corte)
    for sx in (-1, 1):
        for yw in RUEDA_Y:
            vs, cs = [], []
            n = 40
            for xx in (0.52 * sx, 1.4 * sx):
                for i in range(n):
                    a = 2 * math.pi * i / n
                    vs.append((xx, yw + ARCO_R * math.cos(a), RUEDA_R + ARCO_R * math.sin(a)))
            for i in range(n):
                j = (i + 1) % n
                cs.append((i, j, j + n, i + n))
            cs.append(tuple(range(n)))
            cs.append(tuple(reversed(range(n, 2 * n))))
            cil = bc.objeto_malla("CorteArco", vs, cs, corte)
            cil.hide_render = True
            cil.hide_viewport = True
    mb = carro.modifiers.new("Arcos", "BOOLEAN")
    mb.operation = "DIFFERENCE"
    mb.operand_type = "COLLECTION"
    mb.collection = corte
    mb.solver = "EXACT"
    corte.hide_render = True

    objetos = [carro]
    lineas = []

    def linea_superficie(pts_yz, lado, mat, radio=0.008, despeje=0.006, nombre="Contorno"):
        P = []
        for (y, z) in pts_yz:
            P.append((lado * (ancho_en(y, z) + despeje), y, z))
        vs, cs = bc.tubo(np.array(P), radio, 6)
        o = bc.objeto_malla(nombre, vs, cs, col, mat)
        o.parent = raiz
        lineas.append(o)
        return o

    def remuestrear(pts, n):
        pts = np.asarray(pts, float)
        d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        s = np.linspace(0, d[-1], n)
        return np.stack([np.interp(s, d, pts[:, 0]), np.interp(s, d, pts[:, 1])], axis=1)

    def fuera_de_arcos(y, z, margen=0.03):
        return all(math.hypot(y - yw, z - RUEDA_R) > ARCO_R + margen for yw in RUEDA_Y)

    for lado in (-1, 1):
        # ventanas (DLO) y parante
        dlo = remuestrear(poly + [poly[0]], 120)
        linea_superficie(dlo, lado, MATS["cian"], 0.009, nombre="Ventana")
        py_, pz_ = svg_a_mundo(196, 31)
        qy_, qz_ = svg_a_mundo(190, 52)
        linea_superficie(remuestrear([(py_, pz_ - 0.02), (qy_, qz_)], 12), lado, MATS["cian"], 0.007, nombre="Parante")
        # pasos de rueda
        for yw in RUEDA_Y:
            fi = np.linspace(-0.42, math.pi + 0.42, 70)
            pts = [(yw + (ARCO_R + 0.012) * math.cos(f), RUEDA_R + (ARCO_R + 0.012) * math.sin(f)) for f in fi]
            pts = [(y, z) for (y, z) in pts if z > float(z_piso(y)) + 0.03]
            linea_superficie(pts, lado, MATS["cian"], 0.009, nombre="Arco")
        # línea de cintura (como en el SVG) y faldón, cortadas en los arcos
        for zz, mat, rad in ((0.56, MATS["cian_tenue"], 0.006), (0.19, MATS["cian"], 0.008)):
            ys = np.linspace(Y_COLA + 0.12, Y_NARIZ - 0.1, 240)
            tramo = []
            for y in ys:
                ok = fuera_de_arcos(y, zz) and zz < float(z_techo(y)) - 0.05
                if zz < 0.3:
                    ok = ok and RUEDA_Y[0] + ARCO_R < y < RUEDA_Y[1] - ARCO_R
                if ok:
                    tramo.append((y, zz))
                elif len(tramo) > 3:
                    linea_superficie(tramo, lado, mat, rad, nombre="Cintura")
                    tramo = []
                else:
                    tramo = []
            if len(tramo) > 3:
                linea_superficie(tramo, lado, mat, rad, nombre="Cintura")
        # faro y calavera
        a, b = svg_a_mundo(372, 66), svg_a_mundo(392, 72)
        linea_superficie(remuestrear([a, b], 10), lado, MATS["faro"], 0.012, nombre="Faro")
        a, b = svg_a_mundo(16, 72), svg_a_mundo(32, 70)
        linea_superficie(remuestrear([a, b], 10), lado, MATS["rosa"], 0.012, nombre="Calavera")

    # perfil superior (espina) y secciones tenues tipo plano técnico
    ys = np.linspace(Y_COLA + 0.01, Y_NARIZ - 0.01, 200)
    P = np.stack([np.zeros_like(ys), ys, z_techo(ys) + 0.005], axis=1)
    vs, cs = bc.tubo(P, 0.006, 6)
    o = bc.objeto_malla("Espina", vs, cs, col, MATS["cian_tenue"])
    o.parent = raiz
    lineas.append(o)
    if secciones_tenues:
        for y in (-2.0, -0.55, 0.05, 0.6, 1.95):
            ring = _anillo(y, 96)
            P = np.array(ring + [ring[0]], float)
            nrm = P.copy()
            nrm[:, 1] = 0
            nrm[:, 2] -= float((z_piso(y) + z_techo(y)) / 2)
            nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
            P = P + 0.005 * nrm
            vs, cs = bc.tubo(P, 0.004, 5)
            o = bc.objeto_malla("Seccion", vs, cs, col, MATS["cian_tenue"])
            o.parent = raiz
            lineas.append(o)
    # contorno de la cola (cara plana Kamm) y difusor con aletas
    ring = _anillo(Y_COLA + 0.004, 96)
    P = np.array(ring + [ring[0]], float)
    P[:, 1] -= 0.006
    vs, cs = bc.tubo(P, 0.008, 6)
    o = bc.objeto_malla("ContornoCola", vs, cs, col, MATS["cian"])
    o.parent = raiz
    lineas.append(o)
    for xf in (-0.62, -0.2, 0.2, 0.62):
        # aleta triangular colgando del difusor (de la cola hasta donde empieza a subir)
        y0, y1 = Y_COLA + 0.02, -1.55
        z0 = float(z_piso(y0)) - 0.005
        tri = [(y0, z0), (y0, 0.14), (y1, 0.128)]
        pv = [(xf + dx, y, z) for dx in (-0.006, 0.006) for (y, z) in tri]
        cs = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
        o = bc.objeto_malla("Aleta", pv, cs, col, MATS["cian_tenue"])
        o.parent = raiz
        lineas.append(o)

    ruedas = []
    for sx in (-1, 1):
        for yw in RUEDA_Y:
            ruedas.append(rueda("Rueda", sx * RUEDA_X, yw, sx, col, raiz))
    objetos += lineas
    for r in ruedas:
        objetos += list(r.children)
    return {"raiz": raiz, "carroceria": carro, "opacidad": [op_c, op_v], "objetos": objetos}


def opacidad(auto, cuadro, valor):
    for v in auto["opacidad"]:
        bc.clave_valor(v, cuadro, valor)


def fundir(objetos, cuadro, alfa):
    for o in objetos:
        o.color = (1, 1, 1, alfa)
        o.keyframe_insert("color", frame=cuadro, index=3)
