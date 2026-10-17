#!/usr/bin/env python3
"""Legendas automáticas: transcrição (faster-whisper) -> SRT (regras PT-BR) + ASS estilizado + burn-in.

Uso:
  legendas.py VIDEO [--estilo padrao|karaoke|minimal] [--json transcricao.json]
              [--lang pt] [--model small] [--fonte "Montserrat ExtraBold"] [--cor-destaque FFD400]
              [--glossario termos.txt] [--out DIR] [--burn]

--json reaproveita a transcrição gerada pela skill video-decupagem (mesmo formato).
--glossario: arquivo "errado=certo" por linha (nomes próprios, marcas) aplicado no texto.
"""
import argparse
import json
import os
import re
import subprocess
from pathlib import Path

MAX_CHARS, MAX_LINES, MAX_CPS, MIN_DUR, MAX_DUR = 42, 2, 17, 1.0, 6.0


def probe_size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "json", str(path)], capture_output=True, text=True).stdout
    s = (json.loads(out).get("streams") or [{}])[0]
    return s.get("width", 1920), s.get("height", 1080)


def transcribe(path, model_name, lang):
    from faster_whisper import WhisperModel
    import numpy as np  # decodifica via ffmpeg: faster-whisper quebra com av>=17 (metadata_errors)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    model = WhisperModel(model_name, device=os.environ.get("VIDEO_WHISPER_DEVICE", "cpu"), compute_type="int8")  # "auto" quebra sem cublas
    segs, _ = model.transcribe(audio, language=lang, word_timestamps=True, vad_filter=True)
    return [{"start": s.start, "end": s.end, "text": s.text.strip(),
             "words": [{"start": w.start, "end": w.end, "word": w.word.strip()} for w in (s.words or [])]}
            for s in segs]


def apply_glossary(segs, path):
    if not path:
        return segs
    rules = [l.split("=", 1) for l in Path(path).read_text(encoding="utf-8").splitlines() if "=" in l]
    for s in segs:
        for w in s["words"]:
            for bad, good in rules:
                w["word"] = re.sub(rf"\b{re.escape(bad.strip())}\b", good.strip(), w["word"], flags=re.I)
    return segs


def all_words(segs):
    words = [w for s in segs for w in s["words"] if w["word"]]
    if not words:  # transcrição sem timestamps por palavra: distribui pelo segmento
        for s in segs:
            toks = s["text"].split()
            step = (s["end"] - s["start"]) / max(1, len(toks))
            words += [{"start": s["start"] + i * step, "end": s["start"] + (i + 1) * step, "word": t} for i, t in enumerate(toks)]
    merged = []
    for w in words:  # o whisper separa "bem-vindos" em "bem" + "-vindos"
        if merged and w["word"].startswith("-"):
            merged[-1] = {"start": merged[-1]["start"], "end": w["end"], "word": merged[-1]["word"] + w["word"]}
        else:
            merged.append(w)
    return merged


