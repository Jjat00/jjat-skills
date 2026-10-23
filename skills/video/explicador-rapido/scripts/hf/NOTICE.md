# Scripts de HyperFrames incluidos

Estos archivos son del flujo `faceless-explainer` de [HyperFrames](https://github.com/heygen-com/hyperframes),
copiados del commit
[`207c8a4`](https://github.com/heygen-com/hyperframes/tree/207c8a4daf6480d697f203784f1fd422727569e3/skills/faceless-explainer/scripts)
(octubre de 2026). HyperFrames retiró ese flujo de su repositorio poco después, y la skill depende de cuatro de sus
scripts para ensamblar el video: `frame-packets.mjs`, `captions.mjs`, `assemble-index.mjs` y `transitions.mjs`,
con su carpeta `lib/`. Solo usan módulos de Node, sin dependencias.

**Único cambio:** `frame-packets.mjs` toma el rol de los subagentes de `rol/` (`frame-worker-core.md` y
`frame-worker.md`, del mismo commit), porque antes lo leía de otras skills de HyperFrames ya retiradas y fallaba sin
ellas. El resto va tal cual.

Se distribuyen bajo la licencia Apache 2.0 de HyperFrames (`LICENSE` en esta carpeta). Copyright de sus autores.
No se incluyen `audio.mjs` ni `build-frame.mjs`, que dependían de otras skills retiradas: la voz la resuelve
`../alinear.py` y la piel de subtítulos viene en `../../assets/caption-skin.html`.
