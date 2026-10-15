"""Mapa 2D de significados: embeddings reales de bge-m3 proyectados con MDS sobre la distancia coseno.

Uso: .vdb-venv/bin/python tools/mapa.py -> assets/data/mapa.json
"""
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.manifold import MDS, TSNE

ROOT = Path(__file__).resolve().parent.parent
GRUPOS = {
    "animales": ["perro", "cachorro", "gato", "lobo", "caballo"],
    "vehículos": ["carro", "camión", "moto", "bus", "bicicleta"],
    "comida": ["pizza", "hamburguesa", "arepa", "taco", "empanada"],
    "dinero": ["factura", "impuesto", "banco", "préstamo", "salario"],
}
palabras = [p for ps in GRUPOS.values() for p in ps]
grupo = [g for g, ps in GRUPOS.items() for _ in ps]
m = SentenceTransformer("BAAI/bge-m3", device="cpu")
v = m.encode(palabras, normalize_embeddings=True)
S = v @ v.T
D = np.clip(1 - S, 0, None)
res = {}
for nombre, xy in (
    ("mds", MDS(n_components=2, dissimilarity="precomputed", random_state=0, n_init=8).fit_transform(D)),
    ("tsne", TSNE(n_components=2, metric="precomputed", init="random", perplexity=5, random_state=0).fit_transform(D)),
):
    # calidad: % de palabras cuyo vecino más cercano en 2D es de su mismo grupo
    d2 = np.linalg.norm(xy[:, None] - xy[None], axis=-1) + np.eye(len(xy)) * 1e9
    ok = np.mean([grupo[i] == grupo[int(np.argmin(d2[i]))] for i in range(len(xy))])
    res[nombre] = (ok, xy)
    print(nombre, "vecino 2D del mismo grupo:", round(float(ok), 2))
mejor = max(res, key=lambda k: res[k][0])
xy = res[mejor][1]
xy = (xy - xy.min(0)) / (xy.max(0) - xy.min(0))
i = {p: k for k, p in enumerate(palabras)}
out = {
    "modelo": "BAAI/bge-m3", "proyeccion": mejor, "dims": int(v.shape[1]),
    "puntos": [{"palabra": p, "grupo": g, "x": round(float(a), 4), "y": round(float(b), 4)} for p, g, (a, b) in zip(palabras, grupo, xy)],
    "sim": {f"{a}-{b}": round(float(S[i[a], i[b]]), 3) for a, b in [("perro", "cachorro"), ("carro", "camión"), ("perro", "factura"), ("carro", "factura"), ("perro", "carro")]},
}
(ROOT / "assets/data/mapa.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
print(mejor, out["sim"])
for p in out["puntos"]:
    print(p)