def group_cues(words, max_chars, max_lines, max_words=None):
    """Agrupa palavras em legendas respeitando caracteres, linhas, CPS, pausas e pontuação."""
    cues, cur = [], []
    limit = max_chars * max_lines
    for i, w in enumerate(words):
        cur.append(w)
        text = " ".join(x["word"] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 99
        dur = w["end"] - cur[0]["start"]
        nxt_len = len(text) + 1 + len(nxt["word"]) if nxt else 0
        if (nxt is None or gap > 0.6 or re.search(r"[.!?…]$", w["word"])
                or (re.search(r"[,;:]$", w["word"]) and len(text) > max_chars * 0.6)
                or nxt_len > limit or dur > MAX_DUR or (max_words and len(cur) >= max_words)):
            cues.append(cur)
            cur = []
    return cues


def wrap(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    words, best = text.split(), None
    for i in range(1, len(words)):  # quebra mais equilibrada (linha de cima menor ou igual — "pirâmide")
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= max_chars and len(b) <= max_chars:
            score = abs(len(a) - len(b)) + (3 if len(a) > len(b) else 0)
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else [text[:max_chars], text[max_chars:]]


def timing(cues):
    out = []
    for i, c in enumerate(cues):
        start, end = c[0]["start"], c[-1]["end"]
        text = " ".join(w["word"] for w in c)
        end = max(end, start + MIN_DUR, start + len(text) / MAX_CPS)
        if i + 1 < len(cues):
            end = min(end, cues[i + 1][0]["start"] - 0.04)
        out.append((start, max(end, start + 0.3), c))
    return out


def ts(sec, sep=","):
    ms = int(round(sec * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d}{sep}{ms % 1000:03d}"


def ass_ts(sec):
    cs = int(round(sec * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ass_color(hexrgb, alpha="00"):
    h = hexrgb.lstrip("#")
    return f"&H{alpha}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def write_ass(timed, path, w, h, estilo, fonte, destaque):
    vertical = h > w
    size = int(h * (0.055 if estilo == "karaoke" else 0.045 if vertical else 0.05))
    margin_v = int(h * (0.30 if vertical and estilo == "karaoke" else 0.08))
    bold = -1 if estilo != "minimal" else 0
    outline = 4 if estilo == "karaoke" else 2
    back = "&H64000000" if estilo == "minimal" else "&H00000000"
    border = 3 if estilo == "minimal" else 1
    primary = ass_color(destaque) if estilo == "karaoke" else "&H00FFFFFF"
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{fonte},{size},{primary},&H00FFFFFF,&H00000000,{back},{bold},0,0,0,100,100,0,0,{border},{outline},1,2,{int(w * 0.08)},{int(w * 0.08)},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for start, end, cue in timed:
        if estilo == "karaoke":
            parts = []
            for i, wd in enumerate(cue):
                nxt = cue[i + 1]["start"] if i + 1 < len(cue) else end
                k = max(1, int(round((nxt - (wd["start"] if i else start)) * 100)))
                parts.append(f"{{\\k{k}}}{wd['word'].upper()}")
            text = "{\\fad(60,0)}" + " ".join(parts)
        else:
            text = "\\N".join(wrap(" ".join(x["word"] for x in cue), MAX_CHARS))
        lines.append(f"Dialogue: 0,{ass_ts(start)},{ass_ts(end)},Default,,0,0,0,,{text}")
    Path(path).write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--estilo", default="padrao", choices=["padrao", "karaoke", "minimal"])
    ap.add_argument("--json", help="transcrição pronta (formato da skill video-decupagem)")
    ap.add_argument("--lang", default="pt")
    ap.add_argument("--model", default="small")
    ap.add_argument("--fonte", default="Montserrat ExtraBold")
    ap.add_argument("--cor-destaque", default="FFD400")
    ap.add_argument("--glossario")
    ap.add_argument("--out")
    ap.add_argument("--burn", action="store_true")
    a = ap.parse_args()

    src = Path(a.video).resolve()
    out = Path(a.out or src.parent / f"{src.stem}_legendas")
    out.mkdir(parents=True, exist_ok=True)
    w, h = probe_size(src)
    segs = json.loads(Path(a.json).read_text(encoding="utf-8")) if a.json else transcribe(src, a.model, a.lang)
    words = all_words(apply_glossary(segs, a.glossario))

    if a.estilo == "karaoke":
        cues = group_cues(words, 18, 1, max_words=4)
    else:
        cues = group_cues(words, MAX_CHARS, MAX_LINES)
    timed = timing(cues)

    srt = []
    for i, (s, e, c) in enumerate(timed, 1):
        srt.append(f"{i}\n{ts(s)} --> {ts(e)}\n" + "\n".join(wrap(" ".join(x["word"] for x in c), MAX_CHARS)) + "\n")
    (out / "legendas.srt").write_text("\n".join(srt), encoding="utf-8")
    (out / "legendas.vtt").write_text("WEBVTT\n\n" + "\n".join(
        f"{ts(s, '.')} --> {ts(e, '.')}\n" + "\n".join(wrap(" ".join(x["word"] for x in c), MAX_CHARS)) + "\n"
        for s, e, c in timed), encoding="utf-8")
    ass = out / f"legendas_{a.estilo}.ass"
    write_ass(timed, ass, w, h, a.estilo, a.fonte, a.cor_destaque)

    if a.burn:
        esc = str(ass).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf", f"ass='{esc}'",
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy",
                        str(out / "legendado.mp4")], check=True)
    print(json.dumps({"saida": str(out), "legendas": len(timed), "estilo": a.estilo, "burn": a.burn,
                      "resolucao": f"{w}x{h}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
