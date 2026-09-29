#!/usr/bin/env bash
# Enlaza cada skill del repo (skills/<categoria>/<skill>/SKILL.md) en ~/.claude/skills/<skill>.
# No toca carpetas reales que ya existan con el mismo nombre; solo crea o actualiza enlaces.
set -euo pipefail
cd "$(dirname "$0")"
dest="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
dry=0; [ "${1:-}" = "--dry-run" ] && dry=1
mkdir -p "$dest"
find skills -mindepth 2 -maxdepth 3 -name SKILL.md -not -path '*/node_modules/*' | sort | while read -r f; do
  dir="$(cd "$(dirname "$f")" && pwd)"
  name="$(basename "$dir")"
  target="$dest/$name"
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    echo "omitida  $name  (ya existe una carpeta real en $target)"; continue
  fi
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$dir" ]; then
    echo "ok       $name"; continue
  fi
  if [ $dry = 1 ]; then echo "enlazaria $name -> $dir"; else ln -sfn "$dir" "$target"; echo "enlazada $name -> $dir"; fi
done
