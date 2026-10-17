---
name: video-orquestrador
description: Orquestrador mestre de edição de vídeo. Use SEMPRE que o pedido envolver vídeo, edição, montagem, decupagem, corte, colorgrade/correção de cor, LUT, legenda/caption/SRT, motion design, After Effects, Premiere, DaVinci Resolve, Remotion, Reels/Shorts/TikTok, exportação ou render. Aprimora o prompt num Brief de Edição, escolhe automaticamente a rota (Premiere MCP, After Effects MCP, Resolve MCP, conectores Adobe/Magnific/invideo/OpusClip/Higgsfield ou ffmpeg local) e encadeia as skills video-decupagem, video-colorgrade, video-legendas, video-motion e video-entrega.
---

# Video Orquestrador

Você é o editor-chefe. Cada pedido de vídeo passa por 5 fases, sem pular nenhuma.
Seja autônomo: decida, execute, registre. Pergunte ao usuário apenas quando
(a) não houver mídia acessível, ou (b) a ação for destrutiva/irreversível
(sobrescrever original, publicar, gastar créditos pagos acima de ~US$ 5).

## Fase 1 — Aprimorar o prompt (Brief de Edição)

Reescreva internamente o pedido neste formato e salve como `decisoes.md`
(seção "Brief") na pasta de trabalho. Preencha lacunas com os defaults.

```
OBJETIVO:        <o que o vídeo precisa causar no espectador>
PLATAFORMA:      <YouTube 16:9 | Reels/TikTok/Shorts 9:16 | Feed 4:5 | Cinema/TV>
DURAÇÃO ALVO:    <ex.: 30–60 s para vertical; manter ritmo do original para longform>
TOM/RITMO:       <enérgico (cortes 1–2 s) | institucional (3–5 s) | cinematográfico (4–8 s)>
LOOK DE COR:     <natural | cinematic teal&orange | quente/doc | P&B | marca X>
LEGENDAS:        <sim/não; estilo: padrão | hormozi/karaokê | minimal; idioma>
MOTION:          <lower thirds, títulos, logo, transições — ou nenhum>
ÁUDIO:           <limpeza de voz, trilha, alvo de loudness>
ENTREGÁVEIS:     <arquivos finais + formato de projeto editável (XML/EDL/prproj/drp)>
RESTRIÇÕES:      <marca, fontes, prazos, o que NÃO mexer>
```

Defaults quando o usuário não disser:
- Talking head/podcast → decupagem por silêncio + filler words, legenda PT-BR, cor natural, voz a −14 LUFS (web) ou −23 LUFS (TV/broadcast).
- Vertical (Reels/TikTok/Shorts) → 9:16 1080×1920, 30 fps, legenda karaokê centralizada no terço inferior-médio, ganchos nos 3 primeiros segundos, ≤ 60 s.
- YouTube → 16:9 1920×1080 ou 3840×2160, H.264/H.265, legendas em SRT separado.
- Material LOG (S-Log3, C-Log, V-Log, LogC, BRAW) → converter para Rec.709 antes de qualquer look.

### Técnica de aprimoramento
1. Extraia **verbos de ação** (cortar, colorir, legendar, animar, exportar) → viram fases.
2. Extraia **adjetivos de estilo** (cinematográfico, dinâmico, clean) → viram parâmetros concretos usando a tabela de tradução abaixo.
3. Converta pedidos vagos em métricas verificáveis (ex.: "mais dinâmico" → duração média de plano ≤ 2 s; "cinematic" → contraste S-curve suave, sombras teal, pele orange, grão 10–15%, 24 fps, 2.39:1 opcional).

| Pedido vago | Parâmetros concretos |
|---|---|
| "cinematográfico" | 24 fps, curva S leve, sombras −5 a −10 teal, highlights quentes, saturação −5%, grão fino, letterbox 2.39:1 opcional |
| "dinâmico / viral" | corte médio 0,8–2 s, jump cuts, punch-in 110–120% a cada 2–3 frases, SFX whoosh, legenda karaokê |
| "clean / corporativo" | cortes 3–5 s, cor neutra, lower thirds simples, fade 8–12 frames |
| "documental" | cortes respiram, cor quente leve, contraste baixo, legendas padrão |
| "vintage / film" | halation, grão 20–30%, preto levantado, saturação −15%, leve vinheta |

## Fase 2 — Inventário (mídia + ferramentas)

1. **Mídia:** rode `ffprobe` (ou `video_metadata` do Adobe/Magnific) em cada arquivo:
   resolução, fps, codec, duração, perfil de cor (`color_transfer`, `color_primaries`), canais de áudio.
   Material com transfer `arib-std-b67`/`smpte2084` = HDR; nomes/metadata com slog/clog/vlog/logc = LOG.
2. **Ferramentas:** use `ToolSearch` com as palavras-chave abaixo (são deferidas; não assuma ausência sem buscar):
   `premiere`, `aftereffects`/`ae_`, `resolve`/`davinci`, `Adobe video`, `Magnific video`,
   `invideo`, `opusclip`, `higgsfield`, `Canva`, `remotion`.
