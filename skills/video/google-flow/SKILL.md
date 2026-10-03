---
name: google-flow
description: Genera videos e imágenes en Google Flow (Veo 3.1, Omni, Nano Banana) desde la terminal con el CLI propio flow.py, gastando los créditos del plan de Google AI de Jaime. El CLI crea el proyecto, sube fotos y videos de referencia, elige modelo, formato y cantidad, escribe el prompt y descarga el resultado; Jaime solo pulsa enviar y «Aprobar» en Flow, porque el reCAPTCHA rechaza el envío automatizado. Úsala siempre que Jaime pida generar algo «en Flow», «con Veo» o «con los créditos de Google», hacer planos de un guion con Flow, o subir referencias a Flow, aunque no nombre la skill. No sirve para generar sin humano (eso es HF Studio o la Gemini API).
---

# Google Flow (semiautomático)

Flow (`flow.google.com`) no tiene API. El CLI `~/projects/google-flow-cli/flow.py` habla con sus RPC internas
(`batchexecute`) y maneja la interfaz con `agent-browser`. Recon, evidencia y límites en
`~/projects/google-flow-cli/recon/google-flow.md`. El CLI vive en ese repo privado y no se copia aquí.

## La regla que no se rompe

**El envío y la aprobación los hace Jaime.** Enviar el prompt con clics o teclas automatizados devuelve
`PUBLIC_ERROR_UNUSUAL_ACTIVITY` (4 de 4 rechazos el 2026-10-03), y un clic humano en el mismo Chrome pasa (3 de 3).
No intentes saltarlo: arriesga la cuenta. Todo lo demás sí se automatiza: configurar, subir, adjuntar, escribir,
esperar y descargar. Si a Jaime le sale «unusual activity», que pulse «Reintentar».

## Límite de uso

El 2026-10-03, tras unas 3 h de uso intensivo (varios envíos, rechazos y reintentos), Flow empezó a rechazar **también
los clics humanos**: primero `PUBLIC_ERROR_UNUSUAL_ACTIVITY_TOO_MUCH_TRAFFIC` y después `UNUSUAL_ACTIVITY`. Siguió igual
una hora después, con la página limpia. Por eso:
- Usa `prep --clean` y `wait --clean` por defecto: no inyectan nada en la página.
- Si sale «unusual activity», que Jaime pulse «Reintentar» **una sola vez**. Si falla de nuevo, para hasta el día
  siguiente; reintentar en bucle empeora el bloqueo.
- No se cobra nada por los envíos rechazados.

## Flujo

```bash
F=~/projects/google-flow-cli/flow.py
python3 $F start                      # Chrome con perfil flow-chrome y puerto 9334 (sesión ya iniciada)
python3 $F credits                    # saldo; dilo antes de proponer cuántos planos caben
python3 $F new-project "<título>"     # o reutiliza uno: el id está en la URL /project/<id>
python3 $F upload <id> foto1.png video.mp4 ...   # referencias; la 1.ª vez Jaime acepta «Derechos para usar esta imagen»
python3 $F assets <id>                # nombres exactos para --ref (los videos generados también salen aquí)
python3 $F prep <id> "<prompt>" --ref image_1.jpeg --model "Omni 1.1 Flash" --aspect 9:16 --clean
python3 $F wait <carpeta> --clean     # en segundo plano; descarga cuando Jaime envía y aprueba
```

Después de `prep`, dile a Jaime exactamente: «En Flow: pulsa enviar, revisa el costo y pulsa Aprobar». Lanza `wait`
en segundo plano antes de que lo haga. `wait` imprime una línea JSON por archivo y al final el saldo.

## Modelos y costos (observados el 2026-10-03)

| Modelo en el menú | Para qué | Costo | Salida |
|---|---|---|---|
| Veo 3.1 - Lite | Texto a video barato | 10 créditos | 8 s, 720p, con audio |
| Omni 1.1 Flash | Video con imágenes de referencia (producto, personaje) | 15 créditos | 10 s, 720×1280 en 9:16 |
| Veo 3.1 - Fast / Quality | Más calidad | sin medir | — |
| Nano Banana 2 Lite (imagen) | Fotogramas y pruebas | 0 créditos | 1376×768 |

- Con referencias adjuntas, **el agente de Flow cambia a Omni por su cuenta** aunque el modelo por defecto sea otro.
  `--pin-model` añade al prompt la orden de respetarlo, pero el costo real es el que Jaime ve al aprobar.
- La cuenta recibe créditos diarios (banner de Flow: 50 al día para suscriptores, a 2026-10). Reparte un guion
  largo en varios días en vez de agotar el saldo en un solo plano caro.
- Formato: el prompt va al agente de Flow, que lo traduce y amplía. Escríbelo en inglés y empieza con una frase en
  español que diga qué referencias usar («Genera un video vertical 9:16 usando la imagen de referencia del vaso…»).

## Trampas

- Usa siempre `flow.py` o `agent-browser --cdp 9334`. Con `agent-browser connect` y después `close`, los comandos
  siguientes lanzan un navegador propio en blanco, y las capturas salen blancas.
- En zsh no guardes `agent-browser --cdp 9334` en una variable: usa una función (`ab(){ agent-browser --cdp 9334 "$@"; }`).
- Si Jaime recarga la pestaña de Flow después de `prep`, ejecuta `flow.py spy` antes de `wait`, o `wait` no verá la
  generación.
- `pkill -f "<patrón>"` puede matar tu propia shell si el patrón aparece en el comando.
- La sesión vive en el perfil de Chrome; `recon/secrets/` guarda cookies y token (gitignored). Nunca los copies a
  otro lugar.
- Google ya cambió Flow una vez (septiembre de 2026, de `labs.google` a `flow.google.com`). Si una RPC falla o un
  botón no aparece, revisa primero con una captura (`agent-browser --cdp 9334 screenshot`) y el recon antes de
  parchear a ciegas.

## Al terminar

Lista los archivos descargados con su modelo y su costo, el saldo final y qué planos faltan. Si el resultado se
desvió del guion (encuadre, desenfoque, ingredientes cambiados), dilo con el plano concreto y propone el ajuste
del prompt para la siguiente tirada.
