# Skills — referência completa

Atualizado em 2026-10-17 · fonte: documentação do repositório (sem varredura local).
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

Carregadas sob demanda pelo hook (2–5 por pedido). Detalhes e metodologia: `video-ai-pack/catalogo/CATALOGO.md`.

| # | Nota | Skill | Categoria | Tokens | Requisito |
|---|---|---|---|---|---|
| 1 | 87.7 | `remotion-dev/skills/remotion-captions` | legendas | 256 | Remotion |
| 2 | 86.0 | `remotion-dev/skills/remotion-create` | programatico | 655 | Remotion |
| 3 | 86.0 | `remotion-dev/skills/remotion-render` | programatico | 156 | Remotion |
| 4 | 85.9 | `heygen-com/hyperframes/hyperframes-animation` | motion | 1940 | HyperFrames |
| 5 | 84.6 | `wyattblue/auto-editor/auto-editor-export` | decupagem | 820 | local → XML Premiere/Resolve/FCP |
| 6 | 84.3 | `remotion-dev/skills/remotion-best-practices` | programatico | 1029 | Remotion |
| 7 | 83.1 | `heygen-com/hyperframes/hyperframes-core` | programatico | 3137 | HyperFrames |
| 8 | 82.2 | `remotion-dev/skills/remotion-studio` | programatico | 381 | Remotion |
| 9 | 81.6 | `wyattblue/auto-editor/auto-editor` | decupagem | 1637 | local (auto-editor) |
| 10 | 81.2 | `heygen-com/hyperframes/media-use` | programatico | 2196 | HyperFrames |
| 11 | 80.4 | `heygen-com/hyperframes/hyperframes-keyframes` | motion | 3943 | HyperFrames |
| 12 | 79.6 | `openai/skills/transcribe` | legendas | 643 | API OpenAI |
| 13 | 79.4 | `iart-ai/motion-design-skills/after-effects` | motion | 1566 | After Effects |
| 14 | 78.9 | `greensock/gsap-skills/gsap-timeline` | motion | 997 | web/HyperFrames |
| 15 | 78.6 | `samuelgursky/davinci-resolve-mcp/resolve-session` | apps | 858 | Resolve + MCP samuelgursky |
| 16 | 77.9 | `heygen-com/hyperframes/motion-graphics` | motion | 3817 | HyperFrames |
| 17 | 77.6 | `affaan-m/ecc/video-editing` | decupagem | 2841 | local (ffmpeg) |
| 18 | 77.5 | `samuelgursky/davinci-resolve-mcp/resolve-color` | cor | 1816 | Resolve + MCP |
| 19 | 77.2 | `charlie947/motion-graphics-skills/reel-export` | entrega | 703 | local (ffmpeg) |
| 20 | 77.0 | `wyattblue/auto-editor/auto-editor-transcribe` | legendas | 1212 | local (auto-editor) |
| 21 | 76.8 | `heygen-com/hyperframes/embedded-captions` | legendas | 8403 | local (HyperFrames) |
| 22 | 76.8 | `heygen-com/hyperframes/hyperframes` | programatico | 5054 | HyperFrames |
| 23 | 76.7 | `heygen-com/hyperframes/talking-head-recut` | decupagem | 16135 | local (HyperFrames) |
| 24 | 76.7 | `heygen-com/hyperframes/general-video` | programatico | 5349 | HyperFrames |
| 25 | 76.5 | `lottiefiles/motion-design-skill/motion-design` | motion | 2988 | agnóstico |
| 26 | 76.4 | `sfkislev/flue/premiere` | apps | 386 | Premiere + Flue (ExtendScript) |
| 27 | 76.1 | `hetpatel-11/adobe_premiere_pro_mcp/premiere-pro-mcp` | apps | 1258 | Premiere + MCP hetpatel |
| 28 | 76.1 | `iart-ai/motion-design-skills/motion-art-direction` | motion | 1732 | agnóstico |
| 29 | 75.8 | `digitalsamba/claude-code-video-toolkit/ffmpeg` | ffmpeg | 3205 | local (ffmpeg) |
| 30 | 75.7 | `pluviobyte/rnskill/skill-captions` | legendas | 1175 | local |
| 31 | 75.6 | `samuelgursky/davinci-resolve-mcp/resolve-delivery` | entrega | 1923 | Resolve + MCP |
| 32 | 75.6 | `emilkowalski/skills/animation-vocabulary` | motion | 3177 | agnóstico |
| 33 | 75.1 | `samuelgursky/davinci-resolve-mcp/resolve-fusion` | motion | 611 | Resolve + MCP |
| 34 | 75.1 | `diffusionstudio/lottie/text-to-lottie` | motion | 2366 | local (Lottie) |
| 35 | 75.0 | `samuelgursky/davinci-resolve-mcp/resolve-media-pool` | apps | 582 | Resolve + MCP |
| 36 | 75.0 | `pluviobyte/rnskill/ra-audio-to-subtitles` | legendas | 980 | local |
| 37 | 74.7 | `elevenlabs/skills/sound-effects` | audio | 830 | API ElevenLabs |
| 38 | 74.4 | `samuelgursky/davinci-resolve-mcp/resolve-edit` | decupagem | 2303 | Resolve + MCP |
| 39 | 74.3 | `samuelgursky/davinci-resolve-mcp/resolve-rough-cut` | decupagem | 2804 | Resolve + MCP |
| 40 | 74.2 | `samuelgursky/davinci-resolve-mcp/resolve-tighten-recording` | decupagem | 2050 | Resolve + MCP |
| 41 | 74.2 | `remotion-dev/skills/remotion-markup` | programatico | 4318 | Remotion |
| 42 | 73.9 | `browser-use/video-use/video-use` | decupagem | 6353 | local (ffmpeg+whisper) |
| 43 | 73.9 | `samuelgursky/davinci-resolve-mcp/resolve-audio` | audio | 1471 | Resolve + MCP |
| 44 | 73.9 | `bradautomates/claude-video/watch` | analise | 4164 | local (yt-dlp+ffmpeg+whisper) |
| 45 | 73.7 | `heygen-com/hyperframes/hyperframes-audio` | audio | 6418 | HyperFrames |
| 46 | 73.4 | `wyattblue/auto-editor/auto-editor-effects` | decupagem | 1670 | local (auto-editor) |
| 47 | 73.4 | `lobzyjay/motion-design-with-claude-and-codex/motion-design` | motion | 612 | AE/Blender (opcional MCP) |
| 48 | 73.3 | `jakeschincariol/youtube-agent-skill/yt-shorts` | social | 316 | agnóstico |
| 49 | 72.9 | `jaycheng1103/chatgpt-video-editing-skills/chatgpt-short-video-editor` | social | 618 | local |
| 50 | 72.4 | `heygen-com/hyperframes/music-to-video` | programatico | 4617 | HyperFrames |
| 51 | 72.2 | `samuelgursky/davinci-resolve-mcp/resolve-media-analysis` | analise | 1026 | Resolve + MCP |
| 52 | 72.0 | `pluviobyte/rnskill/ra-local-talking-head-cut` | decupagem | 1650 | local |
| 53 | 71.3 | `vincentwei1021/video-shotcraft/video-shotcraft` | programatico | 2560 | local |
| 54 | 71.2 | `social-media-skills/skills/captions-and-clipping` | social | 1133 | agnóstico |
| 55 | 71.2 | `steipete/agent-scripts/video-transcript-downloader` | analise | 525 | local (yt-dlp) |
| 56 | 70.6 | `mrgoonie/claudekit-skills/media-processing` | ffmpeg | 2216 | local (ffmpeg) |
| 57 | 70.5 | `charlie947/social-media-skills/youtube-thumbnail` | social | 1793 | geração de imagem |
| 58 | 70.4 | `heygen-com/hyperframes/hyperframes-cli` | programatico | 6331 | HyperFrames |
| 59 | 70.4 | `coreyhaines31/marketingskills/video` | social | 3535 | agnóstico |
| 60 | 70.2 | `calesthio/generative-media-skills/color-grading-finishing` | cor | n/d | agnóstico |
| 61 | 70.1 | `mirage-hq/tesseract/tesseract-video` | decupagem | 2252 | local (Tesseract) |
| 62 | 69.4 | `leancoderkavy/premiere-pro-mcp/edit-premiere-project` | apps | n/d | Premiere + premiere-pro-mcp |
| 63 | 69.2 | `lordhoell/davinci-resolve-mcp/davinci-resolve-mcp` | apps | 1554 | Resolve + MCP lordhoell |
| 64 | 69.1 | `renezander030/capcut-cli/capcut-edit` | apps | 1310 | CapCut/JianYing |
| 65 | 69.1 | `sugarforever/01coder-agent-skills/subtitle-correction` | legendas | 2177 | agnóstico |
| 66 | 69.0 | `heygen-com/hyperframes/website-to-hyperframes` | programatico | n/d | HyperFrames |
| 67 | 69.0 | `elevenlabs/skills/music` | audio | 3283 | API ElevenLabs |
| 68 | 68.9 | `elevenlabs/skills/speech-to-text` | legendas | 2437 | API ElevenLabs |
| 69 | 68.8 | `inference-sh/skills/video-ad-specs` | entrega | n/d | agnóstico (specs) |
| 70 | 68.5 | `heygen-com/skills/video-understand` | analise | n/d | local (ffmpeg+whisper) |
| 71 | 68.5 | `bsisduck/video-analyzer-skill/analyzing-video` | analise | 1524 | local |
| 72 | 68.4 | `iart-ai/tiktok-video-skills/caption-animation` | legendas | 2335 | local |
| 73 | 68.0 | `av/remotion-bits/remotion-bits` | programatico | 1759 | Remotion |
| 74 | 67.7 | `damionrashford/media-os/workflow-editorial-interchange` | apps | 1365 | local (EDL/XML/AAF) |
| 75 | 67.4 | `elevenlabs/skills/text-to-speech` | audio | 2505 | API ElevenLabs |
| 76 | 66.8 | `dylantarre/animation-principles/video-motion-graphics` | motion | n/d | AE/Premiere |
| 77 | 66.8 | `iart-ai/tiktok-video-skills/short-form-video` | social | 2624 | agnóstico |
| 78 | 66.7 | `heygen-com/skills/video-edit` | decupagem | n/d | local (ffmpeg) |
| 79 | 66.6 | `openclaw/openclaw/video-frames` | analise | n/d | local (ffmpeg) |
| 80 | 66.3 | `josiahsiegel/claude-plugin-marketplace/ffmpeg-captions-subtitles` | legendas | n/d | local (ffmpeg) |
| 81 | 66.3 | `digitalsamba/claude-code-video-toolkit/elevenlabs` | audio | 3449 | API ElevenLabs |
| 82 | 66.0 | `damionrashford/media-os/workflow-vod-post-production` | entrega | 1499 | local (ffmpeg) |
| 83 | 65.8 | `digitalsamba/claude-code-video-toolkit/moviepy` | ffmpeg | 3136 | local (moviepy) |
| 84 | 65.7 | `dylantarre/animation-principles/after-effects` | motion | n/d | After Effects |
| 85 | 65.4 | `inference-sh/skills/ai-video-generation` | geracao | n/d | API paga inference.sh |
| 86 | 65.2 | `higgsfield-ai/skills/higgsfield-generate` | geracao | 5870 | API paga Higgsfield |
| 87 | 64.9 | `ncklrs/startup-os-skills/motion-designer` | motion | 2190 | agnóstico |
| 88 | 64.8 | `aedev-tools/adobe-agent-skills/after-effects` | motion | 4997 | After Effects (ExtendScript) |
| 89 | 64.6 | `barty-bart/motion-graphics/motion-broll` | motion | 2136 | local |
| 90 | 64.6 | `noizai/skills/sound-fx` | audio | 1168 | API Noiz |
| 91 | 64.5 | `openclaudia/openclaudia-skills/podcast-edit` | decupagem | 5723 | local (ffmpeg) |
| 92 | 64.1 | `damionrashford/media-os/workflow-podcast-pipeline` | audio | 1394 | local (ffmpeg) |
| 93 | 63.9 | `affaan-m/ecc/fal-ai-media` | geracao | 1786 | API paga fal.ai |
| 94 | 62.8 | `dylantarre/animation-principles/lottie-bodymovin` | motion | n/d | AE → Lottie |
| 95 | 62.5 | `kajisho5/ffmpeg-skill/ffmpeg-skill` | ffmpeg | 7170 | local (ffmpeg) |
| 96 | 61.6 | `cnemri/google-genai-skills/veo-use` | geracao | 536 | API Google (Veo) |
| 97 | 61.5 | `postplusai/postplus-skills/broll-match-engine` | decupagem | n/d | local |
| 98 | 61.5 | `damionrashford/media-os/ffmpeg-subtitles` | legendas | 2692 | local (ffmpeg) |
| 99 | 61.3 | `kwindla/skill-caption-clip/caption-clip` | legendas | 872 | Deepgram + ffmpeg |
| 100 | 60.9 | `kostja94/marketing-skills/youtube-seo` | social | n/d | agnóstico |

## Adotadas automaticamente pelo agente (0)

- nenhuma ainda
