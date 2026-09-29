---
name: ruta-dron-ubicacion
description: Video de ubicación estilo inmobiliaria a partir de una toma de dron de cualquier propiedad (local comercial, casa, apartamento, lote, finca, terreno). Dibuja una ruta animada pegada a las calles desde un punto de referencia conocido hasta la propiedad y cierra con pin, etiqueta y tarjeta de marca; opcionalmente marca el lote en el suelo con sus medidas y su área. Úsala cuando Jaime pida "mostrar la ubicación", "dibujar el camino hasta…", "ruta como los videos de inmobiliarias", "marcar el lote con medidas" o un video de ubicación sobre una toma de dron, aunque no nombre la skill.
---

# Video de ubicación con ruta animada sobre una toma de dron

Convierte una toma de dron en el típico video inmobiliario de ubicación. Una franja de color «pintada» sobre las calles, con perspectiva real, avanza desde un punto que todo el mundo conoce (un parque, una bomba, una avenida) hasta la propiedad, donde aparecen un pin con haz de luz y la tarjeta con el nombre. Si la propiedad es un terreno, además se dibuja el contorno del lote en el suelo con cotas en metros y el área.

Tiempos con este kit, siguiendo el orden de abajo:
- **Unos 50 min** si basta el modo rápido.
- **1,5 h** si hace falta SfM, que corre en segundo plano mientras se hace lo demás.

Casos hechos (sirven de referencia, no de plantilla de marca):

| Caso | Propiedad | Qué se usó |
|---|---|---|
| Local comercial (26-09-2026) | un local en una calle de pueblo | ruta + pin + cierre; modo SfM con anclaje; `render_route.py` |
| Lote (29-09-2026) | un polideportivo | ruta + lote con cotas y área + punto de referencia; `dk_extend.py`, `dk_refmatch.py`, `render_ruta_lote.py` |

Detalle técnico y porqués: nota de Obsidian [[Ruta animada pegada al suelo en un video de dron]].

## El kit (`scripts/` de esta skill)

| Archivo | Para qué |
|---|---|
| `dk_common.py` | funciones compartidas |
| `dk_prep.py` | prepara el video: hoja de contactos y frames |
| `dk_sfm.py` | cámara 3D con COLMAP y control de calidad |
| `dk_plane.py` | plano del suelo en metros |
| `dk_track.py` | cámara por frame (modo rápido o anclado al SfM) con cadena de homografías |
| `dk_extend.py` | extiende una cámara ya calculada hacia atrás o hacia adelante (reusar el tracking de un video con otra ruta) |
| `dk_route.py` | anotar, construir y revisar la ruta |
| `dk_refmatch.py` | ubica en el video la captura que manda el cliente (SIFT: mejor frame + homografía) |
| `dk_gridcheck.py` | proyecta una cuadrícula del suelo en varios frames para validar la cámara |
| `render_route.py` | renderizador: ruta + pin + tarjeta + cierre |
| `render_ruta_lote.py` | renderizador para terrenos: lo mismo + lote con cotas y área + punto de referencia |
| `dk_finish.py` | une los tramos renderizados y verifica los frames |

- **Plantilla de diseño:** `assets/params_template.json`, con comentarios.
- **Fuentes:** `assets/fonts/`, 16 familias OFL (Poppins, Montserrat, Inter, Bebas Neue, Playfair Display, Oswald, Barlow Condensed…). Se eligen con `font_title` y `font_body` en `params.json`; `assets/fonts/README.md` trae las combinaciones por estilo (inmobiliaria premium, lujo, cinematográfico, técnico…). Se copian al KIT las que se usen.
- **Ejemplos de parámetros:** `references/ejemplos/`.

### Dónde corre
- **Claude Code (este PC, WSL):** corre todo en local. Hace falta python3 con numpy, opencv y Pillow, y ffmpeg con `prores_ks` y `libx264`. Para el SfM, `uv run --with pycolmap python dk_sfm.py …`. Los scripts van con `python3 <skill>/scripts/dk_*.py`.
- **claude.ai con el PC conectado:** el SfM y las previews corren en la nube (subir los `.py`, `.json`, `.ttf` y el video con `device_stage_files`). El render 1080p corre en el PC con `device_bash`, porque `device_commit_files` solo acepta archivos de hasta 20 MB, y en tramos de unos 120 frames por llamada (cada llamada muere a los 180 s). Si vuelves a subir un archivo, usa un nombre nuevo por revisión (`params_v3.json`): subir otro con la misma ruta dejó la versión anterior.

## 0. Preguntar todo de una vez (una sola AskUserQuestion)

