# Evaluaciones oficiales: cuándo gastarlas y qué sacar de ellas

Suelen ser 3. Dan un número (accuracy, exactCount, error medio, tests pasados) y casi nunca los casos. Son la medición más cara del reto.

## Puerta para gastar una

Todas a la vez:

1. M1 al 100 % y M2 ≥ 95 % con una **semilla nueva** (o, en función pura, veredicto `certificada`).
2. Lo transversal medido en todos sus bloques (cada franja, cada bandera en cada tramo, orden de errores completo).
3. Canario sin diferencias en los últimos minutos (el original no cambió).
4. El desplegado es idéntico al local (M2 contra la URL) y acepta el token del juez.
5. **Una predicción escrita**: «espero X; si da menos de Y, la causa más probable es Z». Sin predicción, el número no refuta nada.
6. **Sí explícito de Jaime** en ese momento. Autorizar el bucle de consultas no autoriza el envío.

## Qué sacar del número

- **Es una restricción, no un dato.** «200 de 1000» no dice cuáles; úsalo para descartar hipótesis que no puedan dar ese número, nunca como filtro por igualdad contra un set simulado.
- **Tamaño del hueco → tipo de causa.** Calcula de antemano cuántos tests movería cada supuesto (p. ej. ~40 casos si el error es una hora de frontera, ~90 si es la combinación de banderas). 17 fallos con M2 al 100 % significaba «comportamientos que mi generador no produce», no «reglas mal medidas».
- **Diseña la siguiente para separar causas**, no para «probar suerte». Una tercera evaluación gastada así solo refutó una hipótesis y bajó de 200 a 154.
- Cuenta la mejor si el ranking conserva la mejor; si cuenta la última, no arriesgues la final con una variante.

## Después de cada una

1. Diferencial exploratorio (M6) y barridos de lo desconocido.
2. Logs del host y, si procede, traza temporal del set.
3. Arreglo con su experimento y su fila de log; Codex; commit; despliegue verificado.
4. Semilla nueva de M2, canario, y solo entonces la puerta otra vez.

## Lo que sale mal si no

- Función pura: la primera evaluación se gastó con horas 7–11 y 13–18 nunca sondeadas; ninguna variante simulada reproducía a la vez las dos primeras evaluaciones y el 80 % quedó sin explicar.
- Servicio con estado: la corrida 1 con la puerta cumplida dio 83 igualmente. La puerta no garantiza el puntaje; garantiza que el hueco es información.
