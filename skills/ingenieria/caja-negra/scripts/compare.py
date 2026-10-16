"""Comparador oficial (MATERIAL.md, «Cómo se evalúa»).

Un paso coincide si el status es igual y el cuerpo también: si los dos cuerpos son JSON se
comparan sin orden de claves, con los arrays en orden y con strings y números idénticos
(1 != 1.0 != true); si alguno no es JSON, se compara el texto exacto.

Uso por consola: python -m lab.compare esperado.jsonl obtenido.jsonl
(cada línea con "status" y "response"; se informa el primer paso que difiere).
"""

from __future__ import annotations

import json
import sys

_NO_JSON = object()


def _parsear(texto: str):
    try:
        return json.loads(texto)
    except ValueError:
        return _NO_JSON


def json_igual(a, b) -> bool:
    """Igualdad estricta de tipos: bool, int y float no se mezclan."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(json_igual(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(json_igual(x, y) for x, y in zip(a, b))
    return a == b


def como_texto(cuerpo) -> str:
    """Un cuerpo del log: str = texto crudo; cualquier otra cosa = JSON ya parseado."""
    if isinstance(cuerpo, str):
        return cuerpo
    return json.dumps(cuerpo, ensure_ascii=False, separators=(",", ":"))


def comparar_paso(status_esp: int, cuerpo_esp: str, status_obt: int, cuerpo_obt: str) -> str | None:
    """None si coinciden; si no, el motivo."""
    if status_esp != status_obt:
        return f"status {status_obt} != {status_esp}"
    a, b = _parsear(cuerpo_esp), _parsear(cuerpo_obt)
    if a is _NO_JSON or b is _NO_JSON:
        return None if cuerpo_esp == cuerpo_obt else f"texto {cuerpo_obt!r} != {cuerpo_esp!r}"
    return None if json_igual(a, b) else f"cuerpo {cuerpo_obt} != {cuerpo_esp}"


def primer_diferente(esperados: list[tuple[int, str]], obtenidos: list[tuple[int, str]]):
    """Devuelve (índice, motivo) del primer paso que difiere, o None si la secuencia coincide."""
    if len(esperados) != len(obtenidos):
        return min(len(esperados), len(obtenidos)), "distinto número de pasos"
    for i, ((se, ce), (so, co)) in enumerate(zip(esperados, obtenidos)):
        motivo = comparar_paso(se, ce, so, co)
        if motivo:
            return i, motivo
    return None


def _leer(ruta: str) -> list[tuple[int, str]]:
    with open(ruta, encoding="utf-8") as f:
        filas = [json.loads(l) for l in f if l.strip()]
    return [(r["status"], como_texto(r["response"])) for r in filas]


if __name__ == "__main__":
    diff = primer_diferente(_leer(sys.argv[1]), _leer(sys.argv[2]))
    print("iguales" if diff is None else f"paso {diff[0] + 1}: {diff[1]}")
    sys.exit(0 if diff is None else 1)
