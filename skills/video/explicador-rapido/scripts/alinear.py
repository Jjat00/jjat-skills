"""Alinea la transcripción (palabras con tiempo) con las líneas del guion, corta el audio acelerado por escena
y escribe audio_meta.json (forma frame-keyed que consumen captions.mjs y assemble-index.mjs).

  python3 <SKILL>/scripts/alinear.py --root . --tx assets/audio/transcript.json \
      --audio assets/audio/narracion-completa-x1.13.mp3 --tempo 1.13
--tx es la transcripción de la toma ORIGINAL (sin acelerar); sus tiempos se dividen por --tempo.
--audio es la toma ya acelerada (la que suena en el video). Sin aceleración: --tempo 1.
SCRIPT.md debe usar el formato «## Line N — Título» con el texto indentado 4 espacios.
Las palabras de los subtítulos salen del GUION (ortografía exacta), con los tiempos de la transcripción.
"""
import argparse
import difflib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".", help="raíz del proyecto HyperFrames (donde está SCRIPT.md)")
ap.add_argument("--tx", required=True)
ap.add_argument("--tempo", type=float, default=1.0)
ap.add_argument("--audio", required=True, help="toma completa, ya acelerada si se usó rubberband")
a = ap.parse_args()
ROOT = Path(a.root).resolve()


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


# guion por línea
t = (ROOT / "SCRIPT.md").read_text()
lines = []
for m in re.finditer(r"(?ms)^## Line (\d+) — .*?\n(.*?)(?=^## Line|\Z)", t):
    txt = " ".join(l.strip() for l in m.group(2).splitlines() if l.startswith("    "))
    txt = re.sub(r"\[.*?\]\s*", "", txt)
    lines.append((int(m.group(1)), txt.split()))
script_words = [(n, w) for n, ws in lines for w in ws]

raw = json.loads((ROOT / a.tx).read_text())
tw = raw if isinstance(raw, list) else raw.get("words", raw.get("segments", []))
tx = [{"text": w.get("text", w.get("word", "")).strip(), "start": float(w["start"]) / a.tempo, "end": float(w["end"]) / a.tempo} for w in tw]
tx = [w for w in tx if norm(w["text"])]

A = [norm(w) for _, w in script_words]
B = [norm(w["text"]) for w in tx]
sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
time = [None] * len(A)
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        time[blk.a + k] = (tx[blk.b + k]["start"], tx[blk.b + k]["end"])
# interpolar huecos (números escritos distinto, siglas, etc.)
known = [i for i, v in enumerate(time) if v]
for i in range(len(time)):
    if time[i] is None:
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        s = time[prev][1] if prev is not None else 0.0
        e = time[nxt][0] if nxt is not None else s + 0.4
        gap = [j for j in range(prev + 1 if prev is not None else 0, nxt if nxt is not None else len(time))]
        idx = gap.index(i)
        step = (e - s) / max(1, len(gap))
        time[i] = (s + idx * step, s + (idx + 1) * step)
matched = sum(1 for blk in sm.get_matching_blocks() for _ in range(blk.size))
print(f"palabras guion {len(A)} · transcritas {len(B)} · alineadas {matched}")

total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / a.audio)]).decode())
# cortes por escena: punto medio del silencio entre la última palabra de N y la primera de N+1
first = {}
last = {}
for i, (n, _) in enumerate(script_words):
    first.setdefault(n, i)
    last[n] = i
nums = [n for n, _ in lines]
cuts = [0.0]
for n, nx in zip(nums, nums[1:]):
    cuts.append(round((time[last[n]][1] + time[first[nx]][0]) / 2, 3))
cuts.append(round(total, 3))

# los tiempos de Whisper son aproximados: lleva cada corte al tramo más silencioso (ventanas de 20 ms) a ±0,35 s
import array
pcm = array.array("h", subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / a.audio), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                                     capture_output=True, check=True).stdout)
SR, WIN = 16000, 320


def energia(t):
    i = int(t * SR)
    seg = pcm[max(i - WIN // 2, 0):i + WIN // 2]
    return sum(x * x for x in seg) / max(len(seg), 1)


for k in range(1, len(cuts) - 1):
    c = cuts[k]
    cand = [c + d / 100 for d in range(-35, 36)]
    cuts[k] = round(min(cand, key=lambda t: (energia(t), abs(t - c))), 3)
wav = ROOT / "assets/audio/.toma.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / a.audio), str(wav)], check=True)

outdir = ROOT / "assets/voice"
outdir.mkdir(parents=True, exist_ok=True)
voices = []
for k, n in enumerate(nums):
    s, e = cuts[k], cuts[k + 1]
    p = outdir / f"{n:02d}.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", str(wav),
                    "-af", f"afade=t=in:d=0.01,afade=t=out:st={max(e - s - 0.01, 0):.3f}:d=0.01",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(p)], check=True)
    words = []
    for i in range(first[n], last[n] + 1):
        ws, we = time[i]
        words.append({"id": f"w{i}", "text": script_words[i][1], "start": round(ws - s, 3), "end": round(we - s, 3)})
    voices.append({"frame": n, "path": f"assets/voice/{n:02d}.mp3", "duration_s": round(e - s, 3), "start_global": s, "words": words})
    print(f"{n:02d} {s:7.2f} → {e:7.2f}  ({e - s:5.2f}s)  {' '.join(w['text'] for w in words)[:70]}")
meta = {"voices": voices, "bgm": None, "sfx": []}
(ROOT / "audio_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
wav.unlink()
print("total", total)
