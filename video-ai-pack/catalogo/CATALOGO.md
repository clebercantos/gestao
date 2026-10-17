# Catálogo — as 100 melhores skills de vídeo para Claude

Gerado em 2026-10-17 cruzando **5.490** skills indexadas no skills.sh e no claudemarketplaces.com. Dessas, 1.450 eram candidatas, 697 eram relevantes depois de remover espelhos, 105 passaram pela curadoria e **100** ficaram no ranking final.

## Metodologia

| Critério | Peso | Dado usado |
|---|---|---|
| Comunidade | 30 | Instalações (skills.sh + claudemarketplaces), estrelas do repositório (×0,5 em mega-coleções) |
| Aderência | 35 | Encaixe no fluxo Premiere / After Effects / Resolve / cor / legenda / decupagem (curadoria manual) |
| Segurança | 15 | Auditorias Gen Agent Trust Hub, Socket e Snyk (−6 por *Fail*, −2 por *Warn*) |
| Tokens | 15 | Tamanho real do SKILL.md (≈ caracteres/4); ≤1k = 15 · ≤2k = 12 · ≤3,5k = 9 · ≤6k = 5 · >6k = 2 |
| Frescor | 5 | Data em que o skills.sh viu a skill pela primeira vez |

Tiers: **ouro** ≥ 75 · **prata** 65–75 · **bronze** < 65. "n/d" quer dizer que o SKILL.md fica num caminho fora do padrão (o roteador conta 2.500 t).

## O que os dados mostram

1. **Os números de instalação são inflados por packs.** As skills do HyperFrames, do inference.sh e do RunComfy somam milhões porque instalam dezenas de skills de uma vez. Os espelhos foram agrupados (coluna *esp.*), e as estrelas das mega-coleções valem metade.
2. **Cor é a maior lacuna.** Só duas skills de colorgrade passaram no corte: `resolve-color` e `color-grading-finishing`; as outras dependem de API paga. Por isso a skill própria `video-colorgrade` (análise, LUT .cube, looks) continua sendo a primeira opção.
3. **O Resolve tem o ecossistema mais completo.** `samuelgursky/davinci-resolve-mcp` traz 10 skills especializadas (sessão, edição, rough cut, tighten, cor, áudio, Fusion, delivery), todas leves (0,6k a 2,8k tokens).
4. **Premiere e After Effects ainda são nichos.** As skills existem e são boas, mas têm poucos milhares de instalações. Dependem do MCP/CEP local.
5. **Custo de tokens.** A mediana é ~1,9k tokens por skill. Seis passam de 6k (a maior tem 16k: `talking-head-recut`). Instalar as 100 custaria **~10k tokens fixos por sessão** só com as descrições, e elas disputariam o mesmo gatilho. O roteador do pack carrega no máximo 5 por pedido, dentro de 7k tokens.
6. **Skills que você já tem no claude.ai:** `anthropic-skills:motion-design` é a mesma da LottieFiles e as `gsap-*` são as oficiais da GreenSock. O roteador não duplica essas skills.
7. **Removidas na curadoria:** skills internas de manutenção (`remotion-dev/remotion/pr-name`, `add-expert`, `upload-r2`…), áudio de games (Unity, Godot, Phaser), clones de clones e skills com auditoria *Fail*.

## Ranking geral (top 30)

