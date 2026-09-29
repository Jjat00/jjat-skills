"""Paso final: une los tramos renderizados y verifica.
  python3 dk_finish.py CHUNKS_DIR OUT_DIR [--name Lugar_ruta_final]
Une final_*.mp4 + final_tail.mp4 -> OUT/<name>.mp4 ; plate_* -> OUT/plate.mp4 ; overlay_* -> OUT/overlay.mov ; copia endcard.mov
y compara el número de frames con lo esperado (ffprobe).
"""
import argparse, glob, os, subprocess

ap = argparse.ArgumentParser(); ap.add_argument('chunks'); ap.add_argument('out'); ap.add_argument('--name', default='ruta_final')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)

def parts(kind, ext):
    fs = sorted(f for f in glob.glob(os.path.join(a.chunks, f'{kind}_*.{ext}')) if not f.endswith(f'_tail.{ext}'))
    tail = os.path.join(a.chunks, f'{kind}_tail.{ext}')
    return fs + ([tail] if os.path.exists(tail) else [])

def nframes(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries',
                        'stream=nb_read_packets', '-of', 'csv=p=0', p], capture_output=True, text=True)
    return int(r.stdout.strip() or 0)

for kind, ext, out in (('final', 'mp4', f'{a.name}.mp4'), ('plate', 'mp4', 'plate.mp4'), ('overlay', 'mov', 'overlay.mov')):
    fs = parts(kind, ext)
    if not fs: print('sin tramos de', kind); continue
    lst = os.path.join(a.chunks, f'list_{kind}.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in fs))
    extra = ['-movflags', '+faststart'] if ext == 'mp4' else []
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy'] + extra + [os.path.join(a.out, out)], check=True)
    exp = sum(nframes(f) for f in fs); got = nframes(os.path.join(a.out, out))
    print(f'{out}: {len(fs)} tramos, {got} frames (esperado {exp})', 'OK' if got == exp else 'REVISAR')
ec = os.path.join(a.chunks, 'endcard.mov')
if os.path.exists(ec):
    subprocess.run(['cp', ec, os.path.join(a.out, 'endcard.mov')], check=True); print('endcard.mov:', nframes(ec), 'frames')
