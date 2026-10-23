---
name: explicador-rapido
description: Produce un explicador vertical (1080x1920, ~2:30) en español sobre un tema de software o ingeniería, narrado por una voz y sin nadie frente a la cámara, con el estilo visual jato.run (negro, paleta pastel, todo esquinado, Anton + Poppins + JetBrains Mono, red de partículas), voz de cualquier TTS (gratis con edge-tts, o ElevenLabs), subtítulos palabra a palabra y DATOS REALES calculados con modelos de verdad (YOLO, ResNet, embeddings, benchmarks, física con CoolProp) y, si hace falta, gráficos de ManimGX y tomas 3D de Blender, como los episodios «Visión por computadora» y «Bases de datos vectoriales». Úsala cuando el usuario pida "un explicador de <tema>", "otro video como el de computer vision", "como el de bases de datos vectoriales", "explícame <tema> en un reel", "<tema> explicado rápido", o el siguiente episodio de la serie, aunque no nombre la skill. Construye sobre HyperFrames (la versión actual, con su skill /hyperframes) y subagentes por escena; la skill trae su propio armado del video y de los subtítulos.
---

# Explicador rápido (estilo jato.run)

Reels que explican un tema técnico en ~2:30. La skill nació con dos episodios de la serie de jato.run (octubre de
2026): «Visión por computadora» (YOLOv8, ResNet-18/50, FaceNet, Sobel) y «Bases de datos vectoriales» (bge-m3, CLIP,
hnswlib). Después vinieron «Cuánto cuesta un token» y «La física del Tesla volador», el primero con gráficos de
ManimGX y tomas de Blender. Los dos cuadros de estilo aprobados del ep/02 vienen dentro de la skill, en
`references/cuadros-aprobados/`.
**Ejemplo completo en `references/ejemplo-ep02/`:** brief, guion, storyboard, hoja de capturas del video final, 7
escenas de tipos distintos (portada, tabla, fórmula, benchmark, grafo, flujo, tarjetas) y los scripts de datos reales.
Léelo antes de escribir el guion y vuelve a él al diseñar escenas. Si en la máquina hay proyectos de episodios
anteriores (p. ej. `videos/*-explicado`), también sirven: copia de ahí `tools/` y la estructura, **pero `alinear.py` y
`comun.py` cópialos siempre de `<SKILL>/scripts/`**: los de episodios viejos pueden traer bugs ya corregidos (el ep/06
salió sin voz desde la escena 3 por usar el `alinear.py` del ep/05).

`<SKILL>` es la carpeta de esta skill.

**Qué lo hace funcionar:** una idea por escena, cada revelación cae en la palabra que la motiva, y todas las cifras
salen de un modelo o benchmark corrido de verdad (lo ilustrativo se marca como tal en pantalla).

## Requisitos

