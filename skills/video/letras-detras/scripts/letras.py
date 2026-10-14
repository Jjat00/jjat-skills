# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests",
#   "numpy",
#   "pillow",
#   "onnxruntime",
#   "faster-whisper",
#   "yt-dlp",
# ]
# ///
"""letras.py — letras gigantes de una canción detrás del sujeto de un video.

Subcomandos (todos escriben dentro de <proyecto>/):
  song     <proyecto> <spotify-url | "artista - canción" | nombre>  [--audio archivo]
           → song.json (título, artista, duración, letra sincronizada) + song.<ext>
  segment  <proyecto> --video <video> [--start S | --auto chorus|first]
           → segment.json (qué tramo de la canción suena bajo el video)
  align    <proyecto> [--model small]
           → words.json (cada palabra con su tiempo, relativo al video)
  plan     <proyecto> [--words-per-block 4] [--layout auto|horizontal|vertical]
           → plan.json (bloques, filas, colores; editable a mano; W>H usa el estilo horizontal)
  matte    <proyecto>
           → matte/f_%05d.png (alfa del sujeto, Robust Video Matting)
  preview  <proyecto> [t …]
           → preview/sheet.png (fotogramas compuestos, sin render completo)
  render   <proyecto> [--out final.mp4]
           → final.mp4 (video + letras detrás del sujeto + la canción)
  all      <proyecto> <canción> --video <video> [opciones de segment]
           → song + segment + align + plan + matte (luego preview/render)
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_DIR = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache" / "letras-detras"
UA = {"User-Agent": "Mozilla/5.0 (letras-detras skill)"}

RVM_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/bodonimoda/BodoniModa%5Bopsz%2Cwght%5D.ttf"

DEFAULT_STYLE = {
    "font": None,               # ruta a .ttf; None = Bodoni Moda (se descarga)
    "font_weight": 680,         # eje wght de Bodoni Moda (400–900)
    "condense": 0.56,           # compresión horizontal: el look alto y estrecho de la referencia
    "uppercase": True,
    "anchor": "head",           # "head" = el bloque se centra a la altura de la cabeza del sujeto; "top" = usa block_top
    "head_offset": 0.06,        # con anchor=head: centro del bloque = tope de la cabeza + esto (fracción del alto)
    "block_top": 0.07,          # borde superior del bloque, fracción del alto (anchor=top o sin matte)
    "auto_ink": True,           # fondo claro detrás del bloque → las filas "white" pasan a "ink"
    "block_max_h": 0.50,        # alto máximo del bloque
    "block_w": 0.80,            # ancho objetivo de cada fila (las filas se justifican a este ancho)
    "row_max_h": 0.24,          # alto máximo de mayúscula por fila (palabras cortas no se disparan)
    "row_gap": 0.06,            # separación entre filas, fracción del alto de fila
    "center_x": None,           # None = centrado en el sujeto (centroide del matte); o fracción 0–1
    "letter_reveal": 0.22,      # segundos que tarda una palabra en escribirse letra a letra
    "fade_in": 0.06,            # fundido de cada letra
    "fade_out": 0.18,           # fundido del bloque si hay silencio después
    "dim_bg": 0.0,              # oscurece el fondo (0–1) para que la letra respire
    "shadow": 0.35,             # sombra suave bajo la letra (0 = sin sombra)
    "colors": {
        "white": {"top": "#FFFFFF", "bottom": "#D9D4C8"},
        "red":   {"top": "#E0141B", "bottom": "#9E0A0F"},
        "gold":  {"top": "#F6E7B8", "bottom": "#A8833F"},
        "gray":  {"top": "#B5B5B5", "bottom": "#6E6E6E", "alpha": 0.75},
        "ink":   {"top": "#141210", "bottom": "#2E2A26"},
    },
}

# Video horizontal (W>H): la cabeza ocupa casi todo el alto y con anchor=head los bloques de 3–4
# filas quedaban tapados. Probado con webcam 1280x720 y cara centrada (paranoid, 2026-10): letra
# arriba, más ancha y más alta, con máximo 2 filas por bloque.
LANDSCAPE_STYLE = {
    "anchor": "top",
    "block_top": 0.02,
    "row_max_h": 0.34,
    "block_max_h": 0.60,
    "block_w": 0.94,
    "condense": 0.66,
}
LANDSCAPE_PLAN = {"max_rows": 2, "merge_short": 0.7}

# ─────────────────────────────── utilidades ───────────────────────────────

def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)],
        check=True, capture_output=True, text=True).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    info = {"duration": float(d["format"]["duration"])}
    if v:
        n, den = v.get("avg_frame_rate", "0/1").split("/")
        fps = float(n) / float(den or 1) if float(den or 1) else 0
        if not fps:
            n, den = v["r_frame_rate"].split("/")
            fps = float(n) / float(den)
        info.update(width=int(v["width"]), height=int(v["height"]), fps=fps)
    return info


def load(p, name):
    f = Path(p) / name
    if not f.exists():
        sys.exit(f"Falta {f}. Corre antes el paso que lo genera.")
    return json.loads(f.read_text())


def save(p, name, data):
    (Path(p) / name).write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"  → {Path(p) / name}")


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9ñ]", "", w)


def download(url, dest):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  descargando {dest.name} …")
    with requests.get(url, stream=True, timeout=60, headers=UA) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)
        tmp.rename(dest)
    return dest

# ─────────────────────────────── 1. canción ───────────────────────────────

def spotify_meta(url):
    m = re.search(r"track/([A-Za-z0-9]+)", url)
    if not m:
        sys.exit("El link de Spotify debe ser de una canción (open.spotify.com/track/…).")
    html = requests.get(f"https://open.spotify.com/track/{m.group(1)}", headers=UA, timeout=15).text
    title = re.search(r"<title>(.*?) - song(?: and lyrics)? by (.*?) \| Spotify</title>", html)
    dur = re.search(r'music:duration" content="(\d+)"', html)
    if not title:
        sys.exit("No pude leer el título desde Spotify; pasa «artista - canción».")
    import html as htmllib
    return {
        "track": htmllib.unescape(title.group(1)),
        "artist": htmllib.unescape(title.group(2)).split(", ")[0],
        "duration": float(dur.group(1)) if dur else None,
        "spotify": url,
    }


def lrclib_find(track, artist, duration, hint=""):
    """Mejor letra en LRCLib. hint = título/canal de YouTube para desempatar artista (covers)."""
    hits = []
    if artist:
        r = requests.get("https://lrclib.net/api/get", headers=UA, timeout=15,
                         params={"track_name": track, "artist_name": artist,
                                 **({"duration": int(round(duration))} if duration else {})})
        if r.ok:
            hits.append(r.json())
    for q in {f"{artist} {track}".strip(), track}:
        r = requests.get("https://lrclib.net/api/search", headers=UA, timeout=15, params={"q": q})
        if r.ok:
            hits += r.json()
    hits = [h for h in hits if h.get("syncedLyrics") or h.get("plainLyrics")]
    if not hits:
        return None
    hint_n = norm(hint)

    def score(h):
        s = 0 if h.get("syncedLyrics") else 100
        if duration and h.get("duration"):
            s += abs(h["duration"] - duration)
        a_n = norm(h.get("artistName", ""))
        if artist:
            s += 0 if norm(artist) in a_n or a_n in norm(artist) else 50
        elif hint_n:
            s += 0 if a_n and a_n in hint_n else 50
        if norm(track) != norm(h.get("trackName", "")):
            s += 10
        return s
    return min(hits, key=score)


BAD_VERSIONS = ("cover", "live", "sped up", "slowed", "remix", "karaoke", "instrumental", "8d", "nightcore", "reverb")


def youtube_pick(track, artist, duration):
    import yt_dlp
    q = f"{artist} {track}" if artist else track
    with yt_dlp.YoutubeDL({"quiet": True, "extract_flat": True}) as y:
        entries = (y.extract_info(f"ytsearch8:{q} audio", download=False) or {}).get("entries") or []
    entries = [e for e in entries if e.get("duration")]
    ql = q.lower()
    clean = [e for e in entries if not any(b in (e.get("title") or "").lower() and b not in ql for b in BAD_VERSIONS)]
    entries = clean or entries
    if not entries:
        sys.exit("No encontré la canción en YouTube; pasa el audio con --audio.")
    if duration:
        entries.sort(key=lambda e: abs(e["duration"] - duration))
    return entries[0]  # sin duración: el primero por relevancia (suele ser el original)


def youtube_audio(pick, dest_stem):
    import yt_dlp
    print(f"  YouTube: {pick.get('title')} — {pick.get('channel') or pick.get('uploader')} ({pick['duration']} s)")
    opts = {"quiet": True, "noprogress": True, "format": "bestaudio/best", "outtmpl": str(dest_stem) + ".%(ext)s",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "256"}]}
    with yt_dlp.YoutubeDL(opts) as y:
        y.download([pick["url"] if str(pick.get("url", "")).startswith("http") else f"https://www.youtube.com/watch?v={pick['id']}"])
    return Path(str(dest_stem) + ".mp3")


def parse_lrc(text):
    lines = []
    for raw in (text or "").splitlines():
        stamps = re.findall(r"\[(\d+):(\d+(?:\.\d+)?)\]", raw)
        words = re.sub(r"\[[^\]]*\]", "", raw).strip()
        for mm, ss in stamps:
            lines.append({"t": int(mm) * 60 + float(ss), "text": words})
    lines.sort(key=lambda x: x["t"])
    for i, ln in enumerate(lines):
        ln["end"] = lines[i + 1]["t"] if i + 1 < len(lines) else ln["t"] + 5
    return [ln for ln in lines if ln["text"]]


def cmd_song(a):
    p = Path(a.project); p.mkdir(parents=True, exist_ok=True)
    src = a.song.strip()
    if "spotify.com" in src:
        meta = spotify_meta(src)
    elif " - " in src:
        artist, track = src.split(" - ", 1)
        meta = {"track": track.strip(), "artist": artist.strip(), "duration": None}
    else:
        meta = {"track": src, "artist": "", "duration": None}

    audio = Path(a.audio).resolve() if a.audio else None
    if audio and not meta["duration"]:
        meta["duration"] = ffprobe(audio)["duration"]

    pick = None
    if not audio:
        pick = youtube_pick(meta["track"], meta["artist"], meta["duration"])
        if not meta["duration"]:
            meta["duration"] = float(pick["duration"])
    hint = f"{pick.get('title', '')} {pick.get('channel') or pick.get('uploader') or ''}" if pick else ""
    hit = None if a.lyrics else lrclib_find(meta["track"], meta["artist"], meta["duration"], hint)
    if a.lyrics:
        txt = Path(a.lyrics).read_text(encoding="utf-8")
        meta["lines"] = parse_lrc(txt)  # acepta LRC; si es texto plano queda vacío
        meta["plain"] = re.sub(r"\[[^\]]*\]", "", txt).strip()
        meta["synced"] = bool(meta["lines"])
        print(f"  letra manual ({'LRC sincronizada' if meta['synced'] else 'texto plano'})")
    elif hit:
        meta["track"] = hit.get("trackName") or meta["track"]
        meta["artist"] = hit.get("artistName") or meta["artist"]
        meta["lrclib_duration"] = hit.get("duration")
        meta["lines"] = parse_lrc(hit.get("syncedLyrics"))
        meta["plain"] = hit.get("plainLyrics") or "\n".join(l["text"] for l in meta["lines"])
        meta["synced"] = bool(meta["lines"])
        print(f"  LRCLib: {meta['artist']} - {meta['track']} "
              f"({'sincronizada' if meta['synced'] else 'solo texto'}, {len(meta['lines'])} líneas)")
    else:
        meta.update(lines=[], plain="", synced=False)
        print("  ⚠ LRCLib no tiene la letra: se transcribirá con Whisper (revisa words.json).")

    target = meta.get("lrclib_duration") or meta["duration"]
    if audio:
        dst = p / f"song{audio.suffix}"
        shutil.copyfile(audio, dst)
    else:
        dst = youtube_audio(pick, p / "song")
        meta["youtube"] = {"title": pick.get("title"), "id": pick.get("id"), "duration": pick.get("duration")}
    meta["audio"] = dst.name
    meta["audio_duration"] = ffprobe(dst)["duration"]
    if target and abs(meta["audio_duration"] - target) > 3:
        print(f"  ⚠ El audio dura {meta['audio_duration']:.1f} s y la letra sincronizada {target:.1f} s: "
              "puede ser otra versión. align corrige con Whisper, pero revisa.")
    save(p, "song.json", meta)

# ─────────────────────────────── 2. tramo ───────────────────────────────

def chorus_start(lines):
    """Primera aparición de la línea más repetida (casi siempre el coro)."""
    counts = {}
    for ln in lines:
        k = norm(ln["text"])
        if len(k) > 6:
            counts[k] = counts.get(k, 0) + 1
    if not counts or max(counts.values()) < 2:
        return None
    best = max(counts, key=lambda k: (counts[k], -next(l["t"] for l in lines if norm(l["text"]) == k)))
    first = next(l for l in lines if norm(l["text"]) == best)
    return first["t"]


def cmd_segment(a):
    p = Path(a.project)
    song = load(p, "song.json")
    video = Path(a.video).resolve()
    vinfo = ffprobe(video)
    dst = p / f"video{video.suffix}"
    if not dst.exists() or dst.stat().st_size != video.stat().st_size:
        shutil.copyfile(video, dst)
    lead = a.lead
    if a.start is not None:
        start, why = a.start, "manual"
    else:
        start, why = None, ""
        if a.auto == "chorus" and song["lines"]:
            c = chorus_start(song["lines"])
            if c is not None:
                start, why = max(0.0, c - lead), "coro (línea más repetida)"
        if start is None and song["lines"]:
            start, why = max(0.0, song["lines"][0]["t"] - lead), "primera línea cantada"
        if start is None:
            start, why = 0.0, "inicio de la canción"
    seg = {"video": dst.name, "width": vinfo["width"], "height": vinfo["height"], "fps": vinfo["fps"],
           "duration": vinfo["duration"], "song_start": round(start, 3), "why": why}
    print(f"  tramo: canción {start:.2f}s → {start + vinfo['duration']:.2f}s ({why})")
    for ln in song["lines"]:
        if start - 1 <= ln["t"] <= start + vinfo["duration"]:
            print(f"    {ln['t'] - start:6.2f}  {ln['text']}")
    save(p, "segment.json", seg)

# ─────────────────────────────── 3. alineado ───────────────────────────────

def cmd_align(a):
    p = Path(a.project)
    song, seg = load(p, "song.json"), load(p, "segment.json")
    s0, dur = seg["song_start"], seg["duration"]
    clip = p / "_seg.wav"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(s0), "-t", str(dur), "-i", str(p / song["audio"]),
         "-ac", "1", "-ar", "16000", str(clip)])

    lines = [dict(l, t=l["t"] - s0, end=l["end"] - s0) for l in song["lines"]
             if l["end"] - s0 > 0 and l["t"] - s0 < dur]
    prompt = " ".join(l["text"] for l in lines)[:800] or None

    from faster_whisper import WhisperModel
    print(f"  whisper {a.model} (CPU) …")
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, info = model.transcribe(str(clip), word_timestamps=True, initial_prompt=prompt,
                                  vad_filter=False, condition_on_previous_text=False,
                                  language=a.language)
    heard = [{"w": w.word.strip(), "t": w.start, "e": w.end} for s in segs for w in (s.words or []) if w.word.strip()]
    print(f"  whisper oyó {len(heard)} palabras ({info.language})")

    words = []
    if not lines and song.get("plain"):  # letra sin tiempos: se busca el tramo que suena
        allw = [{"text": w, "line": li} for li, ln in enumerate(song["plain"].splitlines()) for w in ln.split()]
        sm = difflib.SequenceMatcher(a=[norm(w["text"]) for w in allw], b=[norm(h["w"]) for h in heard], autojunk=False)
        hits = [(blk.a + k, heard[blk.b + k]) for blk in sm.get_matching_blocks() for k in range(blk.size)]
        if len(hits) >= 3:
            i0, i1 = hits[0][0], hits[-1][0]
            span = allw[i0:i1 + 1]
            for ai, h in hits:
                span[ai - i0].update(t=h["t"], e=h["e"], src="whisper")
            known = [k for k, w in enumerate(span) if "t" in w]
            for a_, b_ in zip(known, known[1:]):
                for k in range(a_ + 1, b_):
                    f = (k - a_) / (b_ - a_)
                    span[k].update(t=span[a_]["t"] + (span[b_]["t"] - span[a_]["t"]) * f, src="interp")
            for k, w in enumerate(span):
                nxt = span[k + 1]["t"] if k + 1 < len(span) else w.get("e", w["t"] + 0.4)
                w["e"] = round(max(w["t"] + 0.08, min(w.get("e", nxt), nxt) if k + 1 < len(span) else w.get("e", nxt)), 3)
                w["t"] = round(w["t"], 3)
            words = span
        else:
            print("  ⚠ la letra no casa con lo que suena: uso la transcripción de Whisper")
    if words:
        pass
    elif not lines:  # sin letra: lo que oyó Whisper es la letra
        for h in heard:
            words.append({"text": h["w"], "t": round(h["t"], 3), "e": round(h["e"], 3), "line": None, "src": "whisper"})
    else:
        for li, ln in enumerate(lines):
            for w in ln["text"].split():
                words.append({"text": w, "line": li, "lt": ln["t"], "le": ln["end"]})
        A = [norm(w["text"]) for w in words]
        B = [norm(h["w"]) for h in heard]
        sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                w, h = words[blk.a + k], heard[blk.b + k]
                # solo vale si cae cerca de su línea (evita casar con una repetición del coro)
                if w["lt"] - 1.5 <= h["t"] <= w["le"] + 0.5:
                    w["t"], w["e"], w["src"] = h["t"], h["e"], "whisper"
        # rellena por línea: la marca LRC ancla el inicio; los huecos se reparten por longitud
        for li, ln in enumerate(lines):
            lw = [w for w in words if w["line"] == li]
            if not lw:
                continue
            end = min(ln["end"], ln["t"] + max(1.2, 0.45 * len(lw)))
            if "t" not in lw[0]:
                lw[0]["t"], lw[0]["src"] = ln["t"], "lrc"
            i = 1
            while i < len(lw):
                if "t" in lw[i]:
                    i += 1
                    continue
                j = i
                while j < len(lw) and "t" not in lw[j]:
                    j += 1
                t0 = lw[i - 1]["t"]
                t1 = lw[j]["t"] if j < len(lw) else end
                wts = [len(norm(w["text"])) + 2 for w in lw[i - 1:j]]
                tot, acc = sum(wts), 0
                for k in range(i, j):
                    acc += wts[k - i]
                    lw[k]["t"], lw[k]["src"] = t0 + (t1 - t0) * acc / tot, "interp"
                i = j
            for k, w in enumerate(lw):  # monotonía y fin de cada palabra
                if k and w["t"] < lw[k - 1]["t"] + 0.05:
                    w["t"] = lw[k - 1]["t"] + 0.05
            for k, w in enumerate(lw):
                nxt = lw[k + 1]["t"] if k + 1 < len(lw) else max(end, w["t"] + 0.3)
                e = w.get("e", nxt)
                w["e"] = max(w["t"] + 0.08, min(e, nxt) if k + 1 < len(lw) else e)
        for w in words:
            w["t"], w["e"] = round(w["t"], 3), round(w["e"], 3)
            w.pop("lt"); w.pop("le")
    words = [w for w in words if w["e"] > 0 and w["t"] < dur]
    ok = sum(1 for w in words if w.get("src") == "whisper")
    print(f"  {len(words)} palabras en el tramo; {ok} con tiempo de Whisper, el resto de LRC/interpolado")
    save(p, "words.json", {"words": words, "lines": [{"t": round(l["t"], 3), "end": round(l["end"], 3), "text": l["text"]} for l in lines]})
    clip.unlink(missing_ok=True)

# ─────────────────────────────── 4. plan ───────────────────────────────

BREAKERS = {"but", "and", "when", "cause", "'cause", "cuz", "so", "if", "then", "or", "because", "till", "until",
            "pero", "y", "cuando", "porque", "si", "que", "aunque", "mientras", "hasta"}


def chunk_line(ws, maxw):
    """Parte una línea cantada en bloques de ≤maxw palabras, cortando antes de conjunciones."""
    out, cur = [], []
    for i, w in enumerate(ws):
        if cur and (len(cur) >= maxw or (norm(w["text"]) in BREAKERS and len(cur) >= 2)):
            out.append(cur); cur = []
        cur.append(w)
        if re.search(r"[,;:?!.]$", w["text"]) and len(cur) >= 2 and i < len(ws) - 1:
            out.append(cur); cur = []
    if cur:
        if out and len(cur) == 1 and len(out[-1]) < maxw + 1:
            out[-1] += cur
        else:
            out.append(cur)
    return out


def rows_of(block, maxchars=10):
    """Filas de un bloque: palabras cortas se juntan ("BUT I"), largas van solas."""
    rows, cur = [], []
    for w in block:
        txt = " ".join(x["text"] for x in cur + [w])
        if cur and len(txt) > maxchars:
            rows.append(cur); cur = []
        cur.append(w)
    if cur:
        rows.append(cur)
    return rows


def fit_rows(rows, max_rows):
    """Junta filas vecinas (la pareja más corta primero) hasta que queden ≤max_rows."""
    rows = [list(r) for r in rows]
    while max_rows and len(rows) > max_rows:
        size = [len(" ".join(w["text"] for w in rows[i] + rows[i + 1])) for i in range(len(rows) - 1)]
        i = size.index(min(size))
        rows[i:i + 2] = [rows[i] + rows[i + 1]]
    return rows


def cmd_plan(a):
    p = Path(a.project)
    W = load(p, "words.json")
    seg = load(p, "segment.json")
    words = W["words"]
    layout = a.layout
    if layout == "auto":
        layout = "horizontal" if seg.get("width", 0) > seg.get("height", 0) else "vertical"
    land = layout == "horizontal"
    max_rows = a.max_rows if a.max_rows is not None else (LANDSCAPE_PLAN["max_rows"] if land else 0)
    merge_short = a.merge_short if a.merge_short is not None else (LANDSCAPE_PLAN["merge_short"] if land else 0.0)

    groups = {}
    for w in words:
        groups.setdefault(w["line"], []).append(w)
    blocks, line_of = [], []  # cada bloque = lista de filas; cada fila = lista de palabras
    for key in sorted(groups, key=lambda k: groups[k][0]["t"]):
        for b in chunk_line(groups[key], a.words_per_block):
            rows = rows_of(b, a.row_chars)
            if not max_rows or len(rows) <= max_rows:
                blocks.append(rows); line_of.append(key)
                continue
            # más de max_rows filas: se parte en varios bloques; el más corto va primero
            # (3 filas → 1 + 2: «FINISHED» y luego «WITH MY / WOMAN»)
            first = len(rows) % max_rows or max_rows
            blocks.append(rows[:first]); line_of.append(key)
            for i in range(first, len(rows), max_rows):
                blocks.append(rows[i:i + max_rows]); line_of.append(key)

    def span(bi):
        first = blocks[bi][0][0]
        last = blocks[bi][-1][-1]
        nxt = blocks[bi + 1][0][0]["t"] if bi + 1 < len(blocks) else seg["duration"]
        return max(0.0, first["t"]), min(nxt, last["e"] + a.hold)

    # bloques que duran menos de merge_short s se funden con el vecino pegado en el tiempo,
    # de preferencia el de su misma línea cantada
    i = 0
    while merge_short and i < len(blocks):
        s0, e0 = span(i)
        if e0 - s0 >= merge_short or len(blocks) == 1:
            i += 1
            continue
        prev_ok = i > 0 and span(i - 1)[1] >= s0 - 0.05
        next_ok = i + 1 < len(blocks) and blocks[i + 1][0][0]["t"] <= e0 + 0.05
        if not (prev_ok or next_ok):
            i += 1
            continue
        same_prev = prev_ok and line_of[i - 1] == line_of[i]
        same_next = next_ok and line_of[i + 1] == line_of[i]
        j = i - 1 if prev_ok and (same_prev or not same_next) else i
        ws = [w for r in blocks[j] + blocks[j + 1] for w in r]
        blocks[j:j + 2] = [fit_rows(rows_of(ws, a.row_chars), max_rows)]
        line_of[j:j + 2] = [line_of[j]]
        i = max(0, j)

    out = []
    for bi, rows in enumerate(blocks):
        start, end = span(bi)
        out.append({
            "start": start, "end": round(end, 3),
            "rows": [{"color": "white", "words": [{"text": w["text"], "t": w["t"], "e": w["e"]} for w in r]} for r in rows],
        })
    # acentos por defecto (el agente debe revisarlos con criterio): la última fila de
    # bloques con varias filas, alternando rojo y dorado, uno de cada tres bloques
    k = 0
    for blk in out:
        if len(blk["rows"]) >= 2:
            k += 1
            if k % 3 == 1:
                blk["rows"][-1]["color"] = "red"
            elif k % 6 == 0:
                blk["rows"][0]["color"] = "gold"
    style = {**DEFAULT_STYLE, **(LANDSCAPE_STYLE if land else {})}
    plan = {"style": style, "blocks": out}
    print(f"  layout {layout} ({seg.get('width')}x{seg.get('height')}): "
          f"máx. {max_rows or '∞'} filas por bloque, funde bloques < {merge_short} s")
    old = p / "plan.json"
    if old.exists() and not a.force:
        sys.exit("plan.json ya existe (puede tener ediciones a mano). Usa --force para regenerarlo.")
    save(p, "plan.json", plan)
    for blk in out:
        print(f"  {blk['start']:6.2f}–{blk['end']:6.2f}  " + " / ".join(
            ("*" if r["color"] != "white" else "") + " ".join(w["text"] for w in r["words"]) for r in blk["rows"]))

# ─────────────────────────────── 5. matte ───────────────────────────────

def cmd_matte(a):
    import onnxruntime as ort
    p = Path(a.project)
    seg = load(p, "segment.json")
    model = download(RVM_URL, CACHE / "rvm_mobilenetv3_fp32.onnx")
    w, h = seg["width"], seg["height"]
    outdir = p / "matte"
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir()
    sess = ort.InferenceSession(str(model), providers=["CPUExecutionProvider"])
    ratio = np.array([min(1.0, a.ratio or 512 / max(w, h))], dtype=np.float32)
    rec = [np.zeros((1, 1, 1, 1), dtype=np.float32)] * 4
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(p / seg["video"]), "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    n, size = 0, w * h * 3
    centers = []
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        img = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32).transpose(2, 0, 1)[None] / 255
        fgr, pha, *rec = sess.run(None, {"src": img, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2],
                                         "r4i": rec[3], "downsample_ratio": ratio})
        alpha = (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)
        Image.fromarray(alpha, "L").save(outdir / f"f_{n:05d}.png", compress_level=1)
        cols = alpha.mean(0)
        centers.append(float((cols * np.arange(w)).sum() / cols.sum() / w) if cols.sum() > 0 else 0.5)
        n += 1
        if n % 48 == 0:
            print(f"  {n} fotogramas …")
    dec.wait()
    print(f"  matte listo: {n} fotogramas en {outdir}")
    save(p, "matte.json", {"frames": n, "center_x": round(float(np.median(centers)), 3)})

# ─────────────────────────────── 6. render ───────────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class Typesetter:
    def __init__(self, style, H):
        self.s, self.H = style, H
        path = style.get("font") or download(FONT_URL, CACHE / "BodoniModa.ttf")
        self.path = str(path)
        self.cache = {}

    def font(self, px):
        px = max(8, int(px))
        if px not in self.cache:
            f = ImageFont.truetype(self.path, px)
            try:
                axes = f.get_variation_axes()
                vals = []
                for ax in axes:
                    nm = ax.get("name", b"")
                    nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                    if "eight" in nm or nm.lower().startswith("wght"):
                        vals.append(self.s.get("font_weight", 560))
                    elif "ptical" in nm or nm.lower().startswith("opsz"):
                        vals.append(ax["maximum"])
                    else:
                        vals.append(ax.get("default", ax["minimum"]))
                f.set_variation_by_axes(vals)
            except Exception:
                pass
            self.cache[px] = f
        return self.cache[px]

    def text(self, t):
        return t.upper() if self.s.get("uppercase", True) else t

    def glyph_mask(self, text, px):
        """Máscara L de un texto ya condensado; devuelve (img, ancho, alto de mayúscula, offset arriba)."""
        f = self.font(px)
        asc, desc = f.getmetrics()
        bbox = f.getbbox(text)
        w = max(1, bbox[2] - bbox[0])
        img = Image.new("L", (w + 4, asc + desc + 4), 0)
        ImageDraw.Draw(img).text((2 - bbox[0], 2), text, font=f, fill=255)
        cw = max(1, int(img.width * self.s["condense"]))
        img = img.resize((cw, img.height), Image.LANCZOS)
        cap = f.getbbox("H")
        return img, cw, cap[3] - cap[1], cap[1] + 2

    def measure(self, text, px):
        f = self.font(px)
        b = f.getbbox(text)
        return (b[2] - b[0]) * self.s["condense"]


def layout_block(block, ts, W, H, cx, head_top=None):
    """Calcula tamaño y posición de cada fila (bloque justificado) y de cada letra."""
    s = ts.s
    target_w = s["block_w"] * W
    rows = []
    for r in block["rows"]:
        txt = ts.text(" ".join(w["text"] for w in r["words"]))
        w100 = ts.measure(txt, 100)
        cap100 = 100 * 0.70
        px = min(100 * target_w / max(w100, 1), 100 * s["row_max_h"] * H / cap100)
        rows.append({"px": px, "cap": px * 0.70})
    total = sum(r["cap"] for r in rows) * (1 + s["row_gap"])
    k = min(1.0, s["block_max_h"] * H / max(total, 1))
    if s.get("anchor") == "head" and head_top is not None:
        y = (head_top + s["head_offset"]) * H - total * k / 2
        y = max(0.04 * H, min(y, 0.96 * H - total * k))
    else:
        y = s["block_top"] * H
    placed = []
    for r, spec in zip(block["rows"], rows):
        px = spec["px"] * k
        pieces = []  # letras con su tiempo de aparición
        for wi, w in enumerate(r["words"]):
            word = ts.text(w["text"])
            dur = min(s["letter_reveal"], max(0.05, w["e"] - w["t"]))
            for ci, ch in enumerate(word):
                pieces.append({"ch": ch, "t": w["t"] + dur * ci / max(1, len(word))})
            if wi < len(r["words"]) - 1:
                pieces.append({"ch": " ", "t": w["t"]})
        full = "".join(pc["ch"] for pc in pieces)
        mask, mw, cap, top = ts.glyph_mask(full, px)
        # x de cada letra: ancho del prefijo condensado
        f = ts.font(px)
        b0 = f.getbbox(full)[0]
        xs = [int((f.getlength(full[:i]) - b0) * s["condense"]) + 2 for i in range(len(full) + 1)]
        x0 = int(cx * W - mw / 2)
        x0 = max(int(0.02 * W), min(x0, int(0.98 * W) - mw))
        placed.append({"color": r["color"], "mask": mask, "x": x0, "y": int(y - top), "cap": cap,
                       "pieces": pieces, "xs": xs})
        y += cap * (1 + s["row_gap"])
    return placed


def gradient_fill(mask, spec, y_cap_top, cap):
    w, h = mask.size
    top, bot = np.array(hex_rgb(spec["top"]), np.float32), np.array(hex_rgb(spec["bottom"]), np.float32)
    yy = (np.arange(h, dtype=np.float32) - y_cap_top) / max(cap, 1)
    t = np.clip(yy, 0, 1)[:, None, None]
    rgb = top * (1 - t) + bot * t
    return np.broadcast_to(rgb, (h, w, 3))


def render_text_layer(placed, t, block, style, W, H):
    """Capa RGBA (float) con las letras visibles en el instante t."""
    layer = np.zeros((H, W, 4), np.float32)
    fade_out = 1.0
    if block["end"] - t < style["fade_out"] and block.get("_fade"):
        fade_out = max(0.0, (block["end"] - t) / style["fade_out"])
    for row in placed:
        spec = style["colors"].get(row["color"], style["colors"]["white"])
        m = np.asarray(row["mask"], np.float32) / 255
        vis = np.zeros(m.shape[1], np.float32)
        for i, pc in enumerate(row["pieces"]):
            if t >= pc["t"]:
                a = min(1.0, (t - pc["t"]) / max(style["fade_in"], 1e-3))
                x1, x2 = row["xs"][i], row["xs"][i + 1] if i + 1 < len(row["xs"]) else m.shape[1]
                vis[max(0, x1 - 1):x2 + 1] = np.maximum(vis[max(0, x1 - 1):x2 + 1], a)
        if not vis.any():
            continue
        alpha = m * vis[None, :] * spec.get("alpha", 1.0) * fade_out
        rgb = gradient_fill(row["mask"], spec, 0, row["cap"] + row["mask"].height * 0.15)
        x, y = row["x"], row["y"]
        h, w = alpha.shape
        ys, xs_ = max(0, y), max(0, x)
        ye, xe = min(H, y + h), min(W, x + w)
        if ye <= ys or xe <= xs_:
            continue
        sa = alpha[ys - y:ye - y, xs_ - x:xe - x]
        dst = layer[ys:ye, xs_:xe]
        dst[..., :3] = rgb[ys - y:ye - y, xs_ - x:xe - x] * sa[..., None] + dst[..., :3] * (1 - sa[..., None])
        dst[..., 3] = sa + dst[..., 3] * (1 - sa)
    return layer


class Compositor:
    def __init__(self, p):
        self.p = Path(p)
        self.seg = load(p, "segment.json")
        plan = load(p, "plan.json")
        self.style = {**DEFAULT_STYLE, **plan.get("style", {})}
        self.style["colors"] = {**DEFAULT_STYLE["colors"], **self.style.get("colors", {})}
        self.blocks = plan["blocks"]
        for i, b in enumerate(self.blocks):
            nxt = self.blocks[i + 1]["start"] if i + 1 < len(self.blocks) else 1e9
            b["_fade"] = nxt - b["end"] > 0.15
        self.W, self.H = self.seg["width"], self.seg["height"]
        mj = self.p / "matte.json"
        self.cx = self.style["center_x"] if self.style.get("center_x") is not None else (
            json.loads(mj.read_text())["center_x"] if mj.exists() else 0.5)
        self.ts = Typesetter(self.style, self.H)
        self.layouts = {}

    def block_at(self, t):
        for i, b in enumerate(self.blocks):
            if b["start"] <= t < b["end"]:
                return i, b
        return None, None

    def matte(self, n):
        f = self.p / "matte" / f"f_{n:05d}.png"
        if not f.exists():
            return None
        return np.asarray(Image.open(f), np.float32) / 255

    def head_top(self, b):
        """Tope de la cabeza (fracción del alto) promediado en el bloque; None sin matte."""
        fps, tops = self.seg["fps"], []
        for t in (b["start"], (b["start"] + b["end"]) / 2, b["end"] - 0.05):
            m = self.matte(max(0, int(t * fps)))
            if m is None:
                continue
            rows = np.where((m > 0.5).sum(1) > max(3, 0.01 * self.W))[0]
            if len(rows):
                tops.append(rows[0] / self.H)
        return float(np.median(tops)) if tops else None

    def auto_ink(self, placed, rgb, n):
        """Si el fondo detrás de las letras (fuera del sujeto) es claro, la tinta blanca pasa a oscura."""
        m = self.matte(n)
        lum = rgb.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
        vals = []
        for row in placed:
            if row["color"] != "white":
                continue
            x, y = row["x"], row["y"]
            mk = np.asarray(row["mask"], np.float32) / 255
            ys, ye = max(0, y), min(self.H, y + mk.shape[0])
            xs, xe = max(0, x), min(self.W, x + mk.shape[1])
            if ye <= ys or xe <= xs:
                continue
            w = mk[ys - y:ye - y, xs - x:xe - x]
            if m is not None:
                w = w * (1 - m[ys:ye, xs:xe])
            if w.sum() > 0:
                vals.append(float((lum[ys:ye, xs:xe] * w).sum() / w.sum()))
        if vals and np.mean(vals) > self.style.get("ink_threshold", 110):
            for row in placed:
                if row["color"] == "white":
                    row["color"] = "ink"

    def frame(self, rgb, n):
        t = n / self.seg["fps"]
        out = rgb.astype(np.float32)
        if self.style["dim_bg"]:
            out *= 1 - self.style["dim_bg"]
        i, b = self.block_at(t)
        if b is None:
            return rgb
        if i not in self.layouts:
            placed = layout_block(b, self.ts, self.W, self.H, self.cx, self.head_top(b))
            if self.style.get("auto_ink"):
                self.auto_ink(placed, rgb, n)
            self.layouts = {i: placed}
        layer = render_text_layer(self.layouts[i], t, b, self.style, self.W, self.H)
        a = layer[..., 3:4]
        if self.style["shadow"]:
            sh = Image.fromarray((a[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(self.H * 0.012))
            sa = np.asarray(sh, np.float32)[..., None] / 255 * self.style["shadow"]
            out = out * (1 - sa)
        out = layer[..., :3] * a + out * (1 - a)
        m = self.matte(n)
        if m is not None:
            m = m[..., None]
            out = rgb.astype(np.float32) * m + out * (1 - m)
        return np.clip(out, 0, 255).astype(np.uint8)


def read_frames(path, W, H, select=None):
    vf = ["-vf", f"select='{select}'", "-vsync", "0"] if select else []
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), *vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    size = W * H * 3
    while True:
        buf = dec.stdout.read(size)
        if len(buf) < size:
            break
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    dec.wait()


def cmd_preview(a):
    c = Compositor(a.project)
    times = [float(x) for x in a.times] if a.times else [
        min(b["end"] - 0.05, b["rows"][-1]["words"][-1]["t"] + 0.3) for b in c.blocks]
    fps = c.seg["fps"]
    idx = sorted({max(0, int(round(t * fps))) for t in times})
    sel = "+".join(f"eq(n\\,{i})" for i in idx)
    outdir = Path(a.project) / "preview"
    outdir.mkdir(exist_ok=True)
    thumbs = []
    for n, rgb in zip(idx, read_frames(Path(a.project) / c.seg["video"], c.W, c.H, sel)):
        im = Image.fromarray(c.frame(rgb, n))
        im.save(outdir / f"t_{n / fps:06.2f}.png")
        thumbs.append(im.resize((480, int(480 * c.H / c.W))))
    cols = 4
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 480, rows * thumbs[0].height), "black")
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 480, (i // cols) * im.height))
    sheet.save(outdir / "sheet.png")
    print(f"  {len(thumbs)} vistas previas → {outdir / 'sheet.png'}")


def cmd_render(a):
    p = Path(a.project)
    c = Compositor(p)
    song = load(p, "song.json")
    out = Path(a.out) if a.out else p / "final.mp4"
    dur, fps = c.seg["duration"], c.seg["fps"]
    if not (p / "matte" / "f_00000.png").exists():
        print("  ⚠ sin matte: la letra quedará encima del sujeto. Corre «matte» antes.")
    afade = max(0.0, dur - a.audio_fade)
    enc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{c.W}x{c.H}", "-r", str(fps), "-i", "-",
        "-ss", str(c.seg["song_start"]), "-t", str(dur), "-i", str(p / song["audio"]),
        "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:d=0.05,afade=t=out:st={afade:.3f}:d={a.audio_fade}",
        "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE)
    for n, rgb in enumerate(read_frames(p / c.seg["video"], c.W, c.H)):
        enc.stdin.write(c.frame(rgb, n).tobytes())
        if n % 48 == 0:
            print(f"  {n / fps:5.1f}/{dur:.1f} s")
    enc.stdin.close()
    enc.wait()
    print(f"  ✅ {out}")

# ─────────────────────────────── CLI ───────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def seg_opts(x):
        x.add_argument("--video", required=True)
        x.add_argument("--start", type=float, help="segundo de la canción donde arranca el video")
        x.add_argument("--auto", choices=["chorus", "first"], default="chorus")
        x.add_argument("--lead", type=float, default=0.4, help="segundos de música antes de la primera palabra")

    def plan_opts(x):
        x.add_argument("--layout", choices=["auto", "horizontal", "vertical"], default="auto",
                       help="auto = horizontal si el video es más ancho que alto (estilo y cortes para 16:9)")
        x.add_argument("--max-rows", type=int, help="filas máximas por bloque (horizontal: 2; vertical: sin límite)")
        x.add_argument("--merge-short", type=float,
                       help="funde bloques más cortos que esto, en s (horizontal: 0.7; vertical: 0)")

    s = sub.add_parser("song"); s.add_argument("project"); s.add_argument("song"); s.add_argument("--audio")
    s.add_argument("--lyrics", help="archivo con la letra (texto plano o LRC) si LRCLib no la tiene")
    s = sub.add_parser("segment"); s.add_argument("project"); seg_opts(s)
    s = sub.add_parser("align"); s.add_argument("project"); s.add_argument("--model", default="small")
    s.add_argument("--language")
    s = sub.add_parser("plan"); s.add_argument("project")
    s.add_argument("--words-per-block", type=int, default=4); s.add_argument("--row-chars", type=int, default=10)
    s.add_argument("--hold", type=float, default=0.5); s.add_argument("--force", action="store_true")
    plan_opts(s)
    s = sub.add_parser("matte"); s.add_argument("project"); s.add_argument("--ratio", type=float)
    s = sub.add_parser("preview"); s.add_argument("project"); s.add_argument("times", nargs="*")
    s = sub.add_parser("render"); s.add_argument("project"); s.add_argument("--out")
    s.add_argument("--crf", type=int, default=18); s.add_argument("--audio-fade", type=float, default=0.6)
    s = sub.add_parser("all"); s.add_argument("project"); s.add_argument("song"); s.add_argument("--audio")
    s.add_argument("--lyrics")
    seg_opts(s); s.add_argument("--model", default="small"); s.add_argument("--language")
    s.add_argument("--words-per-block", type=int, default=4); s.add_argument("--row-chars", type=int, default=10)
    s.add_argument("--hold", type=float, default=0.5); s.add_argument("--force", action="store_true")
    plan_opts(s)
    s.add_argument("--ratio", type=float)

    a = ap.parse_args()
    if a.cmd == "all":
        for name, fn in [("song", cmd_song), ("segment", cmd_segment), ("align", cmd_align),
                         ("plan", cmd_plan), ("matte", cmd_matte)]:
            print(f"[{name}]")
            fn(a)
        print("Listo para «preview» y «render».")
    else:
        {"song": cmd_song, "segment": cmd_segment, "align": cmd_align, "plan": cmd_plan,
         "matte": cmd_matte, "preview": cmd_preview, "render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main()