| # | Nota | Skill | Categoria | Tokens | Instalações | Requisito |
|---|---|---|---|---|---|---|
| 1 | 87.7 | `remotion-dev/skills/remotion-captions` | legendas | 256 | 164.8K | Remotion |
| 2 | 86.0 | `remotion-dev/skills/remotion-create` | programatico | 655 | 167.1K | Remotion |
| 3 | 86.0 | `remotion-dev/skills/remotion-render` | programatico | 156 | 168.0K | Remotion |
| 4 | 85.9 | `heygen-com/hyperframes/hyperframes-animation` | motion | 1940 | 911.2K | HyperFrames |
| 5 | 84.6 | `wyattblue/auto-editor/auto-editor-export` | decupagem | 820 | 514 | local → XML Premiere/Resolve/FCP |
| 6 | 84.3 | `remotion-dev/skills/remotion-best-practices` | programatico | 1029 | 630.0K | Remotion |
| 7 | 83.1 | `heygen-com/hyperframes/hyperframes-core` | programatico | 3137 | 839.6K | HyperFrames |
| 8 | 82.2 | `remotion-dev/skills/remotion-studio` | programatico | 381 | 130.9K | Remotion |
| 9 | 81.6 | `wyattblue/auto-editor/auto-editor` | decupagem | 1637 | 522 | local (auto-editor) |
| 10 | 81.2 | `heygen-com/hyperframes/media-use` | programatico | 2196 | 934.0K | HyperFrames |
| 11 | 80.4 | `heygen-com/hyperframes/hyperframes-keyframes` | motion | 3943 | 697.2K | HyperFrames |
| 12 | 79.6 | `openai/skills/transcribe` | legendas | 643 | 3.7K | API OpenAI |
| 13 | 79.4 | `iart-ai/motion-design-skills/after-effects` | motion | 1566 | 2.1K | After Effects |
| 14 | 78.9 | `greensock/gsap-skills/gsap-timeline` | motion | 997 | 63.6K | web/HyperFrames |
| 15 | 78.6 | `samuelgursky/davinci-resolve-mcp/resolve-session` | apps | 858 | 20 | Resolve + MCP samuelgursky |
| 16 | 77.9 | `heygen-com/hyperframes/motion-graphics` | motion | 3817 | 470.8K | HyperFrames |
| 17 | 77.6 | `affaan-m/ecc/video-editing` | decupagem | 2841 | 13.2K | local (ffmpeg) |
| 18 | 77.5 | `samuelgursky/davinci-resolve-mcp/resolve-color` | cor | 1816 | 22 | Resolve + MCP |
| 19 | 77.2 | `charlie947/motion-graphics-skills/reel-export` | entrega | 703 | 991 | local (ffmpeg) |
| 20 | 77.0 | `wyattblue/auto-editor/auto-editor-transcribe` | legendas | 1212 | 487 | local (auto-editor) |
| 21 | 76.8 | `heygen-com/hyperframes/embedded-captions` | legendas | 8403 | 420.0K | local (HyperFrames) |
| 22 | 76.8 | `heygen-com/hyperframes/hyperframes` | programatico | 5054 | 1.0M | HyperFrames |
| 23 | 76.7 | `heygen-com/hyperframes/talking-head-recut` | decupagem | 16135 | 377.5K | local (HyperFrames) |
| 24 | 76.7 | `heygen-com/hyperframes/general-video` | programatico | 5349 | 611.4K | HyperFrames |
| 25 | 76.5 | `lottiefiles/motion-design-skill/motion-design` | motion | 2988 | 17.6K | agnóstico |
| 26 | 76.4 | `sfkislev/flue/premiere` | apps | 386 | 1.8K | Premiere + Flue (ExtendScript) |
| 27 | 76.1 | `hetpatel-11/adobe_premiere_pro_mcp/premiere-pro-mcp` | apps | 1258 | 769 | Premiere + MCP hetpatel |
| 28 | 76.1 | `iart-ai/motion-design-skills/motion-art-direction` | motion | 1732 | 2.4K | agnóstico |
| 29 | 75.8 | `digitalsamba/claude-code-video-toolkit/ffmpeg` | ffmpeg | 3205 | 11.8K | local (ffmpeg) |
| 30 | 75.7 | `pluviobyte/rnskill/skill-captions` | legendas | 1175 | 175 | local |

## Todas as 100 por categoria

