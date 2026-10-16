"""Toma mínima de ejemplo: el deportivo de auto.py sobre la grilla, con cámara a tres cuartos.

Uso (desde WSL): correr.sh ejemplo-auto --cuadros 1 --escala 50   (un cuadro de prueba)
                 correr.sh ejemplo-auto && codificar.sh ejemplo-auto   (90 cuadros, 3 s)
Sirve de plantilla: copia bcomun.py, auto.py y este archivo a tools/blender/ del proyecto.
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import auto as au  # noqa: E402
import bcomun as bc  # noqa: E402

CUADROS = 90
args = bc.argumentos()
esc = bc.escena_limpia()
bc.configurar_render(esc, CUADROS, args)

au.construir()
bc.grilla_piso()
cam = bc.camara(lente=40.0)
cam.location = (6.5, -7.5, 2.6)
bc.mirar_a(cam, bc.vacio("Mira", (0, 0, 0.55)))
esc.camera = cam
bc.luz_area("Clave", (3, -4, 5), (0.6, 0, 0.6), 600)
bc.luz_area("Contra", (-4, 4, 3), (-0.8, 0, 3.6), 300, hexa="#c4b5fd")
# giro lento de la cámara alrededor del auto
bc.interpolacion("LINEAR")
bc.clave(cam, "location", 1, (6.5, -7.5, 2.6))
bc.clave(cam, "location", CUADROS, (8.5, -5.0, 2.6))

bc.renderizar(esc, args, "ejemplo-auto")
