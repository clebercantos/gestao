# Skills — referência completa

Atualizado em 2026-10-19 · fonte: documentação do repositório (sem varredura local).
Use para responder "qual skill faz X?" e para não recriar o que já existe. Busque com Ctrl+F / grep.

## Skills do Video AI Pack (sempre instaladas)

| Skill | Para quê |
|---|---|
| `video-audio` | Áudio de vídeo: limpeza de voz/ruído, loudness por plataforma (web -14, TV -23, podcast -16 LUFS), trilha com ducking e mix final. |
| `video-colorgrade` | Correção de cor e colorgrade: exposição, balanço de branco, LOG→Rec.709, looks e LUT .cube para Premiere/Resolve. |
| `video-decupagem` | Decupagem e rough cut automáticos: silêncios, fillers, retakes, melhores takes, log com timecode e EDL para Premiere/Resolve. |
| `video-entrega` | Exportação por plataforma e checklist de QA final de vídeo (codec, loudness, legendas, projeto editável). |
| `video-legendas` | Legendas automáticas: transcrição, SRT/VTT profissional, estilos karaokê/Hormozi/minimal, glossário e burn-in. |
| `video-motion` | Motion design: títulos, lower thirds, logo e transições via After Effects MCP, Remotion ou Higgsfield. |
| `video-orquestrador` | Orquestrador de edição de vídeo — use em qualquer pedido de vídeo, decupagem, corte, colorgrade/LUT, legenda, motion/After Effects, Premiere, DaVinci Resolve, Remotion, Reels/Shorts ou exportação. Ap… |

## Skills da conta Claude (claude.ai e Claude Code)

Disponíveis nas conversas do claude.ai e nas sessões Claude Code ligadas à conta.

- **adobe-for-creativity (plugin):** `adobe`, `adobe-anydocx`, `adobe-anyexcel`, `adobe-anypdf`, `adobe-anypptx`, `adobe-batch-edit-photos`, `adobe-create-pdfs-from-data`, `adobe-create-social-variations`, `adobe-design-from-template`, `adobe-design-to-pdf`, `adobe-document-review`, `adobe-edit-quick-cut`, `adobe-fonts`, `adobe-resize-photos-and-videos`, `adobe-retouch-portraits`
- **anthropic-skills:** `motion-design`, `gsap-core`, `gsap-timeline`, `gsap-scrolltrigger`, `gsap-react`, `gsap-plugins`, `gsap-performance`, `gsap-frameworks`, `gsap-utils`, `genjutsu`, `design-dna`, `threejs-animation`, `threejs-fundamentals`, `threejs-geometry`, `threejs-interaction`, `threejs-lighting`, `threejs-loaders`, `threejs-materials`, `threejs-postprocessing`, `threejs-shaders`, `threejs-textures`, `docs`, `docx`, `pdf`, `pptx`, `xlsx`, `google-workspace`, `deep-research`, `computer-use`, `chrome-browser`, `built-in-browser`, `skill-creator`, `import-memory`, `morning`
- **Claude Code (embutidas):** `dataviz`, `artifact-design`, `artifact-diagramming`, `artifact-capabilities`, `update-config`, `keybindings-help`, `code-review`, `simplify`, `security-review`, `fewer-permission-prompts`, `loop`, `claude-api`, `run`, `plugin-authoring`, `workflow-authoring`, `session-start-hook`, `init`

## Top-100 da comunidade (cofre do roteador, 100 skills)

Carregadas sob demanda pelo hook (2–5 por pedido). Nota, tokens e requisitos: `video-ai-pack/catalogo/CATALOGO.md`.

