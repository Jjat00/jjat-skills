"""Renderiza el carrusel a partir de un plan.json.

Uso:
  uv run --with playwright python render.py <carpeta>/plan.json --mode ig      # 4:5, videos MP4 + imágenes PNG
  uv run --with playwright python render.py <carpeta>/plan.json --mode tiktok  # 9:16, solo PNG
  ... --only 4 7        # re-renderiza solo esas láminas

Los medios se buscan en <carpeta>/medios/. La salida va a <carpeta>/carrusel/ o <carpeta>/carrusel_tiktok/.
Las láminas de video se hacen así: Playwright captura el marco (texto + fondo) como PNG con un hueco
transparente donde va el medio, y ffmpeg monta el video debajo, conservando el audio original.
"""
import argparse, asyncio, html as H, json, pathlib, random, subprocess
from playwright.async_api import async_playwright

SKILL = pathlib.Path(__file__).resolve().parent.parent
CSS = (SKILL / "assets" / "slide.css").read_text(encoding="utf-8")

MODES = {
    # h: alto; pad: padding de .page; hero/h2: portada; tagtop: etiqueta de portada
    "ig": dict(h=1350, pad="56px 52px 60px", hero=800, h2bottom=70, h2size=88, tagtop=52, cta_pad=120),
    # TikTok tapa la franja de abajo (caption) y el borde derecho (botones): se dejan libres.
    "tiktok": dict(h=1920, pad="150px 130px 290px 52px", hero=1180, h2bottom=380, h2size=92, tagtop=150, cta_pad=170),
}

PLEXUS_JS = """
(() => {
  const c = document.getElementById('plexus'); if (!c) return;
  const W = c.width = 1080, Hh = c.height = document.body.clientHeight;
  const x = c.getContext('2d');
  let seed = %SEED%; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  const holes = [...document.querySelectorAll('.media')].map(e => e.getBoundingClientRect());
  x.beginPath(); x.rect(0, 0, W, Hh);
  for (const r of holes) x.rect(r.x - 4, r.y - 4, r.width + 8, r.height + 8);
  x.clip('evenodd');
  const hues = [[190,80,60],[253,75,70],[220,70,65]];
  const P = [];
  // Dos cúmulos, como en el hero de jaimeaza.tech: esquina superior derecha e inferior izquierda.
  for (const [cx, cy, n] of [[W*0.92, Hh*0.08, 70], [W*0.06, Hh*0.94, 60]]) {
    for (let i = 0; i < n; i++) {
      const a = rnd() * Math.PI * 2, d = Math.pow(rnd(), 0.7) * 330;
      const [h, s, l] = hues[Math.floor(rnd() * 3)];
      P.push({x: cx + Math.cos(a) * d * 1.3, y: cy + Math.sin(a) * d, c: `hsla(${h},${s}%,${l}%,`, al: rnd() * 0.35 + 0.15});
    }
  }
  x.lineWidth = 0.8;
  for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
    const dx = P[i].x - P[j].x, dy = P[i].y - P[j].y, d = Math.hypot(dx, dy);
    if (d < 110) { x.strokeStyle = P[i].c + (1 - d / 110) * 0.28 + ')'; x.beginPath(); x.moveTo(P[i].x, P[i].y); x.lineTo(P[j].x, P[j].y); x.stroke(); }
  }
  for (const p of P) { x.fillStyle = p.c + p.al + ')'; x.beginPath(); x.arc(p.x, p.y, 2.2, 0, 7); x.fill(); }
})();
"""


def is_video(name):
    return str(name).lower().endswith((".mp4", ".webm", ".mov"))


def stat_html(st):
    rows = "".join(
        f'<div class="row"><span>{H.escape(r["label"])}</span><div class="bar"><div class="{"hi" if r.get("hi") else ""}" '
        f'style="width:{r["pct"]}%"></div></div><b>{H.escape(r["valor"])}</b></div>'
        for r in st["filas"])
    foot = f'<div class="foot">{st["pie"]}</div>' if st.get("pie") else ""
    return f'<div class="stat"><div class="lbl">{H.escape(st["titulo"])}</div>{rows}{foot}</div>'


def page_html(plan, i, s, hole, uri):
    n = f"{i + 1}/{len(plan['slides'])}"
    tag = f'{H.escape(plan.get("etiqueta", "NOTICIAS DE IA"))} · {H.escape(plan["fecha_label"])}'
    head = f'<div class="top"><div class="tag"><i></i>{tag}</div><div class="num">{n}</div></div>'
    kind = s.get("kind", "news")
    if kind == "cover":
        media = "" if hole else f'<img src="{uri(s["media"])}" style="object-fit:cover">'
        return f"""<div class="page cover{'' if hole else ' solid'}"><canvas id="plexus"></canvas>
          <div class="hero media {'hole' if hole else ''}">{media}</div>
          <div class="fade"></div><div class="bottom"></div>
          <div class="tag tagc"><i></i>{tag}</div><div class="line"></div><h2>{s['title']}</h2></div>"""
    if kind == "cta":
        g = "".join(f'<img src="{uri(x)}">' for x in s.get("imagenes", [])[:6])
        return f"""<div class="page solid cta"><canvas id="plexus"></canvas>
          {head.replace('class="top"', 'class="top" style="position:absolute;top:var(--tagtop);left:52px;right:52px"')}
          <h2>{s['title']}</h2><div class="grid">{g}</div>
          <p>{s.get('body', '')}</p><p class="follow">{s.get('follow', '')}</p></div>"""
    if s.get("stat"):
        inner = stat_html(s["stat"])
    elif hole:
        inner = ""
    else:
        inner = f'<img src="{uri(s["media"])}" style="object-fit:{s.get("fit", "cover")};background:{s.get("bg", "#111110")}">'
    return f"""<div class="page{'' if hole else ' solid'}"><canvas id="plexus"></canvas>{head}
      <div class="txt"><h1>{s['title']}</h1><p>{s['body']}</p></div>
      <div class="media {'hole' if hole else ''}">{inner}<div class="pill">{s['pill']}</div></div>
      <div class="src">{H.escape(s.get('src', ''))}</div></div>"""