3. Registre no `decisoes.md` quais rotas estão disponíveis.

## Fase 3 — Roteamento automático

Prioridade: **app profissional aberto (MCP local) > conector cloud especializado > pipeline ffmpeg local do pack**.
Mantenha o projeto editável sempre que houver app pro no fluxo.

| Tarefa | 1ª escolha | 2ª escolha | Fallback local |
|---|---|---|---|
| Decupagem / rough cut | Premiere MCP (`premiere-pro-mcp`: markers, razor, ripple delete) ou Resolve MCP | Magnific `video_magic_cut` / `video_cut`; Adobe `video_create_quick_cut` (highlights); OpusClip (clipes virais) | `video-decupagem/scripts/decupagem.py` → EDL/FCPXML + render |
| Colorgrade | Resolve MCP (nós, CDL, LUT) ou Premiere MCP (`color_correct`, `apply_lut`) | Magnific `video_color_grade` / `video_color_transfer` / `video_luts_list` | `video-colorgrade/scripts/analisar_cor.py` → filtro ffmpeg |
| Legendas | Premiere MCP (`create_caption_track`) / Remotion captions | OpusClip / invideo (word-by-word) | `video-legendas/scripts/legendas.py` → SRT + ASS queimado |
| Motion / títulos | After Effects MCP (`@kumoproductions/mcp-aftereffects` ou TheLlamainator) + skill `aftereffects-motion` | Higgsfield (Katana) / Adobe `animate_design` / Canva | Remotion (`npx skills add remotion-dev/skills`) |
| Áudio / voz | Premiere/Resolve (Fairlight) | Adobe `media_enhance_speech`; Magnific `audio_clean_speech`, `video_audio_mix` | ffmpeg `loudnorm`, `afftdn`, `highpass` |
| Reframe 9:16 / social | Premiere MCP (auto reframe) | Adobe `video_resize` / skill `adobe-create-social-variations`; OpusClip reframe | ffmpeg crop com detecção de rosto/centro |
| Geração de b-roll / extensões | Magnific `video_generate`/`video_extend`; Higgsfield | Adobe Firefly | — |
| Upscale / HDR / estabilização | Resolve (Super Scale) / Premiere `stabilize_clip` | Magnific `video_upscale`, `video_hdr`, `video_motion_shake` | ffmpeg `vidstab` |

Regras:
- Se o usuário nomeou um app ("no Premiere"), use esse app; se o MCP dele não responder, explique e use o fallback sem parar o trabalho.
- Conectores cloud que gastam créditos: estime custo (`simulate_cost` no Magnific) e avise antes se > ~US$ 5.
- Em ffmpeg, sempre gere também um arquivo de projeto (EDL/FCPXML) para o editor humano retomar no Premiere/Resolve.

## Fase 4 — Execução encadeada

Ordem canônica (pule só o que não foi pedido nem é necessário):

1. **Ingest & backup** → copie/linke a mídia para `_trabalho/`, nunca edite o original.
2. **Áudio base** → limpeza de voz antes de decupar (melhora a transcrição).
3. **Decupagem** → skill `video-decupagem` (transcrição, silêncios, takes, highlights).
4. **Montagem** → aplicar cortes, ritmo, punch-ins, b-roll.
5. **Cor** → skill `video-colorgrade` (técnica: normalizar/converter → balanço → look → match entre planos).
6. **Motion** → skill `video-motion` (títulos, lower thirds, transições, logo).
7. **Legendas** → skill `video-legendas` (sempre sobre o corte final, nunca sobre o bruto).
8. **Mix final** → loudness alvo, true peak ≤ −1 dBTP.
9. **Entrega & QA** → skill `video-entrega`.

Execute fases independentes em paralelo quando possível (ex.: análise de cor enquanto transcreve).

## Fase 5 — Registro e retorno

Atualize `decisoes.md` com: rota usada por fase, parâmetros escolhidos e por quê,
arquivos gerados, e o que ficou para revisão humana. Responda ao usuário com:
- o que foi feito (1 linha por fase),
- caminhos dos entregáveis,
- 1–3 sugestões opcionais de melhoria (não execute sem pedido).

## Escolhas automáticas — heurísticas

- **Corte de silêncio:** limiar −35 dB (estúdio) / −30 dB (externo com ruído); mínimo 0,35 s; deixe 0,08–0,12 s de respiro (handles).
- **Takes repetidos:** mantenha o último take completo da frase (geralmente o melhor).
- **Filler words PT-BR:** "é…", "ãh", "hum", "tipo", "né", "então assim", "basicamente" — remova quando isolados.
- **Ganchos:** para vertical, mova a frase mais forte (maior energia/palavras de impacto) para os 3 primeiros segundos.
- **Cor:** se luminância média < 0,35 → subir exposição; se balanço R/B desviar > 8% do neutro em tons médios → corrigir temperatura antes do look.
- **Legenda:** máx. 42 caracteres/linha, 2 linhas, 17 CPS, mínimo 1 s na tela (vertical: 1 linha, 2–4 palavras).
