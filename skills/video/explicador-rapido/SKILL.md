---
name: explicador-rapido
description: Produce un explicador vertical (1080x1920, ~2:30) en español sobre un tema de software o ingeniería, narrado por una voz y sin nadie frente a la cámara, con el estilo visual jato.run (negro, paleta pastel, todo esquinado, Anton + Poppins + JetBrains Mono, red de partículas), voz de cualquier TTS (gratis con edge-tts, o ElevenLabs), subtítulos palabra a palabra y DATOS REALES calculados con modelos de verdad (YOLO, ResNet, embeddings, benchmarks, física con CoolProp) y, si hace falta, gráficos de ManimGX y tomas 3D de Blender, como los episodios «Visión por computadora» y «Bases de datos vectoriales». Úsala cuando el usuario pida "un explicador de <tema>", "otro video como el de computer vision", "como el de bases de datos vectoriales", "explícame <tema> en un reel", "<tema> explicado rápido", o el siguiente episodio de la serie, aunque no nombre la skill. Construye sobre HyperFrames, con los scripts de ensamblado incluidos en la skill, y subagentes por escena.
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

- **[HyperFrames](https://hyperframes.heygen.com)** por `npx`, fijado en `hyperframes@0.8.186` (Node 20+). La skill
  trae en `scripts/hf/` los cuatro scripts de ensamblado del antiguo flujo `faceless-explainer`, que HyperFrames
  retiró en octubre de 2026 (licencia Apache 2.0, ver `scripts/hf/NOTICE.md`): no hace falta instalar ese flujo.
  Si tienes la skill `/hyperframes`, cárgala para las reglas de composición; no es obligatoria.
- **ffmpeg** con `rubberband` (para acelerar la voz sin cambiar el tono) y **Python 3** (para `scripts/alinear.py`,
  `scripts/voz_edge.py` y los cálculos de datos reales en un venv del proyecto).
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

El flujo es brief → guion → voz → storyboard → cuadros de estilo → paquetes por escena → ensamblado. Todo lo que
necesita viene en la skill; los comandos de HyperFrames van con la versión fijada:

```bash
P=videos/<tema>-explicado
npx --yes hyperframes@0.8.186 init "$P" --non-interactive --example=blank --resolution=portrait
mkdir -p $P/{assets/fonts,assets/data,assets/media,assets/audio,tools,compositions/frames,.hyperframes}
cp <SKILL>/assets/fonts/* $P/assets/fonts/
cp <SKILL>/references/estilo-jato-run.md $P/frame.md
cp <SKILL>/assets/caption-skin.html $P/.hyperframes/caption-skin.html
```

Si el `package.json` del proyecto trae otra versión de `hyperframes` en sus scripts (`dev`, `check`, `render`),
cámbiala por `0.8.186` para que todo use la misma.

`BRIEF.md` como en el ep/02: `workflow: faceless-explainer`, `flow: automation`, `storyboard: yes`, `aspect: 1080x1920`,
`language: es`, `length: 150s`, `angle: concept`, `destination: reels-tiktok`, el `message` en una frase y la voz.

## 2. Guion

- Si hay video de referencia: transcríbelo (`npx --yes hyperframes@0.8.186 transcribe ref.mp4 -m large-v3 -l es`; la
  primera vez baja el modelo de Whisper, ~3 GB) y arma una hoja de
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
  .voz-venv/bin/python <SKILL>/scripts/voz_edge.py --root . --prueba 3   # ~10 s: assets/audio/prueba-voz.mp3
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
- **Otros:** el TTS de OpenAI, Kokoro (`npx --yes hyperframes@0.8.186 tts`) o Piper. Si no dan tiempos por palabra, transcribe.

Pasos:

- Prueba de ~10 s con líneas reales del guion → aprobación → **una sola toma** del guion completo.
- Mide la toma. Si pasa de ~2:35, acelera con rubberband (tono y formantes intactos) en vez de rehacerla:

  ```bash
  ffmpeg -i assets/audio/narracion-completa.mp3 -af "rubberband=tempo=1.13:formant=preserved" assets/audio/narracion-completa-x1.13.mp3
  ```

- **Solo si el TTS no dio tiempos por palabra**, transcribe la toma ORIGINAL. En español solo `large-v3` separa bien
  las palabras (baja ~3 GB la primera vez y tarda varios minutos en CPU):

  ```bash
  npx --yes hyperframes@0.8.186 transcribe assets/audio/narracion-completa.mp3 -m large-v3 -l es
  ```

- Corta por escena con los tiempos (de edge-tts o de la transcripción):

  ```bash
  python3 <SKILL>/scripts/alinear.py --root . --tx assets/audio/transcript.json \
      --audio assets/audio/narracion-completa-x1.13.mp3 --tempo 1.13
  ```

  Escribe `assets/voice/NN.mp3` y `audio_meta.json` (el formato que leen `captions.mjs` y `assemble-index.mjs`). Las
  palabras de los subtítulos salen del guion; los huecos (números, siglas) se interpolan. Sin aceleración, `--tempo 1`
  y `--audio` apunta a la toma original.

## 5. Storyboard y cuadros de estilo

- `STORYBOARD.md` con un bloque por escena y `words: palabra@seg` (relativo al inicio de la escena, sale de
  `audio_meta.json`) para que cada revelación caiga en su palabra. Define la continuidad (qué elemento reaparece
  igual en varias escenas) y los colores por rol. Modelo: `references/ejemplo-ep02/STORYBOARD.md`.
- Sistema visual en `references/estilo-jato-run.md`. Lo no negociable: cero `border-radius` (salvo las partículas),
  HUD con la izquierda vacía, nada debajo de y=1440, un solo degradado cian→violeta por escena.
- Construye primero **dos cuadros de estilo** a mano, partiendo de los aprobados del ep/02
  (`references/cuadros-aprobados/09-cerca.html` y `13-resultado.html`). `scripts/comun.py` tiene las piezas (fuentes,
  fondo, red de partículas, esquinas de mira, HUD, plantilla) si prefieres generarlos con Python.
- Enséñaselos al usuario en Studio (`npx --yes hyperframes@0.8.186 preview --background`) y espera su aprobación.
- **Gráficos de ManimGX y tomas de Blender** (opcional): para diagramas de fuerzas, fórmulas que se transforman,
  curvas que se dibujan o un objeto real en 3D. Se renderizan como MP4 sin texto de lectura y entran a la escena como
  `<video>` con `mix-blend-mode: lighten`. Todo en `references/manim-y-blender.md`, con las utilidades en
  `scripts/manim/` (estilo, `Reloj` que sincroniza con las palabras, silueta de auto) y `scripts/blender/` (render,
  auto 3D, codificación). Los objetos reales se dibujan con su forma real: un auto con carrocería suave y llantas
  redondas, nunca cajas.

## 6. El resto de escenas con subagentes

- Arma un paquete por escena: `node <SKILL>/scripts/hf/frame-packets.mjs --project .` (los deja en
  `.hyperframes/frame-packets/`, con el rol de los subagentes en `_role.md`).
- Copia `references/reglas-escena.md` a `.hyperframes/frame-packets/_reglas.md`, rellena lo que va entre `<…>` y pásalo
  a cada subagente con su paquete. Los dos cuadros aprobados son el esqueleto obligatorio; si la escena es de un tipo
  que tiene modelo en `references/ejemplo-ep02/frames/` (tabla, benchmark, grafo, flujo, tarjetas), pásale también ese.
- **Máximo 20 subagentes a la vez**; el exceso falla sin reintentarse. Lanza en tandas y lleva la cuenta.
- **Un solo `<script>` de timeline por escena.** Un bloque sobrante copiado de otra escena dejó 7 escenas en negro en
  el ep/04 sin que lint ni check dijeran nada (ver `references/trampas.md`).

## 7. Cierre

1. Ensambla con un solo comando, que puedes repetir cada vez que cambies una escena:

   ```bash
   bash <SKILL>/scripts/ensamblar.sh .
   ```

   Hace, en orden: subtítulos (`captions.mjs`, con la piel de `.hyperframes/caption-skin.html`), `index.html` con todas
   las escenas (`assemble-index.mjs`), transiciones (`transitions.mjs inject` y `verify`), la banda de subtítulos en
   1445/170, la **zona segura del feed de Instagram**, la marca de pista de subtítulos que pide el lint y, al final,
   `hyperframes lint`. Si el proyecto tiene `tools/despues_de_ensamblar.py`, lo corre antes del lint: ahí van capas
   propias, como un botón SEGUIR encima del video.

   La zona segura existe porque, sin abrir el reel, el feed lo recorta a 4:5 por el centro (solo se ve y≈285–1635) y
   se pierde la parte alta. Por eso cada escena se reduce y baja
   (`.scene { transform: translate(0px, 184px) scale(0.865); }`), sin fondo propio, sobre un degradado en `#root`.
   El contenido (y=140–1440 en cada escena) cae en ~305–1430 y los subtítulos debajo; en pantalla completa se sigue
   viendo bien.
2. `npm run check` sin errores.
3. Hoja de capturas a mitad de cada escena para revisar todo de un vistazo. Busca textos encimados (fichas sobre
   ejes, cifras sobre rótulos) y escenas vacías: el usuario los ve antes que nada.
4. Preview en Studio → aprobación del usuario → `npm run render`.
5. Entrega en la carpeta de entrega (ver «Preferencias del usuario»): el MP4 (H.264), `creditos-descripcion.txt` y
   el caption (en Instagram, **máximo 5 hashtags**).

## Episodios cortos

Para una prueba, un teaser o un anuncio de 20 a 60 s: el mismo flujo con 3 a 8 escenas (≈2,8 palabras por segundo de
voz, antes de acelerar). Las puertas de aprobación siguen igual, pero basta un cuadro de estilo si son pocas escenas.
Los datos reales siguen siendo obligatorios en lo que salga en pantalla; si no hay cifras, mejor una escena de
concepto que un número inventado.

Antes de construir, lee `references/trampas.md`: HDR, subagentes, contraste, símbolos en Anton, la banda de
subtítulos y los clips de Manim y Blender ya costaron horas.
