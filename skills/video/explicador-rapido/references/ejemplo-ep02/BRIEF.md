---
flow: automation
storyboard: yes
message: "Una base de datos vectorial no busca palabras iguales: busca significados cercanos, porque convierte todo en puntos de un mapa y encuentra a los vecinos"
destination: reels-tiktok
aspect: 1080x1920
language: es
audience: "público general curioso de tecnología y estudiantes de software/ingeniería en Latinoamérica"
length: 150s
angle: concept
voice: "ElevenLabs 4GeB1bS2GAHAsGRM0eeU (juvenil latina) eleven_v4 (sirve cualquier TTS, ver § 4 de la skill)"
---

## Intent

Episodio 2 de la serie de explicadores rápidos (el ep/01 fue «Visión por computadora»).
Mismo sistema visual jato.run, misma voz, mismo pipeline. Narrado por una voz, sin nadie frente a la cámara.

## Assets

- assets/data/datos.json — datos reales con BAAI/bge-m3 (1024 dims): búsqueda semántica vs exacta,
  similitudes, analogía rey-hombre+mujer, mapa de palabras y benchmark fuerza bruta vs HNSW (hnswlib).

## Customizations

- Escenas de datos: tabla SQL, vector de 1024 números, mapa 2D de significados, flechas y ángulo coseno,
  vecinos más cercanos, grafo HNSW por pisos, clústeres IVF, cuantización, filtro por metadatos, RAG.
- Lo ilustrativo se marca como tal en la línea de metadatos.

## Notes

- Revisión: guion + 2 cuadros de estilo antes de construir todo. Prueba de voz de ~10 s antes de la toma.
- Español sin raya larga; «I A» separado si se narra la sigla.
- Entrega en entregas/bases vectoriales <fecha de entrega>.
