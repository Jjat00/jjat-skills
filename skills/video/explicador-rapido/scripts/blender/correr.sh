#!/usr/bin/env bash
# Corre una toma de Blender en modo fondo (probado con Blender 5.2 de Windows lanzado desde WSL).
# Uso: correr.sh <toma> [args para el script, p. ej. --cuadros 1,120 --escala 50]
#   BLENDER   ejecutable (por defecto el de Windows en /mnt/c)
#   SALIDA_WIN carpeta Windows de los PNG (por defecto D:\tmp\blender\<toma>)
set -euo pipefail
TOMA="$1"; shift
DIR="$(cd "$(dirname "$0")" && pwd)"
BLENDER="${BLENDER:-/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe}"
SALIDA_WIN="${SALIDA_WIN:-D:\\tmp\\blender\\$TOMA}"
mkdir -p "$(wslpath -u "$SALIDA_WIN")"
"$BLENDER" -b --factory-startup -P "$(wslpath -w "$DIR/$TOMA.py")" -- --salida "$SALIDA_WIN" "$@"
