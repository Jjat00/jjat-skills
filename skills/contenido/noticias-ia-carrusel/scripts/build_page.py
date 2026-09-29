"""Arma la página de descarga (Artifact) con las láminas ya renderizadas.

Uso:
  python build_page.py <carpeta>/plan.json --out <scratchpad>/pagina

Copia carrusel/ -> <out>/slides/ y carrusel_tiktok/ -> <out>/tiktok/ y escribe <out>/index.html.
El Artifact tool solo publica archivos bajo el directorio de trabajo o el scratchpad: por eso --out.
Luego se publica con: Artifact(file_path=<out>/index.html, root=<out>, files=[slides/*, tiktok/*],
capabilities={"downloads": true}). Los enlaces <a download> no funcionan en un Artifact; la página usa
la capacidad `downloads`.
"""
import argparse, datetime as dt, json, pathlib, re, shutil, subprocess

SKILL = pathlib.Path(__file__).resolve().parent.parent
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def plain(html, n=48):
    t = re.sub(r"<[^>]+>", "", html).strip()
    return t if len(t) <= n else t[: n - 1].rstrip() + "…"


def dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    return f"{round(float(out))} s" if out else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plan_path = pathlib.Path(a.plan).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    out = pathlib.Path(a.out).resolve()
    for sub, src in (("slides", "carrusel"), ("tiktok", "carrusel_tiktok")):
        d = out / sub
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(base / src, d)

    slides = []
    for i, s in enumerate(plan["slides"]):
        n = f"{i + 1:02d}"
        mp4 = base / "carrusel" / f"{n}.mp4"
        file = f"{n}.mp4" if mp4.exists() else f"{n}.png"
        kind = s.get("kind", "news")
        label = "Portada" if kind == "cover" else "Cierre" if kind == "cta" else plain(s["title"])
        slides.append({"file": file, "label": label, "dur": dur(mp4) if mp4.exists() else ""})

    f = dt.date.fromisoformat(plan["fecha"])
    data = {
        "fecha_texto": f"{DIAS[f.weekday()]} {f.day} {MESES[f.month - 1]} {f.year}",
        "titular_html": plan.get("titular_pagina", "Las <b>noticias de IA</b> de las últimas 24 horas"),
        "nota": plan["publicacion"].get("nota", ""),
        "fuentes": plan.get("fuentes_pagina", ""),
        "prefijo": f"ia_{f.day:02d}{MESES[f.month - 1]}_",
        "publicacion": plan["publicacion"],
        "slides": slides,
    }
    title = f"Carrusel IA {f.day} {MESES[f.month - 1]}"
    tpl = (SKILL / "assets" / "page_template.html").read_text(encoding="utf-8")
    html = tpl.replace("__TITLE__", title).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (out / "index.html").write_text(html, encoding="utf-8")
    files = sorted(str(p.relative_to(out)) for p in out.glob("*/*") if p.is_file())
    print(json.dumps({"index": str(out / "index.html"), "root": str(out), "files": files}, ensure_ascii=False))


main()
