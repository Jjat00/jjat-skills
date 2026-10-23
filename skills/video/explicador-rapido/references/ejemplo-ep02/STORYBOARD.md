---
format: 1080x1920
duration: 157.5s
message: "Una base de datos vectorial no busca palabras iguales: busca significados cercanos, porque convierte todo en puntos de un mapa y encuentra a los vecinos"
arc: Gancho cotidiano → falla de la búsqueda exacta → idea clave (significado = números) → mapa de vectores → búsqueda por vecinos → cómo se hace rápido (aproximada, HNSW, barrios, compresión, filtros) → usos (multimodal, RAG) → herramientas → idea central → cierre
audience: público general curioso de tecnología y estudiantes de software en Latinoamérica
mode: collaborative
music: none
---

# STORYBOARD — Bases de datos vectoriales, explicadas rápido

Convenciones comunes: ver `frame.md` (estilo base: negro, pastel, TODO esquinado salvo partículas de la red) y los
dos frames de referencia ya aprobados `compositions/frames/e09-cerca.html` y `compositions/frames/e13-resultado.html`
(estructura, HUD, kicker, specimen-frame con esquinas de mira, línea de metadatos mono, barras segmentadas, red de
partículas). Los tiempos `palabra@seg` del campo `words` son el instante en que la voz dice esa palabra, relativos al
inicio de la escena. Datos reales en `assets/data/datos.json`, `datos2.json`, `datos3.json` y `mapa.json`
(modelo BAAI/bge-m3, 1024 dimensiones; CLIP ViT-B/32; hnswlib). Lo ilustrativo se marca así en la línea de metadatos.

## Video direction

- Laboratorio de datos en vertical: una idea por escena, un foco grande entre y=220 y y=1440, subtítulos en 1470-1700.
- Ritmo: cada revelación cae en su palabra; nada quieto más de ~1,5 s (deriva de partículas, cámara lenta 1→1.04).
- Continuidad visual: la consulta «tenis para correr bajo la lluvia» (escenas 5, 12, 13, 25) siempre en el mismo
  recuadro de consulta cian de la escena 13; el vector de «perro» siempre como pared de números mono; el mapa siempre
  con la cuadrícula de la escena 9.
- Colores por rol: cian = consulta / lo correcto / cerca; lavanda = segunda clase; rosa = lo que falla / lejos;
  durazno = metadatos y advertencias; menta = confirmación (stock, ✓).
- HUD superior: solo la etapa a la derecha (mono, tenue); nada a la izquierda.

## Frame 1 — Portada

- status: animated
- scene: Portada: BASES DE DATOS / VECTORIALES en Anton gigante, «VECTORIALES» con degradado; detrás, una columna de números reales del vector de «perro» que sube tenue; mono «explicado rápido · ep/02».
- duration: 2.573s
- transition_in: crossfade
- voiceover: "Bases de datos vectoriales, explicadas rápido."
- src: compositions/frames/e01-portada.html
- kind: cover
- blueprint: compose
- words: Bases@0.01 de@0.28 datos@0.40 vectoriales,@0.69 explicadas@1.52 rápido.@2.02

Sin medios. «BASES DE DATOS» (Anton, fg) y «VECTORIALES» (Anton, degradado cian→lavanda) entran por líneas con
máscara de abajo hacia arriba @Bases y @vectoriales; debajo mono «explicado rápido · ep/02». Detrás (opacidad .15) dos
columnas de números mono con los primeros 40 valores reales de `datos2.json → perro_1024`, deslizándose hacia arriba
lentamente. Un recuadro de mira (4 esquinas cian) se cierra alrededor del título @rápido. Red de partículas más densa.

## Frame 2 — Lo usas a diario

- status: animated
- scene: Tres UIs simuladas en ráfaga dentro del mismo specimen-frame: app de música con «recomendado para ti», galería del celular buscando «playa al atardecer» con fotos reales, y un chat de empresa que responde citando un documento.
- duration: 7.418s
- transition_in: cut
- voiceover: "Spotify te recomienda una canción que no conocías. Buscas una foto escribiendo «playa al atardecer». Y un chatbot responde con los documentos de tu empresa."
- src: compositions/frames/e02-a-diario.html
- kind: montage
- blueprint: compose
- words: Spotify@0.15 te@0.27 recomienda@0.42 una@1.07 canción@1.17 que@1.66 no@1.77 conocías.@1.89 Buscas@2.85 una@2.99 foto@3.17 escribiendo@3.42 «playa@4.11 al@4.44 atardecer».@4.54 Y@5.16 un@5.25 chatbot@5.34 responde@5.64 con@6.03 los@6.26 documentos@6.33 de@6.85 tu@6.93 empresa.@6.97

Medios: `assets/media/playa-cabo-de-la-vela.jpg`, `playa-paraiso.jpg`, `playa-la-caleta.jpg`. Specimen-frame grande
(65,230,950×1150). SIN logos ni nombres de marcas en pantalla (la voz dice Spotify; la UI es genérica).
@Spotify: UI de música mono/Poppins: cabecera «RECOMENDADO PARA TI», 4 filas de canción (cuadrado de color pastel como
portada, título inventado y artista inventado), la primera con etiqueta cian «nueva para ti». Kicker «LO USAS A DIARIO».
@Buscas: transición dura a UI de galería: barra de búsqueda que escribe «playa al atardecer» (steps) y una cuadrícula
2×2 donde entran las 3 fotos de playa reales + 1 celda vacía tenue. @chatbot: UI de chat: burbuja RECTANGULAR del
usuario «¿Cuántos días de vacaciones tengo?» y respuesta del asistente «15 días hábiles por año trabajado.» con un chip
mono durazno «fuente: manual.pdf · trozo 2». Metadatos: «ui simulada · fotos: Wikimedia Commons».

