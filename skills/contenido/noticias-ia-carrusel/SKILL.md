---
name: noticias-ia-carrusel
description: Investiga las noticias de inteligencia artificial y software del DÍA (últimas 24-36 h, fecha verificada), descarga o captura el video o la imagen de cada una y entrega el carrusel ya renderizado para Instagram (4:5, láminas de video MP4 e imagen PNG) y TikTok (9:16, solo imágenes), con caption, hashtags, hora de publicación y una página de descarga. Estilo visual de jaimeaza.tech. Úsala siempre que Jaime pida "las noticias de IA de hoy", "el carrusel de hoy", "el post del día", "ideas de posts de IA para hoy", "haz el carrusel de noticias" o quiera publicar noticias de IA/software en sus redes, aunque no nombre la skill. Solo para el nicho IA y software; otro nicho es otra skill.
---

# Carrusel diario de noticias de IA y software

Resultado: un carrusel de 10 a 14 láminas y un reel con las mismas noticias de IA y software de hoy, listos para subir. No son ideas ni guiones: son los archivos finales más una página donde se descarga cada uno.

- **Instagram:** 1080×1350. Las láminas con video son MP4 de 8-9 s con audio original; las demás, PNG.
- **TikTok (modo foto):** 1080×1920, solo PNG. La franja inferior y el borde derecho quedan libres para la interfaz de TikTok.
- **Página de descarga:** un Artifact con pestañas Instagram/TikTok, caption con botón de copiar y hora de publicación.

Todo va en `D:\contenido\noticias <día> <mes> <año>\` (en WSL: `/mnt/d/contenido/noticias <día> <mes> <año>/`). Ejemplo: `D:\contenido\noticias 29 sept 2026`. El nombre dice de qué trata la carpeta, con el mes abreviado en español (ene, feb, mar, abr, may, jun, jul, ago, sept, oct, nov, dic) y sin ceros a la izquierda en el día. Jaime lo pidió así el 2026-09-29. No uses `Downloads`, y no toques las carpetas `instragram` y `tiktok` que ya hay en `D:\contenido`. La ruta lleva espacios: ponla siempre entre comillas.

```
noticias <día> <mes> <año>/
  plan.json            # el guion del carrusel (la fuente de verdad)
  medios/              # videos e imágenes originales de cada noticia
  carrusel/            # Instagram: 01.mp4, 02.mp4, 03.png…
  carrusel_tiktok/     # TikTok: 01.png…13.png
  PUBLICACIONES_<fecha>.md   # captions, horas, ideas de reel