- **[HyperFrames](https://hyperframes.heygen.com)**, la versión más reciente por `npx` (Node 20+), y su skill
  **`/hyperframes`** (`npx hyperframes skills`), que tiene el contrato de composición, el ciclo de trabajo y la guía de
  explainers y de video vertical: cárgala al empezar. Cada proyecto fija su versión en `package.json` al crearse.
  La skill trae lo que HyperFrames ya no hace por ti: `scripts/armar.py` escribe `index.html` y los subtítulos de la
  serie, y `scripts/paquetes.py` arma el encargo de cada subagente.
- **ffmpeg** con `rubberband` (para acelerar la voz sin cambiar el tono) y **Python 3** (para los scripts de la skill y
  los cálculos de datos reales en un venv del proyecto).
- **Un TTS** para la narración (ver § 4). Gratis: edge-tts con `scripts/voz_edge.py`. De pago: ElevenLabs u otro.
- **Opcional:** Codex CLI u otro generador de imágenes, para imágenes ilustrativas (ver § 3).
- **Opcional:** [ManimGX](https://manimgx.academa.ai/) para diagramas, fórmulas y curvas animadas, y **Blender** para
  tomas 3D de objetos reales (ver § 5 y `references/manim-y-blender.md`).

## Preferencias del usuario

Antes de empezar, mira si el usuario dejó preferencias (CLAUDE.md, memoria): carpeta de entrega, voz, TTS, marca.
Si no hay, pregunta solo lo que haga falta y usa estos valores por defecto:

| Qué | Por defecto |
|---|---|
| Carpeta del proyecto | `videos/<tema>-explicado` en el directorio de trabajo |
| Entrega | `entregas/<tema> <día> <mes> <año>` |
| Voz | Gratis: edge-tts `es-CO-SalomeNeural` a +8 %. Si hay clave de ElevenLabs: `4GeB1bS2GAHAsGRM0eeU` («juvenil latina»), `eleven_v4`, velocidad 1,08 |
| Estilo | `references/estilo-jato-run.md`. Si el usuario tiene marca propia, cambia paleta y fuentes y conserva la estructura |
| Música | Sin música, salvo que la pida |

## Puertas de aprobación (no te las saltes)

El usuario aprueba en este orden y nada avanza sin su sí:
1. **Guion** completo.
2. **Prueba de voz** de ~10 s con el guion real (antes de pagar la toma completa).
3. **Dos cuadros de estilo** (las escenas más representativas) antes de construir el resto.
4. **Preview** de todo el video antes del render final.

Toda generación de pago muestra su costo en USD antes y espera el OK. La toma completa del ep/02 costó US$0,33 en
ElevenLabs; con edge-tts no cuesta nada.

## 1. Proyecto

El flujo es brief → guion → voz → storyboard → cuadros de estilo → escenas → armado → revisión → render.

```bash
P=videos/<tema>-explicado
npx --yes hyperframes@latest init "$P" --non-interactive --example blank --resolution portrait
mkdir -p $P/{assets/fonts,assets/data,assets/media,assets/audio,tools,compositions/frames}
cp <SKILL>/assets/fonts/* $P/assets/fonts/
cp <SKILL>/references/estilo-jato-run.md $P/frame.md
```

`init` fija la versión de HyperFrames en los scripts de `package.json` (`npm run dev`, `check`, `render`); usa esos
scripts, o `npx hyperframes@<esa versión>`, durante todo el episodio. Al retomar un proyecto viejo, mira si hay una
versión nueva con `npx hyperframes@latest upgrade --project . --check`; si actualizas, corre `npm run check` antes de
seguir y di de qué versión a qué versión pasaste.

`BRIEF.md` como en el ep/02: `storyboard: yes`, `aspect: 1080x1920`,
`language: es`, `length: 150s`, `angle: concept`, `destination: reels-tiktok`, el `message` en una frase y la voz.

## 2. Guion

- Si hay video de referencia: transcríbelo (`npx hyperframes transcribe ref.mp4 --language es --json`, ver § 4) y arma
  una hoja de
  contacto (`ffmpeg -i ref.mp4 -vf "fps=1/2,scale=270:-1,tile=8x5" hoja.png`). **Cubre punto por punto todo lo que
  dice la referencia**: en el ep/01 hubo que reponer 6 detalles perdidos al condensar.
- Mira `references/ejemplo-ep02/SCRIPT.md` para el tono, el largo de cada línea y el arco.
- Arco que funcionó: gancho cotidiano → la pregunta → cómo se hacía antes / por qué falla → idea clave → el mecanismo
  paso a paso con datos reales → cómo se hace rápido o a escala → usos → herramientas → idea central → cierre.
- ~510 palabras para 2:30 tras acelerar. 24 a 28 escenas («Line»).
- **Duración máxima 2:55 si va a Instagram:** los reels de más de 3:00 no se muestran a público nuevo. Antes de pagar
  la voz, estima la duración final (palabras ÷ ~2,8 palabras/s de la toma × aceleración) y recorta el guion. El ep/04
  salió en 3:10 con 711 palabras a ×1,20 y hubo que rehacerlo quitando dos escenas enteras (mejor eso que acelerar más).
- `SCRIPT.md` con este formato exacto (lo lee `alinear.py`):

  ```markdown
  ## Line 1 — Portada
      [curious, engaging explainer] Bases de datos vectoriales, explicadas rápido.
  ```

- Español sin raya larga. Siglas que se narran letra a letra van separadas («I A»). Cifras escritas como se dicen si
  la voz las lee raro («mil veinticuatro»).

## 3. Datos reales

Antes de diseñar escenas, calcula con modelos de verdad cada número que vaya a salir en pantalla. Usa un venv propio
del proyecto (p. ej. `.cv-venv` con torch CPU) y scripts en `tools/` que escriban `assets/data/*.json`.

- Busca ejemplos que **muestren el contraste** que explica el video: «tenis para correr bajo la lluvia» da «tenis de
  mesa» por palabra y «zapatillas impermeables para trotar» (0,63) por significado; FaceNet da 0,73 para la misma
  persona y 1,28 para un extraño con umbral 1,1.
- Prueba varios modelos si el primero no separa bien (ver `references/trampas.md`).
- **Temas de ingeniería o física** (ep/04, un auto que flota con aire comprimido): no te quedes con el anuncio.
  Busca papers, artículos técnicos y lecturas de pantalla del evento, y calcula con bibliotecas de verdad (p. ej.
  CoolProp para gas real: 600 L con 250 kg de aire dan 454 bar con Z = 1,26, no lo que diría el gas ideal). Lo que sea
  estimación tuya (masa, áreas, coeficientes) se marca en pantalla y se lista en una escena de supuestos y en los
  créditos. Guarda las fuentes en `assets/data/fuentes.md`.
- Fotos y videos: Wikimedia Commons por categoría y Pexels, de licencia libre, mejor con escenas latinoamericanas.
  Créditos en `assets/media/CREDITOS.md` y el texto para la descripción del post en `creditos-descripcion.txt`.
- **Imágenes generadas (si hay Codex CLI o un generador de imágenes):** úsalo para lo ilustrativo que no existe con
  licencia libre: fotos de producto de un catálogo de ejemplo, portadas de álbum de una app simulada, pares
  «parecido» (perro/cachorro). Con imágenes el ep/02 quedó mejor que la versión solo con gráficos (2026-10-14).
  - Con Codex (herramienta integrada de imágenes, sin API key aparte; a 2026-10 usa gpt-image-2): un `codex exec`
    por lote con el prompt por stdin y una lista numerada de imágenes con su nombre de archivo; 3 corridas en
    paralelo hicieron 13 imágenes en ~6 min.

    ```bash
    echo "Genera estas imágenes con tu herramienta integrada y guárdalas en este directorio: 1) prod-botas.png …
    Cuadradas, fondo neutro, sin texto ni logotipos. No hagas nada más." | \
      codex exec --skip-git-repo-check --sandbox workspace-write -C assets/gen -
    ```

  - Para una variante que conserve identidad (el cachorro del mismo perro) pasa la primera como referencia con
    `-i perro.png` y describe los rasgos que cambian.
  - Pásalas a JPG de 640 px (`assets/gen/*.jpg`, todo el lote < 1 MB) y no dejes los PNG en el proyecto. En pantalla,
    recortes cuadrados sin `border-radius`, dentro de los paneles del estilo.
  - Si el generador es de pago (HF Studio, Higgsfield, una API), muestra el costo en USD y espera el OK.
  - Créditos en `assets/gen/CREDITOS.md`, aclarando que son ilustrativas y no fotos reales. Los **datos** siguen
    saliendo de modelos reales: la imagen ilustra, nunca reemplaza un número.

## 4. Voz

Cualquier TTS sirve mientras entregue un MP3: `alinear.py` trabaja sobre el audio y los tiempos por palabra, no sobre
el proveedor. Si el usuario tiene una voz preferida, úsala; si no, ofrece muestras y deja elegir.

- **Gratis, sin clave: edge-tts** (voces neuronales de Microsoft Edge) con `scripts/voz_edge.py`. Entrega el tiempo de
  cada palabra, así que **no hace falta transcribir** la toma. Voces que suenan bien: `es-CO-SalomeNeural` (por
  defecto), `es-MX-DaliaNeural`, `es-CO-GonzaloNeural`, `es-MX-JorgeNeural`.

  ```bash
  python3 -m venv .voz-venv && .voz-venv/bin/pip install edge-tts
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --root . --prueba 3   # 3 líneas, ~10 s: assets/audio/prueba-voz.mp3
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --root .              # narracion-completa.mp3 + transcript.json
  ```

- **ElevenLabs** (de pago, la voz de la serie), con `ELEVENLABS_API_KEY` propia. Cobra por carácter según el plan:
  estima el costo con el largo del guion y avísalo antes.

  ```bash
  curl -sS "https://api.elevenlabs.io/v1/text-to-speech/<voice_id>?output_format=mp3_44100_128" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
    -d '{"text": "<guion>", "model_id": "eleven_v4", "voice_settings": {"speed": 1.08}}' \
    -o assets/audio/narracion-completa.mp3
  ```

  Un TTS de pago no da los tiempos por palabra: hay que transcribir la toma (paso de abajo). Las etiquetas de tono del
  guion (`[curious, engaging explainer]`) son de ElevenLabs v3/v4; los demás TTS las ignoran o las leen, y
  `voz_edge.py` ya las quita.
- **Otros:** el TTS de OpenAI, Kokoro (`npx hyperframes tts`, voces en español `ef_dora` y `em_alex`) o Piper. Si no
  dan tiempos por palabra, transcribe.

Pasos:

- Prueba de ~10 s con líneas reales del guion → aprobación → **una sola toma** del guion completo.
- Mide la toma. Si pasa de ~2:35, acelera con rubberband (tono y formantes intactos) en vez de rehacerla:

  ```bash
  ffmpeg -i assets/audio/narracion-completa.mp3 -af "rubberband=tempo=1.13:formant=preserved" assets/audio/narracion-completa-x1.13.mp3
  ```

- **Solo si el TTS no dio tiempos por palabra**, transcribe la toma ORIGINAL. Con Parakeet instalado, HyperFrames lo
  usa solo (es más preciso y rápido que Whisper y cubre el español); sin él, pasa `--model large-v3`: los modelos
  chicos de Whisper separan mal las palabras en español (y `small.en`, el de por defecto, traduce al inglés).

  ```bash
  npx hyperframes models install parakeet          # una vez
  npx hyperframes transcribe assets/audio/narracion-completa.mp3 --language es --json
  ```

  Escribe `assets/transcript.json`: pásaselo a `alinear.py` con `--tx assets/transcript.json` (con edge-tts, el archivo
  es `assets/audio/transcript.json`).

- Corta por escena con los tiempos (`--tx assets/audio/transcript.json` si vienen de edge-tts,
  `--tx assets/transcript.json` si vienen de `transcribe`):

  ```bash
  python3 <SKILL>/scripts/alinear.py --root . --tx assets/audio/transcript.json \
      --audio assets/audio/narracion-completa-x1.13.mp3 --tempo 1.13
  ```

  Escribe `assets/voice/NN.mp3` y `audio_meta.json` (lo que lee `armar.py`). Las
  palabras de los subtítulos salen del guion; los huecos (números, siglas) se interpolan. Sin aceleración, `--tempo 1`
  y `--audio` apunta a la toma original.

## 5. Storyboard y cuadros de estilo

- `STORYBOARD.md` con un bloque `## Frame N — Título` por escena (formato del ejemplo) que lleva `- src:
  compositions/frames/<id>.html`, `- transition_in: crossfade` (o `cut`) y `- words: palabra@seg` (relativo al inicio
  de la escena, sale de `audio_meta.json`) para que cada revelación caiga en su palabra. **El id de cada escena
  empieza con letra** (`e01-gancho`, no `01-gancho`): el id es también un selector CSS y uno que empieza con número
  no es válido. Escribe las escenas con su `scene` y `voiceover`, y deja que
  `python3 <SKILL>/scripts/palabras.py --root .` llene `duration` y `words` de cada una desde `audio_meta.json` (se puede
  repetir si cambia la voz). Define la continuidad (qué elemento reaparece
  igual en varias escenas) y los colores por rol. Modelo: `references/ejemplo-ep02/STORYBOARD.md`.
- Sistema visual en `references/estilo-jato-run.md`. Lo no negociable: cero `border-radius` (salvo las partículas),
  HUD con la izquierda vacía, nada debajo de y=1440, un solo degradado cian→violeta por escena.
- Construye primero **dos cuadros de estilo** a mano, partiendo de los aprobados del ep/02
  (`references/cuadros-aprobados/e09-cerca.html` y `e13-resultado.html`). `scripts/comun.py` tiene las piezas (fuentes,
  fondo, red de partículas, esquinas de mira, HUD, plantilla) si prefieres generarlos con Python.
- Enséñaselos al usuario en Studio (`npm run dev`) y espera su aprobación.
- **Gráficos de ManimGX y tomas de Blender** (opcional): para diagramas de fuerzas, fórmulas que se transforman,
  curvas que se dibujan o un objeto real en 3D. Se renderizan como MP4 sin texto de lectura y entran a la escena como
  `<video>` con `mix-blend-mode: lighten`. Todo en `references/manim-y-blender.md`, con las utilidades en
  `scripts/manim/` (estilo, `Reloj` que sincroniza con las palabras, silueta de auto) y `scripts/blender/` (render,
  auto 3D, codificación). Los objetos reales se dibujan con su forma real: un auto con carrocería suave y llantas
  redondas, nunca cajas.

## 6. El resto de escenas con subagentes

- Arma un paquete por escena:

  ```bash
  python3 <SKILL>/scripts/paquetes.py --root . --refs compositions/frames/<cuadro-a>.html compositions/frames/<cuadro-b>.html
  ```

  Los deja en `.hyperframes/paquetes/<id>.md` y copia `references/reglas-escena.md` a `.hyperframes/paquetes/_reglas.md`:
  rellena ahí lo que va entre `<…>` antes de lanzar a nadie. Cada subagente recibe su paquete, las reglas y la orden de
  cargar `/hyperframes` (el contrato de composición). Los dos cuadros aprobados son el esqueleto obligatorio; si la
  escena es de un tipo que tiene modelo en `references/ejemplo-ep02/frames/` (tabla, benchmark, grafo, flujo,
  tarjetas), pásale también ese.
- **Máximo 20 subagentes a la vez**; el exceso falla sin reintentarse. Lanza en tandas y lleva la cuenta.
- **Un solo script de timeline por escena** (el `<script>` que carga GSAP no cuenta). Un bloque sobrante copiado de otra escena dejó 7 escenas en negro en
  el ep/04 sin que lint ni check dijeran nada (ver `references/trampas.md`).

## 7. Cierre

1. Arma el video con un solo comando, que puedes repetir cada vez que cambies una escena:

   ```bash
   python3 <SKILL>/scripts/armar.py --root .
   ```

   Escribe `index.html` (cada escena en su host, con el mismo id que su `data-composition-id` y que la clave de su
   timeline; la voz de cada escena; el fundido cruzado de 0,5 s, o corte si la escena pide `transition_in: cut`) y
   `compositions/captions.html` (los subtítulos de la serie: grupos de 2 a 3 palabras, tenue lo que viene, cian lo que
   suena, en la banda 1445–1615), y corre el lint con la versión del proyecto. Si el proyecto tiene
   `tools/despues_de_armar.py`, lo corre antes del lint: ahí van capas propias, como un botón SEGUIR encima del video.

   También aplica la **zona segura del feed de Instagram**: sin abrir el reel, el feed lo recorta a 4:5 por el centro
   (solo se ve y≈285–1635) y se pierde la parte alta. Por eso escenas y subtítulos se reducen y bajan
   (`translate(0px, 184px) scale(0.865)`) sobre un degradado de fondo: el contenido (y=140–1440 en cada escena) cae en
   ~305–1430 y los subtítulos debajo; en pantalla completa se sigue viendo bien. `--sin-zona-segura` lo quita (p. ej.
   para TikTok o YouTube Shorts).
2. `npm run check` (o `npx hyperframes check --json`): corrige cada error y pesa cada aviso. La zona segura reduce
   todo a 0,865, así que el texto de lectura va de **33 px para arriba en el diseño** (28 en el video). Los avisos
   `text_below_floor` del HUD y los metadatos (22 px) son el estilo de la serie y se esperan; si salen en un texto de
   lectura, súbelo. También se esperan avisos informativos de desborde de la red de partículas y de solape del HUD
   durante el fundido entre escenas.
3. Revisión visual: `npx hyperframes snapshot --review` y su hoja de capturas. Busca textos encimados (fichas sobre
   ejes, cifras sobre rótulos), escenas vacías o en negro y subtítulos fuera de la banda: el usuario los ve antes que
   nada.
4. Preview en Studio (`npm run dev`) → aprobación del usuario → `npm run render`.
5. Entrega en la carpeta de entrega (ver «Preferencias del usuario»): el MP4 (H.264), `creditos-descripcion.txt` y
   el caption (en Instagram, **máximo 5 hashtags**).

## Episodios cortos

Para una prueba, un teaser o un anuncio de 20 a 60 s: el mismo flujo con 3 a 8 escenas (≈2,8 palabras por segundo de
voz, antes de acelerar). Las puertas de aprobación siguen igual, pero basta un cuadro de estilo si son pocas escenas,
y la prueba de voz es `--prueba 1` (con tan pocas líneas, tres ya son la toma entera).
Los datos reales siguen siendo obligatorios en lo que salga en pantalla; si no hay cifras, mejor una escena de
concepto que un número inventado.

Antes de construir, lee `references/trampas.md`: HDR, subagentes, contraste, símbolos en Anton, la banda de
subtítulos y los clips de Manim y Blender ya costaron horas.
