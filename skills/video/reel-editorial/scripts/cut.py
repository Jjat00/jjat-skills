"""Monta la toma: conserva los tramos del guion y acorta las pausas largas (cortes rápidos de reel).

Uso:
  python cut.py <fuente> <salida.mp4> --keep "17.95-24.62,25.28-34.28,39.78-97.0"
                [--pad 0.10] [--silence-db -30] [--min-silence 0.35] [--fps 30]

--keep son los rangos de la fuente que se quedan, en orden (quita tomas falsas y repeticiones).
Dentro de cada rango, toda pausa de más de --min-silence se recorta dejando --pad a cada lado.
Cada corte lleva un fundido de audio de 12 ms para que no haya clics. Imprime los segmentos y la duración.
Después, vuelve a transcribir la salida: las marcas medidas sobre el montaje son las que valen.
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--keep", required=True)
ap.add_argument("--pad", type=float, default=0.10)
ap.add_argument("--silence-db", type=float, default=-30)
ap.add_argument("--min-silence", type=float, default=0.35)
ap.add_argument("--fps", type=int, default=30)
args = ap.parse_args()

keep = [tuple(map(float, r.split("-"))) for r in args.keep.split(",")]
det = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", args.src, "-af", f"silencedetect=noise={args.silence_db}dB:d={args.min_silence}",
     "-f", "null", "-"],
    capture_output=True, text=True,
).stderr
marks = [float(x) for x in re.findall(r"silence_(?:start|end): ([0-9.]+)", det)]
silences = list(zip(marks[::2], marks[1::2]))

segs = []
for a, b in keep:
    cur = a
    for s, e in silences:
        if e <= a or s >= b:
            continue
        s2, e2 = max(s, a), min(e, b)
        if s2 + args.pad < e2 - args.pad and s2 + args.pad > cur:
            segs.append((cur, s2 + args.pad))
            cur = e2 - args.pad
    if cur < b:
        segs.append((cur, b))
segs = [(round(a, 3), round(b, 3)) for a, b in segs if b - a > 0.08]

fc, parts = [], []
for i, (a, b) in enumerate(segs):
    d = b - a
    fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps={args.fps}[v{i}]")
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(d - 0.012, 0):.3f}:d=0.012[a{i}]")
    parts.append(f"[v{i}][a{i}]")
fc.append("".join(parts) + f"concat=n={len(segs)}:v=1:a=1[v][a]")

with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
    f.write(";\n".join(fc))
subprocess.run(
    ["ffmpeg", "-y", "-v", "error", "-i", args.src, "-filter_complex_script", f.name, "-map", "[v]", "-map", "[a]",
     "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", args.out],
    check=True,
)
Path(f.name).unlink()
total = sum(b - a for a, b in segs)
print(f"{len(segs)} segmentos → {args.out} ({total:.2f} s)")
