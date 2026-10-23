#!/usr/bin/env python3
"""Fluxo Trevisa: proxy 720p -> detectar fala -> prévia -> aprovação -> exportação 4K.
Nenhum comando sobrescreve o original. Python 3.12; FFmpeg/ffprobe no PATH.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def run(args, *, check=True):
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"Falhou ({p.returncode}): {' '.join(str(x) for x in args[:4])}\n{p.stderr[-1800:]}")
    return p


def ffprobe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                           "format=duration,size:stream=codec_type,codec_name,width,height,pix_fmt,color_transfer,color_primaries,color_space,r_frame_rate,avg_frame_rate",
                           "-of", "json", path]).stdout)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024 * 4), b""):
            h.update(chunk)
    return h.hexdigest()


def video_info(path):
    meta = ffprobe(path)
    vid = next((s for s in meta["streams"] if s["codec_type"] == "video"), None)
    if vid is None:
        raise RuntimeError("Não foi encontrado stream de vídeo.")
    return {"meta": meta, "video": vid,
            "duration": float(meta["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in meta["streams"])}


def save_json(path, data):
    if path.exists():
        raise FileExistsError(f"Já existe: {path}. Não será sobrescrito.")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def edit_module():
    p = Path(__file__).with_name("corte-pontual.py")
    spec = importlib.util.spec_from_file_location("corte_pontual", p)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {p}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_proxy(source, target):
    # Mantém proporção e FPS original; não aplica filtros que mudem os timecodes.
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-n", "-i", source,
           "-map", "0:v:0", "-map", "0:a:0?",
           "-vf", "scale=1280:720:force_original_aspect_ratio=decrease:force_divisible_by=2",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
           "-movflags", "+faststart", target]
    run(cmd)


def thumb_preview(edited, target, start, duration):
    take = min(15, max(0.2, duration - start))
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-n",
         "-ss", f"{start:.3f}", "-i", edited, "-t", f"{take:.3f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-b:a", "160k", target])


def normalise_source(path):
    src = path.expanduser().resolve(strict=True)
    if not src.is_file() or src.suffix.lower() not in {".mp4", ".mov", ".mkv"}:
        raise RuntimeError("Selecione um arquivo de vídeo MP4, MOV ou MKV.")
    return src


def prepare(args):
    source = normalise_source(args.video)
    work = (args.trabalho or source.parent / ("REVISAO_" + source.stem)).expanduser().resolve()
    work.mkdir(parents=True, exist_ok=True)
    report_path = work / "origem.json"
    ident = sha256(source)
    fingerprint = {"arquivo": str(source), "bytes": source.stat().st_size, "sha256": ident}
    if report_path.exists():
        previous = json.loads(report_path.read_text(encoding="utf-8"))
        if any(previous[k] != fingerprint[k] for k in fingerprint):
            raise RuntimeError("O original mudou! Use outra pasta de trabalho.")
    else:
        save_json(report_path, fingerprint)
    info = video_info(source)
    if not info["audio"]:
        raise RuntimeError("O vídeo não possui áudio para reconhecer a fala.")
    proxy = work / "proxy_720p.mp4"
    if not proxy.exists():
        build_proxy(source, proxy)
    if abs(video_info(proxy)["duration"] - info["duration"]) > .3:
        raise RuntimeError("Duração proxy e original divergem. Revisar antes de continuar.")

    clip_module = edit_module()
    words_path = work / "palavras.json"
    if words_path.exists():
        words = json.loads(words_path.read_text(encoding="utf-8"))
    else:
        print("Transcrevendo proxy com faster-whisper...", flush=True)
        words = clip_module.words_from_video(proxy, args.modelo)
        save_json(words_path, words)

    candidates = clip_module.candidates(words, args.frase)
    if not (work / "transcricao.txt").exists():
        (work / "transcricao.txt").write_text(" ".join(w["raw"] for w in words), encoding="utf-8")
    plan = work / "revisao.json"
    if not plan.exists():
        choice = candidates[0] if len(candidates) == 1 else None
        payload = {
            "aprovado": False,
            "frase_a_remover": args.frase,
            "inicio": choice["inicio_sugerido"] if choice else None,
            "fim": choice["fim_sugerido"] if choice else None,
            "comentarios_editor": "Confira início/fim da oração, letreiros na imagem e continuidade da trilha.",
            "candidatos": candidates,
            "proxy": str(proxy),
            "original_sha256": ident,
            "aprovador": None
        }
        save_json(plan, payload)

    review = json.loads(plan.read_text(encoding="utf-8"))
    begin, end = review.get("inicio"), review.get("fim")
    edited = work / "PREVIA_COMPLETA_720p.mp4"
    sample = work / "AMOSTRA_DA_EMENDA.mp4"
    if begin is not None and end is not None:
        begin, end = float(begin), float(end)
        if not (0.3 < begin < end < info["duration"] - 0.3):
            raise RuntimeError("Timecodes inválidos; revise revisao.json.")
        if not edited.exists():
            clip_module.render(proxy, edited, begin, end, info["duration"],
                               True, args.fade, False)
        if not sample.exists():
            newdur = video_info(edited)["duration"]
            thumb_preview(edited, sample, max(0, begin - 6), newdur)
    print(json.dumps({"estado": "aguardando_aprovacao",
                      "pasta": str(work), "proxy": str(proxy),
                      "revisao": str(plan),
                      "candidatos": candidates,
                      "previa": str(edited) if edited.exists() else None,
                      "amostra": str(sample) if sample.exists() else None}, ensure_ascii=False))


def finalise(args):
    source = normalise_source(args.video)
    work = (args.trabalho or source.parent / ("REVISAO_" + source.stem)).expanduser().resolve(strict=True)
    fingerprint = json.loads((work / "origem.json").read_text(encoding="utf-8"))
    if fingerprint["bytes"] != source.stat().st_size or fingerprint["sha256"] != sha256(source):
        raise RuntimeError("Arquivo 4K diferente do original aprovado. Exportação bloqueada.")
    review = json.loads((work / "revisao.json").read_text(encoding="utf-8"))
    if review.get("aprovado") is not True:
        raise RuntimeError("A prévia não foi aprovada no revisao.json. Não exportar o 4K.")
    if review.get("original_sha256") != fingerprint["sha256"]:
        raise RuntimeError("Plano de revisão não corresponde ao arquivo original.")
    begin, end = review.get("inicio"), review.get("fim")
    if begin is None or end is None:
        raise RuntimeError("Timecodes ausentes em revisao.json.")
    begin, end = float(begin), float(end)
    info = video_info(source)
    v = info["video"]
    if re.search(r"(p10|p12|10le|12le)", v.get("pix_fmt", "")) or v.get("color_transfer") in ("smpte2084", "arib-std-b67"):
        raise RuntimeError("Fonte 10/12-bit ou HDR. Exige finalização com preservação explícita de HDR, não usar H.264 8-bit.")
    output = work / ("FINAL_4K_" + source.stem + ".mp4")
    if output.exists():
        raise RuntimeError(f"Exportação já existe: {output}. Não sobrescrever.")
    edit_module().render(source, output, begin, end, info["duration"],
                         info["audio"], args.fade, args.nvenc)
    result = video_info(output)
    fps = Fraction(v.get("r_frame_rate", "30/1"))
    expected = info["duration"] - (end - begin) - args.fade
    tolerance = max(0.20, 4 / float(fps))
    success = (abs(result["duration"] - expected) < tolerance and
               result["video"].get("width") == v.get("width") and
               result["video"].get("height") == v.get("height") and
               result["audio"] == info["audio"])
    qa = {"passou": success, "saida": str(output), "original_sha256": fingerprint["sha256"],
          "duracao_esperada": round(expected, 3), "duracao_final": round(result["duration"], 3),
          "resolucao_original": [v.get("width"), v.get("height")],
          "resolucao_saida": [result["video"].get("width"), result["video"].get("height")],
          "audio_presente": result["audio"], "checar_manualmente": [
              "ouvir 5 segundos antes/depois do corte",
              "verificar continuidade de música e entonação",
              "revisar letreiros de ranking e transição visual"]}
    save_json(work / "QA_FINAL.json", qa)
    if not success:
        raise RuntimeError("Arquivo criado, porém QA falhou. Veja QA_FINAL.json.")
    print(json.dumps({"estado": "renderizado_4k_pendente_qa_humano",
                      "saida": str(output), "qa": str(work / "QA_FINAL.json")}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("etapa", choices=("preparar", "finalizar"))
    p.add_argument("video", type=Path)
    p.add_argument("--trabalho", type=Path)
    p.add_argument("--frase", default="17 maior construtora do Brasil")
    p.add_argument("--modelo", default="small")
    p.add_argument("--fade", type=float, default=0.16)
    p.add_argument("--nvenc", action="store_true")
    args = p.parse_args()
    if not .02 <= args.fade <= .8:
        p.error("--fade deve ficar entre 0.02 e 0.8 segundo.")
    if args.etapa == "preparar":
        prepare(args)
    else:
        finalise(args)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("ERRO: " + str(exc), file=sys.stderr)
        sys.exit(1)
