"""Auto de perfil (silueta de deportivo) para las escenas de fuerzas.

Sale de auto-perfil-plano.svg, copia aplanada de assets/svg/auto-perfil.svg (sin <use>, transform ni
stroke-opacity, que ManimGX no lee bien). Mira a la derecha. Estructura del VGroup, igual que el auto viejo:
a[0] carrocería (y ventanas, faro, calavera), a[1] rueda trasera, a[2] rueda delantera; a[k][0] es el círculo
exterior de cada rueda.
"""
from pathlib import Path

import numpy as np

from estilo import *

SVG = str(Path(__file__).resolve().parent / "auto-perfil-plano.svg")
ANCHO_REF = 7.0  # a este ancho los trazos del SVG se ven como en el original


def auto(ancho=3.2):
    """Silueta de `ancho` unidades de largo, con la base de las llantas en y = 0 y centrada en x = 0."""
    s = m.SVGMobject(SVG)
    s.scale_to_fit_width(ancho)
    k = max(ancho / ANCHO_REF, 0.35)  # adelgaza los trazos al achicar (con un mínimo para que no desaparezcan)
    for sub in s.submobjects:
        sub.set_stroke(width=sub.get_stroke_width() * k)
    p = s.submobjects
    a = m.VGroup(m.VGroup(*p[0:6]), m.VGroup(*p[6:14]), m.VGroup(*p[14:22]))
    a.shift(m.UP * -a.get_bottom()[1] + m.RIGHT * -a.get_center()[0])
    return a


def ruedas(a):
    """Centros de las ruedas trasera y delantera (funciona con el auto girado)."""
    return a[1][0].get_center(), a[2][0].get_center()


def radio(a):
    return a[1][0].width / 2


def centro_masa(a):
    """Centro de masa aproximado: entre los ejes, un poco hacia la carrocería (deportivo de centro bajo)."""
    c1, c2 = ruedas(a)
    medio = (c1 + c2) / 2
    return medio + 0.45 * (a[0].get_center() - medio)


def contacto(a, k=2):
    """Punto de la rueda k (1 trasera, 2 delantera) más alejado de la carrocería: donde toca el piso, techo o pared."""
    c = a[k][0].get_center()
    medio = (ruedas(a)[0] + ruedas(a)[1]) / 2
    n = medio - a[0].get_center()  # de la carrocería hacia las llantas
    n = n / np.linalg.norm(n)
    return c + n * radio(a)
