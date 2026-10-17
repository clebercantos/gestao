---
name: video-entrega
description: "Exportação por plataforma e checklist de QA final de vídeo (codec, loudness, legendas, projeto editável)."
---

# Entrega e QA

## Presets (escolha automática pela PLATAFORMA do brief)
| Destino | Resolução | FPS | Vídeo | Áudio | Loudness |
|---|---|---|---|---|---|
| YouTube | 3840×2160 ou 1920×1080 | original | H.264 High CRF 16–18 / H.265 | AAC 320k 48 kHz | −14 LUFS, TP −1 |
| Reels / TikTok / Shorts | 1080×1920 | 30 | H.264 High, 12–16 Mbps | AAC 256k | −14 LUFS, TP −1 |
| Feed Instagram/LinkedIn | 1080×1350 (4:5) | 30 | H.264 | AAC 256k | −14 LUFS |
| TV / broadcast | 1920×1080 | 29.97/59.94 | ProRes 422 HQ / XDCAM | PCM 24-bit | −23 LUFS (EBU R128) / −24 LKFS |
| Master / arquivo | original | original | ProRes 422 HQ ou DNxHR HQX | PCM | — |

Rotas: Premiere MCP (`export_sequence`, `validate_export_preset`, `verify_delivery_file`); Resolve MCP (render queue);
Adobe `video_resize` / skill `adobe-create-social-variations` (reframe multi-plataforma); ffmpeg local:
```bash
ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v libx264 -profile:v high -crf 17 -preset slow \
  -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 320k out_youtube.mp4
# 9:16 a partir de 16:9 (centro; ajuste x pelo rosto detectado)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920" -c:a copy out_vertical.mp4
```

## Checklist de QA (rode SEMPRE antes de dizer que terminou)
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,pix_fmt,color_transfer -show_entries format=duration,bit_rate OUT
ffmpeg -i OUT -af ebur128=peak=true -f null - 2>&1 | tail -12        # loudness integrado e true peak
ffmpeg -i OUT -vf blackdetect=d=0.5:pix_th=0.1 -an -f null - 2>&1 | grep black_start   # frames pretos indevidos
ffmpeg -i OUT -af silencedetect=n=-50dB:d=2 -vn -f null - 2>&1 | grep silence_start      # buracos de áudio
```
- [ ] Resolução, fps, codec e `pix_fmt yuv420p` conforme preset
- [ ] Loudness dentro de ±1 LU do alvo; true peak ≤ −1 dBTP
- [ ] Sem frames pretos/silêncios não intencionais; começo e fim limpos
- [ ] Legendas sincronizadas (cheque 3 pontos: início, meio, fim) e dentro da safe area
- [ ] Cor: frame de referência revisado visualmente (Read em PNG)
- [ ] Arquivo de projeto editável entregue (EDL/XML/prproj/drp) + `decisoes.md` atualizado
- [ ] Nomes: `PROJETO_PLATAFORMA_v###_AAAAMMDD.mp4`
