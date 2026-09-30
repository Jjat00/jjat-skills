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
Para X, Reddit, TikTok e Instagram usa agent-browser (Bash), que abre un navegador real: ver la sección
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

`agent-browser` (CLI global, `~/.nvm/.../bin/agent-browser`) maneja un Chromium real, así que llega a donde WebFetch y Firecrawl se quedan fuera: X, Reddit, TikTok e Instagram. Sirve para confirmar la fecha exacta de un post, ver el video original, leer los comentarios y detectar qué se está compartiendo hoy.

```bash
AB="agent-browser --session-name redes"         # guarda cookies y login entre sesiones
$AB open "https://x.com/search?q=AI%20since%3A<FECHA>&f=live"
$AB wait 3000 && $AB snapshot -i                # árbol accesible con refs @eN
$AB get text @e12                               # texto de un post
$AB scroll down 2000 && $AB snapshot -i         # más resultados
$AB screenshot "<carpeta>/medios/NN_post.png"   # captura del post si no hay otro medio
$AB close
```

- **Qué revisar:** X (búsqueda en vivo y cuentas oficiales: @OpenAI, @AnthropicAI, @GoogleDeepMind, @xai, @runwayml, @higgsfield_ai…), Reddit (`r/singularity`, `r/LocalLLaMA`, `r/artificial`, `r/OpenAI`, orden «new» o «top hoy»), TikTok (búsqueda «inteligencia artificial» y «IA noticias») e Instagram (reels de las cuentas del nicho).
- **Login:** la primera vez, Jaime inicia sesión a mano con `agent-browser --session-name redes --headed open https://x.com/login` (igual para Instagram y TikTok). Con `--session-name redes` el estado queda guardado y las siguientes veces ya entra logueado. Nunca escribas contraseñas en comandos ni en la skill.
- **Solo lectura:** mirar, leer y capturar. Nada de dar like, seguir, comentar ni publicar.
- **Ritmo humano:** esperas de unos segundos entre páginas y pocas decenas de vistas por sesión, para no activar bloqueos anti-bot.
- **Descarga del video:** agent-browser encuentra el post; el archivo se sigue bajando con `uvx yt-dlp <url del post>` (paso 3 de la skill).
- `agent-browser skills get core` muestra la guía completa del CLI.

> [!question] Hueco
> A 2026-09-30 falta probar qué redes cargan sin login y cuáles piden el login guardado; anótalo aquí tras la primera corrida.

## Fuentes que fallan (a 2026-09)
- Reddit: bloquea WebFetch y Firecrawl (JSON y RSS). Usar agent-browser o el resumen diario en GitHub.
- X: devuelve 402 a WebFetch y xcancel está suspendido. Usar agent-browser para leer; los posts se descargan con `uvx yt-dlp <url del post>`.
- TikTok e Instagram: no cargan con WebFetch. Usar agent-browser.
- CNBC: 403. The Verge: solo RSS y metadatos. Ars Technica: solo metadatos.
- TikTok Creative Center: no carga con WebFetch; probar con agent-browser.
- openai.com: a veces sirve un challenge de Cloudflare a Playwright; reintentar una vez con user agent de Chrome.
- YouTube: algunos videos dan 403 en yt-dlp. Alternativa: grabar la demo del sitio con `capture.py rec`.
