#!/usr/bin/env python3
"""Pipeline completo de edição com um comando, sem gastar tokens: decupagem → cor → áudio → formato → legendas → entrega.

Uso:
  pipeline.py VIDEO [--preset reels|youtube|tv|podcast] [--look natural|cinematic|quente|frio|pb|vintage]
              [--saida DIR] [--sem-transcricao] [--sem-cor] [--sem-audio] [--trilha musica.mp3]
  pipeline.py --monitorar PASTA [--loop] [mesmas opções]
      PASTA/entrada      solte os vídeos aqui
      PASTA/saida        resultado de cada vídeo (ENTREGA/ + etapas + decisoes.md)
      PASTA/processados  originais já processados (nunca são apagados)
      PASTA/erros        originais que falharam + log

Presets:
  reels    9:16 1080x1920, cor viva, legenda karaokê gravada no vídeo, -14 LUFS
  youtube  16:9, legenda em SRT separado, -14 LUFS
  tv       16:9, legenda SRT, -23 LUFS (EBU R128)
  podcast  16:9, legenda SRT, -16 LUFS, cor natural
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
SKILLS = next((p for p in (PACK / "skills", Path.home() / ".claude" / "skills") if (p / "video-decupagem").exists()), PACK / "skills")
SCRIPTS = {
    "decupagem": SKILLS / "video-decupagem" / "scripts" / "decupagem.py",
    "cor": SKILLS / "video-colorgrade" / "scripts" / "analisar_cor.py",
    "audio": SKILLS / "video-audio" / "scripts" / "audio.py",
    "legendas": SKILLS / "video-legendas" / "scripts" / "legendas.py",
}
PRESETS = {
    "reels": {"look": "cinematic", "plataforma": "web", "vertical": True, "legenda": "karaoke", "burn": True},
    "youtube": {"look": "natural", "plataforma": "web", "vertical": False, "legenda": "padrao", "burn": False},
    "tv": {"look": "natural", "plataforma": "tv", "vertical": False, "legenda": "padrao", "burn": False},
    "podcast": {"look": "natural", "plataforma": "podcast", "vertical": False, "legenda": "padrao", "burn": False},
}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".mxf", ".avi", ".m4v", ".webm"}


def etapa(nome, cmd, log):
    """Roda um script do pack; devolve o JSON da última linha (ou None em falha)."""
    t0 = time.time()
    p = subprocess.run([sys.executable, *map(str, cmd)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    log.append(f"## {nome} ({time.time() - t0:.0f}s, código {p.returncode})\n```\n{(p.stdout + p.stderr).strip()[-1500:]}\n```\n")
    if p.returncode:
        return None
    for linha in reversed(p.stdout.strip().splitlines()):
        try:
            return json.loads(linha)
        except ValueError:
            continue
    return {}


def vertical(src, dst):
    """16:9 → 9:16 pelo centro (o reframe por rosto fica com Premiere/Adobe quando disponível)."""
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vf",
                    "crop='min(iw,ih*9/16)':ih:'(iw-min(iw,ih*9/16))/2':0,scale=1080:1920,setsar=1",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "copy", str(dst)], check=True)


def processar(video, a):
    video = Path(video).resolve()
    cfg = dict(PRESETS[a.preset])
    if a.look:
        cfg["look"] = a.look
    carimbo = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    w = Path(a.saida or video.parent / "saida").resolve() / f"{video.stem}_{a.preset}_{carimbo}"
    w.mkdir(parents=True, exist_ok=True)
    log, dec, atual = [], [f"# Decisões — {video.name}", "", f"- Preset: **{a.preset}** {cfg}", f"- Início: {carimbo}", ""], video

    # 1. decupagem (com transcrição; se o modelo não estiver disponível, segue só com silêncios)
    r = None
    if not a.sem_transcricao:
        r = etapa("decupagem + transcrição", [SCRIPTS["decupagem"], atual, "--transcribe", "--render", "--out", w / "01_decupagem"], log)
        if r is None:
            dec.append("- Transcrição indisponível: decupagem só por silêncio, sem legendas")
            a.sem_transcricao = True
    if r is None:
        r = etapa("decupagem", [SCRIPTS["decupagem"], atual, "--render", "--out", w / "01_decupagem"], log)
    if r is not None and (w / "01_decupagem" / "corte.mp4").exists():
        atual = w / "01_decupagem" / "corte.mp4"
        dec.append(f"- Decupagem: {r.get('original_s')}s → {r.get('mantido_s')}s em {r.get('trechos')} trechos (EDL em 01_decupagem/cortes.edl)")
    else:
        dec.append("- Decupagem falhou: segue com o vídeo original (veja pipeline.log)")

    # 2. cor
    if not a.sem_cor:
        r = etapa("cor", [SCRIPTS["cor"], atual, "--look", cfg["look"], "--apply", "--out", w / "02_cor"], log)
        if r is not None and (w / "02_cor" / "graded.mp4").exists():
            atual = w / "02_cor" / "graded.mp4"
            dec.append(f"- Cor: look {cfg['look']}; decisões {r.get('decisoes')}; {r.get('consistencia')} (LUT em 02_cor/grade.cube)")
        else:
            dec.append("- Cor falhou: mantida a cor original")

    # 3. áudio
    if not a.sem_audio:
        cmd = [SCRIPTS["audio"], atual, "--plataforma", cfg["plataforma"], "--out", w / "03_audio"]
        if a.trilha:
            cmd += ["--trilha", a.trilha]
        r = etapa("áudio", cmd, log)
        finais = list((w / "03_audio").glob("final.*"))
        if r is not None and finais:
            atual = finais[0]
            dec.append(f"- Áudio: {r.get('antes', {}).get('lufs')} → {r.get('depois', {}).get('lufs')} LUFS, dentro do alvo: {r.get('dentro_do_alvo')}")
        else:
            dec.append("- Áudio falhou: mantido o áudio da etapa anterior")

    # 4. formato
    if cfg["vertical"]:
        try:
            vertical(atual, w / "04_vertical.mp4")
            atual = w / "04_vertical.mp4"
            dec.append("- Formato: 9:16 pelo centro (para reframe por rosto, use o Premiere/Adobe)")
        except subprocess.CalledProcessError:
            dec.append("- Reframe 9:16 falhou: entregue em 16:9")

    # 5. legendas (sempre sobre o corte final)
    srt = None
    if not a.sem_transcricao:
        cmd = [SCRIPTS["legendas"], atual, "--estilo", cfg["legenda"], "--out", w / "05_legendas"]
        if cfg["burn"]:
            cmd.append("--burn")
        r = etapa("legendas", cmd, log)
        if r is not None:
            srt = w / "05_legendas" / "legendas.srt"
            if cfg["burn"] and (w / "05_legendas" / "legendado.mp4").exists():
                atual = w / "05_legendas" / "legendado.mp4"
            dec.append(f"- Legendas: {r.get('legendas')} blocos, estilo {cfg['legenda']}{' gravadas no vídeo' if cfg['burn'] else ' em SRT'}")
        else:
            dec.append("- Legendas falharam (veja pipeline.log)")

    # 6. entrega
    e = w / "ENTREGA"
    e.mkdir(exist_ok=True)
    final = e / f"{video.stem}_{a.preset.upper()}_v001_{dt.date.today():%Y%m%d}{atual.suffix}"
    shutil.copy2(atual, final)
    for origem in (srt, w / "01_decupagem" / "cortes.edl", w / "02_cor" / "grade.cube"):
        if origem and Path(origem).exists():
            shutil.copy2(origem, e / Path(origem).name)
    sonda = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height:format=duration",
                            "-of", "compact=p=0", str(final)], capture_output=True, text=True).stdout.strip()
    dec += ["", "## Entrega", "", f"- `{final.name}`", f"- ffprobe: `{' | '.join(sonda.splitlines())}`",
            "- Projeto editável: `cortes.edl` (importe no Premiere/Resolve) e `grade.cube` (Lumetri > Creative > Look / nó de LUT)",
            "", "Revise um frame do resultado antes de publicar."]
    (w / "decisoes.md").write_text("\n".join(dec) + "\n", encoding="utf-8")
    (w / "pipeline.log").write_text("\n".join(log), encoding="utf-8")
    print(json.dumps({"entrega": str(final), "pasta": str(w)}, ensure_ascii=False))
    return final


def estavel(p):
    """Arquivo terminou de copiar? (tamanho igual em 5 s)"""
    t = p.stat().st_size
    time.sleep(5)
    return p.exists() and p.stat().st_size == t and t > 0


def monitorar(pasta, a):
    pasta = Path(pasta).resolve()
    dirs = {n: pasta / n for n in ("entrada", "saida", "processados", "erros")}
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    a.saida = str(dirs["saida"])
    while True:
        for v in sorted(dirs["entrada"].iterdir()):
            if v.suffix.lower() not in VIDEO_EXT or not estavel(v):
                continue
            print(f"processando {v.name}", flush=True)
            try:
                processar(v, argparse.Namespace(**vars(a)))
                shutil.move(str(v), dirs["processados"] / v.name)
            except Exception as ex:  # um vídeo com problema não trava a fila
                (dirs["erros"] / f"{v.name}.erro.txt").write_text(repr(ex), encoding="utf-8")
                shutil.move(str(v), dirs["erros"] / v.name)
        if not a.loop:
            return
        time.sleep(30)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?")
    ap.add_argument("--monitorar", metavar="PASTA")
    ap.add_argument("--loop", action="store_true", help="com --monitorar: fica vigiando (sem isso, processa a fila e sai)")
    ap.add_argument("--preset", default="youtube", choices=sorted(PRESETS))
    ap.add_argument("--look", choices=["natural", "cinematic", "quente", "frio", "pb", "vintage"])
    ap.add_argument("--saida")
    ap.add_argument("--trilha")
    ap.add_argument("--sem-transcricao", action="store_true")
    ap.add_argument("--sem-cor", action="store_true")
    ap.add_argument("--sem-audio", action="store_true")
    a = ap.parse_args()
    if a.monitorar:
        monitorar(a.monitorar, a)
    elif a.video:
        processar(a.video, a)
    else:
        ap.error("informe VIDEO ou --monitorar PASTA")


if __name__ == "__main__":
    main()