- **legendas:** `remotion-dev/remotion-captions` 87.7, `openai/transcribe` 79.6, `wyattblue/auto-editor-transcribe` 77.0, `heygen-com/embedded-captions` 76.8, `pluviobyte/skill-captions` 75.7, `pluviobyte/ra-audio-to-subtitles` 75.0, `sugarforever/subtitle-correction` 69.1, `elevenlabs/speech-to-text` 68.9, `iart-ai/caption-animation` 68.4, `josiahsiegel/ffmpeg-captions-subtitles` 66.3, `damionrashford/ffmpeg-subtitles` 61.5, `kwindla/caption-clip` 61.3
- **programatico:** `remotion-dev/remotion-create` 86.0, `remotion-dev/remotion-render` 86.0, `remotion-dev/remotion-best-practices` 84.3, `heygen-com/hyperframes-core` 83.1, `remotion-dev/remotion-studio` 82.2, `heygen-com/media-use` 81.2, `heygen-com/hyperframes` 76.8, `heygen-com/general-video` 76.7, `remotion-dev/remotion-markup` 74.2, `heygen-com/music-to-video` 72.4, `vincentwei1021/video-shotcraft` 71.3, `heygen-com/hyperframes-cli` 70.4, `heygen-com/website-to-hyperframes` 69.0, `av/remotion-bits` 68.0
- **motion:** `heygen-com/hyperframes-animation` 85.9, `heygen-com/hyperframes-keyframes` 80.4, `iart-ai/after-effects` 79.4, `greensock/gsap-timeline` 78.9, `heygen-com/motion-graphics` 77.9, `lottiefiles/motion-design` 76.5, `iart-ai/motion-art-direction` 76.1, `emilkowalski/animation-vocabulary` 75.6, `samuelgursky/resolve-fusion` 75.1, `diffusionstudio/text-to-lottie` 75.1, `lobzyjay/motion-design` 73.4, `dylantarre/video-motion-graphics` 66.8, `dylantarre/after-effects` 65.7, `ncklrs/motion-designer` 64.9, `aedev-tools/after-effects` 64.8, `barty-bart/motion-broll` 64.6, `dylantarre/lottie-bodymovin` 62.8
- **decupagem:** `wyattblue/auto-editor-export` 84.6, `wyattblue/auto-editor` 81.6, `affaan-m/video-editing` 77.6, `heygen-com/talking-head-recut` 76.7, `samuelgursky/resolve-edit` 74.4, `samuelgursky/resolve-rough-cut` 74.3, `samuelgursky/resolve-tighten-recording` 74.2, `browser-use/video-use` 73.9, `wyattblue/auto-editor-effects` 73.4, `pluviobyte/ra-local-talking-head-cut` 72.0, `mirage-hq/tesseract-video` 70.1, `heygen-com/video-edit` 66.7, `openclaudia/podcast-edit` 64.5, `postplusai/broll-match-engine` 61.5
- **apps:** `samuelgursky/resolve-session` 78.6, `sfkislev/premiere` 76.4, `hetpatel-11/premiere-pro-mcp` 76.1, `samuelgursky/resolve-media-pool` 75.0, `leancoderkavy/edit-premiere-project` 69.4, `lordhoell/davinci-resolve-mcp` 69.2, `renezander030/capcut-edit` 69.1, `damionrashford/workflow-editorial-interchange` 67.7
- **cor:** `samuelgursky/resolve-color` 77.5, `calesthio/color-grading-finishing` 70.2
- **entrega:** `charlie947/reel-export` 77.2, `samuelgursky/resolve-delivery` 75.6, `inference-sh/video-ad-specs` 68.8, `damionrashford/workflow-vod-post-production` 66.0
- **ffmpeg:** `digitalsamba/ffmpeg` 75.8, `mrgoonie/media-processing` 70.6, `digitalsamba/moviepy` 65.8, `kajisho5/ffmpeg-skill` 62.5
- **audio:** `elevenlabs/sound-effects` 74.7, `samuelgursky/resolve-audio` 73.9, `heygen-com/hyperframes-audio` 73.7, `elevenlabs/music` 69.0, `elevenlabs/text-to-speech` 67.4, `digitalsamba/elevenlabs` 66.3, `noizai/sound-fx` 64.6, `damionrashford/workflow-podcast-pipeline` 64.1
- **analise:** `bradautomates/watch` 73.9, `samuelgursky/resolve-media-analysis` 72.2, `steipete/video-transcript-downloader` 71.2, `heygen-com/video-understand` 68.5, `bsisduck/analyzing-video` 68.5, `openclaw/video-frames` 66.6
- **social:** `jakeschincariol/yt-shorts` 73.3, `jaycheng1103/chatgpt-short-video-editor` 72.9, `social-media-skills/captions-and-clipping` 71.2, `charlie947/youtube-thumbnail` 70.5, `coreyhaines31/video` 70.4, `iart-ai/short-form-video` 66.8, `kostja94/youtube-seo` 60.9
- **geracao:** `inference-sh/ai-video-generation` 65.4, `higgsfield-ai/higgsfield-generate` 65.2, `affaan-m/fal-ai-media` 63.9, `cnemri/veo-use` 61.6

## Adotadas automaticamente pelo agente (0)

- nenhuma ainda
