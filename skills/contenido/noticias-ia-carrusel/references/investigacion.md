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
Usa WebSearch/WebFetch (ToolSearch "select:WebSearch,WebFetch").
Devuelve en español, compacto: 1) 5-8 temas de conversación de esta semana con link; 2) memes o formatos
de IA virales de la semana adaptables al nicho; 3) cambios recientes del algoritmo de Instagram o TikTok;
4) audios en tendencia útiles para tech. No inventes; marca lo que no pudiste verificar.
```

## Fuentes que fallan (a 2026-09)
- Reddit: bloquea WebFetch y Firecrawl (JSON y RSS). Usar el resumen diario en GitHub.
- X: devuelve 402 y xcancel está suspendido; los posts se descargan igual con `uvx yt-dlp <url del post>`.
- CNBC: 403. The Verge: solo RSS y metadatos. Ars Technica: solo metadatos.
- TikTok Creative Center: no carga.
- openai.com: a veces sirve un challenge de Cloudflare a Playwright; reintentar una vez con user agent de Chrome.
- YouTube: algunos videos dan 403 en yt-dlp. Alternativa: grabar la demo del sitio con `capture.py rec`.
