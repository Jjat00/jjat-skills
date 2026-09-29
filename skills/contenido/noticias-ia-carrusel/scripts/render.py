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
    # Reel: mismas zonas seguras que TikTok, sin párrafo (no da tiempo a leerlo) y titular más grande.
    "reel": dict(h=1920, pad="150px 130px 290px 52px", hero=1180, h2bottom=380, h2size=92, tagtop=150, cta_pad=170),
}
REEL_CSS = ".txt p{display:none}.txt h1{font-size:62px;margin-bottom:34px}.pill{font-size:34px}"
REEL_T = {"cover": 3.0, "cta": 3.0, "news": 3.5}   # segundos por lámina en el reel
WHOOSH = pathlib.Path("/mnt/d/sonidos/transiciones/whoosh-corto.mp3")  # biblioteca de sonidos de Jaime

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


def image_segment(png, t, out):
    """Lámina fija -> video con zoom lento (1.00 -> 1.04) y audio en silencio."""
    n = int(round(t * 30))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", str(t), "-i", str(png),
                    "-f", "lavfi", "-t", str(t), "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", f"[0:v]scale=2160:3840,zoompan=z='1+0.04*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p[v]",
                    "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
                    "-t", str(t), str(out)], check=True)


def normalize_segment(src, out, clip_vol=0.35):
    """Video de lámina -> 30 fps, audio estéreo 48 kHz (en silencio si no trae) y volumen del clip bajo."""
    has_audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(src)],
                               capture_output=True, text=True).stdout.strip() != ""
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
    if has_audio:
        cmd += ["-filter_complex", f"[0:a]volume={clip_vol},aresample=48000,aformat=channel_layouts=stereo[a]", "-map", "0:v", "-map", "[a]"]
    else:
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip()
        cmd += ["-f", "lavfi", "-t", d, "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a"]
    cmd += ["-r", "30", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out)]
    subprocess.run(cmd, check=True)


def dur_of(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout.strip())


def add_voice(seg, voice):
    """Mezcla la narración sobre el segmento (el sonido del clip baja para que no compita con la voz)."""
    tmp = seg.with_name(seg.stem + "_v.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(seg), "-i", str(voice), "-filter_complex",
                    "[0:a]volume=0.45[c];[1:a]adelay=150|150,aresample=48000,aformat=channel_layouts=stereo,volume=1.15[v];"
                    "[c][v]amix=inputs=2:normalize=0:duration=first[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", str(tmp)], check=True)
    tmp.replace(seg)


def build_reel(seg_dir, out_mp4, musica=None):
    """Une los segmentos, pone un whoosh en cada corte y, si hay, una pista de música de fondo."""
    segs = sorted(seg_dir.glob("[0-9][0-9].mp4"))
    lst = seg_dir / "lista.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf-8")
    joined = seg_dir / "unido.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)], check=True)
    durs = [float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                 capture_output=True, text=True).stdout) for p in segs]
    total = sum(durs)
    cuts, acc = [], 0.0
    for d in durs[:-1]:
        acc += d; cuts.append(acc)
    inputs = ["-i", str(joined)]
    fc, mix = [], ["[0:a]"]
    k = 1
    if WHOOSH.exists():
        for c in cuts:
            inputs += ["-i", str(WHOOSH)]
            ms = max(0, int((c - 0.18) * 1000))
            fc.append(f"[{k}:a]volume=0.55,adelay={ms}|{ms}[w{k}]"); mix.append(f"[w{k}]"); k += 1
    if musica and pathlib.Path(musica).exists():
        inputs += ["-i", str(musica)]
        fc.append(f"[{k}:a]volume=0.25,atrim=0:{total},afade=t=out:st={total - 1.5}:d=1.5[m]"); mix.append("[m]"); k += 1
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", str(total), str(out_mp4)], check=True)
    return total


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
    # -stream_loop: si la lámina dura más que lo que queda de clip (p. ej. por la narración), el clip se repite
    cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-ss", str(s.get("ss", 0)), "-t", str(t), "-i", str(src), "-loop", "1", "-t", str(t), "-i", str(ov),
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
    ap.add_argument("--musica", help="solo reel: pista de música de fondo (opcional)")
    ap.add_argument("--sin-voz", action="store_true", help="solo reel: ignora reel/voz/ aunque exista (versión sin narración)")
    a = ap.parse_args()
    plan_path = pathlib.Path(a.plan).resolve()
    base = plan_path.parent
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    medios = base / "medios"
    out = base / {"ig": "carrusel", "tiktok": "carrusel_tiktok", "reel": "reel/segmentos"}[a.mode]
    tmp = base / ".render_tmp"
    out.mkdir(parents=True, exist_ok=True); tmp.mkdir(exist_ok=True)
    m = MODES[a.mode]
    W, Hh = 1080, m["h"]
    vars_css = (f":root{{--h:{Hh}px;--hero:{m['hero']}px;--h2bottom:{m['h2bottom']}px;--h2size:{m['h2size']}px;--tagtop:{m['tagtop']}px}}"
                f".page{{padding:{m['pad']}}}.page.cover{{padding:0}}.page.cta{{padding-top:{m['cta_pad']}px}}"
                + (REEL_CSS if a.mode == "reel" else ""))

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
            voice = base / "reel" / "voz" / f"{name}.mp3"
            if a.sin_voz:
                voice = pathlib.Path("/nonexistent")
            if a.mode == "reel":
                t = s.get("reel_t", REEL_T[s.get("kind", "news")])
                if voice.exists():
                    t = max(t, round(dur_of(voice) + 0.5, 2))   # la lámina dura lo que dura su voz
                s = dict(s, t=t, ss=s.get("reel_ss", s.get("ss", 0)))
            if a.mode in ("tiktok", "reel") and s.get("tt_media"):
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
                if a.mode == "reel":
                    image_segment(out / f"{name}.png", s["t"], out / f"{name}.mp4")
                    (out / f"{name}.png").unlink()
                    if voice.exists():
                        add_voice(out / f"{name}.mp4", voice)
                    print("reel", name, "imagen con zoom")
                else:
                    print("png", name)
                continue
            r = await pg.evaluate("(()=>{const r=document.querySelector('.media').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()")
            rect = [round(v) for v in r]
            ov = tmp / f"ov{name}.png"
            await pg.screenshot(path=str(ov), omit_background=True)
            dst = out / f"{name}.mp4"
            raw = tmp / f"raw{name}.mp4" if a.mode == "reel" else dst
            audio = ffmpeg_compose(s, medios / s["media"], ov, rect, W, Hh, raw)
            if a.mode == "reel":
                normalize_segment(raw, dst)
                if voice.exists():
                    add_voice(dst, voice)
            print("mp4", name, "con audio" if audio else "sin audio")
        await b.close()
    if a.mode == "reel" and not a.only:
        narrado = (not a.sin_voz) and (base / "reel" / "voz").exists() and any((base / "reel" / "voz").glob("*.mp3"))
        final = base / "reel" / f"reel_{plan['fecha']}{'_narrado' if narrado else ''}.mp4"
        total = build_reel(out, final, a.musica)
        print(f"reel {final} ({total:.1f} s)")


asyncio.run(main())
