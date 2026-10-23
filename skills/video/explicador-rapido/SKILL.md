---
name: explicador-rapido
description: Produce un explicador vertical (1080x1920, ~2:30) en español sobre un tema de software o ingeniería, narrado por una voz y sin nadie frente a la cámara, con subtítulos palabra a palabra y DATOS REALES calculados con modelos de verdad (YOLO, ResNet, embeddings, benchmarks, física con CoolProp) y, si hace falta, gráficos de ManimGX y tomas 3D de Blender. Trae un estilo base (oscuro, paleta pastel, todo esquinado) que se adapta a la marca de cada persona, un episodio completo de ejemplo y su propio armado del video y los subtítulos sobre HyperFrames. Voz con ElevenLabs o HF Studio. Úsala cuando el usuario pida "un explicador de <tema>", "explícame <tema> en un reel", "<tema> explicado rápido", "un video como el de bases de datos vectoriales" o el siguiente episodio de su serie, aunque no nombre la skill.
---

# Explicador rápido

Reels que explican un tema técnico en ~2:30: una voz narra, la pantalla es toda para los datos y los diagramas, y cada
cifra sale de un modelo o un cálculo corrido de verdad. La skill es una **base**: trae un estilo de partida, un
episodio completo de ejemplo («Bases de datos vectoriales»: bge-m3, CLIP, hnswlib) y los scripts para armar el video;
cada persona le pone su marca, su voz y su ritmo.

- `references/ejemplo-ep02/`: brief, guion, storyboard, hoja de capturas del video final, 7 escenas de tipos
  distintos (portada, tabla, fórmula, benchmark, grafo, flujo, tarjetas) y los scripts de datos reales. Léelo antes
  de escribir el guion y vuelve a él al diseñar escenas.
- `references/cuadros-aprobados/`: dos escenas terminadas que hacen de esqueleto para las demás.
- `references/estilo-base.md`: el sistema visual de partida (§ 2).

`<SKILL>` es la carpeta de esta skill.

**Qué lo hace funcionar:** una idea por escena, cada revelación cae en la palabra que la motiva, y todas las cifras
salen de un modelo o benchmark corrido de verdad (lo ilustrativo se marca como tal en pantalla).

## 0. Instalación (la primera vez)

Antes del primer episodio, revisa la máquina del usuario e instala lo que falte. Dile qué vas a instalar y pide
permiso antes de cualquier comando con `sudo` o que cambie su sistema. Todo se verifica al final con un comando.

**Sistema operativo:** Linux y macOS directo. En **Windows, usa WSL2** (Ubuntu): HyperFrames, ffmpeg y los scripts
de la skill corren ahí sin cambios (`wsl --install` en PowerShell como administrador, y luego todo dentro de Ubuntu).

| Qué | Para qué | Ubuntu / WSL | macOS (Homebrew) | Verificar |
|---|---|---|---|---|
| **Node.js 20+** | HyperFrames y su CLI | `curl -fsSL https://deb.nodesource.com/setup_22.x \| sudo -E bash - && sudo apt install -y nodejs` (o nvm) | `brew install node` | `node -v` |
| **Python 3.10+** con venv | los scripts de la skill y los cálculos de datos | `sudo apt install -y python3 python3-venv python3-pip` | `brew install python` | `python3 --version` |
| **ffmpeg con rubberband** | cortar y acelerar la voz sin cambiar el tono | `sudo apt install -y ffmpeg` (ya trae rubberband) | `brew install ffmpeg-full` (el `ffmpeg` normal de Homebrew no lo trae) | `ffmpeg -hide_banner -filters \| grep rubberband` |
| **Chrome para el render** | HyperFrames renderiza en un Chrome sin interfaz | `npx hyperframes browser ensure` | igual | `npx hyperframes doctor` |
| **Skills de HyperFrames** | el contrato de composición y las guías (`/hyperframes`) | `npx hyperframes skills` | igual | `/hyperframes` aparece en el agente |
| **Clave de voz** | la narración | ver § 5 | ver § 5 | |

HyperFrames no se instala aparte: corre con `npx` y cada proyecto fija su versión al crearse (§ 1).
`npx hyperframes doctor` revisa todo de una vez; los «Not installed (optional)» de Kokoro y MusicGen no hacen falta.

