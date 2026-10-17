#!/usr/bin/env python3
"""Áudio automático: limpeza de voz, loudness por plataforma e trilha com ducking.

Uso:
  audio.py VIDEO_OU_AUDIO [--plataforma web|tv|podcast] [--trilha musica.mp3] [--trilha-db -18]
           [--sem-limpeza] [--out DIR]

Saídas em DIR:
  audio.json          medições antes/depois (LUFS integrado, true peak, LRA) e decisões
  final.<ext>         mídia com o áudio tratado (vídeo copiado sem recodificar)
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ALVOS = {"web": (-14.0, -1.0), "tv": (-23.0, -1.0), "podcast": (-16.0, -1.0)}


def medir(path, extra_filter=""):
    """Mede loudness com ebur128 (LUFS integrado, LRA, true peak)."""
    af = (extra_filter + "," if extra_filter else "") + "ebur128=peak=true"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-filter_complex", f"[0:a]{af}",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    resumo = r.stderr[r.stderr.rfind("Summary:"):]
    def num(rx):
        m = re.search(rx, resumo)
        return float(m.group(1)) if m else None
    return {"lufs": num(r"I:\s+(-?[\d.]+) LUFS"), "lra": num(r"LRA:\s+(-?[\d.]+) LU"), "true_peak": num(r"Peak:\s+(-?[\d.]+) dBFS")}


def ruido_db(path):
    """Estima o piso de ruído (RMS mínimo em janelas) para decidir a força da redução de ruído."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                        "astats=metadata=1:reset=1:length=0.5,ametadata=print:key=lavfi.astats.Overall.RMS_level",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    vals = [float(v) for v in re.findall(r"RMS_level=(-?[\d.]+)", r.stderr) if v not in ("-inf",)]
    vals = sorted(v for v in vals if v > -120)
    return vals[max(0, len(vals) // 10)] if vals else -90.0


def tem_video(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=index", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True).stdout
    return bool(out.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("midia")
    ap.add_argument("--plataforma", default="web", choices=sorted(ALVOS))
    ap.add_argument("--trilha", help="música de fundo; entra com ducking sob a voz")
    ap.add_argument("--trilha-db", type=float, default=-18.0, help="volume base da trilha (dB) antes do ducking")
    ap.add_argument("--sem-limpeza", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()

    src = Path(a.midia).resolve()
    out = Path(a.out or src.parent / f"{src.stem}_audio")
    out.mkdir(parents=True, exist_ok=True)
    alvo_i, alvo_tp = ALVOS[a.plataforma]
    antes = medir(src)
    piso = ruido_db(src)
    decisoes = []

    voz = []
    if not a.sem_limpeza:
        voz += ["highpass=f=80", "lowpass=f=16000"]
        if piso > -60:  # ruído audível: redução proporcional ao piso
            nr = min(30, max(10, int((piso + 75) / 1.5)))
            voz.append(f"afftdn=nr={nr}:nf={max(-80, int(piso) - 5)}")
            decisoes.append(f"redução de ruído nr={nr} dB (piso {piso:.1f} dBFS)")
        voz.append("acompressor=threshold=-20dB:ratio=3:attack=10:release=200:makeup=2")
        decisoes.append("high-pass 80 Hz, compressor 3:1 para voz")
    loud = f"loudnorm=I={alvo_i}:TP={alvo_tp}:LRA=11"
    decisoes.append(f"loudness alvo {alvo_i} LUFS / TP {alvo_tp} dBTP ({a.plataforma})")

    ext = src.suffix if tem_video(src) else ".wav"
    final = out / f"final{ext}"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
    cadeia_voz = ",".join(voz) if voz else "anull"
    if a.trilha:
        cmd += ["-stream_loop", "-1", "-i", str(Path(a.trilha).resolve())]
        grafo = (f"[0:a]{cadeia_voz},asplit=2[voz][sc];"
                 f"[1:a]volume={a.trilha_db}dB[mus];"
                 f"[mus][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[duck];"
                 f"[voz][duck]amix=inputs=2:duration=first:normalize=0,{loud}[a]")
        decisoes.append(f"trilha a {a.trilha_db} dB com ducking (sidechain) sob a voz")
    else:
        grafo = f"[0:a]{cadeia_voz},{loud}[a]"
    cmd += ["-filter_complex", grafo, "-map", "[a]"]
    if ext != ".wav":
        cmd += ["-map", "0:v?", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-ar", "48000", str(final)]
    subprocess.run(cmd, check=True)

    depois = medir(final)
    ok = depois["lufs"] is not None and abs(depois["lufs"] - alvo_i) <= 1.5 and (depois["true_peak"] or 0) <= alvo_tp + 0.5
    rel = {"arquivo": src.name, "plataforma": a.plataforma, "antes": antes, "depois": depois, "piso_ruido_dbfs": round(piso, 1),
           "decisoes": decisoes, "dentro_do_alvo": ok, "saida": str(final)}
    (out / "audio.json").write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: rel[k] for k in ("antes", "depois", "dentro_do_alvo", "saida")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
