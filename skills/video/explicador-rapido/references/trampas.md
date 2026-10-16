# Trampas conocidas

Salieron en el ep/01 (visión por computadora), el ep/02 (bases de datos vectoriales), el ep/03 (costo de un token) y el
ep/04 (física del Tesla volador), octubre de 2026.

## Subagentes
- **Máximo 20 simultáneos.** Las llamadas que lo superan fallan sin reintentarse. Lanza en tandas (el ep/02 usó dos)
  y lleva la cuenta de qué escenas quedaron sin lanzar.
- **Ids que empiezan con número** (`#19-deteccion-box`) rompen `querySelector` y GSAP. Prefijo `f<frame_id>-`.
- **Entradas tardías con `immediateRender:false` y sin estado inicial** (ep/03, 2026-10-15): si el PRIMER tween de un
  elemento es un `fromTo` de opacidad 0→1 con `immediateRender:false`, el elemento se ve desde el inicio de la escena
  hasta su entrada. El lint y el check no lo detectan; se vio en el render (fichas «Bog/ot/á» antes de nombrarlas). En 6
  de 23 escenas pasó. Arreglo: `tl.set("<selectores>", { opacity: 0 }, 0)` al inicio, o `opacity:0` en el CSS. Revisa
  todas las escenas con un script antes de renderizar.
- **Rutas de recursos** en las subcomposiciones: relativas a la raíz del proyecto (`assets/...`), no al archivo.

## Subtítulos
- `captions.mjs` pone la banda en 1600-1920 en vertical, dentro de la interfaz de Reels y TikTok. Después de **cada**
  regeneración reescribe en `compositions/captions.html`: `--cap-band-top: 1460px; --cap-band-height: 240px;`.
- Las palabras de los subtítulos salen del guion (ortografía exacta), no de la transcripción: eso hace `alinear.py`.

## Voz
- La toma completa de ElevenLabs v4 sale más lenta que la prueba corta (2,8 frente a 3,0 palabras/s). Mide la
  duración y acelera con rubberband en vez de pagar otra toma:
  `ffmpeg -i toma.mp3 -af "rubberband=tempo=1.13:formant=preserved" toma-x1.13.mp3`
  (el ep/01 usó x1,17 y el ep/02 x1,133). Pasa el mismo valor a `alinear.py --tempo`.
- Whisper `large-v3` en CPU tarda ~15 min por 3 min de audio si compite con otro proceso pesado: no lo lances junto
  al cálculo de datos.

## Datos reales
- En CPU: YOLOv8x a 1280 sobre 660 cuadros es inviable; YOLOv8m a 960 sí funciona.
- Elegir el modelo de embeddings con un caso que separe significado de palabra. En el ep/02 MiniLM y mpnet
  multilingües ponían «tenis de mesa» primero, e5-base comprimía todo entre 0,77 y 0,83, y solo `BAAI/bge-m3`
  ordenó por significado (perro-cachorro 0,81 frente a perro-factura 0,44).
- El render no tiene red: los valores van escritos en el HTML, nunca con `fetch`.

## Render
- **Un solo clip HDR** (HLG/BT.2020, típico de Pexels grabado en iPhone) activa el modo «HDR layered composite»:
  108 min en vez de 9 y se filtran estados de otras escenas. Revisa `color_transfer` con ffprobe y pasa todo a
  BT.709 antes:
  `-vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p"`. En el log aparece
  `"hasHdrContent":true`.
- Un objeto que aparece poco tiempo en un video: `data-playback-rate="0.5"` (cámara lenta compatible con el render).
- `#666` como color de texto falla el chequeo de contraste: usa `#8f8f8a`.
- Anton no trae ≈ ≠ → ↔ ✓ −: esos símbolos en JetBrains Mono o Poppins.
- Las JetBrains Mono de `assets/fonts/` son la fuente completa (≈ μ → ∫ Δ ₀ incluidos) desde el ep/04. Si copias
  fuentes de un proyecto viejo, revisa el peso: las de 21 KB eran un subconjunto de 229 glifos sin esos símbolos.

- **Feed de Instagram:** la vista previa del feed recorta el reel a 4:5 (y≈285–1635). Si el contenido empieza en y=140 y los subtítulos van en 1460–1700, en el feed se pierde el kicker y sobra espacio abajo. Arreglo en el índice: escala 0.865 + translateY 184 a `.scene` (ver SKILL.md § 7).

## Clips de ManimGX y Blender (ep/04)
- **Escenas en negro sin error visible:** una escena tenía un **segundo `<script>`** copiado de otra. Re-registraba su
  timeline y su `onUpdate` hacía `textContent` sobre un id inexistente; la excepción en el seek cortaba la
  actualización de las escenas siguientes y 7 salían vacías (también en el render). Lint y check no lo ven y `check`
  se colgaba por tiempo. Se encontró con puppeteer: `window.__player.seek(t)` en el iframe `/preview` y la consola.
  Revisa con un script que cada `getElementById("…")` de los frames apunte a un id que existe.
- **Rectángulo oscuro alrededor del clip:** el `transform` de la zona segura del feed crea un contexto de
  apilamiento; el `lighten` del `<video>` solo se mezcla dentro de la escena. Arreglo: `.scene { mix-blend-mode:
  lighten; }` en `index.html`.
- **Fichas HTML encima de los ejes de Manim:** el detector de solapes mira cajas de texto, no los píxeles del video.
  Reserva franjas fijas: Manim de y = −2,25 u hacia arriba (≈ 1264 px), fichas HTML en 1290–1440 px.
- **MP4 de ManimGX con cuadros variables** y ~0,05 s de más: recodifica con
  `-vf "fps=30,tpad=stop_mode=clone:stop_duration=2" -t <duration_s>`.
- **Dos codificaciones al mismo archivo** (una en segundo plano y otra a mano) dejan un MP4 corrupto que rompe la
  escena en el render. Una sola codificación por archivo; verifica con `ffprobe` antes de montar.
- El detector de solapes por cajas da falsos positivos con Anton (la caja de línea es más alta que las letras):
  confirma cada choque con una captura.
- En el DOM del runtime, `data-duration` de las escenas montadas aparece como `data-hf-authored-duration`.
