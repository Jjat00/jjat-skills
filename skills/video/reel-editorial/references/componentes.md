# Componentes del reel editorial

Todos los estilos ya están en `assets/template.html`; aquí está qué hace cada pieza y cómo se usa. El ejemplo completo
(7 paneles y 4 textos sobre pantalla completa) está en `references/ejemplo-claude-codex/`: cópialo como punto de
partida y reescribe el contenido.

## Lienzo y capas

- 1080×1920. `#full` = presentador a pantalla completa (`assets/edit.mp4`); `#split` = papel crema + tarjeta de color
  con el presentador recortado (`assets/presenter-alpha.webm`). `build.py` alterna las dos capas según
  `reel.json.windows`; tú solo escribes el contenido.
- **Zona útil de los paneles:** `y` de 96 a ~860 (la tarjeta empieza en 880). Márgenes laterales de 80 px.
- **Subtítulos:** `build.py` los genera; quedan en y=1560 (dividida) o y=1400 (completa). No pongas nada ahí.

## Paneles (pantalla dividida)

Cada panel es un clip: `<div id="pN" class="panel clip" data-start=".." data-duration=".." data-track-index="4">`.
Su `data-start`/`data-duration` debe caer dentro de un tramo `split`.

| Pieza | Clases / estructura | Úsala para |
| --- | --- | --- |
| Etiqueta de sección | `<div class="label"><b>01</b> · EL TRUCO</div>` | Numerar cada idea (como la referencia). Siempre la primera en entrar. |
| Titular editorial | `<div class="headline serif"><span>línea 1</span><span class="red">línea 2</span></div>` | Frases e ideas. Serif itálica; la segunda línea en rojo remata. |
| Palabra gigante | `<div class="giant">NO ES</div>` (`.giant.red` para el golpe) | Una o dos palabras que pegan ("SE SESGA", "SÍGUEME"). |
| Tachado | `<div class="strike" style="left;top;width">` + `scaleX 0→1` | Negar una frase. |
| X roja | `<span class="xmark"><i></i><i></i></span>` dentro de la palabra (`position:relative`), barras a ±22° | Marcar un error sobre una palabra concreta. |
| Píldoras | `.pill`, `.pill.red`, `.pill.outline` | Roles, etiquetas, chips (commit, PR, "rol: evaluador"). |
| Tarjetas de comparación | `#…-cards` con dos `.cmp` (logo + `.name` + `.who` + `.badge`) | A frente a B (blueprint `comparison-split`): entran desde lados opuestos con `rotationY` espejo. |
| Terminal | `.term` > `.bar` (tres `<i>` + título) + `.panes` > `.pane` (o `.body`) | Herramientas de terminal, agentes. `.orange`, `.dim`, `.ok` para colores. |
| Tecleo | `<div id="x-prompt"><span class="orange">&gt; </span><!--__TYPE:pc__--><span id="p4-caret"></span></div>` + entrada en `reel.json.typing` (el cursor `#p4-caret` ya tiene estilo y el ejemplo lo hace parpadear) | Un prompt que se escribe mientras se dice (blueprint `prompt-type-submit-generate`). Pon `white-space:pre-wrap` y ningún espacio de plantilla dentro del contenedor. |
| Conversación | `.agent` (`.avatar` + `.nm`), `.role`, `.bubble.l` / `.bubble.r` | Dos agentes o personas hablando (blueprint `agent-progress-theater`, hilo). |
| Revisión + sello | tarjeta tipo `#p6-review` con spinner + `#…-stamp` (borde rojo, rotado −8°) | Un veredicto: "APROBADO", "LISTO". El sello entra con `scale 2.6→1`, `power4.in` y una sacudida corta. |
| Bucle | dos `.node` + SVG con dos flechas curvas (`strokeDashoffset`) + contador de rondas | Iterar, ciclos, ida y vuelta. |
| Mascota | SVG pequeño (cuerpo redondeado rojo, ojos, patas) con clase `.mascot` | Un personaje propio que asoma y se balancea. No copies la mascota de la referencia. |
| Sticker | `.sticker` + píldora rotada 6° | Notas al margen ("↗ video anterior"). |

## Textos sobre pantalla completa (overlays)

Clip dentro de `#full`: `<div id="oN" class="clip" data-start data-duration data-track-index="5">` con
`<div class="ovl"><div class="ovl-card"><div class="serif s1">…</div><div class="s2">…</div></div></div>`.
`.s2` empieza con `display:none`: haz `tl.set("#oN-s2",{display:"block"},t)` justo antes de su `pop`, así la tarjeta
crece al entrar la segunda línea en vez de mostrar un hueco.

## Animación (scenes.js)

Ayudas ya definidas en la plantilla:

- `pop(sel, t, from)` — entrada con rebote (`back.out`), para píldoras, stickers y burbujas.
- `rise(sel, t, y)` — sube y aparece, para etiquetas y titulares.
- `show(sel, a, b)` — muestra un `.beat` entre `a` y `b` (varios beats en un mismo panel, uno tras otro).

Reglas que pide HyperFrames (el lint las revisa):

- Sincroniza cada entrada con la palabra que la motiva: toma el `start` de `assets/words.json`.
- No pongas `transform` en el CSS de algo que animes: usa `fromTo` con el estado inicial.
- Varios `fromTo` sobre el mismo elemento: el segundo lleva `immediateRender:false`, o fija un estado base con
  `tl.set(sel, {...}, 0)`.
- Bucles con `repeat` finito (nunca `-1`). Nada de `letterSpacing` ni propiedades de maquetación: solo transformaciones
  y opacidad.
- Titulares de varias líneas con interlineado ajustado: `check` los marca como `content_overlap`. Si se ven bien en la
  captura, pon `data-layout-allow-overlap` en **cada** `span`/línea (no se hereda desde el contenedor).
