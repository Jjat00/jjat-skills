#!/usr/bin/env bash
# Ensambla el video: subtítulos, escenas, transiciones, banda de subtítulos, zona segura del feed y lint.
# Se puede correr las veces que haga falta (cada paso reescribe lo suyo).
#
#   bash <SKILL>/scripts/ensamblar.sh [carpeta-del-proyecto]
#
# Necesita STORYBOARD.md y audio_meta.json (de alinear.py) en el proyecto, y las escenas en compositions/frames/.
# Si el proyecto tiene tools/despues_de_ensamblar.py, lo corre al final para sus capas propias (p. ej. un botón
# SEGUIR encima del video). La versión de HyperFrames se fija con HYPERFRAMES_VERSION.
set -euo pipefail

SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HF="$SKILL/scripts/hf"
HYPERFRAMES_VERSION="${HYPERFRAMES_VERSION:-0.8.186}"
cd "${1:-.}"

for f in STORYBOARD.md audio_meta.json; do
  [ -f "$f" ] || { echo "ensamblar: falta $f en $(pwd)" >&2; exit 2; }
done
mkdir -p .hyperframes
[ -f .hyperframes/caption-skin.html ] || cp "$SKILL/assets/caption-skin.html" .hyperframes/caption-skin.html

node "$HF/captions.mjs" build --storyboard ./STORYBOARD.md --audio-meta ./audio_meta.json --hyperframes . --out ./caption_groups.json | tail -1
node "$HF/assemble-index.mjs" --storyboard ./STORYBOARD.md --hyperframes . | tail -1
node "$HF/transitions.mjs" inject --storyboard ./STORYBOARD.md --hyperframes . | tail -1
node "$HF/transitions.mjs" verify --storyboard ./STORYBOARD.md --index ./index.html | tail -1

# captions.mjs vuelve a poner su banda (dentro de la interfaz de Reels): la de la serie es 1445–1615.
sed -i 's/--cap-band-top: [0-9]*px;/--cap-band-top: 1445px;/; s/--cap-band-height: [0-9]*px;/--cap-band-height: 170px;/' compositions/captions.html

# Zona segura del feed de Instagram (recorte 4:5, y≈285–1635): cada escena se reduce y baja, sin fondo propio.
python3 - <<'PY'
s = open("index.html").read()
css = """
      /* zona segura del feed de Instagram (recorte 4:5 = y 285–1635): la escena se reduce y baja */
      .scene { transform: translate(0px, 184px) scale(0.865); transform-origin: 540px 0px; mix-blend-mode: lighten; }
      .scene [id$="-bg"] { background: transparent !important; }
      #root { background: radial-gradient(120% 80% at 50% 45%, #121212 0%, #0a0a0a 55%, #050505 100%); }
    </style>"""
if "zona segura" not in s:
    s = s.replace("    </style>", css, 1)
# el lint pide marcar la pista de subtítulos (caption_track_kind_missing)
if 'id="el-captions"' in s and 'data-track-kind="captions"' not in s:
    s = s.replace('id="el-captions"', 'id="el-captions"\n        data-track-kind="captions"', 1)
open("index.html", "w").write(s)
PY

if [ -f tools/despues_de_ensamblar.py ]; then python3 tools/despues_de_ensamblar.py; fi
npx --yes "hyperframes@$HYPERFRAMES_VERSION" lint | tail -3
