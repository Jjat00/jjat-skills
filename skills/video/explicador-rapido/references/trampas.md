# Trampas conocidas

Salieron en el ep/01 (visión por computadora) y el ep/02 (bases de datos vectoriales), octubre de 2026.

## Subagentes
- **Máximo 20 simultáneos.** Las llamadas que lo superan fallan sin reintentarse. Lanza en tandas (el ep/02 usó dos)
  y lleva la cuenta de qué escenas quedaron sin lanzar.
- **Ids que empiezan con número** (`#19-deteccion-box`) rompen `querySelector` y GSAP. Prefijo `f<frame_id>-`.
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

- **Feed de Instagram:** la vista previa del feed recorta el reel a 4:5 (y≈285–1635). Si el contenido empieza en y=140 y los subtítulos van en 1460–1700, en el feed se pierde el kicker y sobra espacio abajo. Arreglo en el índice: escala 0.865 + translateY 184 a `.scene` (ver SKILL.md § 7).