1. **El archivo original del dron.** No sirve uno que pasó por WhatsApp: llega comprimido y a baja resolución (1024×576 en el primer caso), y es lo que más limita la calidad. Si es DJI, pedir también el `.SRT`.
2. **Tipo de propiedad y destino.** Local, casa, lote… Si es un lote, preguntar si se muestran las medidas y el área.
3. **Punto de partida.** Un lugar que cualquiera reconozca, con una captura con la ruta dibujada encima o una descripción («desde el parque, por la avenida…»). **Una sola ruta**: si dibuja dos, son propuestas.
4. **Punto de referencia** opcional: colegio, iglesia, bomba… Se etiqueta durante el vuelo.
5. **Formato.** 16:9, el recomendado. El renderizador conserva la proporción del video; para 9:16 se recorta después.
6. **Color y textos.** Color de la ruta (el claro se deriva), título, subtítulo y @ del cierre. Sin nombres de calles salvo que los pida.
7. **Video de referencia**, si tiene uno.

Si deja una «primera versión» hecha por otro agente, mírala antes para no repetir sus errores (ver «Qué NO hacer»).

## 1. Preparar

```
python3 dk_prep.py VIDEO WD --start S --end E
```

Crea `WD/contact.jpg` (una miniatura cada 5 s con el tiempo) y los frames en gris. Mira la hoja y elige el tramo útil: desde un poco antes de que se vea el punto de partida hasta que la propiedad está cerca. Descarta el despegue y lo que viene después de la llegada. Con 4K, escala el video a 1280 de ancho antes de preparar; el render sale igual a 1080p.

Si el cliente mandó capturas con la ruta dibujada, ubícalas en el video:

```
python3 dk_refmatch.py WD captura.jpg f0,f1,paso
```

Imprime el mejor frame y guarda la homografía, lo que permite pasar sus trazos a coordenadas del video.

## 2. Lanzar el SfM en segundo plano y seguir trabajando

```
nohup python3 dk_sfm.py WD all > WD/sfm.log 2>&1 &
```

Por defecto usa un keyframe cada 12 frames. Tiempos medidos con 2 CPU, video de 1024×576 y 65 s útiles:

| Paso | Tiempo |
|---|---|
| extract | 7 min |
| match | 14 min |
| map | 22 min (171 keyframes) |
| perframe | 6 min |
| qa | 1 min |

**No esperes sin hacer nada:** mientras corre, anota la ruta (paso 3) y prueba el modo rápido (paso 4). Mándale a Jaime un mensaje corto de avance.

Un clip corto (menos de 15 s) o con poco desplazamiento da un SfM degenerado aunque el error de reproyección sea bajo (probado: focal de 389 en vez de 651 y giros falsos de 10–20°). El QA lo detecta.

**Mismo video, otra propiedad:** si ya existe el tracking de ese video (`cams.npz`), no rehagas el SfM. Reúsalo y extiéndelo a los frames que falten:

```
python3 dk_extend.py WD --to 0
```

Encadena homografías del suelo; con `--route-m` y `--corridor` se limita al corredor de la ruta. No voltees el signo de N cuando `N[2,2] < 0`: el origen puede quedar detrás de la cámara.

## 3. Anotar la ruta (`route.json`, en píxeles)

- Se hace mientras corre el SfM. `python3 dk_route.py WD grid F x0 y0 x1 y1` saca un recorte ampliado con cuadrícula en coordenadas del video; funciona sin cámara.
- Anota el **centro de la calzada**, no el andén, con `grid` en 2–4 frames repartidos por calle, incluyendo frames lejanos y cercanos.
- El formato está en el docstring de `dk_route.py`:
  - tramos `line` para calles rectas (la esquina sale de la intersección);
  - tramos `poly` para curvas.
- Incluye `start`, `end` y `dest`. `dest` es la base de la puerta o el centro del lote, en el frame de la llegada.

## 4. Cámara por frame: modo rápido primero, SfM si hace falta

`route.json` guarda **píxeles**, así que sirve para los dos modos. Si cambias de modo, basta con volver a correr `dk_route.py build`.

### 4a. Modo rápido, sin SfM (unos 5 min)

Hace falta algo rectangular y plano de medida conocida: una cancha (microfútbol o baloncesto de unos 28×15 m), un parqueadero o un lote. Anota sus 4 esquinas en el frame donde se vea **más desde arriba**; con una vista rasante (10° de inclinación) la escala salió un 30 % corta, aunque la ruta quedó bien alineada.

