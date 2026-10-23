"""Utilidades comunes para las tomas 3D de Blender (estilo jato.run).

Lo importan las tomas (p. ej. ejemplo-auto.py). Todo procedural: mallas, materiales emisivos,
tubos de flujo con UV = "tiempo de vuelo" para animar pulsos que viajan a la
velocidad del fluido, y la configuración de render (EEVEE, Standard, fondo #0a0a0a).
"""
import math
import os
import sys

import bpy
import numpy as np

# ---------------------------------------------------------------- paleta
PALETA = {
    "fondo": "#0a0a0a",
    "cian": "#9fe3f5",
    "lavanda": "#c4b5fd",
    "durazno": "#ffd9a0",
    "rosa": "#ffadbb",
    "menta": "#b4ecc8",
    "azul": "#a8c5ff",
    "linea": "#232323",
    "linea2": "#333333",
    "blanco": "#ffffff",
}


def srgb_a_lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def color(hexa, alfa=1.0):
    """'#rrggbb' -> RGBA lineal (lo que esperan los nodos de Blender)."""
    h = hexa.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (srgb_a_lineal(r), srgb_a_lineal(g), srgb_a_lineal(b), alfa)


# ---------------------------------------------------------------- argumentos
def argumentos():
    """Lee los argumentos que van después de '--' en la línea de Blender."""
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--salida", required=True, help="carpeta de los PNG")
    p.add_argument("--inicio", type=int, default=None)
    p.add_argument("--fin", type=int, default=None)
    p.add_argument("--paso", type=int, default=1)
    p.add_argument("--escala", type=int, default=100, help="% de resolución")
    p.add_argument("--muestras", type=int, default=32)
    p.add_argument("--cuadros", type=str, default="", help="lista '1,90,200' (pruebas)")
    p.add_argument("--blend", type=str, default="", help="guardar .blend aquí")
    return p.parse_args(argv)


# ---------------------------------------------------------------- escena
def escena_limpia():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    esc = bpy.context.scene
    return esc


def configurar_render(esc, cuadros, args):
    esc.render.engine = "BLENDER_EEVEE"
    esc.render.resolution_x = 1080
    esc.render.resolution_y = 1920
    esc.render.resolution_percentage = args.escala
    esc.render.fps = 30
    esc.frame_start = 1
    esc.frame_end = cuadros
    esc.frame_step = args.paso
    esc.render.film_transparent = False
    esc.render.dither_intensity = 0.0  # sin ruido de dithering: el fondo queda exacto
    ee = esc.eevee
    ee.taa_render_samples = args.muestras
    if hasattr(ee, "use_raytracing"):
        ee.use_raytracing = False
    if hasattr(ee, "use_shadows"):
        ee.use_shadows = True
    # Gestión de color: Standard, sin look, para que #0a0a0a no se lave
    esc.display_settings.display_device = "sRGB"
    esc.view_settings.view_transform = "Standard"
    esc.view_settings.look = "None"
    esc.view_settings.exposure = 0.0
    esc.view_settings.gamma = 1.0
    im = esc.render.image_settings
    im.file_format = "PNG"
    im.color_mode = "RGB"
    im.color_depth = "8"
    im.compression = 15
    esc.render.use_file_extension = True
    # Mundo: color plano #0a0a0a
    mundo = bpy.data.worlds.new("Mundo")
    esc.world = mundo
    mundo.use_nodes = True
    bg = mundo.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = color(PALETA["fondo"])
    bg.inputs["Strength"].default_value = 1.0


def renderizar(esc, args, nombre):
    """Renderiza la animación (o cuadros sueltos de prueba) a la carpeta de salida."""
    import time
    if args.blend:
        bpy.ops.wm.save_as_mainfile(filepath=args.blend)
    salida = args.salida.rstrip("\\/")
    # Blender de Windows recibe rutas C:\…; en Linux y macOS, rutas con /.
    sep = "\\" if ":\\" in salida else "/"
    if args.cuadros:
        for f in [int(x) for x in args.cuadros.split(",")]:
            esc.frame_set(f)
            esc.render.filepath = f"{salida}{sep}prueba_{f:04d}"
            t0 = time.time()
            bpy.ops.render.render(write_still=True)
            print(f"CUADRO {f} {time.time() - t0:.2f}s", flush=True)
        return
    if args.inicio is not None:
        esc.frame_start = args.inicio
    if args.fin is not None:
        esc.frame_end = args.fin
    esc.render.filepath = f"{salida}{sep}{nombre}_"
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    n = (esc.frame_end - esc.frame_start) // esc.frame_step + 1
    print(f"RENDER {n} cuadros {time.time() - t0:.1f}s ({(time.time() - t0) / n:.2f}s/cuadro)", flush=True)