def ffmpeg_still(src, t, crop, out):
    vf = (f"crop={crop}," if crop else "") + "scale=iw:ih"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(src), "-frames:v", "1", "-vf", vf, str(out)], check=True)


def ffmpeg_compose(s, src, ov, rect, W, Hh, out):
    x, y, w, h = rect
    pre = f"crop={s['crop']}," if s.get("crop") else ""
    if s.get("vfit") == "contain":
        vf = f"{pre}scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={s.get('bg', '#111110')}"
    else:
        vf = f"{pre}scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    t = s.get("t", 8)
    has_audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout.strip() != ""
    fc = (f"color=0x0a0a0a:s={W}x{Hh}:r=30:d={t}[bg];[0:v]fps=30,{vf},setsar=1[v];"
          f"[bg][v]overlay={x}:{y}:shortest=1[b];[b][1:v]overlay=0:0,format=yuv420p[out]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(s.get("ss", 0)), "-t", str(t), "-i", str(src), "-loop", "1", "-t", str(t), "-i", str(ov),
           "-filter_complex", fc, "-map", "[out]"]
    if has_audio:
        cmd += ["-map", "0:a:0", "-c:a", "aac", "-b:a", "128k", "-af", f"afade=t=in:d=0.3,afade=t=out:st={t - 0.5}:d=0.5"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-profile:v", "high", "-movflags", "+faststart", "-t", str(t), str(out)]
    subprocess.run(cmd, check=True)
    return has_audio


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--mode", choices=MODES, default="ig")
    ap.add_argument("--only", type=int, nargs="*")
    a = ap.parse_args()
    plan_path = pathlib.Path(a.plan).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    medios = base / "medios"
    out = base / ("carrusel" if a.mode == "ig" else "carrusel_tiktok")
    tmp = base / ".render_tmp"
    out.mkdir(exist_ok=True); tmp.mkdir(exist_ok=True)
    m = MODES[a.mode]
    W, Hh = 1080, m["h"]
    vars_css = (f":root{{--h:{Hh}px;--hero:{m['hero']}px;--h2bottom:{m['h2bottom']}px;--h2size:{m['h2size']}px;--tagtop:{m['tagtop']}px}}"
                f".page{{padding:{m['pad']}}}.page.cover{{padding:0}}.page.cta{{padding-top:{m['cta_pad']}px}}")

    def uri(name):
        p = pathlib.Path(name)
        return (p if p.is_absolute() else medios / name).as_uri()

    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": Hh})
        for i, s in enumerate(plan["slides"]):
            if a.only and i + 1 not in a.only:
                continue
            name = f"{i + 1:02d}"
            vid = is_video(s.get("media", ""))
            if a.mode == "tiktok" and s.get("tt_media"):
                # imagen propia para TikTok (p. ej. paneles apilados en vertical)
                s = dict(s, media=s["tt_media"], fit=s.get("tt_fit", "contain"), pill=s.get("tt_pill", s.get("pill", "")))
                vid = False
            if vid and a.mode == "tiktok":
                fr = tmp / f"still{name}.png"
                ffmpeg_still(medios / s["media"], s.get("ss", 0) + s.get("still", 3), s.get("crop"), fr)
                s = dict(s, media=str(fr), fit=s.get("vfit", "cover"))
                vid = False
            doc = (f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}{vars_css}</style></head><body>"
                   f"{page_html(plan, i, s, vid, uri)}</body></html>")
            f = tmp / f"s{name}.html"
            f.write_text(doc, encoding="utf-8")
            await pg.goto(f.as_uri())
            await pg.evaluate("document.fonts.ready")
            await pg.wait_for_timeout(500)
            await pg.evaluate(PLEXUS_JS.replace('%SEED%', str(97 + i * 131)))  # tras cargar fuentes: el layout ya es el final
            if not vid:
                await pg.screenshot(path=str(out / f"{name}.png"))
                print("png", name)
                continue
            r = await pg.evaluate("(()=>{const r=document.querySelector('.media').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
            rect = [round(v) for v in r]
            ov = tmp / f"ov{name}.png"
            await pg.screenshot(path=str(ov), omit_background=True)
            audio = ffmpeg_compose(s, medios / s["media"], ov, rect, W, Hh, out / f"{name}.mp4")
            print("mp4", name, "con audio" if audio else "sin audio")
        await b.close()


asyncio.run(main())
