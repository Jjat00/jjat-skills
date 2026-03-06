# jjat-skills

Skills mejoradas de LangSmith para [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Basadas en las [skills oficiales de LangSmith](https://github.com/langchain-ai/langsmith-skills), con contenido ampliado a partir del curso [Reliable AI Agents](https://github.com/langchain-ai/lca-reliable-agents), su [documentacion](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction) y el material del PDF "Agentes IA Confiables".

## Skills disponibles

| Skill | Descripcion | Basada en |
|---|---|---|
| `jjat-langsmith-tracing` | Tracing, observabilidad, debugging, CLI | `langsmith-trace` |
| `jjat-langsmith-datasets` | Datasets, PRD-driven building, tipos | `langsmith-dataset` |
| `jjat-langsmith-evaluators` | Evaluadores, LLM judges, pairwise, experiments | `langsmith-evaluator` |
| `jjat-langsmith-production` | Online evals, monitoreo, deploy | *(nueva)* |

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
- Python 3.10+
- `pip install langsmith openai anthropic`

## Creditos

- Skills oficiales de LangSmith: [langchain-ai/langsmith-skills](https://github.com/langchain-ai/langsmith-skills)
- Repositorio del curso: [langchain-ai/lca-reliable-agents](https://github.com/langchain-ai/lca-reliable-agents)
- Documentacion del curso: [langchain-ai-lca-reliable-agents.mintlify.app](https://langchain-ai-lca-reliable-agents.mintlify.app/introduction)
