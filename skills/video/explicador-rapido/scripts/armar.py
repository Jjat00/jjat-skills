"""Arma el video: index.html con todas las escenas, la voz y el fundido entre escenas, y compositions/captions.html con
los subtítulos palabra a palabra. Luego corre el lint de HyperFrames. Se puede repetir cuantas veces haga
falta: reescribe los dos archivos desde cero.

  python3 <SKILL>/scripts/armar.py --root .

Lee STORYBOARD.md (el orden de las escenas, su `src` y su `transition_in`) y audio_meta.json (de alinear.py: cuándo
empieza cada escena, cuánto dura su voz y el tiempo de cada palabra). Sigue el contrato actual de HyperFrames: el
host de cada escena lleva el mismo id que su `data-composition-id` y que la clave de su timeline; las escenas van en
la pista `graphics` y los subtítulos en un solo host de la pista `captions`.

El aspecto de los subtítulos sale de subtitulos.json en la raíz del proyecto, si existe (fuente, tamaño, colores y
banda; ver ESTILO_SUBTITULOS abajo); si no, del estilo base de la skill. Si el proyecto tiene tools/despues_de_armar.py, lo corre antes del lint: ahí van capas propias del episodio (p. ej. un
botón SEGUIR encima del video).
"""
import argparse
import html
import json
import re
import subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".")
ap.add_argument("--fundido", type=float, default=0.5, help="segundos del fundido cruzado entre escenas")
ap.add_argument("--sin-zona-segura", action="store_true", help="no reducir las escenas para el recorte 4:5 del feed")
ap.add_argument("--max-palabras", type=int, default=3, help="palabras por grupo de subtítulos")
ap.add_argument("--sin-lint", action="store_true")
a = ap.parse_args()
ROOT = Path(a.root).resolve()
W, H = 1080, 1920
F = a.fundido

# Aspecto de los subtítulos. El proyecto lo cambia con un subtitulos.json que trae solo las claves que quiere cambiar.
ESTILO_SUBTITULOS = {
    "fuente": "Poppins",                 # familia
    "archivo": "Poppins-SemiBold.ttf",   # en assets/fonts/; null si la fuente viene con HyperFrames o el sistema
    "peso": 600,
    "tamano": 54,                        # px antes de la zona segura
    "mayusculas": False,
    "viene": "rgba(237, 237, 237, 0.38)",  # palabras que todavía no se dicen
    "activa": "#9fe3f5",                 # la que suena
    "dicha": "#ededed",                  # las ya dichas
    "cifra": "#c4b5fd",                  # una cifra mientras suena
    "sombra": "0 2px 14px rgba(0, 0, 0, 0.85), 0 0 2px rgba(0, 0, 0, 0.9)",
    "banda_arriba": 1445,                # px desde arriba, antes de la zona segura
    "banda_alto": 170,
}
propio = ROOT / "subtitulos.json"
if propio.exists():
    ESTILO_SUBTITULOS.update(json.loads(propio.read_text()))
E = ESTILO_SUBTITULOS

# --- escenas: el orden y el archivo salen del storyboard; los tiempos, de audio_meta.json ---------------------------
sb = (ROOT / "STORYBOARD.md").read_text()
escenas = []
for m in re.finditer(r"(?ms)^## Frame (\d+) — .*?(?=^## Frame|\Z)", sb):
    src = re.search(r"- src: (compositions/frames/(\S+)\.html)", m.group(0))
    if not src:
        raise SystemExit(f"armar: la escena {m.group(1)} no tiene «- src: compositions/frames/<id>.html»")
    trans = re.search(r"- transition_in: (\S+)", m.group(0))
    escenas.append({"n": int(m.group(1)), "src": src.group(1), "id": src.group(2), "trans": trans.group(1) if trans else "crossfade"})

voces = {v["frame"]: v for v in json.loads((ROOT / "audio_meta.json").read_text())["voices"]}
for e in escenas:
    v = voces.get(e["n"])
    if not v:
        raise SystemExit(f"armar: audio_meta.json no tiene la voz de la escena {e['n']} ({e['id']}); corre alinear.py")
    if not (ROOT / e["src"]).exists():
        raise SystemExit(f"armar: falta {e['src']}")
    # el id del host tiene que ser el data-composition-id de la escena (si no, cada render espera 45 s por escena)
    cid = re.search(r'data-composition-id="([^"]+)"', (ROOT / e["src"]).read_text())
    if not cid or cid.group(1) != e["id"]:
        raise SystemExit(f"armar: {e['src']} debe tener data-composition-id=\"{e['id']}\" en su raíz")
    e.update(ini=float(v["start_global"]), dur=float(v["duration_s"]), voz=v["path"], palabras=v.get("words", []))

