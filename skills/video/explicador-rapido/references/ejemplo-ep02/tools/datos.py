"""Datos reales para el guion: embeddings, similitudes y tiempos de búsqueda.

Uso: .vdb-venv/bin/python tools/datos.py  -> escribe assets/data/datos.json
"""
import json
import time
from pathlib import Path

import hnswlib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

SALIDA = Path(__file__).resolve().parent.parent / "assets" / "data" / "datos.json"
MODELO = "BAAI/bge-m3"

modelo = SentenceTransformer(MODELO, device="cpu")


def emb(textos):
    return modelo.encode(textos, normalize_embeddings=True)


def cos(a, b):
    return float(np.dot(a, b))


datos = {"modelo": MODELO}

# 1. Exacto vs significado
consulta = "tenis para correr bajo la lluvia"
catalogo = [
    "zapatillas impermeables para trotar",
    "chaqueta rompevientos para running",
    "zapatos de cuero para oficina",
    "botas de caucho para niños",
    "tenis de mesa profesional",
    "paraguas plegable negro",
    "licuadora de 600 vatios",
]
v = emb([consulta] + catalogo)
datos["busqueda"] = {
    "consulta": consulta,
    "exacta_sql": [t for t in catalogo if "tenis" in t],
    "resultados": sorted(
        [{"texto": t, "sim": round(cos(v[0], v[i + 1]), 3)} for i, t in enumerate(catalogo)],
        key=lambda r: -r["sim"],
    ),
}

# 2. Un embedding de verdad
e = emb(["perro"])[0]
datos["embedding_perro"] = {"dims": int(e.shape[0]), "primeros": [round(float(x), 3) for x in e[:12]]}

# 3. Mapa 2D de palabras
palabras = ["perro", "cachorro", "gato", "lobo", "carro", "moto", "bus", "camión",
            "pizza", "hamburguesa", "arepa", "taco", "factura", "impuesto", "banco", "préstamo"]
vp = emb(palabras)
xy = PCA(n_components=2, random_state=0).fit_transform(vp)
datos["mapa"] = [{"palabra": p, "x": round(float(a), 3), "y": round(float(b), 3)} for p, (a, b) in zip(palabras, xy)]
datos["pares"] = {
    "perro-cachorro": round(cos(vp[0], vp[1]), 3),
    "perro-gato": round(cos(vp[0], vp[2]), 3),
    "perro-factura": round(cos(vp[0], vp[12]), 3),
}

# 4. Analogía rey - hombre + mujer
va = emb(["rey", "hombre", "mujer", "reina", "princesa", "príncipe", "señora", "monarca"])
obj = va[0] - va[1] + va[2]
obj /= np.linalg.norm(obj)
datos["analogia"] = sorted(
    [{"palabra": p, "sim": round(cos(obj, va[i]), 3)} for i, p in
     [(3, "reina"), (4, "princesa"), (5, "príncipe"), (6, "señora"), (7, "monarca")]],
    key=lambda r: -r["sim"],
)

# 5. Fuerza bruta vs HNSW sobre N vectores de 384 dimensiones
N, D, K = 200_000, 1024, 10
rng = np.random.default_rng(0)
# vectores con estructura (mezcla de 2000 centros) para que el índice se comporte como con datos reales
centros = rng.standard_normal((2000, D)).astype(np.float32)
X = np.empty((N, D), dtype=np.float32)
for i in range(0, N, 50_000):
    b = centros[rng.integers(0, 2000, min(50_000, N - i))]
    b += 0.6 * rng.standard_normal(b.shape, dtype=np.float32)
    X[i:i + len(b)] = b / np.linalg.norm(b, axis=1, keepdims=True)
Q = X[rng.integers(0, N, 100)] + 0.05 * rng.standard_normal((100, D)).astype(np.float32)
Q /= np.linalg.norm(Q, axis=1, keepdims=True)

t = time.perf_counter()
exactos = [np.argpartition(-(X @ q), K)[:K] for q in Q]
t_bruta = (time.perf_counter() - t) / len(Q)

idx = hnswlib.Index(space="cosine", dim=D)
idx.init_index(max_elements=N, ef_construction=200, M=32)
t = time.perf_counter()
idx.add_items(X, num_threads=-1)
t_build = time.perf_counter() - t
idx.set_ef(200)
t = time.perf_counter()
etq, _ = idx.knn_query(Q, k=K, num_threads=1)
t_hnsw = (time.perf_counter() - t) / len(Q)
recall = float(np.mean([len(set(a) & set(b)) / K for a, b in zip(etq, exactos)]))

datos["velocidad"] = {
    "n": N, "dims": D, "k": K,
    "bruta_ms": round(t_bruta * 1000, 2),
    "hnsw_ms": round(t_hnsw * 1000, 3),
    "acelera": round(t_bruta / t_hnsw, 1),
    "recall": round(recall, 3),
    "construccion_s": round(t_build, 1),
    "memoria_mb_float32": round(N * D * 4 / 1e6),
}

SALIDA.parent.mkdir(parents=True, exist_ok=True)
SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2))
print(json.dumps(datos, ensure_ascii=False, indent=2))
