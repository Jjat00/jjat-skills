"""Narración con ElevenLabs y el tiempo de cada palabra, en una sola llamada (sin transcribir).

Usa el endpoint `with-timestamps`, que devuelve el audio y el tiempo de cada carácter; de ahí salen las palabras con
su inicio y fin, en el formato que lee alinear.py. Solo usa la biblioteca estándar de Python.

  export ELEVENLABS_API_KEY=...                     # ver «Instalación» en SKILL.md: de dónde sale la clave
  python3 <SKILL>/scripts/voz_elevenlabs.py --root . --prueba 3            # cuenta caracteres, no gasta nada
  python3 <SKILL>/scripts/voz_elevenlabs.py --root . --prueba 3 --generar  # ~10 s: assets/audio/prueba-voz.mp3
  python3 <SKILL>/scripts/voz_elevenlabs.py --root . --generar             # narracion-completa.mp3 + transcript.json

Sin --generar solo dice cuántos caracteres cobraría ElevenLabs (cobra por carácter según el plan): muéstraselo al
usuario y espera su OK antes de generar. Un guion largo se pide en tramos de líneas completas, con el texto vecino
como contexto para que la entonación siga, y se une en un solo MP3.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".", help="raíz del proyecto (donde está SCRIPT.md)")
ap.add_argument("--voz", default="4GeB1bS2GAHAsGRM0eeU", help="voice_id de ElevenLabs (por defecto, una voz latina juvenil)")
ap.add_argument("--modelo", default="eleven_v4")
ap.add_argument("--velocidad", type=float, default=1.08)
ap.add_argument("--estabilidad", type=float, default=0.5)
ap.add_argument("--prueba", type=int, default=0, help="solo las N primeras líneas, para la prueba de voz")
ap.add_argument("--tramo", type=int, default=2500, help="caracteres máximos por llamada")
ap.add_argument("--generar", action="store_true", help="genera de verdad (gasta créditos); sin esto solo cuenta")
a = ap.parse_args()


def guion(root):
    """El texto de cada «## Line N — Título». Las etiquetas de tono ([curious, …]) se conservan: ElevenLabs las usa."""
    t = (root / "SCRIPT.md").read_text()
    lineas = []
    for m in re.finditer(r"(?ms)^## Line (\d+) — .*?\n(.*?)(?=^## Line|\Z)", t):
        txt = " ".join(l.strip() for l in m.group(2).splitlines() if l.startswith("    ")).strip()
        if txt:
            lineas.append(txt)
    return lineas


def tramos(lineas, maximo):
    """Agrupa líneas completas en tramos de hasta `maximo` caracteres."""
    out, actual = [], []
    for l in lineas:
        if actual and len(" ".join(actual + [l])) > maximo:
            out.append(actual)
            actual = []
        actual.append(l)
    if actual:
        out.append(actual)
    return out


def pedir(texto, anterior, siguiente, clave):
    cuerpo = {
        "text": texto,
        "model_id": a.modelo,
        "voice_settings": {"stability": a.estabilidad, "speed": a.velocidad},
    }
    if anterior:
        cuerpo["previous_text"] = anterior
    if siguiente:
        cuerpo["next_text"] = siguiente
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{a.voz}/with-timestamps?output_format=mp3_44100_128",
        data=json.dumps(cuerpo).encode(),
        headers={"xi-api-key": clave, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"voz_elevenlabs: ElevenLabs respondió {e.code}: {e.read().decode()[:300]}")


def palabras(alineacion, desfase):
    """Junta los caracteres en palabras (se corta en los espacios) con el inicio del primero y el fin del último.
    Lo que va entre corchetes son etiquetas de tono que no se dicen: se salta."""
    out, actual, ini, fin, etiqueta = [], "", None, None, False
    for c, s, e in zip(alineacion["characters"], alineacion["character_start_times_seconds"], alineacion["character_end_times_seconds"]):
        if c == "[" or etiqueta:
            etiqueta = c != "]"
            continue
        if c.isspace():
            if actual:
                out.append({"text": actual, "start": round(ini + desfase, 3), "end": round(fin + desfase, 3)})
            actual, ini = "", None
            continue
        if ini is None:
            ini = s
        actual += c
        fin = e
    if actual:
        out.append({"text": actual, "start": round(ini + desfase, 3), "end": round(fin + desfase, 3)})
    return out


def duracion(mp3):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)], capture_output=True, text=True)
    return float(r.stdout.strip())


root = Path(a.root).resolve()
lineas = guion(root)
if not lineas:
    raise SystemExit("voz_elevenlabs: SCRIPT.md no tiene líneas «## Line N — Título» con el texto indentado 4 espacios")
if a.prueba:
    lineas = lineas[: a.prueba]
grupos = tramos(lineas, a.tramo)
caracteres = sum(len(" ".join(g)) for g in grupos)
print(f"{len(lineas)} línea(s), {caracteres} caracteres en {len(grupos)} llamada(s) a ElevenLabs ({a.modelo}, voz {a.voz})")
if not a.generar:
    print("No se generó nada. Con el OK del usuario, repite con --generar.")
    raise SystemExit

clave = os.environ.get("ELEVENLABS_API_KEY")
if not clave:
    raise SystemExit("voz_elevenlabs: falta ELEVENLABS_API_KEY (ver «Instalación» en SKILL.md)")
audio = root / "assets" / "audio"
audio.mkdir(parents=True, exist_ok=True)
mp3_final, tx = (audio / "prueba-voz.mp3", audio / "prueba-voz.json") if a.prueba else (audio / "narracion-completa.mp3", audio / "transcript.json")

todas, piezas, desfase = [], [], 0.0
with tempfile.TemporaryDirectory() as tmp:
    for k, g in enumerate(grupos):
        anterior = " ".join(grupos[k - 1]) if k else ""
        siguiente = " ".join(grupos[k + 1]) if k + 1 < len(grupos) else ""
        r = pedir(" ".join(g), anterior[-500:], siguiente[:500], clave)
        pieza = Path(tmp) / f"{k:03d}.mp3"
        pieza.write_bytes(base64.b64decode(r["audio_base64"]))
        todas += palabras(r.get("alignment") or r["normalized_alignment"], desfase)
        desfase += duracion(pieza)
        piezas.append(pieza)
        print(f"  tramo {k + 1}/{len(grupos)}: {duracion(pieza):.1f} s")
    if len(piezas) == 1:
        mp3_final.write_bytes(piezas[0].read_bytes())
    else:
        lista = Path(tmp) / "lista.txt"
        lista.write_text("".join(f"file '{p}'\n" for p in piezas))
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(mp3_final)], check=True)

tx.write_text(json.dumps(todas, ensure_ascii=False, indent=1))
print(f"{mp3_final.relative_to(root)}: {len(todas)} palabras, {duracion(mp3_final):.1f} s; tiempos en {tx.relative_to(root)}")