## Frame 3 — La pregunta

- status: animated
- scene: Dos tarjetas: IGUAL («perro» = «perro», ✓ menta) y PARECIDO («perro» ≈ «cachorro», «?» lavanda grande); la segunda crece.
- duration: 3.795s
- transition_in: cut
- voiceover: "¿Cómo encuentra una computadora cosas parecidas… y no solo iguales?"
- src: compositions/frames/e03-pregunta.html
- kind: question
- blueprint: compose
- words: ¿Cómo@0.00 encuentra@0.45 una@0.95 computadora@1.12 cosas@1.74 parecidas…@2.05 y@2.58 no@2.72 solo@2.88 iguales?@3.30

Sin medios. Dos tarjetas rectangulares apiladas (surface, hairline). Tarjeta PARECIDO (arriba) @parecidas:
rótulo mono «PARECIDO», dentro «perro» ≈ «cachorro» (el ≈ en JetBrains Mono, no en Anton) y un «?» Anton enorme lavanda
a la derecha que entra con escala. Tarjeta IGUAL (abajo) @iguales: rótulo mono «IGUAL», dentro «perro» = «perro» en
Poppins 600 y un cuadrito menta con ✓; entra más pequeña y tenue, y la tarjeta PARECIDO crece (scale 1.06) con un
cursor de mira cuadrado que se posa sobre el «?». Kicker «¿PARECIDO O IGUAL?» desde el inicio.

## Frame 4 — La base de siempre

- status: animated
- scene: Tabla SQL de productos (id, nombre, precio, stock) que se dibuja fila a fila; una consulta WHERE nombre = 'tenis de mesa profesional' resalta una única fila exacta.
- duration: 4.113s
- transition_in: cut
- voiceover: "Una base de datos normal guarda filas y columnas, y busca coincidencias exactas."
- src: compositions/frames/e04-base-normal.html
- kind: table
- blueprint: compose
- words: Una@0.00 base@0.26 de@0.44 datos@0.56 normal@0.89 guarda@1.26 filas@1.64 y@1.95 columnas,@2.01 y@2.58 busca@2.64 coincidencias@2.97 exactas.@3.60