# ---------------------------------------------------------------- animación
def interpolacion(tipo):
    """'LINEAR' o 'BEZIER' para las claves que se inserten desde aquí."""
    bpy.context.preferences.edit.keyframe_new_interpolation_type = tipo


def clave(objeto, ruta, cuadro, valor=None, indice=-1):
    if valor is not None:
        if indice >= 0:
            getattr(objeto, ruta)[indice] = valor
        else:
            setattr(objeto, ruta, valor)
    objeto.keyframe_insert(ruta, frame=cuadro, index=indice)


def clave_valor(nodo_valor, cuadro, valor):
    """Clave sobre un nodo Value de un material."""
    nodo_valor.outputs[0].default_value = valor
    nodo_valor.outputs[0].keyframe_insert("default_value", frame=cuadro)


def suave(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def rampa(t, a, b):
    """0 antes de a, 1 después de b, suavizado entre medio."""
    return suave((t - a) / (b - a)) if b > a else float(t >= a)


# ---------------------------------------------------------------- mallas
def objeto_malla(nombre, verts, caras, coleccion=None, material=None):
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(c) for c in caras])
    me.update()
    ob = bpy.data.objects.new(nombre, me)
    (coleccion or bpy.context.scene.collection).objects.link(ob)
    if material:
        me.materials.append(material)
    return ob


def tubo(puntos, radio, lados=6, uv=None, uv2=None):
    """Tubo a lo largo de una polilínea (N×3). Devuelve verts, caras, uv por vértice.

    uv: N×2 valores por punto de la línea (p. ej. tiempo de vuelo y color).
    uv2: N×2 extra (p. ej. fase aleatoria de la línea).
    radio: escalar o arreglo N.
    """
    P = np.asarray(puntos, float)
    n = len(P)
    r = np.broadcast_to(np.asarray(radio, float), (n,))
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    # transporte paralelo para que el tubo no se retuerza
    ref = np.array([0, 0, 1.0]) if abs(T[0][2]) < 0.9 else np.array([1.0, 0, 0])
    N0 = np.cross(T[0], ref)
    N0 /= np.linalg.norm(N0)
    Ns = [N0]
    for i in range(1, n):
        v = Ns[-1] - np.dot(Ns[-1], T[i]) * T[i]
        v /= np.linalg.norm(v) + 1e-12
        Ns.append(v)
    Ns = np.array(Ns)
    Bs = np.cross(T, Ns)
    ang = np.linspace(0, 2 * math.pi, lados, endpoint=False)
    verts = (P[:, None, :] + r[:, None, None] * (np.cos(ang)[None, :, None] * Ns[:, None, :]
                                                  + np.sin(ang)[None, :, None] * Bs[:, None, :]))
    verts = verts.reshape(-1, 3)
    caras = []
    for i in range(n - 1):
        for j in range(lados):
            a = i * lados + j
            b = i * lados + (j + 1) % lados
            caras.append((a, b, b + lados, a + lados))
    return verts, caras


def unir_tubos(lista):
    """lista de (verts, caras, uv N×2, uv2 N×2, lados) -> una sola malla con 2 mapas UV."""
    V, C, U1, U2 = [], [], [], []
    off = 0
    for verts, caras, uv, uv2, lados in lista:
        V.append(verts)
        C.extend([tuple(x + off for x in c) for c in caras])
        U1.append(np.repeat(np.asarray(uv, float), lados, axis=0))
        U2.append(np.repeat(np.asarray(uv2, float), lados, axis=0))
        off += len(verts)
    return np.vstack(V), C, np.vstack(U1), np.vstack(U2)