### Decupagem / edição (14)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 5 | 84.6 | ouro | [`wyattblue/auto-editor/auto-editor-export`](https://skills.sh/wyattblue/auto-editor/auto-editor-export) | 820 | 514 | 5.5K | 0 | local → XML Premiere/Resolve/FCP |
| 9 | 81.6 | ouro | [`wyattblue/auto-editor/auto-editor`](https://skills.sh/wyattblue/auto-editor/auto-editor) | 1637 | 522 | 5.5K | 0 | local (auto-editor) |
| 17 | 77.6 | ouro | [`affaan-m/ecc/video-editing`](https://skills.sh/affaan-m/ecc/video-editing) | 2841 | 13.2K | 281.6K | 0 | local (ffmpeg) |
| 23 | 76.7 | ouro | [`heygen-com/hyperframes/talking-head-recut`](https://skills.sh/heygen-com/hyperframes/talking-head-recut) | 16135 | 377.5K | 65.2K | 0 | local (HyperFrames) |
| 38 | 74.4 | prata | [`samuelgursky/davinci-resolve-mcp/resolve-edit`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-edit) | 2303 | 21 | 3.6K | 0 | Resolve + MCP |
| 39 | 74.3 | prata | [`samuelgursky/davinci-resolve-mcp/resolve-rough-cut`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-rough-cut) | 2804 | 19 | 3.6K | 0 | Resolve + MCP |
| 40 | 74.2 | prata | [`samuelgursky/davinci-resolve-mcp/resolve-tighten-recording`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-tighten-recording) | 2050 | 18 | 3.6K | 0 | Resolve + MCP |
| 42 | 73.9 | prata | [`browser-use/video-use/video-use`](https://skills.sh/browser-use/video-use/video-use) | 6353 | 4.6K | 29.0K | 0 | local (ffmpeg+whisper) |
| 46 | 73.4 | prata | [`wyattblue/auto-editor/auto-editor-effects`](https://skills.sh/wyattblue/auto-editor/auto-editor-effects) | 1670 | 471 | 5.5K | 0 | local (auto-editor) |
| 52 | 72.0 | prata | [`pluviobyte/rnskill/ra-local-talking-head-cut`](https://skills.sh/pluviobyte/rnskill/ra-local-talking-head-cut) | 1650 | 174 | 1.6K | 0 | local |
| 61 | 70.1 | prata | [`mirage-hq/tesseract/tesseract-video`](https://skills.sh/mirage-hq/tesseract/tesseract-video) | 2252 | 2.7K | 142 | 0 | local (Tesseract) |
| 78 | 66.7 | prata | [`heygen-com/skills/video-edit`](https://skills.sh/heygen-com/skills/video-edit) | n/d | 2.3K | 488 | 1 | local (ffmpeg) |
| 91 | 64.5 | bronze | [`openclaudia/openclaudia-skills/podcast-edit`](https://skills.sh/openclaudia/openclaudia-skills/podcast-edit) | 5723 | 248 | 715 | 0 | local (ffmpeg) |
| 97 | 61.5 | bronze | [`postplusai/postplus-skills/broll-match-engine`](https://skills.sh/postplusai/postplus-skills/broll-match-engine) | n/d | 302 | 26 | 0 | local |

### Apps profissionais (Premiere, Resolve, CapCut) (8)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 15 | 78.6 | ouro | [`samuelgursky/davinci-resolve-mcp/resolve-session`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-session) | 858 | 20 | 3.6K | 0 | Resolve + MCP samuelgursky |
| 26 | 76.4 | ouro | [`sfkislev/flue/premiere`](https://skills.sh/sfkislev/flue/premiere) | 386 | 1.8K | 97 | 0 | Premiere + Flue (ExtendScript) |
| 27 | 76.1 | ouro | [`hetpatel-11/adobe_premiere_pro_mcp/premiere-pro-mcp`](https://skills.sh/hetpatel-11/adobe_premiere_pro_mcp/premiere-pro-mcp) | 1258 | 769 | 699 | 0 | Premiere + MCP hetpatel |
| 35 | 75.0 | ouro | [`samuelgursky/davinci-resolve-mcp/resolve-media-pool`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-media-pool) | 582 | 18 | 3.6K | 0 | Resolve + MCP |
| 62 | 69.4 | prata | [`leancoderkavy/premiere-pro-mcp/edit-premiere-project`](https://skills.sh/leancoderkavy/premiere-pro-mcp/edit-premiere-project) | n/d | 12 | 384 | 0 | Premiere + premiere-pro-mcp |
| 63 | 69.2 | prata | [`lordhoell/davinci-resolve-mcp/davinci-resolve-mcp`](https://skills.sh/lordhoell/davinci-resolve-mcp/davinci-resolve-mcp) | 1554 | 11 | 12 | 0 | Resolve + MCP lordhoell |
| 64 | 69.1 | prata | [`renezander030/capcut-cli/capcut-edit`](https://skills.sh/renezander030/capcut-cli/capcut-edit) | 1310 | 530 | 901 | 0 | CapCut/JianYing |
| 74 | 67.7 | prata | [`damionrashford/media-os/workflow-editorial-interchange`](https://skills.sh/damionrashford/media-os/workflow-editorial-interchange) | 1365 | 11 | 21 | 0 | local (EDL/XML/AAF) |

### Cor (2)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 18 | 77.5 | ouro | [`samuelgursky/davinci-resolve-mcp/resolve-color`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-color) | 1816 | 22 | 3.6K | 0 | Resolve + MCP |
| 60 | 70.2 | prata | [`calesthio/generative-media-skills/color-grading-finishing`](https://skills.sh/calesthio/generative-media-skills/color-grading-finishing) | n/d | 202 | 203 | 0 | agnóstico |

### Legendas / transcrição (12)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 1 | 87.7 | ouro | [`remotion-dev/skills/remotion-captions`](https://skills.sh/remotion-dev/skills/remotion-captions) | 256 | 164.8K | 5.2K | 0 | Remotion |
| 12 | 79.6 | ouro | [`openai/skills/transcribe`](https://skills.sh/openai/skills/transcribe) | 643 | 3.7K | 28.1K | 0 | API OpenAI |
| 20 | 77.0 | ouro | [`wyattblue/auto-editor/auto-editor-transcribe`](https://skills.sh/wyattblue/auto-editor/auto-editor-transcribe) | 1212 | 487 | 5.5K | 0 | local (auto-editor) |
| 21 | 76.8 | ouro | [`heygen-com/hyperframes/embedded-captions`](https://skills.sh/heygen-com/hyperframes/embedded-captions) | 8403 | 420.0K | 65.2K | 0 | local (HyperFrames) |
| 30 | 75.7 | ouro | [`pluviobyte/rnskill/skill-captions`](https://skills.sh/pluviobyte/rnskill/skill-captions) | 1175 | 175 | 1.6K | 0 | local |
| 36 | 75.0 | ouro | [`pluviobyte/rnskill/ra-audio-to-subtitles`](https://skills.sh/pluviobyte/rnskill/ra-audio-to-subtitles) | 980 | 179 | 1.6K | 0 | local |
| 65 | 69.1 | prata | [`sugarforever/01coder-agent-skills/subtitle-correction`](https://skills.sh/sugarforever/01coder-agent-skills/subtitle-correction) | 2177 | 534 | 137 | 0 | agnóstico |
| 68 | 68.9 | prata | [`elevenlabs/skills/speech-to-text`](https://skills.sh/elevenlabs/skills/speech-to-text) | 2437 | 11.7K | 491 | 2 | API ElevenLabs |
| 72 | 68.4 | prata | [`iart-ai/tiktok-video-skills/caption-animation`](https://skills.sh/iart-ai/tiktok-video-skills/caption-animation) | 2335 | 1.5K | 14 | 0 | local |
| 80 | 66.3 | prata | [`josiahsiegel/claude-plugin-marketplace/ffmpeg-captions-subtitles`](https://skills.sh/josiahsiegel/claude-plugin-marketplace/ffmpeg-captions-subtitles) | n/d | 442 | 59 | 0 | local (ffmpeg) |
| 98 | 61.5 | bronze | [`damionrashford/media-os/ffmpeg-subtitles`](https://skills.sh/damionrashford/media-os/ffmpeg-subtitles) | 2692 | 14 | 21 | 0 | local (ffmpeg) |
| 99 | 61.3 | bronze | [`kwindla/skill-caption-clip/caption-clip`](https://skills.sh/kwindla/skill-caption-clip/caption-clip) | 872 | 62 | 2 | 0 | Deepgram + ffmpeg |

### Motion design / After Effects (17)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 4 | 85.9 | ouro | [`heygen-com/hyperframes/hyperframes-animation`](https://skills.sh/heygen-com/hyperframes/hyperframes-animation) | 1940 | 911.2K | 65.2K | 0 | HyperFrames |
| 11 | 80.4 | ouro | [`heygen-com/hyperframes/hyperframes-keyframes`](https://skills.sh/heygen-com/hyperframes/hyperframes-keyframes) | 3943 | 697.2K | 65.2K | 0 | HyperFrames |
| 13 | 79.4 | ouro | [`iart-ai/motion-design-skills/after-effects`](https://skills.sh/iart-ai/motion-design-skills/after-effects) | 1566 | 2.1K | 133 | 0 | After Effects |
| 14 | 78.9 | ouro | [`greensock/gsap-skills/gsap-timeline`](https://skills.sh/greensock/gsap-skills/gsap-timeline) | 997 | 63.6K | 16.5K | 0 | web/HyperFrames |
| 16 | 77.9 | ouro | [`heygen-com/hyperframes/motion-graphics`](https://skills.sh/heygen-com/hyperframes/motion-graphics) | 3817 | 470.8K | 65.2K | 0 | HyperFrames |
| 25 | 76.5 | ouro | [`lottiefiles/motion-design-skill/motion-design`](https://skills.sh/lottiefiles/motion-design-skill/motion-design) | 2988 | 17.6K | 2.3K | 0 | agnóstico |
| 28 | 76.1 | ouro | [`iart-ai/motion-design-skills/motion-art-direction`](https://skills.sh/iart-ai/motion-design-skills/motion-art-direction) | 1732 | 2.4K | 133 | 0 | agnóstico |
| 32 | 75.6 | ouro | [`emilkowalski/skills/animation-vocabulary`](https://skills.sh/emilkowalski/skills/animation-vocabulary) | 3177 | 215.1K | 46.7K | 0 | agnóstico |
| 33 | 75.1 | ouro | [`samuelgursky/davinci-resolve-mcp/resolve-fusion`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-fusion) | 611 | 19 | 3.6K | 0 | Resolve + MCP |
| 34 | 75.1 | ouro | [`diffusionstudio/lottie/text-to-lottie`](https://skills.sh/diffusionstudio/lottie/text-to-lottie) | 2366 | 10.3K | 5.6K | 0 | local (Lottie) |
| 47 | 73.4 | prata | [`lobzyjay/motion-design-with-claude-and-codex/motion-design`](https://skills.sh/lobzyjay/motion-design-with-claude-and-codex/motion-design) | 612 | 234 | 25 | 0 | AE/Blender (opcional MCP) |
| 76 | 66.8 | prata | [`dylantarre/animation-principles/video-motion-graphics`](https://skills.sh/dylantarre/animation-principles/video-motion-graphics) | n/d | 2.2K | 108 | 0 | AE/Premiere |
| 84 | 65.7 | prata | [`dylantarre/animation-principles/after-effects`](https://skills.sh/dylantarre/animation-principles/after-effects) | n/d | 842 | 108 | 0 | After Effects |
| 87 | 64.9 | bronze | [`ncklrs/startup-os-skills/motion-designer`](https://skills.sh/ncklrs/startup-os-skills/motion-designer) | 2190 | 544 | 52 | 0 | agnóstico |
| 88 | 64.8 | bronze | [`aedev-tools/adobe-agent-skills/after-effects`](https://skills.sh/aedev-tools/adobe-agent-skills/after-effects) | 4997 | 584 | 111 | 1 | After Effects (ExtendScript) |
| 89 | 64.6 | bronze | [`barty-bart/motion-graphics/motion-broll`](https://skills.sh/barty-bart/motion-graphics/motion-broll) | 2136 | 1.0K | 700 | 0 | local |
| 94 | 62.8 | bronze | [`dylantarre/animation-principles/lottie-bodymovin`](https://skills.sh/dylantarre/animation-principles/lottie-bodymovin) | n/d | 1.5K | 108 | 2 | AE → Lottie |

### Vídeo programático (Remotion / HyperFrames) (14)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 2 | 86.0 | ouro | [`remotion-dev/skills/remotion-create`](https://skills.sh/remotion-dev/skills/remotion-create) | 655 | 167.1K | 5.2K | 0 | Remotion |
| 3 | 86.0 | ouro | [`remotion-dev/skills/remotion-render`](https://skills.sh/remotion-dev/skills/remotion-render) | 156 | 168.0K | 5.2K | 0 | Remotion |
| 6 | 84.3 | ouro | [`remotion-dev/skills/remotion-best-practices`](https://skills.sh/remotion-dev/skills/remotion-best-practices) | 1029 | 630.0K | 5.2K | 1 | Remotion |
| 7 | 83.1 | ouro | [`heygen-com/hyperframes/hyperframes-core`](https://skills.sh/heygen-com/hyperframes/hyperframes-core) | 3137 | 839.6K | 65.2K | 0 | HyperFrames |
| 8 | 82.2 | ouro | [`remotion-dev/skills/remotion-studio`](https://skills.sh/remotion-dev/skills/remotion-studio) | 381 | 130.9K | 5.2K | 0 | Remotion |
| 10 | 81.2 | ouro | [`heygen-com/hyperframes/media-use`](https://skills.sh/heygen-com/hyperframes/media-use) | 2196 | 934.0K | 65.2K | 0 | HyperFrames |
| 22 | 76.8 | ouro | [`heygen-com/hyperframes/hyperframes`](https://skills.sh/heygen-com/hyperframes/hyperframes) | 5054 | 1.0M | 65.2K | 0 | HyperFrames |
| 24 | 76.7 | ouro | [`heygen-com/hyperframes/general-video`](https://skills.sh/heygen-com/hyperframes/general-video) | 5349 | 611.4K | 65.2K | 0 | HyperFrames |
| 41 | 74.2 | prata | [`remotion-dev/skills/remotion-markup`](https://skills.sh/remotion-dev/skills/remotion-markup) | 4318 | 161.1K | 5.2K | 0 | Remotion |
| 50 | 72.4 | prata | [`heygen-com/hyperframes/music-to-video`](https://skills.sh/heygen-com/hyperframes/music-to-video) | 4617 | 389.4K | 65.2K | 0 | HyperFrames |
| 53 | 71.3 | prata | [`vincentwei1021/video-shotcraft/video-shotcraft`](https://skills.sh/vincentwei1021/video-shotcraft/video-shotcraft) | 2560 | 4.0K | 12.2K | 0 | local |
| 58 | 70.4 | prata | [`heygen-com/hyperframes/hyperframes-cli`](https://skills.sh/heygen-com/hyperframes/hyperframes-cli) | 6331 | 1.1M | 65.2K | 0 | HyperFrames |
| 66 | 69.0 | prata | [`heygen-com/hyperframes/website-to-hyperframes`](https://skills.sh/heygen-com/hyperframes/website-to-hyperframes) | n/d | 89.3K | 65.2K | 0 | HyperFrames |
| 73 | 68.0 | prata | [`av/remotion-bits/remotion-bits`](https://skills.sh/av/remotion-bits/remotion-bits) | 1759 | 361 | 491 | 0 | Remotion |

### Áudio (8)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 37 | 74.7 | prata | [`elevenlabs/skills/sound-effects`](https://skills.sh/elevenlabs/skills/sound-effects) | 830 | 10.0K | 491 | 0 | API ElevenLabs |
| 43 | 73.9 | prata | [`samuelgursky/davinci-resolve-mcp/resolve-audio`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-audio) | 1471 | 21 | 3.6K | 0 | Resolve + MCP |
| 45 | 73.7 | prata | [`heygen-com/hyperframes/hyperframes-audio`](https://skills.sh/heygen-com/hyperframes/hyperframes-audio) | 6418 | 593.9K | 65.2K | 0 | HyperFrames |
| 67 | 69.0 | prata | [`elevenlabs/skills/music`](https://skills.sh/elevenlabs/skills/music) | 3283 | 10.6K | 491 | 1 | API ElevenLabs |
| 75 | 67.4 | prata | [`elevenlabs/skills/text-to-speech`](https://skills.sh/elevenlabs/skills/text-to-speech) | 2505 | 15.2K | 491 | 0 | API ElevenLabs |
| 81 | 66.3 | prata | [`digitalsamba/claude-code-video-toolkit/elevenlabs`](https://skills.sh/digitalsamba/claude-code-video-toolkit/elevenlabs) | 3449 | 1.1K | 2.3K | 0 | API ElevenLabs |
| 90 | 64.6 | bronze | [`noizai/skills/sound-fx`](https://skills.sh/noizai/skills/sound-fx) | 1168 | 356 | 529 | 0 | API Noiz |
| 92 | 64.1 | bronze | [`damionrashford/media-os/workflow-podcast-pipeline`](https://skills.sh/damionrashford/media-os/workflow-podcast-pipeline) | 1394 | 10 | 21 | 0 | local (ffmpeg) |

### Entrega / exportação (4)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 19 | 77.2 | ouro | [`charlie947/motion-graphics-skills/reel-export`](https://skills.sh/charlie947/motion-graphics-skills/reel-export) | 703 | 991 | 299 | 0 | local (ffmpeg) |
| 31 | 75.6 | ouro | [`samuelgursky/davinci-resolve-mcp/resolve-delivery`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-delivery) | 1923 | 20 | 3.6K | 0 | Resolve + MCP |
| 69 | 68.8 | prata | [`inference-sh/skills/video-ad-specs`](https://skills.sh/inference-sh/skills/video-ad-specs) | n/d | 280.7K | 769 | 6 | agnóstico (specs) |
| 82 | 66.0 | prata | [`damionrashford/media-os/workflow-vod-post-production`](https://skills.sh/damionrashford/media-os/workflow-vod-post-production) | 1499 | 11 | 21 | 0 | local (ffmpeg) |

### Social / formatos curtos (7)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 48 | 73.3 | prata | [`jakeschincariol/youtube-agent-skill/yt-shorts`](https://skills.sh/jakeschincariol/youtube-agent-skill/yt-shorts) | 316 | 204 | 1.5K | 0 | agnóstico |
| 49 | 72.9 | prata | [`jaycheng1103/chatgpt-video-editing-skills/chatgpt-short-video-editor`](https://skills.sh/jaycheng1103/chatgpt-video-editing-skills/chatgpt-short-video-editor) | 618 | 341 | 590 | 0 | local |
| 54 | 71.2 | prata | [`social-media-skills/skills/captions-and-clipping`](https://skills.sh/social-media-skills/skills/captions-and-clipping) | 1133 | 588 | 162 | 0 | agnóstico |
| 57 | 70.5 | prata | [`charlie947/social-media-skills/youtube-thumbnail`](https://skills.sh/charlie947/social-media-skills/youtube-thumbnail) | 1793 | 1.4K | 4.2K | 0 | geração de imagem |
| 59 | 70.4 | prata | [`coreyhaines31/marketingskills/video`](https://skills.sh/coreyhaines31/marketingskills/video) | 3535 | 81.4K | 55.1K | 0 | agnóstico |
| 77 | 66.8 | prata | [`iart-ai/tiktok-video-skills/short-form-video`](https://skills.sh/iart-ai/tiktok-video-skills/short-form-video) | 2624 | 1.7K | 14 | 0 | agnóstico |
| 100 | 60.9 | bronze | [`kostja94/marketing-skills/youtube-seo`](https://skills.sh/kostja94/marketing-skills/youtube-seo) | n/d | 3.3K | 1.0K | 0 | agnóstico |

### Análise de vídeo (6)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 44 | 73.9 | prata | [`bradautomates/claude-video/watch`](https://skills.sh/bradautomates/claude-video/watch) | 4164 | 10.7K | 18.7K | 0 | local (yt-dlp+ffmpeg+whisper) |
| 51 | 72.2 | prata | [`samuelgursky/davinci-resolve-mcp/resolve-media-analysis`](https://skills.sh/samuelgursky/davinci-resolve-mcp/resolve-media-analysis) | 1026 | 21 | 3.6K | 0 | Resolve + MCP |
| 55 | 71.2 | prata | [`steipete/agent-scripts/video-transcript-downloader`](https://skills.sh/steipete/agent-scripts/video-transcript-downloader) | 525 | 1.0K | 7.4K | 0 | local (yt-dlp) |
| 70 | 68.5 | prata | [`heygen-com/skills/video-understand`](https://skills.sh/heygen-com/skills/video-understand) | n/d | 2.3K | 488 | 2 | local (ffmpeg+whisper) |
| 71 | 68.5 | prata | [`bsisduck/video-analyzer-skill/analyzing-video`](https://skills.sh/bsisduck/video-analyzer-skill/analyzing-video) | 1524 | 253 | 42 | 0 | local |
| 79 | 66.6 | prata | [`openclaw/openclaw/video-frames`](https://skills.sh/openclaw/openclaw/video-frames) | n/d | 3.6K | 392.2K | 0 | local (ffmpeg) |

### FFmpeg (base) (4)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 29 | 75.8 | ouro | [`digitalsamba/claude-code-video-toolkit/ffmpeg`](https://skills.sh/digitalsamba/claude-code-video-toolkit/ffmpeg) | 3205 | 11.8K | 2.3K | 1 | local (ffmpeg) |
| 56 | 70.6 | prata | [`mrgoonie/claudekit-skills/media-processing`](https://skills.sh/mrgoonie/claudekit-skills/media-processing) | 2216 | 544 | 2.2K | 0 | local (ffmpeg) |
| 83 | 65.8 | prata | [`digitalsamba/claude-code-video-toolkit/moviepy`](https://skills.sh/digitalsamba/claude-code-video-toolkit/moviepy) | 3136 | 914 | 2.3K | 0 | local (moviepy) |
| 95 | 62.5 | bronze | [`kajisho5/ffmpeg-skill/ffmpeg-skill`](https://skills.sh/kajisho5/ffmpeg-skill/ffmpeg-skill) | 7170 | 182 | 2.0K | 0 | local (ffmpeg) |

### Geração por IA (b-roll) (4)

| # | Nota | Tier | Skill | Tokens | Inst. | ★ repo | esp. | Requisito |
|---|---|---|---|---|---|---|---|---|
| 85 | 65.4 | prata | [`inference-sh/skills/ai-video-generation`](https://skills.sh/inference-sh/skills/ai-video-generation) | n/d | 4.9M | 769 | 11 | API paga inference.sh |
| 86 | 65.2 | prata | [`higgsfield-ai/skills/higgsfield-generate`](https://skills.sh/higgsfield-ai/skills/higgsfield-generate) | 5870 | 131.5K | 1.3K | 0 | API paga Higgsfield |
| 93 | 63.9 | bronze | [`affaan-m/ecc/fal-ai-media`](https://skills.sh/affaan-m/ecc/fal-ai-media) | 1786 | 9.3K | 281.6K | 0 | API paga fal.ai |
| 96 | 61.6 | bronze | [`cnemri/google-genai-skills/veo-use`](https://skills.sh/cnemri/google-genai-skills/veo-use) | 536 | 193 | 127 | 0 | API Google (Veo) |

## Fontes

- skills.sh: API de busca, páginas de skill (instalações, estrelas, auditorias, first seen)
- claudemarketplaces.com: categorias *video-editing* e *ai-media*
- raw.githubusercontent.com: SKILL.md de cada skill, para medir tokens

Para regerar os dados, rode `pack.py list` / `pack.py stats`. O catálogo completo, com notas parciais, está em `skills.json`.
