# jjat-skills

Skills mejoradas de LangSmith para [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Basadas en las [skills oficiales de LangSmith](https://github.com/langchain-ai/langsmith-skills), con contenido ampliado a partir del curso oficial de LangChain Academy [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents), su [repositorio](https://github.com/langchain-ai/lca-reliable-agents), [documentacion](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction) y material complementario.

Cada skill es un **superset estricto** de su contraparte oficial — todo el contenido original esta incluido, mas las mejoras adicionales.

## Skills disponibles

| Skill | Descripcion | Basada en | Lineas |
|---|---|---|---|
| `jjat-langsmith-tracing` | Tracing, observabilidad, debugging, TypeScript, CLI | `langsmith-trace` | ~530 |
| `jjat-langsmith-datasets` | Datasets, PRD-driven building, TypeScript, tipos | `langsmith-dataset` | ~400 |
| `jjat-langsmith-evaluators` | Evaluadores, LLM judges, pairwise, TypeScript, experiments | `langsmith-evaluator` | ~690 |
| `jjat-langsmith-production` | Online evals, monitoreo, deploy | *(nueva)* | ~340 |

Para ver en detalle que mejoras tiene cada skill sobre las oficiales, consulta [skills/README.md](skills/README.md).

## Instalacion

### Opcion 1: Instalar desde el repositorio clonado

```bash
git clone https://github.com/tu-usuario/jjat-skills.git
cd jjat-skills

# Instalar todas las skills
claude skill install --path ./skills/jjat-langsmith-tracing
claude skill install --path ./skills/jjat-langsmith-datasets
claude skill install --path ./skills/jjat-langsmith-evaluators
claude skill install --path ./skills/jjat-langsmith-production
```

### Opcion 2: Instalar directamente desde GitHub

```bash
claude skill install --url https://github.com/tu-usuario/jjat-skills/tree/main/skills/jjat-langsmith-tracing
claude skill install --url https://github.com/tu-usuario/jjat-skills/tree/main/skills/jjat-langsmith-datasets
claude skill install --url https://github.com/tu-usuario/jjat-skills/tree/main/skills/jjat-langsmith-evaluators
claude skill install --url https://github.com/tu-usuario/jjat-skills/tree/main/skills/jjat-langsmith-production
```

### Verificar instalacion

```bash
claude skill list
```

## Requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado
- Cuenta de [LangSmith](https://smith.langchain.com/) con API key
- Python 3.10+ y/o Node.js 18+
- `pip install langsmith openai anthropic python-dotenv`
- `npm install langsmith openai` (para TypeScript)

## Creditos

- Skills oficiales de LangSmith: [langchain-ai/langsmith-skills](https://github.com/langchain-ai/langsmith-skills)
- Curso oficial de LangChain Academy: [Foundation: Building Reliable Agents](https://academy.langchain.com/courses/building-reliable-agents)
- Repositorio del curso: [langchain-ai/lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents)
- Documentacion del curso: [langchain-ai-lca-reliable-agents.mintlify.app](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction)
