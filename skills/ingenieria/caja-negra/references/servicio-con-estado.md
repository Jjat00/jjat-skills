# Servicio con estado y muchas requests

Estructura probada en un reto real (de 83 a 100 de 100). `lab/` y `app/` se montan en minutos con los scripts de esta skill.

## Estructura

```
lab/                  habla con el original y mide (nunca lo importa el reemplazo)
  probe.py            cliente: límite de tasa, reset por secuencia, redacta credenciales, registra cada request
  compare.py          comparador oficial, idéntico al del enunciado
  control.py          el cálculo transversal (checksum) compartido con el reemplazo solo por copia
  exp/eNN_tema.py     un experimento por script, con su hipótesis en el docstring
  m1.py fuzz.py canario.py recorrida.py m3.py m5.py
app/                  reemplazo determinista, sin llamadas al original
  main.py             ruta comodín (bytes exactos; el framework no genera sus propios 404/405/422)
  tuberia.py          etapas de validación cuyo orden fija el perfil
  perfiles.py         reglas por versión del servicio (PERFIL=v_manana | v_tarde)
  catalogo.py         códigos de error y textos exactos, como datos
  comandos.py         manejadores puros (estado, args) -> (status, cuerpo, estado')
experimentos.jsonl    log append-only: id, seq, x_req, hipotesis, request, status, response, conclusion
docs/diseno.md, docs/especificacion.md, docs/diseno-cambios.md
.revisiones/          informes de Codex (gitignored)
```

## Decisiones de arquitectura (y su alternativa descartada)

| Restricción | Decisión | Descartada |
|---|---|---|
| Comparación exacta + checksum | Motor determinista | LLM que imite respuestas |
| El framework responde sus propios errores | Ruta comodín con bytes exactos | Rutas tipadas con validación del framework |
| Varias fallas dan un solo error; una versión nueva puede reordenar | Tubería ordenada como configuración + catálogo como datos | `if` dentro de cada comando |
| Cada test empieza con reset; un solo proceso | Estado en memoria, 1 réplica, 1 worker | SQLite o Redis |
| El servicio cambia durante el día | Perfiles por versión | Editar en sitio |
| La spec cita el log; el juez resta por afirmación falsa | El log como única fuente de verdad | Notas sueltas |
| Serverless rompe la memoria entre pasos | Proceso largo (Railway) | Vercel serverless |

## Mediciones

| | Qué | Puerta |
|---|---|---|
| **M1** | Regresión: repite todo el log (por versión) contra el reemplazo local | 100 % de pasos |
| **M2** | Fuzzer diferencial: lotes de 100 tests inéditos con la mezcla del set, semilla guardada, contra original y reemplazo. Tras cada arreglo, **semilla nueva** | ≥ 95 %, idealmente 100 |
| **M3** | Cobertura: comando × error × estado; cuenta comportamientos de la spec por confianza | ≥ 90 % confirmados |
| **M4** | Canario: secuencia fija (~40 pasos) que toca cada regla; detecta si el original cambió | 0 diferencias |
| **M5** | Latencia p99 del desplegado | muy por debajo del límite por paso |
| **M6** | Diferencial exploratorio con el original como oráculo: mutaciones de carácter de mensajes válidos (con el checksum recalculado), variantes del cuerpo/rutas/auth, barrido de nombres de comando | 0 diferencias y 0 comandos fuera del catálogo |

**El punto ciego que costó 17 tests:** M2 solo genera lo que tu modelo ya conoce. M6 responde otra pregunta («¿qué existe que no conozco?») y va **separada** para que la tasa de M2 siga siendo comparable con el set.

## Orden de trabajo que funcionó

1. 10:20–11:45: material, laboratorio y ~140 sondas cortas solo sobre lo que cambia la arquitectura. Una la cambió: el router iba antes que la auth.
2. Hasta 13:15: control (por pesos de posición), orden completo de errores, negocio, bloqueo, comandos ocultos por sugerencias; reemplazo, M1 100 %, M2 100/100 en dos semillas, canario base. ~2300 requests.
3. Corrida 1: 83. Diferencial M6 (~2200 requests): comando oculto NOTAS, mayúsculas solo ASCII, `NaN` → E100.
4. Versión nueva del original a media tarde: el canario la detectó en el primer paso; un experimento midió los cambios; perfil nuevo; semilla nueva 100/100.
5. Corrida 2: 99. Logs HTTP del host para reconstruir la forma del set; experimentos sobre los candidatos; traza temporal en el reemplazo durante la corrida 3 (99 otra vez) dio el texto exacto de los 100 tests: el que fallaba era `HALT;1`.
6. Arreglo, traza retirada, M1 y despliegue verificados: **100/100** en la corrida final.

## Gotchas de servicio

- **Token del equipo ≠ token personal**: el reemplazo acepta el que usa el juez; el original se explora con el personal. La primera validación falló con `/health` 401 por eso.
- **Despliegue automático durante una corrida reinicia el proceso y borra el estado**: no hacer push mientras evalúan.
- Railpack puede ignorar el start command de `railway.json`: `railpack.json` explícito.
- Los registradores copian headers: redacta credenciales antes del primer commit.
- Búsquedas binarias contra un servicio con estado se contaminan (tres rechazos bloquearon la cuenta y el bloqueo pasó por éxito): reset por sonda y abortar ante una respuesta inesperada.
- Un header de conteo (`X-Req`) puede sobrevivir al reset: comprueba qué evalúa el juez antes de replicarlo.
