"""Experimentos contra el servicio original.

Cada request al original queda en experimentos.jsonl con el formato del README
(id, seq, x_req, hipotesis, request, status, response, conclusion).

Uso como librería:
    from lab.probe import Lab
    lab = Lab()
    lab.reset("s3")                       # nueva secuencia (reset del token)
    lab.msg("PING;64", "PING responde sin estado")
    lab.conclude("responde pong")         # conclusión del último experimento

Uso por consola:
    uv run python -m lab.probe reset s3
    uv run python -m lab.probe msg s3 "PING;64" "hipótesis"
"""

from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

BASE = os.environ["ORIGINAL_URL"]
TOKEN = os.environ.get("TOKEN", "")
LOG = ROOT / "experimentos.jsonl"
MIN_INTERVAL = 0.11  # límite de 10 requests por segundo por token

_lock = threading.Lock()


class Lab:
    def __init__(self, token: str = TOKEN, log: Path = LOG):
        self.client = httpx.Client(base_url=BASE, timeout=10)
        self.token = token
        self.log = log
        self.seq = "s0"
        self._last = 0.0
        self._last_id: int | None = None

    def _next_id(self) -> int:
        if not self.log.exists():
            return 1
        lines = [l for l in self.log.read_text().splitlines() if l.strip()]
        return json.loads(lines[-1])["id"] + 1 if lines else 1

    def _throttle(self) -> None:
        wait = self._last + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()

    def raw(self, method: str, path: str, *, body=None, content=None, token: str | None = "default",
            headers: dict | None = None) -> httpx.Response:
        """Transporte interno sin registro. Para explorar se usa siempre send() o reset()."""
        self._throttle()
        h = dict(headers or {})
        tok = self.token if token == "default" else token
        if tok is not None:
            h["Authorization"] = f"Bearer {tok}"
        return self.client.request(method, path, json=body, content=content, headers=h)

    def reset(self, seq: str, hipotesis: str = "reset: estado inicial del token") -> int:
        """Empieza una secuencia nueva. El reset también queda registrado en el log."""
        self.seq = seq
        return self.send(None, hipotesis, path="/__reset")["status"]

    def send(self, request, hipotesis: str, *, path: str = "/msg", method: str = "POST",
             content: str | bytes | None = None, auth: str = "propio", **kw) -> dict:
        """Manda un request y lo registra en el log.

        `request` es el cuerpo JSON; para cuerpos que no son JSON se pasa `content` (texto crudo)
        y `request` se registra como ese texto. `auth` describe la variante de autenticación
        usada (propio, sin_token, token_invalido, ...) y queda en el log si no es la normal.
        """
        body_mode = "raw" if content is not None else ("json" if request is not None else "none")
        logged = content if isinstance(content, str) else (
            content.decode("utf-8", "replace") if content is not None else request)
        meta = {}
        if path != "/msg" or method != "POST":
            meta["ruta"] = f"{method} {path}"
        if auth != "propio":
            meta["auth"] = auth
        if kw.get("headers"):
            # el token nunca entra al log: M1 reconstruye cada variante desde `auth`
            meta["headers"] = {k: v.replace(self.token, "<TOKEN>") if self.token else v
                               for k, v in kw["headers"].items()}
        while True:
            if content is not None:
                resp = self.raw(method, path, content=content, **kw)
            else:
                resp = self.raw(method, path, body=request, **kw)
            if resp.headers.get("X-Infra") != "rate-limit":
                break
            self._write({"seq": self.seq, "x_req": resp.headers.get("X-Req"), "infra": "rate-limit",
                         "hipotesis": f"(reintento) {hipotesis}", "request": logged,
                         "status": resp.status_code, "response": resp.text, "body_mode": body_mode, **meta})
            time.sleep(1)
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        with _lock:
            row = {
                "id": self._next_id(),
                "seq": self.seq,
                "x_req": resp.headers.get("X-Req"),
                "hipotesis": hipotesis,
                "request": logged,
                "status": resp.status_code,
                "response": body,
                "body_mode": body_mode,
                **meta,
            }
            with self.log.open("a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            self._last_id = row["id"]
        return row

    def _write(self, row: dict) -> None:
        """Escribe una fila extra (p. ej. una respuesta de infraestructura) con el siguiente id."""
        with _lock:
            row = {"id": self._next_id(), **row}
            with self.log.open("a") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def msg(self, m: str, hipotesis: str) -> dict:
        return self.send({"m": m}, hipotesis)

    def conclude(self, conclusion: str, ids: list[int] | None = None) -> None:
        """Agrega la conclusión a uno o varios experimentos (por defecto, el último)."""
        targets = set(ids or [self._last_id])
        rows = [json.loads(l) for l in self.log.read_text().splitlines() if l.strip()]
        for r in rows:
            if r["id"] in targets:
                r["conclusion"] = conclusion
        self.log.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def main() -> None:
    lab = Lab()
    cmd, *args = sys.argv[1:]
    if cmd == "reset":
        print(lab.reset(args[0]))
    elif cmd == "msg":
        lab.seq = args[0]
        print(json.dumps(lab.msg(args[1], args[2]), ensure_ascii=False))


if __name__ == "__main__":
    main()
