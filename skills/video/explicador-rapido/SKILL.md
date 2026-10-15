---
name: explicador-rapido
description: Produce un explicador vertical (1080x1920, ~2:30) en español sobre un tema de software o ingeniería, narrado por una voz y sin nadie frente a la cámara, con el estilo visual jato.run (negro, paleta pastel, todo esquinado, Anton + Poppins + JetBrains Mono, red de partículas), voz de ElevenLabs (vía HF Studio, la API directa u otro TTS), subtítulos palabra a palabra y DATOS REALES calculados con modelos de verdad (YOLO, ResNet, embeddings, benchmarks), como los episodios «Visión por computadora» y «Bases de datos vectoriales». Úsala cuando el usuario pida "un explicador de <tema>", "otro video como el de computer vision", "como el de bases de datos vectoriales", "explícame <tema> en un reel", "<tema> explicado rápido", el siguiente episodio de la serie, o un video estilo @rick.theengineer, aunque no nombre la skill. Construye sobre HyperFrames (flujo faceless-explainer) con subagentes por escena.
---

# Explicador rápido (estilo jato.run)

Reels que explican un tema técnico en ~2:30. La skill nació con dos episodios de la serie de jato.run (octubre de
2026): «Visión por computadora» (YOLOv8, ResNet-18/50, FaceNet, Sobel) y «Bases de datos vectoriales» (bge-m3, CLIP,
hnswlib). Los dos cuadros de estilo aprobados del ep/02 vienen dentro de la skill, en `references/cuadros-aprobados/`.
Si en la máquina existen proyectos de episodios anteriores (p. ej. `videos/*-explicado`), son la mejor referencia:
copia de ahí `tools/` y la estructura.

`<SKILL>` es la carpeta de esta skill.

**Qué lo hace funcionar:** una idea por escena, cada revelación cae en la palabra que la motiva, y todas las cifras
salen de un modelo o benchmark corrido de verdad (lo ilustrativo se marca como tal en pantalla).

## Requisitos