Sin medios. Tabla mono dentro de un panel (surface #111110, hairline): cabecera «productos» y columnas
id · nombre · precio · stock. Filas con los 7 productos de `datos.json → busqueda.resultados[].texto` (orden de la
lista original: zapatillas impermeables para trotar, chaqueta rompevientos para running, zapatos de cuero para oficina,
botas de caucho para niños, tenis de mesa profesional, paraguas plegable negro, licuadora de 600 vatios), precios y stock
de ejemplo en pesos colombianos ($ 189.900, $ 145.000, $ 230.000, $ 79.900, $ 320.000, $ 39.900, $ 159.900; stock 12, 0, 5,
8, 3, 20, 0). @filas las filas se dibujan una a una; @columnas se encienden las cabeceras. Arriba, panel de consulta
que escribe `SELECT * FROM productos WHERE nombre = 'tenis de mesa profesional';` @busca. @exactas: solo esa fila se
resalta con borde cian y un sello mono «1 fila · coincidencia exacta». Metadatos: «precios y stock de ejemplo».

## Frame 5 — El problema

- status: animated
- scene: Recuadro de consulta «tenis para correr bajo la lluvia»; la base busca la palabra «tenis» y devuelve «tenis de mesa profesional»; la palabra «tenis» se ilumina en ambos lados.
- duration: 5.331s
- transition_in: cut
- voiceover: "Si buscas «tenis para correr bajo la lluvia», te devuelve… tenis de mesa. Es lo único que dice «tenis»."
- src: compositions/frames/e05-problema.html
- kind: statement
- blueprint: compose
- words: Si@0.00 buscas@0.22 «tenis@0.49 para@0.76 correr@1.00 bajo@1.36 la@1.59 lluvia»,@1.73 te@2.17 devuelve…@2.29 tenis@2.75 de@3.07 mesa.@3.21 Es@3.65 lo@3.95 único@3.99 que@4.34 dice@4.58 «tenis».@4.86

Sin medios. Arriba, el recuadro de consulta cian (mismo diseño que la escena 13) que escribe
«tenis para correr bajo la lluvia» @tenis..lluvia. Debajo, flecha mono hacia una línea de código
`WHERE nombre LIKE '%tenis%'` (aparece @devuelve). Luego una tarjeta de resultado grande: «tenis de mesa profesional»
en Poppins 600 @mesa, con un dibujo vectorial simple y esquinado de una raqueta de ping-pong (cuadrado + mango
rectangular, trazo rosa). En la consulta y en el resultado, la palabra «tenis» se resalta con fondo rosa al 35 % @«tenis»
(la última palabra). Sello rectangular rosa girado -4° «1 RESULTADO · NO ES LO QUE BUSCABAS» @único.
Kicker «BUSCA PALABRAS, NO IDEAS».

## Frame 6 — La idea clave

- status: animated
- scene: Golpe: «PALABRAS» tachado en rosa, luego «SIGNIFICADOS» con degradado; @números la palabra «perro» se deshace en una columna de números reales.
- duration: 6.364s
- transition_in: crossfade
- voiceover: "La clave es esta: en vez de comparar palabras, comparamos significados. Y para eso, el significado se convierte en números."
- src: compositions/frames/e06-idea-clave.html
- kind: statement
- blueprint: compose
- words: La@0.00 clave@0.33 es@0.62 esta:@0.77 en@1.33 vez@1.44 de@1.60 comparar@1.72 palabras,@2.11 comparamos@2.62 significados.@3.14 Y@3.86 para@4.06 eso,@4.26 el@4.55 significado@4.61 se@5.19 convierte@5.30 en@5.77 números.@5.88

Sin medios. Anton grande centrado: «COMPARAR PALABRAS» (fg) aparece @comparar y una barra rosa la tacha
@palabras(2ª vez, ~1.8s); debajo «COMPARAR SIGNIFICADOS» con «SIGNIFICADOS» en degradado @significados. @números: abajo,
la palabra «perro» en Poppins 600 se desintegra en una columna de 10 números mono (primeros valores de
`datos2.json → perro_1024`) que caen como una lista. Kicker «LA CLAVE».

## Frame 7 — El embedding

- status: animated
- scene: «perro» → caja MODELO DE EMBEDDINGS (bge-m3) → pared de 1024 números reales (32×32 celdas tintadas por signo); contador hasta 1024.
- duration: 7.44s
- transition_in: cut
- voiceover: "Un modelo de embeddings lee un texto y lo convierte en un vector: una lista de números. La palabra «perro», por ejemplo, son mil veinticuatro números."
- src: compositions/frames/e07-embedding.html
- kind: pipeline
- blueprint: compose
- words: Un@-0.00 modelo@0.41 de@0.51 embeddings@0.61 lee@1.16 un@1.32 texto@1.43 y@1.70 lo@1.76 convierte@1.92 en@2.36 un@2.46 vector:@2.57 una@3.15 lista@3.41 de@3.67 números.@3.74 La@4.35 palabra@4.68 «perro»,@4.87 por@5.31 ejemplo,@5.45 son@5.95 mil@6.06 veinticuatro@6.44 números.@6.81

Datos: `datos2.json → perro_1024` (1024 valores reales). Arriba, fila de pipeline: chip texto «perro» → flecha
→ caja «MODELO DE EMBEDDINGS» (mono, borde lavanda, subtítulo «bge-m3») @modelo → flecha → «vector» @vector.
Debajo, pared 32×32 de celdas cuadradas (≈28 px) tintadas: positivo = cian, negativo = rosa, opacidad según |valor|
(normaliza con el máximo absoluto); las celdas aparecen en barrido @lista..números. Encima, una lupa rectangular muestra
los primeros 6 valores en mono grande (-0.060, 0.005, -0.051, 0.002, -0.023, 0.024) @perro. Contador Anton «1024»
con «NÚMEROS» mono @mil veinticuatro (cuenta de 0 a 1024). Metadatos: «modelo: bge-m3 · vector real de "perro" · 1024
dimensiones».

## Frame 8 — Un mapa

- status: animated
- scene: Arriba un mapa esquemático con Bogotá ubicada por 2 números (4.711, -74.072); abajo «perro» ubicado por 1024 números; ecuación 2 → 1024.
- duration: 5.985s
- transition_in: cut
- voiceover: "Piensa en esos números como coordenadas. Con dos números ubicas una ciudad en el mapa; con mil, ubicas una idea."
- src: compositions/frames/e08-coordenadas.html
- kind: analogy
- blueprint: compose
- words: Piensa@0.00 en@0.40 esos@0.43 números@0.66 como@1.05 coordenadas.@1.32 Con@2.10 dos@2.34 números@2.44 ubicas@2.90 una@3.26 ciudad@3.38 en@3.71 el@3.85 mapa;@3.93 con@4.35 mil,@4.65 ubicas@4.92 una@5.30 idea.@5.57

Sin medios. Dos paneles apilados. Panel 1 (@coordenadas / @ciudad): cuadrícula tipo mapa con un marcador
cuadrado cian y la etiqueta «Bogotá», y dos chips mono «lat 4.711» «lon -74.072» que llegan a los ejes. Contador
mono «2 números». Panel 2 (@mil / @idea): la misma cuadrícula pero con un marcador lavanda «perro» y una tira de números
mono que se desborda por la derecha (valores de `perro_1024`), contador «1024 números». Entre ambos, Anton grande
«2 → 1024». Kicker «NÚMEROS = COORDENADAS». Metadatos: «coordenadas reales de Bogotá · vector real de bge-m3».

## Frame 9 — Cerca significa parecido

- status: animated
- scene: Mapa 2D real (t-SNE de bge-m3) con 20 palabras en 4 grupos; se trazan perro↔cachorro, carro↔camión y perro↔factura con sus similitudes reales.
- duration: 6.169s
- transition_in: cut
- voiceover: "Y en ese mapa, lo parecido queda cerca: perro junto a cachorro, carro junto a camión, y factura lejos de los dos."
- src: compositions/frames/e09-cerca.html
- kind: data-viz
- blueprint: compose
- words: Y@-0.00 en@0.14 ese@0.27 mapa,@0.38 lo@0.74 parecido@0.91 queda@1.36 cerca:@1.78 perro@2.44 junto@2.47 a@2.75 cachorro,@2.83 carro@3.65 junto@3.72 a@4.00 camión,@4.05 y@4.49 factura@4.78 lejos@5.08 de@5.41 los@5.54 dos.@5.74

YA CONSTRUIDO Y APROBADO (`tools/gen_estilo.py`). No se reconstruye.

## Frame 10 — Direcciones con sentido

- status: animated
- scene: Aritmética de vectores con flechas: rey − hombre + mujer → cae junto a reina; ranking real de los candidatos.
- duration: 4.863s
- transition_in: cut
- voiceover: "Hasta las direcciones tienen sentido: rey, menos hombre, más mujer… cae al lado de reina."
- src: compositions/frames/e10-analogia.html
- kind: data-viz
- blueprint: compose
- words: Hasta@0.02 las@0.28 direcciones@0.41 tienen@0.94 sentido:@1.16 rey,@1.85 menos@2.12 hombre,@2.49 más@2.96 mujer…@3.19 cae@3.61 al@3.85 lado@3.92 de@4.17 reina.@4.30

Datos: `datos.json → analogia` (reina 0.687, princesa 0.531, señora 0.53, monarca 0.369, príncipe 0.282).
Panel con cuadrícula (estilo escena 9). Flechas esquinadas (líneas SVG con punta triangular, sin redondeo) en 2D
ILUSTRATIVO: @rey aparece el punto «rey»; @menos hombre se dibuja una flecha rosa restando (rey → rey−hombre); @más mujer
una flecha cian sumando; el punto resultado «?» cae @cae y @reina se ilumina el punto «reina» a su lado con un recuadro de
mira. Ecuación mono arriba que se escribe con la voz: «rey − hombre + mujer ≈ ». Debajo del panel, 5 barras segmentadas
con el ranking real (reina en cian, el resto tenue) @reina. Kicker «LAS DIRECCIONES TAMBIÉN SIGNIFICAN».
Metadatos: «similitudes reales bge-m3 · posiciones 2D ilustrativas».

## Frame 11 — Similitud coseno

- status: animated
- scene: Dos flechas desde el origen: perro→cachorro con ángulo de 35,7° (similitud 0,81) y luego perro→factura con 64,1° (0,44); fórmula del coseno.
- duration: 6.973s
- transition_in: cut
- voiceover: "Para medir qué tan cerca están dos ideas se usa la similitud coseno: el ángulo entre dos flechas. Ángulo pequeño, significado parecido."
- src: compositions/frames/e11-coseno.html
- kind: diagram
- blueprint: compose
- words: Para@0.00 medir@0.26 qué@0.52 tan@0.66 cerca@0.83 están@1.17 dos@1.40 ideas@1.56 se@2.00 usa@2.11 la@2.29 similitud@2.40 coseno:@2.97 el@3.50 ángulo@3.67 entre@3.94 dos@4.22 flechas.@4.39 Ángulo@5.22 pequeño,@5.30 significado@5.77 parecido.@6.36

Datos: `datos2.json → angulos` (perro-cachorro 0.812 / 35.7°, perro-factura 0.437 / 64.1°). Panel cuadrado
con origen abajo-izquierda. @flechas: flecha «perro» (cian) y flecha «cachorro» (cian claro) separadas 35.7° reales, con
arco y etiqueta «35,7°»; chip «cos = 0,81». @pequeño: el ángulo se marca menta «parecido». Tras @parecido se añade la flecha «factura» (rosa) a 64.1° del perro, arco rosa «64,1°», chip «cos = 0,44» y etiqueta
«distinto». Arriba, fórmula mono `cos θ = A·B / (|A| |B|)` @coseno. Kicker «EL ÁNGULO MIDE EL PARECIDO».
Metadatos: «ángulos reales entre vectores de 1024 dims · dibujados en 2D».

## Frame 12 — La búsqueda

- status: animated
- scene: La consulta se vuelve un punto cian en el mapa; un radio cuadrado se expande y atrapa a los 3 vecinos más cercanos entre los 7 productos.
- duration: 5.384s
- transition_in: cut
- voiceover: "Ahora la búsqueda: tu pregunta también se convierte en vector, y la base devuelve sus vecinos más cercanos."
- src: compositions/frames/e12-busqueda.html
- kind: data-viz
- blueprint: compose
- words: Ahora@-0.00 la@0.31 búsqueda:@0.41 tu@1.09 pregunta@1.31 también@1.60 se@1.95 convierte@2.05 en@2.50 vector,@2.59 y@3.07 la@3.19 base@3.31 devuelve@3.49 sus@3.94 vecinos@4.12 más@4.53 cercanos.@4.82

Datos: `datos.json → busqueda.resultados` (7 productos con su similitud real). Arriba, el recuadro de consulta
cian (como en 13) con «tenis para correr bajo la lluvia» ya escrito; @vector se le pega el chip «→ vector [1024]».
Debajo, panel-mapa con cuadrícula: el punto consulta (cuadrado cian con halo) en el centro; los 7 productos como cuadrados
con etiqueta mono, a distancia del centro proporcional a (1 − similitud) real y ángulos repartidos (ILUSTRATIVOS).
@vecinos un cuadrado de búsqueda (borde cian discontinuo) crece desde la consulta y los 3 más cercanos se iluminan con
líneas hacia el centro y etiquetas k=1, k=2, k=3 @cercanos. Kicker «BUSCAR VECINOS». Metadatos: «distancia = 1 −
similitud real · ángulos ilustrativos».

## Frame 13 — El resultado

- status: animated
- scene: Consulta, búsqueda exacta SQL tachada y top 7 por similitud coseno real; «zapatillas impermeables para trotar» primero; 0 palabras clave en común.
- duration: 6.037s
- transition_in: cut
- voiceover: "Con «tenis para correr bajo la lluvia», el primero es «zapatillas impermeables para trotar». Sin compartir ni una palabra."
- src: compositions/frames/e13-resultado.html
- kind: ranking
- blueprint: compose
- words: Con@-0.00 «tenis@0.27 para@0.47 correr@0.71 bajo@1.06 la@1.30 lluvia»,@1.41 el@1.96 primero@2.01 es@2.40 «zapatillas@2.54 impermeables@3.12 para@3.76 trotar».@3.93 Sin@4.65 compartir@4.66 ni@5.20 una@5.31 palabra.@5.57

YA CONSTRUIDO Y APROBADO (`tools/gen_estilo.py`). No se reconstruye.

## Frame 14 — Eso es una base vectorial

- status: animated
- scene: Título BASE DE DATOS VECTORIAL; diagrama: filas de vectores (id · vector · metadatos) que se apilan con contador hasta «millones»; una consulta entra y salen los k más cercanos con un cronómetro en milisegundos.
- duration: 6.875s
- transition_in: crossfade
- voiceover: "Una base de datos vectorial es justo eso: guarda millones de vectores y encuentra los más cercanos a uno nuevo, en milisegundos."
- src: compositions/frames/e14-definicion.html
- kind: definition
- blueprint: compose
- words: Una@-0.00 base@0.36 de@0.52 datos@0.64 vectorial@1.00 es@1.53 justo@1.65 eso:@1.97 guarda@2.41 millones@2.70 de@3.12 vectores@3.21 y@3.61 encuentra@3.65 los@4.11 más@4.26 cercanos@4.41 a@4.93 uno@5.25 nuevo,@5.30 en@5.75 milisegundos.@5.89

Sin medios. Anton «BASE DE DATOS VECTORIAL» con «VECTORIAL» en degradado @vectorial(1ª). Debajo, panel
«colección» con filas mono: `id · [0.04, -0.12, … ×1024] · {categoría, precio}`; @guarda las filas se apilan rápido y
un contador mono sube 0 → «12.000.000 vectores» (ILUSTRATIVO) @millones. @encuentra: una flecha cian trae un vector
consulta desde la izquierda y salen 3 filas resaltadas «top-3»; @milisegundos un cronómetro mono «≈ ms». Kicker
«LA DEFINICIÓN». Metadatos: «diagrama ilustrativo».

## Frame 15 — Fuerza bruta

- status: animated
- scene: La consulta se compara contra una rejilla enorme de vectores, uno por uno (barrido); cronómetro real 16 ms con 200.000 vectores; luego la barra de mil millones: ≈ 79 s.
- duration: 9.312s
- transition_in: cut
- voiceover: "Lo ingenuo sería comparar contra todos, uno por uno. En mi prueba, con doscientos mil vectores, eso tarda dieciséis milisegundos por consulta. Con mil millones, más de un minuto."
- src: compositions/frames/e15-fuerza-bruta.html
- kind: stat
- blueprint: compose
- words: Lo@0.00 ingenuo@0.20 sería@0.53 comparar@0.83 contra@1.28 todos,@1.70 uno@2.03 por@2.20 uno.@2.37 En@2.72 mi@2.95 prueba,@2.96 con@3.36 doscientos@3.51 mil@4.03 vectores,@4.54 eso@5.02 tarda@5.22 dieciséis@5.42 milisegundos@5.80 por@6.33 consulta.@6.48 Con@7.36 mil@7.37 millones,@7.56 más@8.28 de@8.42 un@8.55 minuto.@8.69

Datos: `datos.json → velocidad` (n 200000, dims 1024, bruta_ms 15.87). Rejilla de 40×40 cuadraditos (cada uno
«representa 125 vectores») que se barre en orden de lectura con un cursor cian @uno por uno; contador mono
«comparados: 0 → 200.000» @doscientos mil. Cronómetro Anton «16 ms» @dieciséis milisegundos, con mono «por consulta ·
CPU · 1024 dims». @mil millones: debajo, dos barras horizontales segmentadas en escala: «200 mil → 16 ms» (diminuta)
y «1.000 millones → ≈ 79 s» (rosa, ocupa todo) @minuto, con nota mono durazno «extrapolación lineal». Kicker
«COMPARAR CONTRA TODOS». Metadatos: «medido con numpy · vectores sintéticos de 1024 dims».

## Frame 16 — Búsqueda aproximada

- status: animated
- scene: Gráfico real de exactitud vs velocidad de HNSW: seis configuraciones; se destaca 96,5 % de exactitud siendo 11× más rápido que la fuerza bruta.
- duration: 5.6s
- transition_in: cut
- voiceover: "Por eso usan búsqueda aproximada: sacrifican un poquito de exactitud a cambio de muchísima velocidad."
- src: compositions/frames/e16-aproximada.html
- kind: chart
- blueprint: compose
- words: Por@-0.00 eso@0.18 usan@0.45 búsqueda@0.64 aproximada:@1.10 sacrifican@2.00 un@2.40 poquito@2.52 de@2.94 exactitud@3.05 a@3.59 cambio@3.69 de@4.02 muchísima@4.13 velocidad.@4.71

Datos: `datos3.json → hnsw` (ef 10..256: recall 0.568, 0.694, 0.847, 0.965, 1.0, 1.0; acelera 37.7, 28.6, 19.1,
11.4, 6.3, 3.7). Gráfico cuadrado: eje X «más rápido →» (veces más rápido que fuerza bruta, 0-40), eje Y «exactitud»
(50-100 %). Seis marcadores cuadrados conectados por línea recta (SVG, trazo lavanda) que se dibuja @aproximada.
@exactitud un marcador tenue rosa en (37.7×, 56.8 %); @velocidad el punto ef=64 se resalta cian con recuadro de mira y
callout grande: «96,5 %» Anton + «exactitud» mono y «11×» Anton + «más rápido» mono. Kicker «UN POCO MENOS EXACTA,
MUCHO MÁS RÁPIDA». Metadatos: «hnswlib · 200.000 vectores sintéticos · k = 10».

## Frame 17 — HNSW

- status: animated
- scene: Grafo de 3 pisos (autopistas arriba, calles abajo) en perspectiva plana; una ruta cian salta lejos arriba y baja piso por piso hasta el vecino.
- duration: 9.687s
- transition_in: cut
- voiceover: "El índice más popular se llama HNSW. Es un grafo por pisos, como autopistas y calles: arriba saltas lejos, abajo te acercas despacio, hasta llegar al vecino."
- src: compositions/frames/e17-hnsw.html
- kind: diagram
- blueprint: compose
- words: El@0.09 índice@0.11 más@0.73 popular@1.03 se@1.78 llama@1.96 HNSW.@2.47 Es@3.23 un@3.41 grafo@3.44 por@3.70 pisos,@3.86 como@4.23 autopistas@4.45 y@5.00 calles:@5.10 arriba@5.79 saltas@6.00 lejos,@6.43 abajo@7.11 te@7.22 acercas@7.38 despacio,@7.75 hasta@8.30 llegar@8.63 al@8.94 vecino.@9.05

Sin medios, ILUSTRATIVO. Tres planos rectangulares apilados (cada uno un panel con hairline, con leve
desplazamiento en x para dar profundidad, SIN rotaciones 3D redondeadas): PISO 2 con 4 nodos y aristas largas, PISO 1
con 10 nodos, PISO 0 con 30 nodos y aristas cortas. Nodos = cuadrados. @HNSW el título «HNSW» Anton con mono
«Hierarchical Navigable Small World». @pisos aparecen los pisos de arriba abajo. @autopistas el piso 2 se ilumina
(rótulo «autopistas»); @calles el piso 0 («calles»). @arriba la ruta cian hace 2 saltos largos en el piso 2; @abajo
baja con líneas verticales discontinuas al piso 1 y 0 y hace saltos cortos; @vecino llega al nodo destino (cuadrado
menta con recuadro de mira). Contador mono «nodos visitados: 9 de 44». Kicker «AUTOPISTAS Y CALLES».

## Frame 18 — Barrios

- status: animated
- scene: 160 puntos agrupados en 6 barrios con k-means real; la consulta cae en el mapa y solo se revisan los 2 barrios más cercanos (58 de 160 puntos).
- duration: 4.025s
- transition_in: cut
- voiceover: "Otra técnica divide el espacio en barrios y solo busca en los más cercanos a tu pregunta."
- src: compositions/frames/e18-barrios.html
- kind: data-viz
- blueprint: compose
- words: Otra@0.08 técnica@0.34 divide@1.00 el@1.20 espacio@1.28 en@1.59 barrios@1.67 y@1.98 solo@2.03 busca@2.27 en@2.57 los@2.78 más@2.82 cercanos@2.97 a@3.39 tu@3.43 pregunta.@3.57

Datos: `datos3.json → barrios` (puntos con su barrio b, 6 centros, consulta (0.62, 0.41), barrios_buscados
[3, 5], revisados 58 de 160). Panel cuadrado con cuadrícula. @espacio los puntos (cuadraditos de 10 px) aparecen grises;
@barrios se colorean por barrio con 6 colores pastel y aparecen los centros como cuadrados grandes con borde.
@pregunta la consulta (cuadrado cian con halo) cae; @cercanos se resaltan los barrios 3 y 5 y el resto baja a 25 %.
Contador mono «revisados: 58 de 160» Anton. Kicker «BUSCAR SOLO EN TU BARRIO». Metadatos: «k-means real (6 centros) ·
puntos 2D ilustrativos · técnica IVF».

## Frame 19 — Comprimir

- status: animated
- scene: El vector de «perro» en tres formatos: float32 (4096 bytes), int8 (1024) y binario (128); barras de tamaño y similitud con el original 0,9998.
- duration: 4.858s
- transition_in: cut
- voiceover: "Y para que todo quepa en memoria, comprimen los vectores: cada número pasa a ocupar menos bits."
- src: compositions/frames/e19-comprimir.html
- kind: data-grid
- blueprint: compose
- words: Y@-0.00 para@0.14 que@0.29 todo@0.45 quepa@0.64 en@0.89 memoria,@1.01 comprimen@1.50 los@1.93 vectores:@2.07 cada@2.83 número@2.94 pasa@3.28 a@3.54 ocupar@3.61 menos@3.98 bits.@4.34

Datos: `datos2.json → cuantizacion` (primeros_float, primeros_int8, primeros_bin, bytes 4096/1024/128,
sim_original_vs_int8 0.9998, mil_millones_gb 4096/1024/128). Tres filas tipo data-grid con los primeros 8 valores:
FLOAT32 (fg) @memoria, INT8 (lavanda) @comprimen, BINARIO (cian, 0/1) @bits. A la derecha de cada fila una barra
segmentada de tamaño con «4.096 B», «1.024 B», «128 B». @menos bits: callout mono «int8 conserva 0,9998 de
similitud». Abajo: «mil millones de vectores: 4 TB → 1 TB → 128 GB» en mono grande. Kicker «MENOS BITS POR NÚMERO».
Metadatos: «cuantización real del vector de "perro" (bge-m3)».

## Frame 20 — Metadatos

- status: animated
- scene: Tabla de los productos con similitud real + stock + precio; se activan los filtros «en stock» y «< $ 100.000» y solo sobreviven las filas que cumplen.
- duration: 6.192s
- transition_in: cut
- voiceover: "Además guardan datos normales junto a cada vector, para filtrar: parecido a esto, pero en stock y por menos de cien mil pesos."
- src: compositions/frames/e20-metadatos.html
- kind: table
- blueprint: compose
- words: Además@0.09 guardan@0.37 datos@0.76 normales@1.05 junto@1.60 a@1.79 cada@1.84 vector,@2.07 para@2.48 filtrar:@2.79 parecido@3.31 a@3.49 esto,@3.57 pero@3.81 en@3.99 stock@4.08 y@4.31 por@4.36 menos@4.50 de@4.68 cien@4.82 mil@5.28 pesos.@5.75

Datos: similitudes de `datos.json → busqueda.resultados`; precios y stock de ejemplo (los mismos de la
escena 4: zapatillas $ 189.900/12, chaqueta $ 145.000/0, zapatos $ 230.000/5, botas $ 79.900/8, tenis de mesa
$ 320.000/3, paraguas $ 39.900/20, licuadora $ 159.900/0). Tabla mono: producto · similitud (barra segmentada mini) ·
stock · precio. @datos normales se encienden las columnas stock y precio (durazno). @filtrar: dos chips rectangulares de
filtro que se activan: «en stock» @stock (filas con stock 0 se tachan rosa y bajan a 30 %) y «< $ 100.000» @cien mil
(filas caras se tachan). Quedan botas de caucho (0.48) y paraguas plegable (0.47) con borde menta; sello «2 resultados».
Kicker «PARECIDO + FILTROS». Metadatos: «similitudes reales · precios y stock de ejemplo».

## Frame 21 — Más que texto

- status: animated
- scene: Cuatro chips (texto, imagen, audio, video) se vuelven vectores; luego búsqueda real con CLIP: «playa al atardecer» sobre 27 fotos, las playas reales arriba.
- duration: 7.118s
- transition_in: cut
- voiceover: "Y no solo funciona con texto: imágenes, audio y video también se vuelven vectores. Por eso buscas fotos escribiendo lo que quieres ver."
- src: compositions/frames/e21-multimodal.html
- kind: mosaic
- blueprint: compose
- words: Y@-0.00 no@0.09 solo@0.18 funciona@0.45 con@0.89 texto:@1.10 imágenes,@1.76 audio@2.17 y@2.47 video@2.55 también@2.82 se@3.28 vuelven@3.37 vectores.@3.78 Por@4.52 eso@4.70 buscas@4.97 fotos@5.22 escribiendo@5.48 lo@6.03 que@6.21 quieres@6.30 ver.@6.64

Datos: `datos2.json → fotos` (27 fotos, ranking real CLIP: playa-paraiso 0.259, playa-cabo-de-la-vela 0.258,
etiquetadas/21-osito 0.245, playa-la-caleta 0.238, ...). Arriba, fila de 4 chips rectangulares mono «texto»
«imagen» «audio» «video» que @texto, @imágenes, @audio, @video emiten cada uno una mini tira de números (vector) que
vuela hacia una caja «mismo espacio». @fotos: mosaico 6×5 con las 27 fotos (object-fit cover, celdas cuadradas) +
recuadro de consulta cian «playa al atardecer» encima. @quieres ver: las fotos se reordenan por similitud (posiciones
finales según el ranking real) y las 4 primeras quedan con borde cian y su similitud en chip mono; el osito en la arena
(3.º) se queda con su valor, es real. Kicker «IMÁGENES, AUDIO Y VIDEO TAMBIÉN». Metadatos: «CLIP ViT-B/32 multilingüe
· similitud real · fotos Pexels y Wikimedia Commons».

## Frame 22 — RAG

- status: animated
- scene: Pipeline RAG: documento → 8 trozos → vectores en la base; pregunta «¿Cuántos días de vacaciones tengo al año?» → recupera los 2 trozos más cercanos (0,70 y 0,60) → modelo de lenguaje → respuesta citada.
- duration: 11.17s
- transition_in: cut
- voiceover: "Pero su uso estrella hoy es RAG: cortas los documentos de tu empresa en pedazos, guardas sus vectores, y cuando alguien pregunta, recuperas los pedazos más cercanos y se los das al modelo de lenguaje para que responda con ellos."
- src: compositions/frames/e22-rag.html
- kind: pipeline
- blueprint: compose
- words: Pero@0.09 su@0.21 uso@0.36 estrella@0.59 hoy@1.20 es@1.43 RAG:@1.60 cortas@2.25 los@2.39 documentos@2.56 de@3.16 tu@3.22 empresa@3.32 en@3.76 pedazos,@3.83 guardas@4.54 sus@4.73 vectores,@4.93 y@5.46 cuando@5.47 alguien@5.79 pregunta,@6.16 recuperas@6.69 los@7.25 pedazos@7.39 más@7.69 cercanos@7.85 y@8.31 se@8.40 los@8.49 das@8.63 al@8.79 modelo@8.89 de@9.20 lenguaje@9.32 para@9.74 que@10.01 responda@10.11 con@10.53 ellos.@10.69

Datos: `datos2.json → rag` (pregunta y 8 trozos con su similitud real; el 1.º «Vacaciones: cada empleado tiene
15 días hábiles…» 0.699, el 2.º «Las vacaciones se solicitan…» 0.602). Arriba Anton «RAG» con mono «Retrieval-Augmented
Generation» @RAG. Fila 1 @documentos: icono de documento rectangular «manual.pdf» que @pedazos se corta en 8 tarjetas
pequeñas (texto truncado mono). @vectores cada tarjeta gana una mini tira de color (vector) y entra a la caja «base
vectorial». Fila 2 @pregunta: recuadro de consulta cian con la pregunta. @recuperas: de la base salen las 2 tarjetas
ganadoras grandes con su similitud (0,70 y 0,60) y la línea de texto completa legible. @modelo: caja «modelo de lenguaje»
(lavanda). @responda: burbuja rectangular de respuesta «Tienes 15 días hábiles por cada año trabajado.» con chip
durazno «fuente: trozo 2». Kicker «RECUPERAR + GENERAR». Metadatos: «similitudes reales bge-m3 · manual de ejemplo».

## Frame 23 — Las herramientas

- status: animated
- scene: Cinco tarjetas de nombres (Pinecone, Qdrant, Weaviate, Milvus, Chroma) con su tipo; luego Postgres + pgvector con código SQL real.
- duration: 7.789s
- transition_in: cut
- voiceover: "Algunas son Pinecone, Qdrant, Weaviate, Milvus o Chroma. Y si ya usas Postgres, la extensión pgvector lo convierte en una."
- src: compositions/frames/e23-herramientas.html
- kind: list
- blueprint: compose
- words: Algunas@0.15 son@0.46 Pinecone,@0.67 Qdrant,@1.38 Weaviate,@1.91 Milvus@2.64 o@3.07 Chroma.@3.14 Y@3.85 si@3.94 ya@4.04 usas@4.17 Postgres,@4.44 la@5.10 extensión@5.23 pgvector@5.79 lo@6.35 convierte@6.48 en@7.08 una.@7.21

Sin logos ni colores de marca (solo nombres en texto). Cinco tarjetas rectangulares que entran una por una con su
nombre: Pinecone @Pinecone «servicio administrado», Qdrant @Qdrant «código abierto», Weaviate @Weaviate «código abierto»,
Milvus @Milvus «código abierto», Chroma @Chroma «código abierto». @Postgres un panel de código grande: título
«Postgres + pgvector» y el código real, escrito línea a línea:
`CREATE EXTENSION vector;` / `CREATE TABLE productos (id bigserial, embedding vector(1024));` /
`SELECT * FROM productos ORDER BY embedding <=> $1 LIMIT 5;` con `<=>` resaltado cian y comentario mono «-- distancia
coseno». Kicker «¿CON QUÉ SE HACE?». Metadatos: «a octubre de 2026».

## Frame 24 — La idea central

- status: animated
- scene: Tres tarjetas numeradas 01 vectores · 02 mapa · 03 vecinos que se encienden con la voz.
- duration: 5.45s
- transition_in: crossfade
- voiceover: "Pero la idea central no cambia: convertir cosas en vectores, ponerlas en un mapa y buscar a los vecinos."
- src: compositions/frames/e24-idea-central.html
- kind: recap
- blueprint: compose
- words: Pero@0.09 la@0.14 idea@0.25 central@0.48 no@0.88 cambia:@1.01 convertir@1.72 cosas@2.10 en@2.40 vectores,@2.52 ponerlas@3.23 en@3.63 un@3.75 mapa@3.88 y@4.13 buscar@4.19 a@4.57 los@4.62 vecinos.@4.83

Sin medios. Tres tarjetas rectangulares grandes numeradas 01 · 02 · 03 (Anton para el número, mono para el
rótulo), cada una con una mini ilustración: 01 «convertir en vectores» (palabra → mini tira de números) @vectores;
02 «ponerlas en un mapa» (mini cuadrícula con 6 cuadraditos) @mapa; 03 «buscar a los vecinos» (punto cian con 3 líneas a
vecinos) @vecinos. Las anteriores quedan encendidas. Kicker «LA IDEA CENTRAL».

## Frame 25 — Cierre

- status: animated
- scene: Se escribe una pregunta; se convierte en una pared de mil números que gira hacia el resultado: la tarjeta con lo que significa lo mismo.
- duration: 4.66s
- transition_in: cut
- voiceover: "Tú escribes una pregunta. La base ve mil números… y encuentra lo que significa lo mismo."
- src: compositions/frames/e25-cierre.html
- kind: finale
- blueprint: compose
- words: Tú@-0.00 escribes@0.18 una@0.57 pregunta.@0.69 La@1.31 base@1.49 ve@1.69 mil@1.81 números…@1.99 y@2.44 encuentra@2.51 lo@3.08 que@3.20 significa@3.39 lo@3.96 mismo.@4.20

Datos: `datos2.json → perro_1024` para la pared (no se nombra). @escribes: recuadro de consulta cian que escribe
«tenis para correr bajo la lluvia». @mil números: la consulta se disuelve en una pared de 32×32 números mono diminutos
(tintados como en la escena 7) y un contador «1024». @encuentra: la pared se contrae a un punto y aparece la tarjeta
resultado «zapatillas impermeables para trotar» con chip «0,63» @mismo y Anton «MISMO SIGNIFICADO» (degradado en
SIGNIFICADO). Ritmo más lento, cámara 1→1.05. Kicker «DE PALABRAS A SIGNIFICADO».

## Frame 26 — Firma

- status: animated
- scene: Firma: BASES DE DATOS VECTORIALES en Anton con degradado, red de partículas, «tu marca · explicado rápido · ep/02».
- duration: 2.311s
- transition_in: crossfade
- voiceover: "Eso es una base de datos vectorial."
- src: compositions/frames/e26-firma.html
- kind: closer
- blueprint: compose
- words: Eso@-0.00 es@0.18 una@0.20 base@0.33 de@0.49 datos@0.57 vectorial.@0.76

«BASES DE DATOS» (fg) y «VECTORIALES» (degradado) Anton, entran @base @vectorial; red de partículas densa; mono
«tu marca · explicado rápido · ep/02». Fade a negro final permitido (es el último frame).
