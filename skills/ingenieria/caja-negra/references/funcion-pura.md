# Función pura con pocas consultas

Para cajas sin estado y con presupuesto escaso (decenas de consultas): cada consulta vale ~4 % del presupuesto. Conviene un solver propio con familias de hipótesis, planificador, certificación y simulador, documentado en `METODOLOGIA.md`.

## 1. Familias en capas

Enumera hipótesis antes de consultar:

- **H0**: la forma conocida (repo, versión anterior, enunciado) con sus listas de parámetros. Enumerable (del orden de cientos de miles de combinaciones).
- **H1**: la misma forma con otros números u otro orden de operaciones. No enumerable: se resuelve por etapas con poda.
- **H2…**: otras estructuras concretas (lineal por tramos, franja nocturna aditiva…).
- **Protocolo manual**: lo que no cabe en ninguna. Asume que llegarás aquí: en el caso real, H0 murió en la consulta 1 (la respuesta no era múltiplo del redondeo esperado) y H2 en la 3.

**Presupuesto por capa, fijado antes**: si las familias mueren pronto, el resto del presupuesto ya está repartido entre transversal y estructural, no se improvisa.

## 2. Reparto del presupuesto

Con N consultas, como orientación:

| Bloque | % | Qué |
|---|---|---|
| Anclas | ~10 | Puntos válidos bajo cualquier familia (hora neutra, sin banderas) |
| Transversal | ~35 | Cada franja horaria (0–6, 7–11, 12–18, 19–23) al menos una vez; cada bandera en **cada tramo** y a dos distancias; combinaciones de banderas; redondeo final |
| Estructural | ~35 | Tramos, quiebres y umbrales, con al menos un punto feo dentro de cada tramo |
| Confirmación | ~20 | Donde más alternativas vivas discrepan |

Para medir lo transversal usa una **entrada de referencia** cuyo valor base ya sea exacto: así cualquier cambio se atribuye a la variable medida.

## 3. Elegir cada consulta por entropía

Entre las hipótesis vivas, consulta la entrada cuya predicción tenga máxima entropía (ganancia de información esperada con prior uniforme). Mientras H0 vive, calcula la entropía sobre H0 más una población de cobertura de H1: cada consulta identifica dentro y discrimina fuera.

## 4. Parada exacta

Para solo con una hipótesis viva o con todas **equivalentes en todo el dominio del contrato** (el producto cartesiano de los rangos, con una hora por patrón de franja y todas las combinaciones de banderas). Con pasos enteros, `ceil(x/k) = ceil(ceil(x)/k)`: cubrir enteros cubre decimales. Nada de umbrales tipo 99,9 %: una precisión por caso de 0,999 da 37 % de acertar 1000 de 1000.

## 5. Confirmar contra las alternativas reales

Identificada en H0, resuelve H1 completa contra el cuaderno y consulta donde discrepe la mayor fracción. Sin este paso, una réplica falsa (recargos sumados antes del multiplicador) salía «identificada» con 7 consultas y daba **85 %**; con él, 100 % en 12.

## 6. Veredicto único

`certificada | ambigua | incompleta | refutada`, compartido por CLI y simulador. Solo se emite el archivo con `certificada`; forzarlo queda marcado.

## 7. Simular antes de gastar

Construye oráculos simulados independientes (cuerpo literal del motor conocido, variante de orden, H1 aleatoria, estructura ajena) y corre el solver completo contra ellos. Si no recupera las cuatro con el presupuesto, el método falla antes de tocar el real.

## Gotchas

- Igualdad estricta de flotantes: mismos literales y mismo orden de operaciones (`price *= 1.2` y luego sumar no da los mismos bits que otro orden). Evita z3 o racionales para lo que se compara en IEEE-754: evalúa siempre la función real.
- Un resultado muestreado nunca certifica ni refuta.
- Consultas idénticas pueden no consumir presupuesto: compruébalo, sirve para verificar determinismo gratis.
- En esta máquina `grep` es `ugrep` y rechaza `.{0,120}`: usa `command grep`.
