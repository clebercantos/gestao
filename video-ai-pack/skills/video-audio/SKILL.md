---
name: video-audio
description: "Áudio de vídeo: limpeza de voz/ruído, loudness por plataforma (web -14, TV -23, podcast -16 LUFS), trilha com ducking e mix final."
---

# Áudio automático

Ordem: **limpar a voz antes de decupar** (melhora a transcrição) → montar → **mix final por último** (loudness sobre o corte final).

## Rota (escolha automática)
| Situação | Rota |
|---|---|
| Premiere aberto | Filmit `pr_applyEffect` ou Premiere MCP: Essential Sound (Diálogo → Enhance Speech, Loudness Auto-Match); trilha com Auto-Ducking |
| Resolve aberto | Fairlight via Resolve MCP (skill `resolve-audio` do cofre): Voice Isolation, Dialogue Leveler, normalização por plataforma |
| Voz muito ruim (externa, eco) | Adobe `media_enhance_speech` ou Magnific `audio_clean_speech`/`video_audio_isolate`, depois o script para o loudness |
| Local / rápido | script abaixo |

## Script local
```bash
A=~/.claude/skills/video-audio/scripts/audio.py        # no Windows: py -3.12 ...
python3 $A video.mp4                                   # limpeza + -14 LUFS (web/redes)
python3 $A video.mp4 --plataforma tv                   # -23 LUFS (EBU R128)
python3 $A video.mp4 --trilha musica.mp3 --trilha-db -20   # trilha com ducking sob a voz
python3 $A video.mp4 --sem-limpeza                     # só loudness (áudio já tratado)
```
Saídas: `final.<ext>`, com o vídeo copiado sem recodificar, e `audio.json`, com as medições antes/depois, as decisões e `dentro_do_alvo`.

## Decisões automáticas
- A redução de ruído só entra se o piso medido passar de −60 dBFS. A força é proporcional ao ruído, para não criar artefatos "robóticos".
- Toda voz recebe high-pass em 80 Hz e um compressor 3:1 suave.
- Loudness de dois estágios via `loudnorm`. True peak ≤ −1 dBTP.
- Trilha: −18 a −22 dB sob a voz, com sidechain (ratio 8, release 400 ms). Sem voz, volta ao nível base.
- Se `dentro_do_alvo` vier `false`, investigue antes de entregar: clipping no original, trecho mudo longo ou música alta demais.
