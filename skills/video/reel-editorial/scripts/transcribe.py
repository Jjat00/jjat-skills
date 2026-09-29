"""Transcribe un video o audio a palabras con marcas de tiempo (faster-whisper, en local).

Uso:
  uv run --with faster-whisper python transcribe.py <video> <salida.json> [--lang es] [--model small]
         [--glossary glosario.json]

Escribe <salida.json> (lista de {text, start, end}) y <salida>.txt (frases con tiempos, para leer el guion).
El glosario es un JSON {"palabra mal oída": "correcta"} que se aplica palabra a palabra, respetando la
puntuación final (p. ej. {"Cloud": "Claude", "Codecs": "Codex"}).
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--lang", default="es")
ap.add_argument("--model", default="small")
ap.add_argument("--glossary")
args = ap.parse_args()

fix = json.loads(Path(args.glossary).read_text()) if args.glossary else {}

# ffmpeg decodifica (evita depender de la versión de PyAV que traiga faster-whisper).
pcm = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", args.src, "-vn", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
    capture_output=True, check=True,
).stdout
audio = np.frombuffer(pcm, dtype=np.float32)
model = WhisperModel(args.model, device="cpu", compute_type="int8")
segs, _ = model.transcribe(audio, language=args.lang, word_timestamps=True, vad_filter=True)
words, lines = [], []
for s in segs:
    lines.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
    for w in s.words:
        text = w.word.strip()
        core, tail = re.match(r"^(.*?)([.,;:?!…]*)$", text).groups()
        text = fix.get(text, fix.get(core, core) + tail)
        words.append({"text": text, "start": round(w.start, 3), "end": round(w.end, 3)})

out = Path(args.out)
out.write_text(json.dumps(words, ensure_ascii=False, indent=0))
out.with_suffix(".txt").write_text("\n".join(lines))
print(f"{len(words)} palabras → {out}")
