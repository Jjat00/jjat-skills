"""Piezas compartidas del estilo jato.run para generar frames (fondo, red de partículas, HUD, fuentes).

Se importa desde los scripts del proyecto que generan los cuadros de estilo:
    sys.path.insert(0, "<SKILL>/scripts"); from comun import css, particle_net, corners, hud, template
Las rutas de fuentes son relativas a la raíz del proyecto (assets/fonts/...).
"""
import math
import random

FONTS = """
@font-face { font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-Regular.ttf") format("truetype"); font-weight: 400; }
@font-face { font-family: "Poppins"; src: url("assets/fonts/Poppins-SemiBold.ttf") format("truetype"); font-weight: 600; }
@font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono-400.woff2") format("woff2"); font-weight: 400; }
@font-face { font-family: "JetBrains Mono"; src: url("assets/fonts/JetBrainsMono-700.woff2") format("woff2"); font-weight: 700; }
"""

BASE_CSS = """
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; font-family: "Poppins", sans-serif; color: #ededed; }
.{p}-bg { position: absolute; inset: 0; background: radial-gradient(120% 80% at 50% 40%, #121212 0%, #0a0a0a 55%, #050505 100%); }
.{p}-net { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.{p}-hud { position: absolute; left: 65px; right: 65px; top: 56px; height: 44px; display: flex; justify-content: space-between; align-items: center;
  font-family: "JetBrains Mono", monospace; font-size: 22px; letter-spacing: .06em; color: #8f8f8a; border-bottom: 1px solid #232323; }
.{p}-hud b { color: #a1a09a; font-weight: 700; }
.{p}-kicker { position: absolute; left: 0; right: 0; top: 140px; text-align: center; font-family: "JetBrains Mono", monospace; font-weight: 700;
  font-size: 30px; letter-spacing: .14em; color: #9fe3f5; text-transform: uppercase; }
.{p}-kicker i { display: inline-block; width: 14px; height: 14px; border-radius:0; margin-right: 16px; vertical-align: 3px;
  background: linear-gradient(135deg, #9fe3f5, #c4b5fd); }
.{p}-spec { position: absolute; border-radius:0; border: 1px solid #232323; box-shadow: 0 30px 80px rgba(0,0,0,.55); overflow: hidden; background: #111110; }
.{p}-spec img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.{p}-corner { position: absolute; width: 28px; height: 28px; border-color: #9fe3f5; border-style: solid; border-width: 0; }
.{p}-meta { position: absolute; font-family: "JetBrains Mono", monospace; font-size: 22px; color: #8f8f8a; letter-spacing: .04em; }
.{p}-meta b { color: #a1a09a; font-weight: 400; }
"""


def css(prefix):
    return FONTS + BASE_CSS.replace("{p}", prefix)


def particle_net(prefix, seed=3):
    """Dos cúmulos deterministas (arriba-derecha y abajo-izquierda), puntos + líneas < 110 px."""
    rnd = random.Random(seed)
    pts = []
    for cx, cy, n in ((900, 330, 34), (170, 1790, 30)):
        for _ in range(n):
            a = rnd.random() * math.tau
            r = (rnd.random() ** 0.6) * 230
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8, rnd.choice(["#9fe3f5", "#c4b5fd", "#a8c5ff"]), 1.6 + rnd.random() * 1.6))
    lines = []
    for i, (x1, y1, *_ ) in enumerate(pts):
        for x2, y2, *_ in pts[i + 1:]:
            d = math.hypot(x2 - x1, y2 - y1)
            if d < 110:
                lines.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="#9fe3f5" stroke-opacity="{0.28 * (1 - d / 110):.2f}" stroke-width="1"/>')
    dots = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{c}" fill-opacity=".8"/>' for x, y, c, r in pts)
    return f'<svg class="{prefix}-net" id="{prefix}-net" viewBox="0 0 1080 1920" opacity=".55"><g id="{prefix}-net-g">{"".join(lines)}{dots}</g></svg>'


def corners(prefix, x, y, w, h, color="#9fe3f5", ids=True):
    out = []
    spec = [("tl", x - 10, y - 10, "border-top-width:2px;border-left-width:2px"),
            ("tr", x + w - 18, y - 10, "border-top-width:2px;border-right-width:2px"),
            ("bl", x - 10, y + h - 18, "border-bottom-width:2px;border-left-width:2px"),
            ("br", x + w - 18, y + h - 18, "border-bottom-width:2px;border-right-width:2px")]
    for k, cx, cy, b in spec:
        out.append(f'<div class="{prefix}-corner {prefix}-corner-{k}" style="left:{cx}px;top:{cy}px;{b};border-color:{color}"></div>')
    return "".join(out)


def hud(prefix, right=""):
    """HUD superior: la izquierda va vacía a propósito (Jaime pidió quitar el rótulo); a la derecha, la etapa."""
    return f'<div class="{prefix}-hud" id="{prefix}-hud"><span></span><span>{right}</span></div>'


def template(frame_id, duration, body, style, script):
    return f"""<template>
<div id="root" data-composition-id="{frame_id}" data-start="0" data-duration="{duration}" data-width="1080" data-height="1920">
<style>
{style}
</style>
<div class="clip f{frame_id}-bg" id="f{frame_id}-bg" data-start="0" data-duration="{duration}" data-track-index="0"></div>
{body}
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
(function(){{
  window.__timelines = window.__timelines || {{}};
  var tl = gsap.timeline({{ paused: true }});
{script}
  tl.to({{}}, {{ duration: {duration} }}, 0);
  window.__timelines["{frame_id}"] = tl;
}})();
</script>
</div>
</template>
"""