```

Formato de referencia: los carruseles de @ingenia.ai (portada con titular gigante y palabras resaltadas; luego una lámina por noticia con titular, párrafo corto y el video o la imagen real de la noticia). Estilo propio: paleta y red de partículas de jaimeaza.tech, ver `references/estilo.md`.

## Pasos

### 1. Investigar (en paralelo)
Lanza dos agentes `general-purpose` en el mismo mensaje con los prompts de `references/investigacion.md`:
- **Noticias:** 10-12 noticias de las últimas 24-36 h con fecha verificada, fuente, y URL directa del medio (mp4, YouTube, post de X, og:image).
- **Tendencias:** temas y formatos que funcionan esta semana. No hace falta todos los días; úsalo si pasó más de una semana desde la última vez o si Jaime lo pide.

Hoy es la fecha del sistema. Descarta todo lo que no sea de hoy o ayer: es la regla que más pide Jaime.

### 2. Elegir 6-8 noticias
Prioriza las que tienen **video oficial o demo visual** (robots, generadores de video, gadgets, juegos hechos con IA). Una noticia sin imagen propia solo entra si es muy fuerte (entonces se usa una captura del titular o un gráfico propio). Orden: la más viral primero después de la portada; la polémica en el medio; cierre con CTA.

### 3. Conseguir los medios → `medios/`
Por orden de preferencia:
1. `curl -sL -A "Mozilla/5.0" -o medios/NN_nombre.mp4 <url directa>` para mp4 e imágenes.
2. `uvx yt-dlp -q -f "bv*[height<=1080]+ba/b" --merge-output-format mp4 -o "medios/NN_nombre.%(ext)s" <url>` para YouTube, v.redd.it y X.
3. `scripts/capture.py shot|rec` (Playwright) cuando no hay archivo: captura del titular o del comunicado, o grabación de una demo o galería (`rec --scroll`).
4. Un gráfico propio (`"stat"` en el plan) cuando el dato es un número que se lee mal en una captura (benchmarks, precios).

Prefijo `NN_` con el número de la noticia. Revisa cada medio (hoja de contactos o una miniatura) antes de usarlo.

### 4. Elegir tramos de video
Por cada video: `scripts/sheet.sh <video> 2 hoja.jpg [crop=…]` y mira la hoja. El número de cada miniatura es exactamente el segundo que va en el plan.
- `ss`: inicio del clip (8-9 s en `t`). Evita tramos con subtítulos quemados en otro idioma o con rótulos del tráiler.
- `still`: segundos desde `ss` para el fotograma de TikTok. Tiene que ser un fotograma limpio, sin rótulos.
- `crop`: si el video trae franjas negras (tráileres), detéctalas con `cropdetect` (comando en `sheet.sh`). También sirve para quedarte con la pantalla del escenario en un keynote.
- `tt_media` / `tt_pill`: imagen y frase propias solo para TikTok. Úsalas cuando el medio es muy horizontal (dos paneles lado a lado): en TikTok van apilados en vertical (ffmpeg `crop` + `vstack`) y la frase cambia de «izquierda/derecha» a «arriba/abajo».
- Si el día tiene un evento después de publicar la versión de la mañana (keynote), rehaz el plan con sus láminas primero y guarda el anterior como `plan_manana.json` y `version_manana/`.

### 5. Escribir `plan.json`
Copia la forma de `references/ejemplo-2026-09-29/plan.json`. Reglas de texto en `references/copy.md` (titular ≤ 12 palabras con una parte en `<b>` que se pinta con el degradado, párrafo ≤ 45 palabras con cifras concretas, frase corta sobre el medio, fuente siempre).

### 6. Renderizar
```bash
S=~/.claude/skills/noticias-ia-carrusel/scripts
uv run --with playwright python $S/render.py "<carpeta>/plan.json" --mode ig
uv run --with playwright python $S/render.py "<carpeta>/plan.json" --mode tiktok
```
`--only 4 7` re-renderiza solo esas láminas. Revisa el resultado con una hoja de miniaturas (un fotograma de cada MP4 y cada PNG, `hstack`/`vstack` con ffmpeg) y corrige: texto que se sale, medio mal encuadrado, rótulos del video, subtítulos que chocan con la frase del medio.

### 6b. Reel con las mismas noticias
Siempre se entrega también un reel vertical (1080×1920) con las mismas láminas.
- Cada lámina muestra el titular grande y la frase sobre el medio. El párrafo no sale, porque en el tiempo que dura no se alcanza a leer.
- Las láminas de video usan su clip; las de imagen, un zoom lento.
- En cada corte suena un whoosh de `D:\sonidos\transiciones`.
- La mezcla sale normalizada a −14 LUFS.

**Antes de hacerlo, pregunta en una sola AskUserQuestion** (dos preguntas):
1. **¿Con narración o sin narración?**
   - Sin narración: unos 45 s (3,5 s por noticia). Jaime pone un audio en tendencia desde la app.
   - Con narración: la voz cuenta cada noticia y cada lámina dura lo que dura su frase (unos 55-60 s).
2. **Voz** (solo si hay narración). Ofrece estas y deja «Other» para cualquier otra:
   - **Gonzalo, colombiano** (`es-CO-GonzaloNeural`, edge-tts, **gratis**). Es la opción por defecto.
   - **Salomé, colombiana** (`es-CO-SalomeNeural`, edge-tts, **gratis**).
   - **Locutor latino de ElevenLabs** (`gWS10amJmGDgPWjYrvU7`, voz comercial, **de pago**).
   - **Jennifer, colombiana, de ElevenLabs** (`Y11rBAl8on4Ba9ZpY3DY`, **de pago**).

   Otras voces de la cuenta, con `list_voices` de HF Studio:
   - Joel (`2mAzYQbilw9TukGpFoQV`, voz grave mexicana);
   - Carlos Corella (`LnGOA2SxH2fX1e1iNzEp`);
   - Alejandro (`qXvyMc4erc4RzqXLpiiR`).

   En edge-tts también hay `es-MX-JorgeNeural` y `es-MX-DaliaNeural`.

**Narración:** campo `"narracion"` en cada lámina del plan.
- **Largo:** 8-15 palabras por lámina.
- **Gancho:** el de la portada va en los primeros 2-3 s y cabe en 12 palabras.
- **Números:** escritos en letras, para que la voz los lea bien («seis punto uno», «ocho mil doscientos millones», «cuatro K»).
- **Duración total:** 60 s como máximo.

**Voz gratis (edge-tts):**
```bash
python $S/narrar.py "<carpeta>/plan.json" --voz es-CO-GonzaloNeural --velocidad +15%
```
Escribe `reel/voz/NN.mp3` e imprime la duración de cada frase. Si el total pasa de 60 s, acorta textos.

**Voz de ElevenLabs (de pago):**
1. Por cada lámina, llama a `text_to_speech` de HF Studio, primero sin `quote_id`, y suma el costo.
2. Díselo a Jaime y espera su OK (regla de costo visible).
3. Genera con los `quote_id`.
4. Descarga cada MP3 a `reel/voz/NN.mp3`.

**Render:**
```bash
uv run --with playwright python $S/render.py "<carpeta>/plan.json" --mode reel            # con voz si existe reel/voz/
uv run --with playwright python $S/render.py "<carpeta>/plan.json" --mode reel --sin-voz  # sin narración
```
Salen `reel/reel_<fecha>.mp4` y `reel/reel_<fecha>_narrado.mp4`.
- **Tramo distinto para el reel:** `reel_ss` elige otro tramo del video (el clip del carrusel puede caer en un rótulo del tráiler).
- **Duración a mano:** `reel_t` fija cuánto dura una lámina.
- **Música:** `--musica <archivo>` agrega una pista de fondo.

Revisa una tira de fotogramas y el volumen (`ebur128`) antes de entregar.

### 7. Página de descarga
```bash
python $S/build_page.py "<carpeta>/plan.json" --out <scratchpad>/pagina_<fecha>
```
Imprime `index`, `root` y `files`. Publica un Artifact **nuevo por día** con `file_path=index`, `root`, `files` (todas las rutas que imprimió), `capabilities={"downloads": true}` e `icon="download"`. Los `<a download>` no funcionan dentro de un Artifact; la página ya usa la capacidad `downloads`. El Artifact solo acepta archivos bajo el scratchpad o el directorio de trabajo: por eso `--out`.

### 8. Entregar
- Tabla corta de las láminas (número, tipo, noticia), link de la página, carpeta local y la hora sugerida.
- Si hay un evento el mismo día (keynote, lanzamiento anunciado), dilo y ofrece cambiar una lámina después.
- `PUBLICACIONES_<fecha>.md` con captions de Instagram y TikTok y 1-2 ideas de reel del día (ver `references/copy.md`).
- Vault: actualiza `Proyectos/Contenido diario de IA en redes.md` (una línea de estado) y `Registro.md`.

## Reglas
- **Solo noticias de hoy o ayer**, con fecha comprobada en la fuente. Si una fecha no se puede verificar, no entra.
- **Nunca inventes** cifras, citas ni nombres. Si dos fuentes discrepan (p. ej. el nombre de un modelo), usa la oficial y menciónalo en la entrega.
- **Derechos:** en Colombia rige el derecho de cita, no el «fair use». Clips cortos (8-9 s), fuente visible en cada lámina, texto propio dominante, sin marcas de agua de otras apps. Detalle en `references/copy.md`.
- **Sin marca por ahora:** la etiqueta es «NOTICIAS DE IA · <fecha>». Cuando Jaime entregue logo y @, se añaden en `assets/slide.css` y `render.py` (`head`).
- **No publiques en las redes**: la skill entrega archivos; subirlos es de Jaime.
