"""Ensambla index.html de un reel editorial.

Lee, desde la raíz del proyecto HyperFrames:
  reel.json              duración, tramos de composición, palabras clave, efectos y tecleos
  assets/words.json      palabras con marcas medidas sobre assets/edit.mp4
  work/overlays.html     textos sobre la pantalla completa (clips)
  work/panels.html       paneles de la pantalla dividida (clips)
  work/scenes.js         animaciones GSAP de overlays y paneles (usa `tl`, `pop`, `rise`, `show`)
y la plantilla base de la skill (assets/template.html).

Uso: python <skill>/scripts/build.py <raíz-del-proyecto>
"""

import html
import json
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
CFG = json.loads((ROOT / "reel.json").read_text())
WORDS = json.loads((ROOT / "assets/words.json").read_text())
D = float(CFG["duration"])
WINDOWS = CFG["windows"]
CARD = {"red": "#E0301E", "blue": "#2F4BE0", **CFG.get("card_colors", {})}
KEYWORDS = {k.lower() for k in CFG.get("keywords", [])}


def layout_at(t: float) -> str:
    for w in WINDOWS:
        if w["start"] <= t < w["end"]:
            return w["layout"]
    return WINDOWS[-1]["layout"]


# ---------- subtítulos: grupos de hasta 3 palabras; cortan en puntuación, pausas o cambio de composición ----------
groups, cur = [], []
for i, w in enumerate(WORDS):
    cur.append(w)
    nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    brk = (
        len(cur) >= CFG.get("words_per_caption", 3)
        or re.search(r"[.,?!:;]$", w["text"])
        or (nxt and nxt["start"] - w["end"] > 0.35)
        or (nxt and layout_at(nxt["start"]) != layout_at(cur[0]["start"]))
    )
    if brk or not nxt:
        groups.append(cur)
        cur = []

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    start = g[0]["start"]
    nxt_start = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else D
    end = min(nxt_start, g[-1]["end"] + 0.45, D)
    pos = "cap-split" if layout_at(start + 0.01) == "split" else "cap-full"
    spans = []
    for wi, w in enumerate(g):
        key = re.sub(r"[^\wáéíóúüñ]", "", w["text"].lower()) in KEYWORDS
        spans.append(f'<span id="w{gi}_{wi}" class="w{" key" if key else ""}">{html.escape(w["text"])}</span>')
        cap_js.append(
            f'tl.fromTo("#w{gi}_{wi}",{{opacity:0,scale:0.82}},'
            f'{{opacity:1,scale:1,duration:0.14,ease:"back.out(2.4)"}},{w["start"]:.3f});'
        )
    cap_html.append(f'<div id="g{gi}" class="cap {pos}">{" ".join(spans)}</div>')
    cap_js.append(f'tl.set("#g{gi}",{{opacity:1}},{start:.3f});tl.set("#g{gi}",{{opacity:0}},{end:.3f});')

# ---------- cambios de composición ----------
layout_js = []
for w in WINDOWS:
    a, b = w["start"], w["end"]
    if w["layout"] == "full":
        z0, z1 = w.get("zoom", [1.0, 1.05])
        layout_js.append(f'tl.set("#full",{{opacity:1}},{a:.3f});tl.set("#split",{{opacity:0}},{a:.3f});')
        layout_js.append(
            f'tl.fromTo("#full-zoom",{{scale:{z0 + 0.06:.3f}}},'
            f'{{scale:{z0:.3f},duration:0.35,ease:"power3.out",immediateRender:false}},{a:.3f});'
        )
        layout_js.append(f'tl.to("#full-zoom",{{scale:{z1:.3f},duration:{max(b - a - 0.35, 0.1):.3f},ease:"none"}},{a + 0.35:.3f});')
    else:
        color = CARD.get(w.get("card", "red"), w.get("card", "#E0301E"))
        layout_js.append(f'tl.set("#split",{{opacity:1}},{a:.3f});tl.set("#full",{{opacity:0}},{a:.3f});')
        layout_js.append(f'tl.set("#card",{{backgroundColor:"{color}"}},{a:.3f});')
        layout_js.append(
            f'tl.fromTo("#paper",{{yPercent:-100}},'
            f'{{yPercent:0,duration:0.42,ease:"power4.out",immediateRender:false}},{a:.3f});'
        )
        layout_js.append(
            f'tl.fromTo("#card-wrap",{{y:260,scale:0.92}},'
            f'{{y:0,scale:1,duration:0.5,ease:"power3.out",immediateRender:false}},{a + 0.08:.3f});'
        )

# ---------- efectos: whoosh automático en cada cambio de composición + los de reel.json ----------
sfx_dir = CFG.get("sfx_dir", "assets/sfx")
SFX = []
if CFG.get("auto_whoosh", True):
    SFX += [{"name": CFG.get("whoosh", "whoosh-corto"), "at": w["start"], "volume": 0.35} for w in WINDOWS[1:]]
SFX += CFG.get("sfx", [])
lens = {}
for name in {s["name"] for s in SFX}:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ROOT / sfx_dir / f"{name}.mp3")],
        capture_output=True, text=True, check=True,
    )
    lens[name] = round(float(out.stdout.strip()), 3)
sfx_html = "\n".join(
    f'<audio id="sfx{i}" src="{sfx_dir}/{s["name"]}.mp3" data-start="{s["at"]:.3f}" data-duration="{lens[s["name"]]}" '
    f'data-track-index="{20 + i % 4}" data-volume="{s.get("volume", 0.3)}"></audio>'
    for i, s in enumerate(sorted(SFX, key=lambda s: s["at"]))
)

# ---------- tecleos: <!--__TYPE:<id>__--> en panels.html se llena carácter a carácter ----------
panels = (ROOT / "work/panels.html").read_text()
type_js = []
for ty in CFG.get("typing", []):
    pid, text = ty["id"], ty["text"]
    step = (ty["end"] - ty["start"]) / max(len(text), 1)
    chars = "".join(f'<span id="{pid}{i}" class="c">{html.escape(ch)}</span>' for i, ch in enumerate(text))
    panels = panels.replace(f"<!--__TYPE:{pid}__-->", chars)
    type_js += [f'tl.set("#{pid}{i}",{{opacity:1}},{ty["start"] + i * step:.3f});' for i in range(len(text))]

page = (SKILL / "assets/template.html").read_text()
page = page.replace("<!--__OVERLAYS__-->", (ROOT / "work/overlays.html").read_text())
page = page.replace("<!--__PANELS__-->", panels)
page = page.replace("/*__SCENES_JS__*/", (ROOT / "work/scenes.js").read_text() + "\n" + "\n".join(type_js))
page = page.replace("/*__LAYOUT__*/", "\n".join(layout_js))
page = page.replace("/*__CAPTIONS__*/", "\n".join(cap_js))
page = page.replace("<!--__CAPTIONS__-->", "\n".join(cap_html))
page = page.replace("<!--__SFX__-->", sfx_html)
page = page.replace("__DURATION__", f"{D}")
(ROOT / "index.html").write_text(page)
print(f"index.html: {len(groups)} grupos de subtítulos, {len(SFX)} efectos, {len(CFG.get('typing', []))} tecleos, {D} s")
