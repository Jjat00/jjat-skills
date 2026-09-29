#!/usr/bin/env bash
# Hoja de contactos para elegir `ss` (inicio del clip) y `still` (fotograma de TikTok).
# Cada miniatura sale de `ffmpeg -ss T` (la misma búsqueda que usa render.py), así que el número
# impreso es exactamente el segundo que hay que poner en el plan.
# Uso: sheet.sh <video> <cada_n_segundos> <salida.jpg> [crop=w:h:x:y]
# Franjas negras de tráileres: ffmpeg -ss 5 -t 3 -i v.mp4 -vf cropdetect=24:2:0 -f null - 2>&1 | grep -o 'crop=[0-9:]*' | tail -1
set -euo pipefail
v="$1"; n="$2"; out="$3"; crop="${4:-}"
pre=""; [ -n "$crop" ] && pre="$crop,"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$v" | cut -d. -f1)
i=0; args=()
for ((t=0; t<d && i<30; t+=n)); do
  ffmpeg -v error -y -ss "$t" -i "$v" -frames:v 1 -vf "${pre}scale=300:-2,drawtext=text='$t s':x=6:y=6:fontsize=24:fontcolor=yellow:box=1:boxcolor=black" "$tmp/$(printf %03d $i).png"
  i=$((i+1))
done
ffmpeg -v error -y -pattern_type glob -i "$tmp/*.png" -vf "tile=6x5:padding=4" -frames:v 1 "$out"
echo "$out ($i miniaturas)"
