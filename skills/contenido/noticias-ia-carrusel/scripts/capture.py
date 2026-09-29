"""Capturas con Playwright cuando una noticia no trae imagen o video descargable.

Uso:
  uv run --with playwright python capture.py shot <url> <salida.png> [--clip x,y,w,h] [--full]
  uv run --with playwright python capture.py rec  <url> <salida.webm> [--segundos 20] [--scroll]

- shot: captura a 2x (viewport 1280x900). Quita banners de cookies comunes antes de capturar.
- rec: graba la pestaña en video (1280x800). Con --scroll baja la página poco a poco (galerías, demos).
  Pulsa Escape al inicio para cerrar modales de bienvenida. Recorta el arranque después con ffmpeg (-ss).
Si la página muestra un challenge de Cloudflare, reintenta una vez; si sigue, usa otra fuente.
"""
import argparse, asyncio, pathlib, shutil
from playwright.async_api import async_playwright

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36"
KILL = "document.querySelectorAll('[class*=ookie],[id*=ookie],[id*=onetrust],[aria-label*=ookie],[class*=consent]').forEach(e=>e.remove())"


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["shot", "rec"])
    ap.add_argument("url"); ap.add_argument("salida")
    ap.add_argument("--clip"); ap.add_argument("--full", action="store_true")
    ap.add_argument("--segundos", type=int, default=20); ap.add_argument("--scroll", action="store_true")
    a = ap.parse_args()
    out = pathlib.Path(a.salida).resolve()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        if a.modo == "shot":
            ctx = await b.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2, user_agent=UA)
            pg = await ctx.new_page()
            await pg.goto(a.url, wait_until="domcontentloaded", timeout=45000)
            await pg.wait_for_timeout(5000)
            await pg.evaluate(KILL)
            kw = {"path": str(out), "full_page": a.full}
            if a.clip:
                x, y, w, h = map(float, a.clip.split(","))
                kw["clip"] = {"x": x, "y": y, "width": w, "height": h}
            await pg.screenshot(**kw)
            print("ok", await pg.title())
        else:
            tmp = out.parent / ".rec_tmp"
            ctx = await b.new_context(viewport={"width": 1280, "height": 800}, user_agent=UA,
                                      record_video_dir=str(tmp), record_video_size={"width": 1280, "height": 800})
            pg = await ctx.new_page()
            await pg.goto(a.url, wait_until="domcontentloaded", timeout=45000)
            await pg.wait_for_timeout(4000)
            await pg.keyboard.press("Escape")
            await pg.evaluate(KILL)
            steps = max(1, a.segundos)
            for _ in range(steps):
                if a.scroll:
                    await pg.mouse.wheel(0, 220)
                await pg.wait_for_timeout(1000)
            print("ok", await pg.title())
            v = pg.video
            await ctx.close()
            shutil.move(await v.path(), out)
            shutil.rmtree(tmp, ignore_errors=True)
        await b.close()


asyncio.run(main())
