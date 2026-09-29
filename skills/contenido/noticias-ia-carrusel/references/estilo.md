# Estilo visual (jaimeaza.tech)

Tomado del código del portfolio (`jjat-portfolio`: `src/styles/global.css`, `AboutMe.astro`, `HeroBackground.astro`) a 2026-09.

| Token | Valor | Uso |
|---|---|---|
| `--bg` | `#0a0a0a` | fondo de lámina y de página |
| `--surface` / `--surface-2` | `#111110` / `#161615` | fondo de medios, gráficos, chips |
| `--line` | `#232323` | bordes de medios, chips, barras |
| `--fg` | `#ededed` | titulares |
| `--muted` | `#a1a09a` | párrafos |
| `--dim` | `#666666` | fuente, numeración |
| `--cyan` → `--violet` | `#68ddfd` → `#9e8cfc` | degradado (el «Aza» del sitio): palabras en `<b>`, punto de la etiqueta, barra resaltada, línea de portada |

- **Red de partículas:** dos cúmulos (arriba a la derecha y abajo a la izquierda) de puntos cian, violeta y azul con líneas finas a menos de 110 px, como el canvas del hero. Nunca se dibuja encima del medio.
- **Esquinas:** casi rectas como en el sitio (8 px en medios, 6 px en la frase y los chips).
- **Tipografía** (elegida por Jaime, se mantiene): Anton para portada y cierre en mayúsculas; Poppins 700 para titulares y 400 para párrafos.
- Todo vive en `assets/slide.css`. Para cambiar el estilo se editan solo los tokens de `:root`.

Pendiente: logo y @ de Jaime (hoy la etiqueta es «NOTICIAS DE IA · fecha»).
