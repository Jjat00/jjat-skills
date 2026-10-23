---
version: alpha
name: Estilo base — laboratorio oscuro (explicadores verticales de software e ingeniería)
description: >
  Estilo de partida de la skill: se adapta a la marca de cada persona (colores, fuentes, esquinas). Lienzo casi
  negro, un solo degradado cian→violeta como voltaje, red de partículas como firma, Anton para
  golpes de titular, Poppins para lectura y JetBrains Mono para la capa de datos (píxeles,
  matrices, probabilidades, etiquetas de modelo). Fotografía y video reales enmarcados como
  "muestras de laboratorio" con esquinas de mira y una línea de metadatos mono. Vertical 9:16.
unit: the frame — 1080×1920 primario (9:16)
principle: los átomos son sagrados · la composición es libre · los números vienen del guion

colors:
  canvas: "#0a0a0a"
  surface: "#111110"
  surface-2: "#161615"
  line: "#232323"
  fg: "#ededed"
  muted: "#a1a09a"
  dim: "#666666"   # solo para líneas y adornos; como texto falla el contraste, usa #8f8f8a
  cyan: "#9fe3f5"
  violet: "#c4b5fd"
  signal-red: "#ffadbb"
  mint: "#b4ecc8"
  blue-pastel: "#a8c5ff"
  signal-amber: "#ffd9a0"

borders: { hairline: "1px solid {colors.line}", hairline-strong: "1px solid #333", cyan: "2px solid {colors.cyan}" }
shadows: { media: "0 30px 80px rgba(0,0,0,0.55)", glow: "0 0 40px rgba(159,227,245,0.25)" }

typography:
  # — capa de lectura —
  body:      { fontFamily: "Poppins", cqw: 3.7, weight: 400, lineHeight: 1.4, color: "muted" }
  lead:      { fontFamily: "Poppins", cqw: 4.6, weight: 600, lineHeight: 1.25, color: "fg" }
  kicker:    { fontFamily: "JetBrains Mono", px: 30, weight: 700, tracking: "0.14em", upper: true, color: "cyan" }
  mono-meta: { fontFamily: "JetBrains Mono", px: 22, weight: 400, tracking: "0.04em", color: "dim" }
  mono-data: { fontFamily: "JetBrains Mono", px: 26, weight: 400, lineHeight: 1.2, color: "fg" }
  # — capa de golpe (Anton, MAYÚSCULAS) —
  headline:  { fontFamily: "Anton", cqw: 11, weight: 400, lineHeight: 0.95, upper: true, color: "fg" }
  display:   { fontFamily: "Anton", cqw: 16, weight: 400, lineHeight: 0.92, upper: true, color: "fg" }
  number-hero: { fontFamily: "Anton", cqw: 20, weight: 400, lineHeight: 0.9 }
  number-unit: { fontFamily: "JetBrains Mono", cqw: 4, weight: 700 }

spacing:
  slide-pad: "6cqw"      # ~65px @1080
  gap-md: "3cqw"
  radius: "0 — TODO es esquinado: sin border-radius, sin círculos, sin píldoras"
  caption-band: "top 1445px · height 170px (la escribe scripts/armar.py; el contenido vive arriba)"

components:
  top-kicker:
    position: "arriba, centrado, a 150px del borde superior"
    typography: "{typography.kicker}"
    description: "El rótulo de la escena (2 a 5 palabras, MAYÚSCULAS, mono, cian) con un punto degradado cian→violeta delante. Equivale al título de escena del ejemplo. Una por escena."
  hud-strip:
    position: "franja superior a 70px: izquierda VACÍA (sin rótulo de serie, a propósito), derecha el nombre de la etapa actual en mono-meta"
    description: "Chrome fino de laboratorio. Hairline inferior {colors.line}. Siempre tenue (dim), nunca compite."
  specimen-frame:
    description: "Marco para foto o video real: sin redondeo, hairline {colors.line}, sombra media, cuatro esquinas de mira en cian (ángulos de 28px, 2px), y debajo una línea mono-meta tipo `input: calle.jpg · 1080×1350 · RGB`. El medio va dentro; nada se dibuja encima salvo anotaciones del modelo."
  detection-box:
    description: "Caja de detección: borde 3px cian (o violeta para la segunda clase), etiqueta mono sobre fondo del mismo color con texto {colors.canvas}: `carro 0.97`. Se dibuja con trazo (draw-on), nunca aparece de golpe."
  data-grid:
    typography: "{typography.mono-data}"
    description: "Rejilla de números (píxeles, filtros, embeddings): celdas {colors.surface-2} con hairline, números {colors.fg}; la celda activa en cian. Los valores RGB pueden teñir el fondo de la celda con su propio color a 35%."
  prob-bar:
    description: "Barra de probabilidad: etiqueta mono a la izquierda, pista {colors.surface-2}, relleno degradado cian→violeta, valor en mono a la derecha. La ganadora llena primero."
  gradient-word:
    description: "La palabra clave de un titular Anton lleva el degradado cian→violeta (background-clip:text). Máximo una por escena."
  particle-net:
    description: "Firma de marca: red de partículas (puntos cian/violeta/azul, 2–3px, líneas de 1px a <110px, opacidad 0.35) en dos cúmulos, arriba a la derecha y abajo a la izquierda. Deriva lenta y determinista. Nunca sobre el medio ni sobre texto."
