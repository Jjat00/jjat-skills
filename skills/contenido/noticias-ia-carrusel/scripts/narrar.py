"""Narración del reel con edge-tts (voces neuronales de Microsoft, gratis).

Uso:
  python narrar.py <carpeta>/plan.json --voz es-CO-GonzaloNeural [--velocidad +8%]

Lee el campo "narracion" de cada lámina del plan y escribe <carpeta>/reel/voz/NN.mp3.
Luego `render.py --mode reel` alarga cada lámina a lo que dura su voz y la mezcla sobre el clip.

Voces recomendadas (español):
  es-CO-GonzaloNeural (hombre, Colombia)   es-CO-SalomeNeural (mujer, Colombia)
  es-MX-JorgeNeural   (hombre, México)     es-MX-DaliaNeural  (mujer, México)
Para ElevenLabs (de pago) no se usa este script: se llama a text_to_speech de HF Studio por lámina
(primero sin quote_id para mostrar el costo) y se guarda cada MP3 como reel/voz/NN.mp3.
"""
import argparse, json, pathlib, subprocess


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--voz", default="es-CO-GonzaloNeural")
    ap.add_argument("--velocidad", default="+8%")
    a = ap.parse_args()
    plan_path = pathlib.Path(a.plan).resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    out = plan_path.parent / "reel" / "voz"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.mp3"):
        old.unlink()
    for i, s in enumerate(plan["slides"]):
        txt = (s.get("narracion") or "").strip()
        if not txt:
            continue
        dst = out / f"{i + 1:02d}.mp3"
        subprocess.run(["uvx", "edge-tts", "--voice", a.voz, f"--rate={a.velocidad}", "--text", txt, "--write-media", str(dst)],
                       check=True, capture_output=True)
        d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)],
                           capture_output=True, text=True).stdout.strip()
        print(f"{i + 1:02d} {float(d):.1f} s  {txt[:60]}")


main()
