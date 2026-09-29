"""Deja el audio de un render listo para redes: −14 LUFS y pico verdadero por debajo de −1 dBTP.

Uso: python normalize_audio.py <render.mp4> <final.mp4> [--lufs -14]

Dos pasadas de loudnorm y un limitador con sobremuestreo después: sin el limitador, el pico verdadero
sube por encima de 0 dBTP al codificar a AAC. La imagen se copia sin recodificar.
"""

import argparse
import json
import re
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--lufs", type=float, default=-14)
args = ap.parse_args()

probe = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", args.src, "-af", f"loudnorm=I={args.lufs}:TP=-2:LRA=11:print_format=json",
     "-f", "null", "-"],
    capture_output=True, text=True,
).stderr
m = json.loads(re.search(r"\{[^{}]*\}", probe, re.S).group(0))
af = (
    f"loudnorm=I={args.lufs}:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
    f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},"
    "aresample=192000,alimiter=limit=0.75:attack=1:release=50:level=false,aresample=48000"
)
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-i", args.src, "-c:v", "copy", "-af", af, "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", args.out],
    check=True,
)
check = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", args.out, "-af", "loudnorm=print_format=summary", "-f", "null", "-"],
    capture_output=True, text=True,
).stderr
print("\n".join(l.strip() for l in check.splitlines() if "Input Integrated" in l or "Input True Peak" in l))