def malla_con_uv(nombre, verts, caras, uvv1, uvv2, material, coleccion=None):
    """Crea la malla y pasa los UV por vértice a dos capas UV (por bucle)."""
    ob = objeto_malla(nombre, verts, caras, coleccion, material)
    me = ob.data
    vidx = np.zeros(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", vidx)
    for nombre_uv, datos in (("Flujo", uvv1), ("Fase", uvv2)):
        capa = me.uv_layers.new(name=nombre_uv)
        capa.data.foreach_set("uv", datos[vidx].astype(np.float32).ravel())
    return ob


def catmull_rom(ctrl, muestras=200):
    """Curva suave por los puntos de control (Catmull-Rom centrípeta simple), remuestreada
    uniformemente por longitud de arco."""
    C = np.asarray(ctrl, float)
    C = np.vstack([2 * C[0] - C[1], C, 2 * C[-1] - C[-2]])
    pts = []
    for i in range(1, len(C) - 2):
        p0, p1, p2, p3 = C[i - 1], C[i], C[i + 1], C[i + 2]
        for t in np.linspace(0, 1, 40, endpoint=False):
            t2, t3 = t * t, t * t * t
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    pts.append(C[-2])
    pts = np.array(pts)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    su = np.linspace(0, s[-1], muestras)
    return np.stack([np.interp(su, s, pts[:, k]) for k in range(3)], axis=1)


# ---------------------------------------------------------------- materiales
class Nodos:
    """Ayudante para armar árboles de nodos de material con poco código."""

    def __init__(self, nombre, metodo="DITHERED"):
        self.mat = bpy.data.materials.new(nombre)
        self.mat.use_nodes = True
        self.t = self.mat.node_tree
        self.t.nodes.clear()
        self.salida = self.t.nodes.new("ShaderNodeOutputMaterial")
        if hasattr(self.mat, "surface_render_method"):
            self.mat.surface_render_method = metodo
        self.mat.use_backface_culling = False

    def n(self, tipo, **props):
        nodo = self.t.nodes.new(tipo)
        for k, v in props.items():
            setattr(nodo, k, v)
        return nodo

    def l(self, a, b):
        self.t.links.new(a, b)

    def mate(self, op, a, b=None, clamp=False):
        m = self.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                self.l(x, m.inputs[i])
        return m.outputs[0]

    def valor(self, v=0.0):
        nodo = self.n("ShaderNodeValue")
        nodo.outputs[0].default_value = v
        return nodo

    def rgb(self, rgba):
        nodo = self.n("ShaderNodeRGB")
        nodo.outputs[0].default_value = rgba
        return nodo.outputs[0]

    def emision(self, col, fuerza):
        e = self.n("ShaderNodeEmission")
        if isinstance(col, tuple):
            e.inputs["Color"].default_value = col
        else:
            self.l(col, e.inputs["Color"])
        if isinstance(fuerza, (int, float)):
            e.inputs["Strength"].default_value = fuerza
        else:
            self.l(fuerza, e.inputs["Strength"])
        return e.outputs[0]

    def transparente(self):
        return self.n("ShaderNodeBsdfTransparent").outputs[0]

    def mezcla(self, fac, a, b):
        m = self.n("ShaderNodeMixShader")
        if isinstance(fac, (int, float)):
            m.inputs[0].default_value = fac
        else:
            self.l(fac, m.inputs[0])
        self.l(a, m.inputs[1])
        self.l(b, m.inputs[2])
        return m.outputs[0]

    def suma(self, a, b):
        m = self.n("ShaderNodeAddShader")
        self.l(a, m.inputs[0])
        self.l(b, m.inputs[1])
        return m.outputs[0]

    def mezcla_color(self, fac, a, b):
        m = self.n("ShaderNodeMix", data_type="RGBA")
        if isinstance(fac, (int, float)):
            m.inputs["Factor"].default_value = fac
        else:
            self.l(fac, m.inputs["Factor"])
        for sock, x in ((m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(x, tuple):
                sock.default_value = x
            else:
                self.l(x, sock)
        return m.outputs[2]

    def rampa_color(self, fac, paradas):
        r = self.n("ShaderNodeValToRGB")
        els = r.color_ramp.elements
        els[0].position, els[0].color = paradas[0]
        els[1].position, els[1].color = paradas[-1]
        for pos, col in paradas[1:-1]:
            e = els.new(pos)
            e.color = col
        self.l(fac, r.inputs[0])
        return r.outputs[0]

    def info_objeto(self):
        return self.n("ShaderNodeObjectInfo")

    def uv(self, nombre):
        u = self.n("ShaderNodeUVMap")
        u.uv_map = nombre
        s = self.n("ShaderNodeSeparateXYZ")
        self.l(u.outputs[0], s.inputs[0])
        return s.outputs[0], s.outputs[1]

    def fin(self, shader):
        self.l(shader, self.salida.inputs["Surface"])
        return self.mat


def mat_emisivo(nombre, hexa, fuerza=1.0, alfa_objeto=True, aditivo=False):
    """Emisión plana. Si alfa_objeto, la opacidad sale de object.color[3] (animable)."""
    nd = Nodos(nombre, "BLENDED" if aditivo else "DITHERED")
    em = nd.emision(color(hexa), fuerza)
    if aditivo:
        info = nd.info_objeto()
        sep = nd.n("ShaderNodeSeparateColor")
        # la alfa del objeto escala la emisión (mezcla aditiva)
        f = nd.mate("MULTIPLY", info.outputs["Alpha"], fuerza)
        em2 = nd.emision(color(hexa), f)
        return nd.fin(nd.suma(nd.transparente(), em2))
    if alfa_objeto:
        info = nd.info_objeto()
        return nd.fin(nd.mezcla(info.outputs["Alpha"], nd.transparente(), em))
    return nd.fin(em)


def mat_oscuro(nombre, hexa="#121316", rugosidad=0.4, metal=0.2, alfa=None):
    """Material oscuro con algo de brillo. alfa: nodo Value para fundir a transparente."""
    nd = Nodos(nombre)
    p = nd.n("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = color(hexa)
    p.inputs["Roughness"].default_value = rugosidad
    p.inputs["Metallic"].default_value = metal
    if alfa is None:
        return nd.fin(p.outputs[0]), None
    v = nd.valor(1.0)
    return nd.fin(nd.mezcla(v.outputs[0], nd.transparente(), p.outputs[0])), v


def aristas(ob, grosor, material, nombre=None):
    """Copia del objeto con modificador Wireframe (aristas brillantes)."""
    cop = ob.copy()
    cop.data = ob.data.copy()
    cop.name = nombre or ob.name + "_aristas"
    for c in ob.users_collection:
        c.objects.link(cop)
    cop.data.materials.clear()
    cop.data.materials.append(material)
    m = cop.modifiers.new("Alambre", "WIREFRAME")
    m.thickness = grosor
    m.use_replace = True
    m.use_even_offset = True
    m.use_relative_offset = False
    m.use_boundary = True
    return cop


def grilla_piso(tam=24.0, paso=0.5, grosor=0.012, radio_fundido=9.0, hexa="#333333", z=0.0,
                centro=(0, 0)):
    """Grilla de líneas tenues sobre el piso que se funde con la distancia."""
    n = int(tam / paso)
    verts, caras = [], []
    h = tam / 2
    def barra(x0, y0, x1, y1):
        i = len(verts)
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * grosor / 2, dx / L * grosor / 2
        verts.extend([(x0 + nx, y0 + ny, z), (x1 + nx, y1 + ny, z), (x1 - nx, y1 - ny, z), (x0 - nx, y0 - ny, z)])
        caras.append((i, i + 1, i + 2, i + 3))
    for k in range(n + 1):
        c = -h + k * paso
        barra(c + centro[0], -h + centro[1], c + centro[0], h + centro[1])
        barra(-h + centro[0], c + centro[1], h + centro[0], c + centro[1])
    nd = Nodos("Grilla")
    tc = nd.n("ShaderNodeTexCoord")
    vm = nd.n("ShaderNodeVectorMath", operation="LENGTH")
    nd.l(tc.outputs["Object"], vm.inputs[0])
    mr = nd.n("ShaderNodeMapRange")
    nd.l(vm.outputs["Value"], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = radio_fundido * 0.35
    mr.inputs["From Max"].default_value = radio_fundido
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    em = nd.emision(color(hexa), 1.0)
    mat = nd.fin(nd.mezcla(mr.outputs[0], nd.transparente(), em))
    ob = objeto_malla("Grilla", verts, caras, material=mat)
    ob.location = (centro[0] * 0, 0, 0)
    return ob


def camara(nombre="Camara", lente=35.0):
    cd = bpy.data.cameras.new(nombre)
    cd.lens = lente
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 36.0
    cd.clip_start = 0.05
    cd.clip_end = 200
    ob = bpy.data.objects.new(nombre, cd)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def mirar_a(cam, objetivo):
    c = cam.constraints.new("TRACK_TO")
    c.target = objetivo
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return c


def vacio(nombre, loc=(0, 0, 0)):
    ob = bpy.data.objects.new(nombre, None)
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)
    return ob


def luz_area(nombre, loc, rot, potencia, tam=3.0, hexa="#ffffff"):
    ld = bpy.data.lights.new(nombre, "AREA")
    ld.energy = potencia
    ld.size = tam
    ld.color = color(hexa)[:3]
    ob = bpy.data.objects.new(nombre, ld)
    ob.location = loc
    ob.rotation_euler = rot
    bpy.context.scene.collection.objects.link(ob)
    return ob