total = round(escenas[-1]["ini"] + escenas[-1]["dur"] + F, 3)
r3 = lambda x: f"{x:.3f}".rstrip("0").rstrip(".")

# --- index.html ------------------------------------------------------------------------------------------------------
hosts, audios, tweens = [], [], []
for i, e in enumerate(escenas):
    ultima = i == len(escenas) - 1
    # cada escena dura lo que su voz más el fundido, para cruzarse con la siguiente
    dur = (total - e["ini"]) if ultima else e["dur"] + F
    hosts.append(
        f'      <div id="{e["id"]}" class="escena" data-composition-id="{e["id"]}" data-composition-src="{e["src"]}"\n'
        f'        data-start="{r3(e["ini"])}" data-duration="{r3(dur)}" data-track-index="{1 + i % 2}" data-track-kind="graphics"\n'
        f'        style="z-index: {i + 1}"></div>'
    )
    audios.append(
        f'      <audio id="voz-{e["n"]:02d}" class="clip" src="{e["voz"]}" data-start="{r3(e["ini"])}" data-duration="{r3(e["dur"])}"'
        f' data-track-index="10" data-volume="1"></audio>'
    )
    if i and e["trans"] != "cut":
        prev = escenas[i - 1]["id"]
        # por id y no con selector «#…»: un id que empieza con número (01-gancho) no es un selector CSS válido
        tweens.append(f'      tl.fromTo(el("{e["id"]}"), {{ opacity: 0 }}, {{ opacity: 1, duration: {F}, ease: "power2.inOut" }}, {r3(e["ini"])});')
        tweens.append(f'      tl.to(el("{prev}"), {{ opacity: 0, duration: {F}, ease: "power2.inOut" }}, {r3(e["ini"])});')

zona = "" if a.sin_zona_segura else """
      /* zona segura del feed de Instagram: sin abrir el reel, el feed lo recorta a 4:5 por el centro (y≈285–1635).
         Escenas y subtítulos se reducen y bajan; el contenido de cada escena (y=140–1440) cae en ~305–1430. */
      .escena { transform: translate(0px, 184px) scale(0.865); transform-origin: 540px 0px; mix-blend-mode: lighten; }
      .escena [id$="-bg"] { background: transparent !important; }"""

index = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      html, body {{ margin: 0; background: #050505; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; }}
      #fondo {{ position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 45%, #121212 0%, #0a0a0a 55%, #050505 100%); }}
      .escena {{ position: absolute; inset: 0; }}{zona}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{r3(total)}" data-width="{W}" data-height="{H}">
      <div id="fondo" class="clip" data-start="0" data-duration="{r3(total)}" data-track-index="0"></div>
{chr(10).join(hosts)}
{chr(10).join(audios)}
      <div id="captions" class="escena" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{r3(total)}" data-track-index="20" data-track-kind="captions" style="z-index: 100"></div>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const el = (id) => document.getElementById(id);
      // fundido cruzado entre escenas (las que piden transition_in: cut entran de golpe)
{chr(10).join(tweens)}
      tl.to({{}}, {{ duration: {r3(total)} }}, 0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
(ROOT / "index.html").write_text(index)

# --- subtítulos ------------------------------------------------------------------------------------------------------
# Grupos de 2 a 3 palabras, el ritmo de un reel: se corta al final de una frase, en una pausa de 150 ms o más, al
# llegar a --max-palabras y siempre al cambiar de escena. Un solo grupo visible a la vez, con cierre forzado al terminar.
palabras = []
for e in escenas:
    for w in e["palabras"]:
        palabras.append({"t": str(w["text"]), "ini": e["ini"] + float(w["start"]), "fin": e["ini"] + float(w["end"]), "escena": e["n"]})

grupos, actual = [], []
for i, w in enumerate(palabras):
    actual.append(w)
    sig = palabras[i + 1] if i + 1 < len(palabras) else None
    corta = (
        sig is None
        or len(actual) >= a.max_palabras
        or sig["escena"] != w["escena"]
        or re.search(r"[.?!:;…»]$", w["t"])
        or (w["t"].endswith(",") and len(actual) >= 2)
        or (sig["ini"] - w["fin"] >= 0.15 and len(actual) >= 2)
    )
    if corta:
        grupos.append(actual)
        actual = []

marcado, lineas_js = [], []
for g, ws in enumerate(grupos):
    ini = max(0.1, ws[0]["ini"] - 0.05)
    sig = grupos[g + 1][0]["ini"] - 0.05 if g + 1 < len(grupos) else total
    fin = max(ini + 0.2, min(sig, ws[-1]["fin"] + 0.3))
    spans = "".join(
        f'<span id="cap-{g}-{k}" class="cap-palabra{" cap-num" if re.search(r"[0-9%]", w["t"]) else ""}">{html.escape(w["t"])}</span>'
        for k, w in enumerate(ws)
    )
    marcado.append(f'      <div id="cap-{g}" class="cap-grupo"><div class="cap-linea">{spans}</div></div>')
    tiempos = ", ".join("%.3f" % w["ini"] for w in ws)
    lineas_js.append(f"      grupo({g}, {ini:.3f}, {fin:.3f}, [{tiempos}], {min(fin, ws[-1]['fin'] + 0.1):.3f});")

fuente = (
    f'@font-face {{ font-family: "{E["fuente"]}"; src: url("assets/fonts/{E["archivo"]}"); font-weight: {E["peso"]}; }}'
    if E.get("archivo")
    else ""
)
captions = f"""<template>
  <style>
    {fuente}
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    /* la banda de subtítulos, antes de la zona segura del feed */
    .cap-banda {{ position: absolute; left: 0; right: 0; top: {E["banda_arriba"]}px; height: {E["banda_alto"]}px; }}
    .cap-grupo {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; visibility: hidden; overflow: visible; }}
    .cap-linea {{
      max-width: 86%; display: flex; flex-wrap: wrap; justify-content: center; gap: 0.1em 0.28em;
      font-family: "{E["fuente"]}", sans-serif; font-weight: {E["peso"]}; font-size: {E["tamano"]}px; line-height: 1.2;
      letter-spacing: -0.01em; text-shadow: {E["sombra"]};{" text-transform: uppercase;" if E["mayusculas"] else ""}
    }}
    .cap-palabra {{ display: inline-block; color: {E["viene"]}; }}
    .cap-palabra.activa {{ color: {E["activa"]}; }}
    .cap-palabra.dicha {{ color: {E["dicha"]}; }}
    .cap-palabra.cap-num.activa {{ color: {E["cifra"]}; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
    <div class="cap-banda">
{chr(10).join(marcado)}
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    // estados con tl.set dentro del timeline: se aplican en cada salto de cuadro (un tl.call() no lo haría el render)
    // la última palabra sigue activa hasta que termina de decirse (finUltima)
    function grupo(g, ini, fin, tiempos, finUltima) {{
      const el = document.getElementById("cap-" + g);
      tl.set(el, {{ opacity: 1, visibility: "visible" }}, ini);
      tiempos.forEach(function (t, k) {{
        const w = document.getElementById("cap-" + g + "-" + k);
        const base = w.classList.contains("cap-num") ? "cap-palabra cap-num" : "cap-palabra";
        tl.set(w, {{ className: base }}, ini);
        tl.set(w, {{ className: base + " activa" }}, Math.max(ini, t));
        if (k + 1 < tiempos.length) tl.set(w, {{ className: base + " dicha" }}, Math.max(ini, tiempos[k + 1]));
        else tl.set(w, {{ className: base + " dicha" }}, Math.max(t, finUltima));
        tl.fromTo(w, {{ scale: 0.98 }}, {{ scale: 1, duration: 0.16, ease: "power1.out", immediateRender: false }}, Math.max(ini, t));
      }});
      tl.to(el, {{ opacity: 0, duration: 0.12, ease: "power2.in" }}, fin - 0.12);
      tl.set(el, {{ opacity: 0, visibility: "hidden" }}, fin);
    }}
{chr(10).join(lineas_js)}
    tl.to({{}}, {{ duration: {r3(total)} }}, 0);
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
(ROOT / "compositions").mkdir(exist_ok=True)
(ROOT / "compositions" / "captions.html").write_text(captions)
print(f"index.html: {len(escenas)} escenas, {r3(total)} s · compositions/captions.html: {len(grupos)} grupos, {len(palabras)} palabras")

gancho = ROOT / "tools" / "despues_de_armar.py"
if gancho.exists():
    subprocess.run(["python3", str(gancho)], cwd=ROOT, check=True)

if not a.sin_lint:
    # la versión de HyperFrames que fijó el proyecto en package.json (init la fija); si no hay, la última
    pkg = ROOT / "package.json"
    pin = re.search(r"hyperframes@([0-9][^\s\"']*)", pkg.read_text()) if pkg.exists() else None
    subprocess.run(["npx", "--yes", f"hyperframes@{pin.group(1) if pin else 'latest'}", "lint"], cwd=ROOT)
