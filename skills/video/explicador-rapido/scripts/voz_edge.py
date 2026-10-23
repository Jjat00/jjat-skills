"""Narración gratis con edge-tts (las voces neuronales de Microsoft Edge, sin clave ni costo).

A diferencia de un TTS de pago, edge-tts entrega el tiempo de cada palabra, así que no hace falta transcribir la toma
con Whisper (en español solo `large-v3`, ~3 GB, separa bien las palabras). Escribe el MP3 y transcript.json, que
alinear.py lee igual que una transcripción.

  python3 -m venv .voz-venv && .voz-venv/bin/pip install edge-tts
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --root . --prueba 3        # ~10 s con las 3 primeras líneas
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --root .                   # la toma completa
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --voces es                 # lista las voces en español

Voces en español que suenan bien para la serie: es-CO-SalomeNeural (por defecto), es-MX-DaliaNeural,
es-CO-GonzaloNeural, es-MX-JorgeNeural. --velocidad acepta «+8%» o «-5%».
"""
import argparse
import asyncio
import json
import re
from pathlib import Path

import edge_tts

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".", help="raíz del proyecto (donde está SCRIPT.md)")
ap.add_argument("--voz", default="es-CO-SalomeNeural")
ap.add_argument("--velocidad", default="+8%")
ap.add_argument("--prueba", type=int, default=0, help="solo las N primeras líneas, para la prueba de voz")
ap.add_argument("--voces", help="lista las voces cuyo idioma empieza así (p. ej. es) y termina")
a = ap.parse_args()


async def voces(prefijo):
    for v in sorted(await edge_tts.list_voices(), key=lambda v: v["ShortName"]):
        if v["Locale"].startswith(prefijo):
            print(f'{v["ShortName"]:28} {v["Gender"]:7} {v["Locale"]}')


def guion(root):
    """El texto de cada «## Line N — Título», sin las etiquetas de tono de ElevenLabs ([curious, …])."""
    t = (root / "SCRIPT.md").read_text()
    lineas = []
    for m in re.finditer(r"(?ms)^## Line (\d+) — .*?\n(.*?)(?=^## Line|\Z)", t):
        txt = " ".join(l.strip() for l in m.group(2).splitlines() if l.startswith("    "))
        lineas.append(re.sub(r"\[.*?\]\s*", "", txt).strip())
    return [l for l in lineas if l]


async def narrar(texto, mp3, tx):
    c = edge_tts.Communicate(texto, a.voz, rate=a.velocidad, boundary="WordBoundary")
    palabras = []
    with open(mp3, "wb") as f:
        async for trozo in c.stream():
            if trozo["type"] == "audio":
                f.write(trozo["data"])
            elif trozo["type"] == "WordBoundary":
                ini = trozo["offset"] / 1e7
                palabras.append({"text": trozo["text"], "start": round(ini, 3), "end": round(ini + trozo["duration"] / 1e7, 3)})
    tx.write_text(json.dumps(palabras, ensure_ascii=False, indent=1))
    return palabras


if a.voces:
    asyncio.run(voces(a.voces))
    raise SystemExit
root = Path(a.root).resolve()
lineas = guion(root)
if not lineas:
    raise SystemExit("voz_edge: SCRIPT.md no tiene líneas «## Line N — Título» con el texto indentado 4 espacios")
audio = root / "assets" / "audio"
audio.mkdir(parents=True, exist_ok=True)
if a.prueba:
    mp3, tx = audio / "prueba-voz.mp3", audio / "prueba-voz.json"
    lineas = lineas[: a.prueba]
else:
    mp3, tx = audio / "narracion-completa.mp3", audio / "transcript.json"
palabras = asyncio.run(narrar(" ".join(lineas), mp3, tx))
dur = palabras[-1]["end"] if palabras else 0
print(f"{mp3.relative_to(root)}: {len(palabras)} palabras, {dur:.1f} s con {a.voz} a {a.velocidad}; tiempos en {tx.relative_to(root)}")
