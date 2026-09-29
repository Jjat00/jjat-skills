---
name: reel-editorial
description: Convierte una toma de cámara o webcam (una persona hablando) en un reel vertical 1080x1920 con estilo editorial — pantalla completa alternada con pantalla dividida (paneles de motion graphics sobre papel crema arriba y la persona recortada sobre una tarjeta roja o azul abajo), subtítulos palabra a palabra con palabras clave resaltadas, titulares serif itálica, números y palabras gigantes en rojo, terminales, chats, sellos y una mascota propia, con cortes rápidos que quitan tomas falsas y pausas. Úsala siempre que Jaime pida "un reel con el mismo formato", "como el reel de Claude y Codex", "estilo editorial", "pasa este video de webcam a reel", "ponle motion graphics a este video donde hablo", o quiera copiar el estilo de un reel sobre una grabación suya, aunque no nombre la skill. Trabaja en local con ffmpeg, faster-whisper y HyperFrames; no necesita Gemini.
---

# Reel editorial

Formato probado el 29-09-2026 con el reel «Claude Code implementa, Codex evalúa» (65 s). Qué lo hace funcionar:
cortes rápidos sin pausas, alternar composiciones cada pocos segundos, y que **cada gráfico entre en la palabra que lo
motiva**. El ejemplo completo está en `references/ejemplo-claude-codex/` y el catálogo de piezas en
`references/componentes.md`.

`<SKILL>` es la carpeta de esta skill. Todo corre en local y gratis.

## 1. Preparar

- Pregunta solo lo que cambie el resultado: qué video, si hay reel de referencia, y si alterna pantalla completa como la
  referencia o prefiere más pantalla dividida (la webcam de 720p se ve algo menos nítida a pantalla completa). Por
  defecto: sin música, solo efectos de la sonoteca.
- Crea el proyecto con el flujo de HyperFrames (carga `/hyperframes` y `/general-video`; ruta `general-video`):

  ```bash
  npx hyperframes init "videos/<slug>" --non-interactive --example=blank --skill=general-video
  mkdir -p videos/<slug>/{assets/fonts,assets/sfx,assets/img,work}
  cp <SKILL>/assets/fonts/* videos/<slug>/assets/fonts/
  ```

  Escribe `BRIEF.md` como pide `/general-video`.
- Efectos: copia de la sonoteca (`/mnt/d/sonidos`, ver su `catalogo.json`) los que uses; los habituales son
  `transiciones/whoosh-corto`, `ui/pop`, `ui/click-suave`, `notificaciones/chime-exito`, `notificaciones/ping`,
  `impactos/impacto-grave-swell`. **No uses `impactos/destello`** (a Jaime no le gusta).
- Logos: `npx hyperframes media-use resolve --type logo --entity <marca> --intent "<marca> logo" --project .`

## 2. Montaje por transcripción

1. Transcribe la toma original y lee el `.txt` para encontrar tomas falsas, repeticiones y el mejor gancho:

   ```bash
   uv run --with faster-whisper python <SKILL>/scripts/transcribe.py "<fuente>" work/fuente.json
   ```

2. Decide los rangos que se quedan (el gancho puede ir primero aunque se haya dicho después) y monta:

   ```bash
   python <SKILL>/scripts/cut.py "<fuente>" assets/edit.mp4 --keep "17.95-24.62,25.28-34.28,39.78-97.0"
   ```

   Recorta las pausas de más de 0,35 s. Un reel de 100 s de toma suele quedar en 60–70 s.
3. **Vuelve a transcribir el montaje** con glosario: estas marcas son las que sincronizan todo.

   ```bash
   uv run --with faster-whisper python <SKILL>/scripts/transcribe.py assets/edit.mp4 assets/words.json --glossary work/glosario.json
   ```

   Whisper escribe mal los nombres técnicos: `{"Cloud": "Claude", "Codecs": "Codex", "Herder": "Herdr", "comida": "commit"}`.
   Revisa también tildes («véanlo», «háganlo», «sí he visto»).

## 3. Recorte de la persona

Saca un fotograma (`ffmpeg -ss 20 -i assets/edit.mp4 -frames:v 1 work/f.jpg`), mira dónde está la persona y recorta
una zona de **840×720** a su alrededor antes de quitar el fondo (es más rápido y la plantilla está calibrada para ese
tamaño):

```bash
ffmpeg -i assets/edit.mp4 -vf "crop=840:720:<x>:0" -an -c:v libx264 -crf 14 work/edit_crop.mp4
npx hyperframes remove-background work/edit_crop.mp4 -o assets/presenter-alpha.webm --quality best
```

Tarda ~0,7 s por fotograma en CPU (**~23 min para 65 s**): lánzalo en segundo plano y diseña mientras tanto. Si el
recorte no es 840×720, ajusta `#presenter-alpha` en la plantilla (ancho ≈ 1,49 × ancho del recorte). Para la pantalla
completa, `object-position` del video es el centro de la persona en x (en el ejemplo, 54,7 %).

## 4. Plan y contenido

- **Tramos** (`reel.json.windows`): empieza con 2–3 s a pantalla completa (gancho), luego alterna. Los tramos a pantalla
  completa duran 3–5 s y llevan un texto encima (overlay); los de pantalla dividida llevan 1–3 paneles. Colores de
  tarjeta: `red` y `blue` (o hex en `card_colors`).
- **Paneles:** una idea por panel, numerada ("01 · EL TRUCO", "02 · EL PROBLEMA"…) y con un blueprint de
  `/hyperframes-animation` (los que funcionaron: `comparison-split`, `kinetic-type-beats`, `device-surface-showcase`,
  `prompt-type-submit-generate`, `agent-progress-theater`). Cierra con una llamada a la acción grande.
- Copia `references/ejemplo-claude-codex/` a `work/` (`overlays.html`, `panels.html`, `scenes.js`) y `reel.json` a la
  raíz; reescribe el contenido con las piezas de `references/componentes.md`. Las marcas de tiempo salen de
  `assets/words.json`.
- `reel.json`: `duration` (la del montaje), `windows`, `keywords` (palabras que se resaltan en los subtítulos), `sfx`
  (`{name, at, volume}`; el whoosh de cada cambio de composición se añade solo) y `typing` (tecleos).

## 5. Construir y validar

```bash
python <SKILL>/scripts/build.py .            # genera index.html
npx hyperframes lint
npx hyperframes snapshot --at <momentos clave> --no-end   # mira snapshots/contact-sheet.jpg
npx hyperframes check                        # debe pasar: 0 errores, contraste AA
```

Revisa la hoja de capturas y corrige solapes, textos que se salen o gráficos que tapan la cara antes de renderizar.

## 6. Render y entrega

```bash
npx hyperframes render -o renders/<slug>.mp4 -f 30 -q delivery --skill general-video   # ~13 min en CPU
python <SKILL>/scripts/normalize_audio.py renders/<slug>.mp4 renders/<slug>-final.mp4  # −14 LUFS, pico < −1 dBTP
cp renders/<slug>-final.mp4 "/mnt/c/Users/Jaime Jjat/Downloads/<slug>.mp4"
```

El render sale a unos −22 LUFS: la normalización no es opcional para Reels y TikTok. Antes de entregar, mira una hoja de
fotogramas del archivo final (`ffmpeg -vf "fps=1/5,scale=216:-1,tile=7x2"`).