**Opcionales, solo si el episodio los pide:**
- **Parakeet** (`npx hyperframes models install parakeet`): transcribir una voz que no trae tiempos por palabra (la
  de HF Studio) o un video de referencia (§ 5). Baja un modelo la primera vez.
- **[HF Studio](https://github.com/Jjat00/hf-studio)**: si además de la voz el usuario quiere generar imágenes o
  video con IA desde el agente (§ 5).
- **Codex CLI** u otro generador de imágenes, para imágenes ilustrativas (§ 4).
- **[ManimGX](https://manimgx.academa.ai/)** para diagramas, fórmulas y curvas animadas, y **Blender** para tomas 3D de
  objetos reales (`references/manim-y-blender.md`).
- Los modelos de cada tema (torch, sentence-transformers, ultralytics, CoolProp…) van en un venv del proyecto (§ 4),
  nunca en el Python del sistema.

## Preferencias del usuario

Antes de empezar, mira si el usuario dejó preferencias (CLAUDE.md, memoria): carpeta de entrega, voz, marca. Si no
hay, pregunta solo lo que haga falta y usa estos valores por defecto:

| Qué | Por defecto |
|---|---|
| Carpeta del proyecto | `videos/<tema>-explicado` en el directorio de trabajo |
| Entrega | `entregas/<tema> <día> <mes> <año>` |
| Estilo | `references/estilo-base.md`, adaptado a su marca si la tiene (§ 2) |
| Voz | ElevenLabs, voz `4GeB1bS2GAHAsGRM0eeU` (latina juvenil, pública), `eleven_v4`, velocidad 1,08; o la suya |
| Música | Sin música, salvo que la pida |

## Puertas de aprobación (no te las saltes)

El usuario aprueba en este orden y nada avanza sin su sí:
1. **Estilo** (§ 2), la primera vez o si cambia de marca.
2. **Guion** completo.
3. **Prueba de voz** de ~10 s con el guion real (antes de pagar la toma completa).
4. **Dos cuadros de estilo** (las escenas más representativas) antes de construir el resto.
5. **Preview** de todo el video antes del render final.

Toda generación de pago muestra su costo en USD antes y espera el OK. Como referencia, la toma completa de un episodio
de 2:30 (~3.000 caracteres) costó US$0,33 en ElevenLabs.

## 1. Proyecto

El flujo es estilo → brief → guion → voz → storyboard → cuadros de estilo → escenas → armado → revisión → render.

```bash
P=videos/<tema>-explicado
npx --yes hyperframes@latest init "$P" --non-interactive --example blank --resolution portrait
mkdir -p $P/{assets/fonts,assets/data,assets/media,assets/audio,tools,compositions/frames}
cp <SKILL>/assets/fonts/* $P/assets/fonts/          # las del estilo base; cámbialas por las de su marca (§ 2)
cp <SKILL>/references/estilo-base.md $P/frame.md     # o el frame.md de su estilo, si ya lo tiene
```

`init` fija la versión de HyperFrames en los scripts de `package.json` (`npm run dev`, `check`, `render`); usa esos
scripts, o `npx hyperframes@<esa versión>`, durante todo el episodio. Al retomar un proyecto viejo, mira si hay una
versión nueva con `npx hyperframes@latest upgrade --project . --check`; si actualizas, corre `npm run check` antes de
seguir y di de qué versión a qué versión pasaste. Carga la skill `/hyperframes` al empezar: tiene el contrato de
composición, el ciclo de trabajo y las guías de explainers y de video vertical.

`BRIEF.md` como en el ejemplo: `storyboard: yes`, `aspect: 1080x1920`, `language: es`, `length: 150s`,
`angle: concept`, `destination: reels-tiktok`, el `message` en una frase y la voz.

## 2. Estilo

La primera vez, el estilo se decide con el usuario. Pregúntale si tiene marca (colores, fuentes, logo, si su estética
es redondeada o esquinada, clara u oscura) y muéstrale el estilo base: una captura de
`references/ejemplo-ep02/capturas-1.jpg` sirve. Tres caminos:

- **Usar el estilo base tal cual:** oscuro casi negro, paleta pastel, todo esquinado, Anton para golpes de titular,
  Poppins para lectura y JetBrains Mono para datos, red de partículas como firma.
- **Adaptarlo a su marca** (lo normal): en el `frame.md` del proyecto cambia los colores (`colors:`), las fuentes
  (`typography:`, con sus archivos en `assets/fonts/` y su licencia), el radio de las esquinas, el nombre y la firma.
  Conserva la estructura: una idea por escena, un foco grande, HUD tenue, datos en mono, revelación en la palabra.
- **Uno nuevo desde cero:** escribe su `frame.md` con las mismas secciones que `estilo-base.md` y diseña los dos
  cuadros de estilo (§ 6) antes de nada.

Los subtítulos toman su aspecto de un `subtitulos.json` en la raíz del proyecto (solo las claves que cambian):

```json
{ "fuente": "Inter", "archivo": null, "peso": 700, "tamano": 56, "mayusculas": false,
  "viene": "rgba(255,255,255,0.35)", "activa": "#ffcc00", "dicha": "#ffffff", "cifra": "#ff6b6b" }
```

`archivo` es la fuente en `assets/fonts/`, o `null` si viene con HyperFrames (Inter, Poppins, Montserrat, Oswald,
Roboto, JetBrains Mono y otras; lista en `/hyperframes`). Sin `subtitulos.json`, quedan los del estilo base.
`scripts/comun.py`, `scripts/manim/estilo.py` y `scripts/blender/bcomun.py` traen los colores del estilo base: cópialos
a `tools/` del proyecto y cámbialos ahí si la marca es otra.

Guarda en la memoria del usuario la decisión de estilo, para no volver a preguntarla en el siguiente episodio.

## 3. Guion

- Si hay video de referencia: transcríbelo (`npx hyperframes transcribe ref.mp4 --language es --json`, ver § 5) y arma
  una hoja de contacto (`ffmpeg -i ref.mp4 -vf "fps=1/2,scale=270:-1,tile=8x5" hoja.png`). **Cubre punto por punto
  todo lo que dice la referencia**: en un episodio hubo que reponer 6 detalles perdidos al condensar.
- Mira `references/ejemplo-ep02/SCRIPT.md` para el tono, el largo de cada línea y el arco.
- Arco que funcionó: gancho cotidiano → la pregunta → cómo se hacía antes / por qué falla → idea clave → el mecanismo
  paso a paso con datos reales → cómo se hace rápido o a escala → usos → herramientas → idea central → cierre.
- ~510 palabras para 2:30 tras acelerar. 24 a 28 escenas («Line»).
- **Duración máxima 2:55 si va a Instagram:** los reels de más de 3:00 no se muestran a público nuevo. Antes de pagar
  la voz, estima la duración final (palabras ÷ ~2,8 palabras/s de la toma × aceleración) y recorta el guion. Un
  episodio salió en 3:10 con 711 palabras a ×1,20 y hubo que rehacerlo quitando dos escenas (mejor eso que acelerar
  más).
- `SCRIPT.md` con este formato exacto (lo leen los scripts de voz y `alinear.py`):

  ```markdown
  ## Line 1 — Portada
      [curious, engaging explainer] Bases de datos vectoriales, explicadas rápido.
  ```

- Español sin raya larga. Siglas que se narran letra a letra van separadas («I A»). Cifras escritas como se dicen si
  la voz las lee raro («mil veinticuatro»). La etiqueta de tono entre corchetes es para ElevenLabs; no se dice.

## 4. Datos reales

Antes de diseñar escenas, calcula con modelos de verdad cada número que vaya a salir en pantalla. Usa un venv propio
del proyecto (p. ej. `.cv-venv` con torch CPU) y scripts en `tools/` que escriban `assets/data/*.json`.

- Busca ejemplos que **muestren el contraste** que explica el video: «tenis para correr bajo la lluvia» da «tenis de
  mesa» por palabra y «zapatillas impermeables para trotar» (0,63) por significado; FaceNet da 0,73 para la misma
  persona y 1,28 para un extraño con umbral 1,1.
- Prueba varios modelos si el primero no separa bien (ver `references/trampas.md`).
- **Temas de ingeniería o física** (p. ej. un auto que flota con aire comprimido): no te quedes con el anuncio. Busca
  papers, artículos técnicos y lecturas de pantalla del evento, y calcula con bibliotecas de verdad (p. ej. CoolProp
  para gas real: 600 L con 250 kg de aire dan 454 bar con Z = 1,26, no lo que diría el gas ideal). Lo que sea
  estimación tuya (masa, áreas, coeficientes) se marca en pantalla y se lista en una escena de supuestos y en los
  créditos. Guarda las fuentes en `assets/data/fuentes.md`.
- Fotos y videos: Wikimedia Commons por categoría y Pexels, de licencia libre, mejor con escenas de la región del
  público. Créditos en `assets/media/CREDITOS.md` y el texto para la descripción del post en `creditos-descripcion.txt`.
- **Imágenes generadas (si hay Codex CLI, HF Studio u otro generador):** para lo ilustrativo que no existe con licencia
  libre: fotos de producto de un catálogo de ejemplo, portadas de álbum de una app simulada, pares «parecido»
  (perro/cachorro). Con imágenes, el episodio de ejemplo quedó mejor que su versión solo con gráficos.
  - Con Codex (herramienta integrada de imágenes, sin API key aparte): un `codex exec` por lote con el prompt por
    stdin y una lista numerada de imágenes con su nombre de archivo; 3 corridas en paralelo hicieron 13 imágenes en
    ~6 min.

    ```bash
    echo "Genera estas imágenes con tu herramienta integrada y guárdalas en este directorio: 1) prod-botas.png …
    Cuadradas, fondo neutro, sin texto ni logotipos. No hagas nada más." | \
      codex exec --skip-git-repo-check --sandbox workspace-write -C assets/gen -
    ```

  - Para una variante que conserve identidad (el cachorro del mismo perro) pasa la primera como referencia con
    `-i perro.png` y describe los rasgos que cambian.
  - Pásalas a JPG de 640 px (`assets/gen/*.jpg`, todo el lote < 1 MB) y no dejes los PNG en el proyecto.
  - Si el generador es de pago (HF Studio, una API), muestra el costo en USD y espera el OK.
  - Créditos en `assets/gen/CREDITOS.md`, aclarando que son ilustrativas y no fotos reales. Los **datos** siguen
    saliendo de modelos reales: la imagen ilustra, nunca reemplaza un número.

## 5. Voz

Dos caminos. Ofrece HF Studio solo si al usuario le sirve para algo más que la voz; si solo quiere la voz, ElevenLabs
directo.

### ElevenLabs (la voz, sin nada más)

**La clave:** el usuario entra a [elevenlabs.io](https://elevenlabs.io) (el plan gratis trae créditos para probar),
abre **Developers → API Keys** (abajo a la izquierda, o
[elevenlabs.io/app/developers/api-keys](https://elevenlabs.io/app/developers/api-keys)), crea una clave con permiso de
**Text to Speech** (y de lectura de **Voices** si quiere elegir voz desde el agente) y la copia una sola vez.
Pídesela, nunca la escribas en un archivo del repo ni la muestres; guárdala como variable de entorno (por ejemplo en
`~/.bashrc` o `~/.zshrc`: `export ELEVENLABS_API_KEY=...`, o en un `.env` del proyecto que esté en `.gitignore`).
ElevenLabs cobra por carácter según el plan: un episodio de 2:30 son ~3.000 caracteres.

**La voz:** por defecto `4GeB1bS2GAHAsGRM0eeU` (latina juvenil, de la biblioteca pública). Si el usuario quiere otra,
que la elija en la Voice Library de ElevenLabs y te pase su `voice_id`.

`scripts/voz_elevenlabs.py` pide la voz **con el tiempo de cada palabra** (endpoint `with-timestamps`), así que no
hace falta transcribir. Sin `--generar` solo cuenta los caracteres: díselo al usuario, con el costo, y espera su OK.

```bash
python3 <SKILL>/scripts/voz_elevenlabs.py --root . --prueba 3              # cuenta: 3 líneas, ~10 s
python3 <SKILL>/scripts/voz_elevenlabs.py --root . --prueba 3 --generar    # assets/audio/prueba-voz.mp3
python3 <SKILL>/scripts/voz_elevenlabs.py --root . --generar               # narracion-completa.mp3 + transcript.json
```

`--voz`, `--modelo`, `--velocidad` y `--estabilidad` cambian la voz. En un episodio corto, la prueba es `--prueba 1`.

### HF Studio (si también va a generar imágenes o video)

[HF Studio](https://github.com/Jjat00/hf-studio) es un estudio de IA open source (MIT) que corre en la máquina del
usuario y se conecta al agente por MCP: voz, música y efectos con ElevenLabs, e imágenes y video con los modelos de
Higgsfield, con el costo antes de gastar. Conviene si el usuario también quiere imágenes ilustrativas o tomas de video
generadas; para solo la voz, ElevenLabs directo es más simple.

- **Instalarlo:** sigue su guía para agentes, [AGENTS.md](https://github.com/Jjat00/hf-studio/blob/main/AGENTS.md)
  (necesita `uv`; la clave obligatoria es la de Higgsfield, de [console.higgsfield.ai](https://console.higgsfield.ai),
  y la de ElevenLabs habilita el audio).
- **La voz:** herramienta `text_to_speech`: sin `quote_id` cotiza; con el `quote_id`, tras el OK, genera. Descarga el
  MP3 a `assets/audio/narracion-completa.mp3`.
- **Los tiempos:** esta voz no trae tiempos por palabra; transcríbela con Parakeet (§ 0):

  ```bash
  npx hyperframes transcribe assets/audio/narracion-completa.mp3 --language es --json   # escribe assets/transcript.json
  ```

  Sin Parakeet, pasa `--model large-v3`: los modelos chicos de Whisper separan mal las palabras en español (y
  `small.en`, el de por defecto, traduce al inglés).

### Después de la toma

- Mide la toma. Si pasa de ~2:35, acelera con rubberband (tono y formantes intactos) en vez de pagar otra:

  ```bash
  ffmpeg -i assets/audio/narracion-completa.mp3 -af "rubberband=tempo=1.13:formant=preserved" assets/audio/narracion-completa-x1.13.mp3
  ```

- Corta por escena con los tiempos (`--tx assets/audio/transcript.json` si vienen de ElevenLabs,
  `--tx assets/transcript.json` si vienen de `transcribe`):

  ```bash
  python3 <SKILL>/scripts/alinear.py --root . --tx assets/audio/transcript.json \
      --audio assets/audio/narracion-completa-x1.13.mp3 --tempo 1.13
  ```

  Escribe `assets/voice/NN.mp3` y `audio_meta.json` (lo que leen `palabras.py` y `armar.py`). Las palabras de los
  subtítulos salen del guion; los huecos (números, siglas) se interpolan. Sin aceleración, `--tempo 1` y `--audio`
  apunta a la toma original.

## 6. Storyboard y cuadros de estilo

- `STORYBOARD.md` con un bloque `## Frame N — Título` por escena (formato del ejemplo) que lleva `- src:
  compositions/frames/<id>.html`, `- transition_in: crossfade` (o `cut`) y `- words: palabra@seg` (relativo al inicio
  de la escena) para que cada revelación caiga en su palabra. **El id de cada escena empieza con letra**
  (`e01-gancho`, no `01-gancho`): el id es también un selector CSS y uno que empieza con número no es válido. Escribe
  las escenas con su `scene` y `voiceover`, y deja que `python3 <SKILL>/scripts/palabras.py --root .` llene
  `duration` y `words` de cada una desde `audio_meta.json` (se puede repetir si cambia la voz). Define la continuidad
  (qué elemento reaparece igual en varias escenas) y los colores por rol. Modelo:
  `references/ejemplo-ep02/STORYBOARD.md`.
- Sistema visual en el `frame.md` del proyecto (§ 2). Del estilo base, lo que sostiene el formato en cualquier marca:
  nada debajo de y=1440 (ahí van los subtítulos), HUD tenue, un solo acento fuerte por escena.
- Construye primero **dos cuadros de estilo** a mano, partiendo de los de `references/cuadros-aprobados/`
  (`e09-cerca.html` y `e13-resultado.html`) y aplicando el estilo del usuario. `scripts/comun.py` tiene las piezas del
  estilo base (fuentes, fondo, red de partículas, esquinas de mira, HUD, plantilla) si prefieres generarlos con Python.
- Enséñaselos al usuario en Studio (`npm run dev`) y espera su aprobación.
- **Gráficos de ManimGX y tomas de Blender** (opcional): para diagramas de fuerzas, fórmulas que se transforman,
  curvas que se dibujan o un objeto real en 3D. Se renderizan como MP4 sin texto de lectura y entran a la escena como
  `<video>` con `mix-blend-mode: lighten`. Todo en `references/manim-y-blender.md`, con las utilidades en
  `scripts/manim/` (estilo, `Reloj` que sincroniza con las palabras, silueta de auto) y `scripts/blender/` (render,
  auto 3D, codificación). Los objetos reales se dibujan con su forma real: un auto con carrocería suave y llantas
  redondas, nunca cajas.

## 7. El resto de escenas con subagentes

- Arma un paquete por escena:

  ```bash
  python3 <SKILL>/scripts/paquetes.py --root . --refs compositions/frames/<cuadro-a>.html compositions/frames/<cuadro-b>.html
  ```

  Los deja en `.hyperframes/paquetes/<id>.md` (sin los cuadros ya aprobados) y copia `references/reglas-escena.md` a
  `.hyperframes/paquetes/_reglas.md`: rellena ahí lo que va entre `<…>` y ajusta las reglas de forma y color al estilo
  del usuario antes de lanzar a nadie. Cada subagente recibe su paquete, las reglas y la orden de cargar
  `/hyperframes` (el contrato de composición). Los dos cuadros aprobados son el esqueleto obligatorio; si la escena es
  de un tipo que tiene modelo en `references/ejemplo-ep02/frames/` (tabla, benchmark, grafo, flujo, tarjetas), pásale
  también ese.
- **Máximo 20 subagentes a la vez**; el exceso falla sin reintentarse. Lanza en tandas y lleva la cuenta.
- **Un solo script de timeline por escena** (el `<script>` que carga GSAP no cuenta). Un bloque sobrante copiado de
  otra escena dejó 7 escenas en negro sin que lint ni check dijeran nada (ver `references/trampas.md`).

## 8. Cierre

1. Arma el video con un solo comando, que puedes repetir cada vez que cambies una escena:

   ```bash
   python3 <SKILL>/scripts/armar.py --root .
   ```

   Escribe `index.html` (cada escena en su host, con el mismo id que su `data-composition-id` y que la clave de su
   timeline; la voz de cada escena; el fundido cruzado de 0,5 s, o corte si la escena pide `transition_in: cut`) y
   `compositions/captions.html` (subtítulos en grupos de 2 a 3 palabras: tenue lo que viene, resaltado lo que suena,
   con el aspecto de `subtitulos.json`), y corre el lint con la versión del proyecto. Si el proyecto tiene
   `tools/despues_de_armar.py`, lo corre antes del lint: ahí van capas propias, como un botón SEGUIR encima del video.

   También aplica la **zona segura del feed de Instagram**: sin abrir el reel, el feed lo recorta a 4:5 por el centro
   (solo se ve y≈285–1635) y se pierde la parte alta. Por eso escenas y subtítulos se reducen y bajan
   (`translate(0px, 184px) scale(0.865)`) sobre un degradado de fondo: el contenido (y=140–1440 en cada escena) cae en
   ~305–1430 y los subtítulos debajo; en pantalla completa se sigue viendo bien. `--sin-zona-segura` lo quita (p. ej.
   para TikTok o YouTube Shorts).
2. `npm run check` (o `npx hyperframes check --json`): corrige cada error y pesa cada aviso. La zona segura reduce
   todo a 0,865, así que el texto de lectura va de **33 px para arriba en el diseño** (28 en el video). Los avisos
   `text_below_floor` del HUD y los metadatos (22 px en el estilo base) son decorativos y se esperan; si salen en un
   texto de lectura, súbelo. También se esperan avisos informativos de desborde de la red de partículas y de solape
   del HUD durante el fundido entre escenas.
3. Revisión visual: `npx hyperframes snapshot --review` y su hoja de capturas. Busca textos encimados (fichas sobre
   ejes, cifras sobre rótulos), escenas vacías o en negro y subtítulos fuera de la banda: el usuario los ve antes que
   nada.
4. Preview en Studio (`npm run dev`) → aprobación del usuario → `npm run render`.
5. Entrega en la carpeta de entrega (ver «Preferencias del usuario»): el MP4 (H.264), `creditos-descripcion.txt` y
   el caption (en Instagram, **máximo 5 hashtags**).

## Episodios cortos

Para una prueba, un teaser o un anuncio de 20 a 60 s: el mismo flujo con 3 a 8 escenas (≈2,8 palabras por segundo de
voz, antes de acelerar). Las puertas de aprobación siguen igual, pero basta un cuadro de estilo si son pocas escenas,
y la prueba de voz es `--prueba 1` (con tan pocas líneas, tres ya son la toma entera). Los datos reales siguen siendo
obligatorios en lo que salga en pantalla; si no hay cifras, mejor una escena de concepto que un número inventado.

Antes de construir, lee `references/trampas.md`: HDR, subagentes, contraste, símbolos en Anton, la banda de
subtítulos y los clips de Manim y Blender ya costaron horas.
