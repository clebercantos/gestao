---
name: video-decupagem
description: "Decupagem e rough cut automáticos: silêncios, fillers, retakes, melhores takes, log com timecode e EDL para Premiere/Resolve."
---

# Decupagem automática

## Rota (escolha automática)
1. **Premiere aberto + `premiere-pro-mcp`** → leia a sequência, gere os cortes com o script abaixo e aplique via ferramentas de marker/razor/ripple delete do MCP (ou importe `cortes.edl`). Mantenha a sequência original duplicada como `_ORIGINAL`.
2. **Resolve aberto + Resolve MCP** (oficial do 21.1 ou `davinci-resolve-mcp`) → importe `cortes.edl` como timeline nova ou aplique cortes pela API.
3. **Sem app aberto** → rode o script local e entregue `corte.mp4` + `cortes.edl`.
4. **Highlights / clipes curtos de um vídeo longo** → Adobe `video_create_quick_cut` (skill `adobe-edit-quick-cut`) ou OpusClip MCP (`opusclip_*`, encontra momentos virais e já reenquadra) ou Magnific `video_magic_cut`.

## Script local

```bash
python3 ~/.claude/skills/video-decupagem/scripts/decupagem.py VIDEO \
  --transcribe --lang pt --model small --render
```

| Parâmetro | Estúdio silencioso | Externo / ruído | Podcast conversa |
|---|---|---|---|
| `--thresh` | −35 | −30 | −40 |
| `--min-sil` | 0.35 | 0.5 | 0.7 |
| `--handle` | 0.08 | 0.12 | 0.15 |

Escolha os parâmetros pelo nível de ruído medido: rode
`ffmpeg -i VIDEO -af astats=metadata=1:reset=0 -f null -` e use o `RMS level` das partes sem fala + 6 dB como limiar.

Saídas: `segmentos.json`, `cortes.edl`, `decupagem.md` (log de decupagem com timecodes e texto),
`transcricao.json` (com `--transcribe`), `corte.mp4` (com `--render`).

## Log de decupagem (o que o editor humano espera)
Para material bruto com vários takes/entrevistas, produza também em `decupagem.md`:
- **Por clipe:** nome, duração, tipo de plano (aberto/médio/close/detalhe — analise frames com `ffmpeg -vf fps=1/5` e visão), qualidade técnica (foco, exposição, áudio).
- **Sonoras:** frases fortes com TC in/out e nota 1–5 (impacto, clareza, emoção).
- **B-roll:** descrição + TC + sugestão de onde cobrir.
- **Descartes:** motivo (erro, ruído, fora de foco, repetido).

## Seleção de melhores momentos (autônoma)
Pontue cada frase da transcrição: +2 frase completa com início/fim claros, +2 dado/número/promessa concreta,
+1 emoção/humor, +1 pergunta retórica (gancho), −2 frase cortada ou com retake, −1 > 25 s.
Monte o corte pela pontuação respeitando a DURAÇÃO ALVO do brief e a narrativa (gancho → contexto → valor → CTA).

## Áudio antes de decupar
Se houver ruído: Adobe `media_enhance_speech` ou Magnific `audio_clean_speech`; local:
`ffmpeg -i in -af "highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11" out.wav`.