- **HyperFrames** con su flujo `faceless-explainer` (skills `/hyperframes` y `/faceless-explainer`;
  [hyperframes.heygen.com](https://hyperframes.heygen.com)). Node 20+ y `npx hyperframes`.
- **ffmpeg** con `rubberband` (para acelerar la voz sin cambiar el tono) y **Python 3** (para `scripts/alinear.py` y
  los cálculos de datos reales en un venv del proyecto).
- **Un TTS** para la narración (ver § 4). Sugerido: HF Studio; también sirve ElevenLabs directo u otro.
- **Opcional:** Codex CLI u otro generador de imágenes, para imágenes ilustrativas (ver § 3).

## Preferencias del usuario

Antes de empezar, mira si el usuario dejó preferencias (CLAUDE.md, memoria): carpeta de entrega, voz, TTS, marca.
Si no hay, pregunta solo lo que haga falta y usa estos valores por defecto:

| Qué | Por defecto |
|---|---|
| Carpeta del proyecto | `videos/<tema>-explicado` en el directorio de trabajo |
| Entrega | `entregas/<tema> <día> <mes> <año>` (el autor original usa `D:\contenido\<tema> 11 oct 2026`) |
| Voz | ElevenLabs `4GeB1bS2GAHAsGRM0eeU` («juvenil latina»), `eleven_v4`, velocidad 1,08 |
| Estilo | `references/estilo-jato-run.md`. Si el usuario tiene marca propia, cambia paleta y fuentes y conserva la estructura |
| Música | Sin música, salvo que la pida |

## Puertas de aprobación (no te las saltes)

El usuario aprueba en este orden y nada avanza sin su sí:
1. **Guion** completo.
2. **Prueba de voz** de ~10 s con el guion real (antes de pagar la toma completa).
3. **Dos cuadros de estilo** (las escenas más representativas) antes de construir el resto.
4. **Preview** de todo el video antes del render final.

Toda generación de pago muestra su costo en USD antes y espera el OK. La toma completa del ep/02 costó US$0,33.

## 1. Proyecto

Carga `/hyperframes` y entra por `/faceless-explainer` (es su flujo: brief → guion → storyboard → paquetes por escena
→ ensamblado). Luego:

```bash
npx hyperframes init "videos/<tema>-explicado" --non-interactive --example=blank --resolution=portrait --skill=faceless-explainer
mkdir -p videos/<tema>-explicado/{assets/fonts,assets/data,assets/media,assets/audio,tools}
cp <SKILL>/assets/fonts/* videos/<tema>-explicado/assets/fonts/
cp <SKILL>/references/estilo-jato-run.md videos/<tema>-explicado/frame.md
```

`BRIEF.md` como en el ep/02: `workflow: faceless-explainer`, `flow: automation`, `storyboard: yes`, `aspect: 1080x1920`,
`language: es`, `length: 150s`, `angle: concept`, `destination: reels-tiktok`, el `message` en una frase y la voz.

## 2. Guion

- Si hay video de referencia: transcríbelo (`npx hyperframes transcribe ref.mp4 -m large-v3 -l es`) y arma una hoja de
  contacto (`ffmpeg -i ref.mp4 -vf "fps=1/2,scale=270:-1,tile=8x5" hoja.png`). **Cubre punto por punto todo lo que
  dice la referencia**: en el ep/01 hubo que reponer 6 detalles perdidos al condensar.
- Arco que funcionó: gancho cotidiano → la pregunta → cómo se hacía antes / por qué falla → idea clave → el mecanismo
  paso a paso con datos reales → cómo se hace rápido o a escala → usos → herramientas → idea central → cierre.
- ~510 palabras para 2:30 tras acelerar. 24 a 28 escenas («Line»).
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

Voz por defecto: ElevenLabs `4GeB1bS2GAHAsGRM0eeU` («juvenil latina»), `eleven_v4`, velocidad 1,08. Si el usuario
tiene otra voz o el tema pide otra, ofrece muestras y deja elegir. Cualquier TTS sirve mientras entregue un MP3:
`alinear.py` trabaja sobre el audio, no sobre el proveedor.

- **Sugerido: HF Studio** (MCP `hf-studio`, `text_to_speech`). Sin `quote_id` cotiza; con el `quote_id`, tras el OK,
  genera. Guarda la generación en la sonoteca.
- **ElevenLabs directo**, con `ELEVENLABS_API_KEY` propia. Cobra por carácter según el plan; estima el costo con el
  largo del guion y avísalo antes:

  ```bash
  curl -sS "https://api.elevenlabs.io/v1/text-to-speech/<voice_id>?output_format=mp3_44100_128" \
    -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
    -d '{"text": "<guion>", "model_id": "eleven_v4", "voice_settings": {"speed": 1.08}}' \
    -o assets/audio/narracion-completa.mp3
  ```

- **Otras:** el TTS de OpenAI o uno local y gratis (Kokoro, Piper, edge-tts) si no hay presupuesto. Las etiquetas de
  tono del guion (`[curious, engaging explainer]`) son de ElevenLabs v3/v4: quítalas del texto para otros TTS.

Pasos:

- Prueba de ~10 s con líneas reales del guion → aprobación → **una sola toma** del guion completo.
- Mide la toma. Si pasa de ~2:35, acelera con rubberband (tono y formantes intactos) en vez de pagar otra:

  ```bash
  ffmpeg -i assets/audio/narracion-completa.mp3 -af "rubberband=tempo=1.13:formant=preserved" assets/audio/narracion-completa-x1.13.mp3
  ```

- Transcribe la toma ORIGINAL y corta por escena:

  ```bash
  npx hyperframes transcribe assets/audio/narracion-completa.mp3 -m large-v3 -l es
  python3 <SKILL>/scripts/alinear.py --root . --tx assets/audio/transcript.json \
      --audio assets/audio/narracion-completa-x1.13.mp3 --tempo 1.13
  ```

  Escribe `assets/voice/NN.mp3` y `audio_meta.json` (el formato que leen `captions.mjs` y `assemble-index.mjs`). Las
  palabras de los subtítulos salen del guion; los huecos (números, siglas) se interpolan.

## 5. Storyboard y cuadros de estilo

- `STORYBOARD.md` del flujo faceless-explainer, con `words: palabra@seg` (relativo al inicio de la escena, sale de
  `audio_meta.json`) para que cada revelación caiga en su palabra. Define la continuidad (qué elemento reaparece
  igual en varias escenas) y los colores por rol.
- Sistema visual en `references/estilo-jato-run.md`. Lo no negociable: cero `border-radius` (salvo las partículas),
  HUD con la izquierda vacía, nada debajo de y=1440, un solo degradado cian→violeta por escena.
- Construye primero **dos cuadros de estilo** a mano, partiendo de los aprobados del ep/02
  (`references/cuadros-aprobados/09-cerca.html` y `13-resultado.html`). `scripts/comun.py` tiene las piezas (fuentes,
  fondo, red de partículas, esquinas de mira, HUD, plantilla) si prefieres generarlos con Python.
- Enséñaselos al usuario en Studio (`npx hyperframes preview --background`) y espera su aprobación.

## 6. El resto de escenas con subagentes

- `frame-packets.mjs` (del flujo faceless-explainer) arma un paquete por escena.
- Copia `references/reglas-escena.md` a `.hyperframes/frame-packets/_reglas.md`, rellena lo que va entre `<…>` y pásalo
  a cada subagente con su paquete. Los dos cuadros aprobados son el esqueleto obligatorio.
- **Máximo 20 subagentes a la vez**; el exceso falla sin reintentarse. Lanza en tandas y lleva la cuenta.

## 7. Cierre

1. `assemble-index`, regenerar subtítulos y **volver a poner la banda** en `compositions/captions.html`
   (`--cap-band-top: 1445px; --cap-band-height: 170px;`).
   **Zona segura del feed de Instagram:** sin abrir el reel, el feed lo recorta a 4:5 por el centro (solo se ve
   y≈285–1635) y se pierde el kicker y la parte alta. En `index.html` reduce y baja todas las escenas
   (`.scene { transform: translate(0px, 184px) scale(0.865); transform-origin: 540px 0px; }`), vuelve
   transparente el fondo propio de cada escena (`.scene [id$="-bg"] { background: transparent !important; }`) y pon en
   `#root` el degradado `radial-gradient(120% 80% at 50% 45%, #121212 0%, #0a0a0a 55%, #050505 100%)`. Así el
   contenido (y=140–1440 en cada escena) cae en ~305–1430 y los subtítulos en ~1445–1615; en pantalla completa
   se sigue viendo bien (se detectó al ver el ep/01 en el feed, 2026-10-14).
2. `transitions inject` y `verify`, `npx hyperframes lint` y `npm run check` sin errores.
3. Hoja de capturas a mitad de cada escena para revisar todo de un vistazo.
4. Preview en Studio → aprobación del usuario → `npm run render`.
5. Entrega en la carpeta de entrega (ver «Preferencias del usuario»): el MP4 (H.264), `creditos-descripcion.txt` y
   el caption.

Antes de construir, lee `references/trampas.md`: HDR, subagentes, contraste, símbolos en Anton y la banda de
subtítulos ya costaron horas.
