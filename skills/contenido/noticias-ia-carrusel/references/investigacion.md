# Investigación: prompts de los dos agentes

Lánzalos juntos (dos llamadas `Agent` en el mismo mensaje, `subagent_type: general-purpose`). Sustituye `<FECHA>` por la fecha de hoy (AAAA-MM-DD).

## Agente 1: noticias del día

```
Hoy es <FECHA>. Investiga las noticias de inteligencia artificial y software publicadas HOY o, como mucho,
en las últimas 24-36 horas. Nada más viejo.

Usa WebSearch y WebFetch (cárgalos con ToolSearch "select:WebSearch,WebFetch") y, si sirve, la skill
firecrawl-search. Revisa: The Verge, TechCrunch, Ars Technica, 9to5Mac, MacRumors, blogs oficiales
(OpenAI, Anthropic, Google DeepMind, Meta AI, NVIDIA, Microsoft, Apple, xAI, Mistral, Runway, Pika,
Luma, Kling, Higgsfield, ElevenLabs, Figure, Tesla Optimus, Unitree, SpaceX), Hacker News (portada),
Product Hunt de hoy, GitHub trending, y el resumen diario de Reddit que se publica en GitHub
("reddit-daily-news") porque Reddit bloquea el acceso directo.
Para X, Reddit y TikTok usa agent-browser (sesión ya iniciada) (Bash), que abre un navegador real: ver la sección
"Redes con agent-browser" de references/investigacion.md en la skill noticias-ia-carrusel.

Prioriza noticias MUY VISUALES (demos en video, robots, gadgets, generadores de video o imagen,
lanzamientos con clip oficial, juegos o apps hechos con IA): cada lámina del carrusel lleva el video o
la imagen de la noticia.

Devuelve 10 a 12 noticias, ordenadas por potencial viral, cada una con:
- Titular en español tipo gancho (máx. 12 palabras, estilo "X acaba de…")
- Resumen en español de 2-3 frases con el dato concreto (cifras, nombres)
- Fecha y hora de publicación verificada y URL de la fuente principal
- URL del MEDIO: link directo al mp4, al video (YouTube, post de X, v.redd.it) o a la imagen oficial
  (og:image). Si no hay, dilo.
- Por qué es viral (1 línea) y confianza (oficial / prensa / rumor)
Añade al final los eventos programados para HOY (keynotes, lanzamientos) con su hora.
Marca si no pudiste verificar una fecha. No inventes nada; si una fuente no carga, dilo.
Responde en español, formato compacto.
```

## Agente 2: tendencias (semanal)

```
Hoy es <FECHA>. Investiga qué está funcionando ESTA SEMANA en contenido de software + IA en TikTok,
Instagram (reels y carruseles) y X, sobre todo en español y LatAm, para un creador que publica a diario.
Usa WebSearch/WebFetch (ToolSearch "select:WebSearch,WebFetch") y, para ver las redes por dentro
(explorar de TikTok, reels, tendencias de X), agent-browser como se explica en la sección
"Redes con agent-browser" de references/investigacion.md en la skill noticias-ia-carrusel.
Devuelve en español, compacto: 1) 5-8 temas de conversación de esta semana con link; 2) memes o formatos
de IA virales de la semana adaptables al nicho; 3) cambios recientes del algoritmo de Instagram o TikTok;
4) audios en tendencia útiles para tech. No inventes; marca lo que no pudiste verificar.
```

## Redes con agent-browser

`agent-browser` maneja un Chrome real, así que llega a donde WebFetch y Firecrawl no llegan: X, Reddit y TikTok. Sirve para descubrir qué se comparte hoy, confirmar la fecha exacta de un post y encontrar el video original. Receta completa y lo que falla en el vault: `Conocimiento/Leer X, Reddit y TikTok con agent-browser y sesión propia.md`.

**La sesión ya está iniciada** (a 2026-09-30) en el perfil `~/.agent-browser/profiles/redes-chrome`: X, Reddit, TikTok y YouTube. **No pidas a Jaime que vuelva a iniciar sesión** salvo que una red muestre la pantalla de login. Instagram todavía no tiene sesión en ese perfil.

```bash
# 1. Lanzar el Chrome normal con el perfil logueado y puerto de depuración
google-chrome --user-data-dir=$HOME/.agent-browser/profiles/redes-chrome --remote-debugging-port=9333 --no-first-run about:blank &
# 2. Conectarse (en zsh usa la variable de entorno, no "$AB open": zsh no separa palabras)
export AGENT_BROWSER_SESSION=redes
agent-browser connect 9333
agent-browser open "https://x.com/search?q=AI%20min_faves%3A1000%20within_time%3A1d&f=top"
agent-browser wait 3000 && agent-browser snapshot -i
agent-browser eval --stdin < extraer.js          # devuelve JSON como texto
agent-browser screenshot "<carpeta>/medios/NN_post.png"
```

- **No uses** `--session-name`, `--profile` ni el Chrome for Testing de agent-browser: Google no deja iniciar sesión y X responde 403.
- **X:** búsqueda `min_faves:1000 within_time:1d` con `f=top`; leer `article`, `[data-testid=tweetText]`, `time` y `[data-testid=like]`. Cuentas oficiales: @OpenAI, @AnthropicAI, @GoogleDeepMind, @xai, @runwayml, @higgsfield_ai…
- **Reddit:** dentro de la página, `fetch('/r/LocalLLaMA+singularity+OpenAI+ClaudeAI/top.json?t=day')` devuelve JSON limpio con score, título, URL e `is_video`. Es la mejor fuente de las tres.
- **TikTok:** `/search/video?q=inteligencia%20artificial`; filtra los enlaces `a[href*="/video/"]` que salen del panel de notificaciones.
- **Solo lectura:** mirar, leer y capturar. Nada de dar like, seguir, comentar ni publicar.
- **Poco volumen:** esperas de unos segundos entre páginas y pocas decenas de vistas por sesión; X y TikTok detectan automatización.
- **Cerrar Chrome al terminar:** recorre `pgrep -x chrome` y revisa `/proc/<pid>/cmdline`; no uses `pkill -f`, que puede matar la propia shell.
- **Descarga del video:** agent-browser encuentra el post; el archivo se baja con `uvx yt-dlp <url del post>` (paso 3 de la skill).
- **Playwright** (`scripts/capture.py`) sigue siendo para capturar sitios públicos sin sesión (comunicados, demos); no tiene el login de las redes.

## Fuentes que fallan (a 2026-09)
- Reddit: bloquea WebFetch y Firecrawl (JSON y RSS). Usar agent-browser o el resumen diario en GitHub.
- X: devuelve 402 a WebFetch y xcancel está suspendido. Usar agent-browser para leer; los posts se descargan con `uvx yt-dlp <url del post>`.
- TikTok: no carga con WebFetch. Usar agent-browser. Instagram: sin sesión en el perfil todavía.
- CNBC: 403. The Verge: solo RSS y metadatos. Ars Technica: solo metadatos.
- TikTok Creative Center: no carga con WebFetch; probar con agent-browser.
- openai.com: a veces sirve un challenge de Cloudflare a Playwright; reintentar una vez con user agent de Chrome.
- YouTube: algunos videos dan 403 en yt-dlp. Alternativa: grabar la demo del sitio con `capture.py rec`.
