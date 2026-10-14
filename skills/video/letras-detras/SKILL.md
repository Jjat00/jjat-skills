---
name: letras-detras
description: >
  Pone la letra de una canción en tipografía gigante DETRÁS del sujeto de un video (estilo lyric video
  editorial: serif condensada alta, palabras que aparecen al ritmo de la voz, la cabeza/cuerpo tapando
  las letras, acentos en rojo o dorado) y le monta la canción. Entradas: el video + la canción como link de
  Spotify, «artista - canción» o solo el nombre; la letra sincronizada sale sola de LRCLib (como
  Frostbyte) y el audio de YouTube, o se pasan a mano. Úsala cuando Jaime pida "letras detrás",
  "lyric video", "la letra de la canción en el video", "letras gigantes detrás de mí", o comparta un
  video con una canción para hacer ese efecto, aunque no nombre la skill.
---

# Letras detrás del sujeto

Reproduce el efecto de `video_ref_letras_atras.mp4`: palabras de la canción en una serif Didone muy
condensada (Bodoni Moda comprimida), apiladas en filas justificadas, que se escriben letra a letra cuando
se cantan y quedan **detrás** de la persona gracias a un matte (Robust Video Matting). Bloques de 1 a 4
palabras que cambian de golpe con cada frase; algunas filas en rojo o dorado como acento.

Todo es local y gratis: no hay generación de pago (LRCLib, YouTube, Whisper y RVM en CPU).

## Entradas

| Qué | Obligatorio | Formas aceptadas |
|---|---|---|
| Video | sí | cualquier mp4/mov; horizontal o vertical; mejor si hay una persona clara |
| Canción | sí | link de Spotify (`open.spotify.com/track/…`), `"Artista - Canción"` o solo `"Canción"` |
| Audio | no | `--audio archivo.mp3` si Jaime lo tiene (si no, se baja de YouTube) |
| Letra | no | `--lyrics letra.txt` (texto plano o LRC) solo si LRCLib no la tiene |
| Tramo | no | `--start <segundo>` de la canción; por defecto arranca en el coro |

Con solo el nombre, el script elige primero el audio en YouTube (descarta covers, live, sped up, remix…)
y después la letra de LRCLib cuyo artista y duración casen con ese audio. Si el nombre es ambiguo,
pide el artista o el link de Spotify.

## Flujo

Script único con dependencias inline (uv las instala solo):

```bash
S=~/.claude/skills/letras-detras/scripts/letras.py
P="/mnt/d/contenido/<tema día mes año>/letras"     # carpeta del proyecto (regla de D:\contenido)

uv run $S all "$P" "<canción>" --video "<video>"  [--start 63.2] [--audio x.mp3] [--lyrics x.txt]
#   = song → segment → align → plan → matte   (≈1 min por cada 5 s de video en CPU, sobre todo el matte)
uv run $S preview "$P"           # fotogramas compuestos → $P/preview/sheet.png (segundos)
# … revisar y editar $P/plan.json …
uv run $S render "$P"            # → $P/final.mp4 (video + letras + canción, fundido al final)
```

Pasos sueltos si hay que repetir uno: `song`, `segment` (cambiar el tramo), `align` (`--model medium`
si la voz se entiende mal), `plan --force` (regenera y **pisa ediciones a mano**), `matte`, `preview [t…]`.
Tras cambiar el tramo hay que repetir `align` y `plan --force`.

### 1. Revisar lo automático (lee la salida, no la des por buena)

- `song`: ¿es el artista y la versión correctos? ¿aviso de duración distinta entre letra y audio?
- `segment`: imprime las líneas que caen en el video. Si el coro no es el mejor tramo, propón otro a
  Jaime con `--start`.
- `align`: `N con tiempo de Whisper`. Si casi ninguna casó, la letra es de otra versión o el tramo es
  instrumental; los tiempos quedan de LRC por línea (sirve, pero menos preciso).

### 2. Paso creativo: editar `plan.json`

`plan.json` = `style` + `blocks[]`; cada bloque tiene `start`/`end` (s, relativo al video) y `rows[]`,
cada fila `color` y `words[]` con su `t`/`e`. Lo que se decide con criterio:

- **Acentos**: el plan pone rojo/dorado de forma mecánica. Muévelos a las palabras con carga (en la
  referencia: STOP, DO THIS, LOSIN', FOREVER). Uno de cada 2 o 3 bloques como máximo; si todo es
  rojo, nada lo es. Colores: `white` (base), `red`, `gold` (degradado dorado), `gray` (translúcido,
  para un cierre que se apaga), `ink` (casi negro; se aplica solo en fondos claros).
- **Cortes**: un bloque es lo que se lee de un vistazo (1 a 4 palabras). Divide o une filas para que
  palabras cortas vayan juntas («BUT I») y las largas solas («EVERYBODY»).
- **Texto**: mayúsculas automáticas; corrige faltas de la letra (LRCLib a veces trae errores).

Estilo (`style`, todos opcionales): `anchor` (`head` centra el bloque a la altura de la cabeza del
sujeto; `top` usa `block_top`), `head_offset`, `block_w` (ancho de fila), `row_max_h`, `block_max_h`,
`condense` (0.56; más bajo = más estrecho), `font_weight`, `font` (otra .ttf), `letter_reveal`,
`fade_in`, `fade_out`, `dim_bg` (oscurecer el fondo), `shadow`, `auto_ink`, `ink_threshold`, `center_x`.

**Video horizontal (W>H)**: `plan` lo detecta y usa otros valores, porque con la cara centrada en 16:9
la cabeza llena casi todo el alto y los bloques de 3–4 filas a la altura de la cabeza quedaban tapados
(probado con webcam 1280x720, 2026-10): `anchor: top`, `block_top: 0.02`, `row_max_h: 0.34`,
`block_max_h: 0.6`, `block_w: 0.94`, `condense: 0.66`; máximo **2 filas por bloque** (uno de 3 filas
se parte en 1 + 2) y los bloques de menos de **0.7 s** se funden con el vecino de su misma línea.
Se fuerza o se ajusta con `--layout horizontal|vertical`, `--max-rows N` (0 = sin límite) y
`--merge-short S` (0 = no fundir); los flags explícitos mandan sobre lo automático. El vertical no cambia.

### 3. Control visual antes del render

`preview` y mira `sheet.png`:
1. ¿Se lee? Si la letra blanca se pierde sobre un fondo claro, `auto_ink` debería pasarla a tinta;
   si no, baja `ink_threshold` o sube `dim_bg`.
2. ¿Queda **detrás** del sujeto y él tapa entre un 20 % y un 50 % del bloque? Si queda flotando lejos,
   ajusta `head_offset`; si lo tapa todo, súbelo con un `head_offset` negativo.
3. ¿El matte recorta bien? RVM está entrenado con personas: objetos sostenidos o vehículos pueden
   quedar fuera (la letra pasa por delante). Mira 2–3 PNG de `$P/matte/`.
4. ¿El orden de lectura de arriba abajo es el orden cantado?

Luego `render` y extrae 2–3 fotogramas de `final.mp4` para confirmar antes de entregarlo.

## Entrega

`final.mp4` en `D:\contenido\<tema día mes año>\…`. Di a Jaime qué tramo de la canción usaste y
qué palabras acentuaste. Recuerda que en Instagram/TikTok una canción comercial incrustada puede
silenciarse por derechos: si va a publicarlo, conviene exportar también sin audio
(`ffmpeg -i final.mp4 -an -c:v copy final_sin_audio.mp4`) y ponerle la música desde la app, al mismo
tramo (el inicio está en `segment.json → song_start`).

## Límites conocidos

- La alineación es por palabra con Whisper sobre la mezcla (sin separar voz): buena en pop/rap con voz
  clara, peor con mucha reverb o coros. Fallback: tiempo de línea LRC repartido por longitud.
- yt-dlp avisa de que falta un runtime de JS; de momento descarga igual. Si YouTube empieza a fallar,
  instalar `deno` o pasar `--audio`.
- Cortes de plano: RVM es recurrente y tarda unos fotogramas en reajustarse tras un corte duro.
