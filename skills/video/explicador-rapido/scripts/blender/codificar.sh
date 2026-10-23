#!/usr/bin/env bash
# Codifica los PNG de una toma a MP4 (H.264, yuv420p, BT.709, 30 fps, sin audio) con bloom suave.
# El bloom solo suma luz de lo que pasa de #0e: el fondo #0a0a0a queda intacto.
# Uso: tools/blender/codificar.sh <toma> [cuadros]   (cuadros recorta la duración, p. ej. 372 = 12,4 s)
set -euo pipefail
TOMA="$1"
LIM=()
[ -n "${2:-}" ] && LIM=(-frames:v "$2")
RAIZ="${RAIZ:-$(cd "$(dirname "$0")/../.." && pwd)}"  # raíz del proyecto (copia este script a tools/blender/)
SRC="${SRC:-/tmp/blender/$TOMA}"  # carpeta de los PNG (la SALIDA de correr.sh)
OUT="$RAIZ/assets/blender"
mkdir -p "$OUT"
BLOOM="format=rgb24,split=3[a][b][c];\
[b]lutrgb=r='max(val-14,0)':g='max(val-14,0)':b='max(val-14,0)',format=gbrp,gblur=sigma=6,lutrgb=r='val*0.22':g='val*0.22':b='val*0.22'[b1];\
[c]lutrgb=r='max(val-40,0)':g='max(val-40,0)':b='max(val-40,0)',format=gbrp,gblur=sigma=28,lutrgb=r='val*0.20':g='val*0.20':b='val*0.20'[c1];\
[a]format=gbrp[a1];[a1][b1]blend=all_mode=addition[ab];[ab][c1]blend=all_mode=addition,\
scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
ffmpeg -loglevel error -y -framerate 30 -i "$SRC/${TOMA}_%04d.png" -filter_complex "$BLOOM" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  "${LIM[@]}" -an -movflags +faststart "$OUT/$TOMA.mp4"
ffmpeg -loglevel error -y -i "$OUT/$TOMA.mp4" -vf "fps=1,scale=270:-1,tile=5x3" -frames:v 1 -q:v 3 "$OUT/hoja-$TOMA.jpg"
# píxel de esquina (debe dar ~0a0a0a)
ffmpeg -loglevel error -i "$OUT/$TOMA.mp4" -vf "select=eq(n\,100),crop=4:4:0:0,scale=1:1,format=rgb24" -frames:v 1 -f rawvideo - | xxd -p
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,pix_fmt,color_space -of default=nw=1 "$OUT/$TOMA.mp4"
