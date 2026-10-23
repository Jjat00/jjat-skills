# SCRIPT — bases-vectoriales-explicado

**Voice:** ElevenLabs `4GeB1bS2GAHAsGRM0eeU` (juvenil latina), `eleven_v4`, `language_code: es`
**Voice settings:** stability 0.5 · speed 1.08 (medir la toma y ajustar con rubberband si pasa de 2:35)
**Voice direction:** Divulgador joven y curioso, ritmo ágil de reel, sin sonar a anuncio. Remata cada idea clave con una mini pausa. Una sola toma; luego se corta por escena.

Datos: `assets/data/datos.json` (BAAI/bge-m3, 1024 dimensiones; benchmark con hnswlib en CPU).

---

## Line 1 — Portada
    [curious, engaging explainer] Bases de datos vectoriales, explicadas rápido.

## Line 2 — Lo usas a diario
    Spotify te recomienda una canción que no conocías. Buscas una foto escribiendo «playa al atardecer». Y un chatbot responde con los documentos de tu empresa.

## Line 3 — La pregunta
    ¿Cómo encuentra una computadora cosas parecidas… y no solo iguales?

## Line 4 — La base de siempre
    Una base de datos normal guarda filas y columnas, y busca coincidencias exactas.

## Line 5 — El problema
    Si buscas «tenis para correr bajo la lluvia», te devuelve… tenis de mesa. Es lo único que dice «tenis».

## Line 6 — La idea clave
    La clave es esta: en vez de comparar palabras, comparamos significados. Y para eso, el significado se convierte en números.

## Line 7 — El embedding
    Un modelo de embeddings lee un texto y lo convierte en un vector: una lista de números. La palabra «perro», por ejemplo, son mil veinticuatro números.

## Line 8 — Un mapa
    Piensa en esos números como coordenadas. Con dos números ubicas una ciudad en el mapa; con mil, ubicas una idea.

## Line 9 — Cerca significa parecido
    Y en ese mapa, lo parecido queda cerca: perro junto a cachorro, carro junto a camión, y factura lejos de los dos.

## Line 10 — Direcciones con sentido
    Hasta las direcciones tienen sentido: rey, menos hombre, más mujer… cae al lado de reina.

## Line 11 — Similitud coseno
    Para medir qué tan cerca están dos ideas se usa la similitud coseno: el ángulo entre dos flechas. Ángulo pequeño, significado parecido.

## Line 12 — La búsqueda
    Ahora la búsqueda: tu pregunta también se convierte en vector, y la base devuelve sus vecinos más cercanos.

## Line 13 — El resultado
    Con «tenis para correr bajo la lluvia», el primero es «zapatillas impermeables para trotar». Sin compartir ni una palabra.

## Line 14 — Eso es una base vectorial
    Una base de datos vectorial es justo eso: guarda millones de vectores y encuentra los más cercanos a uno nuevo, en milisegundos.

## Line 15 — Fuerza bruta
    Lo ingenuo sería comparar contra todos, uno por uno. En mi prueba, con doscientos mil vectores, eso tarda dieciséis milisegundos por consulta. Con mil millones, más de un minuto.

## Line 16 — Búsqueda aproximada
    Por eso usan búsqueda aproximada: sacrifican un poquito de exactitud a cambio de muchísima velocidad.

## Line 17 — HNSW
    El índice más popular se llama HNSW. Es un grafo por pisos, como autopistas y calles: arriba saltas lejos, abajo te acercas despacio, hasta llegar al vecino.

## Line 18 — Barrios
    Otra técnica divide el espacio en barrios y solo busca en los más cercanos a tu pregunta.

## Line 19 — Comprimir
    Y para que todo quepa en memoria, comprimen los vectores: cada número pasa a ocupar menos bits.

## Line 20 — Metadatos
    Además guardan datos normales junto a cada vector, para filtrar: parecido a esto, pero en stock y por menos de cien mil pesos.

## Line 21 — Más que texto
    Y no solo funciona con texto: imágenes, audio y video también se vuelven vectores. Por eso buscas fotos escribiendo lo que quieres ver.

## Line 22 — RAG
    Pero su uso estrella hoy es RAG: cortas los documentos de tu empresa en pedazos, guardas sus vectores, y cuando alguien pregunta, recuperas los pedazos más cercanos y se los das al modelo de lenguaje para que responda con ellos.

## Line 23 — Las herramientas
    Algunas son Pinecone, Qdrant, Weaviate, Milvus o Chroma. Y si ya usas Postgres, la extensión pgvector lo convierte en una.

## Line 24 — La idea central
    Pero la idea central no cambia: convertir cosas en vectores, ponerlas en un mapa y buscar a los vecinos.

## Line 25 — Cierre
**Delivery:** Más lento.

    Tú escribes una pregunta. La base ve mil números… y encuentra lo que significa lo mismo.

## Line 26 — Firma
    Eso es una base de datos vectorial.
