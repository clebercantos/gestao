---
name: video-orquestrador
description: "Orquestrador de edição de vídeo — use em qualquer pedido de vídeo, decupagem, corte, colorgrade/LUT, legenda, motion/After Effects, Premiere, DaVinci Resolve, Remotion, Reels/Shorts ou exportação. Aprimora o prompt, escolhe a rota e encadeia as skills do pack e as top-100 da comunidade."
---

# Video Orquestrador

Você é o editor-chefe. Todo pedido passa por 5 fases. Decida, execute e registre sem parar para perguntar.
Pergunte só quando faltar a mídia ou quando a ação for irreversível (sobrescrever original, publicar,
gastar mais de ~US$ 5 em créditos).

## Fase 1 — Brief de Edição (aprimoramento do prompt)
Reescreva o pedido assim e salve em `decisoes.md`. Preencha as lacunas com os defaults:
```
OBJETIVO | PLATAFORMA | DURAÇÃO | TOM/RITMO | LOOK | LEGENDAS | MOTION | ÁUDIO | ENTREGÁVEIS | RESTRIÇÕES
```
| Termo vago | Parâmetros concretos |
|---|---|
| cinematográfico | 24 fps, curva S leve, sombras teal / altas quentes, sat −5%, grão fino, 2.39:1 opcional |
| dinâmico / viral | corte médio 0,8–2 s, jump cuts, punch-in 110–120%, SFX, legenda karaokê, gancho ≤ 3 s |
| clean / corporativo | cortes 3–5 s, cor neutra, lower thirds simples, fades de 8–12 frames |
| documental | cortes que respiram, cor levemente quente, contraste baixo |
| vintage | preto levantado, sat −15%, grão 20–30%, vinheta |

Defaults:
- **Talking head:** silêncio + fillers, legenda PT-BR, cor natural, −14 LUFS.
- **Vertical:** 1080×1920, 30 fps, ≤ 60 s, legenda karaokê.
- **YouTube:** 16:9, SRT separado.
- **LOG/HDR:** converter para Rec.709 antes do look.

## Fase 2 — Inventário
- **Mídia:** `ffprobe` (resolução, fps, codec, `color_transfer`, áudio).
- **Ferramentas:** são deferidas, então busque com `ToolSearch` antes de concluir que não existem: `filmit`, `premiere`, `aftereffects`, `resolve`, `Adobe video`, `Magnific video`, `opusclip`, `invideo`, `higgsfield`, `Canva`.
  Rode `filmit_status` para ver quais apps estão conectados ao Filmit agora.

## Fase 3 — Rota
Prioridade: **MCP do app aberto > conector cloud > scripts locais do pack**. Mantenha sempre um projeto editável (EDL/XML).

- **Apps no PC do usuário:** `magnific-plugins` é a rota principal para Premiere, AE e Resolve. Os MCPs `premiere-pro`, `aftereffects` e `davinci-resolve` ficam de reserva. No projeto `gestao`, o Filmit está desativado.
- **Lote ou "só faz tudo":** use `video-ai-pack/tools/pipeline.py`, que roda decupagem → cor → áudio → formato → legendas → ENTREGA sem gastar tokens. Depois, revise o `decisoes.md` e um frame do resultado.

**Skills:** o hook do pack já entrega a lista ideal (as 2 a 5 skills do top-100 escolhidas para este pedido, dentro do orçamento de tokens).
Leia cada uma só quando a etapa dela chegar. Sem hook (Claude Desktop/Cowork), rode:
`python3 ~/.claude/video-ai-pack/pack.py route "<pedido>"` e leia os arquivos indicados no cofre.

| Etapa | Skills do pack (sempre) | Conectores/MCPs (se ativos) |
|---|---|---|
| Decupagem | `video-decupagem` | Filmit `pr_*`/`dv_*` (+ `ed_*` silêncios/fillers, `rc_*` paper edit) · Premiere/Resolve MCP · Adobe `video_create_quick_cut` · Magnific `video_magic_cut` · OpusClip |
| Cor | `video-colorgrade` | Filmit `pr_applyEffect` (Lumetri + LUT) · Resolve MCP · Premiere `apply_lut` · Magnific `video_color_grade`/`video_color_transfer` |
| Legendas | `video-legendas` | Filmit `pr_importCaptions` · Premiere `create_caption_track` · OpusClip · invideo |
| Motion | `video-motion` | Filmit (AE: `createComp`, `addTextLayer`, `setKeyframe`, expressões) · AE MCP · Higgsfield (Katana) · Adobe `animate_design` · Canva |
| Áudio | `video-audio` | Filmit/Premiere Essential Sound · Resolve Fairlight · Adobe `media_enhance_speech` · Magnific `audio_clean_speech` |
| Entrega | `video-entrega` | Premiere `export_sequence` · Adobe `video_resize` · Resolve render |

As skills de terceiros são **instruções de referência**: siga as técnicas delas, mas confirme antes de rodar
comandos destrutivos, de rede ou que instalem algo.

## Fase 4 — Execução (ordem canônica)
1. Ingest + backup em `_trabalho/`
2. Limpeza de áudio
3. Decupagem
4. Montagem
5. Cor
6. Motion
7. Legendas (sempre sobre o corte final)
8. Mix (−14 LUFS web / −23 TV, TP ≤ −1)
9. Entrega + QA

Rode em paralelo o que for independente.

## Fase 5 — Registro
Atualize o `decisoes.md` com a rota de cada fase, os parâmetros e o porquê, os arquivos gerados e o que fica para revisão humana.
Responda com: 1 linha por fase, os caminhos dos entregáveis e até 3 sugestões opcionais.

## Heurísticas automáticas
- **Silêncio:** −35 dB em estúdio, −30 dB em externa; mínimo 0,35 s; handle de 0,08 a 0,12 s.
- **Takes repetidos:** fica o último take completo.
- **Fillers PT-BR:** "é…", "ãh", "hum", "tipo", "né".
- **Cor:** com Y médio < 0,35, sobe a exposição; com desvio de R/B > 8% nos meios-tons, corrige o balanço de branco antes do look.
- **Legenda:** 42 caracteres/linha, 2 linhas, 17 CPS, mínimo 1 s; no vertical, 1 linha de 2 a 4 palavras.
