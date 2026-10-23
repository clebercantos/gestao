#!/usr/bin/env python3
"""Corte pontual de uma frase em MP4. Não altera o visual intencionalmente; preserva o arquivo original.
A análise de fala é opcional; sem timecodes confirmados, gera plano para revisão.
Uso:
  py -3.12 corte-pontual.py video.mp4 --buscar "17 maior construtora do Brasil"
  py -3.12 corte-pontual.py video.mp4 --inicio 32.40 --fim 38.10 --render --nvenc
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


def command(argv: list[str], *, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(argv, stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None, check=True)


def probe(source: Path) -> dict:
    p = command(["ffprobe", "-v", "error", "-show_entries",
                 "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate",
                 "-of", "json", str(source)])
    return json.loads(p.stdout.decode("utf-8"))


def clean(text: str) -> str:
    text = "".join(c for c in unicodedata.normalize("NFKD", text.lower())
                   if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def words_from_video(source: Path, model_name: str) -> list[dict]:
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Requer Python 3.12 com numpy e faster-whisper instalados.") from exc
    raw = command(["ffmpeg", "-v", "error", "-i", str(source),
                   "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                   "-f", "f32le", "pipe:1"]).stdout
    audio = np.frombuffer(raw, dtype=np.float32)
    whisper = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _ = whisper.transcribe(audio, language="pt", word_timestamps=True,
                                     vad_filter=True, condition_on_previous_text=False)
    result: list[dict] = []
    for seg in segments:
        for word in seg.words or []:
            tok = clean(word.word)
            if tok:
                result.append({"start": round(float(word.start), 3),
                               "end": round(float(word.end), 3),
                               "raw": word.word, "token": tok})
    return result


def candidates(words: list[dict], phrase: str) -> list[dict]:
    # O âncora semântica é mais estável do que o ordinal: Whisper alterna
    # "17", "décima sétima" e "dezessete".
    tokens = [w["token"] for w in words]
    requested = clean(phrase).split()
    anchor = ["maior", "construtora", "do", "brasil"] if "construtora" in requested else requested
    if not anchor:
        return []
    output = []
    for i in range(len(tokens)):
        # Aceita até 2 palavras extras entre as palavras da expressão-alvo.
        j, matches = i, []
        for piece in anchor:
            for k in range(j, min(j + 4, len(tokens))):
                if tokens[k] == piece:
                    matches.append(k)
                    j = k + 1
                    break
            else:
                break
        if len(matches) != len(anchor):
            continue
        begin = max(0, matches[0] - 10)
        before = " ".join(tokens[begin:matches[0]])
        numeral = bool(re.search(r"\b(17|17a|17o|dezessete|decima\s+setima|decimo\s+setimo|decima\s+sete)\b", before))
        if "17" in requested and not numeral:
            continue
        # Recupera o começo da frase falada, limitado a oito segundos.
        k = matches[0] - 1
        while k > 0 and words[matches[0]]["start"] - words[k - 1]["start"] <= 8:
            if re.search(r"[.!?]", words[k - 1]["raw"]):
                break
            k -= 1
        final = matches[-1]
        # Início/fim incluem pequena margem acústica; confirme no preview.
        start = max(0, words[k]["start"] - 0.15)
        end = words[final]["end"] + 0.18
        output.append({"inicio_sugerido": round(start, 3),
                       "fim_sugerido": round(end, 3),
                       "expressao": " ".join(words[t]["raw"] for t in range(k, final + 1)),
                       "numeral_identificado": numeral})
    # Desduplicação quando o matcher acha várias âncoras no mesmo período.
    unique = {}
    for c in output:
        unique[round(c["fim_sugerido"], 1)] = c
    return list(unique.values())


def render(source: Path, dest: Path, start: float, end: float,
           duration: float, has_audio: bool, fade: float, nvenc: bool) -> None:
    if start < 0 or end <= start or end >= duration:
        raise ValueError(f"Faixa inválida: {start}-{end}s; duração {duration:.2f}s")
    if fade <= 0 or start <= fade or end + fade >= duration:
        raise ValueError("O crossfade deve ser positivo e caber nos dois lados do corte.")
    # A/V terminam sincronizados: no vídeo removemos mais fade segundos
    # (metade antes + metade depois), no áudio sobrepomos fade segundos.
    v1 = start - fade / 2
    v2 = end + fade / 2
    filters = (
        f"[0:v:0]trim=start=0:end={v1:.6f},setpts=PTS-STARTPTS[v0];"
        f"[0:v:0]trim=start={v2:.6f}:end={duration:.6f},setpts=PTS-STARTPTS[v1];"
        f"[v0][v1]concat=n=2:v=1:a=0[v]"
    )
    if has_audio:
        filters += (
            f";[0:a:0]atrim=start=0:end={start:.6f},asetpts=PTS-STARTPTS[a0];"
            f"[0:a:0]atrim=start={end:.6f}:end={duration:.6f},asetpts=PTS-STARTPTS[a1];"
            f"[a0][a1]acrossfade=d={fade:.6f}:c1=tri:c2=tri[a]"
        )
    args = ["ffmpeg", "-hide_banner", "-y", "-i", str(source),
            "-filter_complex", filters, "-map", "[v]"]
    if has_audio:
        args += ["-map", "[a]", "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
    if nvenc:
        args += ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-cq", "18", "-b:v", "0"]
    else:
        args += ["-c:v", "libx264", "-preset", "slow", "-crf", "17"]
    args += ["-pix_fmt", "yuv420p", "-movflags", "+faststart",
             "-map_metadata", "0", str(dest)]
    subprocess.run(args, check=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video", type=Path)
    p.add_argument("--buscar", default="", help="Frase para localizar com faster-whisper")
    p.add_argument("--modelo", default="small", help="Modelo faster-whisper: small ou medium")
    p.add_argument("--inicio", type=float, help="Primeiro frame a descartar, segundos")
    p.add_argument("--fim", type=float, help="Último frame a descartar, segundos")
    p.add_argument("--render", action="store_true", help="Confirma render com os timecodes definidos")
    p.add_argument("--nvenc", action="store_true", help="Codificador Nvidia RTX (H.264)")
    p.add_argument("--fade", type=float, default=0.16, help="Crossfade somente no áudio, em segundos")
    p.add_argument("--saida", type=Path, help="MP4 resultante, sempre caminho diferente do original")
    a = p.parse_args()
    original = a.video.expanduser().resolve(strict=True)
    if original.suffix.lower() not in {".mp4", ".mov", ".mkv"}:
        p.error("Aceita vídeo MP4/MOV/MKV.")
    data = probe(original)
    duration = float(data["format"]["duration"])
    streams = data["streams"]
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not video:
        p.error("Arquivo não contém imagem de vídeo.")
    audio = any(s.get("codec_type") == "audio" for s in streams)
    dest = (a.saida or original.with_name(original.stem + "_CORTE.mp4")).expanduser().resolve()
    if dest == original:
        p.error("Saída deve ser diferente do vídeo original.")
    if dest.exists():
        p.error("A saída já existe; especifique --saida com outro nome. Nada foi sobrescrito.")

    plano = {"original": str(original), "saida": str(dest),
             "duracao_original": round(duration, 3),
             "resolucao": [video.get("width"), video.get("height")],
             "fps": video.get("r_frame_rate"), "audio": audio, "busca": a.buscar}
    if a.buscar:
        ws = words_from_video(original, a.modelo)
        plano["candidatos"] = candidates(ws, a.buscar)
        plano["transcricao"] = " ".join(w["raw"] for w in ws)
        if a.inicio is None or a.fim is None:
            print("Timecodes não definidos. Confira candidatos e execute com --inicio/--fim --render.")
    if a.inicio is not None and a.fim is not None:
        plano["intervalo_removido"] = [a.inicio, a.fim]
    arquivo_plano = dest.with_suffix(".plano.json")
    arquivo_plano.write_text(json.dumps(plano, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Plano: {arquivo_plano}")
    if a.render:
        if a.inicio is None or a.fim is None:
            p.error("--render exige --inicio e --fim confirmados.")
        render(original, dest, a.inicio, a.fim, duration, audio, a.fade, a.nvenc)
        check = probe(dest)
        plano["duracao_saida"] = float(check["format"]["duration"])
        plano["status"] = "renderizado"
        arquivo_plano.write_text(json.dumps(plano, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Vídeo pronto: {dest}")
    else:
        print("Nenhum render executado. Revise a transcrição e os pontos de corte.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        sys.exit(1)
