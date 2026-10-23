"""Llena en STORYBOARD.md la duración y las palabras con tiempo de cada escena, desde audio_meta.json (de alinear.py).

  python3 <SKILL>/scripts/palabras.py --root .

En cada bloque «## Frame N — Título» escribe o reemplaza `- duration: 6.951s` y `- words: Hola@0.04 mundo@0.31 …`
(segundos desde el inicio de la escena). Lo demás del bloque no se toca, así que se puede repetir si cambia la voz.
"""
import argparse
import json
import re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".")
a = ap.parse_args()
root = Path(a.root).resolve()
voces = {v["frame"]: v for v in json.loads((root / "audio_meta.json").read_text())["voices"]}
sb = (root / "STORYBOARD.md").read_text()


def llenar(m):
    bloque, n = m.group(0), int(m.group(1))
    v = voces.get(n)
    if not v:
        print(f"palabras: la escena {n} no tiene voz en audio_meta.json; se deja igual")
        return bloque
    lineas = {
        "duration": "- duration: " + f"{v['duration_s']:.3f}".rstrip("0").rstrip(".") + "s",
        # una palabra que arranca un poco antes del corte de la escena va en 0
        "words": "- words: " + " ".join(f"{w['text']}@{max(0.0, float(w['start'])):.2f}" for w in v.get("words", [])),
    }
    for campo, linea in lineas.items():
        if re.search(rf"(?m)^- {campo}:.*$", bloque):
            bloque = re.sub(rf"(?m)^- {campo}:.*$", lambda _: linea, bloque, count=1)
        else:
            # va después de la última línea «- campo: …» del encabezado del bloque
            items = list(re.finditer(r"(?m)^- [a-z_]+:.*$", bloque))
            pos = items[-1].end() if items else bloque.index("\n") + 1
            bloque = bloque[:pos] + "\n" + linea + bloque[pos:]
    return bloque


nuevo = re.sub(r"(?ms)^## Frame (\d+) — .*?(?=^## Frame|\Z)", llenar, sb)
(root / "STORYBOARD.md").write_text(nuevo)
print(f"STORYBOARD.md: duración y palabras de {len(voces)} escena(s)")
