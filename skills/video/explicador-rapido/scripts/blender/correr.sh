#!/usr/bin/env bash
# Corre una toma de Blender en modo fondo y escribe sus PNG.
# Uso: correr.sh <toma> [args para el script, p. ej. --cuadros 1,120 --escala 50]
#   BLENDER  ejecutable (por defecto `blender` del PATH)
#   SALIDA   carpeta de los PNG (por defecto /tmp/blender/<toma>; mejor fuera del proyecto y de carpetas sincronizadas)
# En WSL con el Blender de Windows: BLENDER="/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" y una
# SALIDA en un disco de Windows (p. ej. /mnt/d/tmp/blender/<toma>); el script pasa las rutas con wslpath.
set -euo pipefail
TOMA="$1"; shift
DIR="$(cd "$(dirname "$0")" && pwd)"
BLENDER="${BLENDER:-blender}"
SALIDA="${SALIDA:-/tmp/blender/$TOMA}"
mkdir -p "$SALIDA"
if [[ "$BLENDER" == *.exe ]] && command -v wslpath >/dev/null; then
  "$BLENDER" -b --factory-startup -P "$(wslpath -w "$DIR/$TOMA.py")" -- --salida "$(wslpath -w "$SALIDA")" "$@"
else
  "$BLENDER" -b --factory-startup -P "$DIR/$TOMA.py" -- --salida "$SALIDA" "$@"
fi
