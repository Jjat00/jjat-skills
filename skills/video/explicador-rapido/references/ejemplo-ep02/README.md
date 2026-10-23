# Ejemplo completo: ep/02 «Bases de datos vectoriales»

Material real del episodio 2 (octubre de 2026, 2:37,5, 26 escenas). Sirve para ver cómo se ve un guion terminado,
cómo se escribe un storyboard que los subagentes entienden y qué variedad de escenas tiene un episodio. No se copia tal
cual: se usa de referencia para el tema nuevo.

| Archivo | Qué muestra |
|---|---|
| `BRIEF.md` | El brief con mensaje, público, duración y voz. |
| `SCRIPT.md` | El guion aprobado: 26 líneas en el formato exacto que lee `scripts/alinear.py`. |
| `STORYBOARD.md` | Una ficha por escena: `kind`, qué se ve, `voiceover`, `words: palabra@seg` y la continuidad. |
| `capturas-1.jpg` a `capturas-3.jpg` | Hoja de capturas a mitad de cada escena del video final. Mírala antes de diseñar. |
| `frames/` | 7 escenas terminadas de tipos distintos (abajo). |
| `tools/datos.py`, `tools/mapa.py` | Cómo se calcularon los números: embeddings con `BAAI/bge-m3`, similitudes, benchmark con hnswlib y mapa t-SNE. |
| `data/*.json` | La salida de esos scripts, que las escenas leen. |

## Escenas incluidas

Además de los dos cuadros de estilo de `../cuadros-aprobados/` (09 mapa de vecinos, 13 resultado de búsqueda):

| Escena | Tipo | Para qué sirve de modelo |
|---|---|---|
| `01-portada.html` | portada | Título en Anton con degradado y, detrás, los números reales del vector de «perro». |
| `04-base-normal.html` | tabla | Una tabla SQL que se dibuja fila a fila y una consulta `WHERE` que resalta la fila exacta. |
| `11-coseno.html` | fórmula y ángulo | Flechas perro→cachorro (35,7°, 0,81) y perro→factura (64,1°, 0,44) con la fórmula del coseno. |
| `15-fuerza-bruta.html` | benchmark | Barrido uno por uno con cronómetro real (16 ms con 200 000 vectores) y la barra de mil millones (≈ 79 s). |
| `17-hnsw.html` | grafo por pisos | Grafo HNSW de 3 pisos; la ruta salta lejos arriba y baja piso por piso hasta el vecino. |
| `22-rag.html` | diagrama de flujo | RAG: documento → trozos → vectores; la pregunta recupera los 2 trozos más cercanos y el modelo responde citando. |
| `23-herramientas.html` | tarjetas | Pinecone, Qdrant, Weaviate, Milvus y Chroma con su tipo; luego Postgres + pgvector con SQL real. |

Todas cargan las fuentes desde `assets/fonts/` (relativo a la raíz del proyecto) y GSAP por CDN: para abrirlas, cópialas
a `compositions/frames/` de un proyecto que ya tenga las fuentes de `<SKILL>/assets/fonts/`.

## Lo que no está

- La voz y los cortes por escena (`assets/voice/`, `audio_meta.json`): se generan para cada episodio.
- Las otras 17 escenas y las fotos con licencia libre de la escena 21.
- El video final: en [skills.jato.run/explicador-rapido](https://skills.jato.run/explicador-rapido/) hay recortes.
