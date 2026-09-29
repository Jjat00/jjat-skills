# jjat-skills

Skills para [Claude Code](https://docs.anthropic.com/en/docs/claude-code): LangSmith mejoradas + Gemini Embedding 2.

## Estructura

Las skills se ordenan por carpetas de categoría. Cada skill es una carpeta con su `SKILL.md`:

```
skills/
  contenido/     # publicaciones para redes: carruseles, posts
  ia-agentes/    # agentes, LLMs, evaluación, embeddings
  video/         # edición y producción de video
```

Una skill nueva va en la carpeta de su categoría; si no encaja en ninguna, se crea una categoría nueva (nombre corto, en minúscula). Luego se enlaza en Claude Code con `./install.sh` y se añade a la tabla de su categoría abajo.

## Skills disponibles

### Contenido

| Skill | Descripcion |
|---|---|
| `noticias-ia-carrusel` | Investiga las noticias de IA y software del dia (ultimas 24-36 h, fecha verificada), descarga o captura el video o la imagen de cada una y renderiza el carrusel para Instagram (4:5, video + imagen) y TikTok (9:16, solo imagenes) con caption, hashtags, hora y una pagina de descarga. Playwright + ffmpeg. |

### Video

| Skill | Descripcion |
|---|---|
| `reel-editorial` | Convierte una toma de webcam o celular en un reel vertical con estilo editorial: montaje por transcripcion (quita tomas falsas y pausas), persona recortada sobre tarjetas de color, paneles de motion graphics, subtitulos palabra a palabra y audio a -14 LUFS. Local con ffmpeg, faster-whisper y [HyperFrames](https://hyperframes.heygen.com). |

### Gemini Embedding 2

| Skill | Descripcion |
|---|---|
| `gemini-embedding-2` | Embeddings multimodales con Google Gemini Embedding 2 (texto, imagenes, audio, video, PDF), busqueda semantica cross-modal, integracion con Qdrant y ChromaDB, pipelines RAG |

Basada en la [documentacion oficial de Google](https://ai.google.dev/gemini-api/docs/embeddings), el [cookbook de Gemini](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb), la [integracion con Qdrant](https://qdrant.tech/documentation/embeddings/gemini/) y [ChromaDB](https://docs.trychroma.com/integrations/embedding-models/google-gemini).

### LangSmith (mejoradas)

| Skill | Descripcion | Basada en | Lineas |
|---|---|---|---|
| `jjat-langsmith-tracing` | Tracing, observabilidad, debugging, TypeScript, CLI | `langsmith-trace` | ~530 |
| `jjat-langsmith-datasets` | Datasets, PRD-driven building, TypeScript, tipos | `langsmith-dataset` | ~400 |
| `jjat-langsmith-evaluators` | Evaluadores, LLM judges, pairwise, TypeScript, experiments | `langsmith-evaluator` | ~690 |
| `jjat-langsmith-production` | Online evals, monitoreo, deploy | *(nueva)* | ~340 |

Basadas en las [skills oficiales de LangSmith](https://github.com/langchain-ai/langsmith-skills), con contenido ampliado del curso [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents). Cada skill es un **superset estricto** de su contraparte oficial.

Para ver en detalle las mejoras sobre las oficiales, consulta [skills/ia-agentes/README.md](skills/ia-agentes/README.md).

## Instalacion

### Local (enlaces a este repo)

Enlaza todas las skills del repo en `~/.claude/skills` (los cambios en el repo se ven al instante):

```bash
./install.sh            # enlaza todas
./install.sh --dry-run  # muestra que haria
```

### Con npx (recomendado)

Instala todas las skills directamente desde GitHub:

```bash
npx skills add Jjat00/jjat-skills -g
```

O instala skills individuales:

```bash
# Gemini Embedding 2
npx skills add Jjat00/jjat-skills/skills/ia-agentes/gemini-embedding-2 -g

# LangSmith
npx skills add Jjat00/jjat-skills/skills/ia-agentes/jjat-langsmith-tracing -g
npx skills add Jjat00/jjat-skills/skills/ia-agentes/jjat-langsmith-datasets -g
npx skills add Jjat00/jjat-skills/skills/ia-agentes/jjat-langsmith-evaluators -g
npx skills add Jjat00/jjat-skills/skills/ia-agentes/jjat-langsmith-production -g
```

### Con Claude Code CLI

```bash
# Gemini Embedding 2
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/ia-agentes/gemini-embedding-2

# LangSmith
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/ia-agentes/jjat-langsmith-tracing
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/ia-agentes/jjat-langsmith-datasets
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/ia-agentes/jjat-langsmith-evaluators
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/ia-agentes/jjat-langsmith-production
```

```bash
# O desde el repositorio clonado
git clone https://github.com/Jjat00/jjat-skills.git
cd jjat-skills

claude skill install --path ./skills/ia-agentes/gemini-embedding-2
claude skill install --path ./skills/ia-agentes/jjat-langsmith-tracing
claude skill install --path ./skills/ia-agentes/jjat-langsmith-datasets
claude skill install --path ./skills/ia-agentes/jjat-langsmith-evaluators
claude skill install --path ./skills/ia-agentes/jjat-langsmith-production
```

### Verificar instalacion

```bash
claude skill list
```

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

## Creditos

- Documentacion oficial de Gemini Embeddings: [ai.google.dev](https://ai.google.dev/gemini-api/docs/embeddings)
- Skills oficiales de LangSmith: [langchain-ai/langsmith-skills](https://github.com/langchain-ai/langsmith-skills)
- Curso oficial de LangChain Academy: [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents)
- Repositorio del curso: [langchain-ai/lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents)
- Documentacion del curso: [langchain-ai-lca-reliable-agents.mintlify.app](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction)
