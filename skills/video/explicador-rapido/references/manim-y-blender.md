# Gráficos con ManimGX y tomas 3D con Blender

Salió del ep/04 («La física del Tesla volador», 2026-10-16): 10 clips de ManimGX (diagramas de fuerzas, fórmulas que
se transforman, curvas de vaciado, potencia ∝ v³) y 3 tomas de Blender 5.2 (succión bajo el auto, tobera con diamantes
de Mach, giro sobre el eje largo). Todo entra a HyperFrames como `<video>` sin audio; kicker, HUD, fichas con cifras y
subtítulos siguen en HTML, que es donde vive el estilo.

## Cuándo usar cada uno

| Herramienta | Para | No para |
|---|---|---|
| HyperFrames (HTML) | tablas, tarjetas, benchmarks, flujos, cifras grandes, texto de lectura | 3D con cámara, fórmulas que se transforman |
| ManimGX | diagramas de cuerpo libre, `TransformMatchingTex`, curvas que se dibujan, planos que se deforman, 3D simple | texto largo (cae en la banda de subtítulos) |
| Blender | objetos reales en 3D (un auto, una tobera, un flujo de aire), cámara que gira, luz y volumen | gráficos con ejes o fórmulas |

Regla: **un clip, una idea**, sin texto de lectura dentro. Los números que el narrador dice van en fichas HTML.

## ManimGX

- Instalación: `uv tool install --python 3.14 manimgx` (no pide ffmpeg ni LaTeX; sin GPU usa lavapipe en CPU). Docs
  para agentes: <https://manimgx.academa.ai/llms.txt>. Fuentes del estilo instaladas en `~/.local/share/fonts` para que
  `Text(font="Anton")` salga igual que en HTML.
- Copia `<SKILL>/scripts/manim/` a `tools/manim/` del proyecto:
  - `estilo.py`: lienzo 1080×1920 a 30 fps, fondo `#0a0a0a`, paleta y fuentes, y la clase **`Reloj`**, que lee
    `audio_meta.json` y hace `wait()` hasta cada palabra (`r.hasta("fricción")`). Avisa de huecos de más de 1,5 s,
    revelaciones tardías y de todo lo que se salga de la franja útil. `r.fin()` cierra en `duration_s` exacto.
  - `_auto.py` + `auto-perfil-plano.svg`: silueta de deportivo de perfil con llantas redondas, con ayudas para el
    punto de contacto de la llanta y el centro de masa. Sirve de modelo para cualquier objeto real: **nada de cajas
    ni ruedas cuadradas** (el usuario rechazó el primer auto «cuadrado»).
  - `ejemplo-04-friccion.py`: escena completa (piso, auto, flechas F, N y m·g, `F ≤ μN` → `a = μg`).
- **Franja útil:** el gráfico va de y = −2,25 u a 4,6 u (≈ 340–1264 px). Arriba queda el kicker y abajo, de 1290 a
  1440 px, las fichas HTML. Si el gráfico baja más, las fichas tapan los ejes, y el detector de solapes no lo ve porque
  no mira los píxeles del video.
- Flujo por escena, desde `tools/manim/`:

  ```bash
  manimgx inspect 04-friccion.py          # storyboard PNG + línea de tiempo + problemas de maquetación, sin video
  manimgx render 04-friccion.py --fps 30 -r 1080x1920
  D=<duration_s de la escena en audio_meta.json>
  ffmpeg -y -i Escena.mp4 -vf "fps=30,tpad=stop_mode=clone:stop_duration=2" -t $D \
    -c:v libx264 -crf 18 -pix_fmt yuv420p -an -movflags +faststart ../../assets/manim/04-friccion.mp4
  ```

  La recodificación es obligatoria: `render` deja cuadros variables (no duplica los de los `wait`), el contenedor dura
  ~0,05 s de más y le falta la cola. Con `tpad` sale a 30 fps constantes y dura exactamente lo que la escena.
- Detalles de Typst y LaTeX: `1\mathord{,}26` (no `1{,}26`, que deja espacio); `\textstyle\int` para integrales que
  no sean gigantes; las fracciones son altas, así que apila las ecuaciones con `next_to` y mide. Números de ejes en
  mono con `font_size` ≥ 28 para que `inspect` no los marque como pequeños (mide a 1080 de alto, no a 1920).
- Velocidad en WSL sin GPU: ~3 veces el tiempo real (8 s de escena, 23 s de render).

## Blender

- Probado con Blender 5.2 de Windows lanzado desde WSL en modo fondo (EEVEE, ~5 s por cuadro a 1080×1920 en CPU/GPU
  integrada). Copia `<SKILL>/scripts/blender/` a `tools/blender/`:
  - `bcomun.py`: escena limpia, render EEVEE con «Standard» y sin dithering (el fondo `#0a0a0a` sale exacto),
    materiales emisivos con la paleta, tubos de flujo con UV de «tiempo de vuelo» para animar pulsos de aire, grilla
    de piso que se funde, cámara, luces y claves.
  - `auto.py`: deportivo procedural de carrocería suave, con ventanas, neumáticos de revolución con rines, y opacidad
    animable para mostrar lo que hay dentro.
  - `ejemplo-auto.py`: toma mínima (auto + grilla + cámara que gira) para partir.
  - `correr.sh <toma> [--cuadros 1,90 --escala 50]`: renderiza PNG (variables `BLENDER` y `SALIDA_WIN`).
  - `codificar.sh <toma> [cuadros]`: PNG → MP4 H.264 BT.709 a 30 fps con bloom suave que no toca el fondo, más una
    hoja de contacto y el color del píxel de esquina (debe dar `0a0a0a`).
- Prueba siempre con `--cuadros` sueltos a escala 50 antes de la toma completa. Escribe los PNG fuera del proyecto y de
  OneDrive (p. ej. `D:\tmp\blender`).
- Duración: calcula los cuadros de la toma con la `duration_s` de la escena y pon en el docstring la línea de tiempo en
  segundos de cada evento, alineada con las palabras del storyboard.
- Las tomas 3D son ilustrativas: dilo en los créditos (`creditos-descripcion.txt`).

## Montaje en HyperFrames

```html
<video id="f04-friccion-clip" class="clip" src="assets/manim/04-friccion.mp4" muted playsinline
       data-start="0" data-duration="7.083" data-track-index="1"></video>
```

```css
#f04-friccion-clip { position:absolute; left:0; top:0; z-index:2; width:1080px; height:1920px;
                     object-fit:cover; mix-blend-mode:lighten; }
```

Capas: 0 fondo → 1 partículas tenues → 2 video (lighten) → 3 kicker, HUD, fichas y metadatos. En `index.html`
añade `.scene { mix-blend-mode: lighten; }`: el `transform` de la zona segura del feed crea un contexto de apilamiento
y sin eso el `#0a0a0a` del clip se ve como un rectángulo más oscuro sobre el degradado del `#root`.
