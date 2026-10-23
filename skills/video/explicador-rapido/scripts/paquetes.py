"""Escribe un paquete por escena en .hyperframes/paquetes/ a partir de STORYBOARD.md, para los subagentes de la § 6.

  python3 <SKILL>/scripts/paquetes.py --root . --refs compositions/frames/_ref-a.html compositions/frames/_ref-b.html

Cada paquete dice qué archivo escribir, con qué id, qué leer antes (estilo, reglas, cuadros aprobados, dirección de
video) y lleva el bloque de su escena tal como está en el storyboard. Las reglas del proyecto se copian a
.hyperframes/paquetes/_reglas.md la primera vez (rellena lo que va entre <…> antes de lanzar los subagentes).
"""
import argparse
import re
import shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".", help="raíz del proyecto (donde está STORYBOARD.md)")
ap.add_argument("--refs", nargs="+", default=[], help="los cuadros de estilo aprobados, que hacen de esqueleto")
ap.add_argument("--solo", nargs="*", default=[], help="solo estos ids de escena (p. ej. 04-base 07-coseno)")
a = ap.parse_args()

root = Path(a.root).resolve()
sb = (root / "STORYBOARD.md").read_text()
out = root / ".hyperframes" / "paquetes"
out.mkdir(parents=True, exist_ok=True)
reglas = out / "_reglas.md"
if not reglas.exists():
    shutil.copy(SKILL / "references" / "reglas-escena.md", reglas)

refs = ", ".join(a.refs) if a.refs else "los dos cuadros aprobados de compositions/frames/"
hechos = 0
for m in re.finditer(r"(?ms)^## Frame (\d+) — .*?(?=^## Frame|\Z)", sb):
    src = re.search(r"- src: compositions/frames/(\S+)\.html", m.group(0))
    if not src:
        raise SystemExit(f"paquetes: la escena {m.group(1)} no tiene «- src: compositions/frames/<id>.html»")
    sid = src.group(1)
    # los cuadros ya aprobados no se vuelven a encargar
    if (a.solo and sid not in a.solo) or any(Path(r).stem == sid for r in a.refs):
        continue
    (out / f"{sid}.md").write_text(f"""# Paquete de escena: {sid}

## Entradas
- Proyecto: {root}
- Estilo: frame.md
- Reglas obligatorias: .hyperframes/paquetes/_reglas.md
- Esqueleto obligatorio (cuadros aprobados): {refs}
- Dirección de video común (colores por rol, elementos que se repiten entre escenas): sección «Video direction» de
  STORYBOARD.md; léela antes de empezar.
- Datos reales: assets/data/ (no inventes cifras: si falta un dato, dilo en tu respuesta).
- Archivo a escribir: compositions/frames/{sid}.html · data-composition-id y clave del timeline: «{sid}» · prefijo de
  ids: {sid}-

## Bloque asignado del storyboard

{m.group(0).strip()}
""")
    hechos += 1
print(f"{hechos} paquete(s) en {out.relative_to(root)}; reglas en {reglas.relative_to(root)}")
