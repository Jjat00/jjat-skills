"""Estilo jato.run para las escenas de ManimGX de los explicadores.

Cópialo a tools/manim/ del proyecto (ROOT es dos carpetas arriba). Salió del ep/04 (física del Tesla volador, 2026-10).

Lienzo vertical 1080×1920 a 30 fps: el cuadro mide 8 unidades de ancho y 14,22 de alto (1 u = 135 px).
El gráfico vive en la franja y ∈ [-2.25, 4.6] u (≈ 340–1264 px desde arriba): arriba va el kicker de
HyperFrames y abajo las fichas HTML y los subtítulos. Sin texto de lectura: solo fórmulas, ejes y rótulos cortos.
Los tiempos salen de audio_meta.json (palabra@seg relativo al inicio de la escena).
"""
import json
import sys
from pathlib import Path

import manimgx as m

m.config.pixel_width, m.config.pixel_height = 1080, 1920
m.config.frame_rate = 30
m.config.background_color = "#0a0a0a"

CIAN, LAVANDA, DURAZNO, ROSA, MENTA, AZUL = "#9fe3f5", "#c4b5fd", "#ffd9a0", "#ffadbb", "#b4ecc8", "#a8c5ff"
FG, MUTED, TENUE, LINEA = "#ededed", "#a1a09a", "#8f8f8a", "#333333"
ANTON, MONO, POP = "Anton", "JetBrains Mono", "Poppins"

ROOT = Path(__file__).resolve().parents[2]
TOP, BOTTOM = 4.6, -2.25  # franja útil en unidades (abajo van las fichas HTML desde ≈1264 px)
MARGEN = 0.3  # margen lateral mínimo


def datos():
    return json.loads((ROOT / "assets/data/fisica.json").read_text())


def escena(n):
    """Duración y palabras (texto, inicio) de la escena n según audio_meta.json."""
    meta = json.loads((ROOT / "audio_meta.json").read_text())
    v = next(x for x in meta["voices"] if x["frame"] == n)
    return v["duration_s"], [(w["text"].strip(".,:;¿?¡!").lower(), max(w["start"], 0.0)) for w in v["words"]]


class Reloj:
    """Avanza la escena hasta cada palabra: self.reloj.hasta('succión') hace self.wait() lo que falte."""

    def __init__(self, scene, n):
        self.s = scene
        self.dur, self.words = escena(n)
        self.t = 0.0

    def cuando(self, palabra, k=0, antes=0.15):
        hits = [t for w, t in self.words if w.startswith(palabra.lower())]
        if not hits:
            raise KeyError(f"palabra «{palabra}» no está en la escena: {[w for w, _ in self.words]}")
        return max(hits[min(k, len(hits) - 1)] - antes, 0.0)

    def hasta(self, palabra, k=0, antes=0.15):
        t = self.cuando(palabra, k, antes)
        if t > self.t + 1e-3:
            if t - self.t > 1.5:
                print(f"[reloj] quieto {t - self.t:.2f} s antes de «{palabra}» (t={self.t:.2f})", file=sys.stderr)
            self.s.wait(t - self.t)
            self.t = t
        elif self.t - t > 0.3:
            print(f"[reloj] «{palabra}» llega {self.t - t:.2f} s tarde (t={self.t:.2f})", file=sys.stderr)

    def play(self, *anims, run_time=0.8, **kw):
        self.s.play(*anims, run_time=run_time, **kw)
        self.t += run_time
        self.revisar()

    def revisar(self):
        """Avisa si algo visible se sale de la franja útil o del margen lateral (solo 2D)."""
        if isinstance(self.s, m.ThreeDScene):
            return
        for mob in self.s.mobjects:
            for sub in mob.get_family():
                if hasattr(sub, "get_num_points") and sub.get_num_points() == 0:
                    continue
                try:
                    if max(sub.get_fill_opacity(), sub.get_stroke_opacity()) < 0.05:
                        continue
                except Exception:
                    pass
                x0, y0 = sub.get_corner(m.DL)[:2]
                x1, y1 = sub.get_corner(m.UR)[:2]
                if y1 > TOP + 0.01 or y0 < BOTTOM - 0.01 or x0 < -4 + MARGEN - 0.01 or x1 > 4 - MARGEN + 0.01:
                    print(f"[franja] t={self.t:.2f} {type(sub).__name__} x[{x0:.2f},{x1:.2f}] y[{y0:.2f},{y1:.2f}]", file=sys.stderr)
                    break

    def fin(self, respira=None):
        """Cierra en duration_s exacto. Si sobra más de ~1 s, `respira` (un Mobject) se escala leve para no quedar quieto."""
        resto = self.dur - self.t
        if resto < -0.05:
            print(f"[reloj] la escena se pasa {-resto:.2f} s (dura {self.t:.2f}, objetivo {self.dur:.2f})", file=sys.stderr)
        if resto > 1e-3:
            if respira is not None and resto > 1.0:
                self.s.play(respira.animate.scale(1.02, about_point=[0, (TOP + BOTTOM) / 2, 0]), run_time=resto, rate_func=m.linear)
                self.t = self.dur
                self.revisar()
            else:
                if resto > 1.5:
                    print(f"[reloj] quieto {resto:.2f} s al final", file=sys.stderr)
                self.s.wait(resto)
            self.t = self.dur


def mono(txt, size=26, color=MUTED, weight=None):
    kw = {"weight": weight} if weight else {}
    return m.Text(txt, font=MONO, font_size=size, color=color, **kw)


def golpe(txt, size=64, color=FG):
    return m.Text(txt, font=ANTON, font_size=size, color=color)


def flecha(a, b, color, ancho=6):
    """Flecha recta con punta triangular (estilo esquinado)."""
    return m.Arrow(a, b, color=color, stroke_width=ancho, buff=0, max_tip_length_to_length_ratio=0.18)


def ejes(xr, yr, w=6.6, h=5.4, **kw):
    ax = m.Axes(x_range=xr, y_range=yr, x_length=w, y_length=h, tips=False,
                axis_config={"color": "#555555", "stroke_width": 2, "include_ticks": True,
                             "font_size": 22}, **kw)
    return ax
