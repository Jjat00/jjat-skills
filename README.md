# jjat-skills

Skills para [Claude Code](https://docs.anthropic.com/en/docs/claude-code): contenido para redes, producción de video, métodos de ingeniería y agentes de IA (LangSmith mejoradas y Gemini Embedding 2).

## Estructura

Las skills se ordenan por carpetas de categoría. Cada skill es una carpeta con su `SKILL.md`:

```
skills/
  contenido/     # publicaciones para redes: carruseles, posts
  ia-agentes/    # agentes, LLMs, evaluación, embeddings
  ingenieria/    # métodos de ingeniería: ingeniería inversa, cajas negras
  video/         # edición y producción de video
```

Una skill nueva va en la carpeta de su categoría; si no encaja en ninguna, se crea una categoría nueva (nombre corto, en minúscula). Luego se enlaza en Claude Code con `./install.sh` y se añade a la tabla de su categoría abajo.

## Skills disponibles

### Contenido

| Skill | Descripción |
|---|---|
| `noticias-ia-carrusel` | Investiga las noticias de IA y software del día (últimas 24-36 h, fecha verificada), descarga o captura el video o la imagen de cada una y renderiza el carrusel para Instagram (4:5, video + imagen), TikTok (9:16, solo imágenes) y LinkedIn (PDF 4:5 con texto profesional), más un reel de hasta 1:30 con o sin narración (voces gratis de edge-tts o de pago de ElevenLabs), con caption, hashtags, hora y una página de descarga. Playwright + ffmpeg. |

### Video

| Skill | Descripción |
|---|---|
| `explicador-rapido` | Explicador vertical de ~2:30 sobre un tema de software o ingeniería, narrado por una voz y sin nadie frente a la cámara, con subtítulos palabra a palabra y datos reales calculados con modelos (YOLO, ResNet, embeddings, benchmarks). Es una base: trae un estilo de partida (oscuro, pastel, esquinado) que se adapta a la marca de cada persona, un episodio completo de ejemplo y su propio armado del video sobre HyperFrames. Voz con ElevenLabs (con tiempos por palabra, sin transcribir) o con [HF Studio](https://github.com/Jjat00/hf-studio) si también se generan imágenes o video. Opcionalmente, imágenes ilustrativas, gráficos de ManimGX y tomas 3D de Blender. La skill explica qué instalar la primera vez (Node, Python, ffmpeg con rubberband y HyperFrames). |
| `google-flow` | Genera video e imagen en Google Flow (Veo 3.1, Omni, Nano Banana) desde la terminal con los créditos del plan de Google AI: crea el proyecto, sube referencias, elige modelo y escribe el prompt; la persona solo pulsa enviar y Aprobar. CLI propio sobre las RPC internas + agent-browser. |
| `letras-detras` | Pone la letra de una canción en tipografía gigante detrás del sujeto de un video (serif condensada, palabras al ritmo de la voz, acentos en rojo o dorado) y le monta la canción. Entradas: video + link de Spotify, nombre o "artista - canción"; letra sincronizada de LRCLib, audio de YouTube, alineado con faster-whisper y matte con Robust Video Matting. Local y gratis. |
| `reel-editorial` | Convierte una toma de webcam o celular en un reel vertical con estilo editorial: montaje por transcripción (quita tomas falsas y pausas), persona recortada sobre tarjetas de color, paneles de motion graphics, subtítulos palabra a palabra y audio a -14 LUFS. Local con ffmpeg, faster-whisper y [HyperFrames](https://hyperframes.heygen.com). |
| `ruta-dron-ubicacion` | Video de ubicación estilo inmobiliaria desde una toma de dron de cualquier propiedad (local, casa, lote, finca): ruta animada pegada a las calles, pin, tarjeta y cierre; opcionalmente el lote con cotas y área. OpenCV + COLMAP + ffmpeg. |

### Ingeniería

| Skill | Descripción |
|---|---|
| `caja-negra` | Método para replicar exactamente una función o un servicio sin código ni documentación a partir de consultas, con un set oculto que lo puntúa. Destilado de dos retos reales: uno perdido (20 %) y otro ganado (83, 99 y 100 de 100). Clasifica la caja, reparte el presupuesto (lo transversal antes que lo estructural), mide con regresión, fuzzer diferencial, canario y diferencial exploratorio, y fija la puerta para gastar una evaluación oficial. Incluye comparador y cliente de laboratorio en Python. |

### Gemini Embedding 2

| Skill | Descripción |
|---|---|
| `gemini-embedding-2` | Embeddings multimodales con Google Gemini Embedding 2 (texto, imágenes, audio, video, PDF), búsqueda semántica cross-modal, integración con Qdrant y ChromaDB, pipelines RAG |

Basada en la [documentación oficial de Google](https://ai.google.dev/gemini-api/docs/embeddings), el [cookbook de Gemini](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb), la [integración con Qdrant](https://qdrant.tech/documentation/embeddings/gemini/) y [ChromaDB](https://docs.trychroma.com/integrations/embedding-models/google-gemini).

### LangSmith (mejoradas)

| Skill | Descripción | Basada en | Líneas |
|---|---|---|---|
| `jjat-langsmith-tracing` | Tracing, observabilidad, debugging, TypeScript, CLI | `langsmith-trace` | ~530 |
| `jjat-langsmith-datasets` | Datasets, PRD-driven building, TypeScript, tipos | `langsmith-dataset` | ~400 |
| `jjat-langsmith-evaluators` | Evaluadores, LLM judges, pairwise, TypeScript, experiments | `langsmith-evaluator` | ~690 |
| `jjat-langsmith-production` | Online evals, monitoreo, deploy | *(nueva)* | ~340 |

Basadas en las [skills oficiales de LangSmith](https://github.com/langchain-ai/langsmith-skills), con contenido ampliado del curso [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents). Cada skill es un **superset estricto** de su contraparte oficial.

Para ver en detalle las mejoras sobre las oficiales, consulta [skills/ia-agentes/README.md](skills/ia-agentes/README.md).

## Instalación

### Local (enlaces a este repo)

Enlaza todas las skills del repo en `~/.claude/skills` (los cambios en el repo se ven al instante):

```bash
./install.sh            # enlaza todas
./install.sh --dry-run  # muestra qué haría
```

### Con npx (recomendado)

Instala todas las skills directamente desde GitHub:

```bash
npx skills add Jjat00/jjat-skills -g
```

O instala skills individuales (`npx skills add Jjat00/jjat-skills --list` muestra todas):

```bash
# Gemini Embedding 2
npx skills add Jjat00/jjat-skills --skill gemini-embedding-2 -g

# LangSmith
npx skills add Jjat00/jjat-skills --skill jjat-langsmith-tracing -g
npx skills add Jjat00/jjat-skills --skill jjat-langsmith-datasets -g
npx skills add Jjat00/jjat-skills --skill jjat-langsmith-evaluators -g
npx skills add Jjat00/jjat-skills --skill jjat-langsmith-production -g
```

### Copia manual

Cada skill es una carpeta autocontenida: cópiala en `~/.claude/skills/` (o en `.claude/skills/` de un proyecto) y Claude Code la carga en la siguiente sesión.

```bash
git clone https://github.com/Jjat00/jjat-skills.git
cp -r jjat-skills/skills/ia-agentes/gemini-embedding-2 ~/.claude/skills/
```

### Verificar la instalación

Dentro de Claude Code, `/skills` lista las skills disponibles.

## Requisitos

### Gemini Embedding 2

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- API key de [Google AI Studio](https://aistudio.google.com/apikey) (`GEMINI_API_KEY`)
- Python 3.10+: `pip install google-genai`
- TypeScript (opcional): `npm install @google/genai`
- Vector DB: `pip install qdrant-client` o `pip install chromadb`

### LangSmith

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Cuenta de [LangSmith](https://smith.langchain.com/) con API key
- Python 3.10+ y/o Node.js 18+
- `pip install langsmith openai anthropic python-dotenv`
- `npm install langsmith openai` (para TypeScript)

## Créditos

- Documentación oficial de Gemini Embeddings: [ai.google.dev](https://ai.google.dev/gemini-api/docs/embeddings)
- Skills oficiales de LangSmith: [langchain-ai/langsmith-skills](https://github.com/langchain-ai/langsmith-skills)
- Curso oficial de LangChain Academy: [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents)
- Repositorio del curso: [langchain-ai/lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents)
- Documentación del curso: [langchain-ai-lca-reliable-agents.mintlify.app](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction)