---

# Estilo base — Frame

## Overview

Un laboratorio de datos visto desde dentro, en vertical. **El negro es el suelo,
el blanco roto es la voz, el degradado cian→violeta es el voltaje.** Cada escena dice UNA idea:
un rótulo mono arriba, un foco grande en el centro (foto real, rejilla de números, diagrama o un
titular Anton), y los subtítulos palabra a palabra en la banda inferior. La red de partículas
vive en las esquinas como firma.

## The Frame

- 1080×1920. Contenido de cada escena en el rectángulo y 180→1440; debajo, nada salvo partículas. El ensamblado reduce y baja la escena para la zona segura del feed y los subtítulos caen debajo del contenido.
- Margen lateral `slide-pad` (65px). El foco central ocupa 80–90% del ancho.
- Fondo: `{colors.canvas}` plano con un viñeteado radial muy suave (centro #111 → borde #050505).

## Colors

**Paleta pastel sobre negro** (desde 2026-10-11): cian pastel `#9fe3f5`, lavanda `#c4b5fd`, durazno `#ffd9a0`, rosa `#ffadbb`, menta `#b4ecc8`, azul pastel `#a8c5ff`. Nada saturado.

Suelo `canvas`; superficies `surface`/`surface-2`; hairline `line`. Texto `fg`, `muted`, `dim`.
El **degradado cian→violeta** (`#9fe3f5 → #c4b5fd`) es el único acento de marca: palabra clave,
caja de detección, celda activa, barra ganadora. `signal-red` solo para "error/pérdida" y
`signal-amber` solo para el número de confianza destacado (ej. 94 %). Nada de azul marino.

## Typography

- **Anton MAYÚSCULAS** para golpes: título de portada, palabras-concepto ("NÚMEROS", "CNN",
  "PROFUNDO"), cifras héroe. Máximo 3 palabras por golpe.
- **Poppins** 400/600 para frases de apoyo (rara vez; los subtítulos ya cargan la narración).
- **JetBrains Mono** para todo lo que sea dato o chrome: rótulos, metadatos, matrices, etiquetas.
- Piso de legibilidad: 26px mono, 36px Poppins.

## Depth & Surface

Hairlines de 1px y una sombra profunda solo bajo los medios. El único brillo permitido es
`shadows.glow` en la celda o caja activa.

## Shapes

**Cero redondeo.** Todo esquinado: medios, tarjetas, etiquetas, chips, puntos (cuadrados); la única excepción son las partículas de la red, que sí son círculos, barras (segmentadas en bloques cuadrados, como píxeles). Nunca `border-radius`, nunca círculos, nunca píldoras. Es una regla firme del estilo.

## Frame Treatments

1. **Portada** — el tema en Anton gigante (p. ej. «BASES DE DATOS / VECTORIALES»), la palabra clave con
   degradado; mono `explicado rápido · ep/NN`; red de partículas más densa; detrás, un dato real tenue
   del tema (la columna de números del vector de «perro» en el ep/02).
2. **Muestra real** — specimen-frame con foto/video + anotaciones del modelo (cajas, puntos, máscara).
3. **Rejilla de datos** — data-grid enorme, una celda o ventana resaltada en cian; ecuación mono debajo.
4. **Golpe** — una palabra Anton a pantalla completa con degradado, sobre la imagen desvanecida.
5. **Diagrama** — bloques de capas/arquitectura en surface con hairline, flechas 2px cian.
6. **Cierre** — vuelve la imagen o el dato del gancho, ya resuelto; handle al final.

## Composition Rules

### Do
- Una idea por escena, un foco dominante.
- Medios reales siempre dentro de specimen-frame con su línea de metadatos.
- Los números que aparecen en pantalla salen del guion.

### Don't
- No poner contenido en la banda de subtítulos.
- No más de un degradado por escena; no colores fuera de la paleta.
- No dibujar partículas sobre medios o texto.

## Numerals & Claims (hard rule)

Toda cifra en pantalla sale del guion (SCRIPT.md). Las matrices de píxeles se toman de la imagen real
cuando se pueda; si no, se marcan como ilustrativas en la línea de metadatos.

## Fonts

```css
@font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-Regular.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-SemiBold.ttf") format("truetype"); font-weight: 600; }
@font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-Bold.ttf") format("truetype"); font-weight: 700; }
@font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono-400.woff2") format("woff2"); font-weight: 400; }
@font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono-700.woff2") format("woff2"); font-weight: 700; }
```
