#!/usr/bin/env python3
"""Decupagem automática: silêncios, filler words, retakes -> EDL + relatório + render.

Uso:
  decupagem.py VIDEO [--out DIR] [--thresh -35] [--min-sil 0.35] [--handle 0.1]
               [--transcribe] [--model small] [--lang pt] [--render]

Saídas em DIR:
  segmentos.json   trechos mantidos (in/out em segundos, texto quando houver)
  cortes.edl       CMX3600 para importar no Premiere / Resolve
  decupagem.md     log de decupagem com timecodes, texto e o que foi descartado
  corte.mp4        (com --render) rough cut renderizado
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FILLERS_PT = {"é", "ãh", "ah", "eh", "hum", "hm", "humm", "tipo", "né", "então", "assim", "basicamente", "uh", "um"}


def ffprobe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True).stdout
    info = json.loads(out)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    fps = 30.0
    if v and v.get("avg_frame_rate", "0/0") != "0/0":
        n, d = v["avg_frame_rate"].split("/")
        fps = float(n) / float(d)
    return float(info["format"]["duration"]), fps, v is not None


def detect_silences(path, thresh, min_sil):
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
         f"silencedetect=noise={thresh}dB:d={min_sil}", "-f", "null", "-"],
        capture_output=True, text=True)
    sils, start = [], None
    for line in proc.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and start is not None:
            sils.append((start, float(m.group(1))))
            start = None
    return sils, start


def keep_from_silences(duration, sils, open_start, handle):
    if open_start is not None:
        sils.append((open_start, duration))
    keep, cur = [], 0.0
    for s, e in sils:
        a, b = cur, min(duration, s + handle)
        if b - a > 0.15:
            keep.append([max(0.0, a), b])
        cur = max(0.0, e - handle)
    if duration - cur > 0.15:
        keep.append([cur, duration])
    return keep


def texto_do_trecho(segs, x, b):
    """Texto falado dentro de [x, b): usa as palavras (ponto médio no trecho); sem palavras, o segmento inteiro."""
    out = []
    for s in segs:
        if not (s["start"] < b and s["end"] > x):
            continue
        ws = s.get("words") or []
        out += [w["word"] for w in ws if x <= (w["start"] + w["end"]) / 2 < b] if ws else [s["text"]]
    return " ".join(out)


def transcribe(path, model_name, lang):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper não instalado: pip install faster-whisper (ou rode sem --transcribe)")
    import numpy as np  # decodifica via ffmpeg: faster-whisper quebra com av>=17 (metadata_errors)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    model = WhisperModel(model_name, device=os.environ.get("VIDEO_WHISPER_DEVICE", "cpu"), compute_type="int8")  # "auto" quebra sem cublas
    segs, _ = model.transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text.strip(),
             "words": [{"start": w.start, "end": w.end, "word": w.word.strip()} for w in (s.words or [])]}
            for s in segs]


def norm_text(t):
    return re.sub(r"[^\w\s]", "", t.lower()).strip()


def refine_with_transcript(keep, segs):
    """Remove filler words isolados e retakes (mantém o último take de frases parecidas)."""
    dropped = []
    # retakes: frase i parecida com o início da frase i+1 -> descarta i
    retake_idx = set()
    for i in range(len(segs) - 1):
        a, b = norm_text(segs[i]["text"]), norm_text(segs[i + 1]["text"])
        if len(a) > 8 and difflib.SequenceMatcher(None, a, b[:len(a) + 10]).ratio() > 0.72:
            retake_idx.add(i)
            dropped.append({"tipo": "retake", "in": segs[i]["start"], "out": segs[i]["end"], "texto": segs[i]["text"]})
    cuts = [(segs[i]["start"], segs[i]["end"]) for i in retake_idx]
    for s in segs:
        for w in s["words"]:
            if norm_text(w["word"]) in FILLERS_PT and (w["end"] - w["start"]) < 1.2:
                cuts.append((w["start"], w["end"]))
                dropped.append({"tipo": "filler", "in": w["start"], "out": w["end"], "texto": w["word"]})
    for cs, ce in sorted(cuts):
        new = []
        for a, b in keep:
            if ce <= a or cs >= b:
                new.append([a, b])
                continue
            if cs - a > 0.15:
                new.append([a, cs])
            if b - ce > 0.15:
                new.append([ce, b])
        keep = new
    keep = [[a, b] for a, b in keep if b - a >= 0.3]  # sobras de handle viram micro-cortes
    return keep, dropped


def tc(sec, fps):
    fr = int(round(sec * fps))
    nfps = int(round(fps))
    return f"{fr // (3600 * nfps):02d}:{fr // (60 * nfps) % 60:02d}:{fr // nfps % 60:02d}:{fr % nfps:02d}"


def write_edl(keep, fps, clip_name, path):
    lines = ["TITLE: DECUPAGEM AUTOMATICA", "FCM: NON-DROP FRAME", ""]
    rec = 0.0
    for i, (a, b) in enumerate(keep, 1):
        lines.append(f"{i:03d}  AX       AA/V  C        {tc(a, fps)} {tc(b, fps)} {tc(rec, fps)} {tc(rec + b - a, fps)}")
        lines.append(f"* FROM CLIP NAME: {clip_name}")
        lines.append("")
        rec += b - a
    Path(path).write_text("\n".join(lines), encoding="utf-8")
def render(src, keep, out, has_video):
    parts, labels = [], []
    for i, (a, b) in enumerate(keep):
        if has_video:
            parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{i}]")
        parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.01,afade=t=out:st={max(0, b - a - 0.01):.3f}:d=0.01[a{i}]")
        labels.append((f"[v{i}]" if has_video else "") + f"[a{i}]")
    graph = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(keep)}:v={1 if has_video else 0}:a=1" + ("[v][a]" if has_video else "[a]")
    script = Path(out).with_suffix(".filter.txt")
    script.write_text(graph, encoding="utf-8")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src)]
    graph = Path(script).read_text(encoding="utf-8")
    # ffmpeg>=7 removeu -filter_complex_script (agora -/filter_complex); grafo curto vai inline em qualquer versão
    cmd += ["-filter_complex", graph] if len(graph) < 20000 else ["-/filter_complex", str(script)]
    cmd += (["-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium"] if has_video else [])
    cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(out)]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", default=None)
    ap.add_argument("--thresh", type=float, default=-35.0, help="limiar de silêncio em dB")
    ap.add_argument("--min-sil", type=float, default=0.35, help="silêncio mínimo (s) para cortar")
    ap.add_argument("--handle", type=float, default=0.1, help="respiro mantido em cada corte (s)")
    ap.add_argument("--transcribe", action="store_true", help="usa faster-whisper p/ fillers e retakes")
    ap.add_argument("--model", default="small")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--render", action="store_true")
    a = ap.parse_args()

    src = Path(a.video).resolve()
    out = Path(a.out or src.parent / f"{src.stem}_decupagem")
    out.mkdir(parents=True, exist_ok=True)

    duration, fps, has_video = ffprobe(src)
    sils, open_start = detect_silences(src, a.thresh, a.min_sil)
    keep = keep_from_silences(duration, sils, open_start, a.handle)
    segs, dropped = [], [{"tipo": "silencio", "in": s, "out": e} for s, e in sils]
    if a.transcribe:
        segs = transcribe(src, a.model, a.lang)
        keep, extra = refine_with_transcript(keep, segs)
        dropped += extra
        (out / "transcricao.json").write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
    kept_total = sum(b - x for x, b in keep)
    result = [{"in": round(x, 3), "out": round(b, 3),
               "texto": texto_do_trecho(segs, x, b)} for x, b in keep]
    (out / "segmentos.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    write_edl(keep, fps, src.name, out / "cortes.edl")

    md = [f"# Decupagem — {src.name}", "",
          f"- Duração original: {duration:.1f}s | Mantido: {kept_total:.1f}s ({kept_total / duration:.0%}) | Trechos: {len(keep)}",
          f"- Parâmetros: limiar {a.thresh} dB, silêncio mín. {a.min_sil}s, handle {a.handle}s, transcrição: {'sim' if a.transcribe else 'não'}",
          "", "## Trechos mantidos", "", "| # | In | Out | Texto |", "|---|---|---|---|"]
    md += [f"| {i} | {tc(r['in'], fps)} | {tc(r['out'], fps)} | {r['texto'][:90]} |" for i, r in enumerate(result, 1)]
    md += ["", "## Descartado", "", "| Tipo | In | Out | Texto |", "|---|---|---|---|"]
    md += [f"| {d['tipo']} | {tc(d['in'], fps)} | {tc(d['out'], fps)} | {d.get('texto', '')} |" for d in dropped]
    (out / "decupagem.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    if a.render and keep:
        render(src, keep, out / "corte.mp4", has_video)
    print(json.dumps({"saida": str(out), "original_s": round(duration, 2), "mantido_s": round(kept_total, 2),
                      "trechos": len(keep), "render": a.render}, ensure_ascii=False))


if __name__ == "__main__":
    main()