```
python3 dk_track.py WD --anchor F --rect x1,y1,x2,y2,x3,y3,x4,y4 --rect-m 28,15 --to PRIMER,ULTIMO --passes 2
```

Comparado con el SfM, la ruta coincide en 1–7 px (a 1024 de ancho) en todo el video. La diferencia está en el **pin**, que se corrió hasta 30 px en una llegada a baja altura: ahí los edificios rompen el supuesto de suelo plano. Por eso, en modo rápido, **anota `dest` en el frame donde el pin se ve más tiempo** (la llegada) y revisa `check.jpg` con zoom en la llegada.

### 4b. Modo SfM (cuando termine el paso 2)

`WD/qa.json` compara el giro de COLMAP contra el de la matriz esencial cada 60 frames y trae `good_ranges`.

- **Todo bueno:** `python3 dk_track.py WD --sfm-range A,B` (A,B = rango completo).
- **Tramo malo al inicio:** es lo típico cuando el dron vuela alto y recto hacia un pueblo lejano; COLMAP «dobla» la trayectoria y da 16° de giro cada 2 s donde la matriz esencial da 0,2–2°. Ancla en el borde del tramo bueno y encadena homografías del corredor de la ruta:

  ```
  python3 dk_track.py WD --sfm-range INICIO_BUENO,FIN --to PRIMER_FRAME
  ```

  El anclaje debe caer dentro del tramo bueno y con margen (por ejemplo, bueno desde 1140 y anclado en 1260).
- **Tramo malo al final:** lo mismo con `--to ÚLTIMO_FRAME`.
- **Requisito:** el modo SfM necesita el plano (paso 5) antes de `dk_track`.

No gastes tiempo intentando arreglar el tramo malo de COLMAP: fijar intrínsecos (`--fix`), enmascarar el cielo y re-mapear no lo arreglaron.

**Cuál usar:** si en el modo rápido la ruta y el pin se ven clavados en los frames de `check` (inicio, giro, llegada, con zoom), entrega con ese y te ahorras la espera. Si el pin o la franja resbalan en la llegada, usa el modo SfM.

## 5. Plano del suelo en metros (solo modo SfM)

```
python3 dk_plane.py WD --frame F --poly x,y,... \
  --scale-frame F2 --scale-pts x1,y1,x2,y2 --scale-m M \
  --dest-frame F3 --dest x,y
```

- **`--poly`:** zona plana y despejada en un frame del tramo bueno (plaza, cancha, parqueadero). Evita techos.
- **Escala:** algo de medida conocida.
  - Cancha de microfútbol o baloncesto: 28 m de largo (una medida en sitio dio 27,5 m).
  - Calle de pueblo: 7–9 m de ancho.
  - Carro: 4,5 m.

  El largo total de la ruta sirve como control de cordura.
- **`--dest`:** base de la puerta o centro del lote, en un frame donde se vea claro. Ubícalo comparando con la captura del cliente (`dk_refmatch.py`).

Valida la cámara con `python3 dk_gridcheck.py WD f1,f2,… --step 50 --scene`: la cuadrícula tiene que quedar quieta sobre el suelo entre frames.

## 6. Construir y revisar la ruta

- `python3 dk_route.py WD build` imprime el residuo por frame. Menos de 3 m está bien; más de 5 m es una mala anotación o un tramo mal trackeado. También imprime el ángulo entre calles (en una cuadrícula de pueblo debe dar cerca de 90°).
- `python3 dk_route.py WD check f1,f2,…` genera una hoja con la línea proyectada. **Mírala siempre** en frames del inicio, medio, giro y llegada, y haz zoom (`grid`) en el giro y en la llegada.
- `python3 dk_route.py WD where F x,y …` convierte píxeles a metros para comprobar un punto.

### Si es un lote
Anota sus 4 esquinas en metros en `scene.npz` como `plaza` (orden NO, NE, SE, SO) y el punto de referencia como `colegio` (son los nombres de clave que usa `render_ruta_lote.py`).
- **Precisión:** mide el lote en dos frames distintos; las esquinas deben coincidir a 1–2 m.
- **Qué medir:** el dibujo del cliente suele abarcar calles y fachadas. Pregunta si las medidas son del predio o de lo dibujado.

## 7. Diseño y previews

Arma un KIT con estos archivos:
- el renderizador (`render_route.py` o `render_ruta_lote.py`);
- las dos fuentes elegidas de `assets/fonts/` (`font_title` y `font_body`; por defecto Poppins Bold y Medium). Elige el estilo según el tipo de propiedad con la tabla de `assets/fonts/README.md`;
- `cams.npz` y `scene.npz`;
- `params.json`, desde `assets/params_template.json` o un ejemplo de `references/ejemplos/`;
- el video, como `video.mp4`.

