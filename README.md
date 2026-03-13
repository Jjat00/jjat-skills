# jjat-skills

Skills para [Claude Code](https://docs.anthropic.com/en/docs/claude-code): LangSmith mejoradas + Gemini Embedding 2.

## Skills disponibles

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

Para ver en detalle las mejoras sobre las oficiales, consulta [skills/README.md](skills/README.md).

## Instalacion

### Con npx (recomendado)

Instala todas las skills directamente desde GitHub:

```bash
npx skills add Jjat00/jjat-skills -g
```

O instala skills individuales:

```bash
# Gemini Embedding 2
npx skills add Jjat00/jjat-skills/skills/gemini-embedding-2 -g

# LangSmith
npx skills add Jjat00/jjat-skills/skills/jjat-langsmith-tracing -g
npx skills add Jjat00/jjat-skills/skills/jjat-langsmith-datasets -g
npx skills add Jjat00/jjat-skills/skills/jjat-langsmith-evaluators -g
npx skills add Jjat00/jjat-skills/skills/jjat-langsmith-production -g
```

### Con Claude Code CLI

```bash
# Gemini Embedding 2
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/gemini-embedding-2

# LangSmith
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/jjat-langsmith-tracing
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/jjat-langsmith-datasets
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/jjat-langsmith-evaluators
claude skill install --url https://github.com/Jjat00/jjat-skills/tree/main/skills/jjat-langsmith-production
```

```bash
# O desde el repositorio clonado
git clone https://github.com/Jjat00/jjat-skills.git
cd jjat-skills

claude skill install --path ./skills/gemini-embedding-2
claude skill install --path ./skills/jjat-langsmith-tracing
claude skill install --path ./skills/jjat-langsmith-datasets
claude skill install --path ./skills/jjat-langsmith-evaluators
claude skill install --path ./skills/jjat-langsmith-production
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