```
python3 render_route.py KIT OUT --src f1,f2,…
```

Saca previews JPG en 5 s. **Mándale un fotograma a Jaime temprano.**

Valores que funcionaron (todo en metros):

| Parámetro | Valor |
|---|---|
| `band_w` | 8 |
| `edge_w` | 0,8 |
| flechas cada | 16 m |
| `dot_r` | 2,6 |
| `ring_r` | 11 |
| `beam_h` | 26 |
| `hot_len` | 40 |

- **Ritmo:** `speed_keys` a 2x en el tramo lejano, 2,6x en el largo del medio y 1x al llegar. Por encima de 1,4x se mezclan frames. En lotes, que el dibujo del lote arranque unos 4 s después de que llega la ruta. Con 11 s de espera, se sintió lento.
- **Tiempo de dibujo:**
  - `render_route.py`: la ruta se dibuja en unos 11 s de video original (`draw_src`).
  - `render_ruta_lote.py`: usa `draw_keys`, pares [segundo del original, metros de ruta] con interpolación monótona.
- **Duración:** el video final queda en unos 30 s más 3 s de cierre.

Después, una versión completa en baja (`--scale 0.5 --range 0,99999`, unos 3 min). Comprímela con ffmpeg a CRF 27 y mándasela para que revise el movimiento.

## 8. Render 1080p

1. Renderiza por tramos de unos 120 frames (unos 2 min cada uno) y guárdalos en una carpeta de tramos:

   ```
   python3 render_route.py KIT CHUNKS --range a,b
   ```

   Al final, `--tail` para el cierre.
2. Une con `python3 dk_finish.py CHUNKS CARPETA_FINAL --name <Lugar>_ubicacion_final`, que verifica los frames. Si los tramos vienen de máquinas distintas, une con concat y reencode al fps del original (p. ej. 30000/1001).

No lances varios procesos de render en paralelo con DaVinci Resolve abierto: con 16 GB se quedó sin RAM.

## 9. DaVinci (MCP, opcional)

1. En una subcarpeta del pool, `import_media` de `plate.mp4`, `overlay.mov` y `endcard.mov`.
2. `create_timeline_from_clips` con el plate y dos `add_track` de video.
3. `append_to_timeline`:
   - overlay en `track_index` 2, con `record_frame` 0;
   - endcard en `track_index` 3, con `record_frame` = número de frames de salida (lo imprime el renderizador).
4. Nombra las pistas.
5. `prepare_render_job` con `format: "mp4"`, `codec: "H264"`, `require_temp_target: false` y `target_dir` en la carpeta final. Luego `start`.
6. Verifica con ffprobe que tenga stream de video y el número de frames.

El render de Resolve sale con la franja un poco más saturada: entrega como principal el `final.mp4` del renderizador.

## 10. Cierre

- Revisa una hoja de fotogramas del final, sobre todo que la ruta no resbale en giros ni en la llegada.
- Guarda el entregable en `D:\contenido\ubicacion <lugar> <día> <mes> <año>\` (regla de Jaime para todo contenido) y di la ruta en lenguaje simple.
- Deja la basura en `_to_delete/`.
- Vault de Obsidian: actualiza la nota técnica, `Reciente.md`, `Registro.md` e `Inicio.md`.
- Añade el video como ejemplo en el catálogo «Taller de skills» si es un caso nuevo (ver [[Skills propias (jjat-skills)]]).

## Qué NO hacer (aprendido)

- **Homografía de todo el cuadro encadenada:** mezcla techos con suelo y deriva hasta 50 px al acercarse.
- **Líneas de ancho fijo en píxeles y etiquetas de cv2:** se ven amateur. La franja va en metros con perspectiva y los textos con PIL y Poppins.
- **pycolmap 4.2:**
  - `IncrementalPipelineOptions.image_names` no sirve para mapear un subconjunto; `dk_sfm subset` copia la base de datos y borra lo demás.
  - El emparejamiento secuencial crea pares a distancia 1, 2, 4, 8… de imagen, así que `--key-step` debe ser 3×2^k (6, 12, 24).
  - Mapear todas las imágenes (681) no terminó en 40 min.
- **`solvePnPRansac` con `useExtrinsicGuess`:** si la pose inicial es mala, la devuelve casi igual. Para re-registrar, úsalo sin guess.
- **Signo de la profundidad:** comprueba `z > 0` al proyectar. Un signo invertido en la base del plano dibujó todo detrás de la cámara.
